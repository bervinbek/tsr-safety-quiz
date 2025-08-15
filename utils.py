import streamlit as st
import pandas as pd
import os
from io import BytesIO

# --- Constants ---
DATA_DIR = "data"
CSV_PATH = os.path.join(DATA_DIR, "participants.csv")

# --- Helper Functions ---

def initialize_data_storage():
    """Creates the data directory and CSV file if they don't exist."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(CSV_PATH):
        df = pd.DataFrame(columns=[
            "UNIT", "COY", "PLATOON", "Rank Name", "Telegram Handle", 
            "Answer", "Score", "Strength", "Weakness", "Improvement", "Timestamp"
        ])
        df.to_csv(CSV_PATH, index=False)

def load_custom_css():
    """Loads and injects custom CSS for styling."""
    try:
        with open("styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("styles.css not found. Using default styles.")

def grade_answer(answer: str) -> dict:
    """
    Grades the user's answer critically.
    This is a placeholder for a more advanced grading model.
    """
    # Simple keyword-based grading for demonstration
    score = 0
    strength = "No specific strengths identified."
    weakness = "Lacked detail on critical safety procedures."
    improvement = "A better answer would include checking for consciousness, calling for a medic, and not moving the injured person."

    if "medic" in answer.lower() or "call for help" in answer.lower():
        score += 4
    if "check" in answer.lower() or "assess" in answer.lower():
        score += 3
    if "conscious" in answer.lower() or "breathing" in answer.lower():
        score += 3
    
    if score >= 7:
        strength = "Good identification of initial response steps."
        weakness = "Could be more specific on who to call and what to check."
    if score >= 4:
        improvement = "Specify calling the platoon medic or section commander and checking for breathing and responsiveness."

    return {
        "Score": score,
        "Strength": strength,
        "Weakness": weakness,
        "Improvement": improvement
    }

def save_participant_data(data: dict):
    """Saves participant data to the CSV file."""
    df = pd.read_csv(CSV_PATH)
    new_entry = pd.DataFrame([data])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)

def send_telegram_message(telegram_handle: str, message: str):
    """Placeholder function to simulate sending a Telegram message."""
    # In a real application, you would use the python-telegram-bot library here
    # e.g., bot = telegram.Bot(token="BOT_ID_HERE")
    #       bot.send_message(chat_id=telegram_handle, text=message)
    st.info(f"Simulating sending message to {telegram_handle}: '{message}'")
    pass
