import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.express as px
from utils import send_telegram_message, CSV_PATH

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quiz_config import load_quiz_config, save_quiz_config, save_scenario_image, load_scenario_image, delete_scenario_image
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
    
    # Container for the form and auto-generate button
    form_container = st.container()
    
    with form_container:
        # Create form for editing
        with st.form("quiz_config_form"):
            st.markdown("### Question Settings")
            
            # Edit scenario title
            scenario_title = st.text_input(
                "Scenario Title:",
                value=config.get("scenario_title", "Safety Scenario Question"),
                help="Title shown above the question"
            )
            
            # Edit question text
            question_text = st.text_area(
                "Question Text:",
                value=config.get("question_text", ""),
                height=100,
                help="The main question that participants will answer"
            )
            
            # Edit scoring and timing
            col1, col2 = st.columns(2)
            with col1:
                passing_score = st.number_input(
                "Passing Score (out of 10):",
                min_value=1,
                max_value=10,
                value=config.get("passing_score", 9),
                help="Minimum score required to pass"
                )
            
            with col2:
                time_limit = st.number_input(
                "Time Limit (seconds):",
                min_value=30,
                max_value=300,
                value=config.get("time_limit", 60),
                step=10,
                help="Time allowed to answer the question"
                )
            
            # Image settings
            image_enabled = st.checkbox(
            "Enable Scenario Image",
            value=config.get("image_enabled", True),
            help="Show an AI-generated image with the question"
            )
            
            # Image generation prompt
            st.markdown("### Image Generation Prompt")
            
            # Check if we should use auto-generated prompt
            if 'auto_generated_prompt' in st.session_state:
                prompt_value = st.session_state.auto_generated_prompt
                del st.session_state.auto_generated_prompt
            else:
                prompt_value = config.get("image_prompt", "")
            
            image_prompt = st.text_area(
            "AI Image Prompt:",
            value=prompt_value,
            height=100,
            help="Concise description for image generation. Use the 'Auto-Generate Prompt' button above to create from question.",
            key="image_prompt_field"
            )
            
            # Save button
            submitted = st.form_submit_button("💾 Save Configuration", type="primary")
            
            if submitted:
                # Update configuration
                new_config = {
                    "question_text": question_text,
                    "scenario_title": scenario_title,
                    "passing_score": passing_score,
                    "time_limit": time_limit,
                    "image_enabled": image_enabled,
                    "image_prompt": image_prompt
                }
                
                if save_quiz_config(new_config):
                    st.success("✅ Configuration saved successfully!")
                    st.balloons()
                else:
                    st.error("Failed to save configuration")
    
    # Auto-generate prompt button (outside form, but positioned nicely)
    with form_container:
        # Position button to appear near the form
        st.write("")  # Add spacing
        if st.button("🤖 Auto-Generate Image Prompt", type="secondary", help="Generate prompt from question text"):
            question_text = config.get("question_text", "")
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
                st.session_state.auto_generated_prompt = generated_prompt
                st.success("✅ Prompt generated and inserted into the form!")
                st.rerun()
            else:
                st.warning("Please save a question text first, then click this button.")
    
    # Image generation section
    st.markdown("### Scenario Image")
    
    # Show current image if exists
    current_image = load_scenario_image()
    if current_image:
        st.image(current_image, caption="Current Scenario Image", use_column_width=True)
    else:
        st.info("No scenario image saved. Generate one below.")
    
    # Show current prompt being used
    with st.expander("📝 Current Image Generation Prompt", expanded=False):
        current_prompt = config.get("image_prompt", "No prompt configured")
        st.text_area("Prompt that will be used:", value=current_prompt, height=100, disabled=True)
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
            key="admin_image_model",
            help="Select AI model for image generation"
        )
    
    with col2:
        if st.button("🎨 Generate New Image", type="secondary"):
            st.session_state.selected_image_model = selected_model
            with st.spinner(f"Generating image with {selected_model}..."):
                try:
                    new_image = generate_safety_scenario_image()
                    if new_image:
                        st.session_state.preview_image = new_image
                        st.success("Image generated! Preview below.")
                        st.rerun()
                    else:
                        st.error("Failed to generate image. Please try again or select a different model.")
                except Exception as e:
                    st.error(f"Error generating image: {str(e)[:200]}")
    
    with col3:
        if current_image and st.button("🗑️ Delete Current", type="secondary"):
            if delete_scenario_image():
                st.success("Image deleted")
                st.rerun()
    
    # Show preview if generated
    if 'preview_image' in st.session_state:
        st.markdown("#### Preview Generated Image")
        st.image(st.session_state.preview_image, caption="Preview - Not Saved Yet", use_column_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Save This Image", type="primary"):
                if save_scenario_image(st.session_state.preview_image):
                    st.success("Image saved successfully!")
                    del st.session_state.preview_image
                    st.rerun()
        
        with col2:
            if st.button("❌ Discard"):
                del st.session_state.preview_image
                st.rerun()

def preview_quiz():
    """Preview how the quiz will appear to participants."""
    st.subheader("Quiz Preview")
    st.info("This shows how the quiz will appear to participants")
    
    # Load configuration
    config = load_quiz_config()
    
    # Show preview container
    with st.container():
        st.markdown("---")
        st.header(config.get("scenario_title", "Safety Scenario Question"))
        st.write(config.get("question_text", "No question configured"))
        
        # Show image if enabled and exists
        if config.get("image_enabled", True):
            saved_image = load_scenario_image()
            if saved_image:
                st.image(saved_image, caption="Safety Scenario", use_column_width=True)
            else:
                st.warning("No scenario image saved. Generate one in the Quiz Configuration tab.")
        
        # Show mock answer area
        st.text_area("Your Answer:", placeholder="Participants will type their answer here...", disabled=True)
        
        # Show timer and submit button (disabled)
        col1, col2 = st.columns([3, 1])
        with col1:
            st.progress(0.8)
            st.markdown(f"**Time Remaining: {int(config.get('time_limit', 60) * 0.8)} seconds**")
        with col2:
            st.button("Submit Answer", disabled=True)
        
        st.markdown("---")
        
        # Show configuration summary
        st.markdown("### Current Settings")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Passing Score", f"{config.get('passing_score', 9)}/10")
        with col2:
            st.metric("Time Limit", f"{config.get('time_limit', 60)} seconds")

if __name__ == "__main__":
    show()
