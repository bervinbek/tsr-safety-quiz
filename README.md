# SAF Safety Quiz Streamlit Application

This project is a web-based safety quiz application built with Streamlit. It is designed to test a user's knowledge on a safety scenario, provide feedback, and record their results. The application includes a separate admin dashboard for viewing and managing participant data.

---

## Features

- **Participant Details Form**: Collects user information before starting the quiz.
- **Timed Quiz Question**: A multi-line text input for the user to answer a scenario-based question within a 60-second time limit.
- **Automated Grading**: The application scores the answer and provides feedback on strengths, weaknesses, and areas for improvement.
- **Retry Mechanism**: Users must score at least 9 out of 10 to pass. If they fail, they are shown feedback and must retry the quiz.
- **Admin Dashboard**: A password-protected page to view all participant submissions in a table.
- **Data Export**: Admins can download the complete dataset as an `.xlsx` file.
- **Telegram Integration (Placeholder)**: A button to simulate sending monthly quiz reminders to participants via Telegram.

---

## Project Structure

```
.
├── data/
│   └── participants.csv  (auto-generated)
├── .venv/                (local virtual environment)
├── app.py                (main streamlit application)
├── instructions.md       (original project requirements)
├── requirements.txt      (python dependencies)
├── styles.css            (custom CSS for styling)
└── README.md             (this file)
```

---

## Getting Started

Follow these instructions to set up and run the project on your local machine.

### Prerequisites

- Python 3.8 or higher

### Installation

1.  **Clone the repository or download the source code.**

2.  **Navigate to the project directory:**
    ```bash
    cd path/to/01_Safety_Quiz
    ```

3.  **Create and activate a Python virtual environment:**

    *   **Windows (Command Prompt):**
        ```bash
        python -m venv .venv
        .venv\Scripts\activate
        ```
    *   **Windows (PowerShell):**
        ```bash
        python -m venv .venv
        .venv\Scripts\Activate.ps1
        ```
    *   **macOS/Linux:**
        ```bash
        python3 -m venv .venv
        source .venv/bin/activate
        ```

4.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

1.  **Ensure your virtual environment is activated.**

2.  **Run the Streamlit app from the terminal:**
    ```bash
    streamlit run app.py
    ```

3.  The application will open in a new tab in your default web browser.

---
