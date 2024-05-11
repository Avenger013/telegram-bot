from sqlalchemy import BigInteger, ForeignKey, Date
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy import Text, DateTime, LargeBinary

from config import SQLALCHEMY_URL

engine = create_async_engine(SQLALCHEMY_URL, echo=True)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Teacher(Base):
    __tablename__: str = 'teachers'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    specialisation: Mapped[str] = mapped_column()

    students = relationship(argument='Student', secondary='student_teacher', back_populates='teachers')


class Student(Base):
    __tablename__: str = 'students'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    name: Mapped[str | None] = mapped_column()
    last_name: Mapped[str | None] = mapped_column()
    phone: Mapped[str | None] = mapped_column()
    specialisation_student: Mapped[str | None] = mapped_column()
    point: Mapped[int | None] = mapped_column()

    homeworks = relationship(argument='Homework', back_populates='student')
    points_history = relationship(argument='PointsHistory', back_populates='student')
    teachers = relationship(argument='Teacher', secondary='student_teacher', back_populates='students')
    daily_check_ins = relationship(argument='DailyCheckIn', back_populates='student')


class StudentTeacher(Base):
    __tablename__ = 'student_teacher'
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id'))
    teacher_id: Mapped[int | None] = mapped_column(ForeignKey('teachers.id'))


class Homework(Base):
    __tablename__: str = 'homeworks'

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id'))
    text_submission = mapped_column(Text)
    photo_submission = mapped_column(LargeBinary)
    video_submission = mapped_column(LargeBinary)
    audio_submission = mapped_column(LargeBinary)
    link_submission: Mapped[str | None] = mapped_column()
    submission_time = mapped_column(DateTime)
    # submission_time = Mapped[datetime.datetime] = mapped_column(server_default=text("TIMEZONE('utc', now()"))
    student = relationship(argument='Student', back_populates='homeworks')


class PointsHistory(Base):
    __tablename__: str = 'points_history'

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id'))
    points_added: Mapped[int | None] = mapped_column()
    date_added = mapped_column(DateTime)

    student = relationship(argument='Student', back_populates='points_history')


class Administrator(Base):
    __tablename__: str = 'administrators'

    id: Mapped[int] = mapped_column(primary_key=True)
    administrator_tg_id = mapped_column(BigInteger)


class Password(Base):
    __tablename__: str = 'passwords'

    id: Mapped[int] = mapped_column(primary_key=True)
    password_teacher: Mapped[str | None] = mapped_column()
    password_newsletter: Mapped[str | None] = mapped_column()


class MonetizationSystem(Base):
    __tablename__: str = 'monetization_systems'

    id: Mapped[int] = mapped_column(primary_key=True)
    task: Mapped[str | None] = mapped_column()
    number_of_points: Mapped[int | None] = mapped_column()


class PointsExchange(Base):
    __tablename__: str = 'points_exchanges'

    id: Mapped[int] = mapped_column(primary_key=True)
    present: Mapped[str | None] = mapped_column()
    number_of_points: Mapped[int | None] = mapped_column()


class SupportInfo(Base):
    __tablename__: str = 'support_info'

    id: Mapped[int] = mapped_column(primary_key=True)
    instruction_support: Mapped[str | None] = mapped_column()


class InfoBot(Base):
    __tablename__: str = 'info_bot'

    id: Mapped[int] = mapped_column(primary_key=True)
    instruction: Mapped[str | None] = mapped_column()


class TasksForTheWeek(Base):
    __tablename__: str = 'tasks_for_the_weeks'

    id: Mapped[int] = mapped_column(primary_key=True)
    quest: Mapped[str | None] = mapped_column()


class DailyCheckIn(Base):
    __tablename__ = 'daily_check_ins'

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('students.id'), unique=True)
    check_in_count: Mapped[int] = mapped_column(default=1)
    date = mapped_column(Date)

    student = relationship(argument='Student', back_populates='daily_check_ins')


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
