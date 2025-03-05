import streamlit as st
from quiz_game import Quiz
import time
from dotenv import load_dotenv
# import os

# Loading environment variables from .env file
#load_dotenv()


# App Title
st.title("Quiz Game 🎯")
st.write("Welcome to the quiz game! Answer the following questions and check the leaderboard.")

# Initialize session state
if 'active_section' not in st.session_state:
    st.session_state.active_section = 'quiz'
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

#*************Sidebar Section**************
with st.sidebar:
    st.header("Navigation")
    # Section selector buttons
    if st.button("📝 Quiz Section"):
        st.session_state.active_section = 'quiz'
    if st.button("🏆 Leaderboard"):
        st.session_state.active_section = 'leaderboard'
    if st.button("🔒 Admin Section"):
        st.session_state.active_section = 'admin'

# Admin Section
if st.session_state.active_section == 'admin':
    st.header("🔒Admin Login")

    # If admin is not logged in, show login form
    if not st.session_state.admin_logged_in:
        admin_username = st.text_input("Admin Username", key="admin_username")
        admin_password = st.text_input("Admin Password", type="password", key="admin_password")
    
        if st.button("Admin Login", key="admin_login"):
            # # Getting admin credentials from environment variables
            # correct_username = os.getenv("ADMIN_USERNAME")
            # correct_password = os.getenv("ADMIN_PASSWORD")
            correct_username = st.secrets["ADMIN_USERNAME"]
            correct_password = st.secrets["ADMIN_PASSWORD"]

            if admin_username == "correct_username" and admin_password == "correct_password":
                st.session_state.admin_logged_in = True
                st.success("Admin logged in successfully!")
                st.balloons()
            else:
                st.error("⚠️Incorrect admin credentials. Please try again.")

    # If admin is logged in, show admin options
    if st.session_state.admin_logged_in:
        st.subheader("Add a MCQ Question 📝")
        new_question = st.text_input("Enter the question:", key="new_question")
        # Four options for the MCQ
        option1 = st.text_input("Option 1:", key="option1")
        option2 = st.text_input("Option 2:", key="option2")
        option3 = st.text_input("Option 3:", key="option3")
        option4 = st.text_input("Option 4:", key="option4")
        # Admin selects the correct answer from the four options
        correct_option = st.selectbox("Select the correct answer", options=["Option 1", "Option 2", "Option 3", "Option 4"]
                                    ,key="correct_option")

        if st.button("Add Question",key="add_question"):
            if new_question and option1 and option2 and option3 and option4:
                 # Create a list of the actual option texts entered by the admin
                actual_options = [option1.strip(), option2.strip(), option3.strip(), option4.strip()]

                # Mapping the selected option to its text
                options_list = ["Option 1", "Option 2", "Option 3", "Option 4"]
                correct_index = options_list.index(correct_option)  # Get index
                correct_answer = actual_options[correct_index]  # Get the correct option text

                # Create a comma-separated string of options
                option_string = ",".join(actual_options)

                admin_game = Quiz("admin")  # Using another name for admin operations
                admin_game.add_questions(new_question.strip(), correct_answer , option_string)
                st.success("✅ Question added successfully!")
            else:
                st.error("⚠️ Please enter both a question and an answer.")

        st.subheader("Delete a Question 🗑️")
        admin_game = Quiz("admin")  # Dummy admin game to access questions
        questions_list = admin_game.questions

        if questions_list:
            question_id = st.selectbox("Select a question to delete", options=[question["question"] for question in questions_list])
            if st.button("Delete Question",key="delete_question"):
                for question in questions_list:
                    if question["question"] == question_id:
                        admin_game.delete_question(question["id"])
                        st.success("✅ Question deleted successfully!")
                        break
        else:
            st.warning("No questions available to delete.")

#*************Quiz Section**************

elif st.session_state.active_section == 'quiz':
    st.header("Quiz Section 🧠")
    # User Input for Name
    name = st.text_input("Enter your name:", key="quiz_name")

    if name:
        # If quiz start time is not set, store it in session_state
        if "quiz_start_time" not in st.session_state:
            st.session_state.quiz_start_time = time.time()

        game = Quiz(name)
        if game.questions:
            user_answers = []
            st.subheader(f"Hello, {name}! Let's start the quiz.")
        
            for i, question in enumerate(game.questions):
                st.write(f"Question {i+1}: {question['question']}")
                if question.get("options"):
                    options_list = question["options"].split(",")
                    user_answer = st.radio("Choose an answer:", options_list, key=f"q_radio_{i}")
                else:
                    user_answer = st.text_input("Enter your answer:", key=f"q_text_{i}")
                user_answers.append(user_answer.strip().lower())

            if st.button("Submit", key="submit_quiz"):
                game.check_answer(user_answers)
                time_taken = time.time() - st.session_state.quiz_start_time  # Get time_taken after checking answers
                game.time_taken = round(time_taken, 2)
                game.save_score()
                st.success(f"🎉 You scored {game.score}/{len(game.questions)} in {game.time_taken:.2f} seconds!!")
                # Optionally clear the quiz start time to allow a fresh attempt later
                del st.session_state.quiz_start_time

            if st.button("Reset Quiz", key="reset_quiz"):
                for key in list(st.session_state.keys()):
                    if key.startswith("quiz_name") or key.startswith("q_radio_") or key.startswith("q_text_") or key == "quiz_start_time":
                        del st.session_state[key]
                st.rerun()
        else:
            st.warning("No questions available for the quiz. please ask admin to add questions!")
    else:
        st.info("Please enter your name to start the quiz.")
            
#********** Leaderboard Section**************
elif st.session_state.active_section == 'leaderboard':
    st.header("Leaderboard 📊")
    game = Quiz("dummy")  # Dummy game to access leaderboard
    leaderboard = game.get_leaderboard()

    if leaderboard:
        for i, (user, score, time_taken) in enumerate(leaderboard, start=1):
            st.markdown(f"""
            <div style="padding:10px; border-radius:5px; margin:5px 0; 
                        background-color:#f0f2f6">
                🏅 {i}. {user} - {score} points 🕒 {time_taken:.2f} sec
            </div>
            """, unsafe_allow_html=True)
        
    else:
        st.warning("Leaderboard is empty.")

