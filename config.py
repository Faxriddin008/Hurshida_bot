# config.py

from aiogram.types import KeyboardButton

# --- BOT VA ADMIN SOZLAMALARI ---
# ⚠️ O'zgartirish shart:
BOT_TOKEN = "8263702293:AAENv-nqHruK8zeHRJ3lmXhuzpIPcbo_O"
ADMIN_CHAT_ID = 1266438824 # NAMUNA: Admin guruh/kanal ID'sini kiriting


# --- LOYIHA UCHUN O'ZGARMASLAR ---

REGIONS = [
    "Andijon", "Buxoro", "Farg'ona", "Jizzax", "Xorazm",
    "Namangan", "Navoiy", "Qashqadaryo", "Samarqand",
    "Sirdaryo", "Surxondaryo", "Toshkent vil.", "Toshkent shahar",
    "Андижан", "Бухара", "Фергана", "Джизак", "Хорезм",
    "Наманган", "Навои", "Кашкадарья", "Самарканд",
    "Сырдарья", "Сурхандарья", "Ташкентская обл.", "Ташкент"
]


# --- LOKALIZATSIYA LUG'ATI ---

TEXTS = {
    'uz': {
        'greeting': "Assalomu alaykum! Iltimos, tilni tanlang:",
        'ask_name': "Iltimos, ismingizni kiriting:",
        'ask_region': "Rahmat. Endi qaysi **viloyatdan** ekaningizni tanlang:",
        'ask_phone': "Endi telefon raqamingizni kiriting yoki pastdagi tugmani bosing:",
        'ask_question': "Savolingiz bo'lsa, iltimos uni **adminga qoldirishingiz mumkin:**",
        'confirm_data': "**YIG'ILGAN MA'LUMOTLARNI TEKSHIRING:**\n", # Endi ishlatilmaydi
        'confirm_instruction': "\n\nAgar ma'lumotlarda xatolik bo'lsa, tahrirlang. Aks holda **Tasdiqlash** tugmasini bosing.", # Endi ishlatilmaydi
        'stop_message': "Joriy jarayon (ma'lumot yig'ish) to'xtatildi. Agar boshlamoqchi bo'lsangiz, /start buyrug'ini bosing.",
        'submit_success': "Rahmat! Sizning savolingiz adminga muvaffaqiyatli yetkazildi. Tez orada javob kutib qoling.",
        'name_label': "👤 Ism:",
        'region_label': "🗺️ Viloyat:",
        'phone_label': "📞 Tel. raqam:",
        'question_label': "❓ Savol:",
        'submit_final': "✅ Tasdiqlash va Yuborish", # Endi ishlatilmaydi
        'phone_button': "📞 Telefon raqamimni yuborish",
        'incorrect_name': "Iltimos, ismingizni to'g'ri kiriting.",
        'incorrect_region': "Iltimos, faqat tugmalar orqali viloyatingizni tanlang:",
        'incorrect_phone': "Iltimos, telefon raqamini to'g'ri formatda kiriting.",
        'choose_lang': "Iltimos, tilni tugmalar orqali tanlang.",
    },
    'ru': {
        'greeting': "Здравствуйте! Пожалуйста, выберите язык:",
        'ask_name': "Пожалуйста, введите ваше имя:",
        'ask_region': "Спасибо. Теперь выберите, из какого вы **региона**:",
        'ask_phone': "Теперь введите свой номер телефона или нажмите кнопку ниже:",
        'ask_question': "Если у вас есть вопрос, пожалуйста, **вы можете оставить его администратору:**",
        'confirm_data': "**ПРОВЕРЬТЕ СОБРАННЫЕ ДАННЫЕ:**\n", # Endi ishlatilmaydi
        'confirm_instruction': "\n\nЕсли в данных есть ошибки, отредактируйте их. В противном случае нажмите **Подтвердить**.", # Endi ishlatilmaydi
        'stop_message': "Текущий процесс (сбор данных) остановлен. Нажмите /start, чтобы начать.",
        'submit_success': "Спасибо! Ваш вопрос успешно передан администратору. Ожидайте скорого ответа.",
        'name_label': "👤 Имя:",
        'region_label': "🗺️ Регион:",
        'phone_label': "📞 Тел. номер:",
        'question_label': "❓ Вопрос:",
        'submit_final': "✅ Подтвердить и отправить", # Endi ishlatilmaydi
        'phone_button': "📞 Отправить мой номер телефона",
        'incorrect_name': "Пожалуйста, введите ваше имя правильно.",
        'incorrect_region': "Пожалуйста, выберите регион только с помощью кнопок:",
        'incorrect_phone': "Пожалуйста, введите номер телефона в правильном формате.",
        'choose_lang': "Пожалуйста, выберите язык с помощью кнопок.",
    }
}
