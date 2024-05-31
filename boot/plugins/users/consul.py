from typing import Union

from pyrogram import Client, filters
from pyrogram.errors import BadRequest
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from database import cur, save
from utils import create_mention, get_info_wallet, dobrosaldo

def obter_resultados(resultados):
    saida = ""
    for categoria, valores in list(resultados.items())[:3]:
        saida += f"\n💳 | ↓ {len(valores)} {categoria} ↓\n"
        for valor in valores:
            saida += f"{valor}\n"
    return saida


@Client.on_message(filters.command(["consul", "consul"]))
@Client.on_callback_query(filters.regex("^consul$"))
async def start(c: Client, m: Union[Message, CallbackQuery]):
    user_id = m.from_user.id

    rt = cur.execute(
        "SELECT id, balance, balance_diamonds, refer FROM users WHERE id=?", [user_id]
    ).fetchone()

    if isinstance(m, Message):
        """refer = (
            int(m.command[1])
            if (len(m.command) == 2)
            and (m.command[1]).isdigit()
            and int(m.command[1]) != user_id
            else None
        )

        if rt[3] is None:
            if refer is not None:
                mention = create_mention(m.from_user, with_id=False)

                cur.execute("UPDATE users SET refer = ? WHERE id = ?", [refer, user_id])
                try:
                    await c.send_message(
                        refer,
                        text=f"<b>O usuário {mention} se tornou seu referenciado.</b>",
                    )
                except BadRequest:
                    pass"""

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
           [
                InlineKeyboardButton(
                    "🏳️ Pesquisar Consul",
                    switch_inline_query_current_chat="consul_buy RENNER",
                ),
                InlineKeyboardButton(
                    "🏳️ Pesquisar Banco",
                    switch_inline_query_current_chat="consul_banco A",
                ),
            ],
            [
            InlineKeyboardButton(
                    "🏳️ Pesquisar Bandeira",
                    switch_inline_query_current_chat="consul_bandeira VISA",
                ),
            ],
            [
            InlineKeyboardButton(
                    "🏳️ Pesquisar por cc",
                    switch_inline_query_current_chat="consul_cc 5",
                ),
            ],
[               InlineKeyboardButton("🔸 Atualizar",callback_data="consul"),
                InlineKeyboardButton("🔸 Voltar",callback_data="consull"),
        
            ],
            ]
    )
    table_name = "consul"
    ccs = cur.execute(
        f"SELECT nomebanco, count() FROM {table_name} GROUP BY nomebanco ORDER BY count() DESC"
    ).fetchall()
    
    counts = cur.execute(
        f"SELECT COUNT(*) FROM consul"
    ).fetchone()

    stock = (
        "\n".join([f"<b>{it[0]}</b>: {it[1]}" for it in ccs])
        or "<b>⚠️ Sem consul no momento</b>"
    )
    total = f"\n\n<b>Total</b>: {sum([int(x[1]) for x in ccs])}" if ccs else ""
    
    
    
    resultados = {}
    first_three = list(resultados.items())[:3]

    for it in ccs:
    	rt = cur.execute(
    	f"SELECT limite, preco, anjo, token, cc, bincc, senha,mes, ano, cvv, cpf, telefone, nome, added_date,nomebanco FROM consul WHERE nomebanco = ? ORDER BY RANDOM() LIMIT 20",
    	[it[0]],).fetchall()
    	print(rt)
    	print(rt[0])
    	#message = f"""R$ {rt[1]}  {rt[4][0:6]}**********"""
#    	#results.append(rt)
    	for tp in rt:
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
            ) = tp
            message = f"""R${preco} - <code>{cc[0:12]}</code> - {nome} - R${limite}"""
            #cons.append(message)
            #linha = f"kkkkkkks {k}"
            chave = f"{nomebanco}"
            if chave not in resultados:
            	resultados[chave] = []
            resultados[chave].append(message)
            
            

            

#    resultados = {
#   'categoria1': [('item1', 'categoria1', 'descricao1'),
#   ('item3', 'categoria1', 'descricao3')],
#   'categoria2': [('item2', 'categoria2', 'descricao2'),
#   ('item4', 'categoria2', 'descricao4')]}
    
    

    
    
    start_message = f"""<b>⚜ Olá {m.from_user.first_name}, seja bem vindo a aba de consultaveis use /pix para realizar uma tranferencia. </b>
<a href='https://cdn.dribbble.com/users/2657768/screenshots/15420992/media/7854e227fa9c24f716be63d4a2f35fd9.mp4'>&#8204</a>

<b>✅ | LISTA COM {counts[0]} CONSULTÁVEIS </b>

<b> Preço  -     Consultavel     -  Nome  -  Limite </b>

<b>{obter_resultados(resultados)}</b>

<b>💳 Consultaveis Disponiveis - </b>\n\n{stock}{total}

<b>🎗 Leia as regras e termo de troca se não for de acordo não compre 🎗
⌛️ 15 Minutos para acesso
⏳ 2 Hora para troca por CVV ou VALIDADE errado Fazendo uma gravação comprando no app, Rotativo digital BH</b> 

<b>🔁  Nao havera troca por mateirial com senha suspensa todas sao consultada certa
💳 Compre o  material e acesse pelo 4g fixo se vier com print de acesso com wifi perde a troca
🔁 Nao havera troca por material com saldo inferior vai ser mandado um gift na percentagem</b>
"""

    if isinstance(m, CallbackQuery):
        send = m.edit_message_text
    else:
        send = m.reply_text
    save()
    await send(start_message, reply_markup=kb)
