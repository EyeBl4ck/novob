from typing import Union

from pyrogram import Client, filters
from pyrogram.errors import BadRequest
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ForceReply,
)

from database import cur, save
from utils import create_mention, get_info_wallet, dobrosaldo
#from config import BOT_LINK
#from config import BOT_LINK_SUPORTE


@Client.on_message(filters.command(["cassino", "cassino"]))
@Client.on_callback_query(filters.regex("^cassino$"))
async def cassinos(c: Client, m: Union[Message, CallbackQuery]):
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
                InlineKeyboardButton("🎲 Dados", callback_data="dices"),
            
            
           
                InlineKeyboardButton("🎲 Ímpar ou Par", callback_data="impars"),
                InlineKeyboardButton("🎯 Dardo", callback_data="dart"),
             ],
             [
                InlineKeyboardButton("🎰 Lucky", callback_data="luckygame"),
                
            
             InlineKeyboardButton("🏀 Basquete", callback_data="ball"),
             
             InlineKeyboardButton("🎳 Boliche", callback_data="boliche"),
             ],
             
             [
        InlineKeyboardButton("Menu", callback_data="start"),
        ],
            
        ]
    )

    bot_logo, news_channel, support_user = cur.execute(
        "SELECT main_img, channel_user, support_user FROM bot_config WHERE ROWID = 0"
    ).fetchone()

    start_message = f"""<a href='https://images.unsplash.com/photo-1518895312237-a9e23508077d?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1184&q=80'>&#8204</a> <b> 🎰 Gosta de apostas e ganhar dinheiro no bot ao mesmo tempo? Está no lugar certo.</b>

{get_info_wallet(user_id)}


"""

    if isinstance(m, CallbackQuery):
        send = m.edit_message_text
    else:
        send = m.reply_text
    save()
    await send(start_message, reply_markup=kb)
    
    
    
#@Client.on_message(filters.command(["lu", "dados"]))
@Client.on_callback_query(filters.regex("^dices$"))
async def dicegames(c: Client, m: Message):
        kb = InlineKeyboardMarkup(
        inline_keyboard=[
        [
        InlineKeyboardButton("✅ Continue",callback_data="jogardices"),
        ],
        [
        InlineKeyboardButton("❌ Cancelar ", callback_data="cancel"),
        ],
        ]
        )
        message_lucky = f"""💰 jogue o dado se der 6 ganhe 6R$
⚠ custo 6 R$"""
        await m.edit_message_text(message_lucky, reply_markup=kb)    
    
 
@Client.on_callback_query(filters.regex("^jogardices$"))
async def stardices(c: Client, m: Message):
    user_id = m.from_user.id
    price = 6
    balance: int = cur.execute("SELECT balance FROM users WHERE id = ?", [user_id]).fetchone()[0]
    
    if balance < price:
            return await m.answer(
            "⚠️ Você não possui saldo para realizar esta aposta. Por favor, adicione saldo no menu principal.",show_alert=True,)
            
            
    om= await c.send_dice(user_id, "🎲")
    if om.dice.value == 6:
           value = 6
           cur.execute("UPDATE users SET balance = balance + ? WHERE id = ?", [value, user_id]).fetchone()
        
           text = f"✅ Você ganhou R$ 6,00 de saldo, por acerto no 6 🎲"
           await om.reply_text(text, quote=True)
	       
	       

    else:
           diamonds = 0
           new_balance = round(balance - price, 2)
           cur.execute("UPDATE users SET balance = round(balance - ?, 2), balance_diamonds = round(balance_diamonds + ?, 2) WHERE id = ?",[price, diamonds, user_id],)
           
           text = f"""{get_info_wallet(user_id)}
           
<b>⚠️ Você não tirou 6 🎲, foram descontados R$ 6,00 da sua conta</b>"""
           await om.reply_text(text, quote=True)						

@Client.on_callback_query(filters.regex("^jogardices$"))
async def stardices(c: Client, m: Message):
    user_id = m.from_user.id
    price = 6
    balance: int = cur.execute("SELECT balance FROM users WHERE id = ?", [user_id]).fetchone()[0]
    
    if balance < price:
            return await m.answer(
            "⚠️ Você não possui saldo para realizar esta aposta. Por favor, adicione saldo no menu principal.",show_alert=True,)
            
            
    om= await c.send_dice(user_id, "🎲")
    if om.dice.value == 6:
           value = 6
           cur.execute("UPDATE users SET balance = balance + ? WHERE id = ?", [value, user_id]).fetchone()
        
           text = f"✅ Você ganhou R$ 6,00 de saldo, por acerto no 6 🎲"
           await om.reply_text(text, quote=True)
	       
	       

    else:
           diamonds = 0
           new_balance = round(balance - price, 2)
           cur.execute("UPDATE users SET balance = round(balance - ?, 2), balance_diamonds = round(balance_diamonds + ?, 2) WHERE id = ?",[price, diamonds, user_id],)
           
           text = f"""{get_info_wallet(user_id)}
           
<b>⚠️ Você não tirou 6 🎲, foram descontados R$ 6,00 da sua conta</b>"""
           await om.reply_text(text, quote=True)          
    
#@Client.on_message(filters.command(["lu", "dados"]))
@Client.on_callback_query(filters.regex("^luckygame$"))
async def luckygame(c: Client, m: Message):
        kb = InlineKeyboardMarkup(
        inline_keyboard=[
        [
        InlineKeyboardButton("✅ Continue",callback_data="jogarlucky"),
        ],
        [
        InlineKeyboardButton("❌ Cancelar ", callback_data="cancel"),
        ],
        ]
        )
        message_lucky = f"""Padrão | Ganho R$
➖➖➖       |  7
🍇🍇🍇       |  12
🍋🍋🍋       |  16
7️⃣7️⃣7️⃣       |  20
⚠ custo 7 R$"""
        await m.edit_message_text(message_lucky, reply_markup=kb)

@Client.on_callback_query(filters.regex("^jogarlucky$"))
async def startluckys(c: Client, m: Message):
    user_id = m.from_user.id
    price = 7
    balance: int = cur.execute("SELECT balance FROM users WHERE id = ?", [user_id]).fetchone()[0]
    
    if balance < price:
            return await m.answer(
            "⚠️ Você não possui saldo para realizar esta aposta. Por favor, adicione saldo no menu principal.",show_alert=True,)
            
            
    om= await c.send_dice(user_id, "“🎰")
    if om.dice.value == 1:
           value = 7
           cur.execute("UPDATE users SET balance = balance + ? WHERE id = ?", [value, user_id]).fetchone()
        
           text = f"✅ Você ganhou R$ 7,00 de saldo, por acerto: ➖➖➖"
           await om.reply_text(text, quote=True)
	       
	       
    elif om.dice.value == 22:
           value = 12
           cur.execute("UPDATE users SET balance = balance + ? WHERE id = ?", [value, user_id]).fetchone()
           
           text = f"✅ Você ganhou R$ 12,00 de saldo, por acerto: 🍇🍇🍇"
           await om.reply_text(text, quote=True)
	       
    elif om.dice.value == 64:
           value = 20
           cur.execute("UPDATE users SET balance = balance + ? WHERE id = ?", [value, user_id]).fetchone()
           text = f"✅ Você ganhou R$ 20,00 de saldo, por acerto: 7⃣7⃣7⃣"
           await om.reply_text(text, quote=True)
	       
	       
    elif om.dice.value == 43:
           value = 16
           cur.execute("UPDATE users SET balance = balance + ? WHERE id = ?", [value, user_id]).fetchone()
           text = f"✅ Você ganhou R$ 16,00 de saldo, por acerto: 🍋🍋🍋"
           await om.reply_text(text, quote=True)
	       	       
    else:
           diamonds = 0
           new_balance = round(balance - price, 2)
           cur.execute("UPDATE users SET balance = round(balance - ?, 2), balance_diamonds = round(balance_diamonds + ?, 2) WHERE id = ?",[price, diamonds, user_id],)
           
           text = f"""{get_info_wallet(user_id)}
           
<b>⚠️ Você não acertou o alvo 🎯, foram descontados R$ 7,00 da sua conta<b/>"""
           await om.reply_text(text, quote=True)
	       	
#@Client.on_message(filters.command(["lu", "dados"]))
@Client.on_callback_query(filters.regex("^dart"))
async def dardo(c: Client, m: Message):

        kb = InlineKeyboardMarkup(
        inline_keyboard=[
        [
        InlineKeyboardButton("✅ Continue",callback_data="jogardart"),
        ],
        [
        InlineKeyboardButton("❌ Cancelar ", callback_data="casino"),
        ],
        ]
        )
        message_lucky = f"""💰 acertando no alvo ganho de 10R$
⚠ custo 8 R$"""
        await m.edit_message_text(message_lucky, reply_markup=kb)
        
        
        
								
@Client.on_callback_query(filters.regex("^jogardart$"))
async def startlucky(c: Client, m: Message):
    user_id = m.from_user.id
    price = 8
    balance: int = cur.execute("SELECT balance FROM users WHERE id = ?", [user_id]).fetchone()[0]
    
    if balance < price:
            return await m.answer(
            "⚠️ Você não possui saldo para realizar esta aposta. Por favor, adicione saldo no menu principal.",show_alert=True,)
            
            
    om= await c.send_dice(user_id, "🎯")
    if om.dice.value == 6:
           value = 10
           cur.execute("UPDATE users SET balance = balance + ? WHERE id = ?", [value, user_id]).fetchone()
        
           text = f"✅ Você ganhou R$ 10,00 de saldo, por acerto no alvo 🎯"
           await om.reply_text(text, quote=True)
	       
	       

    else:
           diamonds = 0
           new_balance = round(balance - price, 2)
           cur.execute("UPDATE users SET balance = round(balance - ?, 2), balance_diamonds = round(balance_diamonds + ?, 2) WHERE id = ?",[price, diamonds, user_id],)
           
           text = f"""{get_info_wallet(user_id)}
           
<b>⚠️ Você não acertou o alvo 🎯, foram descontados R$ 8,00 da sua conta</b>"""
           await om.reply_text(text, quote=True)						
           
@Client.on_callback_query(filters.regex("^ball$"))
async def ballgame(c: Client, m: Message):
        
        kb = InlineKeyboardMarkup(
        inline_keyboard=[
        [
        InlineKeyboardButton("✅ Continue",callback_data="jogarball"),
        ],
        [
        InlineKeyboardButton("❌ Cancelar ", callback_data="casino"),
        ],
        ]
        )
        message_lucky = f"""💰 Jogue na cesta
- se entrar batendo no aro ganhe 5
- se for perfeito 8 R$

⚠ custo 4 R$"""
        await m.edit_message_text(message_lucky, reply_markup=kb)
        
        
        
@Client.on_callback_query(filters.regex("^jogarball$"))
async def jogarball(c: Client, m: Message):
    user_id = m.from_user.id
    price = 4
    balance: int = cur.execute("SELECT balance FROM users WHERE id = ?", [user_id]).fetchone()[0]
    
    if balance < price:
            return await m.answer(
            "⚠️ Você não possui saldo para realizar esta aposta. Por favor, adicione saldo no menu principal.",show_alert=True,)
            
            
    om= await c.send_dice(user_id, "🏀")
    if om.dice.value == 4:
           value = 5
           cur.execute("UPDATE users SET balance = balance + ? WHERE id = ?", [value, user_id]).fetchone()
        
           text = f"✅ Você ganhou R$ 5,00 de saldo, por acerto quase perfeito no aro 🏀"
           await om.reply_text(text, quote=True)
	       
    elif om.dice.value == 5:
           value = 8
           cur.execute("UPDATE users SET balance = balance + ? WHERE id = ?", [value, user_id]).fetchone()
           text = f"✅ Você ganhou R$ 8,00 de saldo, por acerto na cesta 🏀"
           await om.reply_text(text, quote=True)
	       	       	       

    else:
           diamonds = 0
           new_balance = round(balance - price, 2)
           cur.execute("UPDATE users SET balance = round(balance - ?, 2), balance_diamonds = round(balance_diamonds + ?, 2) WHERE id = ?",[price, diamonds, user_id],)
           
           text = f"""{get_info_wallet(user_id)}
           
<b>⚠️ Você não acertou a cesta 🏀, foram descontados R$ 4,00 da sua conta</b>"""
           await om.reply_text(text, quote=True)						
           

@Client.on_callback_query(filters.regex("^impars$"))
async def pargame(c: Client, m: Message):
        
        kb = InlineKeyboardMarkup(
        inline_keyboard=[
        [
        InlineKeyboardButton("✌️ Par",callback_data="par"),
        
        
        InlineKeyboardButton("☝️Impar",callback_data="impar"),
        
        
        InlineKeyboardButton("❌ Cancelar ", callback_data="casino"),
        ],
        ]
        )
        message_lucky = f"""💰 Aposte em PAR ou IMPAR se acertar ganhar 5R$       
⚠ custo 5 R$"""
        await m.edit_message_text(message_lucky, reply_markup=kb)																		
        
@Client.on_callback_query(filters.regex("^par$"))
async def startpar(c: Client, m: Message):
    user_id = m.from_user.id
    price = 5
    balance: int = cur.execute("SELECT balance FROM users WHERE id = ?", [user_id]).fetchone()[0]
    
    if balance < price:
            return await m.answer(
            "⚠️ Você não possui saldo para realizar esta aposta. Por favor, adicione saldo no menu principal.",show_alert=True,)
            
            
    om= await c.send_dice(user_id, "🎲")
    if (om.dice.value%2) == 0:
           value = 5
           cur.execute("UPDATE users SET balance = balance + ? WHERE id = ?", [value, user_id]).fetchone()
        
           text = f"⚠️ Você ganhou R$ 5,00 de saldo, por apostar em PAR ✌️"
           await om.reply_text(text, quote=True)
	       
	       

    else:
           diamonds = 0
           new_balance = round(balance - price, 2)
           cur.execute("UPDATE users SET balance = round(balance - ?, 2), balance_diamonds = round(balance_diamonds + ?, 2) WHERE id = ?",[price, diamonds, user_id],)
           
           text = f"""{get_info_wallet(user_id)}
           
<b>⚠️ Você perdeu, deu IMPAR ☝️, foram descontados R$ 5,00 da sua conta</b>"""
           await om.reply_text(text, quote=True)		        		

           																							           																							
@Client.on_callback_query(filters.regex("^impar$"))
async def startimpar(c: Client, m: Message):
    user_id = m.from_user.id
    price = 5
    balance: int = cur.execute("SELECT balance FROM users WHERE id = ?", [user_id]).fetchone()[0]
    
    if balance < price:
            return await m.answer(
            "⚠️ Você não possui saldo para realizar esta aposta. Por favor, adicione saldo no menu principal.",show_alert=True,)
            
            
    om= await c.send_dice(user_id, "🎲")
    if (om.dice.value%2) == 0:
           diamonds = 0
           new_balance = round(balance - price, 2)
           cur.execute("UPDATE users SET balance = round(balance - ?, 2), balance_diamonds = round(balance_diamonds + ?, 2) WHERE id = ?",[price, diamonds, user_id],)
           
           text = f"""{get_info_wallet(user_id)}
           
<b>⚠️ Você perdeu, deu PAR ✌️, foram descontados R$ 5,00 da sua conta</b>"""
           await om.reply_text(text, quote=True)		        	       	

    else:
           value = 5
           cur.execute("UPDATE users SET balance = balance + ? WHERE id = ?", [value, user_id]).fetchone()
        
           text = f"✅ Você ganhou R$ 5,00 de saldo, por apostar em IMPAR ☝️"
           await om.reply_text(text, quote=True)
	       
	       
@Client.on_callback_query(filters.regex("^boliche$"))
async def boliches(c: Client, m: Message):

        
        kb = InlineKeyboardMarkup(
        inline_keyboard=[
        [
        InlineKeyboardButton("✅ Continue",callback_data="jogarball"),
        ],
        [
        InlineKeyboardButton("❌ Cancelar ", callback_data="casino"),
        ],
        ]
        )
        message_lucky = f"""💰 fazendo o STRIKE ganha 10R$
⚠ custo 8R$"""
        await m.edit_message_text(message_lucky, reply_markup=kb)																		
                   
 
@Client.on_callback_query(filters.regex("^jogarball$"))
async def startball(c: Client, m: Message):
    user_id = m.from_user.id
    price = 8
    balance: int = cur.execute("SELECT balance FROM users WHERE id = ?", [user_id]).fetchone()[0]
    
    if balance < price:
            return await m.answer(
            "⚠️ Você não possui saldo para realizar esta aposta. Por favor, adicione saldo no menu principal.",show_alert=True,)
            
            
    om= await c.send_dice(user_id, "🎳")
    if om.dice.value == 6:
           value = 10
           cur.execute("UPDATE users SET balance = balance + ? WHERE id = ?", [value, user_id]).fetchone()
        
           text = f"Você ganhou R$ 10,00 de saldo, por STRIKE 🎳"
           await om.reply_text(text, quote=True)
	       
	       

    else:
           diamonds = 0
           new_balance = round(balance - price, 2)
           cur.execute("UPDATE users SET balance = round(balance - ?, 2), balance_diamonds = round(balance_diamonds + ?, 2) WHERE id = ?",[price, diamonds, user_id],)
           
           text = f"""{get_info_wallet(user_id)}
           
<b>⚠️ Você não deu STRIKE 🎳 , foram descontados R$ 8,00 da sua conta</b>"""
           await om.reply_text(text, quote=True)						
                   																																																																																																																																																																																																																																																																									       																																																																																																																																																																																																																																																																									
