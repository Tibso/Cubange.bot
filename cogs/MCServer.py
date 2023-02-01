import nextcord
from nextcord.ext import commands, tasks
from requests import get
from mcstatus import JavaServer
from os import system

GUILD_IDS = [637782002145165342]

class MCServer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("MCServer cog loaded")

        self.check_serv.start()

    IP = get('https://api.ipify.org').text

    old_player_count = -2
    
    @tasks.loop(minutes=1)
    async def check_serv(self): 
        try:
            stats = JavaServer('localhost', 25565)
            stats_info = stats.status()

            if self.old_player_count != stats_info.players.online:
                string = str(stats_info.players.online) + "/" + str(stats_info.players.max) + " players"
                await self.bot.change_presence(status=nextcord.Status.online, activity=nextcord.Activity(type=nextcord.ActivityType.watching, name=string))

                self.old_player_count = stats_info.players.online
        except:
            if self.old_player_count != -1:
                await self.bot.change_presence(status=nextcord.Status.dnd, activity=nextcord.Activity(type=nextcord.ActivityType.watching, name="server not running"))
            
                self.old_player_count = -1
            
    @nextcord.slash_command(name="mcstart", description="Attempts to start the Minecraft server", guild_ids=GUILD_IDS)
    async def mcstart(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if self.old_player_count < 0:
            system(r'C:\Users\thiba\Cubange\start.bat')

            print(f"\nServer started by: {interaction.user}")
            await interaction.send("The server has started.", ephemeral=True)
        else:
            await interaction.send("The server is already running.", ephemeral=True)

    @nextcord.slash_command(name="mcinfo", description="Displays the Minecraft Server info", guild_ids=GUILD_IDS)
    async def mcinfo(self, interaction: nextcord.Interaction):
        await interaction.response.defer(with_message=True)

        await interaction.send(
f"""Server info:```
IP/Port:    {self.IP}:28462
Version:    1.19```"""
)

def setup(bot):
    bot.add_cog(MCServer(bot))