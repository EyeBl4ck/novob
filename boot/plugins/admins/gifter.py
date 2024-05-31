import random
import string

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)

from config import ADMIN_CHAT, ADMINS, GIFTERS
from database import cur, save


def gift_generator(size=12, chars=string.ascii_uppercase + string.digits):
    return "".join(random.choices(chars, k=size))


GIFT_MSG = """<b>🏷 GIFT CARD GERADO!</b>
<b>📮 GIFT CARD: </b><code>/resgatar {gift}</code>
<b>💸 VALOR: R$ {value}</b>
<b>📥 RESGATE: @{bot_username}</b>
"""


@Client.on_message(
    filters.regex(r"^/gift (?P<value>-?\d+)") & (filters.user(ADMINS) | filters.user(GIFTERS))  # fmt: skip
)
async def create_gift(c: Client, m: Message):
    value = int(m.matches[0]["value"])
    gift = gift_generator()

    cur.execute("INSERT INTO gifts(token, value) VALUES(?, ?)", [gift, value])
    save()

    await m.reply_text(
        GIFT_MSG.format(value=value, gift=gift, bot_username=c.me.username)
    )

    text = f""
    return await c.send_message(ADMIN_CHAT, text)


@Client.on_inline_query(
    filters.regex(r"^gift (?P<value>-?\d+)") & (filters.user(ADMINS) | filters.user(GIFTERS))  # fmt: skip
)
async def create_gift_inline(c: Client, m: InlineQuery):
    value = int(m.matches[0]["value"])
    gift = gift_generator()

    cur.execute("INSERT INTO gifts(token, value) VALUES(?, ?)", [gift, value])
    save()

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("🎁 Resgatar", callback_data="resgatar " + gift)]
        ]
    )

    results = [
        InlineQueryResultArticle(
            title=f"Gift de R$ {value} criado",
            description="Clique para enviar o gift no chat.",
            input_message_content=InputTextMessageContent(
                GIFT_MSG.format(value=value, gift=gift, bot_username=c.me.username)
            ),
            reply_markup=kb,
        )
    ]

    await m.answer(results, cache_time=0, is_personal=True)

    text = f""
    await c.send_message(ADMIN_CHAT, text)
