from aiogram import Bot, F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.settings import settings
from core.handlers.helpers import button_parser
from core.handlers.searches import ascii2d_handler, saucenao_handler

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

router = Router()

class Ascii2dQuestion(StatesGroup):
    wait_ascii2d = State()

yes_no_keyboard = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="Да"), KeyboardButton(text="Нет")]
], resize_keyboard=True)

@router.message(F.text == "/start", F.chat.type == "private")
async def get_start(message: Message, bot: Bot):
    await message.answer(f'Пришли картинку, я попробую найти оригинал и автора')
    
@router.message(F.photo, F.chat.type == "private")
async def get_photo(message: Message, bot: Bot, state: FSMContext):
    file = await bot.get_file(message.photo[-1].file_id)
    fileUrl = "https://api.telegram.org/file/bot" + settings.tokens.bot_token + "/" + file.file_path
    answer = ''
    attachedUrls = []
    linksMarkup = InlineKeyboardBuilder()
    
    # sauceNao = await saucenao_handler(fileUrl)
    sauceNao = 0
    if sauceNao:
        button_parser(sauceNao, linksMarkup, attachedUrls)
        for item in sauceNao:
            if item.title != '' and item.author != '':
                title = item.title
                author = item.author
                break
        
        answer = "<b>Название: </b>" + title + "\n<b>Автор: </b>" + author + "\n"
        answer += "\n<i>Если нету того, что нужно, попробуй вручную:</i>\n<b>saucenao.com | ascii2d.net | images.google.ru | yandex.ru/images/</b>"
        await message.reply(answer, 
                            reply_markup=linksMarkup.as_markup(), 
                            parse_mode=ParseMode.HTML,
                            disable_web_page_preview = True)
        await state.clear()
    else:
        await message.reply('Поиск по <b>SauceNao</b> ничего не дал. Попробовать <b>ASCII2D</b>?\n<i>Нужно будет немного подождать.</i>', 
                            parse_mode=ParseMode.HTML,
                            reply_markup=yes_no_keyboard)
        await state.update_data(file_url = fileUrl)
        await state.update_data(message_for_answer = message.message_id)
        await state.set_state(Ascii2dQuestion.wait_ascii2d)
        
@router.message(Ascii2dQuestion.wait_ascii2d, F.chat.type == "private", F.text.in_(['Да', 'Нет']))    
async def ascii2d_choosen(message: Message, bot: Bot, state: FSMContext):
    state_data = await state.get_data()
    if message.text == 'Нет':
        answer = "К сожалению, ничего не найдено 😞\nМожешь попробовать сам на сайтах \n<b>saucenao.com | ascii2d.net | images.google.ru | yandex.ru/images/</b>"
        await message.answer(answer,
                            reply_to_message_id=state_data['message_for_answer'], 
                            parse_mode=ParseMode.HTML, 
                            disable_web_page_preview = True,
                            reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        answer = "<b><i>Минутку...</i></b>"
        waitMsg = await message.answer(answer, 
                            parse_mode=ParseMode.HTML, 
                            disable_web_page_preview = True,
                            reply_markup=ReplyKeyboardRemove())
        attachedUrls = []
        linksMarkup = InlineKeyboardBuilder()
        ascii2d = await ascii2d_handler(state_data['file_url'])
        if ascii2d:
            button_parser(ascii2d, linksMarkup, attachedUrls)
            for item in ascii2d:
                if item.title != '' and item.author != '':
                    title = item.title
                    author = item.author
                    break
            
            answer = "<b>Название: </b>" + title + "\n<b>Автор: </b>" + author + "\n"
            answer += "\n<i>Если нету того, что нужно, попробуй вручную:</i>\n<b>saucenao.com | ascii2d.net | images.google.ru | yandex.ru/images/</b>"
            
            await bot.delete_message(chat_id=message.chat.id, message_id=waitMsg.message_id)
            await message.answer(answer,
                                reply_to_message_id=state_data['message_for_answer'],
                                reply_markup=linksMarkup.as_markup(), 
                                parse_mode=ParseMode.HTML,
                                disable_web_page_preview = True)
            await state.clear()     
        else:
            await bot.delete_message(chat_id=message.chat.id, message_id=waitMsg.message_id)
            answer = "К сожалению, ничего не найдено 😞\nМожешь попробовать сам на сайтах \n<b>saucenao.com | ascii2d.net | images.google.ru | yandex.ru/images/</b>"
            await message.answer(answer, 
                                reply_to_message_id=state_data['message_for_answer'],
                                parse_mode=ParseMode.HTML, 
                                disable_web_page_preview = True,
                                reply_markup=ReplyKeyboardRemove())
            await state.clear()
   
@router.message(Ascii2dQuestion.wait_ascii2d, F.chat.type == "private")     
async def wrong_answer(message: Message, bot: Bot, state: FSMContext):
    await message.answer(f'Такие сообщения я не понимаю.\nВыберите вариант ответа из списка ниже.', reply_markup=keyboard, resize_keyboard=True)

@router.message(F.chat.type == "private")         
async def get_anything(message: Message, bot: Bot):
    await message.answer(f'Такие сообщения я не понимаю.')

async def get_group_message(message: Message, bot: Bot):
    await message.answer(f'-')