__version__ = (2, 3, 2)

"""
😘 fork info: Inline buttons in PM (Allow/Deny/Block); auto-allow contacts; bots always allowed; auto-block after 3 msgs + notify (Saved Messages); pretty .allowed listing
"""

from .. import loader, utils
from telethon import functions, types
import logging

logger = logging.getLogger(__name__)

@loader.tds
class AntiPMMod(loader.Module):
    """Anti-PM with inline buttons (Hikka inline.form), auto-allow contacts, auto-block after 3 msgs, notifications"""

    strings = {
        "name": "Anti-PM",
        "pm_off": "<b>Теперь вы принимаете сообщения от всех пользователей.</b>",
        "pm_on": "<b>Вы перестали принимать сообщения от пользователей.</b>",
        "pm_allowed": "<b>Я разрешил {} писать мне.</b>",
        "pm_deny": "<b>Я запретил {} писать мне.</b>",
        "blocked": "<b>{} был занесён в Черный Список.</b>",
        "unblocked": "<b>{} был удалён из Черного Списке.</b>",
        "addcontact": "<b>{} добавлен в контакты.</b>",
        "delcontact": "<b>{} удалён из контактов.</b>",
        "who_to_block": "<b>Укажите, кого блокировать.</b>",
        "who_to_unblock": "<b>Укажите, кого разблокировать.</b>",
        "who_to_contact": "<b>Укажите, кого добавить в контакт.</b>",
        "who_to_delcontact": "<b>Укажите, кого удалить из контактов.</b>",
        "no_args": "<b>Нет аргументов или реплая.</b>",
        "not_pm": "<b>Это не личное сообщение.</b>",
        "allowed_header": "<b>Список разрешённых пользователей:</b>\n",
        "_cfg_custom_message": "Кастомное сообщение при автоответе на ЛС",
    }

    strings_ru = {**strings}

    def __init__(self):
        self.me = None
        # config: only custom_message
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "custom_message",
                "Привет! У меня включён автоблок. Напиши всё в одном сообщении или ожидай ответа.",
                lambda: self.strings("_cfg_custom_message"),
            ),
        )
        self.auto_allow_contacts = True

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.me = await client.get_me()

    # -------- Commands --------
    async def pmcmd(self, message):
        """Используй: .pm — включить/выключить анти-PM (переключатель)."""
        pm = self.db.get("Anti-PM", "pm")
        if pm is not True:
            await utils.answer(message, self.strings["pm_off"])
            self.db.set("Anti-PM", "pm", True)
        else:
            await utils.answer(message, self.strings["pm_on"])
            self.db.set("Anti-PM", "pm", False)

    async def allowcmd(self, message):
        """Используй: .allow — разрешить этому пользователю писать вам в личку."""
        if not message.is_private:
            return await message.edit(self.strings["not_pm"])
        user = await message.client.get_entity(message.chat_id)
        allowed = set(self.db.get("Anti-PM", "allowed", []))
        allowed.add(user.id)
        self.db.set("Anti-PM", "allowed", list(allowed))
        self.db.set("Anti-PM", f"count_{user.id}", 0)
        await utils.answer(message, self.strings["pm_allowed"].format(user.first_name))

    async def blockcmd(self, message):
        """Используй: .block — заблокировать пользователя (реплай/аргумент)."""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        try:
            if message.is_private:
                user = await message.client.get_entity(message.chat_id)
            else:
                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                else:
                    if not args:
                        return await message.edit(self.strings["who_to_block"])
                    user = await message.client.get_entity(int(args) if args.isnumeric() else args)
            await message.client(functions.contacts.BlockRequest(user))
            await utils.answer(message, self.strings["blocked"].format(user.first_name))
        except Exception:
            logger.exception("Error in .block command")

    async def allowedcmd(self, message):
        """Используй: .allowed — посмотреть список разрешённых пользователей."""
        try:
            allowed = self.db.get("Anti-PM", "allowed", [])
            if not allowed:
                return await utils.answer(message, "<b>Список пуст.</b>")
            text = self.strings["allowed_header"]
            number = 0
            for uid in allowed:
                number += 1
                try:
                    u = await self.client.get_entity(int(uid))
                    name = u.first_name or "User"
                    text += f"{number}. <a href=tg://user?id={u.id}>{name}</a> | <code>{u.id}</code>\n"
                except Exception:
                    text += f"{number}. Удалённый аккаунт | <code>{uid}</code>\n"
                if len(text) > 3000:
                    text += "\n<b>И т.д. (много пользователей)</b>"
                    break
            await utils.answer(message, text)
        except Exception:
            logger.exception("Error in .allowed command")

    async def disallowcmd(self, message):
        """Используй: .disallow — убрать пользователя из разрешённых (реплай/в лс/по id)."""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        try:
            if message.is_private:
                user = await message.client.get_entity(message.chat_id)
            else:
                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                else:
                    if not args:
                        return await message.edit(self.strings["no_args"])
                    user = await message.client.get_entity(int(args) if args.isnumeric() else args)
        except Exception:
            return await message.edit("<b>Не удалось найти пользователя.</b>")

        try:
            allowed = set(self.db.get("Anti-PM", "allowed", []))
            if int(user.id) in allowed:
                allowed.discard(int(user.id))
                self.db.set("Anti-PM", "allowed", list(allowed))
                self.db.set("Anti-PM", f"count_{user.id}", 0)
                await utils.answer(message, self.strings.get("pm_deny", "<b>Пользователь убран из разрешённых.</b>").format(user.first_name))
            else:
                await utils.answer(message, "<b>Пользователь и так не в списке разрешённых.</b>")
        except Exception:
            logger.exception("Error in .disallow command")


    async def reportcmd(self, message):
            """User report for spam."""
            args = utils.get_args_raw(message)
            reply = await message.get_reply_message()
            if message.chat_id != (await message.client.get_me()).id and message.is_private:
                user = await message.client.get_entity(message.chat_id)
            else:
                if args:
                    user = await message.client.get_entity(
                        args if not args.isnumeric() else int(args)
                    )
                if reply:
                    user = await message.client.get_entity(reply.sender_id)
                else:
                    return await message.edit("<b>Who I must report?</b>")
    
            await message.client(functions.messages.ReportSpamRequest(peer=user.id))
            await message.edit("<b>You get report for spam!</b>")

    def _is_allowed(self, uid):
        return uid in self.db.get("Anti-PM", "allowed", [])

    def _get_call_uid(self, call):
        """Попытки найти user id в объекте call/message. Возвращает int или None."""
        try:
            # попытка через call.message.to_id.user_id
            m = getattr(call, "message", None)
            if m:
                to_id = getattr(m, "to_id", None)
                if to_id and getattr(to_id, "user_id", None):
                    return int(to_id.user_id)
                # через peer_id.user_id
                peer = getattr(m, "peer_id", None)
                if peer and getattr(peer, "user_id", None):
                    return int(peer.user_id)
                # через chat / chat.id / chat_id
                chat = getattr(m, "chat", None)
                if chat and getattr(chat, "id", None):
                    return int(chat.id)
                if getattr(m, "chat_id", None):
                    return int(m.chat_id)
            # через поля самого call (sender_id / from_id)
            if getattr(call, "sender_id", None):
                return int(call.sender_id)
            if getattr(call, "from_id", None):
                return int(call.from_id)
            # если data присутствует и содержит id (на случай), парсим числа
            data = None
            try:
                data = call.data.decode() if isinstance(call.data, (bytes, bytearray)) else call.data
            except Exception:
                data = None
            if isinstance(data, str):
                for part in data.split("_"):
                    if part.isdigit():
                        return int(part)
        except Exception:
            logger.exception("Error while extracting uid from callback")
        return None

    def _parse_call_data(self, call):
            """Достаём action и uid из call.data"""
            data = None
            try:
                data = call.data.decode() if isinstance(call.data, (bytes, bytearray)) else str(call.data)
            except Exception:
                pass
            if not data or ":" not in data:
                return None, None
            action, uid_str = data.split(":", 1)
            try:
                uid = int(uid_str)
            except Exception:
                uid = None
            return action, uid

    async def _btn_allow(self, call, uid: int):
        if call.from_user.id != uid:
            return await call.answer("❌ Эта кнопка не для тебя.", alert=True)
    
        allowed = set(self.db.get("Anti-PM", "allowed", []))
        allowed.add(uid)
        self.db.set("Anti-PM", "allowed", list(allowed))
        self.db.set("Anti-PM", f"count_{uid}", 0)
    
        await call.edit(f"✅ Разрешено писать: <a href=tg://user?id={uid}>{uid}</a>")
        await self.client.send_message("me", f"✅ Разрешён {uid}")
        await call.answer("Разрешено.")
    
    async def _btn_deny(self, call, uid: int):
        if call.from_user.id != uid:
            return await call.answer("❌ Эта кнопка не для тебя.", alert=True)
    
        await call.edit(f"❌ Отклонено: <a href=tg://user?id={uid}>{uid}</a>")
        await call.answer("Отклонено.")
    
    async def _btn_block(self, call, uid: int):
        if call.from_user.id != uid:
            return await call.answer("❌ Эта кнопка не для тебя.", alert=True)
    
        try:
            user = await self.client.get_entity(uid)
            await self.client(functions.contacts.BlockRequest(user))
        except Exception:
            try:
                await self.client(functions.contacts.BlockRequest(id=uid))
            except Exception:
                pass
    
        await call.edit(f"🔒 Заблокирован: <a href=tg://user?id={uid}>{uid}</a>")
        await self.client.send_message("me", f"🔒 Заблокирован {uid}")
        await call.answer("Заблокирован.")
                   
    # -------- Watcher --------
    async def watcher(self, message):
        """Слежение за входящими ЛС — авто-ответ, кнопки, счётчик и авто-блок."""
        try:
            if not message.is_private:
                return
            if message.sender_id == (await self.client.get_me()).id:
                return

            pm = self.db.get("Anti-PM", "pm")
            if pm is True:
                return

            user = await utils.get_user(message)
            uid = message.sender_id

            # боты всегда пропускаем
            if user and getattr(user, "bot", False):
                try:
                    allowed = set(self.db.get("Anti-PM", "allowed", []))
                    if uid not in allowed:
                        allowed.add(uid)
                        self.db.set("Anti-PM", "allowed", list(allowed))
                except Exception:
                    logger.exception("Error auto-allowing bot")
                return

            # авто-пропуск контактов (жёстко включено)
            if self.auto_allow_contacts:
                try:
                    who = await self.client.get_entity(uid)
                    if isinstance(who, types.User) and who.contact:
                        allowed = set(self.db.get("Anti-PM", "allowed", []))
                        if uid not in allowed:
                            allowed.add(uid)
                            self.db.set("Anti-PM", "allowed", list(allowed))
                        return
                except Exception:
                    logger.exception("Error checking contacts for auto-allow")

            if self._is_allowed(uid):
                return

            key = f"count_{uid}"
            cnt = int(self.db.get("Anti-PM", key, 0)) + 1
            self.db.set("Anti-PM", key, cnt)

            if cnt == 1:
                text = self.config["custom_message"]
                try:
                    await self.inline.form(
                        text=f"❗ Новый контакт <a href=tg://user?id={uid}>{uid}</a> написал:\n\n{message.text}",
                        reply_markup=[
                            [
                                {"text": "✅ Разрешить", "callback": self._btn_allow, "args": (uid,)},
                                {"text": "❌ Запретить", "callback": self._btn_deny, "args": (uid,)},
                                {"text": "🔒 Заблокировать", "callback": self._btn_block, "args": (uid,)},
                            ]
                        ],
                        chat="me"
                    )
                    self.db.set("Anti-PM", f"prompt_{uid}", getattr(sent, "id", 0))
                except Exception:
                    logger.exception("Error sending inline form in watcher")

            if cnt >= 3:
                try:
                    await self.client(functions.contacts.BlockRequest(uid))
                except Exception:
                    logger.exception("Auto block failed in watcher")
                self.db.set("Anti-PM", key, 0)
                try:
                    prompt_id = self.db.get("Anti-PM", f"prompt_{uid}")
                    if prompt_id:
                        try:
                            await self.client.edit_message(message.chat_id, prompt_id, f"🔒 Авто-блок: <a href=tg://user?id={uid}>{uid}</a>")
                        except Exception:
                            logger.exception("Failed to edit prompt after auto-block")
                        self.db.set("Anti-PM", f"prompt_{uid}", 0)
                except Exception:
                    logger.exception("Error handling prompt cleanup after auto-block")
                try:
                    await self.client.send_message(uid, f"❗ <b>{user.first_name if user else uid}</b> (<code>{uid}</code>) прислал 3 сообщения и был автоматически заблокирован.")
                except Exception:
                    logger.exception("Failed to send notification to Saved Messages after auto-block")
        except Exception:
            logger.exception("Unhandled error in watcher")
