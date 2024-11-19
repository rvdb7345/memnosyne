import streamlit as st
import pandas as pd
from utils.helpers import create_dir
from utils.file_paths import add_project_to_path, ProjectPaths

st.set_page_config(page_title="Vocabulary Practice App", layout="wide")


from streamlit_cookies_manager import EncryptedCookieManager

# Initialize cookie manager
cookies = EncryptedCookieManager(
    prefix="vocab_practice_app_",
    password='your-secret-password'  # Replace with a secure password
)

if not cookies.ready():
    st.stop()

pp = ProjectPaths()
add_project_to_path(pp)

# Initialize base directory
EXERCISES_DIR = 'exercises'
create_dir(EXERCISES_DIR)


# Language options with codes for gTTS compatibility
LANGUAGE_OPTIONS = {
    "English": "en",
    "Turkish": "tr",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Dutch": "nl",
    "Russian": "ru",
    "Portuguese": "pt",
    # Add more languages as needed
}

def main():
    if 'page' not in st.session_state:
        st.session_state['page'] = 'main'

    if st.session_state['page'] == 'main':
        show_main_page()
    elif st.session_state['page'] == 'practice':
        show_practice_page()

def show_main_page():
    st.title("Vocabulary Practice App")
    st.write("Please select an option:")

    # Check if progress data is in cookies
    if cookies.get('progress_data'):
        options = ["Continue where you left off", "Upload Progress", "Start New Exercise"]
    else:
        options = ["Upload Progress", "Start New Exercise"]

    choice = st.selectbox("Select an option", options, key='main_choice_selectbox')

    if choice == "Continue where you left off":
        # Load progress data from cookies into session_state
        st.session_state['progress_data'] = cookies['progress_data']
        # Navigate to Practice page
        st.session_state['page'] = 'practice'
        st.rerun()
    elif choice == "Upload Progress":
        st.write("Upload your progress file to continue.")
        progress_file = st.file_uploader("Upload Progress File", type=['json'], key='progress_file_uploader')
        if progress_file is not None:
            # Load progress data into session_state
            st.session_state['progress_data'] = progress_file.getvalue().decode("utf-8")
            # Navigate to Practice page
            st.session_state['page'] = 'practice'
            st.rerun()
    elif choice == "Start New Exercise":
        st.write("Upload a new exercise file (CSV or TXT).")
        uploaded_file = st.file_uploader("Choose a file", type=['txt', 'csv'], key='exercise_file_uploader')
        custom_exercise_name = st.text_input("Custom Exercise Name", key='custom_exercise_name_input')

        source_language_name = st.selectbox(
            "Source Language",
            list(LANGUAGE_OPTIONS.keys()),
            index=1,
            key='source_language_selectbox'
        )
        target_language_name = st.selectbox(
            "Target Language",
            list(LANGUAGE_OPTIONS.keys()),
            index=0,
            key='target_language_selectbox'
        )

        if st.button("Upload Exercise", key='upload_exercise_button'):
            if uploaded_file is not None and custom_exercise_name:
                try:
                    source_language_code = LANGUAGE_OPTIONS[source_language_name]
                    target_language_code = LANGUAGE_OPTIONS[target_language_name]
                    if uploaded_file.name.endswith('.txt'):
                        cleaned_lines = []
                        for line in uploaded_file:
                            line = line.decode('utf-8').rstrip()
                            parts = line.split('\t')
                            cleaned_lines.append('\t'.join(parts[:2]))

                        from io import StringIO
                        cleaned_content = StringIO('\n'.join(cleaned_lines))
                        df = pd.read_csv(
                            cleaned_content,
                            sep='\t',
                            header=None,
                            names=[source_language_name, target_language_name]
                        )

                    elif uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(
                            uploaded_file,
                            header=None,
                            names=[source_language_name, target_language_name]
                        ).applymap(str.strip)
                    else:
                        st.error("Unsupported file format.")
                        return

                    # Save the exercise data to session_state
                    st.session_state['exercise_df'] = df
                    st.session_state['source_language'] = source_language_name
                    st.session_state['target_language'] = target_language_name
                    st.session_state['exercise_name'] = custom_exercise_name
                    # Navigate to Practice page
                    st.session_state['page'] = 'practice'
                    st.rerun()
                except Exception as e:
                    st.error(f"Error uploading exercise: {e}")
            else:
                st.error("Please provide both a file and a custom exercise name.")

def show_practice_page():
    from sections import practice
    practice.show(cookies)

if __name__ == "__main__":
    main()
