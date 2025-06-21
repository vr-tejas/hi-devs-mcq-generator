import pandas as pd
import numpy as np
from collections import defaultdict, Counter

class PerformanceAnalytics:
    def __init__(self):
        """
        Initialize the PerformanceAnalytics class.
        """
        self.user_performance = {}  # user_id -> performance data
    
    def process_test_results(self, user_id, test_results):
        """
        Process test results and update user performance metrics.
        
        Args:
            user_id (str): User ID
            test_results (dict): Test results
        """
        if user_id not in self.user_performance:
            self.user_performance[user_id] = {
                'tests': [],
                'topic_performance': defaultdict(list),
                'difficulty_performance': defaultdict(list),
                'recent_performance': []
            }
        
        # add test results to user's performance data
        self.user_performance[user_id]['tests'].append(test_results)
        
        # keep only the 10 most recent tests for recent performance
        self.user_performance[user_id]['recent_performance'].append({
            'test_name': test_results.get('test_name', 'Unknown Test'),
            'score': test_results.get('score', 0),
            'timestamp': test_results.get('timestamp', '')
        })
        
        self.user_performance[user_id]['recent_performance'] = sorted(
            self.user_performance[user_id]['recent_performance'],
            key=lambda x: x['timestamp'],
            reverse=True
        )[:10]
        
        # update topic performance (simplified approach)
        # in a real application, each question would have its topic and difficulty level
        if 'answers' in test_results:
            topic_correct = defaultdict(int)
            topic_total = defaultdict(int)
            difficulty_correct = defaultdict(int)
            difficulty_total = defaultdict(int)
            
            for answer in test_results['answers']:
                # Assume each answer has a topic and difficulty level
                # In this simplified version, we'll use placeholders
                topic = 'General'  # This would come from the question metadata
                difficulty = 'Medium'  # This would come from the question metadata
                
                topic_total[topic] += 1
                difficulty_total[difficulty] += 1
                
                if answer.get('is_correct', False):
                    topic_correct[topic] += 1
                    difficulty_correct[difficulty] += 1
            
            # Update topic performance
            for topic, total in topic_total.items():
                self.user_performance[user_id]['topic_performance'][topic].append({
                    'correct': topic_correct[topic],
                    'total': total,
                    'score': (topic_correct[topic] / total) * 100 if total > 0 else 0
                })
            
            # Update difficulty performance
            for difficulty, total in difficulty_total.items():
                self.user_performance[user_id]['difficulty_performance'][difficulty].append({
                    'correct': difficulty_correct[difficulty],
                    'total': total,
                    'score': (difficulty_correct[difficulty] / total) * 100 if total > 0 else 0
                })
    
    def get_overall_performance(self, user_id):
        """
        Get overall performance metrics for a user.
        
        Args:
            user_id (str): User ID
            
        Returns:
            dict: Performance metrics
        """
        if user_id not in self.user_performance:
            return {
                'tests_taken': 0,
                'average_score': 0,
                'high_score': 0,
                'low_score': 0,
                'improvement_rate': 0
            }
        
        tests = self.user_performance[user_id]['tests']
        
        if not tests:
            return {
                'tests_taken': 0,
                'average_score': 0,
                'high_score': 0,
                'low_score': 0,
                'improvement_rate': 0
            }
        
        scores = [test.get('score', 0) for test in tests]
        
        # Calculate improvement rate (comparing first and last test scores)
        improvement_rate = 0
        if len(scores) >= 2:
            first_score = scores[0]
            last_score = scores[-1]
            improvement_rate = ((last_score - first_score) / first_score) * 100 if first_score > 0 else 0
        
        return {
            'tests_taken': len(tests),
            'average_score': sum(scores) / len(scores) if scores else 0,
            'high_score': max(scores) if scores else 0,
            'low_score': min(scores) if scores else 0,
            'improvement_rate': improvement_rate
        }
    
    def get_topic_performance(self, user_id):
        """
        Get performance by topic for a user.
        
        Args:
            user_id (str): User ID
            
        Returns:
            list: List of topic performance metrics
        """
        if user_id not in self.user_performance:
            return []
        
        topic_performance = self.user_performance[user_id]['topic_performance']
        
        if not topic_performance:
            return []
        
        # Aggregate topic performance
        aggregated = []
        for topic, performances in topic_performance.items():
            total_correct = sum(p['correct'] for p in performances)
            total_questions = sum(p['total'] for p in performances)
            score = (total_correct / total_questions) * 100 if total_questions > 0 else 0
            
            aggregated.append({
                'Topic': topic,
                'Score': score,
                'TotalQuestions': total_questions
            })
        
        return sorted(aggregated, key=lambda x: x['Score'], reverse=True)
    
    def get_difficulty_performance(self, user_id):
        """
        Get performance by difficulty level for a user.
        
        Args:
            user_id (str): User ID
            
        Returns:
            list: List of difficulty performance metrics
        """
        if user_id not in self.user_performance:
            return []
        
        difficulty_performance = self.user_performance[user_id]['difficulty_performance']
        
        if not difficulty_performance:
            return []
        
        # Aggregate difficulty performance
        aggregated = []
        for difficulty, performances in difficulty_performance.items():
            total_correct = sum(p['correct'] for p in performances)
            total_questions = sum(p['total'] for p in performances)
            score = (total_correct / total_questions) * 100 if total_questions > 0 else 0
            
            aggregated.append({
                'Difficulty': difficulty,
                'Score': score,
                'TotalQuestions': total_questions
            })
        
        return sorted(aggregated, key=lambda x: x['Difficulty'])
    
    def get_performance_trend(self, user_id):
        """
        Get performance trend data for a user.
        
        Args:
            user_id (str): User ID
            
        Returns:
            list: List of test scores by date
        """
        if user_id not in self.user_performance:
            return []
        
        recent_performance = self.user_performance[user_id]['recent_performance']
        
        return [
            {
                'Test': perf['test_name'],
                'Score': perf['score'],
                'Date': perf['timestamp']
            }
            for perf in recent_performance
        ]
    
    def get_strengths_and_weaknesses(self, user_id):
        """
        Identify strengths and weaknesses based on topic performance.
        
        Args:
            user_id (str): User ID
            
        Returns:
            tuple: (strengths, weaknesses) as lists of topics
        """
        topic_performance = self.get_topic_performance(user_id)
        
        if not topic_performance:
            return [], []
        
        # Sort by score
        sorted_topics = sorted(topic_performance, key=lambda x: x['Score'], reverse=True)
        
        # Consider topics with at least 5 questions
        valid_topics = [t for t in sorted_topics if t['TotalQuestions'] >= 5]
        
        if not valid_topics:
            return [], []
        
        # Top 3 topics as strengths
        strengths = [f"{t['Topic']} ({t['Score']:.1f}%)" for t in valid_topics[:3] if t['Score'] >= 60]
        
        # Bottom 3 topics as weaknesses
        weaknesses = [f"{t['Topic']} ({t['Score']:.1f}%)" for t in valid_topics[-3:] if t['Score'] < 60]
        
        return strengths, weaknesses
    
    def get_recommendations(self, user_id):
        """
        Generate personalized recommendations based on performance.
        
        Args:
            user_id (str): User ID
            
        Returns:
            list: List of recommendation strings
        """
        if user_id not in self.user_performance:
            return ["Take some tests to get personalized recommendations."]
        
        recommendations = []
        
        # Get topic performance
        topic_performance = self.get_topic_performance(user_id)
        
        # Get difficulty performance
        difficulty_performance = self.get_difficulty_performance(user_id)
        
        # Get overall performance
        overall = self.get_overall_performance(user_id)
        
        # Recommend based on weak topics
        weak_topics = [t for t in topic_performance if t['Score'] < 60 and t['TotalQuestions'] >= 3]
        if weak_topics:
            for topic in weak_topics[:2]:  # Top 2 weakest topics
                recommendations.append(f"Focus on improving your knowledge of {topic['Topic']} (current score: {topic['Score']:.1f}%).")
        
        # Recommend based on difficulty levels
        if difficulty_performance:
            difficulties = {d['Difficulty']: d['Score'] for d in difficulty_performance}
            
            if 'Easy' in difficulties and difficulties['Easy'] < 80:
                recommendations.append("Work on mastering the basic concepts before moving to more advanced topics.")
            
            if 'Hard' in difficulties and difficulties['Hard'] < 50 and difficulties.get('Medium', 0) >= 70:
                recommendations.append("You're doing well with medium difficulty questions. Challenge yourself with more advanced questions.")
        
        # General recommendations
        if overall['tests_taken'] < 5:
            recommendations.append("Take more tests to get more accurate performance analytics.")
        
        if overall['improvement_rate'] < 0:
            recommendations.append("Your performance is declining. Consider reviewing the fundamentals again.")
        elif overall['improvement_rate'] > 20:
            recommendations.append("Great improvement! Keep up the good work.")
        
        # If no specific recommendations, add a general one
        if not recommendations:
            recommendations.append("Continue practicing to improve your performance.")
        
        return recommendations 