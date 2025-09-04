__version__ = (1, 1, 0)

from random import choice

from telethon.tl.types import (
    InputMessagesFilterPhotos,
    Message,
)

from .. import loader, utils


class lessons_in_loveMod(loader.Module):
    '''Random picture from @lessons_in_love and @lessonsinlove channels'''
    
    strings = {
	"name": "LessonsInLove",
	"choosing": "<emoji document_id=5328311576736833844>🔴</emoji> Choosing {}...",
        "photo": "photo",
        "no_photos": "❌ No suitable photos found",
	}
    
    strings_ru = {
        "choosing": "<emoji document_id=5328311576736833844>🔴</emoji> Подбираем {}...",
        "photo": "вашу картинку(пикчу)",
        "no_photos": "❌ Не найдено подходящих картинок",
	}
    
    SEARCH_TYPES = {
		InputMessagesFilterPhotos: "photo",
	}
    
    @loader.command(
		ru_doc="- подобрать рандом картинку(пикчу)"
	)
    async def hent(self, message: Message):
        """- choose a random picture"""
        search_type = choice([
            InputMessagesFilterPhotos,
        ])
        search_type_str = self.strings(self.SEARCH_TYPES[search_type])
        
        msg = await utils.answer(message, self.strings("choosing").format(search_type_str))
        
        # Собираем сообщения из обоих каналов
        messages = []
        
        # Проверяем первый канал
        async for message_in_channel in self.client.iter_messages(
            "lessons_in_love",
            limit=100,
            filter=search_type
        ):
            if message_in_channel.sender_id == 7365208353
                messages.append(message_in_channel)
                
        # Проверяем второй канал
        async for message_in_channel in self.client.iter_messages(
            "lessonsinlove",
            limit=100,
            filter=search_type
        ):
        
        if not messages:
            await utils.answer(msg, "❌ Не найдено подходящих картинок")
            return
            
        chosed_msg = choice(messages)
        
        reply = None if not (reply := await message.get_reply_message()) else reply.id
        
        return await utils.answer_file(
            msg,
            chosed_msg,
            chosed_msg.text or "<b>Подобрал " + search_type_str + ".</b>",
            reply_to=reply
        )