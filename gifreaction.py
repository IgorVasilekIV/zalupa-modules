"""
Some description:
Auto-reply to specific GIFs ☃️
"""


__version__ = (1, 0, 1)
# meta developer: @l0_ng, @IgorVasilekIV <-(кто это)
# meta fhsdesc: gif, auto, reply, reaction, usefull
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


from hikkatl.types import Message
from hikkatl.tl.types import Document, MessageMediaDocument
from .. import loader, utils

@loader.tds
class GifReaction(loader.Module):
    """Auto-reply to specific GIFs"""
    
    strings = {
        "name": "GifReaction",
        "no_id": "<b><emoji document_id=5339428493992162714>🚫</emoji> Reply to a GIF or provide its id.</b>",
        "not_gif": "<b><emoji document_id=5339428493992162714>🚫</emoji> This is not a GIF (or sticker/document not recognized).</b>",
        "no_args": "<b><emoji document_id=5339428493992162714>🚫</emoji> Specify text/id for reaction.\nExample:</b> <code>.addgif Ahaha, lol | 9182379218381234</code>",
        "added": "<b><emoji document_id=5339256974473199519>✅</emoji> Reaction saved!</b>\n<b>ID:</b> <code>{}</code>\n<b>Response:</b> {}",
        "removed": "<b><emoji document_id=5235927882466876283>🗑</emoji> Reaction for this GIF removed.</b>",
        "not_found": "<b><emoji document_id=5346207996789684577>🖥</emoji> This GIF is not in the database.</b>",
        "list_header": "<b><emoji document_id=5373056919688731596>📂</emoji> List of GIF reactions:</b>\n\n",
        "list_empty": "<b><emoji document_id=5373056919688731596>📂</emoji> List is empty.</b>",
        "_cfg_ignore_chats": "List of chats where the module will not work"
    }

    strings_ru = {
        "_cls_doc": "Авто-ответ на конкретные GIF",
        "no_id": "<b><emoji document_id=5339428493992162714>🚫</emoji> Сделайте реплай на GIF или укажите его айди.</b>",
        "not_gif": "<b><emoji document_id=5339428493992162714>🚫</emoji> Это не GIF (или стикер/документ не распознан).</b>",
        "no_args": "<b><emoji document_id=5339428493992162714>🚫</emoji> Укажите текст для реакции.\nПример:</b> <code>.addgif Ахах, лол</code>",
        "added": "<b><emoji document_id=5339256974473199519>✅</emoji> Реакция сохранена!</b>\n<b>ID:</b> <code>{}</code>\n<b>Ответ:</b> {}",
        "removed": "<b><emoji document_id=5235927882466876283>🗑</emoji> Реакция для этой GIF удалена.</b>",
        "not_found": "<b><emoji document_id=5346207996789684577>🖥</emoji> Этой GIF нет в базе данных.</b>",
        "list_header": "<b><emoji document_id=5373056919688731596>📂</emoji> Список реакций на GIF:</b>\n\n",
        "list_empty": "<b><emoji document_id=5373056919688731596>📂</emoji> Список пуст.</b>",
        "_cfg_ignore_chats": "Список чатов, в которых модуль не будет работать"
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "ignore_chats",
                [],
                doc=self.strings["_cfg_ignore_chats"],
                validator=loader.validators.Series(validator=loader.validators.Integer())
            )
        )

    async def client_ready(self, client, db):
        self._client = client
        self._db = db

    @loader.command(
            en_doc="<text | gif_id> / [reply to gif] - Add a reaction",
            ru_doc="<текст | айди гифки> / [реплай на гифку] - Добавить реакцию"
    )
    async def addgif(self, message: Message):
            """<текст | айди гифки> / [реплай на гифку] - Добавить реакцию"""
            reply = await message.get_reply_message()
            raw_args = utils.get_args_raw(message)
            
            gif_id = None
            text_reaction = None

            if reply and reply.media:
                if hasattr(reply.media, 'document'):
                    gif_id = str(reply.media.document.id)
                    text_reaction = raw_args
                else:
                    return await utils.answer(message, self.strings["not_gif"])
            else:
                if not raw_args or "|" not in raw_args:
                    return await utils.answer(message, self.strings["no_args"])
                
                parts = raw_args.split("|", 1)
                text_reaction = parts[0].strip()
                gif_id = parts[1].strip()

            if not gif_id or not text_reaction:
                return await utils.answer(message, self.strings["no_args"])

            reactions = self._db.get(self.strings["name"], "reactions", {})
            reactions[gif_id] = text_reaction
            self._db.set(self.strings["name"], "reactions", reactions)

            await utils.answer(message, self.strings["added"].format(gif_id, text_reaction))

    @loader.command(
            en_doc="[gif_id] / [reply to gif] - Remove a reaction",
            ru_doc="[айди гифки] / [реплай на гифку] - Удалить реакцию"
    )
    async def rmgif(self, message: Message):
            """[айди гифки] / [реплай на гифку] - Удалить реакцию"""
            
            reply = await message.get_reply_message()
            gif_id = None

            if reply and reply.media:
                if hasattr(reply.media, 'document'):
                    gif_id = str(reply.media.document.id)
                else:
                    return await utils.answer(message, self.strings["not_gif"])
            
            if not gif_id:
                args = utils.get_args_raw(message)
                if args:
                    gif_id = args.strip()

            if not gif_id:
                return await utils.answer(message, self.strings["no_id"])

            # 5. Работаем с базой данных
            reactions = self._db.get(self.strings["name"], "reactions", {})

            if gif_id in reactions:
                del reactions[gif_id]
                self._db.set(self.strings["name"], "reactions", reactions)
                await utils.answer(message, self.strings["removed"])
            else:
                await utils.answer(message, self.strings["not_found"])

    @loader.command(
            en_doc="- Show the list of saved reactions",
            ru_doc="- Показать список сохраненных реакций"
    )
    async def giflist(self, message: Message):
        """- Показать список сохраненных реакций"""
        reactions = self._db.get(self.strings["name"], "reactions", {})
        if not reactions:
            return await utils.answer(message, self.strings["list_empty"])
        
        text = self.strings["list_header"]
        for gid, response in reactions.items():
            text += f"<blockquote expandable>🔹 <b>ID:</b> <code>{gid}</code>\n• <b>Ответ:</b> {response}\n\n"
        
        await utils.answer(message, text + "</blockquote>")

    @loader.watcher()
    async def watcher(self, message: Message):
        if not isinstance(message, Message):
            return
            
        if message.out or message.sender_id == (await self._client.get_me()).id:
            return
            
        if message.chat_id in self.config["ignore_chats"]:
            return

        if not message.media or not isinstance(message.media, MessageMediaDocument):
            return
            
        document = message.media.document
        if not isinstance(document, Document):
            return
        
        reactions = self._db.get(self.strings["name"], "reactions", {})
        gif_id = str(document.id)

        if gif_id in reactions:
            await message.reply(reactions[gif_id])