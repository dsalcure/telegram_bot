from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN:
    raise ValueError("TOKEN não configurado no Railway")

if not CHAT_ID:
    raise ValueError("CHAT_ID não configurado no Railway")

CHAT_ID = int(CHAT_ID.strip())

# ---------- COMANDOS ----------
async def listar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensagem = "📋 Contas:\n\n"
    for c in contas:
        status = "✅ Pago" if c["pago"] else "❌ Pendente"
        mensagem += f"{c['nome']} - dia {c['dia']} - {status}\n"
    await update.message.reply_text(mensagem)

async def pago(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Use: /pago NomeDaConta")
        return

    nome = " ".join(context.args)

    for c in contas:
        if c["nome"].lower() == nome.lower():
            c["pago"] = True
            await update.message.reply_text(f"✅ Conta {nome} marcada como paga!")
            return

    await update.message.reply_text("Conta não encontrada.")

# ---------- MAIN ----------
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("listar", listar))
    app.add_handler(CommandHandler("pago", pago))

    print("Bot rodando...")
    await app.run_polling()

import nest_asyncio
import asyncio

nest_asyncio.apply()
asyncio.get_event_loop().run_until_complete(main())
