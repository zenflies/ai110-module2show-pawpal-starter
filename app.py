import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ---------------------------------------------------------------------------
# Session state bootstrap
# ---------------------------------------------------------------------------
# Streamlit reruns this entire script on every interaction. We check once
# whether our objects already exist in session_state before creating them,
# so data persists across reruns within the same browser session.

if "owner" not in st.session_state:
    st.session_state.owner = None   # set for real in the Owner Setup section

# ---------------------------------------------------------------------------
# Section 1: Owner Setup
# ---------------------------------------------------------------------------
st.header("1. Owner Setup")

with st.form("owner_form"):
    owner_name = st.text_input("Your name", value="Jordan")
    available_minutes = st.number_input(
        "Time available today (minutes)", min_value=10, max_value=480, value=90
    )
    submitted = st.form_submit_button("Save owner")

if submitted:
    # Always recreate the owner when the form is saved so edits take effect.
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
    species = st.selectbox("Species", ["dog", "cat", "other"])
    age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
    add_pet_btn = st.form_submit_button("Add pet")

if add_pet_btn:
    # Check we're not adding a duplicate name
    existing_names = [p.name.lower() for p in owner.get_pets()]
    if pet_name.lower() in existing_names:
        st.warning(f"A pet named '{pet_name}' already exists.")
    else:
        new_pet = Pet(name=pet_name, species=species, age_years=int(age))
        owner.add_pet(new_pet)          # wires the back-reference automatically
        st.success(f"Added {species} '{pet_name}'!")

pets = owner.get_pets()
if pets:
    st.write("**Current pets:**")
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
        task_name = st.text_input("Task name", value="Morning walk")
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.slider("Priority (1 = low, 5 = high)", min_value=1, max_value=5, value=3)
        category = st.selectbox(
            "Category", ["walk", "feed", "meds", "grooming", "enrichment", "other"]
        )
        add_task_btn = st.form_submit_button("Add task")

    if add_task_btn:
        target_pet = next(p for p in pets if p.name == target_pet_name)
        target_pet.add_task(
            Task(name=task_name, duration_minutes=int(duration),
                 priority=priority, category=category)
        )
        st.success(f"Added task '{task_name}' to {target_pet_name}.")

    # Show current tasks grouped by pet
    for pet in pets:
        tasks = pet.get_tasks()
        if tasks:
            st.markdown(f"**{pet.name}'s tasks:**")
            st.table([
                {"Task": t.name, "Category": t.category,
                 "Duration (min)": t.duration_minutes, "Priority": t.priority}
                for t in tasks
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

            st.subheader(f"{pet.name}'s Plan")
            if scheduler.scheduled_tasks:
                st.table([
                    {"Task": t.name, "Category": t.category,
                     "Duration (min)": t.duration_minutes, "Priority": t.priority,
                     "High Priority": "yes" if t.is_high_priority() else "no"}
                    for t in scheduler.scheduled_tasks
                ])
                st.metric("Time used", f"{scheduler.get_total_duration()} min",
                          delta=f"{owner.get_availability() - scheduler.get_total_duration()} min remaining")
            else:
                st.warning(f"No tasks fit within {owner.get_availability()} minutes.")

            if scheduler.unscheduled_tasks:
                with st.expander("Tasks that didn't fit today"):
                    for t in scheduler.unscheduled_tasks:
                        st.markdown(f"- **{t.name}** ({t.duration_minutes} min, priority {t.priority})")

            st.markdown("---")
            with st.expander("Full explanation"):
                st.text(scheduler.explain_plan())
