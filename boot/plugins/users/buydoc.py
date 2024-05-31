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
from config import BOT_LINK
from config import BOT_LINK_SUPORTE
from database import cur, save
from utils import (
    create_mention,
    get_info_wallet,
    get_price,
    insert_docs_sold,
    insert_sold_balance,
    lock_user_buy,
    msg_buy_off_user_doc,
    msg_buy_user,
    msg_group_adm_doc,
    msg_group_pub_doc
)



SELLERS, TESTED = 0, 0


T = 0.1





# Listagem de tipos de compra.
@Client.on_callback_query(filters.regex(r"^comprar_doc$"))
async def comprar_doc_list(c: Client, m: CallbackQuery):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton("🛒 CNH & RG", callback_data="comprar_doc unit"),
                
                
            ],
          

             
            [
                InlineKeyboardButton("❮ ❮", callback_data="shop"),
            ],
        ]
    )

    await m.edit_message_text(
        f"""<b>🎟️ Comprar Documentos</b>
<i>- Escolha abaixo o produto que deseja comprar.</i>

{get_info_wallet(m.from_user.id)}""",
        reply_markup=kb,
    )


# Pesquisa de CCs via inline.
@Client.on_inline_query(filters.regex(r"^buscardoc_(?P<type>\w+) (?P<value>.+)"))
async def search_doc(c: Client, m: InlineQuery):
    """
    Pesquisa uma documentos via inline por tipo e retorna os resultados via inline.

    O parâmetro `type` será o tipo de valor para pesquisar
    """

    typ = m.matches[0]["type"]
    qry = m.matches[0]["value"]

    # Não aceitar outros valores para prevenir SQL Injection.
    if typ not in ("doc", "docs", "score", "cidade"):
        return

    if typ != "bicos":
        qry = f"%{qry}%"

    if typ == "doc":
        typ2 = "level"
        typ3 = "nome"
    elif typ == "cidade":
        typ2 = "level"
        typ3 = "localidade"
    elif typ == "score":
        typ2 = "level"
        typ3 = "score"
    else:
        typ2 = typ

    rt = cur.execute(
        f"SELECT cpf, nome,  {typ2}, idcpf, score, localidade FROM docscnh WHERE {typ2} LIKE ? AND pending = 0 ORDER BY RANDOM() LIMIT 40",
        [qry.upper()],
    ).fetchall()

    results = []
    results.append(
            InlineQueryResultArticle(
                title=f"Total: ({len(rt)}) de resultados encontrados",
                description="Confira todos os documentos abaixo 🛍👇",
                
                input_message_content=InputTextMessageContent(
                    "Compre documentos via Inline ✅"
                ),
            )
        )

    wallet_info = get_info_wallet(m.from_user.id)

    for cpf, nome, value, idcpf, score, localidade in rt:

        price = await get_price("docs", value)

        base = f"""CPF: {cpf[0:6]}********** Nome: {nome} 📊Score: {score} City: {localidade}"""

        base_ml = f"""<b>CPF:</b> <i>{cpf[0:6]}**********</i>
<b>Nome:</b> <i>{nome}</i>
<b>📊Score:</b> <i>{score}</i>
<b>Tipo:</b> <i>{value}</i>
<b>Localidade:</b> <i>{localidade}</i>

<b>Valor:</b> <i>R$ {price}</i>"""

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Comprar",
                        callback_data=f"buydoc_off idcpf '{idcpf}' {value}",
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
    

# Opção Compra de CCs e Listagem de Level's.
@Client.on_callback_query(filters.regex(r"^comprar_doc unit$"))
async def comprar_logi(c: Client, m: CallbackQuery):
    list_levels_logi = cur.execute("SELECT level FROM docscnh GROUP BY level").fetchall()
    levels_list = [x[0] for x in list_levels_logi]

    if not levels_list:
        return await m.answer(
            "⚠️ Não há docs disponíveis no momento, tente novamente mais tarde.",
            show_alert=True,
        )

    levels = []
    for level in levels_list:
        level_name = level
        n = level.split()
        if len(n) > 1:
            level_name = n[0][:4] + " " + n[1]

        price = await get_price("docs", level)
        levels.append(
            InlineKeyboardButton(
                text=f"{level_name.upper()} | R$ {price} - Aleatório 🎲",
                callback_data=f"buydoc_off level '{level}'",
            )
        )

    organ = (
        lambda data, step: [data[x : x + step] for x in range(0, len(data), step)]
    )(levels, 2)
    table_name = "docscnh"
    logins = cur.execute(
        f"SELECT level, count() FROM {table_name} GROUP BY level ORDER BY count() DESC"
    ).fetchall()

    
    total = f"\n\n<b>🧿 Total de documentos</b>: {sum([int(x[1]) for x in logins])}" if logins else ""
    organ.append([InlineKeyboardButton(
                    "🛒 Buscar docs por Nome",
                    switch_inline_query_current_chat="buscardoc_doc A",
                )])
    organ.append([InlineKeyboardButton(
                    "☂️ Buscar docs por Score",
                    switch_inline_query_current_chat="buscardoc_score 8",
                )])
    organ.append([InlineKeyboardButton(
                    "🌁 Buscar docs por Cidade",
                    switch_inline_query_current_chat="buscardoc_cidade SP",
                )])
    organ.append([InlineKeyboardButton(text="❮ ❮", callback_data="comprar_doc")])
    kb = InlineKeyboardMarkup(inline_keyboard=organ)
    await m.edit_message_text(
        f"""<b>👾 Comprar Docs Unitário</b>
<i>- Qual o tipo de DOCUMENTO que você deseja comprar?</i>

<b>⚠️ Caso queira documentos específicos, pesquise via Inline no bot abaixo🔍</b>

{total}


{get_info_wallet(m.from_user.id)}""",
        reply_markup=kb,
    )




@Client.on_callback_query(
    filters.regex(r"^buydoc_off (?P<type>[a-z]+) '(?P<level_log>.+)' ?(?P<other_params>.+)?")  # fmt: skip
)
@lock_user_buy
async def buydoc_off(c: Client, m: CallbackQuery):
    user_id = m.from_user.id
    balance: int = cur.execute("SELECT balance FROM users WHERE id = ?", [user_id]).fetchone()[0]  # fmt: skip
    type_logi = m.matches[0]["type"]
    level_logi = m.matches[0]["level_log"]
    tipo = m.matches[0]["other_params"]

    price = await get_price("docs", tipo)

    if balance < price:
        return await m.answer(
            "⚠️ Você não possui saldo suficiente para esse item. Por favor, faça uma transferência.",
            show_alert=True,
        )

    search_for = "level" if type_logi == "level" else "idcpf"

    selected_logi = cur.execute(
        f"SELECT nome, cpf, linkdoc, added_date, level, idcpf, score, localidade FROM docscnh WHERE {search_for} = ? AND pending = ? ORDER BY RANDOM()",
        [level_logi, False],
    ).fetchone()

    if not selected_logi:
        return await m.answer("⚠️ Sem Docs disponiveis para este nivel.", show_alert=True)

    diamonds = round(((price / 100) * 8), 2)
    new_balance = balance - price
    
    (
        nome,
        cpf,
        linkdoc,
        added_date,
        tipo,
        idcpf,
        score,
        localidade,
    ) = selected_logi
    #nome = nome.upper()
    card = "|".join([nome, cpf, linkdoc])
    ds = "docs"
    list_card_sold = selected_logi + (user_id, ds)

    cur.execute(
        "DELETE FROM docscnh WHERE cpf = ?",
        [selected_logi[1]],
    )

    cur.execute(
        "UPDATE users SET balance = ?, balance_diamonds = round(balance_diamonds + ?, 2) WHERE id = ?",
        [new_balance, diamonds, user_id],
    )

    s = insert_docs_sold(list_card_sold)
    print(s)
    insert_sold_balance(price, user_id, "docs")

    #dados = (cpf, name) if cpf is not None else None
    base = await msg_buy_off_user_doc(user_id, nome, cpf, tipo, price, linkdoc)
    await m.edit_message_text(base)
    mention = create_mention(m.from_user)
    adm_msg = msg_group_adm_doc(
        mention, nome, cpf, linkdoc, price, localidade, new_balance, score, tipo
    )
    pub_msg = msg_group_pub_doc(
        mention, price, tipo, new_balance
    )
    await c.send_message(GRUPO_PUB, pub_msg)
    kb = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="💳 Compre os melhores Docs",url=f"https://t.me/metralhastore_bot"
                            ),
                        ],
                    ]
                )
    await c.send_message(ADMIN_CHAT, adm_msg, reply_markup=kb)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="❮ ❮", callback_data="comprar_doc"),
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
    
    
    
@Client.on_callback_query(
    filters.regex(r"^buydoc_offs (?P<type>[a-z]+) '(?P<level_cc>.+)' ?(?P<other_params>.+)?")  # fmt: skip
)
@lock_user_buy
async def buydoc_offs(c: Client, m: CallbackQuery):
    user_id = m.from_user.id
    balance: int = cur.execute("SELECT balance FROM users WHERE id = ?", [user_id]).fetchone()[0]  # fmt: skip

    type_logi = m.matches[0]["type"]
    level_logi = m.matches[0]["level_cc"]

    price = await get_price("docs", level_logi)

    if balance < price:
        return await m.answer(
            "⚠️ Você não possui saldo suficiente para esse item. Por favor, faça uma transferência.",
            show_alert=True,
        )

    search_for = "level" if type_logi == "level" else "idcpf"

    selected_logi = cur.execute(
        f"SELECT nome, cpf, linkdoc, added_date, level, idcpf, score, localidade FROM docscnh WHERE {search_for} = ? AND pending = ? ORDER BY RANDOM()",
        [level_logi, False],
    ).fetchone()

    if not selected_logi:
        return await m.answer("⚠️ Sem Docs disponiveis para este nivel.", show_alert=True)

    diamonds = round(((price / 100) * 9), 2)
    new_balance = balance - price
    
    (
        nome,
        cpf,
        linkdoc,
        added_date,
        tipo,
        idcpf,
        score,
        localidade,
    ) = selected_logi
    #nome = nome.upper()
    card = "|".join([nome, cpf, linkdoc])
    ds = "docs"
    list_card_sold = type_logi + (user_id, ds)

    cur.execute(
        "DELETE FROM docscnh WHERE cpf = ?",
        [selected_logi[1]],
    )

    cur.execute(
        "UPDATE users SET balance = ?, balance_diamonds = round(balance_diamonds + ?, 2) WHERE id = ?",
        [new_balance, diamonds, user_id],
    )

    s = insert_docs_sold(list_card_sold)
    print(s)
    insert_sold_balance(price, user_id, "docs")

    #dados = (cpf, name) if cpf is not None else None
    base = await msg_buy_off_user_doc(user_id, nome, cpf, tipo, price, linkdoc)
    await m.edit_message_text(base)
    mention = create_mention(m.from_user)
    adm_msg = msg_group_adm_doc(
        mention, nome, cpf, linkdoc, price, localidade, new_balance, score, tipo
    )
    pub_msg = msg_group_pub_doc(
        mention, price, tipo, new_balance
    )
    await c.send_message(GRUPO_PUB, pub_msg)
    await c.send_message(ADMIN_CHAT, adm_msg)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="❮ ❮", callback_data="comprar_doc"),
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