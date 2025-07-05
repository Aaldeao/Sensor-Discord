import discord # Librería para interactuar con Discord
import sqlite3 # Librería para manejar la base de datos SQLite

from discord.ext import commands # Extensión de comandos para Discord
from datetime import datetime, timezone, timedelta
from discord.ext.commands import BucketType

import tokensecrets # Archivo secrets el que tiene el token del bot
import requests # Librería para hacer peticiones HTTP
import random

# === PERMISOS QUE TENDRA EL BOT ===
intents = discord.Intents.default()
intents.message_content = True # Permite al bot leer el contenido de los mensajes
intents.reactions = True # Permite al bot detectar las reacciones
intents.members = True # Permite al bot saber quién es el usuario que reacciona
intents.guilds = True # Permite al bot interactuar con los servidores

# === BOT ===
bot = commands.Bot(command_prefix='$', intents=intents) # Prefijo del comando del bot es '$'

# === BASE DE DATOS ===
conn = sqlite3.connect('./Sensores-LifeSyncGames.db')
cursor = conn.cursor()

# Tabla que guarda el total de puntos del usuario en Discord
cursor.execute('''
CREATE TABLE IF NOT EXISTS bot_discord (
    usuario_id TEXT,
    fecha TEXT,
    puntos INTEGER,
    PRIMARY KEY (usuario_id, fecha)
)
''')

# Tabla que guarda el mensaje que reacciono el usuario por dia
cursor.execute('''
CREATE TABLE IF NOT EXISTS bot_reacciones (
    usuario_id TEXT,
    mensaje_id TEXT,
    fecha TEXT,
    PRIMARY KEY (usuario_id, mensaje_id, fecha)
)
''')

conn.commit() # Guarda los cambios

# === DICCIONARIO PARA QUIZ ===
quiz_mensajes = {} # Guarda el ID del mensaje del quiz, el ID del usuario que lo ejecutó y el comando que ejecutó

# === EMOJIS Y PUNTOS ===
emoji_puntos = {
    '❤️': 1,
    '👍': 1,
    '🤔': 1,
    '👎': 1
}

# === FUNCIONES DE BASE DE DATOS ===

# Función para verificar si tiene vinculada su cuenta de LifeSyncGames con Discord
def usuario_autorizado(id_discord):
    cursor.execute('''
        SELECT COUNT(*) FROM users WHERE id_discord = ?
    ''', (str(id_discord),))
    resultado = cursor.fetchone()[0] 
    return resultado > 0 

# Función para obtener el id_player de LifeSync Games del usuario vinculado a Discord
def obtener_id_player(id_discord):
    cursor.execute('''
        SELECT id_players FROM users WHERE id_discord = ?
    ''', (str(id_discord),))
    result = cursor.fetchone()
    return result[0] if result else None

# Funciones sumar puntos al usuario cuando reacciona a un mensaje del bot
def agregar_puntos(usuario_id, mensaje_id, emoji):
    fecha = datetime.now(timezone(timedelta(hours=-4))).strftime('%Y-%m-%d')

    # Verifica si el usuario ya reaccionó al mensaje hoy
    cursor.execute('''
        SELECT COUNT(*) FROM bot_reacciones WHERE usuario_id = ? AND mensaje_id = ? AND fecha = ?
    ''', (usuario_id, mensaje_id, fecha))
    if cursor.fetchone()[0] > 0:
        print(f"Usuario {usuario_id} ya reaccionó al mensaje {mensaje_id} hoy. No suma puntos.")
        return

    puntos = emoji_puntos.get(emoji, 0) # Obtiene el valor del emoji

    # Registra la reacción del usuario
    cursor.execute('''
        INSERT INTO bot_reacciones (usuario_id, mensaje_id, fecha) VALUES (?, ?, ?)
    ''', (usuario_id, mensaje_id, fecha))

    # Consulta los puntos actuales del usuario del dia
    cursor.execute('''
        SELECT puntos FROM bot_discord WHERE usuario_id = ? AND fecha = ?
    ''', (usuario_id, fecha))
    row = cursor.fetchone()

    # Actualiza los puntos del usuario, asegurando que no exceda 15 puntos
    if row:
        puntos_actuales = row[0]
        puntos_para_enviar = max(0,min(15 - puntos_actuales, puntos)) # Asegura que no se envíen más de 15 puntos en total
        puntos_actualizados = puntos_actuales + puntos_para_enviar
        # Actualiza los puntos del usuario en la base de datos
        cursor.execute('''
            UPDATE bot_discord SET puntos = ? WHERE usuario_id = ? AND fecha = ?
        ''', (puntos_actualizados, usuario_id, fecha))
    else:
        puntos_para_enviar = min(15, puntos)
        puntos_actualizados = puntos_para_enviar
        cursor.execute('''
            INSERT INTO bot_discord (usuario_id, fecha, puntos) VALUES (?, ?, ?)
        ''', (usuario_id, fecha, puntos_actualizados))

    conn.commit() # Guarda los cambios en la base de datos

    # Enviar puntos al servidor de LifeSyncGames
    try:
        id_player = obtener_id_player(usuario_id)
        if id_player is None:
            print(f"No se encontró un id_player para el usuario {usuario_id}.")
            return
        
        # Solo se envían los puntos si hay algo para enviar
        if puntos_para_enviar > 0:
            data = {
                "points": puntos_para_enviar,
                "id_attributes": "0", # Dimensión social 
                "id_players": str(id_player)
            }

            response = requests.put("http://localhost:8080/users/sendPointsDiscord", json=data)

            if response.status_code == 200:
                print(f"Puntos ({puntos_para_enviar}) enviados al servidor para {usuario_id}") # Mensaje de éxito
            else:
                print(f"Error al enviar puntos: {response.status_code} - {response.text}") # Mensaje de error
        else:
            print(f"Usuario {usuario_id} ya alcanzó el máximo de puntos diarios. No se envían más.")
    except Exception as e:
        print(f"Excepción al enviar puntos al servidor: {e}") # Mensaje de excepción

# Funcion para consultar los puntos totales del usuario del dia
def puntos_totales_usuario(usuario_id):
    fecha = datetime.now(timezone(timedelta(hours=-4))).strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT puntos FROM bot_discord WHERE usuario_id = ? AND fecha = ?
    ''', (usuario_id, fecha))
    row = cursor.fetchone()
    return row[0] if row else 0

# === EVENTOS DEL BOT ===
# Evento cuando el bot se conecta a Discord
@bot.event
async def on_ready():
    print(f'Bot conectado {bot.user}')

# Evento que se activa cuando el bot ve que el usuario reacciona a un mensaje
@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return # Ignora las reacciones de otros bots
    
    mensaje = reaction.message
    autor = mensaje.author
    emoji = str(reaction.emoji)
    
    # ===== LOGICA 1: PUNTOS POR LAS REACCIONES QUE REALIZA EL USUARIO AL QUIZ DEL BOT =====
    # Verifica que la reacción sea del mensaje del bot
    if mensaje.author == bot.user:
    # Verifica que la reacción sea una de las reacciones válidas
        if emoji in emoji_puntos:
            # Verifica si el usuario tiene permiso para reaccionar
            if user.id in quiz_mensajes and mensaje.id in quiz_mensajes[user.id]:
                agregar_puntos(str(user.id), str(mensaje.id), emoji)
            else:
                # Quita la reacción no autorizada
                try:
                    await reaction.message.remove_reaction(reaction.emoji, user)
                    print(f"Se quitó reacción no autorizada de {user.name} en mensaje {reaction.message.id}")
                except:
                    pass
        return 
    
    # ===== LOGICA 2: PUNTOS POR LAS REACCIONES QUE REALIZAN LOS OTROS AL MENSAJE DEL USUARIO =====
    # Verifica que el autor del mensaje no sea el mismo que reacciono, que no sea un bot y que la reacción sea con un emoji valido
    if autor.id != user.id and not autor.bot and emoji in emoji_puntos:
        # Verifica que el autor del mensaje tiene vinculado su cuenta de LifeSyncGames con Discord
        if usuario_autorizado(autor.id):
            agregar_puntos(str(autor.id), str(mensaje.id), emoji)

# Evento que se activa cuando un usuario envía un mensaje
@bot.event
async def on_message(message):
    if message.author.bot:
        return # Ignora los mensajes de otros bots
    
    # Verifica si este mensaje es una respuesta a otro mensaje
    if message.reference and message.reference.resolved:
        mensaje_respondido = message.reference.resolved # Obtiene el mensaje al que se le esta respondiendo
        autor_de_mensaje = mensaje_respondido.author # Obtiene el autor del mensaje al que se le esta respondiendo

        # Verifica que la persona que respondió no sea la misma que el autor del mensaje y que no sea un bot
        if autor_de_mensaje.id != message.author.id and not autor_de_mensaje.bot:
            # Verifica que el autor del mensaje tiene vinculado su cuenta de LifeSyncGames con Discord
            if usuario_autorizado(autor_de_mensaje.id):
                # Agrega puntos al autor del mensaje original por la respuesta de otro usuario
                agregar_puntos(str(autor_de_mensaje.id), str(mensaje_respondido.id), '❤️') # 
                print(f"Puntos agregados al autor del mensaje por la respuesta de otro usuario")
    
    # Para que el bot siga procesando los comandos después de manejar este evento
    await bot.process_commands(message)

# === COMANDOOS ===   
@bot.command()
async def LSG(ctx):
    if not usuario_autorizado(ctx.author.id):
        await ctx.send(f"❌ {ctx.author.mention}, no tienes permiso para usar este comando. Por favor, vincula tu cuenta de LifeSyncGames con Discord.")
        return
    # Consulta los puntos totales del usuario del dia
    puntos = puntos_totales_usuario(str(ctx.author.id))
    if puntos > 0:
        await ctx.send(f"📊 {ctx.author.name}, tus puntos de hoy son: **{puntos}** 🎯")
    else:
        await ctx.send(f"No hay puntos registrados para {ctx.author.name} hoy.")


# === QUIZ ===
# === COMANDO PARA EL QUIZ DE CITIES: SKYLINES ===
@bot.command()
@commands.cooldown(1, 86400, BucketType.user) # Limita el uso del comando a una vez cada 24 horas
async def cities(ctx):

    # Verifica si el usuario vinculo su cuenta de LifeSyncGames con Discord
    if not usuario_autorizado(ctx.author.id):
        await ctx.send(f"❌ {ctx.author.mention}, no tienes permiso para usar este comando. Por favor, vincula tu cuenta de LifeSyncGames con Discord.")
        return

    # Verifica si el usuario ya tiene 15 puntos
    puntos_actuales = puntos_totales_usuario(str(ctx.author.id))
    if puntos_actuales >= 15:
        await ctx.send(f"🚫 {ctx.author.mention}, ya has alcanzado el límite de 15 puntos por hoy. ¡Inténtalo de nuevo mañana!")
        return
    
    # Lista de preguntas para el quiz de Cities: Skylines
    preguntas = [
        { "texto": "¿Te gusta jugar Cities: Skylines?" },
        { "texto": "¿Te gusta construir y administrar tu propia ciudad en Cities: Skylines?" },
        { "texto": "¿Te gusta usar mods en Cities: Skylines?" },
        { "texto": "¿Disfrutas personalizar tu ciudad con parques y zonas recreativas?" },
        { "texto": "¿Prefieres construir ciudades grandes y densas en Cities: Skylines?" },
        { "texto": "¿Sueles inspirarte en ciudades reales al construir la tuya?" },
        { "texto": "¿Te divierte diseñar tu ciudad solo por estética, sin preocuparte por la eficiencia?" },
        { "texto": "¿Te gusta empezar desde cero y destruir tu ciudad para mejorarla?" },
        { "texto": "¿Te gusta más construir de noche que de día en el juego?" },
        { "texto": "¿Prefieres construir ciudades realistas en lugar de creativas o locas?" },
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

    # Si no existe el diccionario para el usuario, se crea
    if ctx.author.id not in quiz_mensajes:
        quiz_mensajes[ctx.author.id] = {}

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

        # Agrega las reacciones al mensaje
        for emoji in opciones:
            await pregunta_msg.add_reaction(emoji)

        # Espera a que el usuario reaccione
        reaction, user = await bot.wait_for('reaction_add', check=make_check(pregunta_msg))

        await ctx.send("\u200b") # Espacio en blanco

    await ctx.send(f"{ctx.author.mention} ¡Gracias por completar el quiz de Cities: Skylines! 🎉")

    if ctx.author.id in quiz_mensajes:
        del quiz_mensajes[ctx.author.id] # Limpia el diccionario de mensajes del usuario

# === COMANDO PARA EL QUIZ DE TECNOLOGIA ===
@bot.command()
@commands.cooldown(1, 86400, BucketType.user) # Limita el uso del comando a una vez cada 24 horas
async def technology(ctx):

    # Verifica si el usuario vinculo su cuenta de LifeSyncGames con Discord
    if not usuario_autorizado(ctx.author.id):
        await ctx.send(f"❌ {ctx.author.mention}, no tienes permiso para usar este comando. Por favor, vincula tu cuenta de LifeSyncGames con Discord.")
        return

    # Verifica si el usuario ya tiene 15 puntos
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
        { "texto": "¿Has usado alguna vez un servicio en la nube como Google Drive o iCloud?" },
        { "texto": "¿Has usado alguna app para monitorear tu salud o ejercicio?" },
        { "texto": "¿Has probado alguna app de realidad aumentada?" },
        { "texto": "¿Te gustaría vivir en una ciudad 100% inteligente y conectada?" },
        { "texto": "¿Alguna vez has hablado con una IA como si fuera una persona real?" },
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

    # Si no existe el diccionario para el usuario, se crea
    if ctx.author.id not in quiz_mensajes:
        quiz_mensajes[ctx.author.id] = {}

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

        # Guardamos el mensaje y usuario con el comando ejecutado
        quiz_mensajes[ctx.author.id][pregunta_msg.id] = 'technology'

        # Agrega las reacciones al mensaje
        for emoji in opciones:
            await pregunta_msg.add_reaction(emoji)

        # Espero a que el usuario reaccione
        reaction, user = await bot.wait_for('reaction_add', check=make_check(pregunta_msg))

        await ctx.send("\u200b") # Espacio en blanco

    await ctx.send(f"{ctx.author.mention} ¡Gracias por completar el quiz de tecnologia! 🎉")

    if ctx.author.id in quiz_mensajes:
        del quiz_mensajes[ctx.author.id] # Limpia el diccionario de mensajes del usuario

# === COMANDO PARA EL QUIZ DE INFORMATICA ===
@bot.command()
@commands.cooldown(1, 86400, BucketType.user) # Limita el uso del comando a una vez cada 24 horas
async def informatica(ctx):

    # Verifica si el usuario vinculo su cuenta de LifeSyncGames con Discord
    if not usuario_autorizado(ctx.author.id):
        await ctx.send(f"❌ {ctx.author.mention}, no tienes permiso para usar este comando. Por favor, vincula tu cuenta de LifeSyncGames con Discord.")
        return

    # Verifica si el usuario ya tiene 15 puntos
    puntos_actuales = puntos_totales_usuario(str(ctx.author.id))
    if puntos_actuales >= 15:
        await ctx.send(f"🚫 {ctx.author.mention}, ya has alcanzado el límite de 15 puntos por hoy. ¡Inténtalo de nuevo mañana!")
        return

    # Lista de preguntas para el quiz de informática
    preguntas = [
        { "texto": "¿Te gustaria aprender sobre computadoras y cómo funcionan?" },
        { "texto": "¿Alguna vez has formateado una computadora por tu cuenta?" },
        { "texto": "¿Te gusta arreglar problemas técnicos en tu PC o la de otros?" },
        { "texto": "¿Te interesa saber cómo se construye un programa o aplicación?" },
        { "texto": "¿Te gustaría montar tu propio PC desde cero?" },
        { "texto": "¿Te interesa la ciberseguridad y cómo proteger tus dispositivos?" },
        { "texto": "¿Te gusta usar software libre y de código abierto como Linux?" },
        { "texto": "¿Te gustaría aprender a programar?" },
        { "texto": "¿Crees que saber informática es esencial para cualquier carrera hoy en día?" },
        { "texto": "¿Te gustaría trabajar en algo relacionado con informática algún día?" },
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

    # Si no existe el diccionario para el usuario, se crea
    if ctx.author.id not in quiz_mensajes:
        quiz_mensajes[ctx.author.id] = {}

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
        quiz_mensajes[ctx.author.id][pregunta_msg.id] = 'informatica'

        # Agrega las reacciones al mensaje
        for emoji in opciones:
            await pregunta_msg.add_reaction(emoji)

        # Espera a que el usuario reaccione
        reaction, user = await bot.wait_for('reaction_add', check=make_check(pregunta_msg))

        await ctx.send("\u200b") # Espacio en blanco

    await ctx.send(f"{ctx.author.mention} ¡Gracias por completar el quiz de informática! 🎉")

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
        "`$LSG` → Muestra tus puntos del día.\n"
        "`$cities` → Inicia un quiz sobre Cities: Skylines.\n"
        "`$technology` → Inicia un quiz sobre tecnología.\n"
        "`$informatica` → Inicia un quiz sobre informática.\n"
        "`$clean` → Limpia el canal de mensajes.\n"
        "`$Help` → para ver esta lista de nuevo."
    )
    await ctx.send(ayuda)

# === INICIAR EL BOT ===
bot.run(tokensecrets.TOKEN)