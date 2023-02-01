import nextcord, wavelink
from nextcord.ext import commands

GUILD_IDS = []

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Music cog loaded")

        print("Attempting connection to Lavalink server...")
        self.bot.loop.create_task(self.connect_nodes())

    def calc_time(self, seconds: int):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        return d, h, m, s

    async def connect_nodes(self):
        await self.bot.wait_until_ready()

        await wavelink.NodePool.create_node(bot=self.bot, host='localhost', port=2333, password='youshallnotpass')

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node:wavelink.Node):
        print(f'Wavelink node: <{node.identifier}> is ready!')

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, voice_client: wavelink.Player, track: wavelink.Track, reason):
        if voice_client.queue.is_empty:
            return await voice_client.disconnect()

        next_song = voice_client.queue.get()
        await voice_client.play(next_song)

    @nextcord.slash_command(name="play", description="Plays the given song", guild_ids=GUILD_IDS)
    async def play(self, interaction: nextcord.Interaction, song: str = nextcord.SlashOption(description="The song you want to play")):
        await interaction.response.defer(with_message=True)

        if interaction.user.voice is None:
            return await interaction.send("You must be connected to a voice channel to use this feature.")

        track = await wavelink.YouTubeTrack.search(query=song, return_first=True)

        if interaction.guild.voice_client is None:
            voice_client: wavelink.Player = await interaction.user.voice.channel.connect(cls=wavelink.Player)
            print(f"Joined voice channel: {voice_client.channel}")

            await voice_client.play(track)

            d, h, m, s = self.calc_time(int(track.length))
            await interaction.send(f"Started playing: **{track.title}** - {d}d {h}h {m}m {s}s")
        else:
            voice_client: wavelink.Player = interaction.guild.voice_client

            if interaction.user.voice.channel != voice_client.channel:
                return await interaction.send("You are not connected to the voice channel.")

            await voice_client.queue.put_wait(track)

            await interaction.send(f"Added: **{track.title}** to the queue.")

    @nextcord.slash_command(name="skip", description="Skips the current song", guild_ids=GUILD_IDS)
    async def skip(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)

        voice_client: wavelink.Player = interaction.guild.voice_client

        if voice_client is None:
            return await interaction.send("The bot is not connected to a voice channel.", ephemeral=True)

        if interaction.user.voice.channel != voice_client.channel:
            return await interaction.send("You are not connected to the voice channel.", ephemeral=True)    
        
        await voice_client.seek(voice_client.track.length * 1000)
        if voice_client.is_paused():
            await voice_client.resume()

        print(f"A song has been skipped by: {interaction.user}")
        await interaction.send("The current song has been skipped.", ephemeral=True)

    @nextcord.slash_command(name="pause", description="Pauses the music", guild_ids=GUILD_IDS)
    async def pause(self, interaction: nextcord.Interaction):
        await interaction.response.defer(with_message=True)

        voice_client: wavelink.Player = interaction.guild.voice_client

        if voice_client is None:
            return await interaction.send("The bot is not connected to a voice channel.")

        if interaction.user.voice.channel != voice_client.channel:
            return await interaction.send("You are not connected to the voice channel.")    

        if not voice_client.is_playing():
            return await interaction.send("The music is already paused.")

        await voice_client.pause()
        await interaction.send("The music has been paused.")

    @nextcord.slash_command("resume", description="Resumes the music", guild_ids=GUILD_IDS)
    async def resume(self, interaction: nextcord.Interaction):
        await interaction.response.defer(with_message=True)

        voice_client: wavelink.Player = interaction.guild.voice_client

        if voice_client is None:
            return await interaction.send("The bot is not connected to a voice channel.")

        if interaction.user.voice.channel != voice_client.channel:
            return await interaction.send("You are not connected to the voice channel.")  

        if not voice_client.is_paused():
            return await interaction.send("The music is not paused.")

        await voice_client.resume()
        await interaction.send("The music has been resumed.")

    @nextcord.slash_command(name="stop", description="Stops the music and disconnects the bot", guild_ids=GUILD_IDS)
    async def stop(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)

        voice_client: wavelink.Player = interaction.guild.voice_client

        if voice_client is None:
            return await interaction.send("The bot is not connected to a voice channel.", ephemeral=True)

        if interaction.user.voice.channel != voice_client.channel:
            return await interaction.send("You are not connected to the voice channel.", ephemeral=True)

        await voice_client.stop()
        voice_client.queue.clear()
        await voice_client.disconnect()
        await interaction.send("See you soon!", ephemeral=True)

    @nextcord.slash_command(name="queue", description="Displays the current song queue", guild_ids=GUILD_IDS)
    async def queue(self, interaction: nextcord.Interaction):
        await interaction.response.defer(with_message=True)

        voice_client: wavelink.Player = interaction.guild.voice_client        

        if voice_client is None:
            return await interaction.send("The bot is not connected to a voice channel.")

        if interaction.user.voice.channel != voice_client.channel:
            return await interaction.send("You are not connected to the voice channel.")

        if voice_client.queue.is_empty:
           return await interaction.send("The song queue is empty.")

        queue = voice_client.queue.copy()
        song_count = 0
        message = "The current song queue is:\n"

        for song in queue:
            song_count += 1

            d, h, m, s = self.calc_time(int(song.length))
            message = message + f"\n**{song_count} - {song.info.get('title')}** - {d}d {h}h {m}m {s}s"

        await interaction.send(message)

def setup(bot):
    bot.add_cog(Music(bot))