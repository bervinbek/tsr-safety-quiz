# Streamlit SAF Safety Quiz Web App – Coding Agent Instructions

## Objective
Build a professional-looking Streamlit web app with **no emojis** and a **modern, clean font**. The app must have a **sequential page flow** for the quiz, plus an **admin page** for viewing results and sending reminders.

---

## General Styling Requirements
- **No emojis** anywhere in the UI.
- Use a **modern, clean font** such as *Inter*, *Roboto*, or *Lato*.
- Layout should be minimalistic, with consistent spacing and alignment.
- Ensure all pages adapt to desktop and mobile displays.
- Use Streamlit's `st.session_state` to manage multi-page navigation and data persistence.
- Make all buttons and inputs consistent in style.

---

## Page 1 – Participant Details
- Title: `SAF Safety Quiz – Participant Details`
- Inputs:
  - Dropdown: `UNIT`
  - Dropdown: `COY`
  - Dropdown: `PLATOON`
  - Text Input: `Rank Name`
  - Text Input: `Telegram Handle`
- Button: **Next** → goes to Page 2
- All fields must be required before proceeding.

---

## Page 2 – Safety Scenario Question
- Display **Question**:

  > "Describe the actions when your buddy trips and fall during a march and has difficulty walking but insists to carry on"

- Time Limit:
  - Show **20-second countdown** with a visible **progress bar** decreasing in real-time.
- Input:
  - Multi-line text box for user to type their answer.
- Auto-lock the text input when time reaches zero.
- Button: **Submit Answer** → triggers grading.

---

## Answer Grading Logic
- Grade the answer **critically** out of 10 points.
- Provide **three outputs**:
  - **Strength** (positive aspects of answer)
  - **Weakness** (what was missing or incorrect)
  - **Improvement** (specific suggestions for a better answer)
- Display results to the user after grading.

---

## Page 3 – Completion Screen
- Show a message:  
  `You have completed the SAF Safety Quiz. Your score is: X/10`
- Include a summary of their strengths, weaknesses, and improvement points.
- Button: **Finish** → returns to Page 1.

---

## Admin Page
- Accessible from a separate link or sidebar.
- Displays the **database** of all participants who have completed the quiz in **Excel table format**.
- Button: **Assign Monthly**:
  - Sends a Telegram message with a **placeholder quiz link** to each participant's Telegram handle.
  - Use placeholder for Telegram Bot ID: `BOT_ID_HERE`
  - Actual sending logic can be simulated (leave as a function with `pass` or comment).

---

## Data Storage
- Store quiz answers and participant details in a **CSV or SQLite database**.
- Ensure admin can download the full dataset as an `.xlsx` file.

---

## Technical Notes
- Use `streamlit` for UI.
- Use `pandas` for data handling.
- Use `python-telegram-bot` for sending messages (placeholder only).
- Use `time` or `threading` to implement the 20-second countdown timer.
- Use **server-side logic** to prevent bypassing time limit.

---

## File Structure Example
app.py
data/
participants.csv
styles.css


---

## Deliverables
- Fully functional Streamlit app in a single `app.py` file.
- Styled according to requirements.
- Admin page with Excel export and placeholder Telegram sending function.