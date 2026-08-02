import io
import os
import zipfile
import discord
from discord import app_commands
from discord.ext import commands
import requests

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Sync error: {e}")
    print(f"Logged in as {bot.user.name}!")

@bot.tree.command(name="getlua", description="Generate a ZIP file and get the game name using a Steam App ID")
async def getlua(interaction: discord.Interaction, app_id: str):
    await interaction.response.defer()
    
    # Fetch game name from Steam's public store API
    game_name = f"Unknown Game (App ID: {app_id})"
    try:
        url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
        response = requests.get(url).json()
        if response and str(app_id) in response and response[str(app_id)]['success']:
            game_name = response[str(app_id)]['data']['name']
    except Exception:
        pass # Fallback if request fails
    
    # Standard script content
    lua_content = f"""app.s_id = {app_id}
app.info = {{
    appid = {app_id},
    common = true
}}
"""
    
    # Create the ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr(f"{app_id}.lua", lua_content)
    zip_buffer.seek(0)
    
    zip_file_attachment = discord.File(zip_buffer, filename=f"{app_id}.zip")
    
    # Send text message displaying the game's actual name and the zip file
    await interaction.followup.send(
        content=f"🎮 **Game:** {game_name}\n📦 Here is your configuration ZIP file:",
        file=zip_file_attachment
    )

# This securely grabs your token from the cloud environment variables
bot.run(os.getenv("DISCORD_TOKEN"))