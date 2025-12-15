# meta banner: https://x0.at/tGxk.jpg
# meta pic: https://x0.at/tGxk.jpg
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

# код делала ИИ, не выёбывайтесь 🤔

import asyncio
import logging
from telethon import functions
from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class PCardMod(loader.Module):
    """
    Модуль для автоматической отправки 'ткарточка' каждые 4 часа (да)
    """
    
    strings = {
        "name": "PCard",
        "started": "<b>✅ Таймер запущен!</b>\nСлово <code>ткарточка</code> будет отправляться каждые 4 часа в этом чате.",
        "already_running": "<b>⚠️ Таймер уже запущен в этом чате!</b>",
        "stopped": "<b>🛑 Таймер остановлен в этом чате.</b>",
        "not_running": "<b>⚠️ В этом чате таймер не был запущен.</b>",
        "stopped_all": "<b>🛑 Все таймеры во всех чатах остановлены.</b>",
        "no_chats": "<b>📂 Список чатов с таймером пуст.</b>",
        "chat_list_header": "<b>📋 Чаты с активным таймером:</b>\n<blockquote expandable>",
        "chat_item": "• <a href='{}'>{}</a>\n"
    }

    def __init__(self):
        self.tasks = {}

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        chats = self.db.get("PCard", "chats", [])
        for chat_id in chats:
            self._start_task(chat_id)

    def _start_task(self, chat_id):
        if chat_id not in self.tasks:
            self.tasks[chat_id] = asyncio.create_task(self._sender_loop(chat_id))

    def _stop_task(self, chat_id):
        if chat_id in self.tasks:
            self.tasks[chat_id].cancel()
            del self.tasks[chat_id]

    async def _sender_loop(self, chat_id):
        """Бесконечный цикл отправки"""
        try:
            while True:
                try:
                    await self.client.send_message(chat_id, "ткарточка")
                except Exception as e:
                    logger.error(f"Error sending message in {chat_id}: {e}")
                    # Если бот кикнут или чат удален, останавливаем задачу и чистим БД
                    if "ChatWriteForbiddenError" in str(e) or "ChannelPrivateError" in str(e):
                        chats = self.db.get("PCard", "chats", [])
                        if chat_id in chats:
                            chats.remove(chat_id)
                            self.db.set("PCard", "chats", chats)
                        break
                
                await asyncio.sleep(14400)
        except asyncio.CancelledError:
            pass

    @loader.command(ru_doc="Запустить таймер отправки в текущем чате")
    async def pcardcmd(self, message):
        """Запускает таймер с отправкой 'ткарточка' каждые 4 часа."""
        chat_id = utils.get_chat_id(message)
        chats = self.db.get("PCard", "chats", [])

        if chat_id in chats:
            return await utils.answer(message, self.strings("already_running"))

        chats.append(chat_id)
        self.db.set("PCard", "chats", chats)
        self._start_task(chat_id)
        await utils.answer(message, self.strings("started"))

    @loader.command(ru_doc="Остановить таймер в текущем чате")
    async def pstopcmd(self, message):
        """Останавливает таймер там где запустили."""
        chat_id = utils.get_chat_id(message)
        chats = self.db.get("PCard", "chats", [])

        if chat_id not in chats:
            return await utils.answer(message, self.strings("not_running"))

        chats.remove(chat_id)
        self.db.set("PCard", "chats", chats)
        self._stop_task(chat_id)
        await utils.answer(message, self.strings("stopped"))

    @loader.command(ru_doc="Остановить таймер во всех чатах")
    async def pstopallcmd(self, message):
        """Останавливает во всех чатах, не зависимо от того были ли они."""
        chats = self.db.get("PCard", "chats", [])
        
        for chat_id in chats:
            self._stop_task(chat_id)
            
        self.db.set("PCard", "chats", [])
        await utils.answer(message, self.strings("stopped_all"))

    @loader.command(ru_doc="Показать список чатов с активным таймером")
    async def pchatscmd(self, message):
        """Показывает в каких чатах запущено."""
        chats = self.db.get("PCard", "chats", [])
        
        if not chats:
            return await utils.answer(message, self.strings("no_chats"))

        text = self.strings("chat_list_header")
        
        for chat_id in chats:
            try:
                chat = await self.client.get_entity(chat_id)
                title = utils.escape_html(chat.title)
                
                if hasattr(chat, "username") and chat.username:
                    link = f"https://t.me/{chat.username}"
                else:
                    cid = str(chat_id).replace("-100", "")
                    link = f"https://t.me/c/{cid}/1"
                
                text += self.strings("chat_item").format(link, title)
            except:
                text += self.strings("chat_item").format("#", f"Недоступный чат ({chat_id})")

        await utils.answer(message, text + "</blockquote>")