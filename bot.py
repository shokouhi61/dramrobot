import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

TOKEN = "8826773951:AAHc1YlXzMYCqz28GbnwpRXSfOOvgxIUrg8"
CHANNEL_USERNAME = "@dram2ir"
ADMIN_CHAT_ID = 48460135
MINI_APP_URL = "https://shokouhi61.github.io/dramrobot/"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

users_db = {}

async def check_membership(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ["member", "creator", "administrator"]:
            return True
    except Exception as e:
        print(f"Error checking membership: {e}")
    return False

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    
    is_member = await check_membership(user_id)
    if not is_member:
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton(text="📢 عضویت در کانال", url="https://t.me/dram2ir"),
            InlineKeyboardButton(text="✅ عضو شدم، بررسی مجدد", callback_data="check_sub")
        )
        await message.answer(
            "⚠️ برای استفاده از بازار درام، لطفاً ابتدا در کانال ما عضو شوید:",
            reply_markup=keyboard
        )
        return

    if user_id not in users_db:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(KeyboardButton(text="📱 اشتراک‌گذاری شماره تلفن", request_contact=True))
        await message.answer(
            "خوش آمدید! برای ادامه و تایید هویت، لطفاً شماره تلفن خود را ارسال کنید:",
            reply_markup=keyboard
        )
    else:
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(InlineKeyboardButton(text="🛒 ورود به مینی‌اپ بازار درام", web_app=WebAppInfo(url=MINI_APP_URL)))
        await message.answer("شما قبلاً ثبت‌نام کرده‌اید. از طریق دکمه زیر می‌توانید وارد مینی‌اپ شوید:", reply_markup=keyboard)

@dp.message_handler(content_types=['contact'])
async def get_contact(message: types.Message):
    user_id = message.from_user.id
    phone_number = message.contact.phone_number
    full_name = message.from_user.full_name
    username = message.from_user.username or "ندارد"
    
    users_db[user_id] = {
        "phone": phone_number,
        "name": full_name,
        "username": username
    }
    
    report_text = (
        "📋 **گزارش ثبت‌نام کاربر جدید:**\n"
        f"👤 نام: {full_name}\n"
        f"🔗 یوزرنیم: @{username}\n"
        f"📞 شماره تماس: `{phone_number}`\n"
        f"🆔 شناسه کاربری: `{user_id}`"
    )
    
    try:
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=report_text, parse_mode="Markdown")
    except Exception as e:
        print(f"Failed to send report to admin: {e}")
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text="🛒 ورود به مینی‌اپ بازار درام", web_app=WebAppInfo(url=MINI_APP_URL)))
    
    await message.answer(
        "✅ شماره تلفن شما با موفقیت ثبت شد!\nاکنون می‌توانید از طریق دکمه زیر وارد مینی‌اپ شوید:",
        reply_markup=keyboard
    )

@dp.callback_query_handler(lambda c: c.data == 'check_sub')
async def callback_check_sub(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    is_member = await check_membership(user_id)
    
    if is_member:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.add(KeyboardButton(text="📱 اشتراک‌گذاری شماره تلفن", request_contact=True))
        await bot.send_message(
            chat_id=callback.message.chat.id,
            text="عضویت شما تایید شد! حالا لطفاً شماره تلفن خود را ارسال کنید:",
            reply_markup=keyboard
        )
    else:
        await callback.answer("❌ شما هنوز در کانال عضو نشده‌اید!", show_alert=True)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
                              
