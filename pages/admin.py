import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.express as px
from utils import send_telegram_message, CSV_PATH

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quiz_config import (load_quiz_config, save_quiz_config, save_scenario_image, 
                         load_scenario_image, delete_scenario_image, get_all_questions,
                         add_question, update_question, delete_question, get_question_by_id)
from image_generator import generate_safety_scenario_image

def show():
    """Admin Page: View data and perform admin actions."""
    st.header("USO Admin Dashboard")
    
    # Create tabs for different admin functions
    tab1, tab2, tab3 = st.tabs(["📊 Participant Data", "📝 Quiz Configuration", "🖼️ Preview Quiz"])
    
    with tab1:
        show_participant_data()
    
    with tab2:
        show_quiz_configuration()
    
    with tab3:
        preview_quiz()

def show_participant_data():
    """Display participant data and analytics."""
    try:
        df = pd.read_csv(CSV_PATH)
                
        TOTAL_PER_COY = 60 # As specified, each company has 60 respondents

        # Calculate completion data per company
        completion_by_coy = df.groupby(['UNIT', 'COY'])['Rank Name'].count().reset_index()
        completion_by_coy.rename(columns={'Rank Name': 'Completed'}, inplace=True)
        
        # Add a combined label for the chart
        completion_by_coy['Unit-Company'] = completion_by_coy['UNIT'] + " - " + completion_by_coy['COY']

        if completion_by_coy.empty:
            st.info("Not enough data to generate completion chart.")
        else:
            # Create the bar chart
            fig = px.bar(
                completion_by_coy,
                x='Unit-Company',
                y='Completed',
                title='Completion Status by Company',
                text='Completed', # Display the count on top of the bars
                labels={'Completed': 'Number of Respondents', 'Unit-Company': 'Unit - Company'},
                height=500
            )
            
            # Customize the chart
            fig.update_layout(
                yaxis=dict(range=[0, TOTAL_PER_COY]), # Set y-axis from 0 to 60
                xaxis_title="Unit and Company",
                yaxis_title="Completed Respondents",
                plot_bgcolor='rgba(0,0,0,0)'
            )
            fig.update_traces(
                marker_color='#1E3A8A', 
                texttemplate='%{text}', 
                textposition='outside'
            )
            
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("Raw Participant Data")
        
        # Add action column for delete buttons
        if not df.empty:
            df_display = df.copy()
            df_display.insert(0, "Action", "")
            
            # Display each row with a delete button
            for idx in df.index:
                col1, col2 = st.columns([0.1, 0.9])
                
                with col1:
                    if st.button("🗑️", key=f"del_{idx}", help=f"Delete {df.loc[idx, 'Rank Name']}'s record"):
                        # Delete the row
                        df_updated = df.drop(idx).reset_index(drop=True)
                        df_updated.to_csv(CSV_PATH, index=False)
                        st.success(f"Deleted record for {df.loc[idx, 'Rank Name']}")
                        st.rerun()
                
                with col2:
                    # Display row data in a compact format
                    row_text = f"**{df.loc[idx, 'Rank Name']}** | {df.loc[idx, 'UNIT']} - {df.loc[idx, 'COY']} - Platoon {df.loc[idx, 'PLATOON']} | Score: {df.loc[idx, 'Score']}/10 | {df.loc[idx, 'Timestamp']}"
                    st.write(row_text)
            
            st.markdown("---")
            
            # Also show full dataframe for reference
            with st.expander("View Full Data Table"):
                st.dataframe(df)
        else:
            st.info("No participant data available.")

        # Export to Excel - Fixed xlsxwriter bug
        output = BytesIO()
        excel_created = False
        
        # Try xlsxwriter first
        try:
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Participants')
            output.seek(0)  # Reset buffer position to beginning
            excel_created = True
        except ImportError:
            # Try openpyxl as fallback
            try:
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Participants')
                output.seek(0)  # Reset buffer position to beginning
                excel_created = True
            except Exception as e:
                st.error(f"Error creating Excel file: {e}")
        except Exception as e:
            st.error(f"Error creating Excel file: {e}")
        
        if excel_created:
            st.download_button(
                label="Download Data as .xlsx",
                data=output.getvalue(),
                file_name="participants.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            # Fallback to CSV if Excel export fails
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download Data as .csv (Excel export failed)",
                data=csv,
                file_name="participants.csv",
                mime="text/csv"
            )

        # Assign Monthly Quiz
        if st.button("Assign Monthly"):
            with st.spinner("Sending reminders..."):
                for handle in df["Telegram Handle"].unique():
                    message = "Reminder: Please complete your monthly SAF Safety Quiz. Link: [PLACEHOLDER_QUIZ_LINK]"
                    send_telegram_message(handle, message)
                st.success("Monthly reminders have been sent.")

    except FileNotFoundError:
        st.error("No participant data found.")
    except Exception as e:
        st.error(f"An error occurred: {e}")

def show_quiz_configuration():
    """Allow admin to edit quiz configuration."""
    st.subheader("Quiz Configuration")
    
    # Load current configuration
    config = load_quiz_config()
    questions = get_all_questions()
    
    # Global settings
    with st.expander("⚙️ Global Settings", expanded=False):
        passing_score = st.number_input(
            "Passing Score (out of 10):",
            min_value=1,
            max_value=10,
            value=config.get("passing_score", 9),
            help="Minimum score required to pass"
        )
        
        if st.button("💾 Save Global Settings", type="primary"):
            config["passing_score"] = passing_score
            if save_quiz_config(config):
                st.success("✅ Global settings saved!")
    
    # Question management
    st.markdown("### Questions")
    
    # Add new question button
    if st.button("➕ Add New Question", type="secondary"):
        new_question = {
            "scenario_title": "New Safety Scenario",
            "question_text": "Enter your question here...",
            "image_enabled": True,
            "image_prompt": ""
        }
        success, new_id = add_question(new_question)
        if success:
            st.success(f"✅ New question added with ID: {new_id}")
            st.rerun()
    
    # Create tabs for each question
    if questions:
        tab_labels = [f"Question {i+1}" for i in range(len(questions))]
        tabs = st.tabs(tab_labels)
        
        for i, (tab, question) in enumerate(zip(tabs, questions)):
            with tab:
                show_question_editor(question, i+1)

def show_question_editor(question, question_num):
    """Show the editor for a single question."""
    question_id = question.get("id", "")
    
    # Container for the form and auto-generate button
    form_container = st.container()
    
    with form_container:
        # Create form for editing with unique key per question
        with st.form(f"question_form_{question_id}"):
            st.markdown(f"### Question {question_num} Settings")
            
            # Edit scenario title
            scenario_title = st.text_input(
                "Scenario Title:",
                value=question.get("scenario_title", "Safety Scenario Question"),
                help="Title shown above the question"
            )
            
            # Edit question text
            question_text = st.text_area(
                "Question Text:",
                value=question.get("question_text", ""),
                height=100,
                help="The main question that participants will answer"
            )
            
            
            # Image settings
            image_enabled = st.checkbox(
                "Enable Scenario Image",
                value=question.get("image_enabled", True),
                help="Show an AI-generated image with the question"
            )
            
            # Image generation prompt
            st.markdown("### Image Generation Prompt")
            
            # Check if we should use auto-generated prompt for this question
            session_key = f'auto_generated_prompt_{question_id}'
            if session_key in st.session_state:
                prompt_value = st.session_state[session_key]
                del st.session_state[session_key]
            else:
                prompt_value = question.get("image_prompt", "")
            
            image_prompt = st.text_area(
                "AI Image Prompt:",
                value=prompt_value,
                height=100,
                help="Concise description for image generation. Use the 'Auto-Generate Prompt' button below to create from question.",
                key=f"image_prompt_field_{question_id}"
            )
            
            # Save and Delete buttons
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                submitted = st.form_submit_button("💾 Save Question", type="primary")
            with col2:
                # Only show delete if not the only question
                questions = get_all_questions()
                if len(questions) > 1:
                    delete_clicked = st.form_submit_button("🗑️ Delete Question", type="secondary")
                else:
                    delete_clicked = False
            
            if submitted:
                # Update question
                updated_question = {
                    "scenario_title": scenario_title,
                    "question_text": question_text,
                    "image_enabled": image_enabled,
                    "image_prompt": image_prompt
                }
                
                if update_question(question_id, updated_question):
                    st.success("✅ Question saved successfully!")
                    st.balloons()
                else:
                    st.error("Failed to save question")
            
            if delete_clicked:
                if delete_question(question_id):
                    st.success("✅ Question deleted!")
                    st.rerun()
                else:
                    st.error("Cannot delete the only question")
    
    # Auto-generate prompt button (outside form, but positioned nicely)
    with form_container:
        # Position button to appear near the form
        st.write("")  # Add spacing
        if st.button(f"🤖 Auto-Generate Image Prompt", type="secondary", 
                    help="Generate prompt from question text", key=f"auto_gen_{question_id}"):
            if question_text:
                # Parse the question for key scenario
                scenario = ""
                if "buddy" in question_text.lower() and ("trip" in question_text.lower() or "fall" in question_text.lower() or "injur" in question_text.lower()):
                    scenario = "One soldier is kneeling on a tarmac road, visibly injured, while the other supports/helps him"
                elif "heat" in question_text.lower():
                    scenario = "One soldier showing heat exhaustion symptoms, another providing shade and water"
                elif "weapon" in question_text.lower() or "rifle" in question_text.lower():
                    scenario = "Soldiers demonstrating proper SAR-21 rifle safety procedures"
                elif "grenade" in question_text.lower():
                    scenario = "Soldiers in grenade throwing bay with proper safety positions"
                elif "vehicle" in question_text.lower():
                    scenario = "Soldiers conducting vehicle safety checks near military tonner"
                else:
                    scenario = "Soldiers demonstrating safety procedures during training exercise"
                
                # Determine environment
                environment = "SAF training area with visible infrastructure"
                if "march" in question_text.lower() or "route" in question_text.lower():
                    environment = "SAF training area with visible infrastructure during a route march"
                elif "range" in question_text.lower():
                    environment = "SAF live firing range with safety markers and bunkers"
                elif "field" in question_text.lower():
                    environment = "jungle training area with dense tropical vegetation"
                
                # Generate concise prompt like the user's example
                generated_prompt = f"Photorealistic scene of two NSF soldiers in modern SAF No.4 pixelated camouflage. {scenario}. Distinctive Singapore pixel pattern, field pack with metal frame, black Frontier boots. Background: {environment}."
                
                # Store in session state to update the field on rerun
                st.session_state[f'auto_generated_prompt_{question_id}'] = generated_prompt
                st.success("✅ Prompt generated and inserted into the form!")
                st.rerun()
            else:
                st.warning("Please enter a question text first.")
    
    # Image generation section
    st.markdown("### Scenario Image")
    
    # Show current image if exists for this question
    current_image = load_scenario_image(question_id)
    if current_image:
        st.image(current_image, caption=f"Current Scenario Image for Question {question_num}", use_container_width=True)
    else:
        st.info("No scenario image saved for this question. Generate one below.")
    
    # Show current prompt being used
    with st.expander("📝 Current Image Generation Prompt", expanded=False):
        current_prompt = question.get("image_prompt", "No prompt configured")
        st.text_area("Prompt that will be used:", value=current_prompt, height=100, disabled=True, 
                    key=f"show_prompt_{question_id}")
        st.info("💡 Edit the prompt in the form above and save to update it.")
    
    # Image generation controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Model selection
        model_options = ["Auto (Best)", "Flux (Realistic)", "Turbo (Fast)", "Simplified"]
        try:
            if st.secrets.get("GOOGLE_API_KEY", "") != "":
                model_options.insert(1, "Gemini Enhanced")
        except:
            pass
        
        selected_model = st.selectbox(
            "Image Generation Model:",
            model_options,
            key=f"admin_image_model_{question_id}",
            help="Select AI model for image generation"
        )
    
    with col2:
        if st.button("🎨 Generate New Image", type="secondary", key=f"gen_img_{question_id}"):
            st.session_state.selected_image_model = selected_model
            with st.spinner(f"Generating image with {selected_model}..."):
                try:
                    # Load the question's prompt for generation
                    updated_q = get_question_by_id(question_id)
                    if updated_q and updated_q.get("image_prompt"):
                        # Temporarily set the prompt in session for the generator
                        st.session_state.current_gen_prompt = updated_q.get("image_prompt")
                    
                    new_image = generate_safety_scenario_image()
                    if new_image:
                        st.session_state[f'preview_image_{question_id}'] = new_image
                        st.success("Image generated! Preview below.")
                        st.rerun()
                    else:
                        st.error("Failed to generate image. Please try again or select a different model.")
                except Exception as e:
                    st.error(f"Error generating image: {str(e)[:200]}")
    
    with col3:
        if current_image and st.button("🗑️ Delete Current", type="secondary", key=f"del_img_{question_id}"):
            if delete_scenario_image(question_id):
                st.success("Image deleted")
                st.rerun()
    
    # Show preview if generated for this question
    preview_key = f'preview_image_{question_id}'
    if preview_key in st.session_state:
        st.markdown("#### Preview Generated Image")
        st.image(st.session_state[preview_key], caption="Preview - Not Saved Yet", use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Save This Image", type="primary", key=f"save_img_{question_id}"):
                if save_scenario_image(st.session_state[preview_key], question_id):
                    st.success("Image saved successfully!")
                    del st.session_state[preview_key]
                    st.rerun()
        
        with col2:
            if st.button("❌ Discard", key=f"discard_img_{question_id}"):
                del st.session_state[preview_key]
                st.rerun()

def preview_quiz():
    """Preview how the quiz will appear to participants."""
    st.subheader("Quiz Preview")
    st.info("This shows how all questions will appear to participants (Note: In actual quiz, only one random question is shown)")
    
    # Load configuration and questions
    config = load_quiz_config()
    questions = get_all_questions()
    
    if not questions:
        st.warning("No questions configured. Please add questions in the Quiz Configuration tab.")
        return
    
    # Show all questions in continuous scroll
    for i, question in enumerate(questions, 1):
        question_id = question.get("id", "")
        
        # Show preview container for each question
        with st.container():
            st.markdown("---")
            st.markdown(f"### Question {i}")
            st.header(question.get("scenario_title", "Safety Scenario Question"))
            st.write(question.get("question_text", "No question text configured"))
            
            # Show image if enabled and exists
            if question.get("image_enabled", True):
                saved_image = load_scenario_image(question_id)
                if saved_image:
                    st.image(saved_image, caption=f"Safety Scenario for Question {i}", use_container_width=True)
                else:
                    st.info(f"No scenario image saved for Question {i}. Generate one in the Quiz Configuration tab.")
            
            # Show mock answer area
            st.text_area(f"Your Answer for Question {i}:", 
                        placeholder="Participants will type their answer here...", 
                        disabled=True,
                        key=f"preview_answer_{question_id}")
            
            # Show submit button (disabled)
            st.button(f"Submit Answer", disabled=True, key=f"preview_submit_{question_id}")
    
    st.markdown("---")
    
    # Show configuration summary
    st.markdown("### Current Settings")
    st.metric("Passing Score", f"{config.get('passing_score', 9)}/10")
    st.info("**Note:** In the actual quiz, participants will receive ONE randomly selected question from the above pool.")

if __name__ == "__main__":
    show()
