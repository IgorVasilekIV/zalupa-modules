__version__ = (2, 3, 0)

"""
😘 fork info: Inline buttons in PM (Allow/Deny/Block); auto-allow contacts; bots always allowed; auto-block after 3 msgs + notify (Saved Messages); pretty .allowed listing
"""

# @Sekai_Yoneya (main author btw)

from .. import loader, utils
from telethon import functions, types, events, Button
import logging

logger = logging.getLogger(__name__)

@loader.tds
class AntiPMMod(loader.Module):
    """Anti-PM with inline buttons, auto-allow contacts, auto-block after 3 msgs, notifications"""

    strings = {
        "name": "Anti-PM",
        "pm_off": "<b>Теперь вы принимаете сообщения от всех пользователей.</b>",
        "pm_on": "<b>Вы перестали принимать сообщения от пользователей.</b>",
        "pm_allowed": "<b>Я разрешил {} писать мне.</b>",
        "pm_deny": "<b>Я запретил {} писать мне.</b>",
        "blocked": "<b>{} был занесён в Черный Список.</b>",
        "unblocked": "<b>{} был удалён из Черного Списка.</b>",
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
        "_cfg_auto_allow_contacts": "Авторазрешать всем из контактов (True/False)",
    }

    strings_ru = {
        "name": "Anti-PM",
        "pm_off": "<b>Теперь вы принимаете сообщения от всех пользователей.</b>",
        "pm_on": "<b>Вы перестали принимать сообщения от пользователей.</b>",
        "pm_allowed": "<b>Я разрешил {} писать мне.</b>",
        "pm_deny": "<b>Я запретил {} писать мне.</b>",
        "blocked": "<b>{} был занесён в Черный Список.</b>",
        "unblocked": "<b>{} был удалён из Черного Списка.</b>",
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
        "_cfg_auto_allow_contacts": "Авторазрешать всем из контактов (True/False)",
    }

    def __init__(self):
        self.me = None
        self._cb_handler_added = False

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
        # register callback query handler once
        if not self._cb_handler_added:
            client.add_event_handler(self._callback_query, events.CallbackQuery)
            self._cb_handler_added = True

    # -------- Commands --------
    async def pmcmd(self, message):
        """Используй: .pm — включить/выключить анти-PM (переключатель)."""
        pm = self.db.get("Anti-PM", "pm")
        # Note: original semantics preserved: pm==True -> receiving messages (anti-PM off)
        if pm is not True:
            await utils.answer(message, self.strings["pm_off"])
            self.db.set("Anti-PM", "pm", True)
        else:
            await utils.answer(message, self.strings["pm_on"])
            self.db.set("Anti-PM", "pm", False)

    async def allowcmd(self, message):
        """Используй: .allow — разрешить этому пользователю писать вам в личку (в текущем чате/реплае)."""
        if not message.is_private:
            return await message.edit(self.strings["not_pm"])
        user = await message.client.get_entity(message.chat_id)
        allowed = set(self.db.get("Anti-PM", "allowed", []))
        allowed.add(user.id)
        self.db.set("Anti-PM", "allowed", list(allowed))
        # reset counters and prompts
        self.db.set("Anti-PM", f"count_{user.id}", 0)
        await utils.answer(message, self.strings["pm_allowed"].format(user.first_name))

    async def blockcmd(self, message):
        """Используй: .block — заблокировать пользователя (реплай/аргумент)."""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
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

    async def allowedcmd(self, message):
        """Используй: .allowed — посмотреть список разрешённых пользователей."""
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
            # prevent too long message
            if len(text) > 3000:
                text += "\n<b>И т.д. (много пользователей)</b>"
                break
        await utils.answer(message, text)

    # -------- Internal helpers & watcher --------
    def _is_allowed(self, uid):
        return uid in self.db.get("Anti-PM", "allowed", [])

    async def _callback_query(self, event: events.CallbackQuery.Event):
        """Обработка нажатий inline-кнопок: allow/deny/block"""
        try:
            data = event.data.decode() if isinstance(event.data, (bytes, bytearray)) else str(event.data)
            # format: action_{user_id}
            if not data:
                await event.answer()
                return
            parts = data.split("_", 1)
            if len(parts) != 2:
                await event.answer()
                return
            action, sid = parts[0], parts[1]
            try:
                target_id = int(sid)
            except:
                await event.answer("Ошибка id.", alert=True)
                return

            # get user entity
            try:
                user = await self.client.get_entity(target_id)
            except:
                user = None

            if action == "allow":
                allowed = set(self.db.get("Anti-PM", "allowed", []))
                allowed.add(target_id)
                self.db.set("Anti-PM", "allowed", list(allowed))
                # reset counters
                self.db.set("Anti-PM", f"count_{target_id}", 0)
                # edit the prompt message
                try:
                    await event.edit(f"✅ Разрешено писать: <a href=tg://user?id={target_id}>{user.first_name if user else target_id}</a>")
                except:
                    pass
                await self.client.send_message("me", f"✅ Разрешён {user.first_name if user else target_id} ({target_id})")
                await event.answer("Пользователь разрешён.")
                return

            if action == "deny":
                # just note deny (do not block). keep them blocked by default (not in allowed).
                try:
                    await event.edit(f"❌ Отклонено: <a href=tg://user?id={target_id}>{user.first_name if user else target_id}</a>")
                except:
                    pass
                await event.answer("Отклонено.")
                return

            if action == "block":
                try:
                    if user:
                        await self.client(functions.contacts.BlockRequest(user))
                    else:
                        # fallback: try by id
                        await self.client(functions.contacts.BlockRequest(id=target_id))
                except Exception as e:
                    logger.exception(e)
                try:
                    await event.edit(f"🔒 Заблокирован: <a href=tg://user?id={target_id}>{user.first_name if user else target_id}</a>")
                except:
                    pass
                await self.client.send_message("me", f"🔒 Заблокирован {user.first_name if user else target_id} ({target_id})")
                await event.answer("Пользователь заблокирован.")
                return

            await event.answer()
        except Exception as e:
            logger.exception(e)
            try:
                await event.answer("Произошла ошибка.", alert=True)
            except:
                pass

    async def watcher(self, message):
        """Слежение за входящими ЛС — авто-ответ, кнопки, счётчик и авто-блок."""
        try:
            # skip service messages / non private
            if not message.is_private:
                return
            # skip self
            if message.sender_id == (await self.client.get_me()).id:
                return

            pm = self.db.get("Anti-PM", "pm")  # original semantics: pm == True -> receiving allowed
            # if receiving is allowed (pm True) => anti-PM is off
            if pm is True:
                return

            # get user entity
            user = await utils.get_user(message)
            uid = message.sender_id

            # bots ALWAYS allowed
            if user and getattr(user, "bot", False):
                allowed = set(self.db.get("Anti-PM", "allowed", []))
                if uid not in allowed:
                    allowed.add(uid)
                    self.db.set("Anti-PM", "allowed", list(allowed))
                return
         
            if self.auto_allow_contacts:
                try:
                    # check if in contacts
                    who = await self.client.get_entity(uid)
                    if isinstance(who, types.User) and who.contact:
                        allowed = set(self.db.get("Anti-PM", "allowed", []))
                        if uid not in allowed:
                            allowed.add(uid)
                            self.db.set("Anti-PM", "allowed", list(allowed))
                        return
                except Exception:
                    pass

            # if already allowed -> do nothing
            if self._is_allowed(uid):
                return

            # increment counter
            key = f"count_{uid}"
            cnt = int(self.db.get("Anti-PM", key, 0)) + 1
            self.db.set("Anti-PM", key, cnt)

            # on first message -> send custom_message with buttons (and store prompt id)
            if cnt == 1:
                text = self.config["custom_message"]
                try:
                    sent = await self.client.send_message(
                        message.chat_id,
                        text,
                        buttons=[
                            [
                                Button.inline("✅ Разрешить", f"allow_{uid}"),
                                Button.inline("❌ Отклонить", f"deny_{uid}"),
                                Button.inline("🔒 Заблокировать", f"block_{uid}")
                            ]
                        ]
                    )
                    # store prompt message id to optionally edit later
                    self.db.set("Anti-PM", f"prompt_{uid}", sent.id)
                except Exception as e:
                    logger.exception(e)
            # on 3rd message -> auto-block and notify you
            if cnt >= 3:
                # block user
                try:
                    await self.client(functions.contacts.BlockRequest(uid))
                except Exception as e:
                    logger.exception(e)
                # reset counter and remove prompt id
                self.db.set("Anti-PM", key, 0)
                try:
                    prompt_id = self.db.get("Anti-PM", f"prompt_{uid}")
                    if prompt_id:
                        # try to edit prompt to show blocked (best-effort)
                        try:
                            await self.client.edit_message(message.chat_id, prompt_id, f"🔒 Авто-блок: <a href=tg://user?id={uid}>{uid}</a>")
                        except Exception:
                            pass
                        self.db.set("Anti-PM", f"prompt_{uid}", 0)
                except Exception:
                    pass
                # notify you in Saved Messages
                me_name = (await self.client.get_me()).first_name or "You"
                await self.client.send_message("me", f"❗ <b>{user.first_name if user else uid}</b> (<code>{uid}</code>) прислал 3 сообщения и был автоматически заблокирован.")
        except Exception as e:
            logger.exception(e)
