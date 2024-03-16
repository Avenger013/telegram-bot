import os
import re
import datetime

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from aiogram.exceptions import TelegramBadRequest

from application.states import HomeworkState, HomeworkState2
from application.database.models import Student, async_session
from application.database.requests import get_student

import application.keyboard as kb

router = Router(name=__name__)


async def info_homework(callback: CallbackQuery, reply_markup):
    homework_text = (
        "<b>✉️ Отправка ДЗ</b>\n\n"
        "Есть 3 варианта на выбор:\n\n"
        "📨Отправить выполненное ДЗ\n"
        "├ Данное домашнее задание назначил ваш преподаватель\n"
        "├ Дз можно отправлять в виде: <b>фото</b>, <b>видео</b>, <b>текста</b>, <b>голосового</b> или <b>ссылки</b>\n"
        "├ За его выполнение вы получите <b>+3 балла</b>, после проверки преподавателем\n\n"
        "📆Отправить еженедельное задание\n"
        "├ Данное задание автоматически выставляется всем ученикам раз в неделю\n"
        "├ Задания для учеников, обучающихся только вокалу, только гитаре или сразу вокалу и гитаре, будут отличаться\n"
        "├ За это задание можно получить баллы, только при отправки в текущую неделю (до воскресенья включительно)\n"
        "├ После истечения срока, задание поменяется\n"
        "├ За его выполнение вы получите <b>+1 балл</b>, после проверки преподавателем\n\n"
        "📹Отправить видео с полной версией песни в своем исполнении\n"
        "├ Песню выбираете любую, по своему желанию\n"
        "├ Можно отправлять максимум 2 раза в месяц\n"
        "├ За выполнение вы получите <b>+2 балла</b>, после просмотра преподавателем"
    )
    await callback.message.edit_text(text=homework_text, parse_mode='HTML', reply_markup=reply_markup)


@router.message(F.text == '✉️ Отправка ДЗ')
@router.message(Command('homework'))
async def submitting_homework(message: Message):
    tg_id = message.from_user.id
    async with async_session() as session:
        student = await get_student(session, tg_id)
        if student:
            homework_text = (
                "<b>✉️ Отправка ДЗ</b>\n\n"
                "Есть 3 варианта на выбор:\n\n"
                "📨Отправить выполненное ДЗ\n"
                "├ Данное домашнее задание назначил ваш преподаватель\n"
                "├ Дз можно отправлять в виде: <b>фото</b>, <b>видео</b>, <b>текста</b>, <b>голосового</b> или <b>ссылки</b>\n"
                "├ За его выполнение вы получите <b>+3 балла</b>, после проверки преподавателем\n\n"
                "📆Отправить еженедельное задание\n"
                "├ Данное задание автоматически выставляется всем ученикам раз в неделю\n"
                "├ Задания для учеников, обучающихся только вокалу, только гитаре или сразу вокалу и гитаре, будут отличаться\n"
                "├ За это задание можно получить баллы, только при отправки в текущую неделю (до воскресенья включительно)\n"
                "├ После истечения срока, задание поменяется\n"
                "├ За его выполнение вы получите <b>+1 балл</b>, после проверки преподавателем\n\n"
                "📹Отправить видео с полной версией песни в своем исполнении\n"
                "├ Песню выбираете любую, по своему желанию\n"
                "├ Можно отправлять максимум 2 раза в месяц\n"
                "├ За выполнение вы получите <b>+2 балла</b>, после просмотра преподавателем"
            )
            await message.answer(text=homework_text, parse_mode='HTML', reply_markup=kb.inline_homework1)
        else:
            await message.answer(
                text=f'{message.from_user.first_name}, это ваш первый вход. \nПожалуйста, пройдите быструю регистрацию.',
                reply_markup=kb.registration
            )


@router.callback_query(F.data.startswith('cancel'))
async def call_cancels(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await info_homework(callback, reply_markup=kb.inline_homework1)


@router.callback_query(F.data.startswith('send'))
async def call_submitting(callback: CallbackQuery):
    await info_homework(callback, reply_markup=kb.inline_homework)


@router.callback_query(F.data.startswith('dz_send'))
async def call_submitting_homework(callback: CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id
    await callback.message.edit_text(text='Выберите преподавателя, которому вы хотите отправить домашнее задание:',
                                     reply_markup=await kb.choice_teacher(tg_id))
    await state.set_state(HomeworkState.ChoiceTeacher)


@router.callback_query(F.data.startswith('1_canceled'))
async def call_submitting_homework(callback: CallbackQuery, state: FSMContext):
    await state.clear()
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
    await callback.message.edit_text(text='😁Отлично, теперь пришлите фото вашего домашнего задания!',
                                     reply_markup=kb.tree_can_send)
    await state.set_state(HomeworkState.WaitingForPhoto)


@router.callback_query(F.data.startswith('v_v'), HomeworkState.ChoosingDZType)
async def dz_type_video(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='😁Отлично, теперь пришлите видео вашего домашнего задания!',
                                     reply_markup=kb.tree_can_send)
    await state.set_state(HomeworkState.WaitingForVideo)


@router.callback_query(F.data.startswith('t_l'), HomeworkState.ChoosingDZType)
async def dz_type_text_link(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text='😁Отлично, теперь напишите текст вашего домашнего задания или скиньте ссылку!',
        reply_markup=kb.tree_can_send)
    await state.set_state(HomeworkState.WaitingForTextAndLinks)


@router.callback_query(F.data.startswith('o_i'), HomeworkState.ChoosingDZType)
async def dz_type_text_link(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='😁Отлично, теперь запишите голосовое сообщение и отправьте в чат!',
                                     reply_markup=kb.tree_can_send)
    await state.set_state(HomeworkState.WaitingForVoice)


@router.message(F.photo, HomeworkState.WaitingForPhoto)
async def receive_homework_photo(message: Message, state: FSMContext):
    tg_id = message.from_user.id

    state_data = await state.get_data()
    current_media_group_id = state_data.get('current_media_group_id')

    if message.media_group_id and message.media_group_id == current_media_group_id:
        return

    if message.media_group_id:
        await state.update_data(current_media_group_id=message.media_group_id)
        await message.answer(text="🚫Пожалуйста, отправьте только одно фото, попробуйте еще раз!",
                             reply_markup=kb.tree_can_send)
        return

    async with async_session() as session:
        student = await session.scalar(select(Student).where(Student.tg_id == tg_id))
        if not student:
            await message.answer("🚫Студент не найден в базе данных.")
            return
        student_id = student.id

    data = await state.get_data()
    teacher_id = data.get('teacher_id')

    photo_id = message.photo[-1].file_id

    await state.update_data(photo_id=photo_id, student_id=student_id, teacher_id=teacher_id)
    await message.answer(text="🧐Всё верно? Окончательно отправить?", reply_markup=kb.confirmation)


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
                await callback.message.answer("🚫Произошла ошибка при поиске данных студента.")
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
        await callback.message.answer(text="✅Домашнее задание (фото) успешно отправлено!", reply_markup=kb.menu)
        await state.clear()
    elif call_data == 'change':
        await callback.message.answer(text="😌Отлично, отправьте свое домашнее задание ещё раз.",
                                      reply_markup=kb.tree_can_send)

    await callback.answer()


@router.message(F.video, HomeworkState.WaitingForVideo)
async def receive_homework_video(message: Message, state: FSMContext):
    tg_id = message.from_user.id

    async with async_session() as session:
        student = await session.scalar(select(Student).where(Student.tg_id == tg_id))
        if not student:
            await message.answer("🚫Студент не найден в базе данных.")
            return
        student_id = student.id

    data = await state.get_data()
    teacher_id = data.get('teacher_id')

    video_id = message.video.file_id

    await state.update_data(video_id=video_id, student_id=student_id, teacher_id=teacher_id)
    await message.answer(text="🧐Всё верно? Окончательно отправить?", reply_markup=kb.confirmation_video)


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
                await callback.message.answer("🚫Произошла ошибка при поиске данных студента.")
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
            await callback.message.answer(text="✅Домашнее задание (видео) успешно отправлено!", reply_markup=kb.menu)
            await state.clear()
        except TelegramBadRequest as e:
            if "file is too big" in str(e):
                text = (
                    "<b>✉️Ошибка!</b>\n\n"
                    "😔Извините, ваше видео слишком много весит (максимум 50 МБ)!\n"
                    "├ Попробуйте начать заново, выбрав отправку в виде ссылки.\n"
                    "├ Или отправьте другое видео, меньшего размера."
                )
                await callback.message.edit_text(text=text, reply_markup=kb.inline_keyboard_error_video)
            else:
                await callback.message.answer(text="😔Произошла ошибка при отправке видео.", reply_markup=kb.menu1)
    elif call_data == 'deo_change':
        await callback.message.answer(text="😌Отлично, отправьте свое домашнее задание ещё раз.",
                                      reply_markup=kb.tree_can_send)

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
    await message.answer(text="🧐Всё верно? Окончательно отправить?", reply_markup=kb.confirmation_text)


async def save_homework_with_links(directory_links, filename_links, links):
    if not os.path.exists(directory_links):
        os.makedirs(directory_links)

    with open(filename_links, 'w', encoding='utf-8') as file:
        file.write('<html><body>\n')
        for link in links:
            file.write(f'<a href="{link}">{link}</a><br>\n')
        file.write('</body></html>')


async def save_homework_text(directory, filename, text_content):
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(filename, 'w', encoding='utf-8') as file:
        file.write(text_content)


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
        timestamp = datetime.datetime.now().strftime("%d_%m_%Y_%H-%M-%S")
        links = find_links(text)

        if links:
            directory_links = "application/media/links"
            filename_links = f"{directory_links}/{teacher_id}_{student_id}_{full_name}_{timestamp}_links.html"
            await save_homework_with_links(directory_links, filename_links, links)
            response_message = "✅Домашнее задание (ссылка) успешно отправлено!"
        else:
            text_content = format_text(text)
            directory = "application/media/text"
            filename = f"{directory}/{teacher_id}_{student_id}_{full_name}_{timestamp}_text.txt"
            await save_homework_text(directory, filename, text_content)
            response_message = "✅Домашнее задание (текст) успешно отправлено!"

        await callback.message.answer(text=response_message, reply_markup=kb.menu)
    elif call_data == 'xt_change':
        await callback.message.answer(text="😌Отлично, отправьте домашнее задание ещё раз.",
                                      reply_markup=kb.tree_can_send)

    await callback.answer()
    await state.clear()


@router.message(F.voice, HomeworkState.WaitingForVoice)
async def receive_homework_voice(message: Message, state: FSMContext):
    tg_id = message.from_user.id

    async with async_session() as session:
        student = await session.scalar(select(Student).where(Student.tg_id == tg_id))
        if not student:
            await message.answer("Студент не найден в базе данных.")
            return
        student_id = student.id

    data = await state.get_data()
    teacher_id = data.get('teacher_id')

    voice_id = message.voice.file_id

    await state.update_data(voice_id=voice_id, student_id=student_id, teacher_id=teacher_id)
    await message.answer(text="🧐Всё верно? Окончательно отправить?", reply_markup=kb.confirmation_voice)


@router.callback_query(F.data.in_(['voi_confirm', 'ce_change']), HomeworkState.WaitingForVoice)
async def confirm_homework_voice(callback: CallbackQuery, state: FSMContext, bot: Bot):
    call_data = callback.data

    if call_data == 'voi_confirm':
        data = await state.get_data()
        voice_id = data['voice_id']
        student_id = data['student_id']
        teacher_id = data['teacher_id']

        async with async_session() as session:
            student = await session.scalar(select(Student).where(Student.id == student_id))
            if not student:
                await callback.message.answer("Произошла ошибка при поиске данных студента.")
                return

        full_name = f'{student.name} {student.last_name}'

        file = await bot.get_file(voice_id)
        file_path = file.file_path

        directory = "application/media/voice"
        if not os.path.exists(directory):
            os.makedirs(directory)

        timestamp = datetime.datetime.now().strftime("%d_%m_%Y_%H-%M-%S")
        filename = f"{directory}/{teacher_id}_{student_id}_{full_name}_{timestamp}_voice.ogg"

        await bot.download_file(file_path, filename)
        await callback.message.answer(text="✅Домашнее задание (голосовое сообщение) успешно отправлено!",
                                      reply_markup=kb.menu)
        await state.clear()
    elif call_data == 'ce_change':
        await callback.message.answer(text="😌Отлично, отправьте ваше домашнее задание ещё раз.",
                                      reply_markup=kb.tree_can_send)
    await callback.answer()


@router.callback_query(F.data.startswith('vid_send'))
async def call_submitting_homework_2(callback: CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id
    await callback.message.edit_text(text='Выберите преподавателя, которому вы хотите отправить домашнее задание:',
                                     reply_markup=await kb.choice_teacher(tg_id))
    await state.set_state(HomeworkState2.ChoiceTeacher2)


@router.callback_query(F.data.startswith('2_canceled'))
async def call_submitting_homework_2(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    tg_id = callback.from_user.id
    await callback.message.edit_text(text='Выберите преподавателя, которому вы хотите отправить домашнее задание:',
                                     reply_markup=await kb.choice_teacher(tg_id))
    await state.set_state(HomeworkState2.ChoiceTeacher2)


@router.callback_query(F.data.startswith('choice_'), HomeworkState2.ChoiceTeacher2)
async def teacher_selected_for_homework_2(callback: CallbackQuery, state: FSMContext):
    teacher_id = callback.data.split('_')[1]
    await state.update_data(teacher_id=teacher_id)
    await callback.message.edit_text(text='В каком виде вы хотите отправить видео?', reply_markup=kb.dz_type_2)
    await state.set_state(HomeworkState2.ChoosingDZType2)


@router.callback_query(F.data.startswith('vvv'), HomeworkState2.ChoosingDZType2)
async def dz_type_video_2(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text='😁Отлично, теперь пришлите видео вашего домашнего задания!',
                                     reply_markup=kb.tree_can_send)
    await state.set_state(HomeworkState2.WaitingForVideo2)


@router.callback_query(F.data.startswith('lll'), HomeworkState2.ChoosingDZType2)
async def dz_type_links_2(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text='😁Отлично, теперь пришлите ссылку, по которой можно будет ознакомиться с вашим видео!',
        reply_markup=kb.tree_can_send)
    await state.set_state(HomeworkState2.WaitingForLinks2)


@router.message(F.video, HomeworkState2.WaitingForVideo2)
async def receive_homework_video_2(message: Message, state: FSMContext):
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
    await message.answer(text="🧐Всё верно? Окончательно отправить?", reply_markup=kb.confirmation_video_2)


@router.callback_query(F.data.in_(['iv_2_confirm', 'oed_2_change']), HomeworkState2.WaitingForVideo2)
async def confirm_homework_video_2(callback: CallbackQuery, state: FSMContext, bot: Bot):
    call_data = callback.data

    if call_data == 'iv_2_confirm':
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
            await callback.message.answer(text="✅Видео успешно отправлено!", reply_markup=kb.menu)
            await state.clear()
        except TelegramBadRequest as e:
            if "file is too big" in str(e):
                text = (
                    "<b>✉️Ошибка!</b>\n\n"
                    "😔Извините, ваше видео слишком много весит (максимум 50 МБ)!\n"
                    "├ Попробуйте начать заново, выбрав отправку в виде ссылки.\n"
                    "├ Или отправьте другое видео, меньшего размера."
                )
                await callback.message.edit_text(text=text, reply_markup=kb.inline_keyboard_error_video)
            else:
                await callback.message.answer(text="😔Произошла ошибка при отправке видео.", reply_markup=kb.menu1)
    elif call_data == 'oed_2_change':
        await callback.message.answer(text="😌Отлично, отправьте свое домашнее задание ещё раз.",
                                      reply_markup=kb.tree_can_send)

    await callback.answer()


@router.message(F.text, HomeworkState2.WaitingForLinks2)
async def receive_homework_text_2(message: Message, state: FSMContext):
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
    await message.answer(text="🧐Всё верно? Окончательно отправить?", reply_markup=kb.confirmation_text_2)


@router.callback_query(F.data.in_(['et_2_confirm', 'tx_2_change']), HomeworkState2.WaitingForLinks2)
async def confirm_homework_text_2(callback: CallbackQuery, state: FSMContext):
    call_data = callback.data
    data = await state.get_data()

    if call_data == 'et_2_confirm':
        text = data.get('text')
        student_id = data.get('student_id')
        teacher_id = data.get('teacher_id')

        async with async_session() as session:
            student = await session.scalar(select(Student).where(Student.id == student_id))
            if not student:
                await callback.message.answer("Произошла ошибка при поиске данных студента.")
                return

        full_name = f'{student.name} {student.last_name}'
        timestamp = datetime.datetime.now().strftime("%d_%m_%Y_%H-%M-%S")
        links = find_links(text)

        if links:
            directory_links = "application/media/links"
            filename_links = f"{directory_links}/{teacher_id}_{student_id}_{full_name}_{timestamp}_links.html"
            await save_homework_with_links(directory_links, filename_links, links)
            response_message = "✅Домашнее задание (ссылка) успешно отправлено!"
        else:
            response_message = "❎Вы отправили текст, а нужно ссылку!"
        await callback.message.answer(text=response_message, reply_markup=kb.menu)
    elif call_data == 'tx_2_change':
        await callback.message.answer(text="😌Отлично, отправьте домашнее задание ещё раз.",
                                      reply_markup=kb.tree_can_send)

    await callback.answer()
    await state.clear()


@router.message(F.video | F.text | F.document | F.sticker | F.voice | F.location | F.contact | F.poll,
                HomeworkState.WaitingForPhoto)
async def wrong_homework_type(message: Message):
    await message.answer(text="🥺Вы выбрали не тот тип домашнего задания (ожидалось фото). Попробуйте еще раз.",
                         reply_markup=kb.tree_can_send)


@router.message(F.photo | F.text | F.document | F.sticker | F.voice | F.location | F.contact | F.poll,
                HomeworkState.WaitingForVideo)
async def wrong_type_for_video(message: Message):
    await message.answer(text="🥺Вы выбрали не тот тип домашнего задания (ожидалось видео). Попробуйте еще раз.",
                         reply_markup=kb.tree_can_send)


@router.message(F.photo | F.video | F.document | F.sticker | F.voice | F.location | F.contact | F.poll,
                HomeworkState.WaitingForTextAndLinks)
async def wrong_type_for_text_and_links(message: Message):
    await message.answer(
        text="🥺Вы выбрали не тот тип домашнего задания (ожидался текст или ссылка). Попробуйте еще раз.",
        reply_markup=kb.tree_can_send)


@router.message(F.photo | F.video | F.text | F.document | F.sticker | F.location | F.contact | F.poll,
                HomeworkState.WaitingForVoice)
async def wrong_type_for_voice(message: Message):
    await message.answer(text="🥺Вы выбрали не тот тип домашнего задания (ожидалось голосовое). Попробуйте еще раз.",
                         reply_markup=kb.tree_can_send)


@router.message(F.photo | F.text | F.document | F.sticker | F.voice | F.location | F.contact | F.poll,
                HomeworkState2.WaitingForVideo2)
async def wrong_type_for_video_2(message: Message):
    await message.answer(text="🥺Вы отправили не тот тип сообщения (ожидалось видео). Попробуйте еще раз.",
                         reply_markup=kb.tree_can_send)


@router.message(F.photo | F.video | F.document | F.sticker | F.voice | F.location | F.contact | F.poll,
                HomeworkState2.WaitingForLinks2)
async def wrong_type_for_links_2(message: Message):
    await message.answer(text="🥺Вы отправили не тот тип сообщения (ожидалась ссылка). Попробуйте еще раз.",
                         reply_markup=kb.tree_can_send)
