import os
import openai
from dotenv import load_dotenv
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Load environment variables
load_dotenv()
TELEGRAM_BOT_API_KEY = os.getenv("TELEGRAM_BOT_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

user_histories = {}
# Initialize OpenAI API client
openai.api_key = OPENAI_API_KEY

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_text(f"Привет, {user.first_name}! Я тут, чтобы помочь тебе. Просто задай мне вопрос.")

def chatbot_response(history):
    system_message = {"role": "system", "content": "You are a helpful assistant that speaks Russian."}
    conversation_history = [system_message] + history

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_history,
        max_tokens=100,
        n=1,
        temperature=0.5,
    )

    response_text = response.choices[0].message['content'].strip()
    return response_text


def message_handler(update: Update, context: CallbackContext):
    user_message = update.message.text
    chat_id = update.message.chat_id

    if chat_id not in user_histories:
        user_histories[chat_id] = []

    user_histories[chat_id].append({"role": "user", "content": user_message})

    response_text = chatbot_response(user_histories[chat_id])

    user_histories[chat_id].append({"role": "assistant", "content": response_text})

    context.bot.send_message(chat_id=chat_id, text=response_text)

def main():
    updater = Updater(TELEGRAM_BOT_API_KEY)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, message_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
