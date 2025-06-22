import discord # Librería para interactuar con Discord
import sqlite3 # Librería para manejar la base de datos SQLite

from discord.ext import commands # Extensión de comandos para Discord
from datetime import datetime
from discord.ext.commands import BucketType

import tokensecrets # Archivo secrets el que tiene el token del bot
import random

# === PERMISOS QUE TENDRA EL BOT ===
intents = discord.Intents.default()
intents.message_content = True # Permite al bot leer el contenido de los mensajes
intents.reactions = True # Permite al bot detectar las reacciones
intents.members = True # Permite al bot saber quién es el usuario que reacciona
intents.guilds = True # Permite al bot interactuar con los servidores

# === BOT ===
bot = commands.Bot(command_prefix='$', intents=intents)

# === DICCIONARIO PARA QUIZ ===
quiz_mensajes = {} # Guarda el ID del mensaje del quiz, el ID del usuario que lo ejecutó y el comando que ejecutó

# === CONFIGURACIÓN DE BASE DE DATOS ===
conn = sqlite3.connect('./Sensores-LifeSyncGames.db')
cursor = conn.cursor() # Permite ejecutar comandos SQL

# La tabla bot_discord.
cursor.execute('''
CREATE TABLE IF NOT EXISTS bot_discord (
    usuario_id TEXT,
    mensaje_id TEXT,
    fecha TEXT,
    emoji TEXT,
    puntos INTEGER,
    PRIMARY KEY (usuario_id, mensaje_id, fecha)
)
''')
conn.commit() # Guardamos los cambios en la base de datos

# === FUNCIONES DE BASE DE DATOS ===

# Diccionario que asigna puntos a cada emoji
emoji_puntos = {
    '❤️': 3,
    '👍': 2,
    '🤔': 1,
    '👎': 0
}

# Funciones para guardar reacciones en la base de datos
def guardar_reaccion(usuario_id, mensaje_id, emoji):
    fecha = datetime.utcnow().strftime('%Y-%m-%d')
    puntos = emoji_puntos.get(emoji, 0)  # Obtiene el punto del emoji
    
    # Borra la reacción anterior del mismo usuario si es que existe para ese mensaje y fecha
    cursor.execute('''
        DELETE FROM bot_discord
        WHERE usuario_id = ? AND mensaje_id = ? AND fecha = ? 
    ''', (usuario_id, mensaje_id, fecha))

    # Inserta la nueva reacción
    cursor.execute('''
        INSERT INTO bot_discord (usuario_id, mensaje_id, fecha, emoji, puntos)
        VALUES (?, ?, ?, ?, ?)
    ''', (usuario_id, mensaje_id, fecha, emoji, puntos))

    conn.commit() # Guarda los cambios

# Funciones para eliminar reacciones en la base de datos
def eliminar_reaccion(usuario_id, mensaje_id, emoji):
    fecha = datetime.utcnow().strftime('%Y-%m-%d')
    cursor.execute('''
        DELETE FROM bot_discord
        WHERE usuario_id = ? AND mensaje_id = ? AND fecha = ? AND emoji = ?
    ''', (usuario_id, mensaje_id, fecha, emoji))

    conn.commit() # Guarda los cambios

# Función para obtener los puntos totales de un usuario en el día
def puntos_totales_usuario(usuario_id):
    fecha = datetime.utcnow().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT SUM(puntos) FROM bot_discord
        WHERE usuario_id = ? AND fecha = ?
    ''', (usuario_id, fecha))
    resultado = cursor.fetchone()[0]
    return resultado if resultado else 0

# === EVENTOS DEL BOT ===
@bot.event
async def on_ready():
    print(f'Bot conectado {bot.user}') # Mensaje cuando el bot se conecta por consola

@bot.event
# Evento que se activa cuando el bot vio que un usuario reacciona a un mensaje
async def on_reaction_add(reaction, user):

    if user.bot:# Ignora bots
        return
    
    # Solo guardar si el mensaje es del bot
    if reaction.message.author != bot.user:
        return
    
    user_id = user.id
    mensaje_id = reaction.message.id

    if user_id not in quiz_mensajes or mensaje_id not in quiz_mensajes[user_id]:
        try:
            await reaction.message.remove_reaction(reaction.emoji, user) # Elimina la reaccion de otro usuario
            print(f"Se quitó reacción no autorizada de {user.name} en mensaje {mensaje_id}")
        except:
            pass # Maneja el caso si no se puede quitar la reacción (por ejemplo, si el bot no tiene permisos)
        return  

    # Verifica si la reacción es un emoji válido para el quiz
    if str(reaction.emoji) in ['❤️', '👍', '🤔' , '👎']:
        
        guardar_reaccion(str(user.id), str(reaction.message.id), str(reaction.emoji)) # Guarda en la base de datos
        print(f"{user.name} reaccionó en el mensaje {reaction.message.id}")

@bot.event
# Evento que se activa cuando el bot vio que un usuario quitó una reacción a un mensaje
async def on_reaction_remove(reaction, user):
    if user.bot: # Ignora bots
        return
    
    if reaction.message.author != bot.user:
        return
    
    user_id = user.id
    msg_id = reaction.message.id

    if user_id not in quiz_mensajes:
        return

    if msg_id not in quiz_mensajes[user_id]:
        return

    if str(reaction.emoji) in ['❤️', '👍', '🤔', '👎']:
        eliminar_reaccion(str(user.id), str(reaction.message.id), str(reaction.emoji))
        print(f"{user.name} quitó la reacción en el mensaje {reaction.message.id}")

# === COMANDO PARA VER LAS REACCIONES DEL USUARIO ===   
@bot.command()
async def LSG(ctx): # Comando $LSG
    fecha = datetime.utcnow().strftime('%Y-%m-%d')

    # Obtiene las reacciones del usuario en el mismo día
    cursor.execute('''
        SELECT emoji, COUNT(*), SUM(puntos) FROM bot_discord
        WHERE usuario_id = ? AND fecha = ?
        GROUP BY emoji
    ''', (str(ctx.author.id), fecha))
    resultados = cursor.fetchall()

    if resultados:
        mensaje = f"📊 Reacciones de hoy para {ctx.author.name}:\n"
        total_puntos = 0
        for emoji, cantidad, puntos in resultados:
            mensaje += f"{emoji} → {cantidad} mensajes → {puntos} puntos\n"
            total_puntos += puntos
        mensaje += f"\n🎯 **Total de puntos:** {total_puntos}"
    else:
        mensaje = f"No hay reacciones registradas para {ctx.author.name} hoy."

    await ctx.send(mensaje)

# === COMANDO PARA INICIAR UN QUIZ ===
@bot.command()
@commands.cooldown(1, 60, BucketType.user) # Limita el uso del comando a una vez cada 60 segundos por usuario === (86400 segundos = 24 horas) ===
async def cities(ctx): # Comando $cities

    # Verifica si el usuario ya tiene 15 puntos o más
    puntos_actuales = puntos_totales_usuario(str(ctx.author.id))
    if puntos_actuales >= 15:
        await ctx.send(f"🚫 {ctx.author.mention}, ya has alcanzado el límite de 15 puntos por hoy. ¡Inténtalo de nuevo mañana!")
        return
    
    # Lista de preguntas para el quiz
    preguntas = [
        { "texto": "¿Te gusta jugar Cities: Skylines?" },
        { "texto": "¿Te gusta construir y administrar tu propia ciudad en Cities: Skylines?" },
        { "texto": "¿Te gusta usar mods en Cities: Skylines?" },
        { "texto": "¿Disfrutas personalizar tu ciudad con parques y zonas recreativas?" },
        { "texto": "¿Prefieres construir ciudades grandes y densas en Cities: Skylines?" },
    ]

    random.shuffle(preguntas) # Mezcla las preguntas para que no siempre salgan en el mismo orden

    # Saludamos al usuario y le damos instrucciones
    await ctx.send(
        f"{ctx.author.mention} ¡Bienvenido al quiz de LifeSyncGames! 🎮\n"
        "Responde con una reacción a cada pregunta. Las opciones son:\n\n"
        "❤️ → *Me encanta / Muy de acuerdo*\n"
        "👍 → *Me gusta / De acuerdo*\n"
        "🤔 → *Ni de acuerdo ni en desacuerdo / Neutral*\n"
        "👎 → *No me gusta / En desacuerdo*\n"
    )
    
    # Definimos las opciones de reacción que el bot va a detectar
    opciones = ['❤️', '👍', '🤔', '👎']
    
    await ctx.send("\u200b") # Espacio en blanco

    if ctx.author.id not in quiz_mensajes:
        quiz_mensajes[ctx.author.id] = {} # Diccionario para guardar los mensajes del usuario

    # Función para verificar que la reacción sea del usuario que inició el comando y que use una de las opciones válidas para el quiz
    def make_check(pregunta_msg):
        return lambda reaction, user: (
            user == ctx.author and 
            str(reaction.emoji) in opciones and 
            reaction.message.id == pregunta_msg.id
        )

    # Función para enviar las preguntas, agrega las reacciones y espera la respuesta del usuario
    for pregunta in preguntas:
        pregunta_msg = await ctx.send(f"{ctx.author.mention}, {pregunta['texto']} \n")

        # Guardamos el mensaje y usuario con el comando ejecutado
        quiz_mensajes[ctx.author.id][pregunta_msg.id] = 'cities'

        for emoji in opciones:
            await pregunta_msg.add_reaction(emoji)

        # Espera a que el usuario reaccione
        reaction, user = await bot.wait_for('reaction_add', check=make_check(pregunta_msg))

        await ctx.send("\u200b") # Espacio en blanco

    await ctx.send(f"{ctx.author.mention} ¡Gracias por completar el quiz! 🎉")

    if ctx.author.id in quiz_mensajes:
        del quiz_mensajes[ctx.author.id] # Limpia el diccionario de mensajes del usuario

@bot.command()
@commands.cooldown(1, 60, BucketType.user)  # Limita el uso del comando a una vez cada 60 segundos por usuario === (86400 segundos = 24 horas) ===
async def technology(ctx):

    # Verifica si el usuario ya tiene 15 puntos o más
    puntos_actuales = puntos_totales_usuario(str(ctx.author.id))
    if puntos_actuales >= 15:
        await ctx.send(f"🚫 {ctx.author.mention}, ya has alcanzado el límite de 15 puntos por hoy. ¡Inténtalo de nuevo mañana!")
        return

    # Lista de preguntas para el quiz de tecnología
    preguntas = [
        { "texto": "¿Te gusta usar inteligencia artificial, como ChatGPT o Gemini?" },
        { "texto": "¿Te animarías a usar un auto que se maneje solo?" },
        { "texto": "¿Te gustan los relojes inteligentes como el Apple Watch o Galaxy Watch?" },
        { "texto": "¿Te gusta hacer pagos con el celular, por ejemplo con Google Pay o Apple Pay?" },
        { "texto": "¿Te gustaría tener una casa inteligente con luces o cerraduras controladas desde el celular?" },
    ]

    # Mezcla las preguntas para que no siempre salgan en el mismo orden
    random.shuffle(preguntas)

    # Saludamos al usuario y le damos instrucciones
    await ctx.send(
        f"{ctx.author.mention} ¡Bienvenido al quiz de LifeSyncGames! 🤖\n"
        "Responde con una reacción a cada pregunta. Las opciones son:\n\n"
        "❤️ → *Me encanta / Muy de acuerdo*\n"
        "👍 → *Me gusta / De acuerdo*\n"
        "🤔 → *Ni de acuerdo ni en desacuerdo / Neutral*\n"
        "👎 → *No me gusta / En desacuerdo*\n"
    )
    
    # Definimos las opciones de reacción que el bot va a detectar
    opciones = ['❤️', '👍', '🤔', '👎']
    
    await ctx.send("\u200b") # Espacio en blanco

    if ctx.author.id not in quiz_mensajes:
        quiz_mensajes[ctx.author.id] = {} # Diccionario para guardar los mensajes del usuario

    # Función para verificar que la reacción sea del usuario que inició el comando y que use una de las opciones válidas para el quiz
    def make_check(pregunta_msg):
        return lambda reaction, user: (
            user == ctx.author and 
            str(reaction.emoji) in opciones and 
            reaction.message.id == pregunta_msg.id
        )

    # Envío las preguntas, agrego reacciones y espero la respuesta
    for pregunta in preguntas:
        pregunta_msg = await ctx.send(f"{ctx.author.mention}, {pregunta['texto']} \n")

        quiz_mensajes[ctx.author.id][pregunta_msg.id] = 'technology'

        for emoji in opciones:
            await pregunta_msg.add_reaction(emoji)

        # Espero a que el usuario reaccione
        reaction, user = await bot.wait_for('reaction_add', check=make_check(pregunta_msg))

        await ctx.send("\u200b") # Espacio en blanco

    await ctx.send(f"{ctx.author.mention} ¡Gracias por completar el quiz! 🎉")

    if ctx.author.id in quiz_mensajes:
        del quiz_mensajes[ctx.author.id] # Limpia el diccionario de mensajes del usuario


# === COMANDO PARA LIMPIAR EL CANAL ===    
@bot.command()
async def clean(ctx): # Comando para limpiar el canal
    await ctx.channel.purge()
    await ctx.send("Mensajes Eliminados", delete_after=2)

# == EVENTO PARA MANEJAR ERRORES DE COMANDOS ==
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
         await ctx.send("❌ Ese no es un comando válido. Usa `$Help` para ver la lista de comandos disponibles.")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"🚫 Ya has usado este comando hoy. ¡Inténtalo de nuevo mañana!")
    else:
        await ctx.send("⚠️ Ocurrió un error inesperado al ejecutar el comando. Por favor, intenta de nuevo más tarde.")
        print(f"Error: {error}")

# === COMANDO PARA VER LA AYUDA ===
@bot.command()
async def Help(ctx):
    ayuda = (
        "Aquí tienes la lista de comandos disponibles:\n"
        "`$LSG` → Muestra tus reacciones del día.\n"
        "`$cities` → Inicia un quiz sobre Cities: Skylines.\n"
        "`$technology` → Inicia un quiz sobre tecnología.\n"
        "`$clean` → Limpia el canal de mensajes.\n"
        "`$Help` → para ver esta lista de nuevo."
    )
    await ctx.send(ayuda)

# === INICIAR EL BOT ===
bot.run(tokensecrets.TOKEN)