from hikkatl.types import Message
from .. import loader, utils
import asyncio

@loader.tds
class idi_Zavtra_V_TriModule(loader.Module):
    """@idiPlease"""
    
    strings = {
        "name": "naebal",
        "idi": "иди нахуй заебал чучело",
        "okay": "Хорошо, завтра в три",
    }

    async def idicmd(self, message: Message):
        """ну смешно же пиздец"""

        sent_message = await utils.answer(message, self.strings["idi"])
        await asyncio.sleep(0.25)
        await sent_message.edit(self.strings["okay"])
