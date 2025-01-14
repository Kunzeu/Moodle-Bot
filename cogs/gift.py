import discord
from discord.ext import commands
from discord import app_commands

class GiftPrices(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="gift", description="Displays fixed prices for the GOM and GOJM.")
    async def gi(self, interaction: discord.Interaction):
        # Definir los precios manualmente en monedas de oro
        gift_prices = {
            "Price of GOJM": {
                "gold": 650,  # 650 de oro
                "silver": 0,  # 0 de plata
                "copper": 0   # 0 de cobre
            },
            "Price of GOM": {
                "gold": 600,  # 600 de oro
                "silver": 0,  # 0 de plata
                "copper": 0   # 0 de cobre
            }
        }

        # Función para convertir precios en formato de monedas de oro, plata y cobre
        def calculate_coins(price):
            return f"{price['gold']} <:gold:1328507096324374699> {price['silver']} <:silver:1328507117748879422> {price['copper']} <:Copper:1328507127857418250>"

        # Crear el embed con los precios
        embed = discord.Embed(
            title="Prices for the GOM and GOJM",
            description="These are the current prices of the Gifts:",
            color=0x0099ff
        )

        # Añadir las imágenes al embed (usando las URLs proporcionadas)
        embed.set_thumbnail(url="https://render.guildwars2.com/file/D4E560D3197437F0010DB4B6B2DBEA7D58E9DC27/455854.png")

        # Agregar los precios al embed
        for item_name, price in gift_prices.items():
            price_string = calculate_coins(price)
            embed.add_field(name=item_name, value=price_string, inline=False)

        # Agregar los enlaces al embed
        embed.add_field(name="\u200b", value="[Link to GOJM](https://guaridadevortus.com/comprar-vender-gojm/)", inline=True)
        embed.add_field(name="\u200b", value="[Link to GOM](https://guaridadevortus.com/como-vender-dones-del-dominio-gom/)", inline=True)

        # Enviar el embed como respuesta al comando
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(GiftPrices(bot))