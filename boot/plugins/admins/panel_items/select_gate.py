from functools import partial as partial

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from config import ADMINS
from database import cur, save
from gates import *

GATES = {
    #"w4rlock": w4rlock_check_full,
    #"pre-auth": pre_auth,
    #"confidence_pre-auth": partial(confidence, value=0),
    #"confidence_debit": partial(confidence, value=1),
    #"ruby": ruby_check_full,
    #"darknet_erede": partial(darknet, gate="erede"),
    #"darknet_getnet": partial(darknet, gate="getnet"),
    "joker": gatejoker,
    #"shopcard_pre-auth": partial(shopcard, value=0),
    #"shopcard_debit": partial(shopcard, value=1),
    #"azkaban": azkaban,
    #"zcash": zcash,
    #"gp": gp_chk,
}  # fmt: skip

# Copiando o GATES (que Ã© uma constante) para uma variÃ¡vel,
# na qual poderÃ¡ ser modificada posteriormente.
gates = GATES.copy()


@Client.on_callback_query(filters.regex(r"^select_gate$") & filters.user(ADMINS))
async def type_chk(c: Client, m: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("ðŸ’³ Checagem", callback_data="select_gate gate"),
                InlineKeyboardButton("â™» Trocas", callback_data="select_gate exchange"),
            ],

            [
                InlineKeyboardButton("âž• Adicionar novas gates", callback_data="painel"),
                InlineKeyboardButton("ðŸ›  Configurar gates", callback_data="painel"),
            ],

            [
                InlineKeyboardButton("ðŸ”ƒ Refresh", callback_data="refresh_gates"),
            ],
            [
                InlineKeyboardButton("Â« Voltar", callback_data="painel"),
            ],
        ]
    )

    await m.edit_message_text(
        "<b>ðŸ”ƒ Gates</b>\n"
        "<i>- Esta opÃ§Ã£o permite alterar as gates usadas para checagem e trocas, alÃ©m de ser possÃ­vel reestabelecer as gates.</i>\n\n"
        "<b>Selecione abaixo a opÃ§Ã£o desejada:</b>",
        reply_markup=kb,
    )


@Client.on_callback_query(
    filters.regex(r"^select_gate (?P<chk_type>.+)$") & filters.user(ADMINS)
)
async def options_gates(c: Client, m: CallbackQuery):
    type_exchange = m.matches[0]["chk_type"]
    bt_list = []
    for opt in gates:
        bt_list.append(
            InlineKeyboardButton(
                text=f"ðŸ”¸ {opt}", callback_data=f"set_gate {type_exchange} {opt}"
            )
        )

    orgn = (lambda data, step: [data[x : x + step] for x in range(0, len(data), step)])(
        bt_list, 2
    )
    orgn.append([InlineKeyboardButton(text="Â« Voltar", callback_data="select_gate")])
    kb = InlineKeyboardMarkup(inline_keyboard=orgn)

    await m.edit_message_text(
        "<b>ðŸ”ƒ Selecione a gate para operar checagem no bot</b>", reply_markup=kb
    )


@Client.on_callback_query(
    filters.regex(r"^set_gate (?P<chk_type>.+) (?P<gate>.+)") & filters.user(ADMINS)
)
async def select_gate(c: Client, m: CallbackQuery):
    var_alt = m.matches[0]["chk_type"]
    gate = m.matches[0]["gate"]

    if var_alt == "exchange":
        cur.execute("UPDATE bot_config SET gate_exchange = ?", [gate])
    else:
        cur.execute("UPDATE bot_config SET gate_chk = ?", [gate])
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Â« Voltar", callback_data="select_gate")]
        ]
    )
    save()
    await m.edit_message_text(
        f"<b>âœ… Gate alterada com sucesso. gate â†’ {gate.title()}</b>", reply_markup=kb
    )


@Client.on_callback_query(filters.regex(r"^refresh_gates$") & filters.user(ADMINS))
async def refresh(c: Client, m: CallbackQuery):
    global gates
    gates = GATES.copy()
    await m.answer("Gates reestabelecidas com sucesso.", show_alert=True)
