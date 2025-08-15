import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.express as px
from utils import send_telegram_message, CSV_PATH

def show():
    """Admin Page: View data and perform admin actions."""
    st.header("USO Admin Dashboard")

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
        st.dataframe(df)

        # Export to Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Participants')
        
        st.download_button(
            label="Download Data as .xlsx",
            data=output.getvalue(),
            file_name="participants.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
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

if __name__ == "__main__":
    show()
