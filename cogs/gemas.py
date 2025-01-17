import discord
from discord.ext import commands
from discord import app_commands
import requests

class GW2Gemas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="gemas", description="Muestra las tasas de conversión de gemas")
    async def gemas(self, interaction: discord.Interaction, cantidad: int):
        """
        Muestra cuánto cuestan las gemas en oro.
        
        Parameters:
        cantidad (par): Cantidad de gemas para calcular
        """
        await interaction.response.defer()

        try:
            if cantidad <= 0:
                await interaction.followup.send("La cantidad debe ser mayor que 0.")
                return

            # Para comprar gemas necesitamos consultar cuánto oro cuesta la cantidad de gemas
            estimated_gold = cantidad * 2000  # Estimación inicial
            coins_to_gems_url = f"https://api.guildwars2.com/v2/commerce/exchange/coins?quantity={estimated_gold}"
            

            # Hacemos las consultas
            buy_response = requests.get(coins_to_gems_url).json()

            # Procesamos el costo de comprar gemas
            coins_per_gem = buy_response.get('coins_per_gem', 0)
            total_cost = cantidad * coins_per_gem
            gold_cost = total_cost // 10000
            silver_cost = (total_cost % 10000) // 100
            copper_cost = total_cost % 100
            # Creamos el embed
            embed = discord.Embed(
                title="Cambio de divisa",
                color=discord.Color.red()
            )

            # Formato para compra de gemas
            embed.add_field(
                name=f"{cantidad:,} gemas te costarían",
                value=f" {gold_cost:,} <:gold:1328507096324374699> {silver_cost} <:silver:1328507117748879422> {copper_cost} <:Copper:1328507127857418250>",
                inline=False
            )

            await interaction.followup.send(embed=embed)

        except KeyError as e:
            await interaction.followup.send(f"Error al procesar la respuesta de la API: {str(e)}")
        except requests.RequestException as e:
            await interaction.followup.send(f"Error al conectar con la API: {str(e)}")
        except Exception as e:
            await interaction.followup.send(f"Error inesperado: {str(e)}")

async def setup(bot):
    await bot.add_cog(GW2Gemas(bot))