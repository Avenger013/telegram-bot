from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='profile',
            description='Личный кабинет'
        ),
        BotCommand(
            command='homework',
            description='Отправка ДЗ',
        ),
        BotCommand(
            command='top',
            description='Топ учеников',
        ),
        BotCommand(
            command='leader',
            description='Лидер месяца',
        ),
        BotCommand(
            command='monetization',
            description='Монетизация',
        ),
        BotCommand(
            command='info',
            description='Информация о боте',
        ),
        BotCommand(
            command='support',
            description='Поддержка',
        ),
        BotCommand(
            command='registration',
            description='Регистрация ученика',
        ),
        BotCommand(
            command='start',
            description='Перезапуск бота',
        ),
        BotCommand(
            command='newsletter',
            description='Рассылка',
        )
    ]

    await bot.set_my_commands(commands, BotCommandScopeDefault())