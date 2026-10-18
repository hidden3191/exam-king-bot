import os
import threading
from flask import Flask
import telebot
import google.generativeai as genai

app = Flask(__name__)

# Render Environment se keys lega - GitHub me key likhne ki zarurat nahi
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

print(f"BOT_TOKEN Found: {bool(BOT_TOKEN)}")
print(f"GEMINI_API_KEY Found: {bool(GEMINI_API_KEY)}")

# Gemini Setup
model = None
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("Gemini Model Ready")
    except Exception as e:
        print(f"Gemini Error: {e}")

# Bot Setup
bot = None
if BOT_TOKEN:
    bot = telebot.TeleBot(BOT_TOKEN)
    print("TeleBot Ready")
else:
    print("ERROR: BOT_TOKEN missing in Render Environment")

@app.route('/')
def home():
    return "Exam King Bot is Live! Check Telegram."

if bot:
    @bot.message_handler(commands=['start'])
    def start_cmd(message):
        bot.reply_to(message, "✅ Bot Live Hai!\n\nKoi bhi topic bhejo, mai 5 MCQ ka Quiz bana dunga.\nExample: Photosynthesis, Indian History")

    @bot.message_handler(func=lambda m: True)
    def make_quiz(message):
        if not model:
            bot.reply_to(message, "GEMINI_API_KEY Render me set nahi hai. Environment me check karo.")
            return
        
        chat_id = message.chat.id
        topic = message.text
        
        try:
            bot.send_message(chat_id, f"⏳ *{topic}* par quiz bana raha hu...", parse
