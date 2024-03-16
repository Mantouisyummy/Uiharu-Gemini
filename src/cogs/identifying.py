from io import BytesIO

from disnake import ApplicationCommandInteraction, Option, OptionType, File, User
from disnake.ext import commands

from src.bot import Uiharu
from src.nicknames import NicknameLocked


class Identifying(commands.Cog):
    def __init__(self, bot: Uiharu):
        self.bot = bot

    @commands.slash_command(name="nickname")
    async def nickname(self, interaction: ApplicationCommandInteraction):
        pass

    @nickname.sub_command(
        name="lock", description="鎖定一個人的名字",
        options=[
            Option(type=OptionType.user, name="user", description="要鎖定的人", required=True),
            Option(type=OptionType.boolean, name="ephemeral", description="是否要隱藏訊息", required=False)
        ]
    )
    async def nickname_lock(self, interaction: ApplicationCommandInteraction, user: User, ephemeral: bool = False):
        if not interaction.author.id in interaction.bot.owner_ids:
            return await interaction.response.send_message("❌ 你不是我的主人，你不能這麼做")

        await interaction.response.send_message("⌛ 正在讀取資料...", ephemeral=ephemeral)

        locked = interaction.bot.nickname_manager.lock_nickname(user.id)

        await interaction.edit_original_response(
            content=f"{'🔒' if locked else '🔓'} 已{'鎖定' if locked else '解鎖'} {user.mention} 的暱稱"
        )

    @nickname.sub_command(
        name="list", description="列出初春的名字記憶",
        options=[
            Option(
                name="ephemeral",
                description="是否要隱藏訊息",
                type=OptionType.boolean,
                required=False
            )
        ]
    )
    async def nickname_list(self, interaction: ApplicationCommandInteraction, ephemeral: bool = False):
        if not interaction.author.id in interaction.bot.owner_ids:
            return await interaction.response.send_message("❌ 你不是我的主人，你不能這麼做", ephemeral=ephemeral)

        await interaction.response.send_message("⌛ 正在讀取資料...", ephemeral=ephemeral)

        # noinspection PyUnresolvedReferences
        nicknames = interaction.bot.nickname_manager.list_nicknames()

        nicknames_string = BytesIO()

        for user_id, nickname in nicknames.items():
            nicknames_string.write(f"{self.bot.get_user(user_id)}({user_id}): {nickname}\n".encode("utf-8"))

        nicknames_string.seek(0)

        await interaction.edit_original_response(
            "✅ 這些是我記得的名字", file=File(fp=nicknames_string, filename="nicknames.txt")
        )

    @nickname.sub_command(
        name="set", description="告訴初春你的名字",
        options=[
            Option(
                name="name",
                description="你的名字",
                type=OptionType.string,
                required=True
            ),
            Option(
                name="user",
                description="要設定的使用者 (未指定則設定自己)",
                type=OptionType.user,
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
    async def nickname_set(self, interaction: ApplicationCommandInteraction,
                           name: str, user: User = None, ephemeral: bool = False):
        print(interaction.bot.owner_ids)
        if user and (not interaction.author.id in interaction.bot.owner_ids):
            return await interaction.response.send_message("❌ 你不是我的主人，你不能這麼做", ephemeral=ephemeral)

        if not user:
            user = interaction.author

        await interaction.response.send_message("⌛ 正在寫入資料...", ephemeral=ephemeral)

        for not_allowed_name in ["初春", "uiharu", "Uiharu", "Nathan", "Nat1an", "奈森"]:
            if (name in not_allowed_name) and (not user.id == interaction.bot.owner_id):
                return await interaction.edit_original_response("❌ You cannot use this name for some reason.")

        try:
            # noinspection PyUnresolvedReferences
            interaction.bot.nickname_manager.set_nickname(user_id=user.id, nickname=name, locked=False)
        except NicknameLocked:
            return await interaction.edit_original_response("❌ 這個人的名字被鎖定了，你不能改變它")

        await interaction.edit_original_response(f"✅ 你好，{name}！")

    @nickname.sub_command(
        name="remove", description="將你的名字從移出初春的記憶",
        options=[
            Option(
                name="user",
                description="要設定的使用者 (未指定則設定自己)",
                type=OptionType.user,
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
    async def nickname_remove(self, interaction: ApplicationCommandInteraction,
                              user: User = None, ephemeral: bool = False):
        if user and (not interaction.author.id in interaction.bot.owner_ids):
            return await interaction.response.send_message("❌ 你不是我的主人，你不能這麼做", ephemeral=ephemeral)

        if not user:
            user = interaction.author

        await interaction.response.send_message("⌛ 正在寫入資料...", ephemeral=ephemeral)

        # noinspection PyUnresolvedReferences
        original_nickname = interaction.bot.nickname_manager.remove_nickname(user_id=user.id)

        await interaction.edit_original_response(f"👋 再見了，{original_nickname}")


def setup(bot: Uiharu):
    bot.add_cog(Identifying(bot))
