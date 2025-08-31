import streamlit as st
import pandas as pd
import random
from utils import initialize_data_storage, grade_answer, save_participant_data
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from image_generator import get_cached_scenario_image
from quiz_config import load_quiz_config, load_scenario_image, get_all_questions

def page_participant_details():
    """Page 1: Collects participant details."""
    st.header("SAF Safety Quiz – Participant Details")

    with st.form("details_form"):
        unit = st.selectbox("UNIT", ["-", "1 SIR", "2 SIR", "3 SIR"])
        coy = st.selectbox("COY", ["-", "Alpha", "Bravo", "Charlie"])
        platoon = st.selectbox("PLATOON", ["-", "1", "2", "3", "4"])
        rank_name = st.text_input("Rank Name")
        telegram_handle = st.text_input("Telegram Handle (e.g., @username)")
        
        submitted = st.form_submit_button("Next")

        if submitted:
            if unit == "-" or coy == "-" or platoon == "-" or not rank_name or not telegram_handle:
                st.error("All fields are required.")
            else:
                st.session_state.participant_details = {
                    "UNIT": unit,
                    "COY": coy,
                    "PLATOON": platoon,
                    "Rank Name": rank_name,
                    "Telegram Handle": telegram_handle
                }
                st.session_state.page = "quiz_question"
                st.rerun()

def page_quiz_question():
    """Page 2: Displays the safety scenario question and timer."""
    # Load quiz configuration
    config = load_quiz_config()
    
    # Get all questions and select one
    questions = get_all_questions()
    if not questions:
        st.error("No questions configured. Please contact the administrator.")
        return
    
    # Select a random question if not already selected for this session
    if 'selected_question' not in st.session_state:
        st.session_state.selected_question = random.choice(questions)
    
    question = st.session_state.selected_question
    question_id = question.get("id", "q1")
    
    st.header(question.get("scenario_title", "Safety Scenario Question"))

    # If there's retake feedback, show the feedback screen first.
    if 'retake_feedback' in st.session_state:
        feedback = st.session_state.retake_feedback
        passing_score = config.get("passing_score", 9)
        st.warning(f"Your score was {feedback['Score']}/10. You need a score of {passing_score} or higher to pass.")
        st.subheader("Feedback on your previous answer:")
        st.markdown(f"**Strength:** {feedback['Strength']}")
        st.markdown(f"**Weakness:** {feedback['Weakness']}")
        st.markdown(f"**Improvement:** {feedback['Improvement']}")
        st.markdown("---")
        
        if st.button("Retry Quiz"):
            del st.session_state['retake_feedback']
            st.session_state.page_reloaded_for_retake = True
            st.session_state.answer_displayed = False  # Reset the display flag for retry
            # Clear cached image to regenerate with improved prompt
            if 'scenario_image' in st.session_state:
                del st.session_state['scenario_image']
            st.rerun()
        return # Stop further rendering until user clicks retry

    st.write(question.get("question_text", "Describe the actions when your buddy trips and fall during a march and has difficulty walking but insists to carry on."))
    
    # Display scenario image with model selection
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        # Check if image display is enabled for this question
        if question.get("image_enabled", True):
            # First try to load saved image from admin for this question
            saved_image = load_scenario_image(question_id)
            if saved_image:
                st.image(saved_image, caption=question.get("scenario_title", "Safety Scenario"), use_column_width=True)
            else:
                # Generate new image if no saved image exists
                # Set the question's prompt for generation
                if question.get("image_prompt"):
                    st.session_state.current_gen_prompt = question.get("image_prompt")
                scenario_image = get_cached_scenario_image()
                if scenario_image:
                    st.image(scenario_image, caption=question.get("scenario_title", "Safety Scenario"), use_column_width=True)
    with col2:
        # Only show model selection if no saved image or if image generation is needed
        if question.get("image_enabled", True) and not load_scenario_image(question_id):
            # Model selection dropdown
            model_options = ["Auto (Best)", "Flux (Realistic)", "Turbo (Fast)", "Simplified"]
            
            # Add Gemini option if API key is configured
            try:
                if st.secrets.get("GOOGLE_API_KEY", "") != "":
                    model_options.insert(1, "Gemini Enhanced")
            except:
                pass
                
            selected_model = st.selectbox(
                "Model:",
                model_options,
                key="image_model",
                help="Select AI model for image generation"
            )
            # Store selected model in session state
            st.session_state.selected_image_model = selected_model
    with col3:
        # Only show regenerate if no saved image
        if question.get("image_enabled", True) and not load_scenario_image(question_id):
            if st.button("🔄 Regenerate", help="Generate new image with selected model"):
                if 'scenario_image' in st.session_state:
                    del st.session_state['scenario_image']
                # Set the question's prompt for regeneration
                if question.get("image_prompt"):
                    st.session_state.current_gen_prompt = question.get("image_prompt")
                st.rerun()

    # Initialize answer state
    if 'answer' not in st.session_state or st.session_state.get('page_reloaded_for_retake', False):
        st.session_state.answer = ""
        st.session_state.page_reloaded_for_retake = False

    # Text area for the answer. Pre-fill with previous answer on retake.
    if 'previous_answer' in st.session_state and not st.session_state.get('answer_displayed', False):
        answer_value = st.session_state.previous_answer
        st.session_state.answer_displayed = True  # Mark that we've displayed it
    elif 'previous_answer' not in st.session_state:
        answer_value = ""
    else:
        answer_value = st.session_state.get('user_answer', '')
    
    answer = st.text_area("Your Answer:", value=answer_value, key="user_answer")

    if st.button("Submit Answer"):
        st.session_state.answer = st.session_state.user_answer
        st.session_state.page = "grading"
        st.rerun()

def page_completion():
    """Page 3: Shows the final score and feedback."""
    st.header("Quiz Completion")
    
    score = st.session_state.grading_results["Score"]
    strength = st.session_state.grading_results["Strength"]
    weakness = st.session_state.grading_results["Weakness"]
    improvement = st.session_state.grading_results["Improvement"]

    st.success(f"You have completed the SAF Safety Quiz. Your score is: {score}/10")
    
    st.subheader("Feedback Summary")
    st.markdown(f"**Strength:** {strength}")
    st.markdown(f"**Weakness:** {weakness}")
    st.markdown(f"**Improvement:** {improvement}")

    if st.button("Finish"):
        # Clear session state for the next participant
        for key in list(st.session_state.keys()):
            if key not in ['page', 'is_admin']:
                del st.session_state[key]
        # Make sure to clear selected question for next participant
        if 'selected_question' in st.session_state:
            del st.session_state['selected_question']
        st.session_state.page = "details"
        st.rerun()

# --- Main App Logic ---

def main():
    """Main function to run the Streamlit app."""
    initialize_data_storage()

    if 'page' not in st.session_state:
        st.session_state.page = "details"

    # Page routing
    if st.session_state.page == "details":
        page_participant_details()
    elif st.session_state.page == "quiz_question":
        page_quiz_question()
    elif st.session_state.page == "grading":
        # This is a transient state to perform grading
        with st.spinner("Grading your answer..."):
            grading_results = grade_answer(st.session_state.answer)
            st.session_state.grading_results = grading_results
            
            # Load passing score from config
            passing_score = load_quiz_config().get("passing_score", 9)
            # Check if score is sufficient
            if grading_results["Score"] >= passing_score:
                # Combine all data and save
                full_data = {
                    **st.session_state.participant_details,
                    "Answer": st.session_state.answer,
                    **grading_results,
                    "Timestamp": pd.to_datetime("now").isoformat()
                }
                save_participant_data(full_data)
                
                st.session_state.page = "completion"
            else:
                # Store feedback and previous answer, then go to the feedback screen
                st.session_state.retake_feedback = grading_results
                st.session_state.previous_answer = st.session_state.answer
                st.session_state.page = "quiz_question"
            st.rerun()
    elif st.session_state.page == "completion":
        page_completion()

if __name__ == "__main__":
    main()
