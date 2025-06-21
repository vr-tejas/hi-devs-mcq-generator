import streamlit as st
import pandas as pd
import nltk
from mcq_generator import MCQGenerator
from user_manager import UserManager
from analytics import PerformanceAnalytics

# no longer needed - using direct st.rerun() calls instead

# initialize page state if needed
if 'page' not in st.session_state:
    st.session_state.page = "Login/Register"

# get current page from session state
page = st.session_state.page

# download necessary nltk data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt')
    except:
        st.warning("Could not download NLTK punkt tokenizer. Some features may be limited.")

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    try:
        nltk.download('stopwords')
    except:
        st.warning("Could not download NLTK stopwords. Some features may be limited.")

# app configuration
st.set_page_config(
    page_title="Adaptive MCQ Generator",
    page_icon="📚",
    layout="wide"
)

# initialize session state variables
if 'user_manager' not in st.session_state:
    st.session_state.user_manager = UserManager()
if 'mcq_generator' not in st.session_state:
    st.session_state.mcq_generator = MCQGenerator()
if 'analytics' not in st.session_state:
    st.session_state.analytics = PerformanceAnalytics()
if 'current_user_id' not in st.session_state:
    st.session_state.current_user_id = None
if 'current_test' not in st.session_state:
    st.session_state.current_test = None
if 'test_in_progress' not in st.session_state:
    st.session_state.test_in_progress = False
if 'question_index' not in st.session_state:
    st.session_state.question_index = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = []
if 'test_results' not in st.session_state:
    st.session_state.test_results = None

# initialize more session state variables for login/register
if 'login_username' not in st.session_state:
    st.session_state.login_username = ""
if 'login_password' not in st.session_state:
    st.session_state.login_password = ""
if 'register_username' not in st.session_state:
    st.session_state.register_username = ""
if 'register_password' not in st.session_state:
    st.session_state.register_password = ""
if 'register_confirm' not in st.session_state:
    st.session_state.register_confirm = ""
if 'login_message' not in st.session_state:
    st.session_state.login_message = ""
if 'register_message' not in st.session_state:
    st.session_state.register_message = ""
if 'do_rerun' not in st.session_state:
    st.session_state.do_rerun = False

# app title
st.title("🤖 AI-Powered MCQ Generator for Diagnostic Tests")
st.markdown("*Generate personalized multiple-choice questions using advanced AI technology*")

# debug information
st.write(f"Current page: {st.session_state.page}")
st.write(f"Logged in: {'Yes' if st.session_state.current_user_id else 'No'}")
if st.session_state.current_user_id:
    st.write(f"Current user: {st.session_state.current_user_id}")

# navigation handling - custom navigation bar when logged in
if st.session_state.current_user_id:
    st.write(f"Logged in as: **{st.session_state.current_user_id}**")
    
    # create a horizontal navigation bar with buttons
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
    
    with nav_col1:
        if st.button("Generate Test", use_container_width=True, type="primary" if st.session_state.page == "Generate Test" else "secondary"):
            st.session_state.page = "Generate Test"
            st.rerun()
    
    with nav_col2:
        if st.button("Take Test", use_container_width=True, type="primary" if st.session_state.page == "Take Test" else "secondary"):
            st.session_state.page = "Take Test"
            st.rerun()
    
    with nav_col3:
        if st.button("View Analytics", use_container_width=True, type="primary" if st.session_state.page == "View Analytics" else "secondary"):
            st.session_state.page = "View Analytics"
            st.rerun()
    
    with nav_col4:
        if st.button("Logout", use_container_width=True):
            st.session_state.current_user_id = None
            st.session_state.page = "Login/Register"
            st.rerun()
    
    st.divider()
else:
    # only show the login/register option when not logged in
    st.session_state.page = "Login/Register"

# user login/registration page
if st.session_state.page == "Login/Register":
    if not st.session_state.current_user_id:
        st.header("User Login/Registration")
        
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("Login")
            
            # simple login form
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")
                
                if submit:
                    if st.session_state.user_manager.authenticate_user(username, password):
                        st.session_state.current_user_id = username
                        st.session_state.page = "Generate Test"
                        st.success(f"Welcome back, {username}!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
        
        with tab2:
            st.subheader("Register")
            
            # simple register form
            with st.form("register_form", clear_on_submit=False):
                reg_username = st.text_input("Choose Username")
                reg_password = st.text_input("Choose Password", type="password")
                reg_confirm = st.text_input("Confirm Password", type="password")
                reg_submit = st.form_submit_button("Register")
                
                if reg_submit:
                    if reg_password != reg_confirm:
                        st.error("Passwords don't match.")
                    elif st.session_state.user_manager.user_exists(reg_username):
                        st.error("Username already exists.")
                    else:
                        st.session_state.user_manager.add_user(reg_username, reg_password)
                        st.session_state.current_user_id = reg_username
                        st.session_state.page = "Generate Test"
                        st.success("Registration successful!")
                        st.rerun()

# test generation page
elif st.session_state.page == "Generate Test":
    if not st.session_state.current_user_id:
        st.warning("Please login or register first.")
        st.session_state.page = "Login/Register"
        st.rerun()
    else:
        st.header("Generate Personalized MCQ Test")
        
        # Add info about AI capabilities
        st.info("🚀 **AI-Powered Generation**: This system uses advanced AI to create unique, personalized questions based on your specifications. No more repetitive or hardcoded questions!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            test_name = st.text_input("Test Name")
            subject = st.selectbox("Subject", ["Mathematics", "Science", "History", "English", "Computer Science"])
            
            if subject == "Mathematics":
                topics = ["Algebra", "Geometry", "Calculus", "Statistics", "Trigonometry"]
            elif subject == "Science":
                topics = ["Physics", "Chemistry", "Biology", "Astronomy", "Environmental Science"]
            elif subject == "History":
                topics = ["Ancient History", "Medieval History", "Modern History", "World Wars", "Cold War"]
            elif subject == "English":
                topics = ["Grammar", "Literature", "Comprehension", "Vocabulary", "Writing"]
            elif subject == "Computer Science":
                topics = ["Programming", "Data Structures", "Algorithms", "Databases", "Networking"]
            
            selected_topics = st.multiselect("Topics", topics)
            
        with col2:
            difficulty = st.select_slider("Initial Difficulty Level", options=["Easy", "Medium", "Hard"])
            num_questions = st.number_input("Number of Questions", min_value=5, max_value=50, value=10)
            adaptive = st.checkbox("Enable Adaptive Difficulty", value=True)
        
        # Custom description for AI generation
        st.subheader("🤖 AI Question Generation")
        custom_description = st.text_area(
            "Describe what type of questions you want (Optional)", 
            placeholder="Example: 'Focus on practical programming problems with real-world examples' or 'Include questions about recent developments in AI and machine learning' or 'Create scenario-based questions for business applications'",
            height=100,
            help="The AI will use this description along with the subject and topics to generate more targeted questions."
        )
        
        educational_content = st.text_area("Educational Content (Optional)", 
                                         placeholder="Paste any specific educational content, articles, or material you want the questions to be based on...",
                                         height=150,
                                         help="If provided, the AI will generate questions based on this specific content.")
        
        if st.button("🚀 Generate AI-Powered Test", type="primary"):
            if not test_name:
                st.error("Please enter a test name.")
            elif not selected_topics:
                st.error("Please select at least one topic.")
            else:
                with st.spinner("🤖 Generating questions using AI... This may take a moment."):
                    # generate test questions using AI
                    questions = st.session_state.mcq_generator.generate_questions(
                        subject=subject,
                        topics=selected_topics,
                        difficulty=difficulty,
                        num_questions=num_questions,
                        content=educational_content,
                        custom_description=custom_description
                    )
                
                # save test for the user
                test_id = st.session_state.user_manager.create_test(
                    user_id=st.session_state.current_user_id,
                    test_name=test_name,
                    subject=subject,
                    topics=selected_topics,
                    questions=questions,
                    adaptive=adaptive
                )
                
                if questions and len(questions) > 0:
                    st.success(f"✅ AI successfully generated {len(questions)} questions for '{test_name}'!")
                    st.info("🎯 The questions were created using advanced AI based on your specifications. You can now take this test from the 'Take Test' page.")
                    
                    # Show a preview of the first question
                    if len(questions) > 0:
                        with st.expander("📋 Preview First Question"):
                            st.write(f"**Q1:** {questions[0]['question']}")
                            for i, option in enumerate(questions[0]['options']):
                                st.write(f"{chr(65+i)}. {option}")
                else:
                    st.error("❌ Failed to generate questions. Please try again with different parameters or check your internet connection.")

# take test page
elif st.session_state.page == "Take Test":
    if not st.session_state.current_user_id:
        st.warning("Please login or register first.")
        st.session_state.page = "Login/Register"
        st.rerun()
    else:
        st.header("Take MCQ Test")
        
        if not st.session_state.test_in_progress:
            user_tests = st.session_state.user_manager.get_user_tests(st.session_state.current_user_id)
            
            if not user_tests:
                st.info("You don't have any tests yet. Generate one from the 'Generate Test' page.")
            else:
                test_options = {test["test_name"]: test_id for test_id, test in user_tests.items()}
                selected_test = st.selectbox("Select a test", list(test_options.keys()))
                
                if st.button("Start Test"):
                    selected_test_id = test_options[selected_test]
                    st.session_state.current_test = user_tests[selected_test_id]
                    st.session_state.test_in_progress = True
                    st.session_state.question_index = 0
                    st.session_state.user_answers = []
                    st.rerun()
        
        else:
            # Display current question
            questions = st.session_state.current_test["questions"]
            current_q = questions[st.session_state.question_index]
            
            st.subheader(f"Question {st.session_state.question_index + 1} of {len(questions)}")
            st.write(current_q["question"])
            
            # Randomize answer options to avoid patterns
            options = current_q["options"]
            correct_answer = current_q["correct_answer"]
            
            user_answer = st.radio("Select your answer:", options, key=f"q_{st.session_state.question_index}")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("Previous") and st.session_state.question_index > 0:
                    st.session_state.question_index -= 1
                    st.rerun()
            
            with col2:
                if st.button("Submit Answer"):
                    # Save the answer
                    is_correct = user_answer == correct_answer
                    st.session_state.user_answers.append({
                        "question_index": st.session_state.question_index,
                        "question": current_q["question"],
                        "user_answer": user_answer,
                        "correct_answer": correct_answer,
                        "is_correct": is_correct
                    })
                    
                    # Move to next question or finish test
                    if st.session_state.question_index < len(questions) - 1:
                        st.session_state.question_index += 1
                        st.rerun()
                    else:
                        # Finish test
                        test_id = list(st.session_state.user_manager.get_user_tests(st.session_state.current_user_id).keys())[0]
                        
                        # Calculate results
                        total_questions = len(questions)
                        correct_answers = sum(answer["is_correct"] for answer in st.session_state.user_answers)
                        score = (correct_answers / total_questions) * 100
                        
                        st.session_state.test_results = {
                            "test_id": test_id,
                            "test_name": st.session_state.current_test["test_name"],
                            "total_questions": total_questions,
                            "correct_answers": correct_answers,
                            "score": score,
                            "answers": st.session_state.user_answers
                        }
                        
                        # Save results
                        st.session_state.user_manager.save_test_results(
                            user_id=st.session_state.current_user_id,
                            test_id=test_id,
                            results=st.session_state.test_results
                        )
                        
                        # Update analytics
                        st.session_state.analytics.process_test_results(
                            user_id=st.session_state.current_user_id,
                            test_results=st.session_state.test_results
                        )
                        
                        st.session_state.test_in_progress = False
                        st.success("Test completed! View your results below.")
                        st.rerun()
            
            with col3:
                if st.button("Finish Test"):
                    st.session_state.test_in_progress = False
                    st.rerun()
                    
            # Display progress bar
            st.progress((st.session_state.question_index + 1) / len(questions))
            
        # Display test results if available
        if not st.session_state.test_in_progress and st.session_state.test_results:
            st.header("Test Results")
            st.subheader(f"Test: {st.session_state.test_results['test_name']}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Score", f"{st.session_state.test_results['score']:.1f}%")
            with col2:
                st.metric("Correct Answers", f"{st.session_state.test_results['correct_answers']}/{st.session_state.test_results['total_questions']}")
            with col3:
                accuracy = st.session_state.test_results['correct_answers'] / st.session_state.test_results['total_questions']
                if accuracy >= 0.8:
                    performance = "Excellent"
                elif accuracy >= 0.6:
                    performance = "Good"
                elif accuracy >= 0.4:
                    performance = "Average"
                else:
                    performance = "Needs Improvement"
                st.metric("Performance", performance)
            
            # Display detailed answers
            st.subheader("Question Review")
            for i, answer in enumerate(st.session_state.test_results["answers"]):
                with st.expander(f"Question {i+1}"):
                    st.write(answer["question"])
                    st.write(f"Your answer: {answer['user_answer']}")
                    st.write(f"Correct answer: {answer['correct_answer']}")
                    if answer["is_correct"]:
                        st.success("Correct!")
                    else:
                        st.error("Incorrect")
            
            if st.button("Take Another Test"):
                st.session_state.test_results = None
                st.rerun()

# Analytics page
elif st.session_state.page == "View Analytics":
    if not st.session_state.current_user_id:
        st.warning("Please login or register first.")
        st.session_state.page = "Login/Register"
        st.rerun()
    else:
        st.header("Performance Analytics")
        
        user_results = st.session_state.user_manager.get_all_test_results(st.session_state.current_user_id)
        
        if not user_results:
            st.info("No test results available. Take some tests to see analytics.")
        else:
            # Overall performance metrics
            st.subheader("Overall Performance")
            
            tests_taken = len(user_results)
            avg_score = sum(result["score"] for result in user_results) / tests_taken
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Tests Taken", tests_taken)
                st.metric("Average Score", f"{avg_score:.1f}%")
            
            with col2:
                # Performance trend chart
                if tests_taken > 1:
                    df = pd.DataFrame([
                        {"Test": result["test_name"], "Score": result["score"]}
                        for result in user_results
                    ])
                    st.line_chart(df.set_index("Test")["Score"])
                else:
                    st.info("Take more tests to see performance trends.")
            
            # Topic-wise performance
            st.subheader("Topic-wise Performance")
            
            # We'll need to collect and calculate topic-wise performance here
            # This is a placeholder for the actual implementation
            
            # Show topic performance if available
            topic_performance = st.session_state.analytics.get_topic_performance(st.session_state.current_user_id)
            
            if topic_performance:
                topic_df = pd.DataFrame(topic_performance)
                st.bar_chart(topic_df.set_index("Topic")["Score"])
            else:
                st.info("Not enough data to show topic-wise performance.")
            
            # Strengths and weaknesses
            st.subheader("Strengths and Areas for Improvement")
            
            strengths, weaknesses = st.session_state.analytics.get_strengths_and_weaknesses(
                st.session_state.current_user_id
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.success("Strengths")
                if strengths:
                    for strength in strengths:
                        st.write(f"• {strength}")
                else:
                    st.write("Take more tests to identify your strengths.")
            
            with col2:
                st.error("Areas for Improvement")
                if weaknesses:
                    for weakness in weaknesses:
                        st.write(f"• {weakness}")
                else:
                    st.write("Take more tests to identify areas for improvement.")
            
            # Recommendations
            st.subheader("Personalized Recommendations")
            recommendations = st.session_state.analytics.get_recommendations(st.session_state.current_user_id)
            
            if recommendations:
                for recommendation in recommendations:
                    st.info(recommendation)
            else:
                st.write("Take more tests to get personalized recommendations.")

# Footer
st.markdown("---")
st.markdown("© 2025 Adaptive MCQ Generator | Created with Streamlit") 