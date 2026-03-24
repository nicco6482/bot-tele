import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

# Cargar variables de entorno
load_dotenv()

# Configuración
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Cliente de Groq
client = Groq(api_key=GROQ_API_KEY)

# Historial de conversaciones por usuario
conversations = {}

def get_system_prompt(username=None):
    """Prompt del sistema para Claude-like behavior"""
    prompt = """Eres un asistente útil e inteligente. Responde de forma clara y concisa.
Sí el usuario pregunta algo, dale una respuesta directa y útil.
Puedes ayudar con programación, preguntas generales, y cualquier tarea.
Responde siempre en el mismo idioma que el usuario use."""

    if username:
        prompt += f"\n\nEl usuario se llama @{username}."

    return prompt

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start"""
    user = update.effective_user
    welcome_msg = f"""¡Hola {user.first_name}! 👋

Soy un bot inteligente impulsado por Llama 3 (via Groq).

Puedes:
• Hablar conmigo como un asistente normal
• Usar /clear para limpiar nuestra conversación
• Usar /help para ver más comandos

¡Envíame un mensaje!"""

    await update.message.reply_text(welcome_msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help"""
    help_text = """📚 *Comandos disponibles:*

/start - Iniciar el bot
/help - Mostrar esta ayuda
/clear - Limpiar historial de conversación
/info - Ver información del bot

Simplemente escribe un mensaje y te responderé usando IA."""

    await update.message.reply_text(help_text, parse_mode='Markdown')

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /clear - limpiar historial"""
    user_id = update.effective_user.id

    if user_id in conversations:
        conversations[user_id] = []
        await update.message.reply_text("🗑️ Historial de conversación limpiado.")
    else:
        await update.message.reply_text("No tienes historial para limpiar.")

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /info"""
    user = update.effective_user
    info_text = f"""ℹ️ *Información del Bot*

🤖 Modelo: Llama 3.3 70B
⚡ Provider: Groq
👤 Tu ID: `{user.id}`
👤 Tu username: @{user.username or 'No definido'}

Admin: @{ADMIN_USERNAME if ADMIN_USERNAME else 'No configurado'}"""

    await update.message.reply_text(info_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar mensajes de texto"""
    user = update.effective_user
    user_id = user.id
    username = user.username or ""

    # Obtener historial del usuario
    if user_id not in conversations:
        conversations[user_id] = []

    # Añadir mensaje del usuario al historial
    conversations[user_id].append({
        "role": "user",
        "content": update.message.text
    })

    # Limitar historial para evitar tokens excesivos
    if len(conversations[user_id]) > 20:
        conversations[user_id] = conversations[user_id][-20:]

    # Preparar mensajes para Groq
    messages = [
        {"role": "system", "content": get_system_prompt(username)}
    ] + conversations[user_id]

    try:
        # Enviar "typing" mientras procesa
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )

        # Llamada a Groq API
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=2048,
            temperature=0.7
        )

        reply = response.choices[0].message.content

        # Guardar respuesta en historial
        conversations[user_id].append({
            "role": "assistant",
            "content": reply
        })

        # Enviar respuesta (dividir si es muy larga)
        if len(reply) > 4000:
            # Dividir mensaje largo
            for i in range(0, len(reply), 4000):
                await update.message.reply_text(reply[i:i+4000])
        else:
            await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}")
        await update.message.reply_text(
            "❌ Hubo un error al procesar tu mensaje. Por favor intenta de nuevo."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejar errores"""
    logger.error(f"Error: {context.error}")

    if update and update.message:
        await update.message.reply_text(
            "❌ Ocurrió un error inesperado. Por favor intenta de nuevo."
        )

def main():
    """Iniciar el bot"""
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN no está configurado")

    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY no está configurado")

    # Puerto para webhooks (Render asigna automáticamente)
    port = int(os.environ.get("PORT", 5000))

    # Crear aplicación
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Añadir handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Manejar errores
    app.add_error_handler(error_handler)

    # Iniciar bot
    logger.info("🤖 Bot iniciado!")

    # Usar webhooks para Render (o polling en local)
    if os.environ.get("RENDER"):
        # En Render, usar webhooks
        webhook_url = f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{TELEGRAM_TOKEN}"
        logger.info(f"Webhook URL: {webhook_url}")
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=TELEGRAM_TOKEN,
            webhook_url=webhook_url
        )
    else:
        # En local, usar polling
        app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()