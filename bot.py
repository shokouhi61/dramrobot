import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.filters import Command

# تنظیمات اصلی بات
TOKEN = "8826773951:AAHc1YlXMYCqz28GbnwpRXSfo0vgxIUrg"
CHANNEL_USERNAME = "@dram2ir"
ADMIN_CHAT_ID = 48460135
MINI_APP_URL = "https://shokouhi61.github.io/dramrobot/"

bot = Bot(token=TOKEN)
dp = Dispatcher()

users_db = {}

async def check_membership(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    is_member = await check_membership(user_id)
    
    if is_member:
        kb = ReplyKeyboardBuilder()
        kb.button(text="📱 اشتراک‌گذاری شماره تلفن", request_contact=True)
        kb.adjust(1)
        await message.answer(
            "حساب شما تایید شد! لطفاً شماره تلفن خود را ارسال کنید",
            reply_markup=kb.as_markup(resize_keyboard=True)
        )
    else:
        builder = InlineKeyboardBuilder()
        builder.button(text="📢 عضویت در کانال", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")
        builder.button(text="✅ عضو شدم، بررسی کن", callback_data="check_sub")
        builder.adjust(1)
        await message.answer(
            f"لطفاً ابتدا در کانال ما {CHANNEL_USERNAME} عضو شوید و سپس روی دکمه زیر بزنید.",
            reply_markup=builder.as_markup()
        )

@dp.message(F.contact)
async def handle_contact(message: types.Message):
    user_id = message.from_user.id
    phone = message.contact.phone_number
    users_db[user_id] = phone
    
    builder = InlineKeyboardBuilder()
    builder.button(text="🛒 ورود به مینی‌آپ بازار درام", web_app=types.WebAppInfo(url=MINI_APP_URL))
    builder.adjust(1)
    
    await message.answer(
        "ثبت‌نام شما با موفقیت انجام شد! اکنون می‌توانید از طریق دکمه زیر وارد مینی‌آپ شوید ✅",
        reply_markup=builder.as_markup()
    )

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
            "حساب شما تایید شد! لطفاً شماره تلفن خود را ارسال کنید",
            reply_markup=kb.as_markup(resize_keyboard=True)
        )
    else:
        await callback.answer("❌ هنوز در کانال عضو نشده‌اید!", show_alert=True)

# وب‌سرور برای پاسخ به پورت رندر و جلوگیری از خطای Timeout
async def handle(request):
    return web.Response(text="Bot is running!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await asyncio.gather(
        web_server(),
        dp.start_polling(bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
        
