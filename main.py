import os
import requests
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
FORTNITE_KEY = os.getenv("FORTNITE_API_KEY")

if not FORTNITE_KEY:
    raise ValueError("❌ La clave de Fortnite no se cargó. Verifica tu archivo .env")

print(f"🔐 API Key cargada: {FORTNITE_KEY[:8]}...")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.tree.command(name="stats", description="Muestra estadísticas de Fortnite")
@app_commands.describe(nombre="Nombre del jugador")
async def stats(interaction: discord.Interaction, nombre: str = "Ninja"):
    await interaction.response.defer()

    headers = {"Authorization": FORTNITE_KEY}
    lookup_url = f"https://fortniteapi.io/v1/lookup?username={nombre}"

    try:
        lookup_response = requests.get(lookup_url, headers=headers)
        lookup_data = lookup_response.json()

        if lookup_response.status_code != 200 or not lookup_data.get("result"):
            raise ValueError("No se pudo encontrar el jugador.")

        account_id = lookup_data.get("account_id")
        stats_url = f"https://fortniteapi.io/v1/stats?account={account_id}"
        stats_response = requests.get(stats_url, headers=headers)
        stats_data = stats_response.json()

        global_stats = stats_data.get("global_stats", {})

        if not global_stats:
            raise ValueError("No se encontraron estadísticas globales.")

        # Obtener estadísticas por modalidad
        solo = global_stats.get("solo", {})
        duo = global_stats.get("duo", {})
        squad = global_stats.get("squad", {})

        def format_stats(mode_name, stats):
            if not stats:
                return f"**{mode_name}**: Sin datos.\n"
            return (
                f"**{mode_name}**\n"
                f"🏆 Victorias: {stats.get('placetop1', 0)}\n"
                f"🔫 Kills: {stats.get('kills', 0)}\n"
                f"💀 K/D: {stats.get('kd', 'N/A')}\n"
                f"🎮 Partidas: {stats.get('matchesplayed', 0)}\n"
            )

        embed = discord.Embed(
            title=f"📊 Estadísticas de {nombre}",
            color=0x1E90FF
        )

        embed.add_field(name="🎯 Modo Solo", value=format_stats("Solo", solo), inline=False)
        embed.add_field(name="👥 Modo Duo", value=format_stats("Duo", duo), inline=False)
        embed.add_field(name="👨‍👩‍👧‍👦 Modo Squad", value=format_stats("Squad", squad), inline=False)

        await interaction.followup.send(embed=embed)

    except Exception as e:
        print(f"❌ Excepción atrapada: {e}")
        embed = discord.Embed(
            title="❌ Error",
            description=f"No se pudieron obtener estadísticas.\n{str(e)}",
            color=0xFF0000
        )
        await interaction.followup.send(embed=embed)

if __name__ == "__main__":
    bot.run(TOKEN)
