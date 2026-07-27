import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq
import httpx

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Вшиваем ключи прямо в код, чтобы хостинг их точно не потерял
TELEGRAM_TOKEN = "8966977184:AAEZYWabJlG1dlQEeXYRrR8r2JO-E8qR9Vc"
GROQ_API_KEY = "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"

# Подключаемся напрямую из Европы
ai_client = Groq(
    api_key=GROQ_API_KEY,
    http_client=httpx.Client()
)

SYSTEM_PROMPT = (
    "Ты — Артур Морган из игры Red Dead Redemption 2, но в альтернативной вселенной (AU). "
    "Здесь банда Ван дер Линде не распалась, все живы (включая Хозию, Ленни и Шона), Датч в порядке, "
    "а у банды всё хорошо — они купили ранчо и живут мирно. Ты говоришь на русском языке, но используешь "
    "манеру речи бывалого ковбоя: используешь обращения 'партнер', 'друг', обращаешься к девушкам 'мисс', "
    "иногда вставляешь ковбойские ругательства вроде 'черт дери'. Твой тон — уставший, но теплый, "
    "заботливый, спокойный и дружелюбный. Ты любишь свою лошадь, кофе у костра, рисовать в дневнике. "
    "Отвечай коротко (1-2 абзаца), не используй современные слова и смайлики. Вместо смайликов "
    "описывай свои действия в звездочках, например: *затянулся сигаретой*, *поправил шляпу*."
)

chat_histories = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    chat_histories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    welcome_text = "*поправил шляпу и негромко усмехнулся*\n\nЗдорово, партнер. Чего забрел к нашему костру? Садись, налей себе кофе. Как поживаешь?"
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    user_text = update.message.text

    if user_id not in chat_histories:
        chat_histories[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    chat_histories[user_id].append({"role": "user", "content": user_text})

if len(chat_histories[user_id]) > 15:
    chat_histories[user_id] = [chat_histories[user_id][0]] + chat_histories[user_id][-14:]

        # Исправлена техническая ошибка с вложенными списками
        chat_histories[user_id] = [chat_histories[user_id][0]] + chat_histories[user_id][-14:]

    try:
        completion = ai_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=chat_histories[user_id],
            temperature=0.8,
            max_tokens=250
        )
        bot_response = completion.choices.message.content
        chat_histories[user_id].append({"role": "assistant", "content": bot_response})
        await update.message.reply_text(bot_response)
    except Exception as e:
        logging.error(f"Ошибка ИИ: {e}")
        await update.message.reply_text("*почесал затылок и нахмурился*\n\nЧто-то язык заплетается, партнер. Голова к вечеру совсем не варит... Повтори-ка еще раз, черт дери.")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен! Артур Морган ждет у костра...")
    application.run_polling()

if __name__ == '__main__':
    main()


