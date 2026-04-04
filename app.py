from datetime import date
import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state bootstrap
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None

# ---------------------------------------------------------------------------
# Section 1: Owner Setup
# ---------------------------------------------------------------------------
st.header("1. Owner Setup")

with st.form("owner_form"):
    owner_name        = st.text_input("Your name", value="Jordan")
    available_minutes = st.number_input(
        "Time available today (minutes)", min_value=10, max_value=480, value=90
    )
    submitted = st.form_submit_button("Save owner")

if submitted:
    st.session_state.owner = Owner(name=owner_name, available_minutes=int(available_minutes))
    st.success(f"Owner '{owner_name}' saved with {available_minutes} min available.")

if st.session_state.owner is None:
    st.info("Fill in your details above to get started.")
    st.stop()

owner: Owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Section 2: Add Pets
# ---------------------------------------------------------------------------
st.header("2. Your Pets")

with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name", value="Mochi")
    species  = st.selectbox("Species", ["dog", "cat", "other"])
    age      = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
    add_pet_btn = st.form_submit_button("Add pet")

if add_pet_btn:
    existing_names = [p.name.lower() for p in owner.get_pets()]
    if pet_name.lower() in existing_names:
        st.warning(f"A pet named '{pet_name}' already exists.")
    else:
        owner.add_pet(Pet(name=pet_name, species=species, age_years=int(age)))
        st.success(f"Added {species} '{pet_name}'!")

pets = owner.get_pets()
if pets:
    for p in pets:
        st.markdown(f"- **{p.name}** ({p.species}, {p.age_years} yrs)")
else:
    st.info("No pets yet — add one above.")

# ---------------------------------------------------------------------------
# Section 3: Add Tasks
# ---------------------------------------------------------------------------
st.header("3. Add Tasks")

if not pets:
    st.info("Add a pet first before adding tasks.")
else:
    with st.form("add_task_form"):
        target_pet_name = st.selectbox("Assign to pet", [p.name for p in pets])
        task_name  = st.text_input("Task name", value="Morning walk")
        duration   = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority   = st.slider("Priority (1 = low, 5 = high)", min_value=1, max_value=5, value=3)
        category   = st.selectbox(
            "Category", ["walk", "feed", "meds", "grooming", "enrichment", "other"]
        )
        start_time = st.text_input(
            "Start time (HH:MM, optional)", value="",
            help="Leave blank if this task has no fixed time."
        )
        frequency  = st.selectbox("Frequency", ["once", "daily", "weekly"])
        add_task_btn = st.form_submit_button("Add task")

    if add_task_btn:
        cleaned_time = start_time.strip() or None
        # Validate HH:MM format if provided
        if cleaned_time:
            parts = cleaned_time.split(":")
            if len(parts) != 2 or not all(p.isdigit() for p in parts):
                st.error("Start time must be in HH:MM format (e.g. 08:30).")
                cleaned_time = None

        if cleaned_time is not None or not start_time.strip():
            target_pet = next(p for p in pets if p.name == target_pet_name)
            target_pet.add_task(Task(
                name=task_name,
                duration_minutes=int(duration),
                priority=priority,
                category=category,
                start_time=cleaned_time,
                frequency=frequency,
                due_date=date.today() if frequency != "once" else None,
            ))
            st.success(f"Added '{task_name}' to {target_pet_name}.")

    # Show current tasks per pet, sorted chronologically
    for pet in pets:
        raw_tasks = pet.get_tasks()
        if not raw_tasks:
            continue
        st.markdown(f"**{pet.name}'s tasks** ({len(raw_tasks)} total):")
        sorted_tasks = Scheduler.sort_by_time(raw_tasks)
        st.table([
            {
                "Time":     t.start_time or "—",
                "Task":     t.name,
                "Category": t.category,
                "Min":      t.duration_minutes,
                "Priority": t.priority,
                "Repeat":   t.frequency,
                "Done":     "yes" if t.completed else "no",
            }
            for t in sorted_tasks
        ])

# ---------------------------------------------------------------------------
# Section 4: Generate Schedule
# ---------------------------------------------------------------------------
st.header("4. Today's Schedule")

if not pets or all(len(p.get_tasks()) == 0 for p in pets):
    st.info("Add at least one task before generating a schedule.")
else:
    if st.button("Generate schedule"):
        for pet in pets:
            if not pet.get_tasks():
                continue

            scheduler = Scheduler(owner=owner, pet=pet)
            scheduler.generate_plan()

            st.subheader(f"🐾 {pet.name}'s Plan")

            # --- Conflict warnings (shown first so they're hard to miss) ---
            conflicts = scheduler.detect_conflicts()
            if conflicts:
                st.error(
                    f"**{len(conflicts)} scheduling conflict(s) detected for {pet.name}. "
                    f"Please adjust the task times below.**"
                )
                for warning in conflicts:
                    # Parse out the two task names for a friendlier message
                    st.warning(f"⏰ {warning}")

            # --- Scheduled tasks, sorted by start time ---
            if scheduler.scheduled_tasks:
                sorted_scheduled = Scheduler.sort_by_time(scheduler.scheduled_tasks)
                rows = []
                for t in sorted_scheduled:
                    rows.append({
                        "Time":          t.start_time or "—",
                        "Task":          t.name,
                        "Category":      t.category,
                        "Duration (min)": t.duration_minutes,
                        "Priority":      t.priority,
                        "High Priority": "yes" if t.is_high_priority() else "no",
                        "Repeat":        t.frequency,
                    })
                st.table(rows)

                used      = scheduler.get_total_duration()
                available = owner.get_availability()
                st.metric(
                    "Time used",
                    f"{used} min",
                    delta=f"{available - used} min remaining",
                )
            else:
                st.warning(f"No tasks fit within {owner.get_availability()} minutes.")

            # --- Tasks that didn't fit ---
            if scheduler.unscheduled_tasks:
                with st.expander(f"Tasks that didn't fit ({len(scheduler.unscheduled_tasks)})"):
                    for t in scheduler.unscheduled_tasks:
                        st.markdown(
                            f"- **{t.name}** — {t.duration_minutes} min, "
                            f"priority {t.priority}"
                        )

            # --- Full text explanation ---
            with st.expander("Full explanation"):
                st.text(scheduler.explain_plan())

            st.divider()

        # --- Filter panel (across all pets) ---
        st.subheader("Filter Tasks")
        col1, col2 = st.columns(2)
        with col1:
            filter_pet_name = st.selectbox(
                "Filter by pet", [p.name for p in pets], key="filter_pet"
            )
        with col2:
            filter_status = st.selectbox(
                "Filter by status", ["all", "incomplete", "complete"], key="filter_status"
            )

        filter_pet = next(p for p in pets if p.name == filter_pet_name)
        filter_scheduler = Scheduler(owner=owner, pet=filter_pet)
        completed_arg = {"all": None, "incomplete": False, "complete": True}[filter_status]
        filtered = filter_scheduler.filter_tasks(completed=completed_arg)

        if filtered:
            st.table([
                {
                    "Task":     t.name,
                    "Category": t.category,
                    "Min":      t.duration_minutes,
                    "Priority": t.priority,
                    "Repeat":   t.frequency,
                    "Done":     "yes" if t.completed else "no",
                }
                for t in filtered
            ])
        else:
            st.info("No tasks match the selected filter.")
