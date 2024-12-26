from aiogram import Bot, Dispatcher, types, F
import logging
import asyncio
from aiogram.types import ErrorEvent

API_KEY = ''

bot = Bot(token=API_KEY)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(F.text == '/start')
async def send_welcome(message: types.Message):
    # Создание кнопки
    button = types.KeyboardButton(text='Нажми меня!')

    # Создание клавиатуры
    keyboard = types.ReplyKeyboardMarkup(keyboard=[[button]], resize_keyboard=True)

    await message.answer('Привет! Это тестовый бот. Нажми на кнопку:', reply_markup=keyboard)

# Обработчик кнопки «Нажми меня!»
@dp.message(F.text == 'Нажми меня!')
async def on_button_click(message: types.Message):
    await message.answer('Вы нажали на кнопку!')

@dp.message(F.text == '/help')
async def on_button_click(message: types.Message):
    await message.answer('bla-bla-bla')

@dp.message(F.text == '/weather')
async def on_button_click(message: types.Message):
    await message.answer('bla-bla-bla')

# Обработка других сообщений
@dp.message()
async def handle_unknown_message(message: types.Message):
    await message.answer('Извините, я не понял ваш запрос. Пожалуйста, выберите команду или кнопку.')

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