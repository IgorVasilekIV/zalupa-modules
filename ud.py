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
from telethon.tl.types import InlineKeyboardMarkup, InlineKeyboardButton
import aiohttp
import logging
import json

logger = logging.getLogger(__name__)

UD_API_KEY = "99729790b5mshd8ec94082f78c14p1dbb97jsn52ae508bea0d"

@loader.tds
class UrbanDictionaryMod(loader.Module):
    """Поиск сленговых значений в UrbanDictionary, пишите на английском для лучшего поиска (перевод в будующем)"""

    strings = {"name": "UrbanDictionary"}
    
    def __init__(self):
        self._ud_cache = {}

    async def ud_search(self, term: str):
        """Запрос к Urban Dictionary API"""
        url = "https://mashape-community-urban-dictionary.p.rapidapi.com/define"
        headers = {
            "X-RapidAPI-Key": UD_API_KEY,
            "X-RapidAPI-Host": "mashape-community-urban-dictionary.p.rapidapi.com"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params={"term": term}) as resp:
                    if resp.status != 200:
                        return {"error": f"API Error: {resp.status}"}
                    return (await resp.json()).get("list", [])[:3]
        except Exception as e:
            logger.error(f"Urban error: {e}")
            return {"error": str(e)}

    async def format_definition(self, item: dict, current_page: int, total_pages: int) -> str:
        """Форматирует определение для отображения"""
        definition = item.get("definition", "No definition").replace("[", "").replace("]", "")
        example = item.get("example", "No example").replace("[", "").replace("]", "")
        
        return (
            f"📖 Страница {current_page + 1}/{total_pages}\n\n"
            f"👍 {item.get('thumbs_up', 0)} | 👎 {item.get('thumbs_down', 0)}\n"
            f"📝 <b>Определение:</b>\n<i>{definition[:250]}</i>\n\n"
            f"💬 <b>Пример:</b>\n<i>{example[:200]}</i>"
        )

    @loader.unrestricted
    async def udcmd(self, message: Message):
        """Поиск обозначения"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<emoji document_id=5237993272109967450>❌</emoji> Укажите слово для поиска!")
            return

        result = await self.ud_search(args)

        if isinstance(result, dict) and "error" in result:
            await utils.answer(message, f"<emoji document_id=5210952531676504517>❌</emoji> Ошибка: {result['error']}")
            return

        if not result:
            await utils.answer(message, f"<emoji document_id=5316509307255137126>🔍</emoji> Нет результатов для '{args}'")
            return

        # Сохраняем результаты и текущую страницу
        self._ud_cache = {
            "results": result,
            "term": args,
            "page": 0
        }

        # Создаем инлайн кнопки
        keyboard = [
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=f"ud_nav:{0}:prev"
                ),
                InlineKeyboardButton(
                    text="Вперед ➡️",
                    callback_data=f"ud_nav:{0}:next"
                )
            ]
        ]

        # Форматируем первый результат
        response = await self.format_definition(result[0], 0, len(result))

        await message.respond(
            response,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def ud_nav_callback(self, call):
        """Обработчик нажатий на кнопки навигации"""
        if not call.data.startswith("ud_nav:"):
            return

        # Получаем текущую страницу и направление
        _, current_page, direction = call.data.split(":")
        current_page = int(current_page)

        if not self._ud_cache:
            await call.answer("❌ Данные устарели, сделайте новый поиск")
            return

        results = self._ud_cache["results"]
        new_page = current_page

        if direction == "next" and current_page < len(results) - 1:
            new_page = current_page + 1
        elif direction == "prev" and current_page > 0:
            new_page = current_page - 1
        
        # Обновляем кнопки
        keyboard = [
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=f"ud_nav:{new_page}:prev"
                ),
                InlineKeyboardButton(
                    text="Вперед ➡️",
                    callback_data=f"ud_nav:{new_page}:next"
                )
            ]
        ]

        # Форматируем результат для новой страницы
        response = await self.format_definition(results[new_page], new_page, len(results))

        await call.edit(
            response,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

