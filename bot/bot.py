import discord # Librería para interactuar con Discord
import sqlite3 # Librería para manejar la base de datos SQLite
from discord.ext import commands # Extensión de comandos para Discord
from datetime import datetime # Para manejar fechas y horas

import tokensecrets # Archivo secrets.py el que tiene el token del bot

# Permisos que solicitará el bot 
intents = discord.Intents.default()
intents.message_content = True # Permite al bot leer el contenido de los mensajes
intents.reactions = True # Permite al bot detectar las reacciones
intents.members = True # Permite al bot saber quién es el usuario que reacciona
intents.guilds = True # Permite al bot interactuar con los servidores

bot = commands.Bot(command_prefix='!', intents=intents)

# === CONFIGURACIÓN DE BASE DE DATOS ===
conn = sqlite3.connect('./Sensores-LifeSyncGames.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS bot_discord (
    usuario_id TEXT,
    fecha TEXT,
    emoji TEXT,
    cantidad INTEGER,
    PRIMARY KEY (usuario_id, fecha, emoji)
)
''')
conn.commit()

# === FUNCIONES DE BASE DE DATOS ===

def guardar_reaccion(usuario_id, emoji):
    fecha = datetime.utcnow().strftime('%Y-%m-%d')
    # Verifica si ya existe una entrada para el usuario, fecha y emoji
    cursor.execute('''
        SELECT cantidad FROM bot_discord
        WHERE usuario_id = ? AND fecha = ? AND emoji = ?
    ''', (usuario_id, fecha, emoji))
    resultado = cursor.fetchone()

    if resultado:
        nueva_cantidad = resultado[0] + 1
        cursor.execute('''
            UPDATE bot_discord
            SET cantidad = ?
            WHERE usuario_id = ? AND fecha = ? AND emoji = ?
        ''', (nueva_cantidad, usuario_id, fecha, emoji))
    else:
        cursor.execute('''
            INSERT INTO bot_discord (usuario_id, fecha, emoji, cantidad)
            VALUES (?, ?, ?, 1)
        ''', (usuario_id, fecha, emoji))

    conn.commit()

# === Al reaccionar a un mensaje el bot guardará la reacción ===
@bot.event
async def on_reaction_add(reaction, user):
    if user.bot: # Ignora las reacciones de los bots
        return

    # Verifica que el emoji sea uno de los permitidos
    if str(reaction.emoji) in ['✅', '❌']:
        guardar_reaccion(str(user.id), str(reaction.emoji))
        print(f"{user.name} reaccionó con {reaction.emoji}")

# === Comando para ver la cantidad de reacciones del usuario en el día ===
@bot.command()
async def stats(ctx): # Comando para ver las estadísticas de reacciones del usuario !stats
    fecha = datetime.utcnow().strftime('%Y-%m-%d')
    cursor.execute('''
        SELECT emoji, cantidad FROM bot_discord
        WHERE usuario_id = ? AND fecha = ?
    ''', (str(ctx.author.id), fecha))
    datos = cursor.fetchall()

    if datos:
        mensaje = f"📊 Reacciones de hoy para {ctx.author.name}:\n"
        for emoji, cantidad in datos:
            mensaje += f"{emoji} → {cantidad} veces\n"
    else:
        mensaje = "No tienes reacciones registradas hoy."

    await ctx.send(mensaje)

# === INICIAR EL BOT ===
bot.run(tokensecrets.TOKEN)
