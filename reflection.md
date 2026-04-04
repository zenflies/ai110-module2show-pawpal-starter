# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

A user should be able to register a pet with the app, schedule an activity such as a walk, and receive reminders on basic pet care.

Classes: Owner (stores owner information), Pet (stores pet information), Task (outlines the structure for a generic task), Schedule (defines a streamline for multiple tasks to fulfill a day)

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Pet-Owner linkage was created bidirectionally for additional clarity.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The conflict detector only flags tasks whose *time windows overlap* (start_time + duration_minutes).
It does not detect softer conflicts such as two high-effort tasks back-to-back with no rest, or tasks
that share a pet but whose combined duration would exhaust the owner's energy even if they don't
strictly overlap on the clock.

This tradeoff is reasonable for the current scope: a lightweight pet-care planner needs to warn about
hard scheduling impossibilities (two things literally at the same time) without requiring the owner
to model fatigue or travel time. A future version could add a minimum "buffer" gap between tasks to
catch near-conflicts, but exact-overlap detection covers the most obvious errors with minimal complexity.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used the AI tools throughout the entire process, including design brainstorming and debugging. I would run the structured code myself, identifying any flaws and worked through with CoPilot to detect anomalies.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

The AI at one point had suggested changes that obstructed the functionality of task priorities. I evaluated this through unit testing to identify if the sorted order of some sample tasks make sense.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested behaviors that related to the core functionalities of the program, especially pertaining to the creation of a task and list scheduling. These tests are especially important for human-in-the-loop verification, proving the functionality works. 

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am confident the scheduler works, a few test cases I would try would to be many tasks at once during a day and trying an abnormally long task.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with the creation of a schedule that incorporates the tasks I create.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would create a more complex AI layout to prevent simple scrolling to navigate the page. 

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

AI tools are highly capable, but they are not infallible. It is ultimately the responsibility on the person to understand the subsystem and use it as a tool.