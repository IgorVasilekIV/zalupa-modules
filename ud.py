__version__ = (0, 8, 2)

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
from telethon.tl.types import Message
from hikka.inline.types import InlineCall
import aiohttp

@loader.tds
class UrbanDictionaryMod(loader.Module):
    """Поиск слов в Urban Dictionary"""
    
    strings = {
        "name": "UrbanDict",
        "no_term": "🤔 <b>Что искать?</b>",
        "no_results": "😕 <b>Не найдено</b>",
        "error": "❌ <b>{}</b>",
        "choose_lang": "🌐 <b>Выберите язык для перевода:</b>",
        "translating": "🔄 Перевожу...",
        "translated": "🌐 <b>Перевод на {}:</b>\n\n{}"
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
        
    async def client_ready(self, client, db):
        """Инициализация при загрузке модуля"""
        self._client = client
        self._db = db


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

    async def translate_callback(self, call: InlineCall, text: str, lang: str):
        """Обработчик нажатия на кнопку перевода"""
        try:
            await call.answer(self.strings["translating"])
            
            # Используем встроенный переводчик Hikka
            translated = await self._client.translate(
                text=text,
                dest=lang
            )
            
            buttons = [
                [
                    {"text": "🇬🇧 English", "callback": self.translate_callback, "args": (text, "en")},
                    {"text": "🇷🇺 Русский", "callback": self.translate_callback, "args": (text, "ru")},
                ],
                [
                    {"text": "🇩🇪 Deutsch", "callback": self.translate_callback, "args": (text, "de")},
                    {"text": "🇫🇷 Français", "callback": self.translate_callback, "args": (text, "fr")},
                ],
                [
                    {"text": "🇪🇸 Español", "callback": self.translate_callback, "args": (text, "es")},
                    {"text": "🇯🇵 日本語", "callback": self.translate_callback, "args": (text, "ja")},
                ]
            ]
            
            lang_names = {
                "en": "English 🇬🇧",
                "ru": "Русский 🇷🇺",
                "de": "Deutsch 🇩🇪",
                "fr": "Français 🇫🇷",
                "es": "Español 🇪🇸",
                "ja": "日本語 🇯🇵"
            }
            
            await call.edit(
                text=self.strings["translated"].format(
                    lang_names.get(lang, lang),
                    translated
                ),
                reply_markup=buttons
            )
        except Exception as e:
            await call.answer(f"❌ Ошибка: {str(e)}", show_alert=True)

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
        buttons = []
        
        for i, d in enumerate(defs, 1):
            def_text = self._format_def(d)
            formatted_defs.append(f"<blockquote expandable>{def_text}</blockquote>")
            
            # Добавляем кнопки перевода для каждого определения
            buttons.append([
                {"text": "🇬🇧 English", "callback": self.translate_callback, "args": (def_text, "en")},
                {"text": "🇷🇺 Русский", "callback": self.translate_callback, "args": (def_text, "ru")},
            ])
            buttons.append([
                {"text": "🇩🇪 Deutsch", "callback": self.translate_callback, "args": (def_text, "de")},
                {"text": "🇫🇷 Français", "callback": self.translate_callback, "args": (def_text, "fr")},
            ])
            buttons.append([
                {"text": "🇪🇸 Español", "callback": self.translate_callback, "args": (def_text, "es")},
                {"text": "🇯🇵 日本語", "callback": self.translate_callback, "args": (def_text, "ja")},
            ])
            
            if i < len(defs):  # Добавляем разделитель между определениями
                buttons.append([{"text": "═══════════", "action": "noop"}])
        
        text = "".join(formatted_defs)
        
        await self.inline.form(
            message=message,
            text=text,
            reply_markup=buttons
        )