"""
Progress Tracker Module
Tracks user progress, scores, and adaptive learning difficulty
"""

from datetime import datetime
import json

class ProgressTracker:
    """Tracks and manages user learning progress"""
    
    def __init__(self, db):
        """Initialize progress tracker with database"""
        self.db = db
    
    def update_progress(self, topic, score, difficulty='medium', user_id=1):
        """
        Update user progress for a topic
        user_id defaults to 1 for demo purposes
        """
        from app import Progress
        
        # Create or update progress entry
        progress = Progress(
            user_id=user_id,
            topic=topic,
            difficulty=difficulty,
            score=score,
            data=json.dumps({'last_updated': datetime.utcnow().isoformat()})
        )
        
        self.db.session.add(progress)
        self.db.session.commit()
    
    def get_progress(self, user_id=1):
        """Get all progress for a user"""
        from app import Progress
        
        progress_entries = Progress.query.filter_by(user_id=user_id).all()
        
        progress_data = []
        for entry in progress_entries:
            progress_data.append({
                'topic': entry.topic,
                'difficulty': entry.difficulty,
                'score': entry.score,
                'completed_at': entry.completed_at.isoformat() if entry.completed_at else None
            })
        
        return progress_data
    
    def get_adaptive_difficulty(self, topic, user_id=1):
        """
        Determine adaptive difficulty based on past performance
        Returns: 'easy', 'medium', or 'hard'
        """
        from app import Progress
        
        # Get recent progress for this topic
        recent_progress = Progress.query.filter_by(
            user_id=user_id,
            topic=topic
        ).order_by(Progress.completed_at.desc()).limit(5).all()
        
        if not recent_progress:
            return 'medium'  # Default for new topics
        
        # Calculate average score
        scores = [p.score for p in recent_progress]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Adjust difficulty based on performance
        if avg_score >= 80:
            return 'hard'  # User is doing well, increase difficulty
        elif avg_score >= 60:
            return 'medium'
        else:
            return 'easy'  # User struggling, decrease difficulty

