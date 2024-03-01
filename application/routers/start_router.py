from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

import application.keyboard as kb

router = Router(name=__name__)


@router.message(CommandStart())
async def smd_start(message: Message):
    await message.answer(text=f'{message.from_user.first_name}, добро пожаловать! \nПожалуйста, выбери роль:',
                         reply_markup=kb.main)


@router.message(Command('help'))
async def help_bot(message: Message):
    pass


