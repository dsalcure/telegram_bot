import asyncio
import json
import os
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Pega TOKEN e CHAT_ID do Heroku (variáveis de ambiente)
TOKEN = os.getenv("TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

# ---------- FUNÇÕES PARA PERSISTÊNCIA ----------

def carregar_contas():
    if os.path.exists("contas.json"):
        with open("contas.json", "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_contas(contas):
    with open("contas.json", "w", encoding="utf-8") as f:
        json.dump(contas, f, ensure_ascii=False, indent=4)

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
            salvar_contas(contas)
            await update.message.reply_text(f"✅ Conta {nome} marcada como paga!")
            return

    await update.message.reply_text("Conta não encontrada.")

# ---------- VERIFICAÇÃO AUTOMÁTICA ----------

async def verificar_contas(app):
    while True:
        hoje = datetime.now().day
        for c in contas:
            if not c["pago"] and hoje >= c["dia"]:
                await app.bot.send_message(
                    chat_id=CHAT_ID,
                    text=f"⚠️ Conta {c['nome']} venceu ou vence hoje!"
                )
        await asyncio.sleep(60 * 60 * 6)  # verifica a cada 6 horas

# ---------- MAIN ----------

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("listar", listar))
    app.add_handler(CommandHandler("pago", pago))
    asyncio.create_task(verificar_contas(app))
    print("Bot rodando...")
    await app.run_polling()

# -------- EXECUÇÃO --------
import nest_asyncio
nest_asyncio.apply()
asyncio.get_event_loop().run_until_complete(main())