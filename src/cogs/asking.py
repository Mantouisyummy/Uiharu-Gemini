import logging
from os import getenv

from aiohttp import ClientSession
from disnake import Message, Webhook, ButtonStyle, DMChannel, AllowedMentions
from disnake.ext import commands
from disnake.ui import Button

from src.bot import Uiharu
from src.utils import remove_mentions, keep_typing


class Asking(commands.Cog):
    def __init__(self, bot: Uiharu):
        self.bot = bot

        self.webhook: Webhook = Webhook.from_url(
            getenv("LOG_WEBHOOK"), session=ClientSession(), bot_token=getenv("TOKEN")
        )

    @commands.Cog.listener(name="on_message")
    async def talk(self, message: Message):
        if message.author.bot:
            return

        if message.author == self.bot.user:
            return

        if self.bot.user.id not in [mention.id for mention in message.mentions]:
            if not isinstance(message.channel, DMChannel):
                return

        if len(message.content) > 800:
            await message.reply("❌ | 請不要輸入超過800個字元的訊息")
            return

        await self.bot.wait_until_ready()

        if message.guild:
            data_string = f"GUILD_ID={message.guild.id} CHANNEL_ID={message.channel.id} USER_ID={message.author.id}"
            author_string = f"{message.author} from #{message.channel.name}"

        else:
            data_string = f"(DM) USER_ID={message.author.id}"
            author_string = f"{message.author} from DM"

        log_message = await self.webhook.send(
            content=f"{message.content}\n\n"
                    f"[Original]({message.jump_url})\n"
                    f"```{data_string}\n\n==========\n"
                    f"{message.content}```",
            username=author_string,
            avatar_url=message.author.avatar.url or message.author.default_avatar.url,
            components=[Button(label="Go to message", url=message.jump_url, style=ButtonStyle.url)],
            wait=True
        )

        logging.info(f"New question from {message.author}: {message.content}")

        task = self.bot.loop.create_task(keep_typing(message.channel))

        try:
            conversation = await self.bot.conversation_manager.get_conversation(message.author.id)
            answer = await conversation.ask(remove_mentions(message.content))

        except Exception as error:
            logging.error(f"Error while processing question from {message.author}: {error}")
            await message.reply("❌ | 發生了一些錯誤，請稍後再試")
            return

        finally:
            task.cancel()

        reply_message = await message.channel.send(
            answer,
            reference=message,
            mention_author=True,
            allowed_mentions=AllowedMentions.none()
        )

        await self.webhook.send(
            content=f"{answer}\n\n"
                    f"[Replies to]({log_message.jump_url}) | [Original]({reply_message.jump_url})\n"
                    f"```{answer}```",
            avatar_url=self.bot.user.avatar.url,
            username=self.bot.user.display_name,
            components=[
                Button(
                    label="Replies to",
                    url=log_message.jump_url,
                    style=ButtonStyle.url,
                ),
                Button(
                    label="Go to message",
                    url=reply_message.jump_url,
                    style=ButtonStyle.url
                )
            ]
        )

    # # This feature is hard coded and only available for A.C.G.M City (https://discord.gg/acgmcity)
    # @commands.Cog.listener(name="on_member_join")
    # async def welcome(self, member: Member):
    #     if not member.guild.id == 952461973013037106:
    #         return
    #
    #     if member.id == self.bot.user.id:
    #         return
    #
    #     await self.bot.wait_until_ready()
    #
    #     channel = self.bot.get_channel(952461973491159076)
    #
    #     conversation = await self.bot.conversation_manager.get_conversation(member.id)
    #
    #     answer = await conversation.ask(self.bot, f"你好，我是 {member.display_name}")
    #
    #     await channel.send(
    #         content=f"{member.mention} {answer}",
    #         embed=Embed(
    #             title="📝 來自 Nat1an",
    #             description="這個歡迎訊息是由 AI 自動生成的\n"
    #                         f"你可以透過在訊息中提及 {self.bot.user.mention} 來繼續這個對話\n"
    #                         "如果你有任何問題，歡迎直接在頻道中提出\n"
    #                         "希望你在 A.C.G.M City 過得開心！",
    #             color=0x2b2d31
    #         )
    #     )


def setup(bot: Uiharu):
    bot.add_cog(Asking(bot))
