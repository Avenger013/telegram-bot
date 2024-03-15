from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

import application.keyboard as kb

router = Router(name=__name__)


@router.message(CommandStart())
async def smd_start(message: Message):
    welcome_text = (
        f"Привет, {message.from_user.first_name}, добро пожаловать!\n\n"
        "Личный кабинет ученика - /profile\n\n"
        "🎁В нашем боте есть система получения и обмена баллов, количество своих баллов вы можете увидеть в личном кабинете. Подробности - /monetization\n\n"
        "🎁Этот бот создан для наших учеников и преподавателей, ученики могут выполнять задания за которые получают баллы и легко их обменивать на разные подарки от нас, включая бесплатные занятия, футболки и многое другое.\n"
        "Подробности - /monetization\n\n"
        "💎Преподаватели могут проверять, присланные учениками задания и начислять за это дополнительные баллы, но баллы можно получить не только за счет отправки домашних заданий, но еще и за счет выполненных заданий от самой школы. Подробности - /monetization\n\n"
        "❔Информацию о часто задаваемых вопросах вы найдете с помощью команды - /info"
        "\n\nПри использовании вы соглашаетесь получать от бота сообщения, рассылки и рекламу."
    )
    await message.answer(text=welcome_text, reply_markup=kb.menu)


@router.callback_query(F.data.startswith('cancellation'))
async def call_cancellation(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    welcome_text = (
        f"Привет, <b>{callback.from_user.first_name}</b>, добро пожаловать!\n\n"
        "Личный кабинет ученика - /profile\n"
        "Отправка ДЗ - /homework\n\n"
        "🎁В нашем боте есть система получения и обмена баллов\n"
        "├ Количество своих баллов вы можете увидеть в личном кабинете\n"
        "├ Подробности - /monetization\n\n"
        "🎁Этот бот создан для наших учеников и преподавателей\n"
        "├ Ученики могут выполнять задания за которые получают баллы и легко их обменивать на разные подарки от нас\n"
        "├ Подарки: бесплатные занятия, футболки и многое другое\n"
        "├ Подробности - /monetization\n\n"
        "💎Преподаватели могут проверять, присланные учениками задания и начислять за это дополнительные баллы\n"
        "├ Но баллы можно получить не только за счет отправки домашних заданий\n"
        "├ Также баллы можно получить за счет выполненных заданий от самой школы\n"
        "├ Подробности - /monetization\n\n"
        "❔Информацию о часто задаваемых вопросах вы найдете с помощью команды - /info"
        "\n\nПри использовании вы соглашаетесь получать от бота сообщения, рассылки и рекламу."
    )
    await callback.message.edit_text(text=welcome_text, parse_mode='HTML', reply_markup=kb.back3)
