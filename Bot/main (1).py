
from aiogram.types.callback_query import CallbackQuery
from aiogram.utils import callback_data
import parse
import datetime

import config
import logging
import asyncio
import parser_kor
import parser_pogoda

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, BoundFilter, IDFilter
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, reply_keyboard
from aiogram.utils.callback_data import CallbackData


logging.basicConfig(level=logging.INFO)


#устанавливаем соединение с ботом и диспетчером
loop = asyncio.get_event_loop()
bot = Bot(token=config.bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)



class Schedule(StatesGroup):
    get_facultet = State()
    get_kurs = State()
    get_group = State()
    get_type_schedule = State()
    get_schedule = State()
    
data_callback_list = CallbackData("user_data", "action", "data")

@dp.message_handler(commands=['start'], state='*')
async def main_menu(message, state: FSMContext):
    """
    Стартовое приветствие бота.
    """
    
    
  
    buttons = [
     types.InlineKeyboardButton(text="ПОГОДА", callback_data="get_weather"), 
     types.InlineKeyboardButton(text="КОРОНАВИРУС", callback_data="get_corona"), 
     types.InlineKeyboardButton(text="РАСПИСАНИЕ", callback_data="get_schedule"),]
    start_keyboard = types.InlineKeyboardMarkup(row_width=2)
    start_keyboard.add(*buttons)
    await message.answer("Приветствую тебя, друг!\n\nПока что я могу предложить тебе только посмотреть расписание пар. Но я учусь и в скором времени мой функционал расширится!", reply_markup=start_keyboard)


@dp.callback_query_handler(lambda call: call.data == 'get_weather', state="*")
async def change_facultest(call: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(call.id)
    buttons = [types.InlineKeyboardButton(text="Сейчас", callback_data="get_weather_now"), types.InlineKeyboardButton(text="Сегодня", callback_data="get_weather_today"), 
    types.InlineKeyboardButton(text="Завтра", callback_data="get_weather_tomorrow"),
    types.InlineKeyboardButton(text="На неделю", callback_data="get_weather_week")]
    weather_keyboard = types.InlineKeyboardMarkup(row_width=2)
    weather_keyboard.add(*buttons)
    await call.message.answer("За какой период вы хотите посмотреть погоду?", reply_markup=weather_keyboard)


@dp.callback_query_handler(lambda call: call.data == 'get_weather_now', state="*")
async def change_facultest(call: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(call.id)
    text_weather = parser_pogoda.pogoda_1()
    await call.message.answer(text=text_weather)

@dp.callback_query_handler(lambda call: call.data == 'get_weather_today', state="*")
async def change_facultest(call: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(call.id)
    text_weather = parser_pogoda.pogoda_2()
    await call.message.answer(text=text_weather)

@dp.callback_query_handler(lambda call: call.data == 'get_weather_tomorrow', state="*")
async def change_facultest(call: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(call.id)
    text_weather = parser_pogoda.pogoda_3()
    await call.message.answer(text=text_weather)

@dp.callback_query_handler(lambda call: call.data == 'get_weather_week', state="*")
async def change_facultest(call: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(call.id)
    text_weather = parser_pogoda.pogoda_4()
  
    await call.message.answer(text=text_weather)
    

@dp.callback_query_handler(lambda call: call.data == 'get_corona', state="*")
async def change_facultest(call: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(call.id)
    text_weather = parser_kor.corona_1()
    #text_weather2 = parser_kor.corona_2()
    img_weather = parser_kor.corona_img()
    await call.message.answer(text=text_weather)
    await call.message.answer_photo(photo=types.InputFile("grafik.png"))










@dp.callback_query_handler(lambda call: call.data == 'get_schedule', state="*")
async def change_facultest(call: types.CallbackQuery, state: FSMContext):
    """Парсим список факультутетов с сайта и отправляем пользователю клавиатуру с выбором"""
    list_facultet = parse.get_facultet()
    buttons = []
    for fc in list_facultet:
        buttons.append(types.InlineKeyboardButton(text=fc, callback_data=data_callback_list.new(action="fc", data=fc)))
    facultet_keyboard = types.InlineKeyboardMarkup(row_width=3)
    facultet_keyboard.add(*buttons)

    await call.message.answer(text="Выбери свой факультет", reply_markup=facultet_keyboard)
    await state.set_state(Schedule.get_kurs)
    await bot.answer_callback_query(call.id)
    

@dp.callback_query_handler(data_callback_list.filter(action=["fc"]), state=Schedule.get_kurs)
async def get_facultet(call:types.CallbackQuery, state:FSMContext, callback_data=dict):
    """Записываем выбор пользователя (факультет в state)
    Отсылаем клавиаатуру для выбора курса"""
    await bot.delete_message(chat_id = call.message.chat.id, message_id=call.message.message_id)
    await dp.storage.update_data(user = call.message.chat.id, user_facultet = callback_data["data"])
    list_kurs = parse.get_kurs(callback_data["data"])
    buttons = []
    for kr in list_kurs:
        buttons.append(types.InlineKeyboardButton(text=kr, callback_data=data_callback_list.new(action="kurs", data=kr)))
    kurs_keyboard = types.InlineKeyboardMarkup(row_width=5)
    kurs_keyboard.add(*buttons)
    await call.message.answer(text="Выбери курс", reply_markup=kurs_keyboard)
    await state.set_state(Schedule.get_group)
    
    await bot.answer_callback_query(call.id)
    

@dp.callback_query_handler(data_callback_list.filter(action=["kurs"]), state=Schedule.get_group)
async def get_kurs(call:types.CallbackQuery, state:FSMContext, callback_data=dict):
    """Записываем выбор пользователя (курс в state)
    Отсылаем клавиаатуру для выбора группы"""
    await bot.delete_message(chat_id = call.message.chat.id, message_id=call.message.message_id)
    await dp.storage.update_data(user = call.message.chat.id, user_kurs = callback_data["data"])
    data = await dp.storage.get_data(user=call.message.chat.id)
    #print(data)
    #print(data["user_facultet"])
    list_group = parse.get_group(data["user_facultet"], callback_data["data"])

    buttons = []
    for gr in list_group:
        buttons.append(types.InlineKeyboardButton(text=gr, callback_data=data_callback_list.new(action="group", data=gr)))
        
    group_keyboard = types.InlineKeyboardMarkup(row_width=5)
    group_keyboard.add(*buttons)
    await call.message.answer(text="Выбери группу", reply_markup=group_keyboard)
    await state.set_state(Schedule.get_type_schedule)

    await bot.answer_callback_query(call.id)




@dp.callback_query_handler(data_callback_list.filter(action=["group"]), state=Schedule.get_type_schedule)
async def get_kurs(call:types.CallbackQuery, state:FSMContext, callback_data=dict):
    """Записываем выбор пользователя (группа в state)
    Отсылаем клавиаатуру для выбора типа расписания (сегодня/вся неделя)"""
    await bot.delete_message(chat_id = call.message.chat.id, message_id=call.message.message_id)
    await dp.storage.update_data(user = call.message.chat.id, user_group = callback_data["data"])
    data = await dp.storage.get_data(user=call.message.chat.id)
    list_group = parse.get_group(data["user_facultet"], callback_data["data"]) #получаем список групп

    buttons=[types.InlineKeyboardButton(text="СЕГОДНЯ", callback_data="today"), types.InlineKeyboardButton(text="НЕДЕЛЯ", callback_data="all_schedule")]  
    group_keyboard = types.InlineKeyboardMarkup(row_width=2)
    group_keyboard.add(*buttons)
    await call.message.answer(text="Какое расписание?", reply_markup=group_keyboard)
    await state.set_state(Schedule.get_schedule)

    await bot.answer_callback_query(call.id)


@dp.callback_query_handler(lambda call: call.data == 'today', state=Schedule.get_schedule)
async def get_schedule_today(call:types.CallbackQuery, state:FSMContext):
    """
    Получаем расписание на сегодня
    """
    await bot.delete_message(chat_id = call.message.chat.id, message_id=call.message.message_id)
    data = await dp.storage.get_data(chat=call.message.chat.id)
    schedule = parse.get_schedule(facultet=data["user_facultet"], kurs=data["user_kurs"], group=data["user_group"])
    print(schedule)
    name_day = config.week_list[str(datetime.datetime.today().weekday()+1)]

    text_message='Сегодня: '+name_day+'\nНеделя: '+parse.get_week()+'\n\n'
    
    for sched in schedule:
        if len(sched)>1:
            if sched[0]==name_day:
                if sched[2]==parse.get_week():
                    text_message+='\n\U0000231B '+sched[1]+'\n\U0001F4CC '+sched[4]+'\n\U0001F464 '+sched[5]+'\n\U0001F4D1 '+sched[7]+'\n\n'
    await call.message.answer(text_message)
    await state.finish()
    


@dp.callback_query_handler(lambda call: call.data == 'all_schedule', state=Schedule.get_schedule)
async def get_schedule_all(call:types.CallbackQuery, state:FSMContext):
    """
    Получаем расписание на всю неделю
    """
    await bot.delete_message(chat_id = call.message.chat.id, message_id=call.message.message_id)
    data = await dp.storage.get_data(chat=call.message.chat.id)
    schedule = parse.get_schedule(facultet=data["user_facultet"], kurs=data["user_kurs"], group=data["user_group"])
    name_day = config.week_list[str(datetime.datetime.today().weekday()+1)]

    text_message='\nНеделя: '+parse.get_week()+'\n\n'
    
    for sched in schedule:
        if len(sched)>1:
            if sched[2]==parse.get_week():
                text_message+='\n'+sched[0]+'\n\U0000231B '+sched[1]+'\n\U0001F4CC '+sched[4]+'\n\U0001F464 '+sched[5]+'\n\U0001F4D1 '+sched[7]+'\n\n'
    await call.message.answer(text_message)
    await state.finish()
    

def main():
    executor.start_polling(dp, loop=loop, skip_updates = False)     



if __name__ == "__main__":
    main()
     
