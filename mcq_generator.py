import random
import nltk
import numpy as np
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import cohere
import json
import os

class MCQGenerator:
    def __init__(self):
        """
        Initialize the MCQ Generator with default settings.
        """
        # try to load stopwords safely
        try:
            self.stop_words = set(stopwords.words('english'))
        except:
            # if stopwords fail to load, use a basic set of common english stopwords
            self.stop_words = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 
                              'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 
                              'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 
                              'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 
                              'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 
                              'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 
                              'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 
                              'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 
                              'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 
                              'through', 'during', 'before', 'after', 'above', 'below', 'to', 
                              'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 
                              'again', 'further', 'then', 'once', 'here', 'there', 'when', 
                              'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 
                              'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 
                              'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 
                              'can', 'will', 'just', 'don', 'should', 'now'])
        self.difficulty_levels = ["Easy", "Medium", "Hard"]
        
        # initialize cohere client
        self.cohere_client = cohere.Client("YOb0y5NihggjPCahUAP2S8i8k2epnfsDElDbZGxz")
        
                # fallback questions only used if AI generation fails
        self.fallback_questions = self._load_fallback_questions()
    
    def _load_fallback_questions(self):
        """
        Load minimal fallback questions when AI generation fails.
        """
        fallback_questions = {
            "Mathematics": {
                "Algebra": {
                    "Easy": [
                        {
                            "question": "What is 2 + 2?",
                            "options": ["3", "4", "5", "6"],
                            "correct_answer": "4",
                            "difficulty": "Easy"
                        }
                    ]
                }
            },
            "Computer Science": {
                "Programming": {
                    "Easy": [
                        {
                            "question": "Which of the following is a programming language?",
                            "options": ["HTML", "Python", "CSS", "JSON"],
                            "correct_answer": "Python",
                            "difficulty": "Easy"
                        }
                    ]
                }
            },
            "Science": {
                "Physics": {
                    "Easy": [
                        {
                            "question": "What is the SI unit of force?",
                            "options": ["Newton", "Joule", "Watt", "Pascal"],
                            "correct_answer": "Newton",
                            "difficulty": "Easy"
                        }
                    ]
                }
            }
        }
        
        return fallback_questions
    
    def generate_questions(self, subject, topics, difficulty, num_questions, content=None, custom_description=""):
        """
        Generate MCQ questions using Cohere AI based on subject, topics, difficulty, and custom description.
        
        Args:
            subject (str): The subject area (e.g., Mathematics, Science)
            topics (list): List of specific topics within the subject
            difficulty (str): Difficulty level (Easy, Medium, Hard)
            num_questions (int): Number of questions to generate
            content (str, optional): Educational content to base questions on
            custom_description (str, optional): Custom user description of what they want
            
        Returns:
            list: A list of question dictionaries
        """
        try:
            # Generate questions using Cohere AI
            ai_questions = self._generate_cohere_questions(
                subject=subject,
                topics=topics,
                difficulty=difficulty,
                num_questions=num_questions,
                content=content,
                custom_description=custom_description
            )
            
            if ai_questions and len(ai_questions) > 0:
                return ai_questions
            else:
                # fallback to minimal hardcoded questions only if AI fails
                print("AI generation failed, using fallback questions")
                return self._get_fallback_questions(subject, topics, difficulty, num_questions)
                
        except Exception as e:
            print(f"Error generating questions: {e}")
            # fallback to minimal hardcoded questions
            return self._get_fallback_questions(subject, topics, difficulty, num_questions)
    
    def _generate_cohere_questions(self, subject, topics, difficulty, num_questions, content, custom_description):
        """
        Generate questions using Cohere AI.
        """
        try:
            # Build the prompt for Cohere
            topics_str = ", ".join(topics)
            
            prompt = f"""Generate {num_questions} multiple-choice questions (MCQs) with the following specifications:

Subject: {subject}
Topics: {topics_str}
Difficulty Level: {difficulty}
"""
            
            if custom_description:
                prompt += f"""
IMPORTANT CUSTOM REQUIREMENTS (MUST FOLLOW EXACTLY): {custom_description}

CRITICAL: The questions MUST strictly follow the custom requirements above. Do not deviate from the specified topic or requirements.
"""
            
            if content and len(content.strip()) > 50:
                prompt += f"Base the questions on this educational content: {content}\n"
            
            # Prioritize custom description over general topics if provided
            focus_area = custom_description if custom_description else topics_str
            
            prompt += f"""
Requirements for each question:
1. Create exactly {num_questions} questions
2. Each question should have exactly 4 multiple choice options
3. Mark the correct answer clearly
4. Make sure the difficulty is {difficulty}
5. Questions should be educational and test understanding of: {focus_area}
6. STRICTLY FOLLOW the custom requirements if provided - do not include questions about other topics

Format your response as a valid JSON array like this example:
[
    {{
        "question": "What is the time complexity of binary search?",
        "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"],
        "correct_answer": "O(log n)",
        "difficulty": "{difficulty}"
    }},
    {{
        "question": "Which data structure follows LIFO principle?",
        "options": ["Queue", "Stack", "Array", "Tree"],
        "correct_answer": "Stack", 
        "difficulty": "{difficulty}"
    }}
]

Generate the questions now:"""

            # Call Cohere API
            response = self.cohere_client.generate(
                model="command",
                prompt=prompt,
                max_tokens=3000,
                temperature=0.3,  # Lower temperature for more focused, instruction-following responses
                stop_sequences=[]
            )
            
            # Get the response text
            result = response.generations[0].text.strip()
            
            # Try to extract JSON from the response
            try:
                # Look for JSON array in the response
                start_idx = result.find('[')
                end_idx = result.rfind(']') + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = result[start_idx:end_idx]
                    questions = json.loads(json_str)
                    
                    # Validate the questions format
                    validated_questions = []
                    for q in questions:
                        if all(key in q for key in ['question', 'options', 'correct_answer', 'difficulty']):
                            validated_questions.append(q)
                    
                    return validated_questions[:num_questions]
                else:
                    print(f"Could not find valid JSON in response: {result}")
                    return []
                    
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON response: {e}")
                print(f"Raw response: {result}")
                return []
                
        except Exception as e:
            print(f"Error in Cohere question generation: {e}")
            return []
    
    def _get_fallback_questions(self, subject, topics, difficulty, num_questions):
        """
        Get fallback questions when AI generation fails.
        """
        questions = []
        
        if subject in self.fallback_questions:
            for topic in topics:
                if topic in self.fallback_questions[subject]:
                    if difficulty in self.fallback_questions[subject][topic]:
                        questions.extend(self.fallback_questions[subject][topic][difficulty])
                    
                    # If we need more questions, also include questions from other difficulty levels
                    if len(questions) < num_questions:
                        for diff in self.difficulty_levels:
                            if diff != difficulty and diff in self.fallback_questions[subject][topic]:
                                questions.extend(self.fallback_questions[subject][topic][diff])
        
        # shuffle questions first
        random.shuffle(questions)
        
        # for each question, also randomize the order of options (while keeping track of correct answer)
        randomized_questions = []
        for question in questions[:num_questions]:
            # create a copy to avoid modifying original
            q_copy = question.copy()
            options = q_copy["options"].copy()
            correct_answer = q_copy["correct_answer"]
            
            # create pairs of (option, is_correct)
            option_pairs = [(opt, opt == correct_answer) for opt in options]
            
            # shuffle the options
            random.shuffle(option_pairs)
            
            # update the question with shuffled options
            q_copy["options"] = [pair[0] for pair in option_pairs]
            q_copy["correct_answer"] = correct_answer  # correct answer text stays the same
            
            randomized_questions.append(q_copy)
        
        return randomized_questions
    
    def adjust_difficulty(self, current_difficulty, performance_score):
        """
        Adjust question difficulty based on user performance.
        
        Args:
            current_difficulty (str): Current difficulty level
            performance_score (float): User performance score (0.0 to 1.0)
            
        Returns:
            str: New difficulty level
        """
        difficulty_index = self.difficulty_levels.index(current_difficulty)
        
        if performance_score >= 0.8:  # 80% or higher correct
            # Increase difficulty
            new_index = min(difficulty_index + 1, len(self.difficulty_levels) - 1)
        elif performance_score <= 0.4:  # 40% or lower correct
            # Decrease difficulty
            new_index = max(difficulty_index - 1, 0)
        else:
            # Keep the same difficulty
            new_index = difficulty_index
        
        return self.difficulty_levels[new_index]
    
    def extract_keywords(self, text):
        """
        Extract important keywords from text.
        
        Args:
            text (str): Text to extract keywords from
            
        Returns:
            list: List of important keywords
        """
        try:
            tokens = word_tokenize(text.lower())
            filtered_tokens = [word for word in tokens if word.isalnum() and word not in self.stop_words]
            
            # Use TF-IDF to find important words
            tfidf = TfidfVectorizer(max_features=10)
            try:
                tfidf_matrix = tfidf.fit_transform([text])
                feature_names = tfidf.get_feature_names_out()
                
                # Get top 5 keywords based on TF-IDF score
                tfidf_scores = tfidf_matrix.toarray()[0]
                keywords = [feature_names[i] for i in tfidf_scores.argsort()[-5:]]
                return keywords
            except:
                # Fallback: return most common words
                word_counts = {}
                for word in filtered_tokens:
                    if word in word_counts:
                        word_counts[word] += 1
                    else:
                        word_counts[word] = 1
                # Sort by frequency
                sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
                return [word for word, freq in sorted_words[:5]]
        except:
            # If tokenization fails, extract words using simple split
            words = text.lower().split()
            # Remove common words and short words
            filtered_words = [word for word in words 
                             if len(word) > 3 and word not in self.stop_words]
            # Count frequencies                
            word_counts = {}
            for word in filtered_words:
                if word in word_counts:
                    word_counts[word] += 1
                else:
                    word_counts[word] = 1
            # Sort by frequency
            sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
            return [word for word, freq in sorted_words[:5]] 