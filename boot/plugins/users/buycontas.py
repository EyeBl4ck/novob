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
    insert_contas_sold,
    insert_sold_balance,
    lock_user_buy,
    msg_group_publico_contas,
    msg_buy_off_user_contas,
    msg_buy_user,
    msg_group_adm_contas,
)



SELLERS, TESTED = 0, 0


T = 0.1





# Listagem de tipos de compra.
@Client.on_callback_query(filters.regex(r"^comprar_contas$"))
async def comprar_contas_list(c: Client, m: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("🛒 CONTAS BETANO", callback_data="comprar_contas unit"),
                InlineKeyboardButton("🛒 GMAIL", callback_data="comprar_logins unit"),
                
                
            ],
            [
		InlineKeyboardButton("🛒 DADOS CPF LIVRE", callback_data="comprar_vales unit")
	    ],
             
            [
                InlineKeyboardButton("❮ ❮", callback_data="shop"),
            ],
        ]
    )

    await m.edit_message_text(
        f"""<b>🎟️ Comprar Contas Premium</b>
<i>- Escolha abaixo o produto que deseja comprar.</i>

{get_info_wallet(m.from_user.id)}""",
        reply_markup=kb,
    )


# Pesquisa de logins via inline.
@Client.on_inline_query(filters.regex(r"^buscarcontas_(?P<type>\w+) (?P<value>.+)"))
async def search_contas(c: Client, m: InlineQuery):
    """
    Pesquisa um logins via inline por tipo e retorna os resultados via inline.

    O parâmetro `type` será o tipo de valor para pesquisar
    """

    typ = m.matches[0]["type"]
    qry = m.matches[0]["value"]

    # Não aceitar outros valores para prevenir SQL Injection.
    if typ not in ("tipo", "cidade", "city", "type"):
        return

    if typ != "contas":
        qry = f"%{qry}%"

    if typ == "email":
        typ2 = "senha"
        typ3 = "cidade"
    else:
        typ2 = typ

    rt = cur.execute(
        f"SELECT email,  {typ2}, idcontas, cidade FROM contas WHERE {typ2} LIKE ? AND pending = 0 ORDER BY RANDOM() LIMIT 40",
        [qry.upper()],
    ).fetchall()

    results = []
    results.append(
            InlineQueryResultArticle(
                title=f"Total: ({len(rt)}) de resultados encontrados",
                description="Confira todas as contas abaixo 🛍👇",
                
                input_message_content=InputTextMessageContent(
                    "Compre contas via Inline ✅"
                ),
            )
        )

    wallet_info = get_info_wallet(m.from_user.id)

    for email, value, idcontas, cidade in rt:

        price = await get_price("contas", value)

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
                        callback_data=f"buy_off_contas idcontas '{idcontas}'",
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
@Client.on_callback_query(filters.regex(r"^comprar_contas unit$"))
async def comprar_contas(c: Client, m: CallbackQuery):
    list_levels_contas = cur.execute("SELECT tipo FROM contas GROUP BY tipo").fetchall()
    levels_list = [x[0] for x in list_levels_contas]

    if not levels_list:
        return await m.answer(
            "⚠️ Não há contas premium disponíveis no momento, tente novamente mais tarde.",
            show_alert=True,
        )

    levels = []
    for level in levels_list:
        level_name = level
        n = level.split()
        if len(n) > 1:
            level_name = n[0][:4] + " " + n[1]

        price = await get_price("contas", level)
        levels.append(
            InlineKeyboardButton(
                text=f"{level_name.upper()} | R$ {price} - Aleatório 🎲",
                callback_data=f"buy_off_contas tipo '{level}'",
            )
        )

    organ = (
        lambda data, step: [data[x : x + step] for x in range(0, len(data), step)]
    )(levels, 2)
    table_name = "contas"
    contas = cur.execute(
        f"SELECT tipo, count() FROM {table_name} GROUP BY tipo ORDER BY count() DESC"
    ).fetchall()

    
    total = f"\n\n<b>🧿 Total de Contas Betano</b>: {sum([int(x[1]) for x in contas])}" if contas else ""
    
    organ.append([InlineKeyboardButton(text="❮ ❮", callback_data="comprar_contas")])
    kb = InlineKeyboardMarkup(inline_keyboard=organ)
    await m.edit_message_text(
        f"""<b>👾 Comprar Contas Betao</b>

<i>- Qual o tipo de Contas Betano que você deseja comprar?</i>


{total}


{get_info_wallet(m.from_user.id)}""",
        reply_markup=kb,
    )




@Client.on_callback_query(
    filters.regex(r"^buy_off_contas (?P<type>[a-z]+) '(?P<level_contas>.+)' ?(?P<other_params>.+)?")  # fmt: skip
)
@lock_user_buy
async def buy_off_contas(c: Client, m: CallbackQuery):
    user_id = m.from_user.id
    balance: int = cur.execute("SELECT balance FROM users WHERE id = ?", [user_id]).fetchone()[0]  # fmt: skip

    type_contas = m.matches[0]["type"]
    level_contas = m.matches[0]["level_contas"]

    price = await get_price("contas", level_contas)

    if balance < price:
        return await m.answer(
            "⚠️ Você não possui saldo suficiente para esse item. Por favor, faça uma transferência.",
            show_alert=True,
        )

    search_for = "tipo" if type_contas == "tipo" else "idcontas"

    selected_contas = cur.execute(
        f"SELECT tipo, email, senha, added_date, cidade, idcontas FROM contas WHERE {search_for} = ? AND pending = ? ORDER BY RANDOM()",
        [level_contas, False],
    ).fetchone()

    if not selected_contas:
        return await m.answer("⚠️ Sem contas betano disponiveis para este nivel.", show_alert=True)

    diamonds = round(((price / 100) * 8), 2)
    new_balance = balance - price
    
    (
        tipo,
        email,
        senha,
        added_date,
        cidade,
        idcontas,
    ) = selected_contas
    #nome = nome.upper()
    card = "|".join([tipo, email, senha])
    ds = "contas"
    list_card_sold = selected_contas + (user_id, ds)

    cur.execute(
        "DELETE FROM contas WHERE idcontas = ?",
        [selected_contas[5]],
    )

    cur.execute(
        "UPDATE users SET balance = ?, balance_diamonds = round(balance_diamonds + ?, 2) WHERE id = ?",
        [new_balance, diamonds, user_id],
    )

    s = insert_contas_sold(list_card_sold)
    print(s)
    insert_sold_balance(price, user_id, "contas")
    #dados = (cpf, name) if cpf is not None else None
    base = await msg_buy_off_user_contas(user_id, email, senha, tipo, price, cidade)
    await m.edit_message_text(base)
    mention = create_mention(m.from_user)
    adm_msg = msg_group_adm_contas(
        mention, email, senha, tipo, price, "None", new_balance, cidade
    )

    pub = msg_group_publico_contas(mention, email, senha, tipo, price, "None", new_balance, cidade)
    await c.send_message(ADMIN_CHAT, adm_msg)

    kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="💳 Compre as melhores Contas betano",url=f"https://t.me/LojinhaBetano_bot"
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
