import discord
from discord import app_commands
from discord.ui import Modal, TextInput
import requests
import os
from typing import Optional

# Configuration from environment variables
API_KEY = os.getenv('CRAFTY_API_KEY')
BASE_URL = os.getenv('CRAFTY_BASE_URL')
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
BOT_OWNER_ID = int(os.getenv('BOT_OWNER_ID'))

# Set up intents
intents = discord.Intents.default()
bot = discord.Client(intents=intents)

# Configure tree for user install with all contexts
tree = app_commands.CommandTree(bot)

# Set global install contexts - allows user install and works everywhere
tree.allowed_installs = app_commands.AppInstallationType(guild=True, user=True)
tree.allowed_contexts = app_commands.AppCommandContext(guild=True, dm_channel=True, private_channel=True)

# Helper function for API calls
def crafty_api_call(endpoint, method="GET", data=None):
    """Make API calls to Crafty Controller"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json" if method != "POST" or data else "text/plain"
    }
    
    url = f"{BASE_URL}/api/v2/{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, data=data, headers=headers)
        elif method == "PATCH":
            response = requests.patch(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"status": "error", "error": str(e)}

# Owner check decorator
def is_owner():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id == BOT_OWNER_ID
    return app_commands.check(predicate)

# Whitelist Modal
class WhitelistModal(Modal):
    def __init__(self, server_id):
        super().__init__(title="Whitelist Player")
        self.server_id = server_id
        self.username = TextInput(
            label="Minecraft Username",
            placeholder="Enter the player's username...",
            required=True,
            max_length=16
        )
        self.add_item(self.username)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        username = self.username.value
        command = f"whitelist add {username}"
        
        result = crafty_api_call(f"servers/{self.server_id}/stdin", "POST", command)
        
        if result.get("status") == "ok":
            await interaction.followup.send(f"✅ Whitelisted **{username}**!", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Failed: {result.get('error', result)}", ephemeral=True)

# Custom Command Modal
class CommandModal(Modal):
    def __init__(self, server_id):
        super().__init__(title="Send Server Command")
        self.server_id = server_id
        self.command = TextInput(
            label="Command",
            placeholder="Enter command (without /)...",
            required=True,
            style=discord.TextStyle.short
        )
        self.add_item(self.command)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        command = self.command.value
        
        result = crafty_api_call(f"servers/{self.server_id}/stdin", "POST", command)
        
        if result.get("status") == "ok":
            await interaction.followup.send(f"✅ Sent command: `{command}`", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Failed: {result.get('error', result)}", ephemeral=True)

# ===== COMMANDS =====

@tree.command(name="servers", description="List all Minecraft servers")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@is_owner()
async def list_servers(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    
    result = crafty_api_call("servers")
    
    if result.get("status") == "ok":
        servers = result.get("data", [])
        if not servers:
            await interaction.followup.send("❌ No servers found!", ephemeral=True)
            return
        
        embed = discord.Embed(title="🖥️ Your Minecraft Servers", color=discord.Color.blue())
        
        for server in servers:
            server_id = server.get('server_id')
            server_name = server.get('server_name', 'Unknown')
            server_type = server.get('type', 'Unknown')
            server_port = server.get('server_port', 'N/A')
            
            # Get actual running status from stats
            stats_result = crafty_api_call(f"servers/{server_id}/stats")
            running = False
            players_info = "N/A"
            
            if stats_result.get("status") == "ok":
                stats = stats_result.get("data", {})
                running = stats.get("running", False)
                online = stats.get("online", 0)
                max_players = stats.get("max", 0)
                players_info = f"{online}/{max_players}"
            
            status = "🟢 Running" if running else "🔴 Offline"
            
            embed.add_field(
                name=f"{server_name}",
                value=f"**ID:** `{server_id}`\n**Status:** {status}\n**Type:** {server_type}\n**Port:** {server_port}\n**Players:** {players_info}",
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    else:
        await interaction.followup.send(f"❌ Error: {result.get('error', result)}", ephemeral=True)

@tree.command(name="start", description="Start a Minecraft server")
@app_commands.describe(server_id="The server ID (copy from /servers)")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@is_owner()
async def start_server(interaction: discord.Interaction, server_id: str):
    await interaction.response.defer(ephemeral=True)
    
    result = crafty_api_call(f"servers/{server_id}/action/start_server", "POST")
    
    if result.get("status") == "ok":
        await interaction.followup.send(f"✅ Starting server...", ephemeral=True)
    else:
        await interaction.followup.send(f"❌ Failed to start: {result.get('error', result)}", ephemeral=True)

@tree.command(name="stop", description="Stop a Minecraft server")
@app_commands.describe(server_id="The server ID (copy from /servers)")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@is_owner()
async def stop_server(interaction: discord.Interaction, server_id: str):
    await interaction.response.defer(ephemeral=True)
    
    result = crafty_api_call(f"servers/{server_id}/action/stop_server", "POST")
    
    if result.get("status") == "ok":
        await interaction.followup.send(f"✅ Stopping server...", ephemeral=True)
    else:
        await interaction.followup.send(f"❌ Failed to stop: {result.get('error', result)}", ephemeral=True)

@tree.command(name="restart", description="Restart a Minecraft server")
@app_commands.describe(server_id="The server ID (copy from /servers)")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@is_owner()
async def restart_server(interaction: discord.Interaction, server_id: str):
    await interaction.response.defer(ephemeral=True)
    
    result = crafty_api_call(f"servers/{server_id}/action/restart_server", "POST")
    
    if result.get("status") == "ok":
        await interaction.followup.send(f"✅ Restarting server...", ephemeral=True)
    else:
        await interaction.followup.send(f"❌ Failed to restart: {result.get('error', result)}", ephemeral=True)

@tree.command(name="kill", description="Force kill a Minecraft server")
@app_commands.describe(server_id="The server ID (copy from /servers)")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@is_owner()
async def kill_server(interaction: discord.Interaction, server_id: str):
    await interaction.response.defer(ephemeral=True)
    
    result = crafty_api_call(f"servers/{server_id}/action/kill_server", "POST")
    
    if result.get("status") == "ok":
        await interaction.followup.send(f"✅ Force killing server...", ephemeral=True)
    else:
        await interaction.followup.send(f"❌ Failed to kill: {result.get('error', result)}", ephemeral=True)

@tree.command(name="backup", description="Backup a Minecraft server")
@app_commands.describe(server_id="The server ID (copy from /servers)")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@is_owner()
async def backup_server(interaction: discord.Interaction, server_id: str):
    await interaction.response.defer(ephemeral=True)
    
    result = crafty_api_call(f"servers/{server_id}/action/backup_server", "POST")
    
    if result.get("status") == "ok":
        await interaction.followup.send(f"✅ Backing up server...", ephemeral=True)
    else:
        await interaction.followup.send(f"❌ Failed to backup: {result.get('error', result)}", ephemeral=True)

@tree.command(name="stats", description="Get server statistics")
@app_commands.describe(server_id="The server ID (copy from /servers)")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@is_owner()
async def server_stats(interaction: discord.Interaction, server_id: str):
    await interaction.response.defer(ephemeral=True)
    
    result = crafty_api_call(f"servers/{server_id}/stats")
    
    if result.get("status") == "ok":
        stats = result.get("data", {})
        server_info = stats.get("server_id", {})
        
        # Parse player list
        import json
        players_raw = stats.get("players", "[]")
        try:
            players = json.loads(players_raw) if isinstance(players_raw, str) else players_raw
        except:
            players = []
        player_names = ", ".join(players) if players else "None"
        
        server_name = server_info.get('server_name', 'Server') if isinstance(server_info, dict) else 'Server'
        
        embed = discord.Embed(
            title=f"📊 {server_name} Statistics",
            color=discord.Color.green() if stats.get("running") else discord.Color.red()
        )
        
        # Truncate server ID for display
        display_id = str(server_id)
        if len(display_id) > 20:
            display_id = display_id[:8] + "..." + display_id[-8:]
        
        embed.add_field(name="Server ID", value=f"`{display_id}`", inline=False)
        embed.add_field(name="Status", value="🟢 Running" if stats.get("running") else "🔴 Offline", inline=True)
        embed.add_field(name="CPU Usage", value=f"{stats.get('cpu', 0)}%", inline=True)
        embed.add_field(name="RAM Usage", value=f"{stats.get('mem', 'N/A')} ({stats.get('mem_percent', 0)}%)", inline=True)
        embed.add_field(name="Players", value=f"{stats.get('online', 0)}/{stats.get('max', 0)}", inline=True)
        embed.add_field(name="Version", value=stats.get('version', 'Unknown'), inline=True)
        embed.add_field(name="Port", value=str(stats.get('server_port', 'N/A')), inline=True)
        embed.add_field(name="World Size", value=stats.get('world_size', 'N/A'), inline=True)
        embed.add_field(name="Ping", value="✅" if stats.get('int_ping_results') == "True" else "❌", inline=True)
        embed.add_field(name="Online Players", value=player_names[:1024], inline=False)
        
        if stats.get('crashed'):
            embed.add_field(name="⚠️ Warning", value="Server has crashed!", inline=False)
        if stats.get('updating'):
            embed.add_field(name="🔄 Status", value="Server is updating...", inline=False)
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    else:
        await interaction.followup.send(f"❌ Error: {result.get('error', result)}", ephemeral=True)

@tree.command(name="whitelist", description="Whitelist a player")
@app_commands.describe(server_id="The server ID (copy from /servers)", username="Optional: username (or leave empty for modal)")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@is_owner()
async def whitelist(interaction: discord.Interaction, server_id: str, username: Optional[str] = None):
    if username:
        await interaction.response.defer(ephemeral=True)
        command = f"whitelist add {username}"
        result = crafty_api_call(f"servers/{server_id}/stdin", "POST", command)
        
        if result.get("status") == "ok":
            await interaction.followup.send(f"✅ Whitelisted **{username}**!", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Failed: {result.get('error', result)}", ephemeral=True)
    else:
        modal = WhitelistModal(server_id)
        await interaction.response.send_modal(modal)

@tree.command(name="command", description="Send a custom command to the server")
@app_commands.describe(server_id="The server ID (copy from /servers)", command="Optional: command (or leave empty for modal)")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@is_owner()
async def send_command(interaction: discord.Interaction, server_id: str, command: Optional[str] = None):
    if command:
        await interaction.response.defer(ephemeral=True)
        result = crafty_api_call(f"servers/{server_id}/stdin", "POST", command)
        
        if result.get("status") == "ok":
            await interaction.followup.send(f"✅ Sent: `{command}`", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Failed: {result.get('error', result)}", ephemeral=True)
    else:
        modal = CommandModal(server_id)
        await interaction.response.send_modal(modal)

@tree.command(name="logs", description="Get recent server logs")
@app_commands.describe(server_id="The server ID (copy from /servers)", lines="Number of lines (default: 20)")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@is_owner()
async def get_logs(interaction: discord.Interaction, server_id: str, lines: Optional[int] = 20):
    await interaction.response.defer(ephemeral=True)
    
    result = crafty_api_call(f"servers/{server_id}/logs")
    
    if result.get("status") == "ok":
        log_lines = result.get("data", [])
        recent_logs = log_lines[-lines:] if len(log_lines) > lines else log_lines
        
        log_text = "\n".join(recent_logs)
        
        if len(log_text) > 1900:
            log_text = "... (truncated)\n" + log_text[-1850:]
        
        if log_text:
            await interaction.followup.send(f"📄 **Last {len(recent_logs)} lines:**\n``````", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ No logs available", ephemeral=True)
    else:
        await interaction.followup.send(f"❌ Error: {result.get('error', result)}", ephemeral=True)

# Error handler
@tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "❌ Only the bot owner can use this command!",
                ephemeral=True
            )
    else:
        error_msg = f"❌ An error occurred: {str(error)}"
        if not interaction.response.is_done():
            await interaction.response.send_message(error_msg, ephemeral=True)
        else:
            await interaction.followup.send(error_msg, ephemeral=True)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user}")
    print(f"✅ Commands synced with user install support!")
    print(f"🔑 Owner ID: {BOT_OWNER_ID}")
    print(f"📱 Commands work in: Servers, DMs, and Group Chats")

bot.run(DISCORD_TOKEN)
