from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton, InlineKeyboardMarkup
from application.database.requests import get_teachers, get_teachers_vocal, get_teachers_guitar, get_gifts, get_money, \
    get_student, get_teachers1
from application.database.models import async_session

registration = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Регистрация',
            callback_data='registration'
        )
    ],
    [
        InlineKeyboardButton(
            text='Отмена',
            callback_data='cancellation'
        )
    ]
])

can = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='◀️ Отмена регистрации',
            callback_data='cancellation'
        )
    ]
])

can_update = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='◀️ Отмена изменений',
            callback_data='cell'
        )
    ]
])

tree_can_send = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='◀️Отмена отправки',
            callback_data='cancel'
        )
    ]
])

tool1 = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='🎤 Вокал',
            callback_data='vocal'
        )
    ],
    [
        InlineKeyboardButton(
            text='🎸 Гитара',
            callback_data='guitar'
        )
    ],
    [
        InlineKeyboardButton(
            text='🎤/🎸 Вокал и Гитара',
            callback_data='vocal_guitar'
        )
    ],
    [
        InlineKeyboardButton(
            text='◀️ Отмена регистрации',
            callback_data='cancellation'
        )
    ]
])

tool2 = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='🎤 Вокал',
            callback_data='new_vocal'
        )
    ],
    [
        InlineKeyboardButton(
            text='🎸 Гитара',
            callback_data='new_guitar'
        )
    ],
    [
        InlineKeyboardButton(
            text='🎤/🎸 Вокал и Гитара',
            callback_data='new_vocal_guitar'
        )
    ],
    [
        InlineKeyboardButton(
            text='◀️ Отмена изменений',
            callback_data='cell'
        )
    ]
])

tool3 = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='🎤 Вокал',
            callback_data='new_parts_vocal'
        )
    ],
    [
        InlineKeyboardButton(
            text='🎸 Гитара',
            callback_data='new_parts_guitar'
        )
    ],
    [
        InlineKeyboardButton(
            text='🎤/🎸 Вокал и Гитара',
            callback_data='new_parts_vocal_guitar'
        )
    ],
    [
        InlineKeyboardButton(
            text='◀️ Отмена изменений',
            callback_data='cell'
        )
    ]
])

dz_type = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Фото',
            callback_data='p_p'
        )
    ],
    [
        InlineKeyboardButton(
            text='Видео',
            callback_data='v_v'
        )
    ],
    [
        InlineKeyboardButton(
            text='Текст или ссылка',
            callback_data='t_l'
        )
    ],
    [
        InlineKeyboardButton(
            text='Голосовое',
            callback_data='o_i'
        )
    ],
    [
        InlineKeyboardButton(
            text='◀️ Назад',
            callback_data='1_canceled'
        )
    ]
])

dz_type_2 = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Видео',
            callback_data='vvv'
        )
    ],
    [
        InlineKeyboardButton(
            text='Ссылка',
            callback_data='lll'
        )
    ],
    [
        InlineKeyboardButton(
            text='◀️ Назад',
            callback_data='2_canceled'
        )
    ]
])

confirmation = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Всё верно',
            callback_data='confirm'
        )
    ],
    [
        InlineKeyboardButton(
            text='Хочу изменить',
            callback_data='change'
        )
    ]
])

confirmation_video = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Всё верно',
            callback_data='vi_confirm'
        )
    ],
    [
        InlineKeyboardButton(
            text='Хочу изменить',
            callback_data='deo_change'
        )
    ]
])

confirmation_video_2 = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Всё верно',
            callback_data='iv_2_confirm'
        )
    ],
    [
        InlineKeyboardButton(
            text='Хочу изменить',
            callback_data='oed_2_change'
        )
    ]
])

confirmation_text = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Всё верно',
            callback_data='te_confirm'
        )
    ],
    [
        InlineKeyboardButton(
            text='Хочу изменить',
            callback_data='xt_change'
        )
    ]
])

confirmation_text_2 = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Всё верно',
            callback_data='et_2_confirm'
        )
    ],
    [
        InlineKeyboardButton(
            text='Хочу изменить',
            callback_data='tx_2_change'
        )
    ]
])

confirmation_voice = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Всё верно',
            callback_data='voi_confirm'
        )
    ],
    [
        InlineKeyboardButton(
            text='Хочу изменить',
            callback_data='ce_change'
        )
    ]
])

menu = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text='🔐 Личный кабинет'),
        KeyboardButton(text='🎁 Монетизация')
    ]
], resize_keyboard=True, one_time_keyboard=True)

menu1 = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text='🔐 Личный кабинет'), KeyboardButton(text='✉️ Отправка ДЗ')
    ],
    [
        KeyboardButton(text='📊 ТОП учеников'), KeyboardButton(text='📈 Лидер месяца')
    ],
    [
        KeyboardButton(text='🎁 Монетизация'), KeyboardButton(text='❔ О боте')
    ],
    [
        KeyboardButton(text='✍🏼 Поддержка')
    ]
], resize_keyboard=True, one_time_keyboard=True)

inline_keyboard_personal_area = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='📊ТОП учеников',
            callback_data='viewing'
        ),
        InlineKeyboardButton(
            text='📈Лидер месяца',
            callback_data='lead'
        )
    ],
    [
        InlineKeyboardButton(
            text='✍🏼Поддержка',
            callback_data='supp'
        ),
        InlineKeyboardButton(
            text='❔О боте',
            callback_data='the_info'
        )
    ],
    [
        InlineKeyboardButton(
            text='✉️Отправить ДЗ',
            callback_data='send'
        )
    ],
    [
        InlineKeyboardButton(
            text='🎁Монетизация',
            callback_data='money'
        )
    ],
    [
        InlineKeyboardButton(
            text='⚙️Изменить данные о себе в ЛК',
            callback_data='update_info'
        )
    ]
])

inline_homework = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='📨Отправить выполненное ДЗ',
            callback_data='dz_send'
        )
    ],
    [
        InlineKeyboardButton(
            text='📆Отправить еженедельное задание',
            callback_data='zd_send'
        )
    ],
    [
        InlineKeyboardButton(
            text='📹Отправить видео с исполнением песни',
            callback_data='vid_send'
        )
    ],
    [
        InlineKeyboardButton(
            text='◀️Назад',
            callback_data='back'
        )
    ]
])

inline_homework1 = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='📨Отправить выполненное ДЗ',
            callback_data='dz_send'
        )
    ],
    [
        InlineKeyboardButton(
            text='📆Отправить еженедельное задание',
            callback_data='zd_send'
        )
    ],
    [
        InlineKeyboardButton(
            text='📹Отправить видео с исполнением песни',
            callback_data='vid_send'
        )
    ],
    [
        InlineKeyboardButton(
            text='🔐Перейти в личный кабинет',
            callback_data='back'
        )
    ]
])

updating_in_parts = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='👤Имя',
            callback_data='up_name'
        ),
        InlineKeyboardButton(
            text='👤Фамилию',
            callback_data='up_last_name'
        )
    ],
    [
        InlineKeyboardButton(
            text='📞Номер телефона',
            callback_data='up_phone'
        )
    ],
    [
        InlineKeyboardButton(
            text='🎤/🎸Направление и преподавателя(-лей)',
            callback_data='up_specialization_and_teachers'
        )
    ],
    [
        InlineKeyboardButton(
            text='⚙️Изменить все данные',
            callback_data='up_all'
        )
    ],
    [
        InlineKeyboardButton(
            text='🔐Вернуться в личный кабинет',
            callback_data='back'
        )
    ]
])

inline_keyboard_error_video = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='✉️Отправить ДЗ',
            callback_data='send'
        )
    ],
    [
        InlineKeyboardButton(
            text='📹Отправить другое видео',
            callback_data='deo_change'
        )
    ],
    [
        InlineKeyboardButton(
            text='◀️Отмена отправки',
            callback_data='cancel'
        )
    ]
])

back = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='🌟Получение баллов',
            callback_data='receiving'
        )
    ],
    [
        InlineKeyboardButton(
            text='💎Обмен баллов',
            callback_data='buy'
        )
    ],
    [
        InlineKeyboardButton(
            text='◀️Назад',
            callback_data='back'
        )
    ]
])

back2 = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='◀️Назад',
            callback_data='back'
        )
    ]
])

back3 = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='🔐Перейти в личный кабинет',
            callback_data='back'
        )
    ]
])

back4 = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='🌟Получение баллов',
            callback_data='receiving'
        )
    ],
    [
        InlineKeyboardButton(
            text='💎Обмен баллов',
            callback_data='buy'
        )
    ],
    [
        InlineKeyboardButton(
            text='🔐Перейти в личный кабинет',
            callback_data='back'
        )
    ]
])

choice_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(
            text='Выбрать подарки заново',
            callback_data='select_gifts_again'
        )
    ],
    [
        InlineKeyboardButton(
            text='Завершить выбор',
            callback_data='finish_selection'
        )
    ],
])


async def teachers_choice():
    teachers_choice_kb = InlineKeyboardBuilder()
    teachers_choice = await get_teachers()
    for teacher in teachers_choice:
        full_name = f'{teacher.name} {teacher.last_name}'
        teachers_choice_kb.add(InlineKeyboardButton(text=full_name, callback_data=f'teacher_{teacher.id}'))
    return teachers_choice_kb.adjust(2).as_markup()


async def choice_teacher(tg_id: int):
    teachers_choice_kb = InlineKeyboardBuilder()
    async with async_session() as session:
        student = await get_student(session, tg_id)
        if student:
            teachers_choice = await get_teachers1(student.id)
            for teacher in teachers_choice:
                full_name = f'{teacher.name} {teacher.last_name}'
                teachers_choice_kb.add(InlineKeyboardButton(text=full_name, callback_data=f'choice_{teacher.id}'))
            teachers_choice_kb.add(InlineKeyboardButton(text="◀️ Назад", callback_data='cancel'))
        else:
            pass
    return teachers_choice_kb.adjust(1).as_markup()


async def teachers_choice_students_da(selected_ids=[]):
    teachers_choice_kb = InlineKeyboardBuilder()
    teachers_choice = await get_teachers()
    for teacher in teachers_choice:
        status_emoji = "✅" if teacher.id in selected_ids else ""
        full_name = f"{status_emoji} {teacher.name} {teacher.last_name}"
        teachers_choice_kb.add(InlineKeyboardButton(text=full_name, callback_data=f'select_teacher_{teacher.id}'))
    teachers_choice_kb.add(InlineKeyboardButton(text="🎯Подтвердить выбор", callback_data='done_selecting_teachers'))
    teachers_choice_kb.add(InlineKeyboardButton(text="◀️Отмена", callback_data='cancellation'))
    return teachers_choice_kb.adjust(2).as_markup()


async def teachers_choice_students_da_v(selected_ids=[]):
    teachers_choice_kb = InlineKeyboardBuilder()
    teachers_choice = await get_teachers_vocal()
    for teacher in teachers_choice:
        status_emoji = "✅" if teacher.id in selected_ids else ""
        full_name = f"{status_emoji} {teacher.name} {teacher.last_name}"
        teachers_choice_kb.add(InlineKeyboardButton(text=full_name, callback_data=f'1select_teacher_{teacher.id}'))
    teachers_choice_kb.add(InlineKeyboardButton(text="🎯Подтвердить выбор", callback_data='done_selecting_teachers'))
    teachers_choice_kb.add(InlineKeyboardButton(text="◀️Отмена", callback_data='cancellation'))
    return teachers_choice_kb.adjust(1).as_markup()


async def teachers_choice_students_da_g(selected_ids=[]):
    teachers_choice_kb = InlineKeyboardBuilder()
    teachers_choice = await get_teachers_guitar()
    for teacher in teachers_choice:
        status_emoji = "✅" if teacher.id in selected_ids else ""
        full_name = f"{status_emoji} {teacher.name} {teacher.last_name}"
        teachers_choice_kb.add(InlineKeyboardButton(text=full_name, callback_data=f'2select_teacher_{teacher.id}'))
    teachers_choice_kb.add(InlineKeyboardButton(text="🎯Подтвердить выбор", callback_data='done_selecting_teachers'))
    teachers_choice_kb.add(InlineKeyboardButton(text="◀️Отмена", callback_data='cancellation'))
    return teachers_choice_kb.adjust(1).as_markup()


async def choosing_a_gift(selected_ids=[]):
    choosing_a_gift_kb = InlineKeyboardBuilder()
    choosing_a_gift = await get_gifts()
    for PointsExchanges in choosing_a_gift:
        status_emoji = "✅" if PointsExchanges.id in selected_ids else ""
        choosing_a_gift_kb.add(InlineKeyboardButton(text=f"{status_emoji} {PointsExchanges.present}",
                                                    callback_data=f'gifts_{PointsExchanges.id}'))
    choosing_a_gift_kb.add(InlineKeyboardButton(text="🎯Подтвердить выбор", callback_data='selecting_gifts'))
    return choosing_a_gift_kb.adjust(1).as_markup()


async def choosing_a_money(selected_ids=[]):
    choosing_a_money_kb = InlineKeyboardBuilder()
    choosing_a_money = await get_money()
    for MonetizationSystem in choosing_a_money:
        status_emoji = "✅" if MonetizationSystem.id in selected_ids else ""
        choosing_a_money_kb.add(
            InlineKeyboardButton(text=f"{status_emoji} {MonetizationSystem.task} {MonetizationSystem.number_of_points}",
                                 callback_data=f'monetization_{MonetizationSystem.id}'))
    choosing_a_money_kb.add(InlineKeyboardButton(text="🎯Подтвердить выбор", callback_data='selecting_gifts'))
    return choosing_a_money_kb.adjust(1).as_markup()
