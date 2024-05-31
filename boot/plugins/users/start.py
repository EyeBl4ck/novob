from typing import Union
import datetime
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import BadRequest
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from database import cur, save
from utils import create_mention, get_info_wallet, dobrosaldo
from config import BOT_LINK
from config import BOT_LINK_SUPORTE
import datetime
from typing import Union
import asyncio

@Client.on_message(filters.command(["start", "menu"]))
@Client.on_callback_query(filters.regex("^start$"))
async def start(c: Client, m: Union[Message, CallbackQuery]):
    user_id = m.from_user.id

    hora_atual = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))

    hora_atual_str = hora_atual.strftime('%H:%M:%S')

    data_atual = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))

    data_atual_str = data_atual.strftime('%d/%m/%Y')

    rt = cur.execute(
        "SELECT id, balance, balance_diamonds, refer FROM users WHERE id=?", [user_id]
    ).fetchone()

    if isinstance(m, Message):
        refer = (
            int(m.command[1])
            if (len(m.command) == 2)
            and (m.command[1]).isdigit()
            and int(m.command[1]) != user_id
            else None
        )

        if rt[3] is None:
            if refer is not None:
                mention = create_mention(m.from_user, with_id=False)

                cur.execute("UPDATE users SET refer = ? WHERE id = ?", [refer, user_id])
                try:
                    await c.send_message(
                        refer,
                        text=f"<b>🎁 Parabéns, o usuário {mention} se vinculou com seu link de afiliado e você receberá uma porcentagem do que o mesmo adicionar no nosso bot</b>",
                    )
                except BadRequest:
                    pass

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("🛒 Comprar Produtos", callback_data="shop"),
            
            
			],
			[
                InlineKeyboardButton("💵 Adicionar Saldo", callback_data="add_saldo"),
			],

            [
InlineKeyboardButton("☃️ Perfil", callback_data="user_info"),
            
##InlineKeyboardButton("🕹 Cassino",  callback_data='cassino'),
			],
        ]
    )

    bot_logo, news_channel, support_user = cur.execute(
        "SELECT main_img, channel_user, support_user FROM bot_config WHERE ROWID = 0"
    ).fetchone()

    start_message = f"""‌<a>&#8204</a><b><b> 🛒 | Lojinha Betano - {BOT_LINK}
	
🛒 - @LojinhaBetanoBot
➖➖➖➖➖➖➖➖➖➖➖➖➖➖
✅ Logins Verificados!
⚠️ Testada na hora pelo bot!
💰 Faça recargas pelo /pix!
➖➖➖➖➖➖➖➖➖➖➖➖➖➖
🟢 BOT ONLINE

PARA QUALQUER DÚVIDA, ENTRE EM CONTATO : @Lonsepo"""

    if isinstance(m, CallbackQuery):
        send = m.edit_message_text
    else:
        send = m.reply_text
    save()
    await send(start_message, reply_markup=kb)
