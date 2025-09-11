import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Путь к файлу данных
DATA_FILE = "data.json"

# Загрузка данных
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Сохранение данных
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Состояния FSM
class Form(StatesGroup):
    choosing_status = State()
    entering_start_date = State()
    entering_end_date = State()

# Главное меню
def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Добавить статус"))
    builder.add(KeyboardButton(text="График на неделю"))
    builder.add(KeyboardButton(text="График на месяц"))
    builder.add(KeyboardButton(text="Очистить чат"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

# Клавиатура статусов
def get_status_keyboard():
    statuses = ["Отпуск", "В офисе", "На объекте", "Командировка"]
    builder = ReplyKeyboardBuilder()
    for status in statuses:
        builder.add(KeyboardButton(text=status))
    builder.button(text="Назад")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

# Парсинг даты
def parse_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), "%d.%m.%Y").date()
    except ValueError:
        return None

# Генерация графика
def generate_schedule_report(days=7):
    data = load_data()
    today = datetime.today().date()
    end_date = today + timedelta(days=days-1)

    report = f"📅 График на {'неделю' if days == 7 else 'месяц'} ({today.strftime('%d.%m')} - {end_date.strftime('%d.%m.%Y')}):\n\n"

    if not data:
        return "Нет данных о статусах сотрудников."

    # Собираем все даты в диапазоне
    date_list = [today + timedelta(days=i) for i in range(days)]

    # Для каждого пользователя
    for user_id, user_data in data.items():
        username = user_data.get("username", f"ID{user_id}")
        report += f"👤 {username}:\n"
        user_statuses = user_data.get("statuses", [])

        # Для каждой даты в диапазоне
        for d in date_list:
            status_for_day = "—"
            for record in user_statuses:
                start = datetime.strptime(record["start"], "%Y-%m-%d").date()
                end = datetime.strptime(record["end"], "%Y-%m-%d").date()
                if start <= d <= end:
                    status_for_day = record["status"]
                    break
            report += f"  {d.strftime('%d.%m')}: {status_for_day}\n"
        report += "\n"

    return report.strip()

# Очистка чата (ограничение: только последние 100 сообщений)
async def clear_chat(chat_id, message_id, bot: Bot):
    for i in range(1, 101):
        try:
            await bot.delete_message(chat_id, message_id - i)
        except:
            pass  # Игнорируем ошибки (сообщение не существует или нет прав)

# Обработчик /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = str(message.from_user.id)
    username = message.from_user.username or f"User{user_id}"
    data = load_data()
    if user_id not in data:
        data[user_id] = {"username": username, "statuses": []}
        save_data(data)
    await message.answer(
        f"Привет, {username}! 👋\nВыбери действие:",
        reply_markup=get_main_keyboard()
    )

# Добавить статус — шаг 1
@dp.message(lambda msg: msg.text == "Добавить статус")
async def add_status_start(message: types.Message, state: FSMContext):
    await state.set_state(Form.choosing_status)
    await message.answer("Выбери статус:", reply_markup=get_status_keyboard())

# Выбор статуса — шаг 2
@dp.message(Form.choosing_status)
async def status_chosen(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.clear()
        await message.answer("Выбери действие:", reply_markup=get_main_keyboard())
        return

    valid_statuses = ["Отпуск", "В офисе", "На объекте", "Командировка"]
    if message.text not in valid_statuses:
        await message.answer("Пожалуйста, выбери статус из списка.")
        return

    await state.update_data(chosen_status=message.text)
    await state.set_state(Form.entering_start_date)
    await message.answer(
        "📅 Введи дату начала (в формате ДД.ММ.ГГГГ):\nНапример: 01.06.2025",
        reply_markup=types.ReplyKeyboardRemove()
    )

# Ввод даты начала — шаг 3
@dp.message(Form.entering_start_date)
async def start_date_entered(message: types.Message, state: FSMContext):
    start_date = parse_date(message.text)
    if not start_date:
        await message.answer("❌ Неверный формат даты. Попробуй снова: ДД.ММ.ГГГГ")
        return

    await state.update_data(start_date=start_date.strftime("%Y-%m-%d"))
    await state.set_state(Form.entering_end_date)
    await message.answer("📅 Введи дату окончания (в формате ДД.ММ.ГГГГ):")

# Ввод даты окончания — шаг 4
@dp.message(Form.entering_end_date)
async def end_date_entered(message: types.Message, state: FSMContext):
    end_date = parse_date(message.text)
    if not end_date:
        await message.answer("❌ Неверный формат даты. Попробуй снова: ДД.ММ.ГГГГ")
        return

    data = await state.get_data()
    start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()

    if end_date < start_date:
        await message.answer("❌ Дата окончания не может быть раньше даты начала. Введи заново.")
        return

    user_id = str(message.from_user.id)
    db = load_data()
    record = {
        "status": data["chosen_status"],
        "start": data["start_date"],
        "end": end_date.strftime("%Y-%m-%d")
    }
    db[user_id]["statuses"].append(record)
    save_data(db)

    await state.clear()
    await message.answer(
        f"✅ Статус '{data['chosen_status']}' добавлен с {start_date.strftime('%d.%m.%Y')} по {end_date.strftime('%d.%m.%Y')}",
        reply_markup=get_main_keyboard()
    )

# График на неделю
@dp.message(lambda msg: msg.text == "График на неделю")
async def show_week_schedule(message: types.Message):
    report = generate_schedule_report(days=7)
    await message.answer(report)

# График на месяц
@dp.message(lambda msg: msg.text == "График на месяц")
async def show_month_schedule(message: types.Message):
    report = generate_schedule_report(days=30)
    await message.answer(report)

# Очистить чат
@dp.message(lambda msg: msg.text == "Очистить чат")
async def clear_chat_handler(message: types.Message):
    await message.answer("🧹 Очищаю последние сообщения...")
    await clear_chat(message.chat.id, message.message_id, bot)
    await message.answer("✅ Чат очищен. Выбери действие:", reply_markup=get_main_keyboard())

# Обработка неизвестных команд
@dp.message()
async def unknown_message(message: types.Message):
    await message.answer("Неизвестная команда. Используй кнопки 👇", reply_markup=get_main_keyboard())

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Используем порт 8080 — стандартный для Render
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Запускаем бота на порту {port}")
    
    # Запускаем бота
    asyncio.run(main())
