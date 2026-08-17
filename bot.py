import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# ---------------- СНАЧАЛА ЗАПОЛНИ ЭТИ ДАННЫЕ ----------------
BOT_TOKEN = "8977147484:AAEz9igsPvWzt5i7QQVkYBz6XOCEvvmaeOc"
ADMIN_ID = 7926462587
# -----------------------------------------------------------

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class Form(StatesGroup):
    name = State()
    stats = State()
    goal = State()
    service = State()
    contact = State()


# Главная клавиатура
def main_kb():
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="💪 Оформить анкету")],
            [
                types.KeyboardButton(text="💰 Прайс-лист"),
                types.KeyboardButton(text="📩 Связь со мной"),
            ],
        ],
        resize_keyboard=True,
    )
    return kb


@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    text = (
        f"Здорова, {message.from_user.first_name}!\n\n"
        "Я бот для записи на программы тренировок, разбор техники и силовое ведение.\n"
        "Выбирай нужный пункт в меню ниже 👇"
    )
    await message.answer(text, reply_markup=main_kb())


# Показ прайса
@dp.message(F.text == "💰 Прайс-лист")
async def show_price(message: types.Message):
    text = (
        "📌 **ПРАЙС-ЛИСТ И УСЛУГИ:**\n\n"
        "1️⃣ **Индивидуальная программа тренировок**\n"
        "— Сплит под твои цели (жим, масса, сила, арм-база)\n"
        "— Схема прогрессии весов и подходов\n\n"
        "2️⃣ **Разбор техники по видео**\n"
        "— Детальный разбор твоих рабочих подходов\n"
        "— Указание ошибок, постановка ног, траектории\n\n"
        "3️⃣ **Персональное онлайн-ведение (1 месяц)**\n"
        "— Полная программа + еженедельная корректировка весов\n"
        "— Постоянный разбор техники и ответы на вопросы в ЛС\n\n"
        "Жми **«💪 Оформить анкету»**, чтобы оставить заявку!"
    )
    await message.answer(text, parse_mode="Markdown")


# Прямая связь
@dp.message(F.text == "📩 Связь со мной")
async def contact_me(message: types.Message):
    await message.answer("По всем прямым вопросам пиши в ЛС: @ТВОЙ_ТЕЛЕГРАМ_ХЭНДЛ")


# НАЧАЛО АНКЕТЫ
@dp.message(F.text == "💪 Оформить анкету")
async def start_form(message: types.Message, state: FSMContext):
    await state.set_state(Form.name)
    await message.answer(
        "Шаг 1/5: Как к тебе обращаться? (Имя)",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@dp.message(Form.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Form.stats)
    await message.answer(
        "Шаг 2/5: Напиши свой возраст, рост и вес (например: 18 лет, 175 см, 80 кг):"
    )


@dp.message(Form.stats)
async def process_stats(message: types.Message, state: FSMContext):
    await state.update_data(stats=message.text)
    await state.set_state(Form.goal)
    await message.answer(
        "Шаг 3/5: Какой у тебя стаж в зале и главная цель? (Пример: Стаж 1 год, хочу поднять жим и набрать массу)"
    )


@dp.message(Form.goal)
async def process_goal(message: types.Message, state: FSMContext):
    await state.update_data(goal=message.text)
    await state.set_state(Form.service)

    # Выбор услуги кнопками
    kb = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Программа тренировок")],
            [types.KeyboardButton(text="Разбор техники")],
            [types.KeyboardButton(text="Онлайн-ведение (Месяц)")],
        ],
        resize_keyboard=True,
    )
    await message.answer("Шаг 4/5: Какая услуга тебя интересует?", reply_markup=kb)


@dp.message(Form.service)
async def process_service(message: types.Message, state: FSMContext):
    await state.update_data(service=message.text)
    await state.set_state(Form.contact)
    await message.answer(
        "Шаг 5/5: Напиши свой Telegram для связи (например: @username или номер телефона):",
        reply_markup=types.ReplyKeyboardRemove(),
    )


# ЗАВЕРШЕНИЕ И ОТПРАВКА АНКЕТЫ ТЕБЕ В ЛС
@dp.message(Form.contact)
async def process_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    user_data = await state.get_data()
    await state.clear()

    # Подтверждение пользователю
    await message.answer(
        "🔥 Анкета успешно отправлена! Я изучу твои данные и свяжусь с тобой в ближайшее время.",
        reply_markup=main_kb(),
    )

    # Сообщение ТЕБЕ в ЛС
    admin_text = (
        "📥 **НОВАЯ ЗАЯВКА ИЗ БОТА!**\n\n"
        f"👤 **Имя:** {user_data['name']}\n"
        f"📏 **Параметры:** {user_data['stats']}\n"
        f"🎯 **Цель/Стаж:** {user_data['goal']}\n"
        f"🛠 **Услуга:** {user_data['service']}\n"
        f"📲 **Связь:** {user_data['contact']}\n\n"
        f"Профиль в TG: [{message.from_user.full_name}](tg://user?id={message.from_user.id})"
    )

    await bot.send_message(
        chat_id=ADMIN_ID, text=admin_text, parse_mode="Markdown"
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
