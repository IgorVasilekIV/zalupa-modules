__version__ = (0, 5, 5)

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
                    
                    # Сортируем по количеству лайков
                    definitions = sorted(
                        data["list"], 
                        key=lambda x: x.get('thumbs_up', 0), 
                        reverse=True
                    )
                    
                    return definitions[:int(self.config["definitions"])]
        except:
            return None

    def _format_def(self, d: dict) -> str:
        """Форматируем определение"""
        def cleanup(text: str) -> str:
            """Очистка текста от разметки"""
            return text.replace('[','').replace(']','').strip()
            
        definition = cleanup(d["definition"])
        example = cleanup(d["example"]) if d.get("example") else "Нет примера"
        
        rating = f"👍 {d.get('thumbs_up', 0):,} • 👎 {d.get('thumbs_down', 0):,}"
        
        return (
            f"<b>Определение:</b>\n"
            f"{definition}\n\n"
            f"💭 <b>Пример:</b>\n"
            f"<i>{example}</i>\n\n"
            f"{rating}"
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
        formatted_defs = []
        for i, d in enumerate(defs, 1):
            formatted_defs.append(
                f"<blockquote expandable>{self._format_def(d)}</blockquote>"
            )
        
        text = "".join(formatted_defs)
        await utils.answer(message, text)