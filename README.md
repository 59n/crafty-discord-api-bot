# Crafty Controller Discord Bot

A Discord bot to manage your Minecraft servers through Crafty Controller API.

## Features

- 🖥️ List all servers with live status
- ▶️ Start/Stop/Restart servers
- 📊 View server statistics (CPU, RAM, players)
- 👥 Whitelist players
- 📝 View server logs
- 💾 Create backups
- 🔧 Send custom commands
- 📱 Works everywhere: Servers, DMs, and Group Chats

## Prerequisites

- Docker and Docker Compose installed
- Discord Bot Token
- Crafty Controller API Key
- Your Discord User ID

## Quick Start

### 1. Clone the repository

git clone https://github.com/YOUR_USERNAME/crafty-discord-bot.git
cd crafty-discord-bot

### 2. Create `.env` file

Copy the example and fill in your credentials:

cp .env.example .env
nano .env # or use your preferred editor

### 3. Run with Docker

docker compose up -d

### 4. View logs

docker compose logs -f

## Configuration

Edit `.env` file with your settings:

`DISCORD_TOKEN=your_discord_bot_token_here
BOT_OWNER_ID=your_discord_user_id_here
CRAFTY_API_KEY=your_crafty_api_key_here
CRAFTY_BASE_URL=https://your-crafty-url.com`

### Getting Your Credentials

**Discord Bot Token:**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to "Bot" tab and copy the token
4. Enable "User Install" in the "Installation" tab

**Discord User ID:**
1. Enable Developer Mode in Discord (Settings > Advanced)
2. Right-click your username and "Copy User ID"

**Crafty API Key:**
1. Log into your Crafty Controller
2. Go to your user settings
3. Generate an API token

## Available Commands

- `/servers` - List all your Minecraft servers
- `/stats <server_id>` - View detailed server statistics
- `/start <server_id>` - Start a server
- `/stop <server_id>` - Stop a server
- `/restart <server_id>` - Restart a server
- `/kill <server_id>` - Force kill a server
- `/backup <server_id>` - Create a backup
- `/whitelist <server_id> [username]` - Whitelist a player
- `/command <server_id> [command]` - Send a custom command
- `/logs <server_id> [lines]` - View server logs

## Docker Commands

Start the bot
docker compose up -d

View logs
docker compose logs -f

Restart the bot
docker compose restart

Stop the bot
docker compose down

Rebuild after code changes
docker compose up -d --build

## Troubleshooting

**Bot not responding:**
- Check logs: `docker compose logs -f`
- Verify your `.env` file has correct values
- Ensure the bot token is valid

**Commands not showing in Discord:**
- Wait a few minutes for Discord to sync
- Try restarting the bot: `docker compose restart`

**Permission errors:**
- Verify BOT_OWNER_ID matches your Discord user ID
- Only the bot owner can use commands

## License

MIT License - feel free to modify and use!
