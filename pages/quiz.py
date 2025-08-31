import streamlit as st
import pandas as pd
import time
from utils import initialize_data_storage, grade_answer, save_participant_data
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from image_generator import get_cached_scenario_image

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
    st.header("Safety Scenario Question")

    # If there's retake feedback, show the feedback screen first.
    if 'retake_feedback' in st.session_state:
        feedback = st.session_state.retake_feedback
        st.warning(f"Your score was {feedback['Score']}/10. You need a score of 9 or higher to pass.")
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

    st.write("Describe the actions when your buddy trips and fall during a march and has difficulty walking but insists to carry on.")
    
    # Display scenario image
    col1, col2 = st.columns([4, 1])
    with col1:
        scenario_image = get_cached_scenario_image()
        if scenario_image:
            st.image(scenario_image, caption="Safety Scenario: Combat buddy injured during route march", use_column_width=True)
    with col2:
        if st.button("🔄", help="Regenerate image"):
            if 'scenario_image' in st.session_state:
                del st.session_state['scenario_image']
            st.rerun()

    # Initialize timer and answer state
    if 'timer_start' not in st.session_state or st.session_state.get('page_reloaded_for_retake', False):
        st.session_state.timer_start = time.time()
        st.session_state.answer = ""
        st.session_state.time_up = False
        st.session_state.page_reloaded_for_retake = False

    time_limit = 60
    elapsed_time = time.time() - st.session_state.timer_start
    remaining_time = max(0, time_limit - elapsed_time)

    # Progress bar and countdown text
    progress = remaining_time / time_limit
    st.progress(progress)
    countdown_text = st.empty()
    countdown_text.markdown(f"**Time Remaining: {int(remaining_time)} seconds**")

    # Text area for the answer. Pre-fill with previous answer on retake.
    if 'previous_answer' in st.session_state and not st.session_state.get('answer_displayed', False):
        answer_value = st.session_state.previous_answer
        st.session_state.answer_displayed = True  # Mark that we've displayed it
    elif 'previous_answer' not in st.session_state:
        answer_value = ""
    else:
        answer_value = st.session_state.get('user_answer', '')
    
    answer = st.text_area("Your Answer:", value=answer_value, key="user_answer", disabled=st.session_state.get('time_up', False))

    if st.button("Submit Answer") and not st.session_state.get('time_up', False):
        st.session_state.answer = st.session_state.user_answer
        st.session_state.page = "grading"
        st.rerun()

    # Server-side check to lock input when time is up
    if remaining_time <= 0:
        st.session_state.time_up = True
        st.warning("Time is up! Your input has been locked.")
        # Auto-submit after a short delay
        time.sleep(1)
        st.session_state.answer = st.session_state.user_answer
        st.session_state.page = "grading"
        st.rerun()
    else:
        time.sleep(0.1)
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
            
            # Check if score is sufficient
            if grading_results["Score"] >= 9:
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
