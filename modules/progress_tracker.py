"""
Progress Tracker Module
Tracks user progress, scores, and adaptive learning difficulty
"""

from datetime import datetime
import json

class ProgressTracker:
    """Tracks and manages user learning progress"""
    
    def __init__(self, db, progress_model=None):
        """Initialize progress tracker with database and Progress model"""
        self.db = db
        self.Progress = progress_model  # Store the model class
    
    def update_progress(self, topic, score, difficulty='medium', user_id=1):
        """
        Update user progress for a topic
        user_id defaults to 1 for demo purposes
        """
        # Use the Progress model passed during initialization
        if not self.Progress:
            # Fallback: try to import if not provided (for backward compatibility)
            from app import Progress as ProgressModel
            self.Progress = ProgressModel
        
        # Create or update progress entry
        # Note: Progress model uses 'difficulty_level' field name
        progress = self.Progress(
            user_id=user_id,
            topic=topic,
            difficulty_level=difficulty,  # Map 'difficulty' parameter to 'difficulty_level' field
            score=score,
            data=json.dumps({'last_updated': datetime.utcnow().isoformat()})
        )
        
        self.db.session.add(progress)
        self.db.session.commit()
    
    def get_progress(self, user_id=1):
        """Get all progress for a user"""
        # Use the Progress model passed during initialization
        if not self.Progress:
            # Fallback: try to import if not provided (for backward compatibility)
            from app import Progress as ProgressModel
            self.Progress = ProgressModel
        
        progress_entries = self.Progress.query.filter_by(user_id=user_id).all()
        
        progress_data = []
        for entry in progress_entries:
            progress_data.append({
                'topic': entry.topic,
                'difficulty': entry.difficulty_level,  # Map 'difficulty_level' field to 'difficulty' in response
                'score': entry.score,
                'completed_at': entry.completed_at.isoformat() if entry.completed_at else None
            })
        
        return progress_data
    
    def get_adaptive_difficulty(self, topic, user_id=1):
        """
        Determine adaptive difficulty based on past performance
        Returns: 'easy', 'medium', or 'hard'
        """
        # Use the Progress model passed during initialization
        if not self.Progress:
            # Fallback: try to import if not provided (for backward compatibility)
            from app import Progress as ProgressModel
            self.Progress = ProgressModel
        
        # Get recent progress for this topic
        recent_progress = self.Progress.query.filter_by(
            user_id=user_id,
            topic=topic
        ).order_by(self.Progress.completed_at.desc()).limit(5).all()
        
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

