import io
from typing import Union

from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config import ADMINS
from database import cur, save

keys1 = {
    "cards_full": "💳 Disponíveis",
    "cards_sold_full": "💵 Vendidas",
    "cards_dies_full": "🗑 Trocas/Dies",
}


@Client.on_callback_query(
    filters.regex(r"^stockfull (?P<type_name>\w+)$") & filters.user(ADMINS)
)
@Client.on_message(filters.command(["estoquefull", "stockfull"]))
async def ccs_stockfull(c: Client, m: Union[CallbackQuery, Message]):
    keys = keys1.copy()

    if isinstance(m, CallbackQuery):
        table_name = m.matches[0]["type_name"]
        send = m.edit_message_text
    else:
        table_name = "cards_full"
        send = m.reply_text

    # Altera o emoji da categoria ativa para ✅
    for key in keys:
        if key == table_name:
            keys[key] = "✅ " + keys[key].split(maxsplit=1)[1]

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(name, callback_data="stockfull " + key)
                for key, name in keys.items()
            ],
            [
                InlineKeyboardButton(
                    text=f"⏬ Baixar {keys[table_name].split(maxsplit=1)[1].lower()}",
                    callback_data="downloadfull " + table_name,
                ),
                InlineKeyboardButton(
                    text=f"⛔️ Apagar {keys[table_name].split(maxsplit=1)[1].lower()}",
                    callback_data="clearfull " + table_name,
                ),
            ],
            [
                InlineKeyboardButton("❮ ❮", callback_data="painel"),
            ],
        ]
    )

    ccs = cur.execute(
        f"SELECT level, count() FROM {table_name} GROUP BY level ORDER BY count() DESC"
    ).fetchall()

    stock = (
        "\n".join([f"<b>{it[0]}</b>: {it[1]}" for it in ccs])
        or "<b>Nenhum item nesta categoria FULL DADOS.</b>"
    )
    total = f"\n\n<b>Total</b>: {sum([int(x[1]) for x in ccs])}" if ccs else ""

    await send(
        f"<b>💳 Estoque FULL DADOS - {keys[table_name].split(maxsplit=1)[1]}</b>\n\n{stock}{total}",
        reply_markup=kb if m.from_user.id in ADMINS else None,
    )


@Client.on_callback_query(
    filters.regex(r"^downloadfull (?P<table>\w+)") & filters.user(ADMINS)
)
async def get_stockfull(c: Client, m: CallbackQuery):
    table_name = m.matches[0]["table"]

    # Tables para enviar por categorias
    if table_name == "cards_full":
        tables = "number, month, year, cvv, added_date, name, cpf"
    elif table_name == "cards_sold_full":
        tables = "number, month, year, cvv, added_date, bought_date, owner, name, cpf"
    elif table_name == "cards_dies_full":
        tables = "number, month, year, cvv, added_date, die_date, name, cpf"
    else:
        return

    ccs = cur.execute(f"SELECT {tables} FROM {table_name}").fetchall()

    txt = "\n".join(["|".join([str(d) for d in cc]) for cc in ccs])
    tess = "\n\nCC | MES | ANO | CVV | HORA | ADICAO | COMPRADOR | NOME | CPF"
    if len(txt) > 3500:
        bio = io.BytesIO()
        bio.name = table_name + ".txt"
        bio.write(txt.encode())
        return await m.message.reply_document(
            bio, caption=f"Ordem dos itens: {tables}", quote=True
        )

    return await m.message.reply_text(f"<code>{txt}</code>", quote=True)


@Client.on_callback_query(
    filters.regex(r"^clearfull (?P<table>\w+)") & filters.user(ADMINS)
)
async def clear_tablefull(c: Client, m: CallbackQuery):
    table_name = m.matches[0]["table"]

    table_str = keys1[table_name].split(maxsplit=1)[1].lower()

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"⛔️ Apagar {keys1[table_name].split(maxsplit=1)[1].lower()}",
                    callback_data="clear_confirmfull " + table_name,
                ),
                InlineKeyboardButton(
                    text="❮ ❮",
                    callback_data="stockfull " + table_name,
                ),
            ],
        ]
    )

    await m.edit_message_text(
        f"<b>⛔️ Apagar {table_str}</b>\n\n"
        f"Você tem certeza que deseja zerar o estoque de <b>{table_str}</b>?\n"
        "Note que <b>esta operação é irreversível</b> e um backup é recomendado.",
        reply_markup=kb,
    )


@Client.on_callback_query(
    filters.regex(r"^clear_confirmfull (?P<table>\w+)") & filters.user(ADMINS)
)
async def clear_table_confirmfull(c: Client, m: CallbackQuery):
    table_name = m.matches[0]["table"]

    table_str = keys1[table_name].split(maxsplit=1)[1].lower()

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❮ ❮",
                    callback_data="stockfull " + table_name,
                ),
            ],
        ]
    )

    cur.execute(f"DELETE FROM {table_name}")

    await m.edit_message_text(
        f"✅ Estoque de {table_str} apagado com sucesso.", reply_markup=kb
    )
    save()
