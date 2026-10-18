import os, json, asyncio, threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import google.generativeai as genai

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "Exam King Bot is LIVE 24/7"

def get_quiz_data(subject):
    prompt = f"Create 50 MCQs on {subject}. Return ONLY JSON array: [{{\"q\":\"Q?\",\"options\":[\"A\",\"B\",\"C\",\"D\"],\"answer\":0,\"explain\":\"why\"}}]"
    for m in MODELS:
        try:
            model = genai.GenerativeModel(m)
            res = model.generate_content(prompt)
            txt = res.text
            return json.loads(txt[txt.find('['):txt.rfind(']')+1])
        except: continue
    return []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("SSC GD 50 Quiz", callback_data="SSC GD")],[InlineKeyboardButton("Railway 50 Quiz", callback_data="Railway NTPC")]]
    await update.message.reply_text("👑 Exam King Bot 24/7 Live! Subject chuno:", reply_markup=InlineKeyboardMarkup(kb))

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    subject = q.data
    await q.message.reply_text(f"⏳ {subject} par 50 quiz bana raha hu...")
    quizzes = await asyncio.to_thread(get_quiz_data, subject)
    for i, item in enumerate(quizzes, 1):
        await context.bot.send_poll(q.message.chat_id, f"{i}. {item['q']}"[:295], item['options'], type='quiz', correct_option_id=int(item['answer']), explanation=item.get('explain','')[:190], is_anonymous=False)
        await asyncio.sleep(0.4)

def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_button))
    app.run_polling()

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    app_flask.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
