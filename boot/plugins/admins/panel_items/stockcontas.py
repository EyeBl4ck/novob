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
    "contas": "📨 Disponíveis",
    "contas_sold": "💵 Vendidas",
    
}


@Client.on_callback_query(
    filters.regex(r"^stockcontas (?P<type_name>\w+)$") & filters.user(ADMINS)
)
@Client.on_message(filters.command(["estoquecontas", "stockcontas"]))
async def contas_stock(c: Client, m: Union[CallbackQuery, Message]):
    keys = keys1.copy()

    if isinstance(m, CallbackQuery):
        table_name = m.matches[0]["type_name"]
        send = m.edit_message_text
    else:
        table_name = "contas"
        send = m.reply_text

    # Altera o emoji da categoria ativa para ✅
    for key in keys:
        if key == table_name:
            keys[key] = "✅ " + keys[key].split(maxsplit=1)[1]

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(name, callback_data="stock " + key)
                for key, name in keys.items()
            ],
            [
                InlineKeyboardButton(
                    text=f"⏬ Baixar {keys[table_name].split(maxsplit=1)[1].lower()}",
                    callback_data="downloadcontas " + table_name,
                ),
                InlineKeyboardButton(
                    text=f"⛔️ Apagar {keys[table_name].split(maxsplit=1)[1].lower()}",
                    callback_data="clearcontas " + table_name,
                ),
            ],
            [
                InlineKeyboardButton("❮ ❮", callback_data="painel"),
            ],
        ]
    )

    ccs = cur.execute(
        f"SELECT tipo, count() FROM {table_name} GROUP BY tipo ORDER BY count() DESC"
    ).fetchall()

    stock = (
        "\n".join([f"<b>{it[0]}</b>: {it[1]}" for it in ccs])
        or "<b>Nenhum item nesta categoria Contas Premium.</b>"
    )
    total = f"\n\n<b>Total</b>: {sum([int(x[1]) for x in ccs])}" if ccs else ""

    await send(
        f"<b>📨 Estoque de Contas Premium - {keys[table_name].split(maxsplit=1)[1]}</b>\n\n{stock}{total}",
        reply_markup=kb if m.from_user.id in ADMINS else None,
    )


@Client.on_callback_query(
    filters.regex(r"^downloadcontas (?P<table>\w+)") & filters.user(ADMINS)
)
async def getcontas_stock(c: Client, m: CallbackQuery):
    table_name = m.matches[0]["table"]

    # Tables para enviar por categorias
    if table_name == "contas":
        tables = "tipo, email, senha, cidade, idcontas, added_date"
    elif table_name == "contas_sold":
        tables = "tipo, email, senha, cidade, idcontas, added_date, bought_date, owner"
    elif table_name == "cards_diesnulll":
        tables = "number, month, year, cvv, added_date, die_date"
    else:
        return

    ccs = cur.execute(f"SELECT {tables} FROM {table_name}").fetchall()

    txt = "\n".join(["|".join([str(d) for d in cc]) for cc in ccs])

    if len(txt) > 3500:
        bio = io.BytesIO()
        bio.name = table_name + ".txt"
        bio.write(txt.encode())
        return await m.message.reply_document(
            bio, caption=f"Ordem dos itens: {tables}", quote=True
        )

    return await m.message.reply_text(f"<code>{txt}</code>", quote=True)


@Client.on_callback_query(
    filters.regex(r"^clearcontas (?P<table>\w+)") & filters.user(ADMINS)
)
async def clearcontas_table(c: Client, m: CallbackQuery):
    table_name = m.matches[0]["table"]

    table_str = keys1[table_name].split(maxsplit=1)[1].lower()

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"⛔️ Apagar {keys1[table_name].split(maxsplit=1)[1].lower()}",
                    callback_data="clearcontas_confirm " + table_name,
                ),
                InlineKeyboardButton(
                    text="❮ ❮",
                    callback_data="clearcontas " + table_name,
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
    filters.regex(r"^clearcontas_confirm (?P<table>\w+)") & filters.user(ADMINS)
)
async def clearcontas_table_confirm(c: Client, m: CallbackQuery):
    table_name = m.matches[0]["table"]

    table_str = keys1[table_name].split(maxsplit=1)[1].lower()

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❮ ❮",
                    callback_data="stock " + table_name,
                ),
            ],
        ]
    )

    cur.execute(f"DELETE FROM {table_name}")

    await m.edit_message_text(
        f"✅ Estoque de {table_str} apagado com sucesso.", reply_markup=kb
    )
    save()
