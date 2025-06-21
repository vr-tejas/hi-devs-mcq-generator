import json
import os
import uuid
import hashlib
from datetime import datetime

class UserManager:
    def __init__(self):
        """
        Initialize the UserManager with empty data structures.
        """
        # in a real application, this would connect to a database
        self.users = {}  # username -> user data
        self.tests = {}  # test_id -> test data
        self.results = {}  # user_id -> test_id -> results
        
        # create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # load existing data if available
        self._load_data()
    
    def _load_data(self):
        """
        Load user data from files (if they exist).
        In a production application, this would load from a database.
        """
        try:
            if os.path.exists('data/users.json'):
                with open('data/users.json', 'r') as f:
                    content = f.read().strip()
                    if content:  # check if the file is not empty
                        self.users = json.loads(content)
                    else:
                        self.users = {}
            
            if os.path.exists('data/tests.json'):
                with open('data/tests.json', 'r') as f:
                    content = f.read().strip()
                    if content:
                        self.tests = json.loads(content)
                    else:
                        self.tests = {}
            
            if os.path.exists('data/results.json'):
                with open('data/results.json', 'r') as f:
                    content = f.read().strip()
                    if content:
                        self.results = json.loads(content)
                    else:
                        self.results = {}
        except Exception as e:
            print(f"Error loading data: {e}")
            # initialize with empty data
            self.users = {}
            self.tests = {}
            self.results = {}
    
    def _save_data(self):
        """
        Save user data to files.
        In a production application, this would save to a database.
        """
        try:
            # make sure the directory exists
            os.makedirs('data', exist_ok=True)
            
            with open('data/users.json', 'w') as f:
                json.dump(self.users, f, indent=2)
            
            with open('data/tests.json', 'w') as f:
                json.dump(self.tests, f, indent=2)
            
            with open('data/results.json', 'w') as f:
                json.dump(self.results, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def _hash_password(self, password):
        """
        Simple password hashing.
        In a production application, use a proper password hashing library.
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def user_exists(self, username):
        """
        Check if a user exists.
        
        Args:
            username (str): Username to check
            
        Returns:
            bool: True if user exists, False otherwise
        """
        return username in self.users
    
    def add_user(self, username, password):
        """
        Add a new user.
        
        Args:
            username (str): Username
            password (str): Password
            
        Returns:
            bool: True if user was added successfully, False otherwise
        """
        if self.user_exists(username):
            return False
        
        self.users[username] = {
            'password_hash': self._hash_password(password),
            'created_at': datetime.now().isoformat(),
            'tests': []
        }
        
        self._save_data()
        return True
    
    def authenticate_user(self, username, password):
        """
        Authenticate a user.
        
        Args:
            username (str): Username
            password (str): Password
            
        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not self.user_exists(username):
            return False
        
        password_hash = self._hash_password(password)
        return password_hash == self.users[username]['password_hash']
    
    def create_test(self, user_id, test_name, subject, topics, questions, adaptive=True):
        """
        Create a new test for a user.
        
        Args:
            user_id (str): User ID
            test_name (str): Test name
            subject (str): Subject
            topics (list): List of topics
            questions (list): List of question dictionaries
            adaptive (bool): Whether the test is adaptive
            
        Returns:
            str: Test ID
        """
        test_id = str(uuid.uuid4())
        
        # Store test data
        self.tests[test_id] = {
            'test_name': test_name,
            'subject': subject,
            'topics': topics,
            'questions': questions,
            'created_at': datetime.now().isoformat(),
            'created_by': user_id,
            'adaptive': adaptive
        }
        
        # Associate test with user
        if user_id not in self.users:
            self.users[user_id] = {'tests': []}
        
        if 'tests' not in self.users[user_id]:
            self.users[user_id]['tests'] = []
        
        self.users[user_id]['tests'].append(test_id)
        
        self._save_data()
        return test_id
    
    def get_user_tests(self, user_id):
        """
        Get all tests for a user.
        
        Args:
            user_id (str): User ID
            
        Returns:
            dict: Dictionary of test_id -> test data
        """
        if not self.user_exists(user_id) or 'tests' not in self.users[user_id]:
            return {}
        
        user_tests = {}
        for test_id in self.users[user_id]['tests']:
            if test_id in self.tests:
                user_tests[test_id] = self.tests[test_id]
        
        return user_tests
    
    def get_test(self, test_id):
        """
        Get a test by ID.
        
        Args:
            test_id (str): Test ID
            
        Returns:
            dict: Test data or None if not found
        """
        return self.tests.get(test_id)
    
    def save_test_results(self, user_id, test_id, results):
        """
        Save test results for a user.
        
        Args:
            user_id (str): User ID
            test_id (str): Test ID
            results (dict): Test results
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.user_exists(user_id) or test_id not in self.tests:
            return False
        
        if user_id not in self.results:
            self.results[user_id] = {}
        
        # Add timestamp to results
        results['timestamp'] = datetime.now().isoformat()
        
        # Save results
        self.results[user_id][test_id] = results
        
        self._save_data()
        return True
    
    def get_test_results(self, user_id, test_id):
        """
        Get test results for a user and test.
        
        Args:
            user_id (str): User ID
            test_id (str): Test ID
            
        Returns:
            dict: Test results or None if not found
        """
        if user_id not in self.results or test_id not in self.results[user_id]:
            return None
        
        return self.results[user_id][test_id]
    
    def get_all_test_results(self, user_id):
        """
        Get all test results for a user.
        
        Args:
            user_id (str): User ID
            
        Returns:
            list: List of test results
        """
        if user_id not in self.results:
            return []
        
        return list(self.results[user_id].values())
    
    def get_user_performance(self, user_id):
        """
        Get overall performance metrics for a user.
        
        Args:
            user_id (str): User ID
            
        Returns:
            dict: Performance metrics
        """
        if user_id not in self.results:
            return {
                'tests_taken': 0,
                'average_score': 0,
                'total_questions': 0,
                'correct_answers': 0
            }
        
        test_results = self.results[user_id].values()
        
        if not test_results:
            return {
                'tests_taken': 0,
                'average_score': 0,
                'total_questions': 0,
                'correct_answers': 0
            }
        
        total_questions = sum(result.get('total_questions', 0) for result in test_results)
        correct_answers = sum(result.get('correct_answers', 0) for result in test_results)
        average_score = sum(result.get('score', 0) for result in test_results) / len(test_results)
        
        return {
            'tests_taken': len(test_results),
            'average_score': average_score,
            'total_questions': total_questions,
            'correct_answers': correct_answers
        }
    
    def get_topic_performance(self, user_id):
        """
        Get performance by topic for a user.
        
        Args:
            user_id (str): User ID
            
        Returns:
            dict: Dictionary of topic -> performance metrics
        """
        if user_id not in self.results:
            return {}
        
        topic_performance = {}
        
        for test_id, result in self.results[user_id].items():
            test = self.tests.get(test_id)
            
            if not test:
                continue
            
            # Get topics for this test
            topics = test.get('topics', [])
            
            # For each topic, update performance metrics
            for topic in topics:
                if topic not in topic_performance:
                    topic_performance[topic] = {
                        'total_questions': 0,
                        'correct_answers': 0
                    }
                
                # Simplified approach: divide the test questions equally among topics
                # In a real application, each question would be tagged with its specific topic
                topic_total_questions = result.get('total_questions', 0) / len(topics)
                topic_correct_answers = result.get('correct_answers', 0) / len(topics)
                
                topic_performance[topic]['total_questions'] += topic_total_questions
                topic_performance[topic]['correct_answers'] += topic_correct_answers
        
        # Calculate scores for each topic
        for topic, metrics in topic_performance.items():
            if metrics['total_questions'] > 0:
                metrics['score'] = (metrics['correct_answers'] / metrics['total_questions']) * 100
            else:
                metrics['score'] = 0
        
        return topic_performance 