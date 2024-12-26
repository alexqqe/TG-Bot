from aiogram import Bot, Dispatcher, types, F
import logging
import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ErrorEvent

API_KEY = ''

bot = Bot(token=API_KEY)
dp = Dispatcher()

users = {}

class CityStates(StatesGroup):
    first_city = State()  # Состояние для первого города
    second_city = State()  # Состояние для второго города
    another_cities = State() # Состояние для доп городов

STATE_WRITING1 = 'writing_first_city'
STATE_WRITING2 = 'writing_sec_city'

# Обработчик команды /start
@dp.message(F.text == '/start')
async def send_welcome(message: types.Message):
    # users[message.from_user.id] = {'state': STATE_WRITING1, 'city1': [], 'city2': [], 'another_cities':[]}
    # Создание кнопки
    button = types.KeyboardButton(text='Попробовать!')

    # Создание клавиатуры
    keyboard = types.ReplyKeyboardMarkup(keyboard=[[button]], resize_keyboard=True)

    await message.answer('Привет! Это тестовый бот, который может быстро вернуть информацию о погоде в выбранных городах', reply_markup=keyboard)

# Обработчик кнопки «Нажми меня!»
@dp.message(F.text == 'Попробовать!')
async def start_command(message: Message, state: FSMContext):
    await message.answer("Привет! Введите первый город:")
    await state.set_state(CityStates.first_city)  # Устанавливаем состояние для первого города

# Получаем 1 город
@dp.message(CityStates.first_city)
async def process_first_city(message: Message, state: FSMContext):
    first_city = message.text
    # Сохраняем первый город в состояние
    await state.update_data(first_city=first_city)
    await message.answer(f"Вы ввели первый город: {first_city}. Теперь введите второй город:")
    await state.set_state(CityStates.second_city)  # Переход в состояние ожидания второго города

# Получаем 2 город
@dp.message(CityStates.second_city)
async def process_second_city(message: Message, state: FSMContext):
    second_city = message.text
    # Получаем данные из состояния
    data = await state.get_data()
    first_city = data.get('first_city')

    # Выводим результаты
    await message.answer(f"Вы ввели два города:\n1. {first_city}\n2. {second_city}")

    await message.answer(
        'Добавить в прогноз погоды ещё один город?',
        reply_markup=await get_keyboard_1()
    )
    # # Очистка состояния
    # await state.clear()

async def get_keyboard_1():
    buttons = [InlineKeyboardButton(text='Добавить', callback_data='first'), InlineKeyboardButton(text='Не добавлять', callback_data='sec')]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons], row_width=2)
    return keyboard

@dp.callback_query()
async def handle_callback(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "first":
        await callback_query.message.answer("Введите название города:")
        await state.set_state(CityStates.another_cities)
    elif callback_query.data == "sec":
        await callback_query.message.answer("Спасибо! Все города сохранены.")
        # data = await state.get_data()
        # another_cities = data.get("another_cities", [])
        # await callback_query.message.answer(f'{another_cities}')
        await state.clear()

@dp.message(CityStates.another_cities)
async def process_another_city(message: Message, state: FSMContext):
    another_city = message.text
    data = await state.get_data()
    another_cities = data.get("another_cities", [])
    another_cities.append(another_city)
    await state.update_data(another_cities=another_cities)

    await message.answer(
        f"Вы добавили город: {another_city}. Хотите добавить ещё один город?",
        reply_markup=await get_keyboard_1()
    )


# Обработка сообщений
@dp.message()
async def handle_message(message: types.Message):
    # if users[message.from_user.id]['state'] == STATE_WRITING1:
    #     users[message.from_user.id]['city1'] = F.text
    await message.answer('Извините, я не понял ваш запрос. Пожалуйста, выберите команду или кнопку.')



@dp.message(F.text == '/help')
async def on_button_click(message: types.Message):
    await message.answer('bla-bla-bla')

@dp.message(F.text == '/weather')
async def on_button_click(message: types.Message):
    await message.answer('bla-bla-bla')

@dp.errors()
async def handle_error(event: ErrorEvent):
    logging.error(f'Произошла ошибка: {event.exception}')
    if event.update.message:
        await event.update.message.answer('Извините, произошла ошибка.')

# Запуск бота
if __name__ == '__main__':
    try:
        asyncio.run(dp.start_polling(bot))
    except Exception as e:
        logging.error(f'Ошибка при запуске бота: {e}')