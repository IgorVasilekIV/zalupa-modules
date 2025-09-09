# чатгпт кормит, больные мозги тоже
#
# meta developer: @HikkaZPM
#
# The module is made as a joke, all coincidences are random :P
#
#       кот вахуи
#       /\_____/\
#      /  o   o  \
#     ( ==  ^  == )
#      )         (
#     (           )
#    ( (  )   (  ) )
#   (__(__)___(__)__)
#
from hikkatl.types import Message
from .. import loader, utils

@loader.tds
class SSend(loader.Module):
    """Простой модуль для отправки любого текста"""

    strings = {
        "name": "SSend",
        "error": "❌ Пожалуйста, укажите текст для отправки.",
    }

        def __init__(self):
            self.config = loader.ModuleConfig(
                loader.ConfigValue(
                    "link_preview",
                    False,
                    lambda: "Disable/enable link preview" 
                    validator=loader.validators.Boolean(),
                ),
            )

    @loader.command(ru_doc="Отправить текст с эмодзи")
    async def send(self, message: Message):
        """Отправить текст с эмодзи"""
        args = utils.get_args_raw(message)

        if not args:
            await message.edit(self.strings["error"])
        else:
            await message.delete()
            await message.client.send_message(
                message.to_id,
                args,
                link_preview=self.config["link_preview"]
            )
