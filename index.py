import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
from flask import Flask


app = Flask(__name__)

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Importar el manager de base de datos desde utils/database.py
from utils.database import DatabaseManager

# Inicializar el DatabaseManager
db_manager = DatabaseManager()

# Configuración del bot
bot = commands.Bot(command_prefix='.', intents=intents, activity=discord.Game(name="Guild Wars 2"), status=discord.Status.idle)

@bot.event
async def setup_hook():
    bot.remove_command('help')
    # Cargar las extensiones
    await bot.load_extension('utils.help')

@bot.event
async def on_ready():
    print(f'Bot is ready: {bot.user.name}')
    
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

# Carga los cogs (comandos)
async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            print(f'Loaded {filename[:-3]}')

# Obtener el puerto desde las variables de entorno o asignar un predeterminado
PORT = int(os.getenv("PORT", 8080))

# Función principal para cargar el bot
async def main():
    async with bot:
        await load()
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
    PORT = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)