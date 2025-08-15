import streamlit as st
from utils import load_custom_css
from pages import quiz, admin

# --- Page configuration ---
st.set_page_config(page_title="SAF Safety Quiz", layout="centered")

def main():
    """Main function to run the Streamlit app."""
    load_custom_css()

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Choose a page:", ["Quiz", "Admin"])

    if app_mode == "Quiz":
        quiz.main()
    elif app_mode == "Admin":
        admin.show()

if __name__ == "__main__":
    main()
