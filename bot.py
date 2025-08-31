import os
import base64
import marshal
import zlib
import telebot
from telebot import types

# إعدادات البوت
token = "8101441285:AAH0kS8jpX1sgsXc2savAwVn4rpNz3tkRTA"  # توكن البوت
bot = telebot.TeleBot(token)

# إعدادات القناة الإجبارية
CHANNEL_USERNAME = "@zsewwi"  # يوزر القناة بدون @
CHANNEL_ID = -1001234567890   # معرف القناة (يمكن الحصول عليه من البوت @userinfobot)

def check_subscription(user_id):
    """التحقق من اشتراك المستخدم في القناة"""
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

def encode_files(name, file_name):
    if name == 'marshal':
        en = marshal.dumps(compile(open(file_name, 'rb').read(), file_name, 'exec'))
        return f"import marshal\nexec(marshal.loads({repr(en)}))" 
    elif name == 'base64':
        en = base64.b64encode(open(file_name, 'rb').read())
        return f"import base64\nexec(base64.b64decode({repr(en)}))"
    elif name == 'lambda':
        en = zlib.compress(open(file_name, 'rb').read())
        return f"exec((lambda __, _: exec(zlib.decompress(_)))(None, {repr(en)}))"
    elif name == 'zlib':
        en = zlib.compress(marshal.dumps(compile(open(file_name, 'rb').read(), file_name, 'exec')))
        return f"import zlib, marshal\nexec(marshal.loads(zlib.decompress({repr(en)})))"

def welcome(message):
    channel = types.InlineKeyboardButton('📢 قناتي', url='https://t.me/zsewwi')
    start = types.InlineKeyboardButton('⚡ اضغط هنا لخيارات التشفير', callback_data='start')
    programmer = types.InlineKeyboardButton('👨‍💻 المطور', url='https://t.me/M_6_P_6')
    keyboards = types.InlineKeyboardMarkup()
    keyboards.row_width = 1
    keyboards.add(start, programmer, channel)
    bot.send_message(message.chat.id, '🤖 | أهلاً بك في بوت التشفير الخاص بـ Python', reply_markup=keyboards)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # التحقق من الاشتراك في القناة
    if not check_subscription(message.from_user.id):
        # إذا لم يكن مشتركاً، نطلب منه الاشتراك
        channel_btn = types.InlineKeyboardButton('📢 اشترك في القناة', url=f'https://t.me/{CHANNEL_USERNAME[1:]}')
        check_btn = types.InlineKeyboardButton('✅ تحقق من الاشتراك', callback_data='check_subscription')
        markup = types.InlineKeyboardMarkup()
        markup.row_width = 1
        markup.add(channel_btn, check_btn)
        
        bot.send_message(message.chat.id, 
                        f'⚠️ | يجب عليك الاشتراك في القناة أولاً:\n{CHANNEL_USERNAME}',
                        reply_markup=markup)
        return
    
    welcome(message)

def encryption(message):
    button1 = types.InlineKeyboardButton('base64', callback_data='base64')
    button2 = types.InlineKeyboardButton('lambda', callback_data='lambda')
    button3 = types.InlineKeyboardButton('marshal', callback_data='marshal')
    button4 = types.InlineKeyboardButton('zlib 🔒', callback_data='zlib')
    keyy = types.InlineKeyboardMarkup()
    keyy.row_width = 1
    keyy.add(button1, button2, button3, button4)
    bot.send_message(message.chat.id, '🔰 | اختَر نوع التشفير:', reply_markup=keyy)

@bot.callback_query_handler(func=lambda call: True)
def callbacks_data(call):
    try:
        if call.data == 'start':
            # التحقق من الاشتراك قبل عرض خيارات التشفير
            if not check_subscription(call.from_user.id):
                channel_btn = types.InlineKeyboardButton('📢 اشترك في القناة', url=f'https://t.me/{CHANNEL_USERNAME[1:]}')
                check_btn = types.InlineKeyboardButton('✅ تحقق من الاشتراك', callback_data='check_subscription')
                markup = types.InlineKeyboardMarkup()
                markup.row_width = 1
                markup.add(channel_btn, check_btn)
                
                bot.send_message(call.message.chat.id, 
                                f'⚠️ | يجب عليك الاشتراك في القناة أولاً:\n{CHANNEL_USERNAME}',
                                reply_markup=markup)
                return
            encryption(call.message)
        elif call.data == 'check_subscription':
            # التحقق من الاشتراك مرة أخرى
            if check_subscription(call.from_user.id):
                welcome(call.message)
            else:
                bot.answer_callback_query(call.id, "لم تشترك بعد في القناة!", show_alert=True)
        elif call.data in ['base64', 'lambda', 'marshal', 'zlib']:
            # التحقق من الاشتراك قبل طلب الملف
            if not check_subscription(call.from_user.id):
                channel_btn = types.InlineKeyboardButton('📢 اشترك في القناة', url=f'https://t.me/{CHANNEL_USERNAME[1:]}')
                check_btn = types.InlineKeyboardButton('✅ تحقق من الاشتراك', callback_data='check_subscription')
                markup = types.InlineKeyboardMarkup()
                markup.row_width = 1
                markup.add(channel_btn, check_btn)
                
                bot.send_message(call.message.chat.id, 
                                f'⚠️ | يجب عليك الاشتراك في القناة أولاً:\n{CHANNEL_USERNAME}',
                                reply_markup=markup)
                return
            msg = bot.send_message(call.message.chat.id, '📥 | أرسل الملف المراد تشفيره')
            bot.register_next_step_handler(msg, lambda message: save_file(message, call.data))
    except Exception as ex:
        bot.send_message(call.message.chat.id, str(ex))

def save_file(message, name):
    try:
        # التحقق من الاشتراك مرة أخرى قبل معالجة الملف
        if not check_subscription(message.from_user.id):
            channel_btn = types.InlineKeyboardButton('📢 اشترك في القناة', url=f'https://t.me/{CHANNEL_USERNAME[1:]}')
            check_btn = types.InlineKeyboardButton('✅ تحقق من الاشتراك', callback_data='check_subscription')
            markup = types.InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(channel_btn, check_btn)
            
            bot.send_message(message.chat.id, 
                            f'⚠️ | يجب عليك الاشتراك في القناة أولاً:\n{CHANNEL_USERNAME}',
                            reply_markup=markup)
            return
            
        file_info = bot.get_file(message.document.file_id)
        file_input = bot.download_file(file_info.file_path)
        file_name = message.document.file_name
        with open(file_name, 'wb') as f:
            f.write(file_input)
        encoded = encode_files(name, file_name)
        with open(file_name, 'w') as f:
            f.write(encoded)
        with open(file_name, 'rb') as file_document:
            bot.send_document(message.chat.id, file_document)
        os.remove(file_name)
    except Exception as ex:
        bot.send_message(message.chat.id, str(ex))

if __name__ == "__main__":
    print("✅ Bot Started")
    bot.polling(none_stop=True)