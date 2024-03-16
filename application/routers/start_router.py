from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

import application.keyboard as kb

router = Router(name=__name__)


@router.message(CommandStart())
async def smd_start(message: Message):
    welcome_text = (
        f"Привет, <b>{message.from_user.first_name}</b>, добро пожаловать!\n\n"
        "Вот что ты можешь делать с помощью нашего бота:\n\n"
        "👤 Личный кабинет - /profile\n\n"
        "📚 Отправка ДЗ - /homework\n"
        "🏆 Узнать лидера текущего месяца - /leader\n"
        "📊 ТОП учеников за все время - /top\n\n"
        "🎁 Система баллов:\n"
        "├ Узнать количество своих баллов можно в личном кабинете\n"
        "├ Баллы начисляются за выполнение домашних заданий, а также за выполнение специальных заданий от школы\n"
        "├ Баллы можно обменять на подарки: бесплатные занятия, футболки и многое другое\n"
        "├ Подробнее о системе баллов и подарках - /monetization\n\n"
        "💎 Для преподавателей:\n"
        "├ Возможность проверять домашние задания учеников и начислять за это баллы\n\n"
        "❔ Дополнительную информацию и ответы на часто задаваемы вопросы вы найдете с помощью команды - /info\n\n"
        "При использовании бота вы соглашаетесь на получение от нас сообщений, рассылок и рекламы."
    )
    await message.answer(text=welcome_text, parse_mode='HTML', reply_markup=kb.menu)


@router.callback_query(F.data.startswith('cancellation'))
async def call_cancellation(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    welcome_text = (
        f"Привет, <b>{callback.from_user.first_name}</b>, добро пожаловать!\n\n"
        "Вот что ты можешь делать с помощью нашего бота:\n\n"
        "👤 Личный кабинет - /profile\n\n"
        "📚 Отправка ДЗ - /homework\n"
        "🏆 Узнать лидера текущего месяца - /leader\n"
        "📊 ТОП учеников за все время - /top\n\n"
        "🎁 Система баллов:\n"
        "├ Узнать количество своих баллов можно в личном кабинете\n"
        "├ Баллы начисляются за выполнение домашних заданий, а также за выполнение специальных заданий от школы\n"
        "├ Баллы можно обменять на подарки: бесплатные занятия, футболки и многое другое\n"
        "├ Подробнее о системе баллов и подарках - /monetization\n\n"
        "💎 Для преподавателей:\n"
        "├ Возможность проверять домашние задания учеников и начислять за это баллы\n\n"
        "❔ Дополнительную информацию и ответы на часто задаваемые вопросы вы найдете с помощью команды - /info\n\n"
        "При использовании бота вы соглашаетесь на получение от нас сообщений, рассылок и рекламы."
    )
    await callback.message.edit_text(text=welcome_text, parse_mode='HTML', reply_markup=kb.back3)
