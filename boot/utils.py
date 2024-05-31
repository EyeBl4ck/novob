import html
from asyncio import Lock
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Iterable, Optional, Tuple, Union
import json
from random import randint
from config import BOT_LINK
from config import BOT_LINK
import httpx
from async_lru import alru_cache
from pyrogram import Client
from pyrogram.types import CallbackQuery, User

from database import cur

timeout = httpx.Timeout(40, pool=None)

hc = httpx.AsyncClient(http2=True, timeout=timeout)


lock = Lock()


def is_bot_online() -> bool:
    """Retorna `True` se o bot está online ou `False` se ele está em manutenção."""

    q = cur.execute("SELECT is_on from bot_config")

    return bool(q.fetchone()[0])


def is_user_banned(user_id: int) -> bool:
    """Retorna `True` se o usuário está banido ou `False` caso contrário."""

    q = cur.execute("SELECT is_blacklisted from users WHERE id = ?", [user_id])
    res = q.fetchone()

    return bool(res[0] if res else res)


def get_lara_info() -> Tuple[str, str]:
    """Retorna uma tupla contendo o nome da lara e chave Pix."""

    q = cur.execute("SELECT lara_name, lara_key from bot_config")

    return q.fetchone()


def get_support_user() -> str:
    """Retorna uma string contendo o username do usuário de STORE ."""

    q = cur.execute("SELECT support_user from bot_config")

    return q.fetchone()[0]


def get_news_user() -> str:
    """Retorna uma string contendo o username do canal de notícias."""

    q = cur.execute("SELECT channel_user from bot_config")

    return q.fetchone()[0]


def get_info_wallet(user_id: int) -> str:
    base = """<b>🧾 Seu perfil:</b>
<b> ├👤 ID:</b> <code>{}</code>
<b> └💸 Saldo: R$ {}</b>"""
    rt = cur.execute(
        "SELECT id, balance, balance_diamonds FROM users WHERE id=?", [user_id]
    ).fetchone()
    return base.format(*rt)

def dobrosaldo() -> str:
    #base = """<b>Bônus de recarga: {}</b>"""
    rt = cur.execute(
        "SELECT valordobro FROM dobrosaldo").fetchone()[0]
    rt = float(rt)
    if rt == 0:
     rt = "Desativado"
    else:
     rt = str(rt) + "%"
    #rt = rt
    return rt


def insert_buy_sold(lista: Iterable = "sequence"):
    list_itens = "number, month, year, cvv, level, added_date, vendor, bank, country, cpf, name, owner, plan, is_checked"
    cur.execute(
        f"INSERT INTO cards_sold({list_itens}) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        lista,
    )

def insert_buylogi_sold(lista: Iterable = "sequence"):
    list_itens = "tipo, email, senha, idlogin,cidade, added_date, plan"
    cur.execute(
        f"INSERT INTO logins_sold({list_itens}) VALUES(?, ?, ?, ?, ?, ?, ?)",
        lista,
    )

def insert_buy_sold_full(lista: Iterable = "sequence"):
    list_itens = "number, month, year, cvv, level, added_date, vendor, bank, country, cpf, name, owner, plan, is_checked"
    cur.execute(
        f"INSERT INTO cards_sold_full({list_itens}) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        lista,
    )

def insert_docs_sold(lista: Iterable = "sequence"):
    list_itens = "nome, cpf, linkdoc, added_date, level, idcpf, score ,localidade, owner, plan"
    cur.execute(
        f"INSERT INTO docs_sold({list_itens}) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        lista,
    )

def insert_logins_sold(lista: Iterable = "sequence"):
    list_itens = "tipo, email, senha, added_date, cidade, idlogin, owner, plan"
    cur.execute(
        f"INSERT INTO logins_sold({list_itens}) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
        lista,
    ) 

def insert_contas_sold(lista: Iterable = "sequence"):
    list_itens = "tipo, email, senha, added_date, cidade, idcontas, owner, plan"
    cur.execute(
        f"INSERT INTO contas_sold({list_itens}) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
        lista,
    )

def insert_mixs_sold(lista: Iterable = "sequence"):
    list_itens = "tipo, email, senha, added_date, cidade, idlogin, owner, plan"
    cur.execute(
        f"INSERT INTO logins_sold({list_itens}) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
        lista,
    )

def insert_vales_sold(lista: Iterable = "sequence"):
    list_itens = "tipo, email, senha, added_date, limite, cpf, cidade, idvale, owner, plan"
    cur.execute(
        f"INSERT INTO vales_sold({list_itens}) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        lista,
    )

def insert_sold_balance(value: int, owner: int, type_add_saldo: str, quantity: int = 1):
    cur.execute(
        """INSERT INTO sold_balance(type, value, owner, quantity) VALUES(?, ?, ?, ?)""",
        [type_add_saldo, value, owner, quantity],
    )

async def msg_buy_off_user_logins(
    user_id: int,
    email: str,
    senha: str,
    tipo: str,
    price: str,
    cidade: str,
    
) -> str:
    #cpf, name = dados if dados else await get_person()
    #bdados = f"""\n<b>Nome</b> <code>{name}</code>\n<b>Cpf:</b> <code>{cpf}</code>\n"""

    new_balance = cur.execute(
        "SELECT balance FROM users WHERE id = ?", [user_id]
    ).fetchone()[0]

    produto = f"""<b>💳 Produto:</b>
<b>LOGIN:</b> <code>{email}</code>
<b>SENHA:</b> <code>{senha}</code>

<b>Tenha boas aprovações!!</b>

"""

    base = f"""<b><a href='https://s4.aconvert.com/convert/p3r68-cdx67/tmyea-2idpo.jpeg'>&#8204</a><b> ☑️ Compra efetuada!</b>
<b>- Tipo de Login: {tipo} 📨</b>
<b>- Preço: R$ {price}</b>
<b>- Novo Saldo: R$ {new_balance}</b>

<b>Obrigado pela a preferência✅
</b>

{produto}"""
    return base

async def msg_buy_off_user_contas(
    user_id: int,
    email: str,
    senha: str,
    tipo: str,
    price: str,
    cidade: str,
    
) -> str:
    #cpf, name = dados if dados else await get_person()
    #bdados = f"""\n<b>Nome</b> <code>{name}</code>\n<b>Cpf:</b> <code>{cpf}</code>\n"""

    new_balance = cur.execute(
        "SELECT balance FROM users WHERE id = ?", [user_id]
    ).fetchone()[0]

    produto = f"""<b>💳 Produto:</b>
<b>LOGIN:</b> <code>{email}</code>
<b>SENHA:</b> <code>{senha}</code>

<b>Tenha boas aprovações!!</b>

"""

    base = f"""☑️ Compra efetuada!</b>
<b>- Tipo de Conta Premium: {tipo} 📨</b>
<b>- Preço: R$ {price}</b>
<b>- Novo Saldo: R$ {new_balance}</b>



<b>Obrigado pela a preferência✅
</b>


{produto}"""
    return base

async def msg_buy_off_user(
    user_id: int,
    card: str,
    vendor: str,
    country: str,
    bank: str,
    level_cc: str,
    price: int,
    received_points: float,
    dados: Optional[Tuple[str, str]] = None,
) -> str:
    cpf, name = dados if dados else await get_person()
    bdados = f"""\n<b>Nome</b> <code>{name}</code>\n<b>Cpf:</b> <code>{cpf}</code>\n"""

    new_balance = cur.execute(
        "SELECT balance FROM users WHERE id = ?", [user_id]
    ).fetchone()[0]

    produto = f"""<b>💳 Produto:</b>
<b>Card:</b> <code>{card}</code>
<b>Bandeira:</b> <code>{vendor}</code>
<b>País: </b><code>{country}</code>
<b>Banco: </b> <code>{bank}</code>"""

    base = f"""<b>☑️ Compra efetuada!</b>
<b>- {level_cc}</b>
<b>- Preço: R$ {price}</b>
<b>- Novo Saldo: R$ {new_balance}</b>
<b>- Pontos recebidos: {received_points}</b>


<b>NÃO GARANTIMOS A APROVAÇÃO</b>
<b>NÃO GARANTIMOS SALDO</b>

{produto}
{bdados}
Produto comprado com gate off, ou seja, sem troca."""
    return base

async def msg_buy_off_user_doc(
    user_id: int,
    nome: str,
    cpf: str,
    tipo: str,
    price: str,
    linkdoc: str,
    
) -> str:
    #cpf, name = dados if dados else await get_person()
    #bdados = f"""\n<b>Nome</b> <code>{name}</code>\n<b>Cpf:</b> <code>{cpf}</code>\n"""

    new_balance = cur.execute(
        "SELECT balance FROM users WHERE id = ?", [user_id]
    ).fetchone()[0]

    produto = f"""<b>💳 Produto:</b>
<b>Nome:</b> <code>{nome}</code>
<b>CPF:</b> <code>{cpf}</code>

<b>LINK PARA BAIXAR OS DOCUMENTOS:</b> {linkdoc}

"""

    base = f"""<b><a href='https://s4.aconvert.com/convert/p3r68-cdx67/tort6-yza4v.jpg'>&#8204</a><b>☑️ Compra efetuada!</b>
<b>- Tipo de documento: {tipo} 📨</b>
<b>- Preço: R$ {price}</b>
<b>- Novo Saldo: R$ {new_balance}</b>

<b>Obrigado pela a preferência, após baixado, guarde seus documentos ✅
</b>

{produto}"""
    return base


async def msg_buy_off_user_vales(
    user_id: int,
    email: str,
    senha: str,
    tipo: str,
    limite: str,
    cpf: str,
    price: str,
    cidade: str,
    
) -> str:
    #cpf, name = dados if dados else await get_person()
    #bdados = f"""\n<b>Nome</b> <code>{name}</code>\n<b>Cpf:</b> <code>{cpf}</code>\n"""

    new_balance = cur.execute(
        "SELECT balance FROM users WHERE id = ?", [user_id]
    ).fetchone()[0]

    produto = f"""<b>💳 Produto:</b>
<b>NOME:</b> <code>{email}</code>
<b>TELEFONE:</b> <code>{senha}</code>
<b>CPF:</b> <code>{cidade}</code>
<b>NASCIMENTO:</b> <code>{cpf}</code>
<b>Tenha boas aprovações!!</b>

"""

    base = f"""<b><a href='https://s4.aconvert.com/convert/p3r68-cdx67/tca8v-o55e8.png'>&#8204</a><b>☑️ Compra efetuada!</b>
<b>- Tipo de vale: {tipo} 📨</b>
<b>- Preço: R$ {price}</b>
<b>- Novo Saldo: R$ {new_balance}</b>

<b>Obrigado pela a preferência✅
</b>

{produto}"""
    return base

async def msg_buy_user(
    user_id: int,
    card: str,
    vendor: str,
    country: str,
    bank: str,
    level_cc: str,
    price: int,
    received_points: float,
    dados: Optional[Tuple[str, str]] = None,
) -> str:
    cpf, name = dados if dados else await get_person()

    time = cur.execute("SELECT time_exchange FROM bot_config").fetchone()[0]

    exchange_on = bool(cur.execute("SELECT exchange_is FROM bot_config").fetchone()[0])
    time_exchange = int(
        cur.execute("SELECT time_exchange FROM bot_config").fetchone()[0]
    )
    time_max = (datetime.now() + timedelta(minutes=time_exchange)).strftime(
        "%d/%m/%Y %H:%M:%S"
    )
    info = (
        f"<b>⏰ TEMPO MAXIMO PARA O REEMBOLSO: {time_max}. ({time} minutos)</b>"
        if exchange_on
        else ""
    )
    new_balance = cur.execute(
        "SELECT balance FROM users WHERE id = ?", [user_id]
    ).fetchone()[0]

    number, month, year, cvv = card.split("|")

    base = f"""<b>✅ Compra Efetuada! ✅

⚠️ TESTE NA KENNER www.kenner.com.br SE DER N7 E LIVE E NÃO TEM TROCA NEM ME CHAME CASO DER ESSE RETORNO⚠️</b>

<b>💳Cartão:</b> <code>{number}</code>
<b>📆DATA:</b> <code>{month}/{year}</code>
<b>🔐CVV:</b> <code>{cvv}</code>
<b>🛍️ Cartão Formatado:</b> <code>{card}</code>

<b>👤 DADOS PARA TE AUXILIAR:</b> 
<b>Nome:</b> <code>{name}</code>
<b>CPF:</b> <code>{cpf}</code>

<b>Nível:</b> {level_cc}
<b>Bandeira:</b> {vendor}
<b>Banco:</b> {bank}

<b>- Seu Saldo Restante:</b> R$ {new_balance}

DONATE TODO DIA

https://t.me/+U2RhP5FgwNk4ODhh

<b>{info}</b>"""
    return base


async def msg_mix_buy_user(
    user_id,
    level_cc,
    price,
    received_points,
) -> str:
    time = cur.execute("SELECT time_exchange FROM bot_config").fetchone()[0]

    swap_is = cur.execute("SELECT exchange_is FROM bot_config").fetchone()[0]

    new_balance = cur.execute(
        "SELECT balance FROM users WHERE id = ?", [user_id]
    ).fetchone()[0]

    troca = (
        f"\nVocê tem {time * level_cc} minutos para trocar se alguma CC não estiver live."
        if swap_is == 1
        else ""
    )

    base = f"""<b>✅ Compra efetuada!</b>
<b>- Mix {level_cc}</b>
<b>- Preço: R$ {price}</b>
<b>- Novo Saldo: R$ {new_balance}</b>


<b>GARANTIMOS SOMENTE LIVE!</b>
<b>NÃO GARANTIMOS A APROVAÇÃO</b>
<b>NÃO GARANTIMOS SALDO</b>
{troca}

<b>Produto segue no arquivo abaixo:</b>"""
    return base


def msg_group_adm(
    mention, card, level, type_buy, price, gate, new_balance, vendor
) -> str:
    produto = f"""<b>💳 </b> {mention} <b>comprou {type_buy} {level}</b>
<b>- Preço: R$ {price}</b>
<b>- Novo saldo: R$ {new_balance}</b>

<b>- Produto:</b>
<code>{card}|{vendor}|{gate}</code>"""
    return produto

def msg_group_adm_vale(
    mention, card, level, type_buy, price, gate, new_balance, vendor 
) -> str:
    produto = f"""<b>🎉 </b> {mention} <b>comprou {type_buy}</b>
<b>- Preço: R$ {price}</b>

<b>- Produto:</b>
<code>{card}|{level}|{vendor}</code>"""
    return produto

def msg_group_adm_logins(
    mention, card, level, type_buy, price, gate, new_balance, vendor
) -> str:
    produto = f"""<b>🎉 </b> {mention} <b>comprou {type_buy} cidade: {vendor}</b>
<b>- Preço: R$ {price}</b>
<b>- Novo saldo: R$ {new_balance}</b>

<b>- Produto:</b>
<code>{card}|{level}|{vendor}</code>"""
    return produto

def msg_group_adm_contas(
    mention, card, level, type_buy, price, gate, new_balance, vendor
) -> str:
    produto = f"""<b>🎉 </b> {mention} <b>comprou {type_buy} cidade: {vendor}</b>
<b>- Preço: R$ {price}</b>
<b>- Novo saldo: R$ {new_balance}</b>

<b>- Produto:</b>
<code>{card}|{level}|{vendor}</code>"""
    return produto

def msg_group_publico_logins(
    mention, card, level, type_buy, price, gate, new_balance, vendor
) -> str:
    produto = f"""<a href=</a><b>🎉</b>Comprou um login com sucesso</b>
<b>🔹Tipo: R$ {type_buy}</b>
<b>🔹Preço: R$ {price}</b>

<b>🥤{mention} obrigado pela a preferencia</b>

<a href='https://t.me/{BOT_LINK}'>STORE </a>"""
    return produto

def msg_group_publico_contas(
    mention, card, level, type_buy, price, gate, new_balance, vendor
) -> str:
    produto = f"""<a href='https://t.me/{BOT_LINK}'>&#8204</a><b>🎉</b>Comprou Contas Premium com sucesso</b>
<b>🔹Tipo: R$ {type_buy}</b>
<b>🔹Preço: R$ {price}</b>

<b>🥤{mention} obrigado pela a preferencia</b>


\n\n<a href='https://t.me/{BOT_LINK}'>STORE </a>"""
    return produto

def msg_group_publico_vale(
    mention, card, level, type_buy, price, limite, gate, new_balance
) -> str:
    produto = f"""<a href='https://t.me/{BOT_LINK}'>&#8204</a><b>🎉</b>Comprou um vale com sucesso</b>
<b>🔹Tipo Vale: R$ {type_buy}</b>
<b>🔹Preço: R$ {price}</b>
<b>🔹Limite: R$ {limite}</b>
<b>🥤{mention} obrigado pela a preferencia</b>


\n\n<a href='https://t.me/{BOT_LINK}'>STORE </a>"""
    return produto

def msg_group_pub_doc(
    mention, price, tipo, new_balance
) -> str:
    produto = f"""<a href='https://i.ibb.co/jyDBWmF/images.jpg'</a><b>💳 </b>DOC adquirido com sucesso! </b>
<b>🔹Tipo: {tipo}</b>
<b>🔹Preço: R$ {price}</b>

<b>🥤{mention} obrigado pela a preferencia</b>

<a href='https://t.me/{BOT_LINK}'>STORE </a>"""
    return produto

def msg_group_adm_doc(
    mention, nome, cpf, linkdoc, price, localidade, new_balance, score, tipo
) -> str:
    produto = f"""<b>🪪 </b> {mention} <b>comprou documento, Tipo: {tipo}</b>

<b>💰 - Preço: R$ {price}</b>
<b>💵 - Novo saldo: R$ {new_balance}</b>

<b>- Produto:</b>
<code>{nome}|{cpf}|{linkdoc}|{tipo}|{score}|{localidade}</code>

<b>📎 LINK DO DOCUMENTO:</b> {linkdoc}"""
    return produto
    
def msg_group_publico(
    mention, card, level, type_buy, price, gate, new_balance, vendor
) -> str:
    produto = f"""<a href=>&#8204</a><b>💳 </b>Cartão adquirido com sucesso! </b>
<b>🔹Nivel: R$ {level}</b>
<b>🔹Preço: R$ {price}</b>

<b>🥤{mention} obrigado pela a preferencia</b>


<b>- Produto:</b>
<code>{card[0:6]}**********|{vendor}</code>\n\n<a href='https://t.me/{BOT_LINK}'>STORE </a>"""
    return produto
    
    
def msg_group_adm_full(
    mention, card, level, type_buy, price, gate, new_balance, vendor
) -> str:
    produto = f"""<b>💳 </b> {mention} <b>comprou FULL DADOS {type_buy} {level}</b>
<b>- Preço: R$ {price}</b>
<b>- Novo saldo: R$ {new_balance}</b>

<b>- Produto:</b>
<code>{card}|{vendor}|{gate}</code>"""
    return produto
    
def msg_group_publico(
    mention, card, level, type_buy, price, gate, new_balance, vendor
) -> str:
    produto = f"""<a href=>&#8204</a><b>💳 </b>GG COMPRADA! </b>
<b>🔗 Tipo:R$ {level}</b>
<b>💰 Usuário:{mention} </b>
<b>- Produto:</b>
<code>{card[0:6]}**********|{vendor}</code>\n\n"""
    return produto

def msg_group_publico_full(
    mention, card, level, type_buy, price, gate, new_balance, vendor
) -> str:
    produto = f"""<a href='https://ibb.co/NCY4ZLG'>&#8204</a><b>💳 </b>Cartão FULL DADOS adquirido com sucesso! </b>
<b>🔹Nivel: R$ {level}</b>
<b>🔹Preço: R$ {price}</b>

<b>🥤{mention} obrigado pela a preferencia</b>


<b>- Produto:</b>
<code>{card[0:6]}**********|{vendor}</code>\n\n<a href='https://t.me/{BOT_LINK}'>STORE </a>"""
    return produto
    
    
    
def msg_group_publico_consul(
    mention, card, level, type_buy, price, gate, new_balance, name
) -> str:
    produto = f"""<a href=>&#8204</a><b>💳 </b>Consultavel adquirida com sucesso! </b>
<b>🔹Tipo de consultavel: {name}</b>
<b>🔹Preço: R$ {price}</b>

<b>🥤{mention} obrigado pela a preferencia</b>


<b>- Produto:</b>
<code>{card[0:6]}**********|{name}</code>\n\n<a href='https://t.me/{BOT_LINK}'>STORE </a>"""
    return produto


def msg_mix_group_adm(mention, quantity, price, new_balance) -> str:
    produto = f"""<b>📦 </b> {mention} <b>comprou Mix {quantity}</b>
<b>- Preço: R$ {price}</b>
<b>- Novo saldo: R$ {new_balance}</b>

<b>Produto segue no arquivo abaixo:</b>"""
    return produto


async def get_price(price_type: str, price_name: str) -> int:
    """
    Retorna uma int contendo o preço do item.

    O parâmetro `price_type` será o tipo de valor para pesquisar, ex.:
        UNIT (Por level) ou BIN (Por bin).
    O parâmetro `price_name` será o valor para pesquisa, ex.:
        GOLD (Por level) ou 550209 (Por bin).

    Por padrão, caso a compra for de tipo `BIN`, a função tentará obter
    o preço especifico da bin, e caso falhe, procurará o nível em `UNIT`,
    e caso falhe novamente, procurará o valor de INDEFINIDO em UNIT,
    e caso falhe novamente fará um "fallback" para R$ 12.
    """

    if price_type == "bin":
        price = cur.execute(
            "SELECT price FROM prices WHERE price_type = ? AND price_name LIKE ?",
            [price_type, price_name],
        ).fetchone()

        if price:
            return price[0]

        # Caso não exista preço de bin, pesquisa o level:
        new_price_type = "unit"
        price_name = (await search_bin(price_name))["level"]
    else:
        new_price_type = price_type

    # Caso seja unit ou a bin acima não tinha preço:
    price = cur.execute(
        "SELECT price FROM prices WHERE price_type = ? AND price_name LIKE ?",
        [new_price_type, price_name],
    ).fetchone()

    if price:
        return price[0] + (5 if price_type == "bin" else 0)

    # Caso o level requisitado não exista na db:
    price = cur.execute(
        "SELECT price FROM prices WHERE price_type = ? AND price_name LIKE ?",
        [new_price_type, "INDEFINIDO"],
    ).fetchone()

    if price:
        return price[0] + (5 if price_type == "bin" else 0)

    return 12
    
    
    
async def get_pricefull(price_type: str, price_name: str) -> int:
    """
    Retorna uma int contendo o preço do item.

    O parâmetro `price_type` será o tipo de valor para pesquisar, ex.:
        UNIT (Por level) ou BIN (Por bin).
    O parâmetro `price_name` será o valor para pesquisa, ex.:
        GOLD (Por level) ou 550209 (Por bin).

    Por padrão, caso a compra for de tipo `BIN`, a função tentará obter
    o preço especifico da bin, e caso falhe, procurará o nível em `UNIT`,
    e caso falhe novamente, procurará o valor de INDEFINIDO em UNIT,
    e caso falhe novamente fará um "fallback" para R$ 12.
    """

    if price_type == "null":
        price = cur.execute(
            "SELECT price FROM prices WHERE price_type = ? AND price_name LIKE ?",
            [price_type, price_name],
        ).fetchone()

        if price:
            return price[0]

        # Caso não exista preço de bin, pesquisa o level:
        new_price_type = "full"
        price_name = (await search_bin(price_name))["level"]
    else:
        new_price_type = price_type

    # Caso seja unit ou a bin acima não tinha preço:
    price = cur.execute(
        "SELECT price FROM pricesfull WHERE price_type = ? AND price_name LIKE ?",
        [new_price_type, price_name],
    ).fetchone()

    if price:
        return price[0] + (5 if price_type == "null" else 0)

    # Caso o level requisitado não exista na db:
    price = cur.execute(
        "SELECT price FROM pricesfull WHERE price_type = ? AND price_name LIKE ?",
        [new_price_type, "INDEFINIDO"],
    ).fetchone()

    if price:
        return price[0] + (5 if price_type == "null" else 0)

    return 12
    
    



async def get_person():
  with open("assets/pessoas.json", "r", encoding="utf8") as f:
    r = json.load(f)
    pessoas = r['pessoa']
    q = len(pessoas)
    pessoa = pessoas[randint(0, q-1)]
    cpf = pessoa['cpf']
    nome = pessoa['nome']
    return cpf, nome


def create_mention(user: User, with_id: bool = True) -> str:
    name = f"@{user.username}" if user.username else html.escape(user.first_name)

    mention = f"<a href='tg://user?id={user.id}'>{name}</a>"

    if with_id:
        mention += f" (<code>{user.id}</code>)"

    return mention


@alru_cache
async def search_bin(card_bin: Union[str, int]) -> dict:
    """Pesquisa informações sobre a bin e as retorna em um dict."""

    try:
        r = await hc.get(
            f"http://194.163.185.17/api/?bin={card_bin}",
        )

        rj = r.json()

        info = {"card_bin": card_bin,"country": rj["pais"] or "INDEFINIDO","vendor": rj["bandeira"] or "INDEFINIDO","card_type": rj["tipo"] or "INDEFINIDO","level": rj["level"] or "INDEFINIDO","bank": rj["banco"] or "INDEFINIDO",}
        return info
    except Exception as e:
        print(e)
        info = {
            "card_bin": card_bin,
            "country": "INDEFINIDO",
            "vendor": "INDEFINIDO",
            "card_type": "INDEFINIDO",
            "level": "INDEFINIDO",
            "bank": "INDEFINIDO",
        }
        return info


def to_hex(dec: float):
    digits = "0123456789ABCDEF"
    x = dec % 16
    rest = dec // 16
    if rest == 0:
        return digits[x]
    return to_hex(rest) + digits[x]


def get_crc16(payload: str):
    crc = 0xFFFF
    for i in range(len(payload)):
        crc ^= ord(payload[i]) << 8
        for j in range(8):
            if (crc & 0x8000) > 0:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
    return to_hex(crc & 0xFFFF).upper()


def create_copy_paste_pix(location: str) -> str:
    # Copy paste sem CRC16
    copy_paste = f"00020126830014br.gov.bcb.pix2561{location}520489995303986540105802BR5921Pagseguro Internet SA6009SAO PAULO62070503***6304"

    return copy_paste + get_crc16(copy_paste)


def lock_user_buy(f: Callable):
    @wraps(f)
    async def lock_user(c: Client, m: CallbackQuery, *args, **kwargs):
        q = cur.execute(
            "SELECT is_action_pending FROM users WHERE id = ?", [m.from_user.id]
        ).fetchone()
        cur.execute(
            "UPDATE users SET is_action_pending = ? WHERE id = ?",
            [True, m.from_user.id],
        )
        if q[0]:
            return await m.answer(
                "⚠️ Você só pode fazer uma compra/troca por vez. Por favor aguarde seu pedido anterior ser concluído.",
                show_alert=True,
            )
        try:
            return await f(c, m, *args, **kwargs)
        finally:
            cur.execute(
                "UPDATE users SET is_action_pending = ? WHERE id = ?",
                [False, m.from_user.id],
            )

    return lock_user
    
    
    
def lock_user_buy_full(f: Callable):
    @wraps(f)
    async def lock_user1(c: Client, m: CallbackQuery, *args, **kwargs):
        q = cur.execute(
            "SELECT is_action_pending FROM users WHERE id = ?", [m.from_user.id]
        ).fetchone()
        cur.execute(
            "UPDATE users SET is_action_pending = ? WHERE id = ?",
            [True, m.from_user.id],
        )
        if q[0]:
            return await m.answer(
                "⚠️ Você só pode fazer uma compra/troca por vez. Por favor aguarde seu pedido anterior ser concluído.",
                show_alert=True,
            )
        try:
            return await f(c, m, *args, **kwargs)
        finally:
            cur.execute(
                "UPDATE users SET is_action_pending = ? WHERE id = ?",
                [False, m.from_user.id],
            )

    return lock_user1
