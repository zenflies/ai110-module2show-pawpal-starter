from datetime import date, timedelta
import pytest
from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_owner(minutes=120) -> Owner:
    return Owner(name="Jordan", available_minutes=minutes)


def make_pet(name="Mochi") -> Pet:
    return Pet(name=name, species="dog", age_years=3)


def make_task(name="Walk", duration=20, priority=3, category="walk",
              start_time=None, frequency="once", due_date=None) -> Task:
    return Task(name=name, duration_minutes=duration, priority=priority,
                category=category, start_time=start_time,
                frequency=frequency, due_date=due_date)


# ---------------------------------------------------------------------------
# Phase 2 tests (preserved)
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    """Completing a task flips its completed flag to True."""
    task = make_task()
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding two tasks to a pet yields a task list of length 2."""
    pet = make_pet()
    assert len(pet.get_tasks()) == 0
    pet.add_task(make_task("Breakfast", category="feed"))
    pet.add_task(make_task("Fetch",     category="enrichment"))
    assert len(pet.get_tasks()) == 2


# ---------------------------------------------------------------------------
# Sorting tests
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """Tasks with start_time are returned earliest-first."""
    tasks = [
        make_task("Dinner",    start_time="18:00"),
        make_task("Breakfast", start_time="07:30"),
        make_task("Meds",      start_time="12:00"),
    ]
    sorted_tasks = Scheduler.sort_by_time(tasks)
    times = [t.start_time for t in sorted_tasks]
    assert times == ["07:30", "12:00", "18:00"]


def test_sort_by_time_tasks_without_time_go_last():
    """Tasks missing a start_time appear after all timed tasks."""
    tasks = [
        make_task("Bath",      start_time=None),   # no time
        make_task("Walk",      start_time="08:00"),
        make_task("Grooming",  start_time=None),   # no time
    ]
    sorted_tasks = Scheduler.sort_by_time(tasks)
    assert sorted_tasks[0].start_time == "08:00"
    assert sorted_tasks[1].start_time is None
    assert sorted_tasks[2].start_time is None


def test_sort_by_time_empty_list():
    """Sorting an empty list returns an empty list without error."""
    assert Scheduler.sort_by_time([]) == []


# ---------------------------------------------------------------------------
# Recurrence tests
# ---------------------------------------------------------------------------

def test_daily_task_creates_next_occurrence_one_day_later():
    """Completing a daily task returns a new task due tomorrow."""
    today = date.today()
    task = make_task(frequency="daily", due_date=today)
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == today + timedelta(days=1)
    assert next_task.completed is False


def test_weekly_task_creates_next_occurrence_seven_days_later():
    """Completing a weekly task returns a new task due in 7 days."""
    today = date.today()
    task = make_task(frequency="weekly", due_date=today)
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == today + timedelta(weeks=1)


def test_once_task_returns_no_next_occurrence():
    """Completing a one-off task returns None (no follow-up created)."""
    task = make_task(frequency="once")
    next_task = task.mark_complete()
    assert next_task is None


def test_mark_task_complete_auto_adds_to_pet():
    """Scheduler.mark_task_complete adds the next occurrence directly to the pet."""
    owner = make_owner()
    pet   = make_pet()
    owner.add_pet(pet)
    task = make_task(frequency="daily", due_date=date.today())
    pet.add_task(task)

    scheduler = Scheduler(owner=owner, pet=pet)
    scheduler.generate_plan()
    assert len(pet.get_tasks()) == 1

    scheduler.mark_task_complete(task)
    assert len(pet.get_tasks()) == 2                          # next occurrence added
    assert pet.get_tasks()[0].completed is True               # original is done
    assert pet.get_tasks()[1].completed is False              # new one is pending


def test_recurring_task_preserves_attributes():
    """The next occurrence inherits name, duration, priority, category, and start_time."""
    task = make_task(name="Evening walk", duration=30, priority=4,
                     category="walk", start_time="18:00",
                     frequency="daily", due_date=date.today())
    next_task = task.next_occurrence()
    assert next_task.name          == task.name
    assert next_task.duration_minutes == task.duration_minutes
    assert next_task.priority      == task.priority
    assert next_task.category      == task.category
    assert next_task.start_time    == task.start_time


# ---------------------------------------------------------------------------
# Conflict detection tests
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_overlapping_tasks():
    """Two tasks whose time windows overlap should produce exactly one conflict warning."""
    owner = make_owner()
    pet   = make_pet()
    owner.add_pet(pet)
    # Breakfast 08:00–08:10, Meds 08:05–08:10 → overlap
    pet.add_task(make_task("Breakfast", duration=10, priority=5, start_time="08:00"))
    pet.add_task(make_task("Meds",      duration=5,  priority=5, start_time="08:05"))

    scheduler = Scheduler(owner=owner, pet=pet)
    scheduler.generate_plan()
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "Breakfast" in conflicts[0]
    assert "Meds"      in conflicts[0]


def test_detect_conflicts_no_warning_for_adjacent_tasks():
    """Tasks that touch end-to-start (not overlapping) should not produce a warning."""
    owner = make_owner()
    pet   = make_pet()
    owner.add_pet(pet)
    # Walk 08:00–08:30, then Breakfast 08:30–08:40 — adjacent, no overlap
    pet.add_task(make_task("Walk",      duration=30, priority=5, start_time="08:00"))
    pet.add_task(make_task("Breakfast", duration=10, priority=5, start_time="08:30"))

    scheduler = Scheduler(owner=owner, pet=pet)
    scheduler.generate_plan()
    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_ignores_tasks_without_start_time():
    """Tasks with no start_time are excluded from conflict checking."""
    owner = make_owner()
    pet   = make_pet()
    owner.add_pet(pet)
    pet.add_task(make_task("Bath",   duration=40, priority=3, start_time=None))
    pet.add_task(make_task("Groom",  duration=30, priority=3, start_time=None))

    scheduler = Scheduler(owner=owner, pet=pet)
    scheduler.generate_plan()
    assert scheduler.detect_conflicts() == []


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_generate_plan_with_no_tasks_returns_empty():
    """A pet with no tasks produces an empty schedule without error."""
    owner = make_owner()
    pet   = make_pet()
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner, pet=pet)
    result = scheduler.generate_plan()
    assert result == []
    assert scheduler.scheduled_tasks   == []
    assert scheduler.unscheduled_tasks == []


def test_generate_plan_skips_tasks_exceeding_available_time():
    """A single task longer than the owner's available time is not scheduled."""
    owner = make_owner(minutes=10)
    pet   = make_pet()
    owner.add_pet(pet)
    pet.add_task(make_task("Long bath", duration=60, priority=5))

    scheduler = Scheduler(owner=owner, pet=pet)
    scheduler.generate_plan()
    assert scheduler.scheduled_tasks   == []
    assert len(scheduler.unscheduled_tasks) == 1


def test_filter_tasks_by_completion_status():
    """filter_tasks(completed=False) returns only incomplete tasks."""
    owner = make_owner()
    pet   = make_pet()
    owner.add_pet(pet)
    t1 = make_task("Walk")
    t2 = make_task("Feed", category="feed")
    t1.mark_complete()
    pet.add_task(t1)
    pet.add_task(t2)

    scheduler = Scheduler(owner=owner, pet=pet)
    incomplete = scheduler.filter_tasks(completed=False)
    assert len(incomplete) == 1
    assert incomplete[0].name == "Feed"


def test_filter_tasks_by_category():
    """filter_tasks(category='walk') returns only walk tasks."""
    owner = make_owner()
    pet   = make_pet()
    owner.add_pet(pet)
    pet.add_task(make_task("Morning walk", category="walk"))
    pet.add_task(make_task("Breakfast",    category="feed"))
    pet.add_task(make_task("Evening walk", category="walk"))

    scheduler = Scheduler(owner=owner, pet=pet)
    walks = scheduler.filter_tasks(category="walk")
    assert len(walks) == 2
    assert all(t.category == "walk" for t in walks)
