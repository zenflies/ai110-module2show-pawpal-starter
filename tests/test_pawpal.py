from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    task = Task(name="Morning walk", duration_minutes=30, priority=5, category="walk")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", age_years=3)
    assert len(pet.get_tasks()) == 0
    pet.add_task(Task(name="Breakfast", duration_minutes=10, priority=5, category="feed"))
    pet.add_task(Task(name="Fetch session", duration_minutes=20, priority=2, category="enrichment"))
    assert len(pet.get_tasks()) == 2
