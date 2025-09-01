from .. import loader

@loader.tds
class HelloModule(loader.Module):
    """Пример: реагируем на сообщение без префикса"""

    strings = {"name": "HelloWatcher"}

    async def watcher(self, m):
        # 1. Проверяем, что это твои сообщения (чтобы не триггериться на всех подряд)
        if m.sender_id != (await m.client.get_me()).id:
            return

        # 2. Проверяем текст (без учёта регистра и пробелов)
        if m.raw_text.lower().strip() == "привет":
            await m.reply("О, ты написал без префикса!")