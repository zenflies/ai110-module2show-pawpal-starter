from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
jordan = Owner(name="Jordan", available_minutes=120)
jordan.add_preference("morning walks")
jordan.add_preference("no tasks after 9pm")

mochi    = Pet(name="Mochi",    species="dog", age_years=3)
whiskers = Pet(name="Whiskers", species="cat", age_years=5)

jordan.add_pet(mochi)
jordan.add_pet(whiskers)

# ---------------------------------------------------------------------------
# Tasks for Mochi — added OUT OF ORDER to exercise sort_by_time
# ---------------------------------------------------------------------------
mochi.add_task(Task(
    name="Evening walk",     duration_minutes=20, priority=3, category="walk",
    start_time="18:00", frequency="daily", due_date=date.today()))

mochi.add_task(Task(
    name="Flea medication",  duration_minutes=5,  priority=4, category="meds",
    start_time="09:30"))

mochi.add_task(Task(
    name="Morning walk",     duration_minutes=30, priority=5, category="walk",
    start_time="07:00", frequency="daily", due_date=date.today()))

mochi.add_task(Task(
    name="Breakfast",        duration_minutes=10, priority=5, category="feed",
    start_time="07:45", frequency="daily", due_date=date.today()))

mochi.add_task(Task(
    name="Fetch session",    duration_minutes=20, priority=2, category="enrichment",
    start_time="17:00"))

mochi.add_task(Task(
    name="Bath",             duration_minutes=40, priority=1, category="grooming"))

# Tasks for Whiskers — intentional time conflict between Breakfast and Meds
whiskers.add_task(Task(
    name="Breakfast",        duration_minutes=10, priority=5, category="feed",
    start_time="08:00", frequency="daily", due_date=date.today()))

whiskers.add_task(Task(
    name="Morning meds",     duration_minutes=5,  priority=5, category="meds",
    start_time="08:05"))   # <-- overlaps with Breakfast (08:00–08:10)

whiskers.add_task(Task(
    name="Litter cleaning",  duration_minutes=10, priority=4, category="grooming",
    start_time="10:00", frequency="weekly", due_date=date.today()))

whiskers.add_task(Task(
    name="Laser play",       duration_minutes=15, priority=2, category="enrichment",
    start_time="17:30"))

# ---------------------------------------------------------------------------
# DEMO 1 — generate and print schedule for every pet
# ---------------------------------------------------------------------------
print("=" * 60)
print("            PAWPAL+ — TODAY'S SCHEDULE")
print("=" * 60)

schedulers = {}
for pet in jordan.get_pets():
    s = Scheduler(owner=jordan, pet=pet)
    s.generate_plan()
    schedulers[pet.name] = s
    print()
    print(s.explain_plan())
    print("-" * 60)

# ---------------------------------------------------------------------------
# DEMO 2 — sort_by_time: show Mochi's tasks in chronological order
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("   MOCHI'S TASKS SORTED BY START TIME")
print("=" * 60)
mochi_scheduler = schedulers["Mochi"]
sorted_tasks = Scheduler.sort_by_time(mochi.get_tasks())
for t in sorted_tasks:
    time_label = t.start_time if t.start_time else "(no time set)"
    print(f"  {time_label:>8}  {t.name:<20}  {t.duration_minutes} min  priority {t.priority}")

# ---------------------------------------------------------------------------
# DEMO 3 — filter_tasks: show only incomplete walk tasks for Mochi
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("   MOCHI'S INCOMPLETE WALK TASKS")
print("=" * 60)
walk_tasks = mochi_scheduler.filter_tasks(completed=False, category="walk")
if walk_tasks:
    for t in walk_tasks:
        print(f"  - {t.name}  ({t.frequency})")
else:
    print("  None.")

# ---------------------------------------------------------------------------
# DEMO 4 — recurring tasks: complete Morning Walk → next occurrence is added
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("   RECURRING TASK DEMO")
print("=" * 60)
morning_walk = next(t for t in mochi.get_tasks() if t.name == "Morning walk")
print(f"  Before: Mochi has {len(mochi.get_tasks())} tasks.")
print(f"  Completing '{morning_walk.name}' (frequency={morning_walk.frequency}) ...")
mochi_scheduler.mark_task_complete(morning_walk)
print(f"  After:  Mochi has {len(mochi.get_tasks())} tasks.")
new_occurrence = mochi.get_tasks()[-1]
print(f"  Next occurrence due: {new_occurrence.due_date}")

# ---------------------------------------------------------------------------
# DEMO 5 — detect_conflicts: Whiskers has two tasks that overlap
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("   CONFLICT DETECTION — WHISKERS")
print("=" * 60)
whiskers_scheduler = schedulers["Whiskers"]
conflicts = whiskers_scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  WARNING: {warning}")
else:
    print("  No conflicts found.")

print()
