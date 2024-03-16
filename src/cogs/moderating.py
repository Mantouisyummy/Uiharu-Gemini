from io import BytesIO

from disnake import ApplicationCommandInteraction, TextInputStyle, MessageCommandInteraction, ModalInteraction, \
    Option, OptionType, User, NotFound, File
from disnake.ext import commands
from disnake.ui import Modal, TextInput

from src.bot import Uiharu


class Moderating(commands.Cog):
    def __init__(self, bot: Uiharu):
        self.bot = bot

    def list_conversations(self) -> File:
        file = BytesIO()

        for user_id, conversation in self.bot.conversation_manager.conversations.items():
            file.write(
                f"{self.bot.get_user(int(user_id))}({user_id}): {conversation.nickname}\n"
                .encode("utf-8")
            )

        file.seek(0)

        return File(file, filename="conversations.txt")

    @commands.slash_command(
        name="eval", description="邪惡，超級邪惡",
        options=[
            Option(
                name="code",
                description="要執行的程式碼",
                type=OptionType.string,
                required=True
            ),
            Option(
                name="ephemeral",
                description="是否要隱藏訊息",
                type=OptionType.boolean,
                required=False
            )
        ]

    )
    async def eval(self, interaction: ApplicationCommandInteraction, code: str, ephemeral: bool = True):
        if interaction.author.id not in self.bot.owner_ids:
            return await interaction.response.send_message("❌ 你不是我的主人，你不能這麼做", ephemeral=ephemeral)

        await interaction.response.defer(ephemeral=ephemeral)

        try:
            import asyncio  # noqa
            result = eval(code)

        except Exception as e:
            result = e

        await interaction.edit_original_response(
            f"```py\n{result}\n```"
        )

    @commands.slash_command(
        name="reset", description="重設初春的記憶",
        options=[
            Option(
                name="user",
                description="要重設的使用者 (未指定則列出所有使用者)",
                type=OptionType.user,
                required=False
            ),
            Option(
                name="user_id",
                description="要重設的使用者 ID (未指定則列出所有使用者)",
                type=OptionType.string,
                required=False
            ),
            Option(
                name="ephemeral",
                description="是否要隱藏訊息",
                type=OptionType.boolean,
                required=False
            )
        ]
    )
    async def reset(self, interaction: ApplicationCommandInteraction,
                    user: User = None, user_id: str = None, ephemeral: bool = True):
        if interaction.author.id not in self.bot.owner_ids:
            return await interaction.response.send_message("❌ 你不是我的主人，你不能這麼做", ephemeral=ephemeral)

        await interaction.response.defer(ephemeral=ephemeral)

        if not user:
            try:
                user = self.bot.get_user(int(user_id))
            except TypeError:
                return await interaction.edit_original_response(
                    "📃 這些是正在進行中的對話", file=self.list_conversations()
                )
            except NotFound:
                return await interaction.edit_original_response("❌ 找不到這個使用者")

        await interaction.edit_original_response(f"⌛ 正在重設對 {user} 的記憶")

        await self.bot.conversation_manager.close_conversation(user.id)

        await interaction.edit_original_response(f"✅ 成功重設對 {user} 的記憶")

    @commands.message_command(name="刪除", description="刪除初春的訊息")
    async def delete(self, interaction: MessageCommandInteraction):
        if interaction.author.id not in self.bot.owner_ids:
            return await interaction.response.send_message("❌ 你不是我的主人，你不能這麼做", ephemeral=True)

        await interaction.target.delete()
        await interaction.response.send_message("✅ 刪除完成", ephemeral=True)

    @commands.message_command(name="編輯", description="編輯初春的訊息")
    async def edit(self, interaction: MessageCommandInteraction):
        if interaction.author.id not in self.bot.owner_ids:
            return await interaction.response.send_message("❌ 你不是我的主人，你不能這麼做", ephemeral=True)

        await interaction.response.send_modal(
            Modal(
                title="編輯訊息",
                components=[
                    TextInput(
                        style=TextInputStyle.long,
                        placeholder="訊息內容",
                        label="訊息內容",
                        value=interaction.target.content,
                        custom_id="content",
                        required=True,
                        max_length=2000
                    )
                ]
            )
        )

        def check(i):
            return i.author.id == interaction.author.id

        try:
            modal_interaction: ModalInteraction = await self.bot.wait_for("modal_submit", check=check, timeout=60)
        except TimeoutError:
            return

        await interaction.target.edit(content=modal_interaction.text_values["content"])

        await modal_interaction.response.send_message("✅ 編輯完成", ephemeral=True)


def setup(bot: Uiharu):
    bot.add_cog(Moderating(bot))
