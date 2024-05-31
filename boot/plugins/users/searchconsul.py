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

from config import ADMIN_CHAT,GRUPO_PUB
from config import LOG_CHAT
from config import BOT_LINK_SUPORTE
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
@Client.on_inline_query(filters.regex(r"^consul_(?P<type>\w+) (?P<value>.+)"))
async def search_cc_consul(c: Client, m: InlineQuery):
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
        f"SELECT cc, mes, ano, {typ2}, limite, nome, anjo, token, bincc, preco, nomebanco FROM consul WHERE {typ2} LIKE ? AND pending = 0 ORDER BY RANDOM() LIMIT 50",
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
                        callback_data=f"comprar_consul cc '{number}'",
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
    filters.regex(r"^comprar_consul (?P<type>[a-z]+) '(?P<level_cc>.+)' ?(?P<other_params>.+)?")  # fmt: skip
)
#@lock_user_buy
async def buy_off_consul(c: Client, m: CallbackQuery):
    user_id = m.from_user.id
    balance: int = cur.execute("SELECT balance FROM users WHERE id = ?", [user_id]).fetchone()[0]  # fmt: skip

    type_cc = "bin"
    level_cc = m.matches[0]["level_cc"]

    

    search_for = "level" if type_cc == "unit" else "cc"

    selected_cc = cur.execute(
        f"SELECT limite, preco, anjo, token, cc, bincc, senha, mes, ano, cvv, cpf, telefone, nome, added_date, nomebanco FROM consul WHERE {search_for} = ? AND pending = ? ORDER BY RANDOM() LIMIT 20",
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
                    "💳 ☂ Buscar Consultaveis ", switch_inline_query_current_chat="consul_buy itau"
                ),
            ],
            
            
            
        ]
    )
    
    
    cur.execute(
        "DELETE FROM consul WHERE cc = ?",
        [selected_cc[4]],
    )

  
    
    
    await m.edit_message_text(
            "<b>🔄 Por favor aguarde , estou realizando a sua compra!</b>"
        )
    time.sleep(2)
    
    
    insert_sold_balance(price, user_id, "consul")         
    now = 2
    list_itens = "limite, preco, anjo, token, cc, bincc, senha, mes, ano, cvv, cpf, telefone, nome, added_date, nomebanco, bought_date, owner"
    atest = cur.execute(
        f"INSERT INTO consul_solds({list_itens}) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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
    type_cc = "Consultavel"
    price = preco
    status = "Compra efetuada"
    vendor = f"{mes}|{ano}|{cvv} - {nome} - {senha} - Consul: {nomebanco}"
    
              
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
                
    pub_msg = msg_group_publico_consul(
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
                
    await c.send_message(GRUPO_PUB, pub_msg)
    
    base = f"""Compra feita com sucesso✅

Preço: {preco}
Seu saldo atual após a compra: {balance}
Limite: R$ {limite}
CC: <code>{cc}</code>
cvv: <code>{cvv}</code>
Validade: <code>{mes}/{ano}</code>
Senha: <code>{senha}</code>
Banco da consul: <code>{bincc}</code>
Tipo consul: {nomebanco}

Nome: <code>{nome}</code>
CPF: <code>{cpf}</code>
Telefone: <code>{telefone}</code>
Anjo: {anjo}
Token: {token}

⚠️  REGRAS DE TROCAS PORTO SEGURO  ⚠️

⚙ VENCIMENTO DA FATURA DIA 10

👇  PARA ACESSAR SUA PORTO CLIQUE NO LINK ABAIXO  👇
       
https://prime.altubots.com/chats/portofalecom/e2937dc92b2050bda5ca3cb6430842fa/index.html

⌛️ 10 MINUTOS DE TROCA POR ACESSO BLOQUEADO 

⏳ 20 MINUTOS DE TROCAS POR DADOS INCORRETOS

PASSOU DO PERIODO NÃO CHORE 👍

TROCAS SOMENTE ACEITA MEDIANTE A VIDEO VINCULANDO O CARD NA GOOGLE PLAY E MOSTRANDO O ERRO QUE O EMISSOR RECUSOU 👍


⚠️ REGRAS DE TROCAS DE OUTROS BANCOS ⚠️

❌ CONSULTAVEL COM LIMITE BAIXO NAO TEM TROCA ❌

⚠️ GARANTO O CARTÃO PRAZO PRA ENTRAR E CONFERIR SE TA TUDO OK E DE 10 MINUTOS
PARA VER SE TA BLOQUEADO
PASSOU E TA BLOQUEADO NÃO CHORE 👍

⚠️ PRAZO PARA DADOS ERRADO
CASO CVV OU DATA ERRADO
1 HORAS PRA TROCA SOMENTE COM LIGAÇÃO DO ATENDENTE
JA FAÇA PRA ADIANTAR SUA TROCA CASO PASSE E ACUSE DADOS ERRADO 👍

⚠️ Numero da central 
3003 3030 , 0800 720 3030
peça pra atualizar dados cadastrais
assim eles pedem cvv e data
vim com ligação editada ja perde a troca

🚨 LOGOU PELO WIFI JA ESQUEÇA TROCA OU ALGO DO TIPO 🚨

🚨 NÃO TROCO MATERIAL COM ACORDO OU FATURA EM ATRASO 🚨

✅ NENHUM VENDEDOR GARANTE TRAMPO
OQ GARANTIR E LOTTER ✍️

✅ COMPRE COM A NOÇÃO DE TUDO ISSO
NÃO QUEIRA ATRASAR SEU 
MANO Q ESTA NO CORRE TODOS OS DIAS ✍️🚀

✅ VAMOS PRA CIMA DOS TRAMPO
GOLPE É NO SISTEMA NÃO NO CLIENTE

Suporte @{BOT_LINK_SUPORTE}"""

    
    await m.edit_message_text(base, reply_markup=kb,)
    







