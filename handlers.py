import aiohttp
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from keyboards import main_kb, premium_kb, admin_kb, admin_approve_kb, delete_user_kb, cancel_kb

router = Router()
API_URL = "http://127.0.0.1:8000"

# --- НАСТРОЙКИ ---
ADMIN_ID = 7807899601  # ЗАМЕНИ НА СВОЙ ID
CHANNEL_URL = "https://t.me/quazzzmu_channel"
CHANNEL_ID = "@quazzzmu_channel"
PRIVATE_CHAT_LINK = "https://t.me/quazzzmu_channel"

class AdminStates(StatesGroup):
    waiting_for_mail = State()

async def call_api(method, endpoint, data=None):
    async with aiohttp.ClientSession() as session:
        url = f"{API_URL}{endpoint}"
        try:
            if method == "POST":
                async with session.post(url, json=data) as r: return await r.json(), r.status
            elif method == "DELETE":
                async with session.delete(url) as r: return await r.json(), r.status
            else:
                async with session.get(url) as r: return await r.json(), r.status
        except: return None, 500

@router.message(Command("start"))
async def start(m: Message):
    username = m.from_user.username or "User"
    await call_api("POST", "/register", {"user_id": m.from_user.id, "username": username})
    
    if m.from_user.id == ADMIN_ID:
        return await m.answer("👑 Режим Администратора", reply_markup=admin_kb())

    data, _ = await call_api("GET", f"/check_status/{m.from_user.id}")
    kb = premium_kb() if data.get("status") == 2 else main_kb()
    await m.answer("Добро пожаловать!", reply_markup=kb)

# --- АДМИН ПАНЕЛЬ ---

@router.message(F.text == "👥 Список пользователей")
async def admin_list(m: Message):
    if m.from_user.id != ADMIN_ID: return
    users, _ = await call_api("GET", f"/users?admin_id={ADMIN_ID}")
    if not users: return await m.answer("В базе нет других пользователей.")
    
    for u in users:
        st = "Обычный" if u['status'] == 0 else "Ожидание" if u['status'] == 1 else "Premium"
        text = f"👤 @{u['username']} (<code>{u['user_id']}</code>)\nСтатус: {st}"
        await m.answer(text, parse_mode="HTML", reply_markup=delete_user_kb(u['user_id']))

@router.message(F.text == "📊 Статистика")
async def admin_stats(m: Message):
    if m.from_user.id != ADMIN_ID: return
    users, _ = await call_api("GET", "/users")
    await m.answer(f"📈 Всего пользователей в базе: {len(users)}")

# --- РАССЫЛКА ---

@router.message(F.text == "📢 С сделать рассылку") # Исправлено под твое меню
@router.message(F.text == "📢 Сделать рассылку")
async def mail_start(m: Message, state: FSMContext):
    if m.from_user.id != ADMIN_ID: return
    await state.set_state(AdminStates.waiting_for_mail)
    await m.answer("Пришлите текст для рассылки всем пользователям:", reply_markup=cancel_kb())

@router.message(AdminStates.waiting_for_mail, F.text == "❌ Отмена")
async def mail_cancel(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Рассылка отменена.", reply_markup=admin_kb())

@router.message(AdminStates.waiting_for_mail)
async def mail_run(m: Message, state: FSMContext, bot: Bot):
    await state.clear()
    users, _ = await call_api("GET", "/users")
    count = 0
    for u in users:
        try:
            if u['user_id'] != ADMIN_ID:
                await bot.send_message(u['user_id'], m.text)
                count += 1
        except: continue
    await m.answer(f"✅ Рассылка завершена. Получили: {count} чел.", reply_markup=admin_kb())

# --- ПОЛЬЗОВАТЕЛЬ ---

@router.message(F.text == "💎 Получить доступ")
async def buy(m: Message, bot: Bot):
    if m.from_user.id == ADMIN_ID: return await m.answer("Вы админ!")
    data, _ = await call_api("GET", f"/check_status/{m.from_user.id}")
    if data.get("status") != 0: return await m.answer("Заявка уже в работе или одобрена.")
    
    try:
        check = await bot.get_chat_member(CHANNEL_ID, m.from_user.id)
        if check.status == 'left': return await m.answer(f"Подпишитесь: {CHANNEL_URL}")
    except: return await m.answer("Ошибка доступа к каналу.")

    await call_api("POST", "/request_premium", {"user_id": m.from_user.id})
    await m.answer("Заявка отправлена!")
    await bot.send_message(ADMIN_ID, f"Запрос от {m.from_user.id}", reply_markup=admin_approve_kb(m.from_user.id))

@router.message(F.text == "⭐ Мой доступ (Канал)")
async def get_link(m: Message):
    data, _ = await call_api("GET", f"/check_status/{m.from_user.id}")
    if data.get("status") == 2 or m.from_user.id == ADMIN_ID:
        await m.answer(f"🌟 <b>ВАШ PREMIUM ДОСТУП</b>\n\n👉 <a href='{PRIVATE_CHAT_LINK}'>ВОЙТИ В ЗАКРЫТЫЙ КАНАЛ</a>", 
                       parse_mode="HTML", disable_web_page_preview=True)
    else:
        await m.answer("У вас нет доступа. Нажмите👉 /start чтобы получить доступ")

@router.message(F.text == "🔍 Статус подписки")
async def check_st(m: Message):
    data, _ = await call_api("GET", f"/check_status/{m.from_user.id}")  
    s = data.get("status", 0)
    txt = {0: "Нет доступа. Нажмите👉 /start чтобы получить доступ", 1: "Ожидание", 2: "Premium ✅"}
    await m.answer(txt.get(s))

# --- CALLBACKS ---

@router.callback_query(F.data.startswith("delete_"))
async def cb_del(call: CallbackQuery):
    uid = int(call.data.split("_")[1])
    await call_api("DELETE", f"/delete_user/{uid}")
    await call.message.edit_text(f"Юзер {uid} удален.")

@router.callback_query(F.data.startswith("approve_"))
async def cb_app(call: CallbackQuery, bot: Bot):
    uid = int(call.data.split("_")[1])
    await call_api("POST", "/approve_premium", {"user_id": uid})
    await call.message.edit_text("Одобрено.")
    await bot.send_message(uid, "Вам одобрили премиум! Жмите /start")

@router.callback_query(F.data.startswith("reject_"))
async def cb_rej(call: CallbackQuery):
    uid = int(call.data.split("_")[1])
    await call_api("POST", "/reject_premium", {"user_id": uid})
    await call.message.edit_text("Отклонено.")