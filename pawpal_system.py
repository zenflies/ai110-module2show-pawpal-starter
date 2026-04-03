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
        """Return True if this task has priority 4 or 5."""
        return self.priority >= 4

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


@dataclass
class Pet:
    name: str
    species: str
    age_years: int
    owner: 'Owner' = None
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_name: str) -> None:
        """Remove the first task whose name matches task_name."""
        self.tasks = [t for t in self.tasks if t.name != task_name]

    def get_tasks(self) -> List[Task]:
        """Return a copy of this pet's task list."""
        return list(self.tasks)

    def get_owner(self) -> 'Owner':
        """Return the Owner associated with this pet."""
        return self.owner


class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: List[str] = None):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences: List[str] = preferences if preferences is not None else []
        self.pets: List['Pet'] = []

    def add_preference(self, pref: str) -> None:
        """Add a scheduling preference if it isn't already recorded."""
        if pref not in self.preferences:
            self.preferences.append(pref)

    def get_availability(self) -> int:
        """Return the owner's total available minutes for the day."""
        return self.available_minutes

    def add_pet(self, pet: 'Pet') -> None:
        """Register a pet under this owner and set the back-reference."""
        if pet not in self.pets:
            self.pets.append(pet)
            pet.owner = self

    def remove_pet(self, pet: 'Pet') -> None:
        """Unregister a pet from this owner and clear its back-reference."""
        if pet in self.pets:
            self.pets.remove(pet)
            pet.owner = None

    def get_pets(self) -> List['Pet']:
        """Return a copy of the owner's pet list."""
        return list(self.pets)

    def get_all_tasks(self) -> List[Task]:
        """Return every task across all owned pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.get_tasks())
        return all_tasks


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.scheduled_tasks: List[Task] = []
        self.unscheduled_tasks: List[Task] = []

    def generate_plan(self) -> List[Task]:
        """Greedily schedule tasks highest-priority first, within the owner's available time."""
        self.scheduled_tasks = []
        self.unscheduled_tasks = []

        tasks_by_priority = sorted(self.pet.get_tasks(), key=lambda t: t.priority, reverse=True)
        minutes_remaining = self.owner.get_availability()

        for task in tasks_by_priority:
            if task.duration_minutes <= minutes_remaining:
                self.scheduled_tasks.append(task)
                minutes_remaining -= task.duration_minutes
            else:
                self.unscheduled_tasks.append(task)

        return list(self.scheduled_tasks)

    def explain_plan(self) -> str:
        """Return a human-readable explanation of what was scheduled and why."""
        if not self.scheduled_tasks and not self.unscheduled_tasks:
            return "No plan generated yet. Call generate_plan() first."

        lines = [f"Daily plan for {self.pet.name} (owner: {self.owner.name})",
                 f"Available time: {self.owner.get_availability()} min\n"]

        lines.append("Scheduled tasks:")
        for task in self.scheduled_tasks:
            flag = " [HIGH PRIORITY]" if task.is_high_priority() else ""
            lines.append(
                f"  - {task.name} ({task.category}, {task.duration_minutes} min, "
                f"priority {task.priority}{flag})"
            )

        lines.append(f"\nTotal time used: {self.get_total_duration()} / "
                     f"{self.owner.get_availability()} min")

        if self.unscheduled_tasks:
            lines.append("\nNot scheduled (insufficient time):")
            for task in self.unscheduled_tasks:
                lines.append(
                    f"  - {task.name} ({task.duration_minutes} min, priority {task.priority})"
                )

        return "\n".join(lines)

    def get_total_duration(self) -> int:
        """Return total minutes consumed by scheduled tasks."""
        return sum(t.duration_minutes for t in self.scheduled_tasks)

    def fits_in_day(self, task: Task) -> bool:
        """Check whether adding this task would still fit within available time."""
        return self.get_total_duration() + task.duration_minutes <= self.owner.get_availability()
