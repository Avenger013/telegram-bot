import phonenumbers

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select, update, delete

from application.states import RegistrationState, UpdateRegistrationState, UpdateParts
from application.database.models import Student, async_session, StudentTeacher
from application.database.requests import get_student_info, get_student

import application.keyboard as kb

router = Router(name=__name__)


@router.message(F.text == '🎒 Ученик')
async def choice_of_directional(message: Message, state: FSMContext):
    await register_student(message, state)


async def register_student(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    async with async_session() as session:
        student = await get_student(session, tg_id)
        if student:
            await message.answer(
                text='😁Вы уже зарегистрированы. \nПожалуйста, нажмите на одну из представленных ниже кнопок.',
                reply_markup=kb.menu
            )
        else:
            await message.answer(
                text=f'{message.from_user.first_name}, вы вошли под ролью ученика в первый раз. \nПожалуйста, пройдите быструю регистрацию.',
                reply_markup=kb.registration
            )


@router.callback_query(F.data.startswith('registration'))
async def register_students(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text='Введите ваш номер телефона (без +7 или 8 в начале):')
    await callback.answer('')
    await state.set_state(RegistrationState.EnterPhone)


@router.message(Command('registration'))
async def handle_register_students(message: Message, state: FSMContext):
    tg_id = message.from_user.id
    async with async_session() as session:
        student = await get_student(session, tg_id)
        if student:
            await message.answer(
                text='😁Вы уже зарегистрированы.🍾',
                reply_markup=kb.menu
            )
        else:
            await message.answer('Начало регистрации. \nПожалуйста, введите ваш номер телефона (без +7 или 8 в начале):')
            await state.set_state(RegistrationState.EnterPhone)


@router.message(RegistrationState.EnterPhone)
async def enter_last_name(message: Message, state: FSMContext):
    raw_phone = message.text.strip()

    if not raw_phone.isdigit() or len(raw_phone) != 10:
        await message.answer('''
            Неверный формат номера телефона. Пожалуйста, введите 10 цифр номера, без +7 или 8 в начале''')
        return

    formatted_phone = f"+7 ({raw_phone[:3]}) {raw_phone[3:6]}-{raw_phone[6:8]}-{raw_phone[8:]}"

    await state.update_data(phone=formatted_phone)
    await message.answer(text=f'Телефон {formatted_phone} сохранен! \nТеперь введите ваше имя:')
    await state.set_state(RegistrationState.EnterName)


@router.message(RegistrationState.EnterName)
async def enter_name(message: Message, state: FSMContext):
    name = message.text

    if not name.isalpha():
        await message.answer('Имя должно содержать только буквы. Пожалуйста, введите ваше имя еще раз:')
        return

    await state.update_data(name=name)
    await message.answer(f'Отлично, {name}! \nТеперь введите вашу фамилию:')
    await state.set_state(RegistrationState.EnterLastName)


@router.message(RegistrationState.EnterLastName)
async def enter_last_name(message: Message, state: FSMContext):
    last_name = message.text

    if not last_name.isalpha():
        await message.answer('Фамилия должна содержать только буквы. Пожалуйста, введите вашу фамилию еще раз:')
        return

    await state.update_data(last_name=last_name)
    await message.answer(text=f'Фамилия {last_name} сохранена! \nТеперь выберите ваше направление:',
                         reply_markup=kb.tool1)
    await state.set_state(RegistrationState.ChoiceSpecialisation)


@router.callback_query(F.data.in_(['vocal', 'guitar', 'vocal_guitar']), RegistrationState.ChoiceSpecialisation)
async def process_specialisation(callback_query: CallbackQuery, state: FSMContext):
    specialisation_mapping = {
        'vocal': 'Вокал',
        'guitar': 'Гитара',
        'vocal_guitar': 'Вокал и Гитара'
    }
    specialisation = specialisation_mapping[callback_query.data]
    await state.update_data(specialisation_student=specialisation)

    if specialisation == 'Вокал':
        reply_markup = await kb.teachers_choice_students_da_v()
    elif specialisation == 'Гитара':
        reply_markup = await kb.teachers_choice_students_da_g()
    else:
        reply_markup = await kb.teachers_choice_students_da()

    await callback_query.message.edit_text(
        text=f"Вы выбрали направление: {specialisation}. \nТеперь выберите своего преподавателя или преподавателей:",
        reply_markup=reply_markup
    )
    await state.set_state(RegistrationState.ChoiceIDTeacher)


@router.callback_query(F.data.startswith('select_teacher_'))
async def teacher_selected_students(callback: CallbackQuery, state: FSMContext):
    teacher_id = int(callback.data.split('_')[2])
    data = await state.get_data()
    selected_teachers = data.get('selected_teachers', [])
    if teacher_id in selected_teachers:
        selected_teachers.remove(teacher_id)  # Удаляем, если уже выбран
        await callback.answer("Преподаватель удален из списка выбранных.")
    else:
        selected_teachers.append(teacher_id)  # Добавляем, если еще не выбран
        await callback.answer("Преподаватель добавлен в список выбранных.")
    await state.update_data(selected_teachers=selected_teachers)

    # Обновляем клавиатуру, чтобы показать текущий выбор
    new_markup = await kb.teachers_choice_students_da(selected_teachers)
    await callback.message.edit_reply_markup(reply_markup=new_markup)


@router.callback_query(F.data.startswith('1select_teacher_'))
async def teacher_selected_students(callback: CallbackQuery, state: FSMContext):
    teacher_id = int(callback.data.split('_')[2])
    data = await state.get_data()
    selected_teachers = data.get('selected_teachers', [])
    if teacher_id in selected_teachers:
        selected_teachers.remove(teacher_id)
        await callback.answer("Преподаватель удален из списка выбранных.")
    else:
        selected_teachers.append(teacher_id)
        await callback.answer("Преподаватель добавлен в список выбранных.")
    await state.update_data(selected_teachers=selected_teachers)

    new_markup = await kb.teachers_choice_students_da_v(selected_teachers)
    await callback.message.edit_reply_markup(reply_markup=new_markup)


@router.callback_query(F.data.startswith('2select_teacher_'))
async def teacher_selected_students(callback: CallbackQuery, state: FSMContext):
    teacher_id = int(callback.data.split('_')[2])
    data = await state.get_data()
    selected_teachers = data.get('selected_teachers', [])
    if teacher_id in selected_teachers:
        selected_teachers.remove(teacher_id)
        await callback.answer("Преподаватель удален из списка выбранных.")
    else:
        selected_teachers.append(teacher_id)
        await callback.answer("Преподаватель добавлен в список выбранных.")
    await state.update_data(selected_teachers=selected_teachers)

    new_markup = await kb.teachers_choice_students_da_g(selected_teachers)
    await callback.message.edit_reply_markup(reply_markup=new_markup)


@router.callback_query(F.data.startswith('done_selecting_teachers'))
async def teacher_selected_students(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected_teachers = data.get('selected_teachers', [])
    tg_id = callback.from_user.id

    async with async_session() as session:
        student = await session.scalar(select(Student).filter_by(tg_id=tg_id))

        if student:
            if any(data.get(f'new_{field}') for field in ['name', 'last_name', 'phone', 'specialisation_student']):
                new_name = data.get('new_name', student.name)
                new_last_name = data.get('new_last_name', student.last_name)
                new_phone = data.get('new_phone', student.phone)
                new_specialisation_student = data.get('new_specialisation_student', student.specialisation_student)

                await session.execute(
                    update(Student)
                    .where(Student.tg_id == tg_id)
                    .values(
                        name=new_name,
                        last_name=new_last_name,
                        phone=new_phone,
                        specialisation_student=new_specialisation_student
                    )
                )
                message_text = 'Информация успешно обновлена!'
        else:
            student = Student(tg_id=tg_id, name=data.get('name'), last_name=data.get('last_name'),
                              phone=data.get('phone'),
                              specialisation_student=data.get('specialisation_student'), point=0)
            session.add(student)
            await session.flush()
            message_text = 'Регистрация успешно завершена, Спасибо!'

        await session.execute(delete(StudentTeacher).where(StudentTeacher.student_id == student.id))

        for teacher_id in selected_teachers:
            new_student_teacher = StudentTeacher(student_id=student.id, teacher_id=teacher_id)
            session.add(new_student_teacher)

        await session.commit()
        await callback.message.answer(text=message_text, reply_markup=kb.menu)
        await state.clear()


@router.callback_query(F.data.startswith('update_info'))
async def change_inline_keyboard(callback: CallbackQuery):
    tg_id = callback.from_user.id
    async with async_session() as session:
        student, teachers = await get_student_info(session, tg_id)

        if student:
            teacher_word = "Преподаватель" if len(teachers) == 1 else "Преподаватели"
            teachers_info = "Не указан" if not teachers else ", ".join([f"{t.name} {t.last_name}" for t in teachers])

            await callback.message.edit_text(text=f"<b>Текущая информация:</b>\n\n"
                                                  f"Имя (👤): {student.name}\n"
                                                  f"Фамилия (👤): {student.last_name}\n"
                                                  f"Телефон (📞): {student.phone}\n"
                                                  f"Направление (🎤/🎸): {student.specialisation_student}\n"
                                                  f"{teacher_word} (🎓): {teachers_info}\n"
                                                  "\nВыберите, что вы хотите изменить:",
                                             parse_mode="HTML", reply_markup=kb.updating_in_parts)


@router.callback_query(F.data.startswith('up_all'))
async def update_info(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новый номер телефона (без +7 или 8 в начале):")
    await state.set_state(UpdateRegistrationState.UpdatePhone)


@router.message(UpdateRegistrationState.UpdatePhone)
async def update_phone(message: Message, state: FSMContext):
    raw_phone = message.text.strip()

    if not raw_phone.isdigit() or len(raw_phone) != 10:
        await message.answer('''
            Неверный формат номера телефона. Пожалуйста, введите 10 цифр номера, без +7 или 8 в начале''')
        return

    new_phone = f"+7 ({raw_phone[:3]}) {raw_phone[3:6]}-{raw_phone[6:8]}-{raw_phone[8:]}"

    await state.update_data(new_phone=new_phone)
    await message.answer(text=f'Отлично! Новый телефон: {new_phone}!\nТеперь введите ваше новое имя:')
    await state.set_state(UpdateRegistrationState.UpdateName)


@router.message(UpdateRegistrationState.UpdateName)
async def update_name(message: Message, state: FSMContext):
    new_name = message.text

    if not new_name.isalpha():
        await message.answer('Имя должно содержать только буквы. Пожалуйста, введите ваше имя еще раз:')
        return

    await state.update_data(new_name=new_name)
    await message.answer(f'Отлично! Новое имя: {new_name}!\nВведите новую фамилию:')
    await state.set_state(UpdateRegistrationState.UpdateLastName)


@router.message(UpdateRegistrationState.UpdateLastName)
async def update_last_name(message: Message, state: FSMContext):
    new_last_name = message.text

    if not new_last_name.isalpha():
        await message.answer('Фамилия должна содержать только буквы. Пожалуйста, введите вашу фамилию еще раз:')
        return

    await state.update_data(new_last_name=new_last_name)
    await message.answer(text=f'Отлично! Новая фамилия: {new_last_name}!\nВберите новую специализацию:',
                         reply_markup=kb.tool2)
    await state.set_state(UpdateRegistrationState.UpdateChoiceSpecialisation)


@router.callback_query(F.data.in_(['new_vocal', 'new_guitar', 'new_vocal_guitar']),
                       UpdateRegistrationState.UpdateChoiceSpecialisation)
async def update_process_specialisation(callback_query: CallbackQuery, state: FSMContext):
    specialisation_mapping = {
        'new_vocal': 'Вокал',
        'new_guitar': 'Гитара',
        'new_vocal_guitar': 'Вокал и Гитара'
    }
    new_specialisation_student = specialisation_mapping[callback_query.data]
    await state.update_data(new_specialisation_student=new_specialisation_student)

    if new_specialisation_student == 'Вокал':
        reply_markup = await kb.teachers_choice_students_da_v()
    elif new_specialisation_student == 'Гитара':
        reply_markup = await kb.teachers_choice_students_da_g()
    else:
        reply_markup = await kb.teachers_choice_students_da()

    await callback_query.message.edit_text(
        text=f"Вы выбрали направление: {new_specialisation_student}. \nТеперь выберите нового преподавателя или преподавателей:",
        reply_markup=reply_markup
    )
    await state.set_state(UpdateRegistrationState.UpdateIDTeacher)


@router.callback_query(F.data.startswith('up_name'))
async def update_parts_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ваше новое имя:")
    await state.set_state(UpdateParts.UpdatePartsName)


@router.message(UpdateParts.UpdatePartsName)
async def process_new_name(message: Message, state: FSMContext):
    parts_name = message.text
    tg_id = message.from_user.id

    if not parts_name.isalpha():
        await message.answer('Имя должно содержать только буквы. Пожалуйста, введите ваше имя еще раз:')
        return

    async with async_session() as session:
        await session.execute(
            update(Student)
            .where(Student.tg_id == tg_id)
            .values(name=parts_name)
        )
        await session.commit()

    await message.answer(text='Отлично! Ваше имя было успешно изменено.', reply_markup=kb.menu1)
    await state.clear()


@router.callback_query(F.data.startswith('up_last_name'))
async def update_parts_last_name(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите вашу новую фамилию:")
    await state.set_state(UpdateParts.UpdatePartsLastName)


@router.message(UpdateParts.UpdatePartsLastName)
async def process_new_last_name(message: Message, state: FSMContext):
    parts_last_name = message.text
    tg_id = message.from_user.id

    if not parts_last_name.isalpha():
        await message.answer('Фамилия должна содержать только буквы. Пожалуйста, введите вашу фамилию еще раз:')
        return

    async with async_session() as session:
        await session.execute(
            update(Student)
            .where(Student.tg_id == tg_id)
            .values(last_name=parts_last_name)
        )
        await session.commit()

    await message.answer(text='Отлично! Ваша фамилия была успешно изменена.', reply_markup=kb.menu1)
    await state.clear()


@router.callback_query(F.data.startswith('up_phone'))
async def update_parts_phone(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новый номер телефона (без +7 или 8 в начале):")
    await state.set_state(UpdateParts.UpdatePartsPhone)


@router.message(UpdateParts.UpdatePartsPhone)
async def process_new_phone(message: Message, state: FSMContext):
    raw_phone = message.text.strip()
    tg_id = message.from_user.id

    if not raw_phone.isdigit() or len(raw_phone) != 10:
        await message.answer('''
                Неверный формат номера телефона. Пожалуйста, введите 10 цифр номера, без +7 или 8 в начале''')
        return

    parts_phone = f"+7 ({raw_phone[:3]}) {raw_phone[3:6]}-{raw_phone[6:8]}-{raw_phone[8:]}"

    async with async_session() as session:
        await session.execute(
            update(Student)
            .where(Student.tg_id == tg_id)
            .values(phone=parts_phone)
        )
        await session.commit()

    await message.answer(text='Отлично! Номер телефона успешно изменен.', reply_markup=kb.menu1)
    await state.clear()


@router.callback_query(F.data.startswith('up_specialization_and_teachers'))
async def change_parts_inline_keyboard(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(text='Выберите новую специализацию:', reply_markup=kb.tool3)
    await state.set_state(UpdateParts.UpdatePartsChoiceSpecialisation)


@router.callback_query(F.data.in_(['new_parts_vocal', 'new_parts_guitar', 'new_parts_vocal_guitar']),
                       UpdateParts.UpdatePartsChoiceSpecialisation)
async def update_parts_process_specialisation(callback_query: CallbackQuery, state: FSMContext):
    specialisation_mapping = {
        'new_parts_vocal': 'Вокал',
        'new_parts_guitar': 'Гитара',
        'new_parts_vocal_guitar': 'Вокал и Гитара'
    }
    new_parts_specialisation_student = specialisation_mapping[callback_query.data]
    await state.update_data(new_specialisation_student=new_parts_specialisation_student)

    if new_parts_specialisation_student == 'Вокал':
        reply_markup = await kb.teachers_choice_students_da_v()
    elif new_parts_specialisation_student == 'Гитара':
        reply_markup = await kb.teachers_choice_students_da_g()
    else:
        reply_markup = await kb.teachers_choice_students_da()

    await callback_query.message.edit_text(
        text=f"Вы выбрали направление: {new_parts_specialisation_student}. \nТеперь выберите нового преподавателя или преподавателей:",
        reply_markup=reply_markup
    )
    await state.set_state(UpdateParts.UpdatePartsIDTeacher)