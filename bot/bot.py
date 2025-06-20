import discord # Librería para interactuar con Discord
import sqlite3 # Librería para manejar la base de datos SQLite
from discord.ext import commands # Extensión de comandos para Discord
from datetime import datetime # Para manejar fechas y horas

import tokensecrets # Archivo secrets.py el que tiene el token del bot

# === PERMISOS QUE TENDRA EL BOT ===
intents = discord.Intents.default()
intents.message_content = True # Permite al bot leer el contenido de los mensajes
intents.reactions = True # Permite al bot detectar las reacciones
intents.members = True # Permite al bot saber quién es el usuario que reacciona
intents.guilds = True # Permite al bot interactuar con los servidores

# === BOT ===
bot = commands.Bot(command_prefix='$', intents=intents)

# === CONFIGURACIÓN DE BASE DE DATOS ===
conn = sqlite3.connect('./Sensores-LifeSyncGames.db')
cursor = conn.cursor() # Permite ejecutar comandos SQL en la base de datos

# Creamos la tabla LifeSyncGames si aún no existe.
cursor.execute('''
CREATE TABLE IF NOT EXISTS bot_discord (
    usuario_id TEXT,
    mensaje_id TEXT,
    fecha TEXT,
    emoji TEXT,
    PRIMARY KEY (usuario_id, mensaje_id, fecha)
)
''')
conn.commit() # Guardamos los cambios en la base de datos

# === FUNCIONES DE BASE DE DATOS ===
# Funciones para guardar reacciones en la base de datos
def guardar_reaccion(usuario_id, mensaje_id, emoji):
    fecha = datetime.utcnow().strftime('%Y-%m-%d')
    
    # Borra la reacción anterior si existe
    cursor.execute('''
        DELETE FROM bot_discord
        WHERE usuario_id = ? AND mensaje_id = ? AND fecha = ?
    ''', (usuario_id, mensaje_id, fecha))

    # Inserta la nueva reacción
    cursor.execute('''
        INSERT INTO bot_discord (usuario_id, mensaje_id, fecha, emoji)
        VALUES (?, ?, ?, ?)
    ''', (usuario_id, mensaje_id, fecha, emoji))

    conn.commit() # Guardamos los cambios en la base de datos

# Funciones para eliminar reacciones en la base de datos
def eliminar_reaccion(usuario_id, mensaje_id, emoji):
    fecha = datetime.utcnow().strftime('%Y-%m-%d')
    cursor.execute('''
        DELETE FROM bot_discord
        WHERE usuario_id = ? AND mensaje_id = ? AND fecha = ? AND emoji = ?
    ''', (usuario_id, mensaje_id, fecha, emoji))

    conn.commit() # Guardamos los cambios en la base de datos

# === EVENTOS DEL BOT ===
@bot.event
async def on_ready():
    print(f'Bot conectado {bot.user}')

@bot.event
# Evento que se activa cuando el bot vio que un usuario reacciona a un mensaje
async def on_reaction_add(reaction, user):
    if user.bot:  # Ignora las reacciones de otros bots
        return
    
    # Verifica si la reacción es un emoji específico
    if str(reaction.emoji) in ['✅', '❌']:  # Iconos que el bot va a detectar
        guardar_reaccion(str(user.id), str(reaction.message.id), str(reaction.emoji))  # Guarda en la base de datos
        print(f"{user.name} reaccionó con {reaction.emoji} en mensaje {reaction.message.id}")

@bot.event
# Evento que se activa cuando el bot vio que un usuario quitó una reacción a un mensaje
async def on_reaction_remove(reaction, user):
    if user.bot:
        return

    if str(reaction.emoji) in ['✅', '❌']:
        eliminar_reaccion(str(user.id), str(reaction.message.id), str(reaction.emoji))
        print(f"{user.name} quitó {reaction.emoji} en mensaje {reaction.message.id}")

# === COMANDO ===   
@bot.command() # Permite crear un comando que se puede invocar con el prefijo definido
async def LSG(ctx): # Comando que se invoca con $LSG
    fecha = datetime.utcnow().strftime('%Y-%m-%d')
    
    # Consulta la base de datos para obtener las reacciones del usuario en la fecha actual
    cursor.execute('''
        SELECT emoji, COUNT(*) FROM bot_discord
        WHERE usuario_id = ? AND fecha = ?
        GROUP BY emoji
    ''', (str(ctx.author.id), fecha))
    resultados = cursor.fetchall()

    if resultados:
        mensaje = f"📊 Reacciones de hoy para {ctx.author.name}:\n"
        for emoji, cantidad in resultados:
            mensaje += f"{emoji} → {cantidad} mensajes\n"
    else:
        mensaje = f"No hay reacciones registradas para {ctx.author.name} hoy."

    await ctx.send(mensaje)  # Envía el mensaje al canal donde se invocó el comando
# === COMANDO PARA LIMPIAR EL CANAL ===    
@bot.command()
async def Clean(ctx):
    await ctx.channel.purge()  # Limpia el canal
    await ctx.send("Mensajes Eliminados", delete_after=2)  # Mensaje que se borra solo después de 3 segundos

# === INICIAR EL BOT ===
bot.run(tokensecrets.TOKEN)