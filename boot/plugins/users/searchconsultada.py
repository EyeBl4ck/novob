import asyncio
import time
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQuery,
    Message,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

from config import ADMIN_CHAT
from config import LOG_CHAT
from database import cur, save
from utils import (
    create_mention,
    get_price,
    insert_sold_balance,
    get_info_wallet,
    msg_buy_off_user,
    msg_buy_user,
    msg_group_adm,
    msg_group_publico_consul,
)

from ..admins.panel_items.select_gate import gates



# Pesquisa de CCs via inline.
@Client.on_inline_query(filters.regex(r"^consulta_(?P<type>\w+) (?P<value>.+)"))
async def search_cc_consulta(c: Client, m: InlineQuery):
    """
    Pesquisa uma CC via inline por tipo e retorna os resultados via inline.

    O parâmetro `type` será o tipo de valor para pesquisar, ex.:
        bin (Por bin), bank (Por banco), vendor (Por bandeira), etc.
    O parâmetro `value` será o valor para pesquisa, ex.:
        550209 (Bin), Nubank (Banco), Mastercard (Bandeira), etc.
    """

    typ = m.matches[0]["type"]
    qry = m.matches[0]["value"]
    qry = qry[0:6]

    # Não aceitar outros valores para prevenir SQL Injection.
    if typ not in ("buy", "banco", "bandeira"):
        return

    if typ != "bin":
        qry = f"%{qry}%"

    if typ == "buy":
        typ2 = "nomebanco"
    elif typ == "bandeira":
        typ2 = "vendor"
    else:
        typ2 = typ

    rt = cur.execute(
        f"SELECT cc, mes, ano, {typ2}, limite, nome, anjo, token, bincc, preco, nomebanco FROM consulta WHERE {typ2} LIKE ? AND pending = 0 ORDER BY RANDOM() LIMIT 50",
        [qry.upper()],
    ).fetchall()

    results = []

    wallet_info = get_info_wallet(m.from_user.id)

    for number, month, year, value, limite, nome, anjo, token, bincc, preco, nomebanco in rt:

        price = preco

        base = f"""Limite: {limite}
Banco: {nomebanco}
Bandeira: {bincc}"""

        base_ml = f"""<b>Cartão:</b> <i>{number[0:6]}**********</i>
<b>Validade:</b> <i>**/****</i>
<b>Cvv:</b> <i>***</i>
<b>Nome:</b> {nome}
<b>Anjo:</b> {anjo}
<b>Token:</b> {token}
<b>Banco da consul:</b> {bincc}
<b>Consul:</b> {nomebanco}




<b>Valor:</b> <i>R$ {price}</i>\n\n
{wallet_info}"""

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Comprar",
                        callback_data=f"comprar_consulta cc '{number}'",
                    )
                ]
            ]
        )
        thumb = "https://cdn-icons-png.flaticon.com/512/4553/4553547.png"
        results.append(
            InlineQueryResultArticle(
                title=f". {typ} {value} - R$ {price}",
                description=base,
                thumb_url=thumb,
                input_message_content=InputTextMessageContent(
                    base_ml 
                ),
                reply_markup=kb,
            )
        )

    await m.answer(results, cache_time=5, is_personal=True)




#compra da consul
@Client.on_callback_query(
    filters.regex(r"^comprar_consulta (?P<type>[a-z]+) '(?P<level_cc>.+)' ?(?P<other_params>.+)?")  # fmt: skip
)
#@lock_user_buy
async def buy_off_consulta(c: Client, m: CallbackQuery):
    user_id = m.from_user.id
    balance: int = cur.execute("SELECT balance FROM users WHERE id = ?", [user_id]).fetchone()[0]  # fmt: skip

    type_cc = "bin"
    level_cc = m.matches[0]["level_cc"]

    

    search_for = "level" if type_cc == "unit" else "cc"

    selected_cc = cur.execute(
        f"SELECT limite, preco, anjo, token, cc, bincc, senha, mes, ano, cvv, cpf, telefone, nome, added_date, nomebanco FROM consulta WHERE {search_for} = ? AND pending = ? ORDER BY RANDOM() LIMIT 20",
        [level_cc, False],
    ).fetchone()
    
    
    

    if not selected_cc:
        return await m.answer("⚠️ Sem consul disponiveis para este nivel.", show_alert=True)

    (
        limite,
        preco,
        anjo,
        token,
        cc,
        bincc,
        senha,
        mes,
        ano,
        cvv,
        cpf,
        telefone,
        nome,
        added_date,
        nomebanco,     
    ) = selected_cc
    
    price = int(preco)

    if balance < price:
        return await m.answer(
            f"⚠️ Você não possui saldo suficiente para esse item R$ {price}. Por favor, faça uma transferência.",
            show_alert=True,
        )
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    "💳 ☂ Buscar Consultadas ", switch_inline_query_current_chat="consulta_buy itau"
                ),
            ],
            
            
            
        ]
    )
    
    
    cur.execute(
        "DELETE FROM consulta WHERE cc = ?",
        [selected_cc[4]],
    )

  
    
    
    await m.edit_message_text(
            "<b>🔄 Por favor aguarde , estou realizando a sua compra!</b>"
        )
    time.sleep(2)
    
    
    insert_sold_balance(price, user_id, "consulta")         
    now = 2
    list_itens = "limite, preco, anjo, token, cc, bincc, senha, mes, ano, cvv, cpf, telefone, nome, added_date, nomebanco, bought_date, owner"
    atest = cur.execute(
        f"INSERT INTO consulta_solds({list_itens}) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [limite, preco, anjo, token, cc, bincc, senha, mes, ano, cvv, cpf, telefone, nome, added_date, nomebanco, now, user_id],
    )
    print(atest)
    save()
    live_or_die = True
    if live_or_die == True:  # caso venha cc live
                diamonds = 0
                new_balance = round(balance - price, 2)

                cur.execute(
                    "UPDATE users SET balance = round(balance - ?, 2), balance_diamonds = round(balance_diamonds + ?, 2) WHERE id = ?",
                    [price, diamonds, user_id],
                )
    level_cc = bincc
    card = cc
    type_cc = "Consultadas"
    price = preco
    status = "Compra efetuada"
    vendor = f"{mes}|{ano}|{cvv} - {nome} - {senha} - Consultada: {nomebanco}"
    
              
    mention = create_mention(m.from_user)
    adm_msg = msg_group_adm(
                    mention,
                    card,
                    level_cc,
                    type_cc,
                    price,
                    status,
                    new_balance,
                    vendor,
                )
                
    mention = m.from_user.first_name
                
    adm_msg = msg_group_publico_consul(
                    mention,
                    card,
                    level_cc,
                    type_cc,
                    price,
                    status,
                    new_balance,
                    nomebanco,
                )
    await c.send_message(ADMIN_CHAT, adm_msg)
                
    await c.send_message(ADMIN_CHAT, adm_msg)
    
    base = f"""Compra feita com ✅

Preço: {preco}
Seu saldo atual após a compra: {balance}
Limite: R$ {limite}
CC: <code>{cc}</code>
cvv: <code>{cvv}</code>
Validade: <code>{mes}/{ano}</code>
Senha: <code>{senha}</code>
Banco da consultada: <code>{bincc}</code>
Tipo consultada: {nomebanco}

Nome: <code>{nome}</code>
CPF: <code>{cpf}</code>
Telefone: <code>{telefone}</code>
Anjo: {anjo}
Token: {token}
♠️♥️♣️♦️♠️♥️♣️♦️♠️♥️♣️♦️

*⚠️LEIA COM ATENÇÃO⚠️*

*📝 REGRAS DE TROCAS DAS INFO CONSULTADAS📝*

*⏰ 20 MIN DE TROCAS MEDIANTE A VIDEO VINCULANDO NA GOOGLE PLAY & MOSTRANDO O ERRO QUE O EMISSOR RECUSOU*

*💳 CONSULTADA CAIXA ADICIONAL NAO DA PARA CONSULTAR O SALDO LIGANDO, SOMENTE COM CHECKER ESPECÍFICO  

*✅ QUALQUER OUTRO ERRO QUE DER AO VINCULAR É PROBLEMA NA CONTA, QUANDO DA O ERRO QUE O EMISSOR RECUSOU QUER DIZER QUE ESTA DIE,ENTÃO A TROCA VAI SER EFETUADA SEM PROBLEMAS*

*👇COMO CONSULTAR SUA PORTO SEGURO:👇*

* >4004 3600 > NÚMERO DO CARD > 1 > 1*

*⛔️ NÃO ACEITO TESTE EM OUTRO SITE OU OUTRO APP*

*⛔️NÃO GARANTO SUA APROVAÇÃO*

*🟢GARANTO APENAS A QUALIDADE DO MATERIAL*         
         
♠️♥️♣️♦️♠️♥️♣️♦️♠️♥️♣️♦️♠️♥️"""

    
    await m.edit_message_text(base, reply_markup=kb,)
    







