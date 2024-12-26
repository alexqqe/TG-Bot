from aiogram import Bot, Dispatcher, types, F
import logging
import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from weather_forecast import forecast

# Инициализация бота
with open('/Users/skomorohovaleks/PycharmProjects/TG-Bot/.venv/api_key_1.txt', 'r') as file:
    API_KEY = file.read().strip()

bot = Bot(token=API_KEY)
dp = Dispatcher()

# Логгирование
logging.basicConfig(level=logging.INFO)

class CityStates(StatesGroup):
    first_city = State()  # Состояние для первого города
    second_city = State()  # Состояние для второго города
    another_cities = State()  # Состояние для дополнительных городов
    getting_data = State()  # Получение данных прогноза

# Обработчик команды /start
@dp.message(F.text == '/start')
async def send_welcome(message: types.Message):
    button = types.KeyboardButton(text='Попробовать!')
    keyboard = types.ReplyKeyboardMarkup(keyboard=[[button]], resize_keyboard=True)
    await message.answer('Привет! Это бот для прогноза погоды. Нажмите "Попробовать!", чтобы начать.', reply_markup=keyboard)

# Начало сценария
@dp.message(F.text == 'Попробовать!')
async def start_command(message: Message, state: FSMContext):
    await message.answer("Введите первый город(на английском языке):")
    await state.set_state(CityStates.first_city)

@dp.message(F.text == '/help')
async def start_command1(message: Message, state: FSMContext):
    await message.answer("Это бот для прогноза погоды. Нажмите 'Попробовать!', чтобы начать.")

@dp.message(F.text == '/weather')
async def start_command1(message: Message, state: FSMContext):
    await message.answer("Введите первый город(на английском языке):")
    await state.set_state(CityStates.first_city)

# Обработка первого города
@dp.message(CityStates.first_city)
async def process_first_city(message: Message, state: FSMContext):
    first_city = message.text
    await state.update_data(first_city=first_city)
    await message.answer(f"Первый город: {first_city}. Теперь введите второй город(на английском языке):")
    await state.set_state(CityStates.second_city)

# Обработка второго города
@dp.message(CityStates.second_city)
async def process_second_city(message: Message, state: FSMContext):
    second_city = message.text
    await state.update_data(second_city=second_city)
    data = await state.get_data()
    await message.answer(f"Вы ввели:\n1. {data['first_city']}\n2. {data['second_city']}")
    await message.answer('Хотите добавить ещё города?', reply_markup=await get_keyboard_1())

# Клавиатура для добавления городов
async def get_keyboard_1():
    buttons = [
        InlineKeyboardButton(text='Добавить город', callback_data='add_city'),
        InlineKeyboardButton(text='Готово', callback_data='done')
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

# Клавиатура для выбора дня
async def get_keyboard_2():
    buttons = [
        InlineKeyboardButton(text='Сегодня', callback_data='0'),
        InlineKeyboardButton(text='1 день', callback_data='1'),
        InlineKeyboardButton(text='2 дня', callback_data='2'),
        InlineKeyboardButton(text='3 дня', callback_data='3'),
        InlineKeyboardButton(text='4 дня', callback_data='4')
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

# Обработка нажатий кнопок
@dp.callback_query()
async def handle_callback(callback_query: CallbackQuery, state: FSMContext):
    data = callback_query.data

    if data == 'add_city':
        await callback_query.message.answer("Введите название города:")
        await state.set_state(CityStates.another_cities)
    elif data == 'done':
        await callback_query.message.answer("Выберите день для прогноза:", reply_markup=await get_keyboard_2())
        await state.set_state(CityStates.getting_data)
    else:
        await getting_data(callback_query, state)

# Добавление дополнительных городов
@dp.message(CityStates.another_cities)
async def process_another_city(message: Message, state: FSMContext):
    another_city = message.text
    data = await state.get_data()
    another_cities = data.get("another_cities", [])
    another_cities.append(another_city)
    await state.update_data(another_cities=another_cities)
    await message.answer(f"Город {another_city} добавлен. Хотите добавить ещё?", reply_markup=await get_keyboard_1())

# Получение прогноза погоды
@dp.callback_query(CityStates.getting_data)
async def getting_data(callback_query: CallbackQuery, state: FSMContext):
    day_number = int(callback_query.data)
    data = await state.get_data()

    # Формирование списка городов
    cities = [data.get('first_city'), data.get('second_city')]
    cities += data.get('another_cities', [])

    for city in cities:
        if not city:
            continue

        try:
            forecast_data = forecast(city)
            day_forecast = forecast_data[day_number]
            date = day_forecast["Date"]
            wind_speed = day_forecast["WindSpeed"]
            humidity = day_forecast["Humidity"]
            precipitation = day_forecast["PrecipitationProbability"]
            temp_max = day_forecast["TemperatureMax"]
            temp_min = day_forecast["TemperatureMin"]

            await callback_query.message.answer(
                f"Прогноз для {city}:\n"
                f"Дата: {date[:10]}\n"
                f"Скорость ветра: {wind_speed} м/с\n"
                f"Влажность: {humidity}%\n"
                f"Вероятность дождя: {precipitation}%\n"
                f"Температура: от {temp_min}°F до {temp_max}°F"
            )
        except Exception as e:
            logging.error(f"Ошибка при обработке города {city}: {e}")
            await callback_query.message.answer(f"Не удалось получить прогноз для города {city}.")

# Запуск бота
if __name__ == '__main__':
    try:
        asyncio.run(dp.start_polling(bot))
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")

# логирование и обработку ошибок мне помог сделать великий и ужасный чат-гпт, спасибо ему. считаю это честным