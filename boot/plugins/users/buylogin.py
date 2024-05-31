import asyncio

from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from config import ADMIN_CHAT, GRUPO_PUB
from config import LOG_CHAT
from database import cur, save
from utils import (
    create_mention,
    get_info_wallet,
    get_price,
    insert_logins_sold,
    insert_sold_balance,
    lock_user_buy,
    msg_group_publico_logins,
    msg_buy_off_user_logins,
    msg_buy_user,
    msg_group_adm_logins,
)



SELLERS, TESTED = 0, 0


T = 0.1





# Listagem de tipos de compra.
@Client.on_callback_query(filters.regex(r"^comprar_log$"))
async def comprar_logins_list(c: Client, m: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("📰 Login Gmail", callback_data="comprar_login unit"),
            #    InlineKeyboardButton("🛒 MIX", callback_data="comprar_logins mix"),
                
                
            ],
          

             
            [
                InlineKeyboardButton("❮ ❮", callback_data="comprar_contas"),
            ],
        ]
    )

    await m.edit_message_text(
        f"""<a href='https://i.ibb.co/r0jsL20/IMG-20230712-135120-982.jpg'</a><b>🎟️ Comprar Gmail</b>
<i>- Escolha abaixo o produto que deseja comprar.</i>

{get_info_wallet(m.from_user.id)}""",
        reply_markup=kb,
    )


# Pesquisa de logins via inline.
@Client.on_inline_query(filters.regex(r"^buscarlog_(?P<type>\w+) (?P<value>.+)"))
async def search_logins(c: Client, m: InlineQuery):
    """
    Pesquisa uma logins via inline por tipo e retorna os resultados via inline.

    O parâmetro `type` será o tipo de valor para pesquisar
    """

    typ = m.matches[0]["type"]
    qry = m.matches[0]["value"]

    # Não aceitar outros valores para prevenir SQL Injection.
    if typ not in ("tipo", "cidade", "city", "type"):
        return

    if typ != "logins":
        qry = f"%{qry}%"

    if typ == "email":
        typ2 = "senha"
        typ3 = "cidade"
    else:
        typ2 = typ

    rt = cur.execute(
        f"SELECT email,  {typ2}, idlogin, cidade FROM logins WHERE {typ2} LIKE ? AND pending = 0 ORDER BY RANDOM() LIMIT 40",
        [qry.upper()],
    ).fetchall()

    results = []
    results.append(
            InlineQueryResultArticle(
                title=f"Total: ({len(rt)}) de resultados encontrados",
                description="Confira todos os logins abaixo 🛍👇",
                
                input_message_content=InputTextMessageContent(
                    "Compre logins via Inline ✅"
                ),
            )
        )

    wallet_info = get_info_wallet(m.from_user.id)

    for email, value, idlogin, cidade in rt:

        price = await get_price("logins", value)

        base = f"""Email: {email[0:6]}********** Tipo: {value} City: {cidade}"""

        base_ml = f"""<b>Email:</b> <i>{email[0:6]}**********</i>
<b>Tipo:</b> <i>{value}</i>
<b>Cidade:</b> <i>{cidade}</i>

<b>Valor:</b> <i>R$ {price}</i>"""

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Comprar",
                        callback_data=f"buy_off_logins idlogin '{idlogin}'",
                    )
                ]
            ]
        )

        results.append(
            InlineQueryResultArticle(
                title=f"{typ} {value} - R$ {price}",
                description=base,
                
                input_message_content=InputTextMessageContent(
                    base_ml + "\n\n" + wallet_info
                ),
                reply_markup=kb,
            )
        )

    await m.answer(results, cache_time=5, is_personal=True)
    

# Opção Compra de logins e Listagem de Level's.
@Client.on_callback_query(filters.regex(r"^comprar_login unit$"))
async def comprar_logins(c: Client, m: CallbackQuery):
    list_levels_logins = cur.execute("SELECT tipo FROM logins GROUP BY tipo").fetchall()
    levels_list = [x[0] for x in list_levels_logins]

    if not levels_list:
        return await m.answer(
            "⚠️ Não há Gmail disponíveis no momento, tente novamente mais tarde.",
            show_alert=True,
        )

    levels = []
    for level in levels_list:
        level_name = level
        n = level.split()
        if len(n) > 1:
            level_name = n[0][:4] + " " + n[1]

        price = await get_price("logins", level)
        levels.append(
            InlineKeyboardButton(
                text=f"{level_name.upper()} | R$ {price} - Aleatório 🎲",
                callback_data=f"buy_off_logins tipo '{level}'",
            )
        )

    organ = (
        lambda data, step: [data[x : x + step] for x in range(0, len(data), step)]
    )(levels, 2)
    table_name = "logins"
    logins = cur.execute(
        f"SELECT tipo, count() FROM {table_name} GROUP BY tipo ORDER BY count() DESC"
    ).fetchall()

    
    total = f"<b>🧿 Total de Gmail</b>: {sum([int(x[1]) for x in logins])}" if logins else ""
    
    organ.append([InlineKeyboardButton(text="❮ ❮", callback_data="comprar_contas")])
    kb = InlineKeyboardMarkup(inline_keyboard=organ)
    await m.edit_message_text(
        f"""<b>👾 Comprar Gmail</b>
<b>- Escolha abaixo seu Login Gmail</b>

{total}

{get_info_wallet(m.from_user.id)}""",
        reply_markup=kb,
    )




@Client.on_callback_query(
    filters.regex(r"^buy_off_logins (?P<type>[a-z]+) '(?P<level_logins>.+)' ?(?P<other_params>.+)?")  # fmt: skip
)
@lock_user_buy
async def buy_off_logins(c: Client, m: CallbackQuery):
    user_id = m.from_user.id
    balance: int = cur.execute("SELECT balance FROM users WHERE id = ?", [user_id]).fetchone()[0]  # fmt: skip

    type_logins = m.matches[0]["type"]
    level_logins = m.matches[0]["level_logins"]

    price = await get_price("logins", level_logins)

    if balance < price:
        return await m.answer(
            "⚠️ Você não possui saldo suficiente para esse item. Por favor, faça um /pix.",
            show_alert=True,
        )

    search_for = "tipo" if type_logins == "tipo" else "idlogin"

    selected_logins = cur.execute(
        f"SELECT tipo, email, senha, added_date, cidade, idlogin FROM logins WHERE {search_for} = ? AND pending = ? ORDER BY RANDOM()",
        [level_logins, False],
    ).fetchone()

    if not selected_logins:
        return await m.answer("⚠️ Sem logins disponiveis para este nivel.", show_alert=True)

    diamonds = round(((price / 100) * 8), 2)
    new_balance = balance - price
    
    (
        tipo,
        email,
        senha,
        added_date,
        cidade,
        idlogin,
    ) = selected_logins
    #nome = nome.upper()
    card = "|".join([tipo, email, senha])
    ds = "logins"
    list_card_sold = selected_logins + (user_id, ds)

    cur.execute(
        "DELETE FROM logins WHERE idlogin = ?",
        [selected_logins[5]],
    )

    cur.execute(
        "UPDATE users SET balance = ?, balance_diamonds = round(balance_diamonds + ?, 2) WHERE id = ?",
        [new_balance, diamonds, user_id],
    )

    s = insert_logins_sold(list_card_sold)
    print(s)
    insert_sold_balance(price, user_id, "logins")

    #dados = (cpf, name) if cpf is not None else None
    base = await msg_buy_off_user_logins(user_id, email, senha, tipo, price, cidade)
    await m.edit_message_text(base)
    mention = create_mention(m.from_user)
    adm_msg = msg_group_adm_logins(
        mention, email, senha, tipo, price, "None", new_balance, cidade
    )
    pub = msg_group_publico_logins(mention, email, senha, tipo, price, "None", new_balance, cidade)
    await c.send_message(ADMIN_CHAT, adm_msg)
    kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="🎟 Compre os melhores Logins",url=f"https://t.me/LojinhaBetano_bot"
                            ),
                        ],
                    ]
                )
    await c.send_message(GRUPO_PUB, pub, reply_markup=kb)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="❮ ❮", callback_data="comprar_contas"),
            ],
        ]
    )
    try:
        await m.message.reply_text(
            "✅ Compra realizada com sucesso. Clique no botão abaixo para voltar para o menu principal.",
            reply_markup=kb,
        )
    except:
        ...
    save()
