import discord
from discord.ext import commands, tasks
import datetime
import re
import json
from typing import Optional, Tuple

class TimeConverter:
    time_regex = re.compile(r"""
        (?:(?P<seconds>\d+)(?:s|seconds|second|sec))?
        (?:(?P<minutes>\d+)(?:m))?
        (?:(?P<hours>\d+)(?:h|hours|hour))?
        (?:(?P<days>\d+)(?:d|days|day))?
        (?:(?P<months>\d+)(?:mo|months|month|))?
        (?:(?P<weeks>\d+)(?:w|weeks|week))?
    """, re.VERBOSE)

    @classmethod
    def parse_time(cls, time_str: str) -> Optional[datetime.timedelta]:
        matches = cls.time_regex.match(time_str)
        if not matches:
            return None

        params = {name: int(param) for name, param in matches.groupdict().items() if param}
        if not params:
            return None

        if 'months' in params:
            params['days'] = params.get('days', 0) + params.pop('months') * 30

        return datetime.timedelta(**params)

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminders = []
        self.load_reminders()
        self.check_reminders.start()

    def cog_unload(self):
        self.check_reminders.cancel()
        self.save_reminders()

    def load_reminders(self):
        try:
            with open('reminders.json', 'r') as f:
                data = json.load(f)
                self.reminders = [
                    {
                        'user_id': reminder['user_id'],
                        'channel_id': reminder['channel_id'],
                        'target_id': reminder.get('target_id'),
                        'message': reminder['message'],
                        'time': datetime.datetime.fromisoformat(reminder['time']),
                        'original_message': reminder.get('original_message', '')
                    }
                    for reminder in data
                ]
        except FileNotFoundError:
            self.reminders = []

    def save_reminders(self):
        with open('reminders.json', 'w') as f:
            json.dump([{
                'user_id': reminder['user_id'],
                'channel_id': reminder['channel_id'],
                'target_id': reminder.get('target_id'),
                'message': reminder['message'],
                'time': reminder['time'].isoformat(),
                'original_message': reminder.get('original_message', '')
            } for reminder in self.reminders], f)

    @tasks.loop(seconds=30)
    async def check_reminders(self):
        now = datetime.datetime.now()
        reminders_to_remove = []

        for reminder in self.reminders:
            if reminder['time'] <= now:
                user = self.bot.get_user(reminder['user_id'])
                if user:
                    embed = discord.Embed(
                        title="Reminder",
                        color=discord.Color.blue(),
                    )
                    value = reminder['message']
                    embed.add_field(
                        name="Message",
                        value=reminder['message'],
                        inline=False
                    )
                    embed.add_field(
                        name="Created At",
                        value=reminder['time'].strftime('%Y-%m-%d %H:%M:%S'),
                        inline=False
                    )
                    embed.add_field(
                        name="By",
                        value=f"<@{reminder['user_id']}>",
                        inline=False
                    )
                    mention = f"<@{reminder['target_id'] or reminder['user_id']}>"
                    try:
                        await user.send(embed=embed)
                    except discord.HTTPException:
                        pass
                reminders_to_remove.append(reminder)

        for reminder in reminders_to_remove:
            self.reminders.remove(reminder)

        if reminders_to_remove:
            self.save_reminders()

    async def parse_remind_command(self, ctx, content: str) -> Tuple[Optional[int], Optional[int], str, datetime.timedelta]:
        content = content.strip()
        target_id = None
        channel_id = None
        
        if content.startswith('me '):
            target_id = ctx.author.id
            content = content[3:]
        elif content.startswith('meorother '):
            content = content[10:]

        channel_match = re.match(r'^<#(\d+)>\s+(.+)$', content)
        if channel_match:
            channel_id = int(channel_match.group(1))
            content = channel_match.group(2)

        words = content.split()
        time_str = words[0]
        message = ' '.join(words[1:])
        time_delta = TimeConverter.parse_time(time_str)
        if not time_delta:
            raise ValueError("Invalid time format")

        if not channel_id:
            channel_id = ctx.channel.id

        if target_id is None and 'meorother' in ctx.message.content:
            user_mention_match = re.search(r'<@!?(\d+)>', message)
            if user_mention_match:
                target_id = int(user_mention_match.group(1))
            else:
                target_id = ctx.author.id

        return target_id, channel_id, message, time_delta

    @commands.command(name='remind')
    async def remind(self, ctx, *, content: str):
        try:
            target_id, channel_id, message, time_delta = await self.parse_remind_command(ctx, content)
            reminder_time = datetime.datetime.now() + time_delta

            reminder = {
                'user_id': ctx.author.id,
                'channel_id': channel_id,
                'target_id': target_id,
                'message': message,
                'time': reminder_time,
                'original_message': f"Set on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }

            self.reminders.append(reminder)
            self.save_reminders()

            embed = discord.Embed(
                title="",
                color=discord.Color.green(),
            )
            embed.add_field(
                name=" ",
            value=f"⏰ I will remind <@{ctx.author.id}> to **{message}** "
                  f"<t:{int(reminder_time.timestamp())}:R> (<t:{int(reminder_time.timestamp())}:f>)",
            inline=False
            )
            await ctx.send(embed=embed)

        except ValueError as e:
            await ctx.send(f"❌ Error: {str(e)}")
        except Exception as e:
            await ctx.send("❌ An error occurred while setting the reminder.")
            print(f"Reminder error: {e}")

    @commands.command(name='reminders')
    async def list_reminders(self, ctx):
        user_reminders = [r for r in self.reminders if r['user_id'] == ctx.author.id]
        
        if not user_reminders:
            await ctx.send("You have no active reminders.")
            return

        embed = discord.Embed(
            title="📝 Your Reminders",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )

        for i, reminder in enumerate(user_reminders, 1):
            time_left = reminder['time'] - datetime.datetime.now()
            hours, remainder = divmod(int(time_left.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours}h {minutes}m {seconds}s"
            channel = self.bot.get_channel(reminder['channel_id'])
            channel_str = channel.mention if channel else "Unknown channel"

            embed.add_field(
                name=f"Reminder #{i}",
                value=f"**Message:** {reminder['message']}\n"
                      f"**Channel:** {channel_str}\n"
                      f"**Time Left:** {time_str}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='remove')
    async def remove_reminder(self, ctx, index: int):
        user_reminders = [r for r in self.reminders if r['user_id'] == ctx.author.id]
        
        if not user_reminders or index > len(user_reminders) or index < 1:
            await ctx.send("❌ Invalid reminder index.")
            return

        reminder_to_remove = user_reminders[index - 1]
        self.reminders.remove(reminder_to_remove)
        self.save_reminders()

        await ctx.send(f"✅ Reminder #{index} has been removed.")

    @commands.command(name='removeall')
    async def remove_all_reminders(self, ctx):
        user_reminders = [r for r in self.reminders if r['user_id'] == ctx.author.id]

        if not user_reminders:
            await ctx.send("You have no active reminders to remove.")
            return

        # Eliminar todos los recordatorios del usuario
        self.reminders = [r for r in self.reminders if r['user_id'] != ctx.author.id]
        self.save_reminders()

        await ctx.send("✅ All your reminders have been removed.")

async def setup(bot):
    await bot.add_cog(Reminders(bot))
