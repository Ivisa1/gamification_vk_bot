from typing import Tuple
from vkbottle.bot import BotLabeler

from .create_task import create_task_labeler
from .leaderboard import leaderboard_labeler
from .profile import profile_labeler
from .tasks_list import tasks_list_labeler

labelers: Tuple[BotLabeler] = (
    create_task_labeler,
    leaderboard_labeler,
    profile_labeler,
    tasks_list_labeler
)

__all__ = (
    "create_task_labeler",
    "leaderboard_labeler",
    "profile_labeler",
    "tasks_list_labeler"
)