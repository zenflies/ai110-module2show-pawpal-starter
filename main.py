from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
jordan = Owner(name="Jordan", available_minutes=90)
jordan.add_preference("morning walks")
jordan.add_preference("no tasks after 9pm")

mochi = Pet(name="Mochi", species="dog", age_years=3)
whiskers = Pet(name="Whiskers", species="cat", age_years=5)

jordan.add_pet(mochi)
jordan.add_pet(whiskers)

# --- Tasks for Mochi (dog) ---
mochi.add_task(Task(name="Morning walk",    duration_minutes=30, priority=5, category="walk"))
mochi.add_task(Task(name="Breakfast",       duration_minutes=10, priority=5, category="feed"))
mochi.add_task(Task(name="Flea medication", duration_minutes=5,  priority=4, category="meds"))
mochi.add_task(Task(name="Fetch session",   duration_minutes=20, priority=2, category="enrichment"))
mochi.add_task(Task(name="Bath",            duration_minutes=40, priority=1, category="grooming"))

# --- Tasks for Whiskers (cat) ---
whiskers.add_task(Task(name="Breakfast",      duration_minutes=10, priority=5, category="feed"))
whiskers.add_task(Task(name="Litter cleaning",duration_minutes=10, priority=4, category="grooming"))
whiskers.add_task(Task(name="Laser play",     duration_minutes=15, priority=2, category="enrichment"))

# --- Generate and print schedules ---
print("=" * 50)
print("         PAWPAL+ — TODAY'S SCHEDULE")
print("=" * 50)

for pet in jordan.get_pets():
    scheduler = Scheduler(owner=jordan, pet=pet)
    scheduler.generate_plan()
    print()
    print(scheduler.explain_plan())
    print("-" * 50)
