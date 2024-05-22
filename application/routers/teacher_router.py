import glob
import re
import hashlib
import os

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardBuilder

from application.states import PasswordCheck
from application.database.requests import get_homework_with_details, get_teacher_by_password, get_users_by_ids
from application.database.models import async_session

router = Router(name=__name__)

file_hash_map = {}


@router.message(Command('teacher'))
async def register_students(message: Message, state: FSMContext):
    await message.answer(text='Введите пароль:', reply_markup=ReplyKeyboardRemove())
    await state.set_state(PasswordCheck.EnterPassword)


# @router.message(PasswordCheck.EnterPassword)
# async def check_password(message: Message, state: FSMContext):
#     commands = ['/profile', '/homework', '/top', '/leader', '/monetization', '/info', '/support', '/registration',
#                 '/start', '/newsletter']
#     input_text = message.text
#
#     if input_text in commands:
#         await state.clear()
#         await message.answer("Обнаружена команда. Пожалуйста, введите команду ещё раз.")
#         return
#
#     input_password = message.text
#     teacher_password = await get_teacher_password()
#     if input_password == teacher_password:
#         await message.answer('Пароль верен!')
#         await message.answer(text='Выберите себя:', reply_markup=await kb.teachers_choice())
#         await state.clear()
#     else:
#         await message.answer('🙈Извините, пароль не верен, попробуйте еще раз.')


@router.message(PasswordCheck.EnterPassword)
async def check_password(message: Message, state: FSMContext):
    commands = ['/profile', '/homework', '/top', '/leader', '/monetization', '/info', '/support', '/registration',
                '/start', '/newsletter']
    input_text = message.text

    if input_text in commands:
        await state.clear()
        await message.answer("Обнаружена команда. Пожалуйста, введите команду ещё раз.")
        return

    input_password = input_text.strip()
    teacher = await get_teacher_by_password(input_password)

    if teacher:
        teacher_full_name = f'{teacher.name} {teacher.last_name}'
        await message.answer(f'Пароль верен! Здравствуйте, {teacher_full_name}!')
        keyboard = await students_choice(teacher.id)
        await message.answer(text='Выберите ученика, чтобы посмотреть его домашние задания:', reply_markup=keyboard)
        await state.clear()
    else:
        await message.answer('🙈 Извините, пароль не верен, попробуйте еще раз.')


async def students_choice(teacher_id: int) -> InlineKeyboardMarkup:
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
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Нет доступных домашних заданий", callback_data="no_homework")]
        ])
        return keyboard

    students_choice_kb = InlineKeyboardBuilder()
    students = await get_users_by_ids(list(student_ids))
    for student in students:
        full_name = f'{student.name} {student.last_name}'
        students_choice_kb.add(InlineKeyboardButton(text=full_name, callback_data=f'student_{student.id}_{teacher_id}'))
    return students_choice_kb.adjust(2).as_markup()


# @router.callback_query(F.data.startswith('teacher_'))
# async def teacher_selected(callback: CallbackQuery):
#     teacher_id = callback.data.split('_')[1]
#     directories = {
#         "application/media/photo": "*.jpg",
#         "application/media/text": "*.txt",
#         "application/media/video": "*.mp4",
#         "application/media/links": "*.html",
#         "application/media/voice": "*.ogg",
#     }
#
#     student_ids = set()
#
#     for directory, ext in directories.items():
#         files = glob.glob(f"{directory}/{teacher_id}_*{ext}")
#         for filename in files:
#             match = re.search(rf"{teacher_id}_(\d+)_", filename)
#             if match:
#                 student_ids.add(match.group(1))
#
#     if not student_ids:
#         await callback.message.answer("Для вас нет отправленных домашних заданий.")
#         return
#
#     keyboard = await kb.students_choice(list(student_ids), teacher_id)
#     await callback.message.answer(text="Выберите ученика, чтобы посмотреть его домашние задания:",
#                                   reply_markup=keyboard)


async def generate_hash(file_path):
    filename = os.path.basename(file_path)
    file_hash = hashlib.md5(filename.encode()).hexdigest()
    file_hash_map[file_hash] = file_path
    return file_hash


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
                 InlineKeyboardButton(text="Отклонить", callback_data=f'decline_{file_hash}')],
                [InlineKeyboardButton(text="Обратная связь", callback_data=f'feedback_{file_hash}')]
            ])
            file_input = FSInputFile(path=filename)

            await bot.send_document(chat_id=callback.from_user.id, document=file_input, reply_markup=keyboard)

    if not files_found:
        await callback.message.answer("У этого ученика нет отправленных домашних заданий.")


@router.callback_query(F.data.startswith('accept_'))
async def accept_homework(callback: CallbackQuery):
    file_hash = callback.data.split('_', 1)[1]

    async with async_session() as session:
        homework, student = await get_homework_with_details(session, file_hash)

        if not homework:
            await callback.answer(text="Домашнее задание не найдено.", show_alert=True)
            return

        if not student:
            await callback.answer(text="Студент не найден.", show_alert=True)
            return

        student.point = (student.point or 0) + 3

        await session.delete(homework)
        await session.commit()

        file_path = file_hash_map.get(file_hash)
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

    updated_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Проверено", callback_data=f'checked_{file_hash}')]
    ])

    await callback.message.edit_reply_markup(reply_markup=updated_keyboard)


@router.callback_query(F.data.startswith('decline_'))
async def decline_homework(callback: CallbackQuery):
    file_hash = callback.data.split('_', 1)[1]

    async with async_session() as session:
        homework, student = await get_homework_with_details(session, file_hash)

        if not homework:
            await callback.answer(text="Домашнее задание не найдено.", show_alert=True)
            return

        if not student:
            await callback.answer(text="Студент не найден.", show_alert=True)
            return

        await session.delete(homework)
        await session.commit()

        file_path = file_hash_map.get(file_hash)
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

    updated_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Проверено", callback_data=f'checked_{file_hash}')]
    ])

    await callback.message.edit_reply_markup(reply_markup=updated_keyboard)


@router.callback_query(F.data.startswith('checked_'))
async def checked_homework(callback: CallbackQuery):
    await callback.answer(text="Это домашнее задание уже проверено.", show_alert=True)


@router.callback_query(F.data.startswith('no_homework'))
async def checked_homework(callback: CallbackQuery):
    await callback.answer(text="Для вас нет заданий для проверки.", show_alert=True)


@router.callback_query(F.data.startswith('feedback_'))
async def feedback_homework(callback: CallbackQuery):
    pass
