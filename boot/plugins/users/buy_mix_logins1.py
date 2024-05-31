from io import BytesIO

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from config import ADMIN_CHAT
from database import cur, save
from plugins.users.buy_cc import chking
from utils import (
    create_mention,
    get_info_wallet,
    get_price,
    insert_buylogi_sold,
    insert_sold_balance,
    lock_user_buy,
    msg_mix_buy_user,
    msg_mix_group_adm,
)


# OpÃ§Ã£o Compra de CCs tipo Mix.
@Client.on_callback_query(filters.regex(r"^comprar_logins mix$"))
async def buy_mixes_login(c: Client, m: CallbackQuery):
    levels_list_logins = cur.execute(
        "SELECT price_name, price, price FROM prices WHERE price_type LIKE ?", ["loginsmix"]
    ).fetchall()
    levels_list_logins.sort(key=lambda x: x[0])
    #levels_list = [x[0] for x in levels_list]
    print(levels_list_logins)

    if not levels_list_logins:
        return await m.answer(
            "⚠️ Não hã Mixes disponiveis no momento, tente novamente mais tarde.",
            show_alert=True,
        )

    levels = []
    for level, price, tipo in levels_list_logins:
        levels.append(
            InlineKeyboardButton(
                text=f"Mix {level} {tipo} | R$ {price}",
                callback_data=f"comprar_log mix {level}",
            )
        )

    organ = (
        lambda data, step: [data[x : x + step] for x in range(0, len(data), step)]
    )(levels, 2)
    organ.append([InlineKeyboardButton(text="❮ ❮", callback_data="comprar_log")])
    kb = InlineKeyboardMarkup(inline_keyboard=organ)

    await m.edit_message_text(
        f"""<b> Comprar Mix</b>
<i>- Escolha abaixo a quantidade desejada.</i>

{get_info_wallet(m.from_user.id)}""",
        reply_markup=kb,
    )


@Client.on_callback_query(filters.regex(r"^comprar_log mix (?P<quantitylog>\d+)"))
@lock_user_buy
async def buy_mixes_log(c: Client, m: CallbackQuery):
    user_id = m.from_user.id
    balance: int = cur.execute("SELECT balance FROM users WHERE id = ?", [user_id]).fetchone()[0]  # fmt: skip

    type_log = "logins"
    quantitylog = int(m.matches[0]["quantitylog"])

    do_checklog = quantitylog <= 20

    price = await get_price(type_log, quantitylog)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="❮ ❮", callback_data="comprar_log"),
            ],
        ]
    )

    if balance < price:
        return await m.answer(
            "⚠️ Você não possui saldo suficiente para esse item. Por favor, faça uma transferencia.",
            show_alert=True,
        )

    logins_list = cur.execute(
        "SELECT tipo, email, senha, cidade, idlogin, added_date FROM logins WHERE pending = ? ORDER BY RANDOM() LIMIT ?",
         [False, quantitylog * 20 if do_checklog else quantitylog],
    ).fetchall()

    if len(logins_list) < quantitylog:
        return await m.answer(
            "⚠️ Não hã logins disponiveis para o tamanho do logins requisitado.",
            show_alert=True,
        )

    logins_list = []

    await m.edit_message_text("⏳ Aguarde, estou processando o seu pedido...")

    for log in logins_list:
        (
            tipo,
            email,
            senha,
            cidade,
            idlogin,
            added_date,
        ) = log

        logins = "|".join([tipo, email, senha, idlogin,cidade,added_date])
        is_pending = cur.execute(
            "SELECT pending FROM logins WHERE email = ?", [log[0]]
        ).fetchone()
        # Se retornar None, a cc jÃ¡ foi vendida ou marcada die.
        # Se is_pending[0] for True, ela estÃ¡ sendo verificada por outro processo.
        if not is_pending or is_pending[0]:
            continue
        cur.execute("UPDATE logins SET pending = 1 WHERE email = ?", [email])
        if do_checklog:
            livelog_or_die = True, True
        else:
            livelog_or_die = True, True

        if livelog_or_die[0]:  # caso venha cc live
            logins_list.append(log)
            if len(logins_list) == quantitylog:
                break
            if do_checklog:
                await m.edit_message_text(
                    f"⏳ Aguarde, estou processando o seu pedido... ({len(logins_list)}/{quantitylog})"
                )

        elif livelog_or_die[0] is False:  # ccs type return None
            cur.execute("UPDATE logins SET pending = False WHERE idlogin = ?", [log[4]])

        else:  # para cc die
            cur.execute(
                "DELETE FROM logins WHERE email = ?",
                [log[0]],
            )
            values = "tipo, email, senha, idlogin,cidade, added_date, plan"
            listlog_dies = log + (type_log,)
            cur.execute(
                f"INSERT INTO cards_dies({values}) VALUES(?, ?, ?, ?, ?, ?, ?)",
                listlog_dies,
            )
    # Fim do for, finaliza a compra aqui.

    # Se o tamanho da lista de CCs checadas for inferior a quantidade:
    if len(logins_list) < quantitylog:
        return await m.edit_message_text(
            "⚠️ Infelizmente erro.",
            reply_markup=kb,
        )

    # Se o tamaho da lista for igual ao requisitado (sucesso), continua a compra:
    diamonds = (price / 100) * 8

    base = await msg_mix_buy_user(
        user_id,
        quantitylog,
        price,
        diamonds,
    )

    to_message = []

    for new_login in logins_list:
        (
            tipo, email, senha, idlogin,cidade
        ) = new_login

        cur.execute(
            "DELETE FROM logins WHERE email = ?",
            [idlogin],
        )

        list_dados = new_login + (user_id, f"mix {quantitylog}", False)

        insert_buylogi_sold(list_dados)

        to_message.append("|".join([tipo, email, senha, idlogin,cidade]))

    insert_sold_balance(price, user_id, "logins", quantity=quantitylog)

    await m.edit_message_text(base)

    file = BytesIO()
    file.name = f"mix_{m.from_user.id}.txt"
    file.write("\n".join(to_message).encode())

    await m.message.reply_document(file)

    cur.execute(
        "UPDATE users SET balance = round(balance - ?, 2), balance_diamonds = round(balance_diamonds + ?, 2) WHERE id = ?",
        [price, diamonds, user_id],
    )

    await m.message.reply_text(
        "✅ Compra realizada com sucesso. Clique no botão abaixo para voltar para o menu principal.",
        reply_markup=kb,
    )

    mention = create_mention(m.from_user)
    adm_msg = msg_mix_group_adm(
        mention,
        quantitylog,
        price,
        round(balance - price, 2),
    )
    await c.send_message(ADMIN_CHAT, adm_msg)
    await c.send_document(ADMIN_CHAT, file)

    save()
