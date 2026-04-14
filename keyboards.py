from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="💎 Получить доступ")],
        [KeyboardButton(text="🔍 Статус подписки")]
    ], resize_keyboard=True)

def premium_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="⭐ Мой доступ (Канал)")],
        [KeyboardButton(text="🔍 Статус подписки")]
    ], resize_keyboard=True)

def admin_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="👥 Список пользователей")],
        [KeyboardButton(text="📢 Сделать рассылку")],
        [KeyboardButton(text="📊 Статистика")]
    ], resize_keyboard=True)

def cancel_kb():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="❌ Отмена")]
    ], resize_keyboard=True)

def delete_user_kb(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Удалить из базы", callback_data=f"delete_{user_id}")]
    ])

def admin_approve_kb(user_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{user_id}")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{user_id}")]
    ])