import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.filters import Command

# --- تنظیمات امنیتی و اختصاصی شما ---
TOKEN = "8826773951:AAHc1YlXzMYCqz28GbnwpRXSfOOvgxIUrg8"
CHANNEL_USERNAME = "@dram2ir"
ADMIN_CHAT_ID = 48460135

bot = Bot(token=TOKEN)
dp = Dispatcher()

# حافظه موقت برای ذخیره شماره تلفن‌ها
users_db = {}

# بررسی عضویت کانال
async def check_membership(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ["member", "creator", "administrator"]:
            return True
    except Exception as e:
        print(f"Error checking membership: {e}")
    return False

# دستور استارت
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    
    # ۱. بررسی عضویت در کانال
    is_member = await check_membership(user_id)
    if not is_member:
        builder = InlineKeyboardBuilder()
        builder.button(text="📢 عضویت در کانال", url=f"https://t.me/dram2ir")
        builder.button(text="✅ عضو شدم، بررسی مجدد", callback_data="check_sub")
        builder.adjust(1)
        
        await message.answer(
            "⚠️ برای استفاده از بازار درام، لطفاً ابتدا در کانال ما عضو شوید:",
            reply_markup=builder.as_markup()
        )
        return

    # ۲. بررسی دریافت شماره تلفن
    if user_id not in users_db:
        kb = ReplyKeyboardBuilder()
        kb.button(text="📱 اشتراک‌گذاری شماره تلفن", request_contact=True)
        kb.adjust(1)
        
        await message.answer(
            "خوش آمدید! برای ادامه و تایید هویت، لطفاً شماره تلفن خود را ارسال کنید:",
            reply_markup=kb.as_markup(resize_keyboard=True, one_time_keyboard=True)
        )
    else:
        await message.answer("شما قبلاً ثبت‌نام کرده‌اید. از طریق دکمه زیر می‌توانید وارد مینی‌اپ شوید.")

# دریافت شماره تلفن کاربر
@dp.message(F.contact)
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
    
    await message.answer(
        "✅ شماره تلفن شما با موفقیت ثبت شد!",
        reply_markup=types.ReplyKeyboardRemove()
    )
    
    # ارسال گزارش لیستی به ادمین
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
    
    await message.answer("اکنون می‌توانید از امکانات بازار درام استفاده کنید.")

# دکمه بررسی مجدد عضویت
@dp.callback_query(F.data == "check_sub")
async def callback_check_sub(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    is_member = await check_membership(user_id)
    
    if is_member:
        await callback.message.delete()
        kb = ReplyKeyboardBuilder()
        kb.button(text="📱 اشتراک‌گذاری شماره تلفن", request_contact=True)
        kb.adjust(1)
        await callback.message.answer(
            "عضویت شما تایید شد! حالا لطفاً شماره تلفن خود را ارسال کنید:",
            reply_markup=kb.as_markup(resize_keyboard=True, one_time_keyboard=True)
        )
    else:
        await callback.answer("❌ شما هنوز در کانال عضو نشده‌اید!", show_alert=True)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
  
