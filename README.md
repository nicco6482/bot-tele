# Bot de Telegram con Llama 3 (Groq)

Bot de Telegram gratuito que usa Llama 3.1 a través de Groq API.

## Configuración Local

1. **Clonar/Descargar el proyecto**

2. **Crear entorno virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**:
   ```bash
   cp .env.example .env
   ```

   Edita `.env` con tus valores:
   ```
   TELEGRAM_BOT_TOKEN=tu_token_de_botfather
   GROQ_API_KEY=tu_api_key_de_groq
   ADMIN_USERNAME=tu_username_telegram
   ```

5. **Ejecutar**:
   ```bash
   python bot.py
   ```

## Despliegue en Render (Gratis)

1. **Crear cuenta en [Render](https://render.com)**

2. **Crear nuevo Web Service**:
   - Conecta tu repo de GitHub/GitLab
   - Selecciona "New Web Service"
   - Render detectará automáticamente la configuración desde `render.yaml`

3. **Añadir variables de entorno**:
   - `TELEGRAM_BOT_TOKEN`
   - `GROQ_API_KEY`
   - `ADMIN_USERNAME`

4. **Deploy** - Render instalará y ejecutará automáticamente

## Alternativa: Usar Webhook

Para Render (free tier), puede ser mejor usar webhook en lugar de polling:

```python
app.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get("PORT", 5000)),
    webhook_url=f"https://tu-app.onrender.com/{TELEGRAM_TOKEN}"
)
```

## Comandos del Bot

- `/start` - Iniciar el bot
- `/help` - Ver ayuda
- `/clear` - Limpiar historial
- `/info` - Información del bot

## Costos

- **Telegram**: Gratis
- **Groq**: Tier gratuito generoso (ver limits en console.groq.com)
- **Render**: 750 horas gratis/mes

## Licencia

MIT