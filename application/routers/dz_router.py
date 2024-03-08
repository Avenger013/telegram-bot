import os
import re
import datetime

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from aiogram.exceptions import TelegramBadRequest

from application.states import HomeworkState
from application.database.models import Student, async_session
from application.database.requests import get_student

import application.keyboard as kb

router = Router(name=__name__)


@router.message(F.text == '✉️ Отправка ДЗ')
@router.message(Command('homework'))
async def submitting_homework(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    async with async_session() as session:
        student = await get_student(session, tg_id)
        if student:
            await message.answer(
                text='😁Вы уже зарегистрированы. \nПожалуйста, выберите преподавателя, которому вы хотите отправить домашнее задание:',
                reply_markup=await kb.choice_teacher(tg_id)
            )
            await state.set_state(HomeworkState.ChoiceTeacher)
        else:
            await message.answer(
                text=f'{message.from_user.first_name}, это ваш первый вход. \nПожалуйста, пройдите быструю регистрацию.',
                reply_markup=kb.registration
            )


@router.callback_query(F.data.startswith('send'))
async def call_submitting_homework(callback: CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id
    await callback.message.edit_text(text='Выберите преподавателя, которому вы хотите отправить домашнее задание:',
                                     reply_markup=await kb.choice_teacher(tg_id))
    await state.set_state(HomeworkState.ChoiceTeacher)


@router.callback_query(F.data.startswith('choice_'), HomeworkState.ChoiceTeacher)
async def teacher_selected_for_homework(callback: CallbackQuery, state: FSMContext):
    teacher_id = callback.data.split('_')[1]
    await state.update_data(teacher_id=teacher_id)
    await callback.message.edit_text(text='Какой тип домашнего задания вы хотите отправить?', reply_markup=kb.dz_type)
    await state.set_state(HomeworkState.ChoosingDZType)


@router.callback_query(F.data.startswith('p_p'), HomeworkState.ChoosingDZType)
async def dz_type_photo(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Отлично, теперь пришлите фото вашего домашнего задания!')
    await state.set_state(HomeworkState.WaitingForPhoto)


@router.callback_query(F.data.startswith('v_v'), HomeworkState.ChoosingDZType)
async def dz_type_video(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Отлично, теперь пришлите видео вашего домашнего задания!')
    await state.set_state(HomeworkState.WaitingForVideo)


@router.callback_query(F.data.startswith('t_l'), HomeworkState.ChoosingDZType)
async def dz_type_text_link(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Отлично, теперь напишите текст вашего домашнего задания или скиньте ссылку!')
    await state.set_state(HomeworkState.WaitingForTextAndLinks)


@router.message(F.photo, HomeworkState.WaitingForPhoto)
async def receive_homework_photo(message: Message, state: FSMContext):
    tg_id = message.from_user.id

    async with async_session() as session:
        student = await session.scalar(select(Student).where(Student.tg_id == tg_id))
        if not student:
            await message.answer("Студент не найден в базе данных.")
            return
        student_id = student.id

    data = await state.get_data()
    teacher_id = data.get('teacher_id')

    photo_id = message.photo[-1].file_id

    await state.update_data(photo_id=photo_id, student_id=student_id, teacher_id=teacher_id)
    await message.answer(text="Всё верно? Окончательно отправить?", reply_markup=kb.confirmation)


@router.callback_query(F.data.in_(['confirm', 'change']), HomeworkState.WaitingForPhoto)
async def confirm_homework_photo(callback: CallbackQuery, state: FSMContext, bot: Bot):
    call_data = callback.data

    if call_data == 'confirm':
        data = await state.get_data()
        photo_id = data['photo_id']
        student_id = data['student_id']
        teacher_id = data['teacher_id']

        async with async_session() as session:
            student = await session.scalar(select(Student).where(Student.id == student_id))
            if not student:
                await callback.message.answer("Произошла ошибка при поиске данных студента.")
                return

        full_name = f'{student.name} {student.last_name}'

        file = await bot.get_file(photo_id)
        file_path = file.file_path

        directory = "application/media/photo"
        if not os.path.exists(directory):
            os.makedirs(directory)

        timestamp = datetime.datetime.now().strftime("%d_%m_%Y_%H-%M-%S")
        filename = f"{directory}/{teacher_id}_{student_id}_{full_name}_{timestamp}_photo.jpg"

        await bot.download_file(file_path, filename)
        await callback.message.answer("Домашнее задание (фото) успешно отправлено!")
        await state.clear()
    elif call_data == 'change':
        await callback.message.answer("Отлично, отправьте свое домашнее задание ещё раз.")

    await callback.answer()


@router.message(F.video, HomeworkState.WaitingForVideo)
async def receive_homework_video(message: Message, state: FSMContext):
    tg_id = message.from_user.id

    async with async_session() as session:
        student = await session.scalar(select(Student).where(Student.tg_id == tg_id))
        if not student:
            await message.answer("Студент не найден в базе данных.")
            return
        student_id = student.id

    data = await state.get_data()
    teacher_id = data.get('teacher_id')

    video_id = message.video.file_id

    await state.update_data(video_id=video_id, student_id=student_id, teacher_id=teacher_id)
    await message.answer(text="Всё верно? Окончательно отправить?", reply_markup=kb.confirmation_video)


@router.callback_query(F.data.in_(['vi_confirm', 'deo_change']), HomeworkState.WaitingForVideo)
async def confirm_homework_video(callback: CallbackQuery, state: FSMContext, bot: Bot):
    call_data = callback.data

    if call_data == 'vi_confirm':
        data = await state.get_data()
        video_id = data['video_id']
        student_id = data['student_id']
        teacher_id = data['teacher_id']

        async with async_session() as session:
            student = await session.scalar(select(Student).where(Student.id == student_id))
            if not student:
                await callback.message.answer("Произошла ошибка при поиске данных студента.")
                return

        full_name = f'{student.name} {student.last_name}'

        try:
            file = await bot.get_file(video_id)
            file_path = file.file_path

            directory = "application/media/video"
            if not os.path.exists(directory):
                os.makedirs(directory)

            timestamp = datetime.datetime.now().strftime("%d_%m_%Y_%H-%M-%S")
            filename = f"{directory}/{teacher_id}_{student_id}_{full_name}_{timestamp}_video.mp4"

            await bot.download_file(file_path, filename)
            await callback.message.answer("Домашнее задание (видео) успешно отправлено!")
            await state.clear()
        except TelegramBadRequest as e:
            if "file is too big" in str(e):
                await callback.message.edit_text(text='''
                😔Извините, ваше видео слишком много весит (максимум 50 МБ)!\n\n
                Попробуйте начать заново, выбрав отправку в виде ссылки.\n\n
                Или отправьте другое видео, меньшего размера.
                ''', reply_markup=kb.inline_keyboard_error_video)
            else:
                await callback.message.answer("Произошла ошибка при отправке видео.")
    elif call_data == 'deo_change':
        await callback.message.answer("Отлично, отправьте свое домашнее задание ещё раз.")

    await callback.answer()


def format_text(text, line_length=80):
    lines = []
    while text:
        if len(text) > line_length:
            space_index = text.rfind(' ', 0, line_length)
            if space_index == -1:
                space_index = line_length
            lines.append(text[:space_index])
            text = text[space_index:].lstrip()
        else:
            lines.append(text)
            break
    return '\n'.join(lines)


def find_links(text):
    url_regex = r'https?://[^\s]+'
    return re.findall(url_regex, text)


@router.message(F.text, HomeworkState.WaitingForTextAndLinks)
async def receive_homework_text(message: Message, state: FSMContext):
    tg_id = message.from_user.id

    async with async_session() as session:
        student = await session.scalar(select(Student).where(Student.tg_id == tg_id))
        if not student:
            await message.answer("Студент не найден в базе данных.")
            return
        student_id = student.id

    data = await state.get_data()
    teacher_id = data.get('teacher_id')

    await state.update_data(text=message.text, student_id=student_id, teacher_id=teacher_id)
    await message.answer(text="Всё верно? Окончательно отправить?", reply_markup=kb.confirmation_text)


@router.callback_query(F.data.in_(['te_confirm', 'xt_change']), HomeworkState.WaitingForTextAndLinks)
async def confirm_homework_text(callback: CallbackQuery, state: FSMContext):
    call_data = callback.data
    data = await state.get_data()

    if call_data == 'te_confirm':
        text = data.get('text')
        student_id = data.get('student_id')
        teacher_id = data.get('teacher_id')

        async with async_session() as session:
            student = await session.scalar(select(Student).where(Student.id == student_id))
            if not student:
                await callback.message.answer("Произошла ошибка при поиске данных студента.")
                return

        full_name = f'{student.name} {student.last_name}'

        links = find_links(text)
        timestamp = datetime.datetime.now().strftime("%d_%m_%Y_%H-%M-%S")

        if links:
            directory_links = "application/media/links"
            if not os.path.exists(directory_links):
                os.makedirs(directory_links)

            filename_links = f"{directory_links}/{teacher_id}_{student_id}_{full_name}_{timestamp}_links.html"

            with open(filename_links, 'w', encoding='utf-8') as file:
                file.write('<html><body>\n')
                for link in links:
                    file.write(f'<a href="{link}">{link}</a><br>\n')
                file.write('</body></html>')

            response_message = "Домашнее задание (ссылка) успешно отправлено!"
        else:
            text_content = format_text(text)

            directory = "application/media/text"
            if not os.path.exists(directory):
                os.makedirs(directory)

            filename = f"{directory}/{teacher_id}_{student_id}_{full_name}_{timestamp}_text.txt"

            with open(filename, 'w', encoding='utf-8') as file:
                file.write(text_content)

            response_message = "Домашнее задание (текст) успешно отправлено!"

        await callback.message.answer(response_message)
        await state.clear()
    elif call_data == 'xt_change':
        await callback.message.answer("Отправьте домашнее задание ещё раз.")

    await callback.answer()


@router.message(F.video | F.text | F.document | F.sticker | F.voice | F.location | F.contact | F.poll,
                HomeworkState.WaitingForPhoto)
async def wrong_homework_type(message: Message):
    await message.answer("Вы выбрали не тот тип домашнего задания (ожидалось фото). Попробуйте еще раз.")


@router.message(F.photo | F.text | F.document | F.sticker | F.voice | F.location | F.contact | F.poll,
                HomeworkState.WaitingForVideo)
async def wrong_type_for_video(message: Message):
    await message.answer("Вы выбрали не тот тип домашнего задания (ожидалось видео). Попробуйте еще раз.")


@router.message(F.photo | F.video | F.document | F.sticker | F.voice | F.location | F.contact | F.poll,
                HomeworkState.WaitingForTextAndLinks)
async def wrong_type_for_text_and_links(message: Message):
    await message.answer("Вы выбрали не тот тип домашнего задания (ожидался текст или ссылка). Попробуйте еще раз.")
