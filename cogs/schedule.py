from discord.ext import commands, tasks
from datetime import datetime, time
import pytz

class Reminder(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.tz_col = pytz.timezone('America/Bogota')
        self.reminder.start()

    def cog_unload(self):
        self.reminder.cancel()

    def is_monday_2am(self):
        now = datetime.now(self.tz_col)
        return now.weekday() == 0 and now.hour == 2 and now.minute == 0
    

    @tasks.loop(minutes=1)
    async def reminder(self):
        if self.is_monday_2am():
            channel = self.client.get_channel(1327872662369996840)
            if channel:
                await channel.send(f"Hoy se reinicia la semana. ¡Recuerda comprar tus ASS! <@&1239969056099012628>")

    @reminder.before_loop
    async def before_reminder(self):
        await self.client.wait_until_ready()

async def setup(client):
    await client.add_cog(Reminder(client))