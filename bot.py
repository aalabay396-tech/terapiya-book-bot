import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    ReplyKeyboardRemove,
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from dotenv import load_dotenv

# .env faylini yuklash
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
CARD_NUMBER = os.getenv("CARD_NUMBER", "4067 0700 0848 5596")
CARD_HOLDER = os.getenv("CARD_HOLDER", "Ruziyev Javlonbek")

# Kitob qismlari va narxlari
BOOKS = {
    "part_1": {
        "title": "Terapiya (1-qism)",
        "price": "140 000 so'm"
    },
    "part_2": {
        "title": "Terapiya (2-qism)",
        "price": "200 000 so'm"
    },
    "both": {
        "title": "Terapiya (1 va 2-qism birgalikda)",
        "price": "340 000 so'm"
    }
}

BOOK_DESCRIPTION = (
    "📚 <b>«Terapiya» kitobi</b>\n\n"
    "Ushbu kitob <b>5 ta bo'limdan</b> iborat bo'lib, har bir bo'limning normal anatomiyasi, "
    "gistologiyasi, fiziologiyasi va undan tashqari bo'limga aloqador shikoyatlari hamda tekshirish usullarini o'z ichiga oladi.\n\n"
    "👨‍⚕️ <i>Tibbiyotdagi barcha talabalar o'qib foydalanishi mumkin.</i>\n\n"
    "💰 <b>Narxlar:</b>\n"
    "• 1-qism: <b>140 000 so'm</b>\n"
    "• 2-qism: <b>200 000 so'm</b>\n"
    "• Ikkala qism birga: <b>340 000 so'm</b>"
)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# FSM (Holatlar ketma-ketligi)
class OrderState(StatesGroup):
    full_name = State()
    phone = State()
    address = State()
    waiting_receipt = State()

# 1. /start bosilganda
@dp.message(CommandStart())
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    
    text = (
        f"Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n\n"
        f"{BOOK_DESCRIPTION}\n\n"
        "Xarid qilish uchun o'zingizga kerakli qismni tanlang:"
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 1-qismni sotib olish (140 000 so'm)", callback_data="buy_part_1")],
        [InlineKeyboardButton(text="📖 2-qismni sotib olish (200 000 so'm)", callback_data="buy_part_2")],
        [InlineKeyboardButton(text="📚 Ikkala qismni birga olish (340 000 so'm)", callback_data="buy_both")]
    ])
    
    await message.answer(text, reply_markup=kb, parse_mode="HTML")

# 2. Kitob qismi tanlanganda -> Ism-familiya so'rash
@dp.callback_query(F.data.startswith("buy_"))
async def process_buy(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    book_key = callback.data.replace("buy_", "")
    selected_book = BOOKS.get(book_key)
    
    if not selected_book:
        return
        
    await state.update_data(
        book_title=selected_book["title"],
        book_price=selected_book["price"]
    )
    
    await callback.message.answer(
        f"Tanlandi: <b>{selected_book['title']}</b> ({selected_book['price']})\n\n"
        "Yetkazib berish uchun <b>Ism va Familiyangizni</b> kiriting:\n"
        "<i>(Masalan: Ali Valiyev)</i>",
        parse_mode="HTML"
    )
    await state.set_state(OrderState.full_name)

# 3. Ism qabul qilindi -> Telefon raqamni so'rash
@dp.message(OrderState.full_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    
    phone_btn = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        "Rahmat! Endi <b>telefon raqamingizni</b> yuboring (yoki pastdagi tugmani bosing):",
        reply_markup=phone_btn,
        parse_mode="HTML"
    )
    await state.set_state(OrderState.phone)

# 4. Telefon qabul qilindi -> Manzilni so'rash
@dp.message(OrderState.phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone_number = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone_number)
    
    await message.answer(
        "Yetkazib berish <b>manzilingizni</b> kiriting:\n"
        "<i>(Viloyat, tuman, ko'cha, uy/xonadon raqami)</i>",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )
    await state.set_state(OrderState.address)

# 5. Manzil qabul qilindi -> Karta va to'lov chekini so'rash
@dp.message(OrderState.address)
async def process_address(message: types.Message, state: FSMContext):
    await state.update_data(address=message.text)
    data = await state.get_data()
    
    text = (
        f"✅ <b>Buyurtma ma'lumotlari saqlandi!</b>\n\n"
        f"📚 <b>Tanlangan kitob:</b> {data['book_title']}\n"
        f"💵 <b>To'lov summasi:</b> <b>{data['book_price']}</b>\n\n"
        f"To'lov uchun karta ma'lumotlari:\n"
        f"💳 <b>Karta:</b> <code>{CARD_NUMBER}</code>\n"
        f"👤 <b>Karta egasi:</b> {CARD_HOLDER}\n\n"
        f"⚠️ <b>Iltimos, to'lovni amalga oshirib, to'lov chekining RASMINI (skrinshotini) shu yerga yuboring.</b>"
    )
    
    await message.answer(text, parse_mode="HTML")
    await state.set_state(OrderState.waiting_receipt)

# 6. Chek (rasm) qabul qilindi -> Adminga to'liq yuborish
@dp.message(OrderState.waiting_receipt, F.photo)
async def process_receipt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    
    admin_caption = (
        "🔥 <b>YANGI BUYURTMA VA TO'LOV CHEKI!</b>\n"
        "───────────────────────\n"
        f"📚 <b>Kitob:</b> {data['book_title']}\n"
        f"💵 <b>Summa:</b> {data['book_price']}\n"
        "───────────────────────\n"
        f"👤 <b>Mijoz:</b> {data['full_name']} ({username})\n"
        f"📞 <b>Telefon:</b> {data['phone']}\n"
        f"📍 <b>Manzil:</b> {data['address']}\n"
    )
    
    photo_id = message.photo[-1].file_id
    
    if ADMIN_ID != 0:
        try:
            await bot.send_photo(
                chat_id=ADMIN_ID,
                photo=photo_id,
                caption=admin_caption,
                parse_mode="HTML"
            )
        except Exception as e:
            logging.error(f"Adminga yuborishda xatolik yuz berdi: {e}")
    
    await message.answer(
        "🎉 <b>To'lov chekingiz qabul qilindi!</b>\n\n"
        "Buyurtmangiz tekshiriladi va tez orada kitobingiz yetkazib beriladi. Rahmat!",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML"
    )
    await state.clear()

# Agar rasm o'rniga matn yuborsa
@dp.message(OrderState.waiting_receipt)
async def wrong_receipt(message: types.Message):
    await message.answer("⚠️ Iltimos, to'lov chekini <b>rasm (skrinshot)</b> ko'rinishida yuboring!")

async def main():
    print("Bot muvaffaqiyatli ishga tushdi va xabarlarni kutmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
