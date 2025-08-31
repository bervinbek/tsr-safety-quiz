import json
import os
from PIL import Image
import streamlit as st

# Configuration file paths
CONFIG_DIR = "data"
CONFIG_FILE = os.path.join(CONFIG_DIR, "quiz_config.json")
QUESTIONS_DIR = os.path.join(CONFIG_DIR, "questions")

# Default quiz configuration
DEFAULT_CONFIG = {
    "passing_score": 9,
    "time_limit": 60,
    "questions": [
        {
            "id": "q1",
            "scenario_title": "Safety Scenario Question",
            "question_text": "Describe the actions when your buddy trips and fall during a march and has difficulty walking but insists to carry on.",
            "image_enabled": True,
            "image_prompt": "Photorealistic scene of two NSF soldiers in modern SAF No.4 pixelated camouflage. One soldier is kneeling on a tarmac road, visibly injured, while the other supports/helps him. Distinctive Singapore pixel pattern, field pack with metal frame, black Frontier boots. Background: SAF training area with visible infrastructure during a route march.",
            "image_file": "q1_image.png"
        }
    ]
}

def load_quiz_config():
    """Load quiz configuration from file or return defaults."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                
                # Handle backward compatibility - convert old format to new
                if "question_text" in config and "questions" not in config:
                    # Old format - convert to new format with questions array
                    old_question = {
                        "id": "q1",
                        "scenario_title": config.get("scenario_title", "Safety Scenario Question"),
                        "question_text": config.get("question_text", ""),
                        "image_enabled": config.get("image_enabled", True),
                        "image_prompt": config.get("image_prompt", ""),
                        "image_file": "q1_image.png"
                    }
                    config["questions"] = [old_question]
                    # Remove old keys
                    for key in ["question_text", "scenario_title", "image_enabled", "image_prompt"]:
                        config.pop(key, None)
                
                # Merge with defaults to ensure all keys exist
                for key, value in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = value
                return config
    except Exception as e:
        st.error(f"Error loading quiz config: {e}")
    
    return DEFAULT_CONFIG.copy()

def save_quiz_config(config):
    """Save quiz configuration to file."""
    try:
        # Ensure directory exists
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        
        # Save configuration
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        
        return True
    except Exception as e:
        st.error(f"Error saving quiz config: {e}")
        return False

def save_scenario_image(image, question_id="q1"):
    """Save the scenario image to file for a specific question."""
    try:
        # Ensure directory exists
        if not os.path.exists(QUESTIONS_DIR):
            os.makedirs(QUESTIONS_DIR)
        
        # Save image with question ID
        if image:
            image_file = os.path.join(QUESTIONS_DIR, f"{question_id}_image.png")
            image.save(image_file, "PNG")
            return True
    except Exception as e:
        st.error(f"Error saving image: {e}")
        return False

def load_scenario_image(question_id="q1"):
    """Load the saved scenario image for a specific question if it exists."""
    try:
        image_file = os.path.join(QUESTIONS_DIR, f"{question_id}_image.png")
        if os.path.exists(image_file):
            return Image.open(image_file)
        # Fallback to old location for backward compatibility
        old_file = os.path.join(CONFIG_DIR, "scenario_image.png")
        if os.path.exists(old_file) and question_id == "q1":
            return Image.open(old_file)
    except Exception as e:
        st.error(f"Error loading image: {e}")
    return None

def delete_scenario_image(question_id="q1"):
    """Delete the saved scenario image for a specific question."""
    try:
        image_file = os.path.join(QUESTIONS_DIR, f"{question_id}_image.png")
        if os.path.exists(image_file):
            os.remove(image_file)
            return True
        # Also try old location for backward compatibility
        old_file = os.path.join(CONFIG_DIR, "scenario_image.png")
        if os.path.exists(old_file) and question_id == "q1":
            os.remove(old_file)
            return True
    except Exception as e:
        st.error(f"Error deleting image: {e}")
    return False

def get_all_questions():
    """Get all questions from the configuration."""
    config = load_quiz_config()
    return config.get("questions", [])

def get_question_by_id(question_id):
    """Get a specific question by its ID."""
    questions = get_all_questions()
    for q in questions:
        if q.get("id") == question_id:
            return q
    return None

def add_question(question):
    """Add a new question to the configuration."""
    config = load_quiz_config()
    if "questions" not in config:
        config["questions"] = []
    
    # Generate new ID
    existing_ids = [q.get("id", "") for q in config["questions"]]
    new_id = f"q{len(existing_ids) + 1}"
    while new_id in existing_ids:
        new_id = f"q{int(new_id[1:]) + 1}"
    
    question["id"] = new_id
    config["questions"].append(question)
    return save_quiz_config(config), new_id

def update_question(question_id, updated_question):
    """Update an existing question."""
    config = load_quiz_config()
    questions = config.get("questions", [])
    
    for i, q in enumerate(questions):
        if q.get("id") == question_id:
            updated_question["id"] = question_id
            questions[i] = updated_question
            config["questions"] = questions
            return save_quiz_config(config)
    return False

def delete_question(question_id):
    """Delete a question and its associated image."""
    config = load_quiz_config()
    questions = config.get("questions", [])
    
    # Don't delete if it's the only question
    if len(questions) <= 1:
        return False
    
    # Remove the question
    config["questions"] = [q for q in questions if q.get("id") != question_id]
    
    # Delete associated image if exists
    delete_scenario_image(question_id)
    
    return save_quiz_config(config)