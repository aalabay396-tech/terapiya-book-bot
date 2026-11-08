# Kitob Sotish Boti

Bu bot orqali mijozlar kitob haqida ma'lumot oladi, buyurtma berish uchun ism-familiyasi, telefon raqami va manzilini kiritadi hamda to'lov chekini yuboradi. Barcha ma'lumotlar va to'lov rasmi to'g'ridan-to'g'ri admin (sizning) Telegramingizga keladi.

## Fayllar:
- `bot.py` — Asosiy bot dasturi
- `.env` — Sozlamalar (Bot tokeni, Admin ID, karta raqami, kitob ma'lumotlari)
- `requirements.txt` — Kerakli kutubxonalar

## Ishga tushirish (Kompyuterda):
1. Kutubxonalarni o'rnatish:
   ```bash
   pip install -r requirements.txt
   ```
2. Botni yurgizish:
   ```bash
   python bot.py
   ```

## Kompyuter o'chganda ham ishlashi uchun (Render.com bepul hosting):
1. Loyihani GitHub-ga yuklang.
2. [Render.com](https://render.com) ga kiring va **New + -> Background Worker** tanlang.
3. Repozitoriyani ulab:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
4. **Environment Variables** bo'limida `.env` ichidagi o'zgaruvchilarni kiriting.
