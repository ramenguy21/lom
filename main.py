import discord
import os
from dotenv import load_dotenv

bot = discord.Bot(command_prefix='!')
connections = {}

load_dotenv()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

@bot.slash_command(name="hey", description="say hi")
async def hey(ctx : discord.ApplicationContext):
    await ctx.respond(f"hi there {ctx.author}")

@bot.slash_command(name="record", description="ddos the bev")
async def record(ctx : discord.ApplicationContext):
    voice = ctx.author.voice

    if not voice:
        await ctx.respond("Not in a voice channel, idk where to go lol")
        return

    vc = await voice.channel.connect()
    connections.update({ctx.guild.id : vc})
    
    vc.start_recording(
            discord.sinks.WaveSink(),
            once_done,
            ctx.channel
    )
    await ctx.respond("Initiating gaand phaar device")

async def once_done(sink: discord.sinks, channel: discord.TextChannel, *args):  # Our voice client already passes these in.
    recorded_users = [  # A list of recorded users
        f"<@{user_id}>"
        for user_id, audio in sink.audio_data.items()
    ]
    await sink.vc.disconnect()  # Disconnect from the voice channel.
    files = [discord.File(audio.file, f"{user_id}.{sink.encoding}") for user_id, audio in sink.audio_data.items()]  # List down the files.
    await channel.send(f"finished recording audio for: {', '.join(recorded_users)}.", files=files)  # Send a message with the accumfiles.

@bot.command()
async def stop_recording(ctx):
    if ctx.guild.id in connections:  # Check if the guild is in the cache.
        vc = connections[ctx.guild.id]
        vc.stop_recording()  # Stop recording, and call the callback (once_done).
        del connections[ctx.guild.id]  # Remove the guild from the cache.
        await ctx.delete()  # And delete.
    else:
        await ctx.respond("I am currently not recording here.")

# env.get()
bot.run(os.getenv('TOKEN'))
