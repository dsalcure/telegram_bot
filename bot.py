import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import nest_asyncio
import asyncio

# Garantir que o TOKEN está configurado corretamente
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN:
    raise ValueError("TOKEN não configurado no Railway")

if not CHAT_ID:
    raise ValueError("CHAT_ID não configurado no Railway")

CHAT_ID = int(CHAT_ID.strip())

# ---------- LER CONTAS DE JSON ----------
def carregar_contas():
    with open('contas.json', 'r') as file:
        return json.load(file)

contas = carregar_contas()

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
    # Usando a nova API com ApplicationBuilder
    app = ApplicationBuilder().token(TOKEN).build()

    # Adicionando handlers para os comandos
    app.add_handler(CommandHandler("listar", listar))
    app.add_handler(CommandHandler("pago", pago))

    print("Bot rodando...")
    await app.run_polling()

# Assegurando que o asyncio vai funcionar no Railway
nest_asyncio.apply()
asyncio.get_event_loop().run_until_complete(main())
