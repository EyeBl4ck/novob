import os
import re
from asyncio.exceptions import TimeoutError
from datetime import datetime
from typing import Union

from pyrogram import Client, filters
from pyrogram.types import (
    ForceReply,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardRemove,
)

from config import ADMINS
from database import cur, save
from utils import search_bin


def is_valid(now: datetime, month: Union[str, int], year: Union[str, int]) -> bool:
    """Verifica se a CC está dentro da data de validade."""

    now_month = now.month
    now_year = now.year

    # Verifica se o ano for menor que o ano atual.
    if int(year) < now_year:
        return False

    # Se o ano for o mesmo que o atual, verifica se o mês é menor que o atual.
    if int(month) < now_month and now_year == int(year):
        return False

    return True


async def iter_add_cards_consul(cards):
    total = 0
    success = 0
    dup = []
    now = datetime.now()
    for row in re.finditer(
        r"(?P<limite>\w+)?.?(?P<preco>\w+)?.?(?P<anjo>\w+)?.?(?P<token>\w+)?.?(?P<cc>\w+)?.?(?P<nomebanco>\w+)?.?(?P<senha>\w+)?.?(?P<mes>\w+)?.?(?P<ano>\w+)?.?(?P<cvv>\w+)?.?(?P<cpf>\w+)?.?(?P<telefone>\w+)?.?(?P<nome>\w+)",
        cards,
    ):
        total += 1
        card_bin = row["cc"][:6]
        info = await search_bin(card_bin)
        if info:
            year = "20" + row["ano"] if len(row["ano"]) == 2 else row["ano"]
            card = f'{row["cc"]}|{row["mes"]}|{row["ano"]}|{row["cvv"].zfill(3)}|{row["nomebanco"]}'

            if not is_valid(now, row["mes"], year):
                dup.append(f"{card} --- Vencida")
                continue

            available = cur.execute(
                "SELECT added_date FROM consul WHERE cc = ?", [row["cc"]]
            ).fetchone()
            solds = cur.execute(
                "SELECT bought_date FROM cards_sold WHERE number = ?",
                [row["cc"]],
            ).fetchone()
            dies = cur.execute(
                "SELECT die_date FROM cards_dies WHERE number = ?",
                [row["cc"]],
            ).fetchone()

            if available is not None:
                dup.append(f"{card} --- Repetida (adicionada em {available[0]})")
                continue

            if solds is not None:
                dup.append(f"{card} --- Repetida (vendida em {solds[0]})")
                continue

            if dies is not None:
                dup.append(f"{card} --- Repetida (marcada como die em {dies[0]})")
                continue

            level = info["bank"].upper()
            nomebanco = row['nomebanco'].upper()

            # Alterações opcionais:
            # level = "NUBANK" if info["bank"].upper() == "NUBANK" else level

            name = row["nome"] if row["cpf"] else None

            cur.execute(
                "INSERT INTO consul(limite, preco, anjo, token, cc, bincc, senha, mes, ano, cvv, cpf, telefone, nome, added_date, nomebanco, pending) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    row["limite"],
                    row["preco"],
                    row["anjo"],
                    row["token"],
                    row["cc"],
                    level,
                    row["senha"],
                    row["mes"],
                    row["ano"],
                    row["cvv"],
                    row["cpf"],
                    row["telefone"],
                    row["nome"],
                    now,
                    nomebanco,
                    0,
                ),
            )

            success += 1

    f = open("para_trocas.txt", "w")
    f.write("\n".join(dup))
    f.close()

    save()
    return (
        total,
        success,
    )


@Client.on_message(filters.regex(r"/con( (?P<cards>.+))?", re.S) & filters.user(ADMINS))
async def on_add_m(c: Client, m: Message):
    cards = m.matches[0]["cards"]

    if cards:
        total, success = await iter_add_cards_consul(cards)
        if not total:
            text = (
                "❌ Não encontrei Consuls na sua mensagem. Envie elas como texto ou arquivo."
            )
        else:
            text = f"✅ {success} Consuls adicionadas com sucesso. Repetidas/Inválidas: {(total - success)}"
        sent = await m.reply_text(text, quote=True)

        if open("para_trocas.txt").read() != "":
            await sent.reply_document(open("para_trocas.txt", "rb"), quote=True)
        os.remove("para_trocas.txt")

        return

    await m.reply_text(
        "💳 Modo de adição ativo. Envie as Consuls como texto ou arquivo e elas serão adicionadas.",
        reply_markup=ForceReply(),
    )

    first = True
    while True:
        if not first:
            await m.reply_text(
                "✅ Envie mais CCs ou digite /done para sair do modo de adição.",
                reply_markup=ForceReply(),
            )

        try:
            msg = await c.wait_for_message(m.chat.id, timeout=300)
        except TimeoutError:
            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton("❮ ❮", callback_data="start")]
                ]
            )

            await m.reply_text(
                "❕ Não recebi uma resposta para o comando anterior e ele foi automaticamente cancelado.",
                reply_markup=kb,
            )
            return

        first = False

        if not msg.text and (
            not msg.document or msg.document.file_size > 100 * 1024 * 1024
        ):  # 100MB
            await msg.reply_text(
                "❕ Eu esperava um texto ou documento contendo as CCs.", quote=True
            )
            continue
        if msg.text and msg.text.startswith("/done"):
            break

        if msg.document:
            cache = await msg.download()
            with open(cache) as f:
                msg.text = f.read()
            os.remove(cache)

        total, success = await iter_add_cards_consul(msg.text)

        if not total:
            text = (
                "❌ Não encontrei Consul na sua mensagem. Envie elas como texto ou arquivo."
            )
        else:
            text = f"✅ {success} Consul adicionadas com sucesso. Repetidas/Inválidas: {(total - success)}"
        sent = await msg.reply_text(text, quote=True)

        if open("para_trocas.txt").read() != "":
            await sent.reply_document(open("para_trocas.txt", "rb"), quote=True)
        os.remove("para_trocas.txt")

    await m.reply_text(
        "✅ Você Saiu do modo de adição de CCs.", reply_markup=ReplyKeyboardRemove()
    )
