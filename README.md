# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

### What the tests cover

| Area | Tests |
|---|---|
| **Task completion** | `mark_complete()` flips `completed` to `True` |
| **Pet task list** | `add_task()` correctly grows the task count |
| **Sorting** | `sort_by_time()` returns tasks in chronological order; tasks without a time go last; empty list is safe |
| **Recurrence** | Daily tasks produce a next occurrence due tomorrow; weekly tasks due in 7 days; one-off tasks return `None`; next occurrence inherits all attributes; `mark_task_complete()` auto-appends the follow-up to the pet |
| **Conflict detection** | Overlapping windows produce a warning; adjacent (non-overlapping) tasks do not; tasks without `start_time` are excluded from conflict checks |
| **Edge cases** | Pet with no tasks returns an empty plan; a task longer than available time is skipped; `filter_tasks` filters correctly by completion status and category |

**Confidence level: ★★★★☆**
The core scheduling, sorting, recurrence, and conflict-detection paths are all covered.
The main gap is the Streamlit UI layer (session state interactions) which is not unit-tested,
and multi-pet conflict scenarios (tasks for different pets scheduled at the same time).

---

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
