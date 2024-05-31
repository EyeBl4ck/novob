from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    ForceReply,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from database import cur, save
from utils import get_info_wallet

import datetime
from typing import Union
import asyncio

@Client.on_callback_query(filters.regex(r"^user_info$"))
async def user_info(c: Client, m: CallbackQuery):
    hora_atual = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))

    hora_atual_str = hora_atual.strftime('%H:%M:%S')

    data_atual = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3)))

    data_atual_str = data_atual.strftime('%d/%m/%Y')
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    "🗑️ Histórico", callback_data="history"
                ),
            ],
             [
                 InlineKeyboardButton("👤 Dados De Pagamento", callback_data="swap_info"),
             ],
             [
              #   InlineKeyboardButton("⏳ Trocas disponível", callback_data="start_exchange"),
             ],
             [
               InlineKeyboardButton("🚢 AFILIADOS", callback_data="dev"),
             ],
             [
                 InlineKeyboardButton("❮ ❮", callback_data="start"),
             ],

        ]
    )
    link = f"https://t.me/{c.me.username}?start={m.from_user.id}"
    await m.edit_message_text(
         f"""<b>👤 Suas informações</b>
<i>- Aqui você pode visualizar os detalhes da sua conta.</i>


<i>Convidando novos usuarios pelo link abaixo voce recebe um bonus a cada vez que seus referenciados adicionarem saldo no bot</i>

{get_info_wallet(m.from_user.id)}""",

        reply_markup=kb,
    ),


@Client.on_callback_query(filters.regex(r"^dev$"))
async def btc(c: Client, m: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
        
        [
InlineKeyboardButton("Pontos De Compras", callback_data="swap"),
     #   InlineKeyboardButton("🔔 Atualizaçoes", url="t.me/VigaristaReferencias")
        ],
            [
                InlineKeyboardButton("❮ ❮", callback_data="user_info"),
            ],
        ]
    )
    await m.edit_message_text(
f"""<a href="https://i.im.ge/2023/03/13/DuSIj9.B2D50DEC-E286-454A-966D-03B6F687DFAF.jpg">🛍️</a> <b>Ganhar Saldo</b>

🚢| <b>Sistema de Afiliados</b>

<i>Divulgue seu link de afiliado e ganhe 10% em toda recarga do seu indicado!</i>

<b>Como funciona?</b>
    
<i>- Cada pessoa que for indicada pelo seu link e recarregar qualquer valor, você vai ganhar 20% do valor que ele recarregou, isso inclui todas as recargas que ele fizer!</i>

<i>- Os valores serão concedidos automaticamente em dinheiro na sua conta cadastrada no bot.</i>

<i>- Quanto mais pessoas você indicar, mais você vai ganhar!</i>

<b>Seu link de afiliação:</b> <code>https://t.me/{c.me.username}?start={m.from_user.id}</code>

{get_info_wallet(m.from_user.id)}""",
        reply_markup=kb,
    )  

@Client.on_callback_query(filters.regex(r"^history$"))
async def history(c: Client, m: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
        
        [
        InlineKeyboardButton("Historico Betano", callback_data="buy_history_log"),],
       [ InlineKeyboardButton("Historico Gmail", callback_data="buy_history_cc")
        ],
            [
                InlineKeyboardButton("❮ ❮", callback_data="user_info"),
            ],
        ]
    )
    await m.edit_message_text(
        f"""⚠️ Selecione qual historico de compras você deseja ver.</b>""",
        reply_markup=kb,
    )

@Client.on_callback_query(filters.regex(r"^buy_history$"))
async def buy_history(c: Client, m: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("❮ ❮", callback_data="history"),
            ],
        ]
    )
    history = cur.execute(
        "SELECT nome, cpf, linkdoc, bought_date , level, score ,localidade FROM docs_sold WHERE owner = ? ORDER BY bought_date DESC LIMIT 50",
        [m.from_user.id],
    ).fetchall()

    if not history:
        cards_txt = "<b>⚠️ Não há nenhuma compra nos registros.</b>"
    else:
        documentos = []
        print(documentos)
        for card in history:
            documentos.append("|".join([i for i in card]))
        cards_txt = "\n".join([f"<code>{cds}</code>" for cds in documentos])

    await m.edit_message_text(
        f"""<b>🛒 Histórico de compras</b>
<i>- Histórico de 50 últimas compras.</i>
NOME|CPF|LINK|COMPRADO|TIPO|SCORE|CIDADE

{cards_txt}""",
        reply_markup=kb,
    )

@Client.on_callback_query(filters.regex(r"^buy_history_log$"))
async def buy_history_log(c: Client, m: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("❮ ❮", callback_data="history"),
            ],
        ]
    )
    history = cur.execute(
        "SELECT tipo, email, senha, cidade bought_date FROM logins_sold WHERE owner = ? ORDER BY bought_date DESC LIMIT 50",
        [m.from_user.id],
    ).fetchall()

    if not history:
        cards_txt = "<b>⚠️ Não há nenhuma compra nos registros.</b>"
    else:
        documentos = []
        print(documentos)
        for card in history:
            documentos.append("|".join([i for i in card]))
        cards_txt = "\n".join([f"<code>{cds}</code>" for cds in documentos])

    await m.edit_message_text(
        f"""<b>🛒 Histórico de compras</b>
<i>- Histórico de 50 últimas compras.</i>
TIPO|EMAIL|SENHA|CIDADE|COMPRADO

{cards_txt}""",
        reply_markup=kb,
    )

@Client.on_callback_query(filters.regex(r"^buy_history_vales$"))
async def buy_history_vales(c: Client, m: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("❮ ❮", callback_data="history"),
            ],
        ]
    )
    history = cur.execute(
        "SELECT tipo, email, senha, cpf,limite,cidade bought_date FROM vales_sold WHERE owner = ? ORDER BY bought_date DESC LIMIT 50",
        [m.from_user.id],
    ).fetchall()

    if not history:
        cards_txt = "<b>⚠️ Não há nenhuma compra nos registros.</b>"
    else:
        documentos = []
        print(documentos)
        for card in history:
            documentos.append("|".join([i for i in card]))
        cards_txt = "\n".join([f"<code>{cds}</code>" for cds in documentos])

    await m.edit_message_text(
        f"""<b>🛒 Histórico de compras</b>
<i>- Histórico de 50 últimas compras.</i>
TIPO|EMAIL|SENHA|CPF|LIMIE|CIDADE|COMPRADO

{cards_txt}""",
        reply_markup=kb,
    )

@Client.on_callback_query(filters.regex(r"^buy_history_cc$"))
async def buy_history(c: Client, m: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("🔙 Voltar", callback_data="history"),
            ],
        ]
    )
    history = cur.execute(
        "SELECT number, month, year, cvv FROM cards_sold WHERE owner = ? ORDER BY bought_date DESC LIMIT 50",
        [m.from_user.id],
    ).fetchall()

    if not history:
        cards_txt = "<b>Não há nenhuma compra nos registros.</b>"
    else:
        cards = []
        for card in history:
            cards.append("|".join([i for i in card]))
        cards_txt = "\n".join([f"<code>{cds}</code>" for cds in cards])

    await m.edit_message_text(
        f"""<b>🛒 Histórico de compras</b>
<i>- Histórico de 50 últimas compras.</i>

{cards_txt}""",
        reply_markup=kb,
    )

@Client.on_callback_query(filters.regex(r"^swap$"))
async def swap_points(c: Client, m: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("❮ ❮", callback_data="user_info"),
            ],
        ]
    )

    user_id = m.from_user.id
    balance, diamonds = cur.execute(
        "SELECT balance, balance_diamonds FROM users WHERE id=?", [user_id]
    ).fetchone()

    if diamonds >= 10:
        add_saldo = round((diamonds / 2), 2)
        new_balance = round((balance + add_saldo), 2)

        txt = f"⚜️ Seus <b>{diamonds}</b> pontos foram convertidos em R$ <b>{add_saldo}</b> de saldo."

        cur.execute(
            "UPDATE users SET balance = ?, balance_diamonds=?  WHERE id = ?",
            [new_balance, 0, user_id],
        )
        return await m.edit_message_text(txt, reply_markup=kb)

    await m.answer(
        "⚠️ Você não tem pontos suficientes para realizar a troca. O mínimo é 10 pontos.",
        show_alert=True,
    )


@Client.on_callback_query(filters.regex(r"^swap_info$"))
async def swap_info(c: Client, m: CallbackQuery):
    await m.message.delete()

    cpf = await m.message.ask(
        "<b>👤 CPF da lara (válido) da lara que irá pagar</b>",
        reply_markup=ForceReply(),
        timeout=120,
    )
    name = await m.message.ask(
        "<b>👤 Nome completo do pagador</b>", reply_markup=ForceReply(), timeout=120
    )
    email = await m.message.ask(
        "<b>📧 E-mail</b>", reply_markup=ForceReply(), timeout=120
    )
    cpf, name, email = cpf.text, name.text, email.text
    cur.execute(
        "UPDATE users SET cpf = ?, name = ?, email = ?  WHERE id = ?",
        [cpf, name, email, m.from_user.id],
    )
    save()

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("❮ ❮", callback_data="start"),
            ]
        ]
    )
    await m.message.reply_text(
        "<b>⚠️ Seus dados foram alterados com sucesso.</b>", reply_markup=kb
    )



