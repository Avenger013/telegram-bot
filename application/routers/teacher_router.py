import glob
import re
import hashlib

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup

from application.states import PasswordCheck
from application.database.requests import get_teacher_password

import application.keyboard as kb

router = Router(name=__name__)


@router.message(Command('teacher'))
async def register_students(message: Message, state: FSMContext):
    await message.answer(text='Введите пароль:', reply_markup=ReplyKeyboardRemove())
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
async def teacher_selected(callback: CallbackQuery):
    teacher_id = callback.data.split('_')[1]
    directories = {
        "application/media/photo": "*.jpg",
        "application/media/text": "*.txt",
        "application/media/video": "*.mp4",
        "application/media/links": "*.html",
        "application/media/voice": "*.ogg",
    }

    student_ids = set()

    for directory, ext in directories.items():
        files = glob.glob(f"{directory}/{teacher_id}_*{ext}")
        for filename in files:
            match = re.search(rf"{teacher_id}_(\d+)_", filename)
            if match:
                student_ids.add(match.group(1))

    if not student_ids:
        await callback.message.answer("Для вас нет отправленных домашних заданий.")
        return

    keyboard = await kb.students_choice(list(student_ids), teacher_id)
    await callback.message.answer(text="Выберите ученика, чтобы посмотреть его домашние задания:",
                                  reply_markup=keyboard)


async def generate_hash(input_string):
    return hashlib.md5(input_string.encode()).hexdigest()[:8]


@router.callback_query(F.data.startswith('student_'))
async def student_files(callback: CallbackQuery, bot: Bot):
    parts = callback.data.split('_')
    student_id = parts[1]
    teacher_id = parts[2]

    directories = {
        "application/media/photo": f"{teacher_id}_{student_id}_*.jpg",
        "application/media/text": f"{teacher_id}_{student_id}_*.txt",
        "application/media/video": f"{teacher_id}_{student_id}_*.mp4",
        "application/media/links": f"{teacher_id}_{student_id}_*.html",
        "application/media/voice": f"{teacher_id}_{student_id}_*.ogg",
    }

    files_found = False
    for directory, pattern in directories.items():
        full_pattern = f"{directory}/{pattern}"
        files = glob.glob(full_pattern)

        for filename in files:
            files_found = True
            file_hash = await generate_hash(filename)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Принять", callback_data=f'accept_{file_hash}'),
                 InlineKeyboardButton(text="Отклонить", callback_data=f'decline_{file_hash}')]
            ])
            file_input = FSInputFile(path=filename)

            await bot.send_document(chat_id=callback.from_user.id, document=file_input, reply_markup=keyboard)

    if not files_found:
        await callback.message.answer("Для этого ученика нет отправленных домашних заданий.")
