from .. import loader  # Импортируем необходи
@loader.tds
class MusicSearchMod(loader.Module):
    """Модуль для поиска музыки"""

    strings = {"name": "MusicSearch"}  # Название модуля

    async def muscmd(self, message):
        """Используй .mus <аргументы> для поиска музыки"""
        args = message.raw_text.split(maxsplit=1)  # Разделяем текст команды
        if len(args) < 2:
            await message.edit("Пожалуйста, укажите, что искать.")  # Если нет аргументов
            return
        search_query = args[1]  # Получаем аргументы команды
        await message.respond(f"Найти {search_query}")  # Отправляем сообщение
        await message.delete()  # Удаляем команду
