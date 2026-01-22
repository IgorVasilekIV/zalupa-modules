"""
Some description:
Event who rolls the highest number on a dice
"""

__version__ = (1, 3, 5)

# meta developer: @HikkaZPM
# meta fhsdeck: dice, event, game, chat
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

from .. import loader, utils
import asyncio
import random

from telethon.tl.types import InputMediaDice

@loader.tds
class DiceEventMod(loader.Module):
    """Event who rolls the highest number on a dice\n\nBe sure to enable `.tsec chat DiceEventMod` and `.nonickchat` to 'on' before starting the game"""

    strings = {
        "name": "DiceEvent",
        "_cls_doc": "Event who rolls the highest number on a dice\n\nBe sure to enable `.tsec chat DiceEventMod` and `.nonickchat` to 'on' before starting the game",
        "_cfg_waiting_participants": "Timeout for joining to game",
        "event_already_started": "⚠️ Event is already running — wait for the end.",
        "event_started": "🎲 Event started: type <code>{prefix}join</code> within {timeout} seconds to join.",
        "few_participants": "No one joined the game. Round cancelled.",
        "winner_announce": "🏆 Winner: {winner} — congratulations!",
        "roll_result": "🎲 {name}, your roll: {rolled}",
        "draw_announce": "🤝 Draw between: {winner_lines}",
        "join_success": "✅ {display_name}, you're in the game!",
        "no_active_game": "❌ There's no active round. Start one with <code>{prefix}dice</code>.",
        "join_already": "⚠️ You're already in the game."
    }
    strings_ru = {
        "_cls_doc": "Ивент кому выпадет больше число на кубике\n\nОбязательно включите .tsec chat DiceEventMod и .nonickchat на 'включено' перед началом игры",
        "_cfg_waiting_participants": "Время ожидания участников в игру",
        "event_already_started": "⚠️ Ивент уже идёт — подожди завершения.",
        "event_started": "🎲 Ивент начался: пишите <code>{prefix}join</code> в течение {timeout}с. что бы присоеденится.",
        "few_participants": "Никто не зашёл в игру. Раунд отменён.",
        "winner_announce": "🏆 Победитель: {winner} — поздравляю!",
        "roll_result": "🎲 {name}, твой бросок: {rolled}",
        "draw_announce": "🤝 Ничья между: {winner_lines}",
        "join_success": "✅ {display_name}, ты в игре!",
        "no_active_game": "❌ Сейчас нет активного раунда. Запусти <code>{prefix}dice</code> чтобы начать.",
        "join_already": "⚠️ Ты уже в игре."
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "waiting_participants",
                15,
                lambda: self.strings["_cfg_waiting_participants"],
                validator=loader.validators.Integer()
            )
        )
        self.SEND_DELAY = 0.5
        self.DEFAULT_EMOJI = "🎲"
        # +- структура: games[chat_id] = {"participants": {user_id: {"name": str, "msg_id": int}}, "lock": asyncio.Lock(), "running": bool}
        self.games = {}

    async def client_ready(self, client, db):
        self.client = client
        self.db = db        

    def _ensure_game(self, chat_id):
        g = self.games.get(chat_id)
        if not g:
            g = {
                "participants": {},
                "lock": asyncio.Lock(),
                "running": False
            }
            self.games[chat_id] = g
        return g

    @loader.command(
        ru_doc="[время] [эмодзи (кубик, боулинг ...)] - начать игру. [] это опциональная настройка"
    )
    async def dice(self, message):
        """[time] [emoji (cube, bowling ...)] - start a game. [] optional value"""
        args_raw = utils.get_args_raw(message).strip()
        args = args_raw.split() if args_raw else []

        # первый арг - отсчёт
        timeout = self.config["waiting_participants"]
        emoji_arg = self.DEFAULT_EMOJI

        if args:
            if args[0].lstrip("-").isdigit():
                try:
                    timeout = max(1, int(args[0]))
                except Exception:
                    timeout = self.config["waiting_participants"]
                if len(args) > 1:
                    emoji_arg = args[1]
            else:
                emoji_arg = args[0]

        chat_id = message.chat_id
        game = self._ensure_game(chat_id)

        async with game["lock"]:
            if game["running"]:
                await utils.answer(message, self.strings["event_already_started"])
                return
            game["running"] = True
            game["participants"].clear()

        prefix = self.get_prefix()
        await utils.answer(message, self.strings["event_started"].format(prefix=prefix, timeout=timeout))

        # ждём участников
        await asyncio.sleep(timeout)

        async with game["lock"]:
            participants = dict(game["participants"])
            game["running"] = False
            game["participants"].clear()

        if not participants:
            await utils.answer(message, self.strings["few_participants"])
            return

        results = {}  # user_id -> rolled value

        for user_id, info in participants.items():
            name = info["name"]
            join_msg_id = info["msg_id"]

            try:
                sent = await self.client.send_message(
                    chat_id,
                    file=InputMediaDice(emoji_arg),
                    reply_to=join_msg_id
                )
                rolled = None
                if sent and getattr(sent, "media", None):
                    rolled = getattr(sent.media, "value", None)
                if not rolled:
                    # fallback на локальный рандом (если значение None)
                    rolled = random.randint(1, 6)
            except Exception:
                rolled = random.randint(1, 6)
                await self.client.send_message(chat_id, self.strings["roll_result"].format(name=name, rolled=rolled))

            results[user_id] = rolled
            # небольшая пауза между отправками
            await asyncio.sleep(self.SEND_DELAY)

        # обьявляем победителя(ей)
        max_roll = max(results.values())
        winners = [uid for uid, val in results.items() if val == max_roll]

        winner_lines = []
        for uid in winners:
            display = participants.get(uid, {}).get("name", str(uid))
            winner_lines.append(f"{display} ({results[uid]})")

        await asyncio.sleep(4.0) # ждём пока кубик остановится
        # формирование:
        if len(winners) == 1:
            await self.client.send_message(chat_id, self.strings["winner_announce"].format(winner=winner_lines[0]))
        else:
            await self.client.send_message(chat_id, self.strings["draw_announce"].format(winner_lines=", ".join(winner_lines)))

    @loader.command(
        ru_doc="- присоеденится к текущей игре. Сделай `.tsec chat DiceEvent` если у тебя есть чат!"
    )
    async def joincmd(self, message):
        """- join to game. Do `.tsec chat DiceEvent` if you do this in chat!"""
        chat_id = message.chat_id
        sender = await message.get_sender()
        game = self._ensure_game(chat_id)

        async with game["lock"]:
            if not game["running"]:
                prefix = self.get_prefix()
                await utils.answer(message, self.strings["no_active_game"].format(prefix=prefix))
                return

            uid = sender.id
            display_name = ("@" + sender.username) if sender.username else sender.first_name
            game["participants"][uid] = {
                "name": display_name,
                "msg_id": message.id
            }

        await utils.answer(message, self.strings["join_success"].format(display_name=display_name))