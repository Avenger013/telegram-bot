import glob

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.filters import Command

from application.states import PasswordCheck
from application.database.requests import get_teacher_password

import application.keyboard as kb

router = Router(name=__name__)


@router.message(Command('teacher'))
async def register_students(message: Message, state: FSMContext):
    await message.answer(text='Введите пароль:',  reply_markup=ReplyKeyboardRemove())
    await state.set_state(PasswordCheck.EnterPassword)


@router.message(PasswordCheck.EnterPassword)
async def check_password(message: Message, state: FSMContext):
    commands = ['/profile', '/homework', '/top', '/leader', '/monetization', '/info', '/support', '/registration',
                '/start', '/newsletter']
    input_text = message.text

    if input_text in commands:
        await state.clear()
        await message.answer("Обнаружена команда. Пожалуйста, введите команду ещё раз.")
        return

    input_password = message.text
    teacher_password = await get_teacher_password()
    if input_password == teacher_password:
        await message.answer('Пароль верен!')
        await message.answer(text='Выберите себя:', reply_markup=await kb.teachers_choice())
        await state.clear()
    else:
        await message.answer('🙈Извините, пароль не верен, попробуйте еще раз.')


@router.callback_query(F.data.startswith('teacher_'))
async def teacher_selected(callback: CallbackQuery, bot: Bot):
    teacher_id = callback.data.split('_')[1]

    directories = {
        "application/media/photo": f"{teacher_id}_*.jpg",
        "application/media/text": f"{teacher_id}_*.txt",
        "application/media/video": f"{teacher_id}_*.mp4",
        "application/media/links": f"{teacher_id}_*.html",
    }

    files_found = False

    for directory, pattern in directories.items():
        full_pattern = f"{directory}/{pattern}"
        files = glob.glob(full_pattern)

        for filename in files:
            files_found = True
            file_input = FSInputFile(path=filename)
            await bot.send_document(chat_id=callback.from_user.id, document=file_input)

    if not files_found:
        await callback.message.answer("Для вас нет отправленных домашних заданий.")

