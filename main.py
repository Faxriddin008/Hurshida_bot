# main.py

import asyncio
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from aiogram.client.default import DefaultBotProperties

# --- CONFIG FAYLDAN IMPORT (config.py faylida bo'lishi shart) ---
from config import BOT_TOKEN, ADMIN_CHAT_ID, REGIONS, TEXTS


# --- FSM HOLATLARI ---

class UserRegistration(StatesGroup):
    """Foydalanuvchidan ma'lumot yig'ish bosqichlari"""
    SELECT_LANGUAGE = State()
    ASK_NAME = State()
    ASK_PHONE = State()
    ASK_REGION = State()
    ASK_QUESTION = State()


class AdminChat(StatesGroup):
    """Adminning foydalanuvchi bilan aloqa qilish holati"""
    ACTIVE_CHAT = State()  # Admin mijoz bilan faol gaplashayotgan holat


# --- TUGMALAR FUNKSIYALARI ---

def get_language_keyboard() -> ReplyKeyboardMarkup:
    """Til tanlash tugmalarini hosil qiladi."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🇺🇿 O'zbekcha"),
                KeyboardButton(text="🇷🇺 Русский")
            ]
        ],
        resize_keyboard=True
    )


def get_regions_keyboard() -> ReplyKeyboardMarkup:
    """Viloyatlar tugmasini hosil qiladi."""
    regions_uz = [
        "Andijon", "Buxoro", "Farg'ona", "Jizzax", "Xorazm",
        "Namangan", "Navoiy", "Qashqadaryo", "Samarqand",
        "Sirdaryo", "Surxondaryo", "Toshkent vil.", "Toshkent shahar"
    ]

    keyboard = []
    for i in range(0, len(regions_uz), 2):
        row = [KeyboardButton(text=regions_uz[i])]
        if i + 1 < len(regions_uz):
            row.append(KeyboardButton(text=regions_uz[i + 1]))
        keyboard.append(row)
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_phone_keyboard(lang: str) -> ReplyKeyboardMarkup:
    """Telefon raqami yuborish tugmasini hosil qiladi."""
    texts = TEXTS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts['phone_button'], request_contact=True)]
        ],
        resize_keyboard=True
    )


def get_admin_action_keyboard(user_id: int, message_id: int, is_new_message: bool = False) -> InlineKeyboardMarkup:
    """Admin uchun 'Mijoz bilan bog'lanish', 'Bajarildi/Bajarilmadi' tugmalarini hosil qiladi."""

    chat_button_text = "💬 Chatni boshlash" if is_new_message else "💬 Mijoz bilan bog'lanish"

    keyboard = [
        [
            InlineKeyboardButton(
                text=chat_button_text,
                callback_data=f"status:chat:{user_id}:{message_id}"
            )
        ]
    ]

    # Faqat ma'lumot yig'ish xabari uchun status tugmalari qo'shiladi
    if not is_new_message:
        keyboard.append([
            InlineKeyboardButton(
                text="✅ Bajarildi",
                callback_data=f"status:done:{user_id}:{message_id}"
            ),
            InlineKeyboardButton(
                text="❌ Bajarilmadi",
                callback_data=f"status:not_done:{user_id}:{message_id}"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_admin_end_chat_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Admin uchun 'Chatni yakunlash' tugmasini hosil qiladi."""
    keyboard = [
        [
            InlineKeyboardButton(
                text="🛑 Chatni yakunlash",
                callback_data=f"admin_chat:end:{user_id}"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# --- ADMIN MENU HANDLERS ---

async def cmd_chat_end_menu(message: types.Message, state: FSMContext):
    """/endchat buyrug'i: Faol chatni yakunlash tugmasini chiqaradi (menyudan foydalanish uchun)."""
    if message.chat.id != ADMIN_CHAT_ID:
        return

    current_state = await state.get_state()
    if current_state != AdminChat.ACTIVE_CHAT.state:
        await message.answer("Faol chat mavjud emas.")
        return

    data = await state.get_data()
    user_id = data.get('target_user_id')

    await message.answer(
        f"Mijoz ({user_id}) bilan faol chat mavjud.\nChatni yakunlashni tasdiqlaysizmi?",
        reply_markup=get_admin_end_chat_keyboard(user_id),
    )


# --- XABAR QABUL QILUVCHILAR (HANDLERS) ---


async def cmd_start(message: types.Message, state: FSMContext):
    """/start buyrug'i: Til tanlashni boshlaydi."""
    await state.clear()
    await state.set_state(UserRegistration.SELECT_LANGUAGE)

    await message.answer(
        TEXTS['uz']['greeting'],
        reply_markup=get_language_keyboard()
    )


async def cmd_restart(message: types.Message, state: FSMContext):
    """/restart buyrug'i: Jarayonni qayta boshlaydi (til tanlashdan)."""
    await cmd_start(message, state)


async def cmd_stop(message: types.Message, state: FSMContext):
    """/stop buyrug'i: Joriy jarayonni to'xtatadi."""
    user_data = await state.get_data()
    lang = user_data.get('lang', 'uz')
    texts = TEXTS[lang]

    await state.clear()

    await message.answer(
        texts['stop_message'],
        reply_markup=ReplyKeyboardRemove()
    )


async def process_language(message: types.Message, state: FSMContext):
    """1. Tilni tanlash va Ismni so'rashga o'tish."""
    if message.text == "🇺🇿 O'zbekcha":
        lang = 'uz'
    elif message.text == "🇷🇺 Русский":
        lang = 'ru'
    else:
        await message.answer(TEXTS['uz']['choose_lang'], reply_markup=get_language_keyboard())
        return

    await state.update_data(lang=lang)
    texts = TEXTS[lang]

    await state.set_state(UserRegistration.ASK_NAME)

    await message.answer(
        texts['ask_name'],
        reply_markup=ReplyKeyboardRemove()
    )


async def process_name(message: types.Message, state: FSMContext):
    """2. Ismni qabul qilish va Telefon raqamini so'rash."""
    user_data = await state.get_data()
    lang = user_data.get('lang', 'uz')
    texts = TEXTS[lang]

    if len(message.text) < 2 or len(message.text) > 50:
        await message.answer(texts['incorrect_name'], reply_markup=ReplyKeyboardRemove())
        return

    await state.update_data(name=message.text)

    await state.set_state(UserRegistration.ASK_PHONE)

    await message.answer(
        texts['ask_phone'],
        reply_markup=get_phone_keyboard(lang)
    )


async def process_phone(message: types.Message, state: FSMContext):
    """3. Telefon raqamini qabul qilish va Viloyatni so'rash."""
    user_data = await state.get_data()
    lang = user_data.get('lang', 'uz')
    texts = TEXTS[lang]

    phone_number = None

    if message.contact:
        phone_number = message.contact.phone_number
    elif message.text and message.text.replace(" ", "").isdigit() and len(message.text.replace(" ", "")) >= 9:
        phone_number = message.text

    if phone_number is None:
        await message.answer(texts['incorrect_phone'], reply_markup=get_phone_keyboard(lang))
        return

    await state.update_data(phone=phone_number)

    await state.set_state(UserRegistration.ASK_REGION)

    await message.answer(
        texts['ask_region'],
        reply_markup=get_regions_keyboard()
    )


async def process_region(message: types.Message, state: FSMContext):
    """4. Viloyatni qabul qilish va Savolni so'rash."""
    user_data = await state.get_data()
    lang = user_data.get('lang', 'uz')
    texts = TEXTS[lang]

    selected_region = message.text

    if selected_region not in REGIONS:
        await message.answer(
            texts['incorrect_region'],
            reply_markup=get_regions_keyboard()
        )
        return

    await state.update_data(region=selected_region)

    await state.set_state(UserRegistration.ASK_QUESTION)

    await message.answer(
        texts['ask_question'],
        reply_markup=ReplyKeyboardRemove()
    )


async def process_question(message: types.Message, state: FSMContext, bot: Bot):
    """5. Savolni qabul qilish, Adminga to'g'ridan-to'g'ri yuborish va yakunlash."""

    # 1. Savolni saqlash
    await state.update_data(question=message.text)
    user_data = await state.get_data()
    lang = user_data.get('lang', 'uz')
    texts = TEXTS[lang]
    user_id = message.from_user.id

    # 2. Adminga yuborish uchun hisobot tayyorlash
    report = (
        f"**📩 YANGI SAVOL KELDI**\n"
        f"---------------------------\n"
        f"👤 **Foydalanuvchi:** {user_data.get('name')}\n"
        f"📞 **Tel. raqam:** `{user_data.get('phone')}`\n"
        f"🗺️ **Viloyat:** {user_data.get('region')}\n"
        f"**ID:** `{user_id}`\n"
        f"**Til:** `{lang.upper()}`\n"
        f"---------------------------\n"
        f"❓ **SAVOL:**\n{user_data.get('question')}"
    )

    try:
        # 3. Adminga xabarni yuborish
        sent_message = await bot.send_message(
            ADMIN_CHAT_ID,
            report,
            parse_mode='Markdown'
        )

        # 4. Admin xabariga aloqa tugmalarini qo'shish (status tugmalari bilan)
        admin_keyboard = get_admin_action_keyboard(
            user_id=user_id,
            message_id=sent_message.message_id,
            is_new_message=False
        )
        await bot.edit_message_reply_markup(
            chat_id=ADMIN_CHAT_ID,
            message_id=sent_message.message_id,
            reply_markup=admin_keyboard
        )

        # 5. Mijozga muvaffaqiyat xabari yuborish
        await message.answer(texts['submit_success'], reply_markup=ReplyKeyboardRemove())

    except Exception as e:
        await message.answer("Kechirasiz, ma'lumotni yuborishda xatolik yuz berdi.", reply_markup=ReplyKeyboardRemove())
        print(f"Adminga yuborishda xato: {e}")

    # 6. Jarayonni yakunlash
    await state.clear()


# --- ADMIN CHAT MANTIQI ---

async def start_admin_chat(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Adminning 'Mijoz bilan bog'lanish/Chatni boshlash' tugmasini bosganda ishlaydi."""

    parts = callback_query.data.split(':')
    user_id = int(parts[2])
    admin_message_id = int(parts[3])

    # Agar chat allaqachon faol bo'lsa, xato bermaslik uchun tekshirish
    current_state = await state.get_state()
    if current_state == AdminChat.ACTIVE_CHAT.state:
        # Agar admin faqat bitta mijoz bilan gaplashishga mo'ljallangan bo'lsa, bu yerda qaytariladi.
        # Biz bitta FSM holatidan foydalanyapmiz, shuning uchun faqat bitta faol chat bo'lishi mumkin.
        await callback_query.answer("Chat allaqachon faol. Yakunlangan bo'lsa, /endchat yuboring.", show_alert=True)
        return

    # 1. Admin holatini yangilash
    await state.set_state(AdminChat.ACTIVE_CHAT)
    await state.update_data(target_user_id=user_id, admin_start_message_id=admin_message_id)

    # 2. Admin xabarini yangilash (Chat tugmasini o'chirib, yakunlash tugmasini qo'shish)
    try:
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=admin_message_id,
            text=f"***[Chat boshlandi. Mijoz: {user_id}]***"
                 f"---------------------------\n"
                 f"➡️ **CHAT BOSHLANDI:** Bu suhbat to'g'ridan-to'g'ri mijoz ({user_id}) uchun! "
                 f"Yuboriladigan har bir xabar mijozga yetkaziladi. Tugatish uchun pastdagi tugmani yoki /endchat buyrug'ini bosing.",
            reply_markup=get_admin_end_chat_keyboard(user_id),
            parse_mode='Markdown'
        )
    except Exception as e:
        print(f"Chat boshlanganda xabarni o'zgartirishda xato: {e}")

    # 3. Mijozga aloqa boshlanganini xabar berish
    try:
        await bot.send_message(
            chat_id=user_id,
            text="🤝 **Admin siz bilan aloqaga chiqdi!** Endi to'g'ridan-to'g'ri yozishingiz mumkin."
        )
    except Exception as e:
        await callback_query.message.answer(f"Mijozga xabar yuborilmadi (bloklagan bo'lishi mumkin): {e}")

    await callback_query.answer("Chat boshlandi.")


async def forward_admin_message_to_user(message: types.Message, state: FSMContext, bot: Bot):
    """AdminChat.ACTIVE_CHAT holatidagi xabarlarni mijozga yuborish (Anonim tarzda)."""

    data = await state.get_data()
    target_user_id = data.get('target_user_id')

    if target_user_id is None:
        await message.answer("Xatolik: Aloqa maqsadini topa olmadim.")
        await state.clear()
        return

    try:
        # Anonim yuborish uchun copy_message yoki text+prefix ishlatiladi
        caption_text = f"**👨‍💼 Admin:** {message.caption}" if message.caption else None

        # Agar bu faqat matnli xabar bo'lsa
        if message.text:
            text_to_send = f"**👨‍💼 Admin:** {message.text}"
            await bot.send_message(
                chat_id=target_user_id,
                text=text_to_send,
                parse_mode='Markdown'
            )
        # Agar bu media (rasm/hujjat/video) bo'lsa
        else:
            await bot.copy_message(
                chat_id=target_user_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
                caption=caption_text,
                parse_mode='Markdown'
            )

        await message.reply("Mijozga yuborildi.")

    except Exception as e:
        await message.answer(f"Mijozga xabar yuborishda xato: {e}")


async def forward_user_message_to_admin(message: types.Message, state: FSMContext, bot: Bot):
    """Mijoz yozgan xabarni adminga yuborish. Faol chat bo'lmasa, 'Chatni boshlash' tugmasi qo'shiladi."""

    # Faqat mijozlar uchun
    if message.chat.id == ADMIN_CHAT_ID:
        return

    user_id = message.from_user.id

    # 1. Adminning hozirgi holatini va ma'lumotlarini tekshirish
    admin_state = await state.get_state()
    admin_data = await state.get_data()

    is_active_chat_with_this_user = (
            admin_state == AdminChat.ACTIVE_CHAT.state and
            admin_data.get('target_user_id') == user_id
    )

    # Agar chat allaqachon faol bo'lsa, hech qanday tugma qo'shmaymiz, shunchaki xabar yuboramiz.
    reply_markup = None
    user_info = f"**👤 Mijoz Xabari:** {message.from_user.full_name} (`{user_id}`)"

    if not is_active_chat_with_this_user:
        # 2. Xabarni adminga forward qilish
        try:
            forwarded_msg = await bot.forward_message(
                chat_id=ADMIN_CHAT_ID,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
        except Exception as e:
            print(f"Mijoz xabarini forward qilishda xato: {e}")
            return  # Xato bo'lsa, davom etmaymiz

        user_info = f"**🔥 YANGI MUROJAAT/XABAR:** {message.from_user.full_name} (`{user_id}`)"

        # 'Chatni boshlash' tugmasini yaratish
        reply_markup = get_admin_action_keyboard(
            user_id=user_id,
            message_id=forwarded_msg.message_id,
            is_new_message=True
        )
        reply_to_message_id = forwarded_msg.message_id  # forward qilingan xabarga reply
    else:
        # Faqat xabarni forward qilamiz (tugmasiz)
        try:
            forwarded_msg = await bot.forward_message(
                chat_id=ADMIN_CHAT_ID,
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
            reply_to_message_id = forwarded_msg.message_id
            user_info = f"**💬 {message.from_user.full_name} dan yangi xabar** (Faol chat)"
        except Exception as e:
            print(f"Faol chat xabarini forward qilishda xato: {e}")
            return

    # 3. Adminga xabarni yuborish
    try:
        await bot.send_message(
            ADMIN_CHAT_ID,
            user_info,
            reply_to_message_id=reply_to_message_id,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    except Exception as e:
        print(f"Mijoz xabarini adminga yuborishda xato: {e}")
        if "bot was blocked by the user" in str(e):
            await message.answer("Kechirasiz, admin hozircha sizga javob bera olmaydi.")


async def end_admin_chat(callback_query: types.CallbackQuery, state: FSMContext, bot: Bot):
    """Adminning 'Chatni yakunlash' tugmasini bosganda ishlaydi."""

    current_state = await state.get_state()
    if current_state != AdminChat.ACTIVE_CHAT.state:
        await callback_query.answer("Chat allaqachon yakunlangan.", show_alert=True)
        return

    data = await state.get_data()
    user_id = data.get('target_user_id')

    # 1. Admin holatini yakunlash
    await state.clear()

    # 2. Admin xabarini yakunlash
    try:
        # Callback kelgan xabarni o'zgartirish (agar bu chatni boshlash xabari bo'lsa)
        await callback_query.message.edit_text(
            f"🛑 **CHAT YAKUNLANDI.** Mijoz: {user_id}",
            reply_markup=None,
            parse_mode='Markdown'
        )
    except Exception:
        pass  # Agar xabar /endchat buyrug'idan kelgan bo'lsa, o'zgartira olmaydi

    # 3. Mijozga xabar berish
    try:
        await bot.send_message(
            chat_id=user_id,
            text="👋 **Aloqa yakunlandi.** Savollaringiz bo'lsa, /start buyrug'ini bosing."
        )
    except Exception as e:
        print(f"Mijozga yakuniy xabar yuborilmadi: {e}")

    await callback_query.answer("Chat yakunlandi.")


# ADMINNING HOLATINI BOSHQARISH (Status)

async def process_admin_action(callback_query: types.CallbackQuery, bot: Bot):
    """Adminning status (Bajarildi/Bajarilmadi) tugmasini qabul qilish."""
    if callback_query.message.chat.id != ADMIN_CHAT_ID:
        await callback_query.answer("Kechirasiz, bu buyruq faqat admin guruhida ishlaydi.", show_alert=True)
        return

    if callback_query.data.startswith("status:chat:"):
        await callback_query.answer()
        return

    try:
        parts = callback_query.data.split(':')
        action = parts[1]
        admin_message_id = int(parts[3])

    except (IndexError, ValueError):
        await callback_query.answer("Ma'lumot noto'g'ri shaklda keldi.", show_alert=True)
        return

    status_text_uz = "✅ Bajarildi" if action == "done" else "❌ Bajarilmadi"

    try:
        # Xabarga statusni qo'shish (Mijozga yuborilmaydi)
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=admin_message_id,
            text=f"{callback_query.message.text.split('--------------')[0]}\n"
                 f"---------------------------\n"
                 f"**Holati:** {status_text_uz} (Admin: {callback_query.from_user.full_name})",
            reply_markup=None,
            parse_mode='Markdown'
        )

        await callback_query.answer(f"Holat muvaffaqiyatli o'zgartirildi: {status_text_uz}")

    except Exception as e:
        await callback_query.answer("Xabarni yangilashda xatolik yuz berdi.", show_alert=True)
        print(f"Callback xatosi: {e}")


# ADMINNING REPLY MANTIQI (Chat faol bo'lmasa)

async def process_admin_reply(message: types.Message, bot: Bot, state: FSMContext):
    """Adminning javobini qabul qilish (Reply bo'lsa)."""

    current_state = await state.get_state()
    if current_state == AdminChat.ACTIVE_CHAT.state:
        return

    admin_reply_text = message.text
    replied_message = message.reply_to_message

    if replied_message is None:
        return

    # Reply qilingan xabar ichidan foydalanuvchi ID'sini topish
    id_match = re.search(r"ID:\s*`(\d+)`", replied_message.text or replied_message.caption or "")
    if not id_match:
        id_match = re.search(r"\( `(\d+)` \)", replied_message.text or replied_message.caption or "")

    if not id_match:
        await message.answer("Foydalanuvchi ID'si topilmadi. Faqat mijozning xabarlariga javob bering.")
        return

    target_user_id = int(id_match.group(1))

    try:
        reply_message_for_user = (
            f"**📩 Admin Javobi:**\n"
            f"----------------------\n"
            f"{admin_reply_text}"
        )

        await bot.send_message(
            chat_id=target_user_id,
            text=reply_message_for_user,
            parse_mode='Markdown'
        )

        await message.reply(
            f"Javob muvaffaqiyatli tarzda foydalanuvchiga (`{target_user_id}`) yuborildi."
        )

    except Exception as e:
        await message.answer(f"Javobni foydalanuvchiga yuborishda xato yuz berdi. Ehtimol, u botni bloklagan: {e}")


# --- BOTNI ISHGA TUSHIRISH ---

async def main():
    default_properties = DefaultBotProperties(parse_mode="HTML")
    bot = Bot(token=BOT_TOKEN, default=default_properties)
    dp = Dispatcher()

    # --- Mijoz tomonidan kiruvchi xabarlar ---

    # FSM Mantiqi
    dp.message.register(cmd_start, CommandStart())
    dp.message.register(cmd_restart, Command('restart'))
    dp.message.register(cmd_stop, Command('stop'))
    dp.message.register(process_language, UserRegistration.SELECT_LANGUAGE, F.text)
    dp.message.register(process_name, UserRegistration.ASK_NAME, F.text)
    dp.message.register(process_phone, UserRegistration.ASK_PHONE, F.text | F.contact)
    dp.message.register(process_region, UserRegistration.ASK_REGION, F.text)
    dp.message.register(process_question, UserRegistration.ASK_QUESTION, F.text)

    # Mijozning barcha xabarlari (ma'lumot yig'ish jarayonidan tashqari) adminga forward bo'ladi
    dp.message.register(forward_user_message_to_admin, F.chat.id != ADMIN_CHAT_ID)

    # --- Admin tomonidan kiruvchi xabarlar (Faqat ADMIN_CHAT_ID uchun) ---

    # Admin Menu
    dp.message.register(cmd_chat_end_menu, Command('endchat'), F.chat.id == ADMIN_CHAT_ID)

    # Admin Chat Callback Handlers
    dp.callback_query.register(start_admin_chat, F.data.startswith("status:chat:"))
    dp.callback_query.register(end_admin_chat, F.data.startswith("admin_chat:end:"))
    dp.callback_query.register(process_admin_action, F.data.startswith("status:"))

    # Admin Chat faol bo'lsa, xabarni to'g'ridan-to'g'ri mijozga yuborish
    dp.message.register(
        forward_admin_message_to_user,
        AdminChat.ACTIVE_CHAT,
        F.chat.id == ADMIN_CHAT_ID
    )
    # Admin Chat faol bo'lmasa, REPLY mantiqini ishlatish
    dp.message.register(
        process_admin_reply,
        F.reply_to_message.is_not(None),
        F.chat.id == ADMIN_CHAT_ID
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi")