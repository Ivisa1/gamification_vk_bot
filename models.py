# Файл, в котором определены существующие в БД модели для работы
from sqlalchemy import (
    BigInteger, String, Enum as SQLAlchemyEnum,
    Boolean, DefaultClause, ClauseElement,
    ForeignKey
)
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.ext.asyncio import AsyncSession
import enum
from typing import Annotated

### ПЕРЕЧИСЛЕНИЯ ДЛЯ ЗНАЧЕНИЙ МОДЕЛИ ###

# Пример, как делать Enum: https://habr.com/ru/companies/amvera/articles/849836/
class DifficulcyEnum(str, enum.Enum):
    VERY_EASY = 'very_easy'
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'
    VERY_HARD = 'very_hard'

class TypeEnum(str, enum.Enum):
    DISPOSABLE = 'disposable'
    REUSABLE = 'reusable'


print(DifficulcyEnum.VERY_EASY)
print(DifficulcyEnum('very_easy'))


### ТИПЫ ДЛЯ АННОТАЦИЙ

### МОДЕЛИ ###

# Базовая абстрактная модель
class BaseModel(DeclarativeBase):
    pass

# Модель пользователей
class UserModel(BaseModel):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True) # user_id (из ВКонкакте)
    first_name: Mapped[str] = mapped_column(String, nullable=False) # Имя
    last_name: Mapped[str] = mapped_column(String, nullable=False) # Фамилия
    current_xp: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, server_default=DefaultClause('0')) # Опыт пользователя
    is_public: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=DefaultClause('false')) # Будет ли появляться пользователь в глобальной таблице лидеров

# Модель пользовательских задач
class TasksModel(BaseModel):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey(column='users.id', ondelete='CASCADE'))
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    difficulcy: Mapped[DifficulcyEnum] = mapped_column(
        SQLAlchemyEnum(DifficulcyEnum, name='difficulcy_level'),
        default=DifficulcyEnum.VERY_EASY,
        nullable=False
    )
    type: Mapped[TypeEnum] = mapped_column(
        SQLAlchemyEnum(TypeEnum, name='task_type'),
        default=TypeEnum.DISPOSABLE,
        nullable=False
    )

class UserCountersModel(BaseModel):
    __tablename__ = 'user_counters'

    id: Mapped[int] = mapped_column(ForeignKey(column='users.id', ondelete='CASCADE'), primary_key=True)
    very_easy: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, server_default=DefaultClause('0'))
    easy: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, server_default=DefaultClause('0'))
    medium: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, server_default=DefaultClause('0'))
    hard: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, server_default=DefaultClause('0'))
    very_hard: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0, server_default=DefaultClause('0'))