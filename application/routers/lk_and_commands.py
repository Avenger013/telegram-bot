from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from application.states import Gifts, Systems
from application.database.models import PointsHistory, async_session
from application.database.requests import get_student_info, get_top_students, get_leader_of_the_month, get_money, \
    get_gifts, get_student, get_gift_by_id, update_student_points, get_support, get_info, get_task_by_id

import application.keyboard as kb

router = Router(name=__name__)


@router.message(F.text == '🔐 Личный кабинет')
@router.message(Command('profile'))
async def personal_area(message: Message):
    tg_id = message.from_user.id
    async with async_session() as session:
        student, teachers = await get_student_info(session, tg_id)

        if student:
            student_name = student.name
            student_last_name = student.last_name
            phone = student.phone
            specialisation_student = student.specialisation_student
            point = student.point
            teacher_word = "Преподаватель" if len(teachers) == 1 else "Преподаватели"
            teachers_info = "Не указан" if not teachers else ", ".join([f"{t.name} {t.last_name}" for t in teachers])

            response = "🔐 <b>Личный кабинет</b>\n\n"
            response += f"👤Пользователь: {student_name} {student_last_name}\n"
            response += f"📞Номер телефона: {phone}\n"

            if specialisation_student == "Вокал":
                response += f"🎤Специализация: {specialisation_student}\n"
            elif specialisation_student == "Гитара":
                response += f"🎸Специализация: {specialisation_student}\n"
            else:
                response += f"🎤/🎸Специализация: {specialisation_student}\n"

            response += f"🎓{teacher_word}: {teachers_info}\n"
            response += f"\n🧮Количество баллов: {point}\n"
            response += "\nСистему получения баллов и то, на что их можно обменять, вы найдете в разделе 🎁Монетизация"

            await message.answer(response, parse_mode='HTML', reply_markup=kb.inline_keyboard_personal_area)
            await message.answer(text='', reply_markup=kb.menu)
        else:
            await message.answer(
                text=f'{message.from_user.first_name}, это ваш первый вход. \nПожалуйста, пройдите быструю регистрацию.',
                reply_markup=kb.registration
            )


@router.callback_query(F.data.startswith('back'))
async def call_back(callback: CallbackQuery):
    tg_id = callback.from_user.id
    async with async_session() as session:
        student, teachers = await get_student_info(session, tg_id)

        if student:
            student_name = student.name
            student_last_name = student.last_name
            phone = student.phone
            specialisation_student = student.specialisation_student
            point = student.point
            teacher_word = "Преподаватель" if len(teachers) == 1 else "Преподаватели"
            teachers_info = "Не указан" if not teachers else ", ".join([f"{t.name} {t.last_name}" for t in teachers])

            response = "🔐 <b>Личный кабинет</b>\n\n"
            response += f"👤Пользователь: {student_name} {student_last_name}\n"
            response += f"📞Номер телефона: {phone}\n"

            if specialisation_student == "Вокал":
                response += f"🎤Специализация: {specialisation_student}\n"
            elif specialisation_student == "Гитара":
                response += f"🎸Специализация: {specialisation_student}\n"
            else:
                response += f"🎤/🎸Специализация: {specialisation_student}\n"

            response += f"🎓{teacher_word}: {teachers_info}\n"
            response += f"\n🧮Количество баллов: {point}\n"
            response += "\nСистему получения баллов и то, на что их можно обменять, вы найдете в разделе 🎁Монетизация"

            await callback.message.edit_text(response, parse_mode='HTML', reply_markup=kb.inline_keyboard_personal_area)
            await callback.message.answer(text='', reply_markup=kb.menu)
        else:
            await callback.message.edit_text(
                text=f'{callback.from_user.first_name}, это ваш первый вход. \nПожалуйста, пройдите быструю регистрацию.',
                reply_markup=kb.registration
            )


def get_points_word(points):
    if points % 10 == 1 and points % 100 != 11:
        return "балл"
    elif 2 <= points % 10 <= 4 and (points % 100 < 10 or points % 100 >= 20):
        return "балла"
    else:
        return "баллов"


@router.message(F.text == '📊 ТОП учеников')
@router.message(Command('top'))
async def top_students(message: Message):
    top_students_list = await get_top_students(10)
    if top_students_list:
        response_message = "🏆 ТОП учеников по баллам:\n\n"
        for i, student in enumerate(top_students_list, start=1):
            points_word = get_points_word(student.point)
            response_message += f"{i}. {student.name} {student.last_name} - {student.point} {points_word}\n"
    else:
        response_message = "Учеников пока нет."

    await message.answer(response_message, reply_markup=kb.back3)


@router.callback_query(F.data.startswith('viewing'))
async def call_top_students(callback: CallbackQuery):
    top_students_list = await get_top_students(10)
    if top_students_list:
        response_message = "🏆 ТОП учеников по баллам:\n\n"
        for i, student in enumerate(top_students_list, start=1):
            points_word = get_points_word(student.point)
            response_message += f"{i}. {student.name} {student.last_name} - {student.point} {points_word}\n"
    else:
        response_message = "Учеников пока нет."

    await callback.message.edit_text(response_message, reply_markup=kb.back2)


@router.message(F.text == '📈 Лидер месяца')
@router.message(Command('leader'))
async def leader_of_the_month(message: Message):
    current_year = datetime.now().year
    current_month = datetime.now().month

    leader_info = await get_leader_of_the_month(current_year, current_month)

    if leader_info:
        response_message = (
            "<b>🏆 Лидер месяца:</b>\n\n"
            f"<b>🌟 {leader_info['name']} {leader_info['last_name']} 🌟</b>\n\n"
            f"Количество заработанных за этот месяц баллов: <b>{leader_info['total_points']}</b>"
        )
    else:
        response_message = "<b>В этом месяце еще нет лидера.</b>"

    await message.answer(response_message, reply_markup=kb.back3, parse_mode='HTML')


@router.callback_query(F.data.startswith('lead'))
async def call_leader_of_the_month(callback: CallbackQuery):
    current_year = datetime.now().year
    current_month = datetime.now().month

    leader_info = await get_leader_of_the_month(current_year, current_month)

    if leader_info:
        response_message = (
            "<b>🏆 Лидер месяца:</b>\n\n"
            f"<b>🌟 {leader_info['name']} {leader_info['last_name']} 🌟</b>\n\n"
            f"Количество заработанных за этот месяц баллов: <b>{leader_info['total_points']}</b>"
        )
    else:
        response_message = "<b>В этом месяце еще нет лидера.</b>"

    await callback.message.edit_text(response_message, reply_markup=kb.back2, parse_mode='HTML')


@router.message(F.text == '🎁 Монетизация')
@router.message(Command('monetization'))
async def monetization_list(message: Message):
    monetization_items = await get_money()
    response_text = "<b>Получение баллов:</b>\n"

    for item in monetization_items:
        points_word = get_points_word(item.number_of_points)
        response_text += f"        {item.task} - {item.number_of_points} {points_word}\n"

    gifts = await get_gifts()
    response_text += "\n\n<b>Обмен баллов:</b>\n"

    for gift in gifts:
        points_word = get_points_word(gift.number_of_points)
        response_text += f"        {gift.present} - {gift.number_of_points} {points_word}\n"

    await message.answer(text=response_text, reply_markup=kb.back4, parse_mode='HTML')


async def call_monetization_list_info(callback: CallbackQuery, reply_markup):
    monetization_items = await get_money()
    response_text = "<b>Получение баллов:</b>\n"

    for item in monetization_items:
        points_word = get_points_word(item.number_of_points)
        response_text += f"        {item.task} - {item.number_of_points} {points_word}\n"

    gifts = await get_gifts()
    response_text += "\n\n<b>Обмен баллов:</b>\n"

    for gift in gifts:
        points_word = get_points_word(gift.number_of_points)
        response_text += f"        {gift.present} - {gift.number_of_points} {points_word}\n"

    await callback.message.edit_text(text=response_text, parse_mode='HTML', reply_markup=reply_markup)


@router.callback_query(F.data.startswith('comeback'))
async def call_comeback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await call_monetization_list_info(callback, reply_markup=kb.back4)


@router.callback_query(F.data.startswith('money'))
async def call_monetization_list(callback: CallbackQuery):
    await call_monetization_list_info(callback, reply_markup=kb.back)


@router.callback_query(F.data.startswith('buy'))
async def exchange_points(callback: CallbackQuery, state: FSMContext):
    new_markup = await kb.choosing_a_gift()
    await callback.message.edit_text(
        text="Выберите то, что хотите получить (можно выбрать 1 или несколько позиций сразу):",
        reply_markup=new_markup)
    await state.set_state(Gifts.Gift)


@router.callback_query(F.data.startswith('gifts_'), Gifts.Gift)
async def gift_selected(callback: CallbackQuery, state: FSMContext):
    gift_id = int(callback.data.split('_')[1])
    data = await state.get_data()
    selected_gifts = data.get('selected_gifts', [])
    if gift_id in selected_gifts:
        selected_gifts.remove(gift_id)
        await callback.answer("Подарок удален из списка выбранных.")
    else:
        selected_gifts.append(gift_id)
        await callback.answer("Подарок добавлен в список выбранных.")
    await state.update_data(selected_gifts=selected_gifts)

    new_markup = await kb.choosing_a_gift(selected_gifts)
    await callback.message.edit_reply_markup(reply_markup=new_markup)


async def calculate_total_points(selected_gift_ids):
    total_points_needed = 0
    gifts_descriptions = []

    for gift_id in selected_gift_ids:
        gift = await get_gift_by_id(int(gift_id))
        if gift:
            total_points_needed += gift.number_of_points
            gifts_descriptions.append(f"{gift.present} ({gift.number_of_points} баллов)")

    return total_points_needed, gifts_descriptions


@router.callback_query(F.data == 'selecting_gifts')
async def selecting_gifts(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_gift_ids = data.get('selected_gifts', [])
    tg_id = callback.from_user.id
    async with async_session() as session:
        student = await get_student(session, tg_id)
        if student:
            total_points_needed, gifts_descriptions = await calculate_total_points(selected_gift_ids)
            if student.point < total_points_needed:
                await callback.message.edit_text("Извините, у вас недостаточно очков.")
                await callback.message.answer(text="Хотите выбрать подарки заново или завершить выбор?",
                                              reply_markup=kb.choice_keyboard)
            else:
                student.point -= total_points_needed
                await update_student_points(session, student.id, student.point)
                await session.commit()
                if len(gifts_descriptions) > 1:
                    gifts_text = "Баллы были успешно списаны, вы получили:\n" + ";\n".join(gifts_descriptions) + "."
                else:
                    gifts_text = "Баллы были успешно списаны, вы получаете:\n" + "; ".join(gifts_descriptions) + "."

                await callback.message.edit_text(
                    text=gifts_text + "\n\nОбратитесь к администратору для получения.", reply_markup=kb.back3
                )
        else:
            await callback.message.answer("Профиль студента не найден.")
        await state.clear()


@router.callback_query(F.data.startswith('select_gifts_again'))
async def exchange_points(callback: CallbackQuery, state: FSMContext):
    new_markup = await kb.choosing_a_gift()
    await callback.message.edit_text(
        text="Выберите то, что хотите получить (можно выбрать 1 или несколько позиций сразу):",
        reply_markup=new_markup)
    await state.set_state(Gifts.Gift)


@router.callback_query(F.data.startswith('finish_selection'))
async def call_monetization_list(callback: CallbackQuery):
    # await state.clear()
    await call_monetization_list_info(callback, reply_markup=kb.back4)


@router.message(F.text == '✍🏼 Поддержка')
@router.message(Command('support'))
async def support_service(message: Message):
    support_info = await get_support()
    response_text = "✍🏼 <b>Служба поддержки</b>\n\n"

    for info in support_info:
        response_text += f"{info.instruction_support} 🤝🏼.\n"

    await message.answer(text=response_text, reply_markup=kb.back3, parse_mode='HTML')


@router.callback_query(F.data.startswith('supp'))
async def call_support_service(callback: CallbackQuery):
    support_info = await get_support()
    response_text = "✍🏼 <b>Служба поддержки</b>\n\n"

    for info in support_info:
        response_text += f"{info.instruction_support} 🤝🏼.\n"

    await callback.message.edit_text(text=response_text, reply_markup=kb.back2, parse_mode='HTML')


@router.message(F.text == '❔ О боте')
@router.message(Command('info'))
async def information_bot(message: Message):
    bot_info = await get_info()
    response_text = "❔ <b>Информация о боте</b>\n\n"

    for info in bot_info:
        response_text += f"{info.instruction}\n\n"

    await message.answer(text=response_text, reply_markup=kb.back3, parse_mode='HTML')


@router.callback_query(F.data.startswith('the_info'))
async def call_information_bot(callback: CallbackQuery):
    bot_info = await get_info()
    response_text = "❔ <b>Информация о боте</b>\n\n"

    for info in bot_info:
        response_text += f"{info.instruction}\n\n"

    await callback.message.edit_text(text=response_text, reply_markup=kb.back2, parse_mode='HTML')


@router.callback_query(F.data.startswith('receiving'))
async def getting_points(callback: CallbackQuery, state: FSMContext):
    monetization_items = await get_money()
    new_markup = await kb.choosing_a_money()
    response_text = "<b>Получение баллов:</b>\n"

    for index, item in enumerate(monetization_items, start=1):
        points_word = get_points_word(item.number_of_points)
        response_text += f"        {index}) {item.task} - <b>{item.number_of_points}</b> {points_word}\n"

    response_text += (
        "\n\n🎁Выберите то, что вы сделали!\n"
        "├ Мы уведомим администратора и после проверки вам начисляться баллы!\n"
        "├ Можно выбрать 1 или несколько позиций сразу:"
    )

    await callback.message.edit_text(text=response_text, reply_markup=new_markup, parse_mode='HTML')
    await state.set_state(Systems.System)


@router.callback_query(F.data.startswith('6_monetization_'), Systems.System)
async def task_selected(callback: CallbackQuery, state: FSMContext):
    task_id = int(callback.data.split('_')[2])
    data = await state.get_data()
    selected_tasks = data.get('selected_tasks', [])

    if task_id in selected_tasks:
        selected_tasks.remove(task_id)
        await callback.answer("Позиция удалена из списка выбранных.")
    else:
        selected_tasks.append(task_id)
        await callback.answer("Позиция добавлена в список выбранных.")

    await state.update_data(selected_tasks=selected_tasks)

    new_markup = await kb.choosing_a_money(selected_tasks)
    await callback.message.edit_reply_markup(reply_markup=new_markup)


async def calculate_total_points_for_tasks(selected_task_ids):
    total_points = 0

    for task_id in selected_task_ids:
        task = await get_task_by_id(int(task_id))
        if task:
            total_points += task.number_of_points

    return total_points


@router.callback_query(F.data == 'on_selecting')
async def selecting_money(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_task_ids = data.get('selected_tasks', [])
    tg_id = callback.from_user.id

    if not selected_task_ids:
        await callback.answer("Вы не выбрали ни одной позиции.")
        return

    async with async_session() as session:
        student = await get_student(session, tg_id)
        if student:
            total_points_to_add = await calculate_total_points_for_tasks(selected_task_ids)

            new_points_history = PointsHistory(student_id=student.id, points_added=total_points_to_add,
                                               date_added=datetime.now())
            session.add(new_points_history)

            student.point += total_points_to_add
            await update_student_points(session, student.id, student.point)
            await session.refresh(student)
            await callback.message.answer(
                text=f"✅ Баллы успешно начислены!\nВаше текущее количество баллов: <b>{student.point}</b>",
                parse_mode='HTML', reply_markup=kb.menu)
        else:
            await callback.message.answer("Профиль студента не найден.")

    await state.clear()
