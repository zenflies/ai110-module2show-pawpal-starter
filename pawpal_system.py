from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    name: str
    duration_minutes: int
    priority: int          # 1 (low) to 5 (high)
    category: str          # "walk", "feed", "meds", "grooming", "enrichment", etc.
    completed: bool = False

    def is_high_priority(self) -> bool:
        pass

    def mark_complete(self) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    age_years: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_name: str) -> None:
        pass

    def get_tasks(self) -> List[Task]:
        pass


class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: List[str] = None):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences: List[str] = preferences if preferences is not None else []

    def add_preference(self, pref: str) -> None:
        pass

    def get_availability(self) -> int:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.scheduled_tasks: List[Task] = []
        self.unscheduled_tasks: List[Task] = []

    def generate_plan(self) -> List[Task]:
        pass

    def explain_plan(self) -> str:
        pass

    def get_total_duration(self) -> int:
        pass

    def fits_in_day(self, task: Task) -> bool:
        pass
