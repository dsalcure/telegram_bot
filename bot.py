import asyncio
import json
import os
from datetime import datetime
from telegram import Update
from zoneinfo import ZoneInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ---------- CONFIGURAÇÃO ----------
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ---------- FUNÇÕES DE PERSISTÊNCIA ----------
#e

def carregar_dados():
    """
    Carrega o JSON de contas.
    Suporta tanto lista antiga quanto novo formato com 'mes' e 'contas'.
    """
    if os.path.exists("contas.json"):
        with open("contas.json", "r", encoding="utf-8") as f:
            dados = json.load(f)

        # Se for lista antiga, converte para novo formato automaticamente
        if isinstance(dados, list):
            return {"mes": datetime.now().month, "contas": dados}

        return dados

    # Arquivo não existe ainda
    return {"mes": datetime.now().month, "contas": []}

def salvar_dados(dados):
    with open("contas.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

dados = carregar_dados()
contas = dados["contas"]

# ---------- RESET MENSAL ----------

def resetar_mes():
    """Se mudou o mês, reseta todas as contas para não pagas"""
    mes_atual = datetime.now().month
    if dados["mes"] != mes_atual:
        for c in contas:
            c["pago"] = False
        dados["mes"] = mes_atual
        salvar_dados(dados)
        print("🔄 Reset mensal executado")

# ---------- COMANDOS DO BOT ----------

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
            salvar_dados(dados)
            await update.message.reply_text(f"✅ Conta {nome} marcada como paga!")
            return

    await update.message.reply_text("Conta não encontrada.")

# ---------- VERIFICAÇÃO AUTOMÁTICA ----------

async def verificar_contas(app):
    while True:
        BRASILIA = zoneinfo.ZoneInfo("America/Sao_Paulo")
        agora = datetime.now(tz=BRASILIA)
        hoje = agora.day
        hora = agora.hour
        print(hora)

        # Reset mensal automático
        resetar_mes()

        # Só enviar alertas depois das 10h
        if hora >= 13:
            for c in contas:
                if not c["pago"] and hoje >= c["dia"]:
                    await app.bot.send_message(
                        chat_id=CHAT_ID,
                        text=f"⚠️ Conta {c['nome']} venceu ou vence hoje!"
                    )

        await asyncio.sleep(60 * 60 * 2)  # verifica a cada 2 horas

        #await asyncio.sleep(60) 

# ---------- INICIALIZAÇÃO DO BOT ----------

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("listar", listar))
    app.add_handler(CommandHandler("pago", pago))

    # Cria a tarefa de verificação automática
    asyncio.create_task(verificar_contas(app))

    print("Bot rodando...")
    await app.run_polling()

# ---------- EXECUÇÃO ----------

import nest_asyncio
nest_asyncio.apply()
asyncio.get_event_loop().run_until_complete(main())
