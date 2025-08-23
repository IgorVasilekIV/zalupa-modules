__version__ = (0, 4, 3)

"""
Search words definitions in Urban Dictionary through their API

TODO: add inline buttons for translation (ru/en) using googletrans / self._client.translate_message
"""

# чатгпт кормит, больные мозги тоже
#
# meta banner: https://files.catbox.moe/swqxd1.png
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
#

from .. import loader, utils
import aiohttp

@loader.tds
class UrbanDictionaryMod(loader.Module):
    """Поиск слов в Urban Dictionary"""
    
    strings = {
        "name": "UrbanDict",
        "no_term": "🤔 <b>Что искать?</b>",
        "no_results": "😕 <b>Не найдено</b>",
        "error": "❌ <b>{}</b>"
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "definitions",
                3,
                doc="Количество определений для вывода",
                validator=loader.validators.Integer(minimum=1, maximum=8)
            )
        )


    async def _get_definition(self, term: str):
        """Получаем определение слова"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.urbandictionary.com/v0/define",
                    params={"term": term},
                    timeout=5
                ) as resp:
                    if resp.status != 200:
                        return None
                        
                    data = await resp.json()
                    if not data.get("list"):
                        return None
                        
                    return data["list"][:self.config["definitions"]]
        except:
            return None

    def _format_def(self, d: dict) -> str:
        """Форматируем определение"""
        return (
            f"<b>{d['thumbs_up']}👍</b>\n"
            f"{d['definition'].replace('[','').replace(']','')[:150]}..."
        )

    @loader.unrestricted
    async def udcmd(self, message):
        """[слово] - найти определение"""
        term = utils.get_args_raw(message)
        if not term:
            await utils.answer(message, self.strings["no_term"])
            return

        defs = await self._get_definition(term)
        if not defs:
            await utils.answer(message, self.strings["no_results"])
            return

        # собираем в одну кучу
        text = "\n\n".join(f"<blockquote expandable>{self._format_def(d)}\n</blockquote>" for i, d in enumerate(defs))
        await utils.answer(message, text)
            


