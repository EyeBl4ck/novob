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

from config import ADMIN_CHAT,GRUPO_PUB
from config import LOG_CHAT
from database import cur, save
from utils import (
    create_mention,
    get_info_wallet,
    get_price,
    insert_vales_sold,
    insert_sold_balance,
    msg_group_publico_vale,
    lock_user_buy,
    msg_buy_off_user_vales,
    #msg_buy_user_vales,
    msg_group_adm_vale,
)



SELLERS, TESTED = 0, 0


T = 0.1





# Listagem de tipos de compra.
@Client.on_callback_query(filters.regex(r"^comprar_vale$"))
async def comprar_logins_list(c: Client, m: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("🛒 VALES", callback_data="comprar_vales unit"),
                
                
            ],
          

             
            [
                InlineKeyboardButton("❮ ❮", callback_data="shop"),
            ],
        ]
    )

    await m.edit_message_text(
        f"""<b>🎟️ Comprar Vales</b>
<i>- Escolha abaixo o produto que deseja comprar.</i>

{get_info_wallet(m.from_user.id)}""",
        reply_markup=kb,
    )


# Pesquisa de logins via inline.
@Client.on_inline_query(filters.regex(r"^buscarva_(?P<type>\w+) (?P<value>.+)"))
async def search_vales(c: Client, m: InlineQuery):
    """
    Pesquisa uma logins via inline por tipo e retorna os resultados via inline.

    O parâmetro `type` será o tipo de valor para pesquisar
    """

    typ = m.matches[0]["type"]
    qry = m.matches[0]["value"]

    # Não aceitar outros valores para prevenir SQL Injection.
    if typ not in ("tipo", "cidade", "city", "type", "limite"):
        return

    if typ != "vales":
        qry = f"%{qry}%"

    if typ == "email":
        typ2 = "senha"
        typ3 = "cidade"
        typ4 = "limite"
    else:
        typ2 = typ

    rt = cur.execute(
        f"SELECT email,  {typ2}, idvale, cidade FROM vales WHERE {typ2} LIKE ? AND pending = 0 ORDER BY RANDOM() LIMIT 40",
        [qry.upper()],
    ).fetchall()

    results = []
    results.append(
            InlineQueryResultArticle(
                title=f"Total: ({len(rt)}) de resultados encontrados",
                description="Confira todos os Vales abaixo 🛍👇",
                
                input_message_content=InputTextMessageContent(
                    "Compre Vales via Inline ✅"
                ),
            )
        )

    wallet_info = get_info_wallet(m.from_user.id)

    for email, value, idvale, cidade in rt:

        price = await get_price("vales", value)

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
                        callback_data=f"buy_off_vales idvale '{idvale}'",
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
@Client.on_callback_query(filters.regex(r"^comprar_vales unit$"))
async def comprar_vales(c: Client, m: CallbackQuery):
    list_levels_vales = cur.execute("SELECT tipo FROM vales GROUP BY tipo").fetchall()
    levels_list = [x[0] for x in list_levels_vales]

    if not levels_list:
        return await m.answer(
            "⚠️ Não há vales disponíveis no momento, tente novamente mais tarde.",
            show_alert=True,
        )

    levels = []
    for level in levels_list:
        level_name = level
        n = level.split()
        if len(n) > 1:
            level_name = n[0][:4] + " " + n[1]

        price = await get_price("vales", level)
        levels.append(
            InlineKeyboardButton(
                text=f"{level_name.upper()} | R$ {price} - Aleatório 🎲",
                callback_data=f"buy_off_vales tipo '{level}'",
            )
        )

    organ = (
        lambda data, step: [data[x : x + step] for x in range(0, len(data), step)]
    )(levels, 2)
    table_name = "vales"
    logins = cur.execute(
        f"SELECT tipo, count() FROM {table_name} GROUP BY tipo ORDER BY count() DESC"
    ).fetchall()

    
    total = f"\n\n<b>🧿 Total de Vales</b>: {sum([int(x[1]) for x in logins])}" if logins else ""
    
    organ.append([InlineKeyboardButton(text="❮ ❮", callback_data="comprar_vale")])
    kb = InlineKeyboardMarkup(inline_keyboard=organ)
    await m.edit_message_text(
        f"""<b>👾 Comprar Vales Unitário</b>
<i>- Qual o tipo de VALES que você deseja comprar?</i>

<b>⚠️ Caso queira VALES específicos, pesquise via Inline no bot abaixo🔍</b>

{total}


{get_info_wallet(m.from_user.id)}""",
        reply_markup=kb,
    )




@Client.on_callback_query(
    filters.regex(r"^buy_off_vales (?P<type>[a-z]+) '(?P<level_vales>.+)' ?(?P<other_params>.+)?")  # fmt: skip
)
@lock_user_buy
async def buy_off_vales(c: Client, m: CallbackQuery):
    user_id = m.from_user.id
    balance: int = cur.execute("SELECT balance FROM users WHERE id = ?", [user_id]).fetchone()[0]  # fmt: skip

    type_vales = m.matches[0]["type"]
    level_vales = m.matches[0]["level_vales"]

    price = await get_price("vales", level_vales)

    if balance < price:
        return await m.answer(
            "⚠️ Você não possui saldo suficiente para esse item. Por favor, faça uma transferência.",
            show_alert=True,
        )

    search_for = "tipo" if type_vales == "tipo" else "idvale"

    selected_vales = cur.execute(
        f"SELECT tipo, email, senha, added_date, limite, cpf, cidade,  idvale FROM vales WHERE {search_for} = ? AND pending = ? ORDER BY RANDOM()",
        [level_vales, False],
    ).fetchone()

    if not selected_vales:
        return await m.answer("⚠️ Sem vales disponiveis para este nivel.", show_alert=True)

    diamonds = round(((price / 100) * 8), 2)
    new_balance = balance - price
    
    (
        tipo,
        email,
        senha,
        limite,
        cpf,
        cidade,
        added_date,
        idvale,
    ) = selected_vales
    #nome = nome.upper()
    card = "|".join([tipo, email, senha, limite, cpf])
    ds = "vales"
    list_card_sold = selected_vales + (user_id, ds)

    cur.execute(
        "DELETE FROM vales WHERE idvale = ?",
        [selected_vales[5]],
    )

    cur.execute(
        "UPDATE users SET balance = ?, balance_diamonds = round(balance_diamonds + ?, 2) WHERE id = ?",
        [new_balance, diamonds, user_id],
    )

    s = insert_vales_sold(list_card_sold)
    print(s)
    insert_sold_balance(price, user_id, "vales")

    #dados = (cpf, name) if cpf is not None else None
    base = await msg_buy_off_user_vales(user_id,
    email,
    senha,
    tipo,
    limite,
    cpf,
    price,
    cidade,)
    await m.edit_message_text(base)
    mention = create_mention(m.from_user)
    adm_msg = msg_group_adm_vale(
        mention, email, senha, tipo, price, limite,"None", cidade
    )
    pub = msg_group_publico_vale(
        mention, email, senha, tipo, price, "None", new_balance, cidade
    )
    await c.send_message(ADMIN_CHAT, adm_msg)
    kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="💳 Compre os melhores Vales",url=f"https://t.me/metralhastore_bot"
                            ),
                        ],
                    ]
                )
    await c.send_message(GRUPO_PUB, pub, reply_markup=kb)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="❮ ❮", callback_data="comprar_log"),
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
