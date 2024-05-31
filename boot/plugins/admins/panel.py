from typing import Union

from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    ForceReply,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config import ADMINS
from database import cur, save


@Client.on_message(filters.command("painel") & filters.user(ADMINS))
@Client.on_callback_query(filters.regex("^painel$") & filters.user(ADMINS))
async def panel(c: Client, m: Union[Message, CallbackQuery]):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("🧰 Manutenção", callback_data="bot_status"),
                InlineKeyboardButton("🏦 Lara", callback_data="change_lara"), 
				InlineKeyboardButton("🏦 ranking", callback_data="ranking"),
            ],
            [
                InlineKeyboardButton("💸 Preços", callback_data="change_prices"),
                InlineKeyboardButton("🔃 Gates", callback_data="select_gate"),
            ],
            [
                InlineKeyboardButton("💠 Pix auto", callback_data="auto_pay"),
                InlineKeyboardButton("📊 Estoque", callback_data="stock cards"),
            ],
            [
                InlineKeyboardButton("🎃 Dobro saldo", callback_data="dobro"),
		InlineKeyboardButton("📊 Estoque vale", callback_data="stockvales vales"),
            ],
            [
                InlineKeyboardButton("👤 Usuários", switch_inline_query_current_chat="search_user "),
                InlineKeyboardButton("🛠 Outras configs", callback_data="bot_config"),
            ],
            [InlineKeyboardButton("♻ Config trocas", callback_data="settings"),
            InlineKeyboardButton("📊 Estoque full", callback_data="stockfull cards_full")],
            
        ]
    )

    if isinstance(m, CallbackQuery):
        send = m.edit_message_text
    else:
        send = m.reply_text

    await send(
        """<b>📋 Painel de administração</b>
<i>- Selecione o que você deseja modificar.</i>""",
        reply_markup=kb,
    )


@Client.on_message(
    filters.command(["settings", "set", "config", "setting", "dobro"]) & filters.user(ADMINS)
)
@Client.on_callback_query(filters.regex("^settings") & filters.user(ADMINS))
async def settings(c: Client, m: Union[CallbackQuery, Message]):
    m = m.reply_text if isinstance(m, Message) else m.message.edit_text
    exhance_is = cur.execute("SELECT exchange_is FROM bot_config").fetchone()[0]
    msg, calb = (
        ("🚫 Desabilitar", "exchange_0")
        if exhance_is == 1
        else ("✅ Habilitar", "exchange_1")
    )
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🕐 Tempo de troca", callback_data="set time")],
            [InlineKeyboardButton(text=msg, callback_data=f"set {calb}")],
            [InlineKeyboardButton(text="❮ ❮", callback_data="painel")],
        ]
    )
    await m("<b>Selecione uma opção para configurar</b>", reply_markup=kb)


@Client.on_callback_query(filters.regex(r"^set (?P<action>\w+)") & filters.user(ADMINS))
async def set_exchange(c: Client, m: CallbackQuery):
    action = m.matches[0]["action"]

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❮ ❮", callback_data="painel")]
        ]
    )

    if action == "time":
        await m.message.delete()
        new_time = await m.message.ask(
            "⚠️ Digite o tempo de troca",
            filters=filters.regex(r"^\d+"),
            reply_markup=ForceReply(),
        )
        cur.execute("UPDATE bot_config SET time_exchange=?", [int(new_time.text)])
        save()
        return await m.message.reply_text(
            f"✅ Tempo de troca alterado com sucesso. Novo tempo {new_time.text}m",
            reply_markup=kb,
        )
    st = action.split("_")[1]
    is_exch = "habilitadas" if st == 1 else "Desabilitadas"
    cur.execute("UPDATE bot_config SET exchange_is=?", [int(st)])
    save()
    return await m.edit_message_text(
        f"<b>✅ Trocas {is_exch} com sucesso.</b>", reply_markup=kb
    )
