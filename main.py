from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Токен и инициализация бота
API_TOKEN = "8862971826:AAHZffWQ-JEAJuSEhz9IeUDp4udbp9ve_Mg"
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
# Состояния бота
class AppointmentState(StatesGroup):
    name = State() #ФИО
    doctor = State() #доктор
    time = State() #дата

# Команда /start
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.reply("Привет! Напиши /book чтобы записаться к врачу.")

# Просим ФИО
@dp.message(Command("book"))
async def book_cmd(message: types.Message, state: FSMContext):
    await state.set_state(AppointmentState.name)
    await message.reply("Введите ФИО пациента:")

# Ловим ФИО и выводим сообщение с врачами
@dp.message(AppointmentState.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(user_name=message.text) # сохраняем имя
    await state.set_state(AppointmentState.doctor) # переключаем шаг

    # Создаем кнопки выбора врача
    kb = InlineKeyboardBuilder()
    kb.button(text="Терапевт", callback_data="Терапевт")
    kb.button(text="Хирург", callback_data="Хирург")
    kb.button(text="Кардиолог", callback_data="Кардиолог")
    kb.button(text="Изменить ФИО", callback_data="to_name") # кнопка назад
    kb.adjust(1)

    await message.reply(f"Пациент: {message.text}\n\nВыберите врача:", reply_markup=kb.as_markup())

# Назад к ФИО
@dp.callback_query(AppointmentState.doctor, lambda c: c.data == "to_name")
async def back_to_name(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AppointmentState.name)
    await callback.message.delete() # удаление сообщения с кнопками
    await callback.message.answer("Введите ФИО пациента заново:")

# Получаем выбор врача и меняем сообщение на выбор времени
@dp.callback_query(AppointmentState.doctor)
async def get_doctor(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(user_doctor=callback.data) # сохраняем callback_data как название врача
    await state.set_state(AppointmentState.time) # переключаем шаг

    data = await state.get_data() # берем имя из памяти

    # Создаем кнопки выбора времени
    kb = InlineKeyboardBuilder()
    kb.button(text="Сегодня, 14:00", callback_data="14:00")
    kb.button(text="Завтра, 10:00", callback_data="10:00")
    kb.button(text="Завтра, 15:30", callback_data="15:30")
    kb.button(text="Назад к врачам", callback_data="to_doctor") # кнопка назад
    kb.adjust(1)

    # Редактируем старое сообщение
    await callback.message.edit_text(
        f"Пациент: {data['user_name']}\nВрач: {callback.data}\n\nВыберите время:",
        reply_markup=kb.as_markup()
    )

# Назад к выбору врача
@dp.callback_query(AppointmentState.time, lambda c: c.data == "to_doctor")
async def back_to_doctor(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(AppointmentState.doctor)
    data = await state.get_data()

    # Заново создаем клавиатуру врачей для старого сообщения
    kb = InlineKeyboardBuilder()
    kb.button(text="Терапевт", callback_data="Терапевт")
    kb.button(text="Хирург", callback_data="Хирург")
    kb.button(text="Кардиолог", callback_data="Кардиолог")
    kb.button(text="Изменить ФИО", callback_data="to_name")
    kb.adjust(1)

    await callback.message.edit_text(f"Пациент: {data['user_name']}\n\nВыберите врача:", reply_markup=kb.as_markup())

# Получаем время и выводим итог
@dp.callback_query(AppointmentState.time)
async def get_time(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data() # достаем все данные из памяти

    itog = (
        f"Запись оформлена!\n"
        f"Пациент: {data['user_name']}\n"
        f"Врач: {data['user_doctor']}\n"
        f"Время: {callback.data}"
    )

    # Заменяем сообщение на финальный текст без кнопок
    await callback.message.edit_text(itog)
    await state.clear() # очищаем бота

# Запуск бота
if __name__ == '__main__':
    dp.run_polling(bot)
