import json
import os
from PIL import Image
import streamlit as st

# Configuration file paths
CONFIG_DIR = "data"
CONFIG_FILE = os.path.join(CONFIG_DIR, "quiz_config.json")
IMAGE_FILE = os.path.join(CONFIG_DIR, "scenario_image.png")

# Default quiz configuration
DEFAULT_CONFIG = {
    "question_text": "Describe the actions when your buddy trips and fall during a march and has difficulty walking but insists to carry on.",
    "passing_score": 9,
    "time_limit": 60,
    "scenario_title": "Safety Scenario Question",
    "image_enabled": True,
    "image_prompt": "Photorealistic scene of two NSF soldiers in modern SAF No.4 pixelated camouflage. One soldier is kneeling on a tarmac road, visibly injured, while the other supports/helps him. Distinctive Singapore pixel pattern, field pack with metal frame, black Frontier boots. Background: SAF training area with visible infrastructure during a route march."
}

def load_quiz_config():
    """Load quiz configuration from file or return defaults."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
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

def save_scenario_image(image):
    """Save the scenario image to file."""
    try:
        # Ensure directory exists
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        
        # Save image
        if image:
            image.save(IMAGE_FILE, "PNG")
            return True
    except Exception as e:
        st.error(f"Error saving image: {e}")
        return False

def load_scenario_image():
    """Load the saved scenario image if it exists."""
    try:
        if os.path.exists(IMAGE_FILE):
            return Image.open(IMAGE_FILE)
    except Exception as e:
        st.error(f"Error loading image: {e}")
    return None

def delete_scenario_image():
    """Delete the saved scenario image."""
    try:
        if os.path.exists(IMAGE_FILE):
            os.remove(IMAGE_FILE)
            return True
    except Exception as e:
        st.error(f"Error deleting image: {e}")
    return False