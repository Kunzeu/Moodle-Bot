import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Importar el manager de base de datos
from utils.database import dbManager

# Configuración del bot
bot = commands.Bot(
    command_prefix='.',
    intents=intents,
    activity=discord.Game(name="Guild Wars 2"),
    status=discord.Status.idle
)

@bot.event
async def on_ready():
    print(f'Bot is ready: {bot.user.name}')
    # Esperar un momento para asegurarse de que el bot esté completamente listo
    await asyncio.sleep(1)
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Error al sincronizar comandos: {e}")

# Carga los cogs (comandos)
async def load():
    bot.remove_command('help')
    # Cargar las extensiones
    await bot.load_extension('utils.help')
    
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'Loaded {filename[:-3]}')
            except Exception as e:
                print(f'Failed to load extension {filename}: {e}')

# Función principal para cargar el bot
async def main():
    async with bot:
        await load()
        await bot.start(TOKEN)

if __name__ == "__main__":
    # Iniciar Flask en un thread separado
    server_thread = Thread(target=run_flask, daemon=True)
    server_thread.start()
    
    # Iniciar el bot
    asyncio.run(main())