```python
import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from anthropic import Anthropic

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = Anthropic(api_key=ANTHROPIC_API_KEY)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

conversas = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Oi! Eu sou o Jarvis. Pode me mandar uma mensagem de texto que eu respondo.")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    texto_usuario = update.message.text

    historico = conversas.get(chat_id, [])
    historico.append({"role": "user", "content": texto_usuario})

    try:
        resposta = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            messages=historico
        )
        texto_resposta = resposta.content[0].text
        historico.append({"role": "assistant", "content": texto_resposta})
        conversas[chat_id] = historico[-20:]

        await update.message.reply_text(texto_resposta)
    except Exception as e:
        logger.error(f"Erro: {e}")
        await update.message.reply_text("Deu um erro aqui, tenta de novo.")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    app.run_polling()

if __name__ == "__main__":
    main()
```
