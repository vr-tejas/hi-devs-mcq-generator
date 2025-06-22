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
                    difficulty=difficulty,
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
                        
                        # Add timestamp to results
                        st.session_state.test_results["timestamp"] = pd.Timestamp.now().isoformat()
                        
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
        st.header("📊 Performance Analytics Dashboard")
        
        user_results = st.session_state.user_manager.get_all_test_results(st.session_state.current_user_id)
        
        if not user_results:
            st.info("📈 No test results available yet. Take some tests to unlock your personalized analytics dashboard!")
            st.markdown("### What you'll see here after taking tests:")
            st.markdown("- 📊 **Performance Trends** - Track your improvement over time")
            st.markdown("- 🎯 **Subject & Topic Analysis** - See your strongest and weakest areas") 
            st.markdown("- 🏆 **Achievement Metrics** - Monitor your progress and milestones")
            st.markdown("- 💡 **Smart Recommendations** - Get AI-powered study suggestions")
            st.markdown("- ⚡ **Difficulty Progression** - Understand your skill level growth")
        else:
            # Enhanced overall performance metrics
            st.subheader("🏆 Overall Performance Summary")
            
            tests_taken = len(user_results)
            scores = [result["score"] for result in user_results]
            avg_score = sum(scores) / tests_taken
            highest_score = max(scores)
            latest_score = scores[-1] if scores else 0
            
            # Calculate improvement
            improvement = 0
            if len(scores) >= 2:
                first_half = scores[:len(scores)//2] if len(scores) > 4 else scores[:2]
                second_half = scores[len(scores)//2:] if len(scores) > 4 else scores[2:]
                if first_half and second_half:
                    improvement = sum(second_half) / len(second_half) - sum(first_half) / len(first_half)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🎯 Tests Taken", tests_taken)
            with col2:
                st.metric("📊 Average Score", f"{avg_score:.1f}%", 
                         delta=f"{improvement:+.1f}%" if improvement != 0 else None)
            with col3:
                st.metric("🏆 Best Score", f"{highest_score:.1f}%")
            with col4:
                st.metric("📈 Latest Score", f"{latest_score:.1f}%")
            
            # Performance trend with better visualization
            st.subheader("📈 Performance Trend Over Time")
            if tests_taken > 1:
                # Create a more detailed trend chart
                trend_data = []
                for i, result in enumerate(user_results):
                    trend_data.append({
                        "Test_Number": i + 1,
                        "Score": result["score"],
                        "Test_Name": result["test_name"][:20] + "..." if len(result["test_name"]) > 20 else result["test_name"],
                        "Date": result.get("timestamp", f"Test {i+1}")[:10] if result.get("timestamp") else f"Test {i+1}"
                    })
                
                df = pd.DataFrame(trend_data)
                st.line_chart(df.set_index("Test_Number")["Score"], height=300)
                
                # Show trend insight
                if improvement > 5:
                    st.success(f"🔥 Great progress! You've improved by {improvement:.1f}% on average!")
                elif improvement > 0:
                    st.info(f"📊 You're improving! Average improvement of {improvement:.1f}%")
                elif improvement < -5:
                    st.warning("📉 Your scores are declining. Consider reviewing fundamentals.")
                else:
                    st.info("📊 Your performance is stable. Try more challenging topics!")
            else:
                st.info("Take more tests to see your progress trend.")
            
            # Clear and meaningful performance analysis
            st.subheader("📊 Detailed Performance Breakdown")
            
            # Analyze performance by subject and topic
            subject_performance = {}
            topic_performance = {}
            
            for result in user_results:
                subject = result.get('subject', 'General')
                topics = result.get('topics', ['General'])
                score = result['score']
                
                if subject not in subject_performance:
                    subject_performance[subject] = []
                subject_performance[subject].append(score)
                
                for topic in topics:
                    if topic not in topic_performance:
                        topic_performance[topic] = []
                    topic_performance[topic].append(score)
            
            # Subject Performance with clear context
            if subject_performance:
                st.markdown("### 📚 **Performance by Subject**")
                subject_cols = st.columns(len(subject_performance))
                
                for i, (subject, scores) in enumerate(subject_performance.items()):
                    avg_score = sum(scores) / len(scores)
                    test_count = len(scores)
                    
                    # Determine performance level
                    if avg_score >= 80:
                        level = "Excellent"
                        color = "🟢"
                    elif avg_score >= 70:
                        level = "Good"
                        color = "🟡"
                    elif avg_score >= 60:
                        level = "Average"
                        color = "🟠"
                    else:
                        level = "Needs Work"
                        color = "🔴"
                    
                    with subject_cols[i]:
                        st.metric(
                            label=f"{color} **{subject}**",
                            value=f"{avg_score:.0f}%",
                            delta=f"{test_count} test{'s' if test_count != 1 else ''}"
                        )
                        st.markdown(f"<div style='text-align: center; color: gray; font-size: 14px;'>{level}</div>", unsafe_allow_html=True)
                
                st.markdown("---")
            
            # Topic Performance with clear context
            if topic_performance:
                st.markdown("### 🏷️ **Performance by Topic**")
                
                # Sort topics by performance
                sorted_topics = sorted(topic_performance.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True)
                
                for topic, scores in sorted_topics[:6]:  # Show top 6 topics
                    avg_score = sum(scores) / len(scores)
                    test_count = len(scores)
                    
                    # Create a progress bar representation
                    progress_bar = "█" * int(avg_score // 10) + "░" * (10 - int(avg_score // 10))
                    
                    # Determine color
                    if avg_score >= 80:
                        emoji = "🟢"
                    elif avg_score >= 70:
                        emoji = "🟡"
                    elif avg_score >= 60:
                        emoji = "🟠"
                    else:
                        emoji = "🔴"
                    
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"{emoji} **{topic}**")
                    with col2:
                        st.markdown(f"`{progress_bar}` **{avg_score:.0f}%**")
                    with col3:
                        st.markdown(f"*{test_count} test{'s' if test_count != 1 else ''}*")
                
                st.markdown("---")
            
            # Difficulty analysis with better visualization
            st.markdown("### ⚡ **Difficulty Level Mastery**")
            
            difficulty_performance = {}
            for result in user_results:
                difficulty = result.get('difficulty', 'Medium')
                score = result['score']
                
                if difficulty not in difficulty_performance:
                    difficulty_performance[difficulty] = []
                difficulty_performance[difficulty].append(score)
            
            if difficulty_performance:
                # Order difficulties logically
                difficulty_order = ['Easy', 'Medium', 'Hard']
                ordered_difficulties = [d for d in difficulty_order if d in difficulty_performance]
                
                diff_cols = st.columns(len(ordered_difficulties))
                
                for i, difficulty in enumerate(ordered_difficulties):
                    scores = difficulty_performance[difficulty]
                    avg_score = sum(scores) / len(scores)
                    test_count = len(scores)
                    
                    # Determine mastery level
                    if difficulty == 'Easy':
                        if avg_score >= 85:
                            status = "Mastered ✅"
                            advice = "Ready for Medium!"
                        elif avg_score >= 70:
                            status = "Good Progress 📈"
                            advice = "Almost there!"
                        else:
                            status = "Needs Practice 📚"
                            advice = "Focus on basics"
                    elif difficulty == 'Medium':
                        if avg_score >= 75:
                            status = "Strong 💪"
                            advice = "Try Hard level!"
                        elif avg_score >= 60:
                            status = "Developing 🔧"
                            advice = "Keep practicing"
                        else:
                            status = "Challenging 🎯"
                            advice = "Review Easy first"
                    else:  # Hard
                        if avg_score >= 70:
                            status = "Expert Level 🏆"
                            advice = "Outstanding!"
                        elif avg_score >= 50:
                            status = "Advanced 🚀"
                            advice = "Great progress!"
                        else:
                            status = "Tough 💪"
                            advice = "Very challenging"
                    
                    with diff_cols[i]:
                        st.metric(
                            label=f"**{difficulty} Level**",
                            value=f"{avg_score:.0f}%",
                            delta=f"{test_count} test{'s' if test_count != 1 else ''}"
                        )
                        st.markdown(f"<div style='text-align: center; color: #666; font-size: 14px; margin-top: -10px;'>{status}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div style='text-align: center; color: #888; font-size: 12px; font-style: italic;'>{advice}</div>", unsafe_allow_html=True)
            
            # Enhanced strengths and weaknesses with better insights
            st.subheader("💪 Strengths & 🎯 Areas for Improvement")
            
            col1, col2 = st.columns(2)
            
            # Calculate strengths and weaknesses based on actual data
            strong_subjects = [subj for subj, scores in subject_performance.items() 
                             if sum(scores)/len(scores) >= 75 and len(scores) >= 2]
            weak_subjects = [subj for subj, scores in subject_performance.items() 
                           if sum(scores)/len(scores) < 60 and len(scores) >= 2]
            
            strong_topics = [topic for topic, scores in topic_performance.items() 
                           if sum(scores)/len(scores) >= 75 and len(scores) >= 2]
            weak_topics = [topic for topic, scores in topic_performance.items() 
                         if sum(scores)/len(scores) < 60 and len(scores) >= 2]
            
            with col1:
                st.success("**💪 Your Strengths**")
                if strong_subjects or strong_topics:
                    if strong_subjects:
                        st.markdown("**Strong Subjects:**")
                        for subject in strong_subjects[:3]:
                            avg = sum(subject_performance[subject]) / len(subject_performance[subject])
                            st.markdown(f"🏆 {subject}: {avg:.1f}%")
                    
                    if strong_topics:
                        st.markdown("**Strong Topics:**")
                        for topic in strong_topics[:3]:
                            avg = sum(topic_performance[topic]) / len(topic_performance[topic])
                            st.markdown(f"⭐ {topic}: {avg:.1f}%")
                else:
                    st.markdown("Take more tests to identify your strengths!")
            
            with col2:
                st.error("**🎯 Focus Areas**")
                if weak_subjects or weak_topics:
                    if weak_subjects:
                        st.markdown("**Subjects to Improve:**")
                        for subject in weak_subjects[:3]:
                            avg = sum(subject_performance[subject]) / len(subject_performance[subject])
                            st.markdown(f"📚 {subject}: {avg:.1f}%")
                    
                    if weak_topics:
                        st.markdown("**Topics to Focus On:**")
                        for topic in weak_topics[:3]:
                            avg = sum(topic_performance[topic]) / len(topic_performance[topic])
                            st.markdown(f"🎯 {topic}: {avg:.1f}%")
                else:
                    st.markdown("Great job! No major weak areas identified.")
            
            # Actionable recommendations
            st.subheader("💡 Your Personal Study Plan")
            
            recommendations = []
            
            # Generate actionable recommendations based on data
            if weak_subjects:
                subject = weak_subjects[0]
                avg_score = sum(subject_performance[subject]) / len(subject_performance[subject])
                recommendations.append({
                    "priority": "🔴 HIGH PRIORITY",
                    "action": f"Improve {subject} Performance",
                    "current": f"Current: {avg_score:.0f}%",
                    "target": "Target: 70%+",
                    "plan": f"Take 2-3 more {subject} tests focusing on fundamentals. Review incorrect answers carefully."
                })
            
            if strong_subjects:
                subject = strong_subjects[0]
                avg_score = sum(subject_performance[subject]) / len(subject_performance[subject])
                recommendations.append({
                    "priority": "🟢 STRENGTH",
                    "action": f"Advance {subject} Skills",
                    "current": f"Current: {avg_score:.0f}%",
                    "target": "Target: 90%+",
                    "plan": f"Try harder difficulty levels in {subject}. Challenge yourself with advanced topics."
                })
            
            # Difficulty progression recommendations
            if 'Easy' in difficulty_performance:
                easy_avg = sum(difficulty_performance['Easy']) / len(difficulty_performance['Easy'])
                if easy_avg >= 85 and 'Medium' not in difficulty_performance:
                    recommendations.append({
                        "priority": "🟡 READY TO ADVANCE",
                        "action": "Progress to Medium Difficulty",
                        "current": f"Easy Level: {easy_avg:.0f}%",
                        "target": "Try Medium Level",
                        "plan": "You've mastered Easy level! Take your first Medium difficulty test."
                    })
                elif easy_avg < 70:
                    recommendations.append({
                        "priority": "🔴 FOUNDATION NEEDED",
                        "action": "Master Easy Level First",
                        "current": f"Easy Level: {easy_avg:.0f}%",
                        "target": "Target: 85%+",
                        "plan": "Focus on Easy level until you consistently score 85%+. Build strong fundamentals."
                    })
            
            if 'Medium' in difficulty_performance:
                medium_avg = sum(difficulty_performance['Medium']) / len(difficulty_performance['Medium'])
                if medium_avg >= 75 and 'Hard' not in difficulty_performance:
                    recommendations.append({
                        "priority": "🟡 READY FOR CHALLENGE",
                        "action": "Try Hard Difficulty",
                        "current": f"Medium Level: {medium_avg:.0f}%",
                        "target": "Try Hard Level",
                        "plan": "Excellent Medium performance! Ready for Hard difficulty challenges."
                    })
            
            if improvement < -10:
                recommendations.append({
                    "priority": "🔴 URGENT",
                    "action": "Performance Recovery",
                    "current": f"Declining by {abs(improvement):.1f}%",
                    "target": "Stabilize performance",
                    "plan": "Take a break, review your study method, and focus on easier topics to rebuild confidence."
                })
            elif improvement > 15:
                recommendations.append({
                    "priority": "🟢 EXCELLENT",
                    "action": "Maintain Momentum",
                    "current": f"Improving by {improvement:.1f}%",
                    "target": "Keep improving",
                    "plan": "Great progress! Continue your current study routine and gradually increase difficulty."
                })
            
            if tests_taken < 3:
                recommendations.append({
                    "priority": "🟡 GETTING STARTED",
                    "action": "Build Data History",
                    "current": f"Only {tests_taken} test{'s' if tests_taken != 1 else ''} taken",
                    "target": "Take 3+ tests",
                    "plan": "Take a few more tests to get accurate analytics and personalized recommendations."
                })
            
            if not recommendations:
                recommendations.append({
                    "priority": "🎉 EXCELLENT",
                    "action": "Well-Rounded Performance",
                    "current": "Consistent across all areas",
                    "target": "Continue excellence",
                    "plan": "You're performing well! Try exploring new subjects or increase difficulty levels."
                })
            
            # Display recommendations in a clean format
            for i, rec in enumerate(recommendations[:4], 1):
                with st.container():
                    col1, col2 = st.columns([3, 2])
                    with col1:
                        st.markdown(f"**{i}. {rec['action']}**")
                        st.markdown(f"*{rec['plan']}*")
                    with col2:
                        st.markdown(f"**{rec['priority']}**")
                        st.markdown(f"📊 {rec['current']}")
                        st.markdown(f"🎯 {rec['target']}")
                    st.markdown("---")
            
            # Study insights
            st.subheader("🧠 Study Insights")
            
            insights_col1, insights_col2 = st.columns(2)
            
            with insights_col1:
                st.markdown("**📅 Study Pattern**")
                if tests_taken >= 3:
                    recent_tests = user_results[-3:]
                    dates = [result.get('timestamp', '')[:10] for result in recent_tests if result.get('timestamp')]
                    if len(set(dates)) == len(dates):
                        st.success("✅ Consistent study schedule")
                    else:
                        st.warning("📅 Consider spacing out your tests more evenly")
                else:
                    st.info("Take more tests to analyze your study pattern")
            
            with insights_col2:
                st.markdown("**🎯 Accuracy Trend**")
                if tests_taken >= 3:
                    recent_avg = sum(scores[-3:]) / min(3, len(scores))
                    if recent_avg > avg_score:
                        st.success(f"📈 Recent improvement: +{recent_avg - avg_score:.1f}%")
                    elif recent_avg < avg_score - 5:
                        st.warning(f"📉 Recent decline: {recent_avg - avg_score:.1f}%")
                    else:
                        st.info("📊 Stable performance")
                else:
                    st.info("Take more tests to track accuracy trends")

# Footer
st.markdown("---")
st.markdown("© 2025 Adaptive MCQ Generator | Created with Streamlit") 