import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
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

# .env yuklash
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "9249605244:AAGsAkKFCJSZZGLB_glTV8Sq5tjMP8iZHeQ")
ADMIN_ID = int(os.getenv("ADMIN_ID", "5337661007"))
CARD_NUMBER = os.getenv("CARD_NUMBER", "4067 0700 0848 5596")
CARD_HOLDER = os.getenv("CARD_HOLDER", "Ruziyev Javlonbek")
ADMIN_USERNAME = "@Astrummed_manager"  # Kitob egasining telegram username'i

# Kitob qismlari
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
        "title": "Terapiya (1 va 2-qism birga)",
        "price": "340 000 so'm"
    }
}

# Doimiy pastda turadigan asosiy menyu tugmalari
def get_main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Kitob haqida ma'lumot"), KeyboardButton(text="🛍️ Kitob sotib olish")],
            [KeyboardButton(text="💳 To'lov ma'lumotlari"), KeyboardButton(text="✍️ Savol berish (Muallifga yozish)")],
            [KeyboardButton(text="🔄 Asosiy menyu (Start)")]
        ],
        resize_keyboard=True
    )

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class OrderState(StatesGroup):
    full_name = State()
    phone = State()
    address = State()
    waiting_receipt = State()

class QuestionState(StatesGroup):
    waiting_question = State()

# /start yoki "Asosiy menyu" bosilganda
@dp.message(CommandStart())
@dp.message(F.text == "🔄 Asosiy menyu (Start)")
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    
    text = (
        f"Assalomu alaykum, <b>{message.from_user.full_name}</b>!\n\n"
        "«Terapiya» kitobining rasmiy savdo botiga xush kelibsiz.\n\n"
        "Kerakli bo'limni tanlash uchun pastdagi menyu tugmalaridan foydalaning:"
    )
    
    await message.answer(text, reply_markup=get_main_menu(), parse_mode="HTML")

# 1-Bo'lim: Kitob haqida ma'lumot
@dp.message(F.text == "📚 Kitob haqida ma'lumot")
async def book_info(message: types.Message):
    info_text = (
        "📚 <b>«Terapiya» kitobi haqida:</b>\n\n"
        "Kitob <b>5 ta asosiy bo'limdan</b> iborat:\n"
        "1️⃣ Normal anatomiya\n"
        "2️⃣ Gistologiya\n"
        "3️⃣ Fiziologiya\n"
        "4️⃣ Har bir bo'limga oid asosiy shikoyatlar\n"
        "5️⃣ Zamonaviy tekshirish va tashxislash usullari\n\n"
        "👨‍⚕️ <i>Tibbiyot oliygohlari, kollej talabalari hamda amaliyotchi shifokorlar uchun maxsus qo'llanma.</i>\n\n"
        "💰 <b>Narxlar:</b>\n"
        "• 1-qism: <b>140 000 so'm</b>\n"
        "• 2-qism: <b>200 000 so'm</b>\n"
        "• 1 va 2-qism birgalikda: <b>340 000 so'm</b>"
    )
    
    buy_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍️ Xarid qilish", callback_data="open_buy_menu")]
    ])
    
    await message.answer(info_text, reply_markup=buy_kb, parse_mode="HTML")

# 2-Bo'lim: Kitob sotib olish
@dp.message(F.text == "🛍️ Kitob sotib olish")
@dp.callback_query(F.data == "open_buy_menu")
async def buy_menu(event: types.Message | types.CallbackQuery, state: FSMContext):
    await state.clear()
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 1-qismni olish (140 000 so'm)", callback_data="buy_part_1")],
        [InlineKeyboardButton(text="📖 2-qismni olish (200 000 so'm)", callback_data="buy_part_2")],
        [InlineKeyboardButton(text="📚 1 va 2-qismni birga olish (340 000 so'm)", callback_data="buy_both")]
    ])
    
    text = "O'zingizga kerakli qismni tanlang:"
    if isinstance(event, types.CallbackQuery):
        await event.answer()
        await event.message.answer(text, reply_markup=kb)
    else:
        await event.answer(text, reply_markup=kb)

# 3-Bo'lim: To'lov ma'lumotlari
@dp.message(F.text == "💳 To'lov ma'lumotlari")
async def payment_info(message: types.Message):
    text = (
        "💳 <b>To'lov rekvizitlari:</b>\n\n"
        f"Karta raqami: <code>{CARD_NUMBER}</code>\n"
        f"Karta egasi: <b>{CARD_HOLDER}</b>\n\n"
        "<i>To'lovni amalga oshirgach, chekni «Kitob sotib olish» bo'limi orqali yuborishingiz mumkin.</i>"
    )
    await message.answer(text, parse_mode="HTML")

# 4-Bo'lim: Savol berish / Kitob egasiga yozish
@dp.message(F.text == "✍️ Savol berish (Muallifga yozish)")
async def ask_question(message: types.Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Muallif profiliga o'tish", url=f"https://t.me/Astrummed_manager")]
    ])
    
    await message.answer(
        "Savollaringiz bo'lsa, to'g'ridan-to'g'ri kitob egasiga yozishingiz mumkin:\n"
        f"👤 <b>Muallif:</b> {ADMIN_USERNAME}\n\n"
        "Yoki savolingizni shu yerga xabar qilib yozib qoldiring, bot uni muallifga yetkazadi:",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await state.set_state(QuestionState.waiting_question)

# Foydalanuvchi bot orqali savol yozganda -> Adminga boradi
@dp.message(QuestionState.waiting_question)
async def forward_question_to_admin(message: types.Message, state: FSMContext):
    user_tag = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    
    admin_msg = (
        "❓ <b>MIJOZDAN YANGI SAVOL:</b>\n"
        "───────────────────────\n"
        f"👤 <b>Mijoz:</b> {message.from_user.full_name} ({user_tag})\n"
        f"💬 <b>Savol:</b> {message.text}\n"
    )
    
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=admin_msg, parse_mode="HTML")
        await message.answer("✅ Savolingiz muallifga yetkazildi! Tez orada siz bilan bog'lanishadi.", reply_markup=get_main_menu())
    except Exception as e:
        await message.answer(f"Savolingizni to'g'ridan-to'g'ri {ADMIN_USERNAME} profiliga yozishingiz mumkin.")
    
    await state.clear()

# Sotib olish jarayoni (FSM)
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

@dp.message(OrderState.full_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    
    phone_btn = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    
    await message.answer(
        "Rahmat! Endi <b>telefon raqamingizni</b> yozing yoki tugmani bosing:",
        reply_markup=phone_btn,
        parse_mode="HTML"
    )
    await state.set_state(OrderState.phone)

@dp.message(OrderState.phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone_number = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone_number)
    
    await message.answer(
        "Yetkazib berish <b>manzilingizni</b> yozing:\n"
        "<i>(Viloyat, tuman, ko'cha, uy/xonadon raqami)</i>",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
    await state.set_state(OrderState.address)

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
    
    await message.answer(text, reply_markup=get_main_menu(), parse_mode="HTML")
    await state.set_state(OrderState.waiting_receipt)

@dp.message(OrderState.waiting_receipt, F.photo)
async def process_receipt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    
    admin_caption = (
        "🔥 <b>YANGI BUYURTMA VA TO'LOV CHEKI!</b>\n"
        "───────────────────────\n"
        f"📚 <b>Kitob:</b> {data.get('book_title')}\n"
        f"💵 <b>Summa:</b> {data.get('book_price')}\n"
        "───────────────────────\n"
        f"👤 <b>Mijoz:</b> {data.get('full_name')} ({username})\n"
        f"📞 <b>Telefon:</b> {data.get('phone')}\n"
        f"📍 <b>Manzil:</b> {data.get('address')}\n"
    )
    
    photo_id = message.photo[-1].file_id
    
    try:
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_id,
            caption=admin_caption,
            parse_mode="HTML"
        )
    except Exception as e:
        logging.error(f"Adminga yuborishda xatolik: {e}")
    
    await message.answer(
        "🎉 <b>To'lov chekingiz qabul qilindi!</b>\n\n"
        "Buyurtmangiz tekshiriladi va kitobingiz yetkazib beriladi. Rahmat!",
        reply_markup=get_main_menu(),
        parse_mode="HTML"
    )
    await state.clear()

async def main():
    print("Bot yangilandi va ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
