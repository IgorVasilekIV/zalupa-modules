# -*- coding: utf-8 -*-

"""
😘 fork info: added blacklist, `|` as a separator, response deletion after time
"""

# ------------------------------------------------------------
# Module: KsenonAFK
# Description: Универсальный AFK модуль с поддержкой кастом сообщения и премиум статуса.
# Author: @kmodules
# ------------------------------------------------------------
# Licensed under the GNU AGPLv3
# https:/www.gnu.org/licenses/agpl-3.0.html
# ------------------------------------------------------------
# Author: @MeKsenon
# Commands: .afk .unafk .ignorusers .timeafk
# scope: hikka_only
# meta banner: https://i.ibb.co/gy5xbPd/d4be263e-63b5-42e1-ac2b-0dac067b0623.jpg
# meta developer: @kmodules
# ------------------------------------------------------------

from .. import loader, utils
from telethon import types, functions
import time
import datetime
import logging
import subprocess
from collections import defaultdict
import asyncio

__version__ = (1, 1, 1)

name = "KsenonAFK"
logger = logging.getLogger(name)

@loader.tds
class KsenonAFKMod(loader.Module):
    """Универсальный AFK модуль с поддержкой кастом сообщения и премиум статуса."""

    strings = {
        "name": "KsenonAFK",
        "gone": "<emoji document_id=5870948572526022116>✋</emoji> <b>I'm now in AFK mode</b>\n<emoji document_id=5870695289714643076>👤</emoji> <b>Last seen:</b> Just now\n<emoji document_id=5870729937215819584>⏰️</emoji> <b>Reason:</b> <i>{}</i>",
        "gone_with_time": "<emoji document_id=5870948572526022116>✋</emoji> <b>I'm now in AFK mode</b>\n<emoji document_id=5870695289714643076>👤</emoji> <b>Last seen:</b> Just now\n<emoji document_id=5873146865637133757>🎤</emoji> <b>Will be back at:</b> <b>{}</b>\n<emoji document_id=5870729937215819584>⏰️</emoji> <b>Reason:</b> <i>{}</i>",
        "back": "<emoji document_id=5883964170268840032>👤</emoji> <b>No longer in AFK mode.</b>",
        "afk": "<emoji document_id=5870948572526022116>✋</emoji> <b>I'm in AFK mode</b>\n<emoji document_id=5870695289714643076>👤</emoji> <b>Last seen:</b> {} ago",
        "afk_reason": "<emoji document_id=5870948572526022116>✋</emoji> <b>I'm in AFK mode</b>\n<emoji document_id=5870695289714643076>👤</emoji> <b>Last seen:</b> {} ago\n<emoji document_id=5870729937215819584>⏰️</emoji> <b>Reason:</b> <i>{}</i>",
        "afk_reason_time": "<emoji document_id=5870948572526022116>✋</emoji> <b>I'm in AFK mode</b>\n<emoji document_id=5870695289714643076>👤</emoji> <b>Last seen:</b> {} ago\n<emoji document_id=5873146865637133757>🎤</emoji> <b>Will be back at:</b> <b>{}</b>\n<emoji document_id=5870729937215819584>⏰️</emoji> <b>Reason:</b> <i>{}</i>",
        "default_afk_message": "<emoji document_id=5870948572526022116>✋</emoji> <b>Сейчас я в AFK режиме</b>\n<emoji document_id=5870695289714643076>👤</emoji> <b>Был в сети:</b> {was_online} назад\n{reason_text}{come_time}",
        "reason_text": "<emoji document_id=5870729937215819584>⏰️</emoji> <b>Ушел по причине:</b> <i>{reason}</i>\n",
        "come_text": "<emoji document_id=5873146865637133757>🎤</emoji> <b>Прийду в:</b> <b>{come_time}</b>",
        "no_reason": "Нету",
        "ignore_set": "✅ Установлено ограничение: {} сообщений за {} минут в одном чате",
        "time_limit_set": "✅ Установлено ограничение: {} сообщений за {} минут (ЛС: {} сообщений)"
    }

    strings_ru = {
        "gone": "<emoji document_id=5870948572526022116>✋</emoji> <b>Сейчас я в AFK режиме</b>\n<emoji document_id=5870695289714643076>👤</emoji> <b>Был в сети:</b> Только что\n<emoji document_id=5870729937215819584>⏰️</emoji> <b>Ушел по причине:</b> <i>{}</i>",
        "gone_with_time": "<emoji document_id=5870948572526022116>✋</emoji> <b>Сейчас я в AFK режиме</b>\n<emoji document_id=5870695289714643076>👤</emoji> <b>Был в сети:</b> Только что\n<emoji document_id=5873146865637133757>🎤</emoji> <b>Прийду в:</b> <b>{}</b>\n<emoji document_id=5870729937215819584>⏰️</emoji> <b>Ушел по причине:</b> <i>{}</i>",
        "back": "<emoji document_id=5883964170268840032>👤</emoji><b>Больше не в режиме AFK.</b>",
        "afk": "<emoji document_id=5870948572526022116>✋</emoji> <b>Сейчас я в AFK режиме</b>\n<emoji document_id=5870695289714643076>👤</emoji> <b>Был в сети</b> {} назад",
        "afk_reason": "<emoji document_id=5870948572526022116>✋</emoji> <b>Сейчас я в AFK режиме</b>\n<emoji document_id=5870695289714643076>👤</emoji> <b>Был в сети</b> {} назад\n<emoji document_id=5870729937215819584>⏰️</emoji> <b>Ушел по причине:</b> <i>{}</i>",
        "afk_reason_time": "<emoji document_id=5870948572526022116>✋</emoji> <b>Сейчас я в AFK режиме</b>\n<emoji document_id=5870695289714643076>👤</emoji> <b>Был в сети</b> {} назад\n<emoji document_id=5873146865637133757>🎤</emoji> <b>Прийду в:</b> <b>{}</b>\n<emoji document_id=5870729937215819584>⏰️</emoji> <b>Ушел по причине:</b> <i>{}</i>",
        "default_afk_message": "<emoji document_id=5870948572526022116>✋</emoji> <b>Сейчас я в AFK режиме</b>\n<emoji document_id=5870695289714643076>👤</emoji> <b>Был в сети:</b> {was_online} назад\n{reason_text}{come_time}",
        "reason_text": "<emoji document_id=5870729937215819584>⏰️</emoji> <b>Ушел по причине:</b> <i>{reason}</i>\n",
        "come_text": "<emoji document_id=5873146865637133757>🎤</emoji> <b>Прийду в:</b> <b>{come_time}</b>",
        "no_reason": "Нету",
        "ignore_set": "✅ Установлено ограничение: {} сообщений за {} минут в одном чате",
        "time_limit_set": "✅ Установлено ограничение: {} сообщений за {} минут (ЛС: {} сообщений)"
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "alwaysAnswer",
                False,
                lambda: "Отвечать всегда когда тэгнули.",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "setPremiumStatus",
                True,
                lambda: "Ставить премиум статус при афк.",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "timeZone",
                "UTC",
                lambda: "Таймзона",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "custom_message",
                "{default}",
                lambda: "Кастом AFK сообщение. Функции:\n{was_online} - последний раз в сети\n{reason} - AFK причина\n{come_time} - Время возвращения\n{default} - Дефолт сообщение.",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "blacklist_chats",
                [],
                lambda: "Айди чатов, в которых не будет работать модуль",
                validator=loader.validators.Series(loader.validators.Integer())
            ),
            loader.ConfigValue(
                "customEmojiStatus",
                4969889971700761796,
                lambda: "Здесь вы можете поставить кастомный премиум статус. Взять Document ID статуса легко, отправьте премиум стикер, напишите e r.text и там же выйдет document_id. Вставьте только цифры.",
                validator=loader.validators.Integer()
            ),
            loader.ConfigValue(
                "ignoredChats",
                [],
                lambda: "Список ID чатов, в которых не будут отправляться AFK сообщения",
                validator=loader.validators.Series(validator=loader.validators.TelegramID())
            ),
            loader.ConfigValue(
                "deleteResponseTime",
                3.5,
                lambda: "Время в секундах, через которое будет удаляться AFK ответ\nЕсли 0 то не будет удаляться",
                validator=loader.validators.Float()
            )

        )
        self.answered_users = set()
        self.chat_messages = defaultdict(list)
        self.ignore_limit = None 
        self.ignore_time = None
        self.pm_limit = None
        self.chat_limit = None
        self.time_interval = None

    async def client_ready(self, client, db):
        self._db = db
        self._me = await client.get_me()
        self.client = client
        self._old_status = None

    def _get_timezone(self):
        try:
            process = subprocess.Popen(['timedatectl', '|', 'grep', '"Time zone"'],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    shell=True)
            output, _ = process.communicate()
            timezone = output.decode().split(': ')[1].strip()
            return timezone
        except Exception:
            return "UTC"

    def _format_custom_message(self, was_online, reason=None, come_time=None):
        reason_text = self.strings["reason_text"].format(reason=reason) if reason and reason != self.strings["no_reason"] else ""
        come_time_text = self.strings["come_text"].format(come_time=come_time) if come_time else ""
        default_message = self.strings["default_afk_message"].format(
            was_online=was_online,
            reason_text=reason_text,
            come_time=come_time_text
        )
        
        custom_message = self.config["custom_message"]
        if custom_message == "{default}":
            return default_message
            
        return custom_message.format(
            was_online=was_online,
            reason=reason if reason else self.strings["no_reason"],
            come_time=come_time if come_time else "",
            default=default_message
        )

    @loader.command(ru_doc="[причина] | [время] - Установить режим AFK.")
    async def afk(self, message):
        """[reason] | [time] - Set AFK mode status."""
        args = utils.get_args_raw(message)
        reason = None
        time_val = None

        if args:
            parts = args.split('|', 1)
            reason = parts[0].strip()

            if len(parts) > 1:
                time_val = parts[1].strip()

        if reason and reason.lower() == self.strings["no_reason"].lower():
            reason = None
        
        if not reason:
            reason = None
        
        if time_val and time_val.lower() == self.strings["no_reason"].lower():
            time_val = None
        
        if not time_val:
            time_val = None

        if self.config["setPremiumStatus"]:
            try:
                me = await self.client.get_me()
                if me.emoji_status:
                    self._old_status = me.emoji_status
                await self.client(functions.account.UpdateEmojiStatusRequest(
                    emoji_status=types.EmojiStatus(
                        document_id=self.config["customEmojiStatus"]
                    )
                ))
            except Exception as e:
                logger.error(f"Failed to update emoji status: {e}")

        self._db.set(name, "afk", reason or True)
        self._db.set(name, "gone", time.time())
        self._db.set(name, "return_time", time_val)
        self.answered_users.clear()
        self.chat_messages.clear()

        preview_message = "<emoji document_id=5870730156259152122>😀</emoji> <b>AFK режим включен!</b>\n<emoji document_id=5877700484453634587>✈️</emoji> <b>KsenonAFK будет отвечать вам этим сообщением:</b>\n\n"
        preview = self._format_custom_message("Только что", reason, time_val)
        
        await utils.answer(message, preview_message + preview)

    @loader.command(ru_doc="Выйти из режима AFK")
    async def unafk(self, message):
        """Exit AFK mode"""
        self._db.set(name, "afk", False)
        self._db.set(name, "gone", None)
        self._db.set(name, "return_time", None)
        self.answered_users.clear()
        self.chat_messages.clear()

        if self.config["setPremiumStatus"] and self._old_status:
            try:
                await self.client(functions.account.UpdateEmojiStatusRequest(
                    emoji_status=self._old_status
                ))
            except Exception as e:
                logger.error(f"Failed to restore emoji status: {e}")

        await utils.answer(message, self.strings["back"])

        await asyncio.sleep(self.config["deleteResponseTime"])
        if self.config["deleteResponseTime"] > 0:
            await message.delete()

    @loader.command(ru_doc="<кол-во> <минуты> - Установить ограничение сообщений в чате")
    async def ignorusers(self, message):
        """<count> <minutes> - Set message limit per chat"""
        args = utils.get_args(message)
        if len(args) != 2:
            return await message.edit("❌ Необходимо указать количество сообщений и время в минутах")
        
        try:
            msg_limit = int(args[0])
            time_limit = int(args[1])
        except ValueError:
            return await message.edit("❌ Аргументы должны быть числами")

        self.ignore_limit = msg_limit
        self.ignore_time = time_limit * 60
        
        await message.edit(self.strings["ignore_set"].format(msg_limit, time_limit))

    @loader.command(ru_doc="<минуты> <макс.сообщений> - Установить временной лимит сообщений") 
    async def timeafk(self, message):
        """<minutes> <max_msgs> - Set time-based message limits"""
        args = utils.get_args(message)
        if len(args) != 2:
            return await message.edit("❌ Необходимо указать интервал в минутах и максимальное количество сообщений")
        
        try:
            interval = int(args[0])
            max_msgs = int(args[1])
        except ValueError:
            return await message.edit("❌ Аргументы должны быть числами")

        self.time_interval = interval * 60
        self.pm_limit = 2  
        self.chat_limit = max_msgs
        
        await message.edit(self.strings["time_limit_set"].format(max_msgs, interval, 2))

    def _check_limits(self, chat_id, is_pm=False):
        current_time = time.time()
        
        if self.ignore_limit and self.ignore_time:
            self.chat_messages[chat_id] = [msg_time for msg_time in self.chat_messages[chat_id] 
                                         if current_time - msg_time < self.ignore_time]
            if len(self.chat_messages[chat_id]) >= self.ignore_limit:
                return False

        if self.time_interval:
            limit = self.pm_limit if is_pm else self.chat_limit
            recent_msgs = [msg_time for msg_time in self.chat_messages[chat_id] 
                          if current_time - msg_time < self.time_interval]
            if len(recent_msgs) >= limit:
                return False
            self.chat_messages[chat_id] = recent_msgs

        self.chat_messages[chat_id].append(current_time)
        return True

    async def watcher(self, message):
        if not isinstance(message, types.Message):
            return

        chat_id = utils.get_chat_id(message)
        
        if abs(chat_id) in self.config["blacklist_chats"]:
            return

        if message.mentioned or getattr(message.to_id, "user_id", None) == self._me.id:
            # Проверяем, не находится ли чат в списке игнорируемых
            if message.chat_id in self.config["ignoredChats"]:
                return

            afk_state = self.get_afk()
            if not afk_state:
                return

            user = await utils.get_user(message)
            if user.is_self or user.bot or user.verified:
                return

            if not self.config["alwaysAnswer"] and user.id in self.answered_users:
                return

            is_pm = isinstance(message.to_id, types.PeerUser)
            chat_id_limit = user.id if is_pm else chat_id

            if not self._check_limits(chat_id_limit, is_pm):
                return

            if not self.config["alwaysAnswer"]:
                self.answered_users.add(user.id)

            now = datetime.datetime.now().replace(microsecond=0)
            gone = datetime.datetime.fromtimestamp(
                self._db.get(name, "gone")
            ).replace(microsecond=0)
            diff = now - gone

            return_time = self._db.get(name, "return_time", None)
            reason = afk_state if isinstance(afk_state, str) else None

            response = self._format_custom_message(str(diff), reason, return_time)
            
            msg = await utils.answer(message, response, reply_to=message)
            await asyncio.sleep(3.5)
            await msg.delete()


    def get_afk(self):
        return self._db.get(name, "afk", False)