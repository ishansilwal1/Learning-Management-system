"""ML prediction functions for the LMS."""
import os
import numpy as np
from datetime import datetime, timedelta
from django.utils import timezone

try:
    import joblib
except ImportError:
    joblib = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ML_DIR = os.path.join(BASE_DIR, 'ml')


def load_models():
    """Load trained models and scalers."""
    if not joblib:
        print("joblib not available")
        return None
        
    models_dir = os.path.join(ML_DIR, 'models')
    
    try:
        risk_model = joblib.load(os.path.join(models_dir, 'risk_model.pkl'))
        risk_scaler = joblib.load(os.path.join(models_dir, 'risk_scaler.pkl'))
        grade_model = joblib.load(os.path.join(models_dir, 'grade_model.pkl'))
        grade_scaler = joblib.load(os.path.join(models_dir, 'grade_scaler.pkl'))
        
        return {
            'risk_model': risk_model,
            'risk_scaler': risk_scaler,
            'grade_model': grade_model,
            'grade_scaler': grade_scaler
        }
    except Exception as e:
        print(f"Error loading models: {e}")
        return None


def collect_student_features(student, classroom):
    """Collect features for a student in a classroom"""
    from grades.models import Grade
    from assignments.models import Submission, Assignment
    
    # Get student's grades in this classroom
    grades = Grade.objects.filter(student=student, classroom=classroom)
    submissions = Submission.objects.filter(
        student=student, 
        assignment__classroom=classroom
    )
    assignments = Assignment.objects.filter(classroom=classroom)
    
    # Calculate metrics
    total_assignments = assignments.count()
    submitted_count = submissions.count()
    graded_count = grades.count()
    
    # Average score
    if graded_count > 0:
        avg_score = sum(float(g.marks_obtained) / float(g.total_marks) * 100 for g in grades)
        avg_score = avg_score / graded_count
    else:
        avg_score = 0
    
    # Submission rate
    submission_rate = (submitted_count / total_assignments * 100) if total_assignments > 0 else 0
    
    # On-time submission rate
    on_time_count = 0
    for submission in submissions:
        if submission.assignment.deadline and submission.assignment.deadline >= submission.submitted_at:
            on_time_count += 1
    
    on_time_rate = (on_time_count / submitted_count * 100) if submitted_count > 0 else 0
    
    # Participation score (simplified)
    participation = min(100, submission_rate + (on_time_rate * 0.5))
    
    # Days since last submission
    latest_submission = submissions.order_by('-submitted_at').first()
    if latest_submission:
        days_since_last = (timezone.now() - latest_submission.submitted_at).days
    else:
        days_since_last = 30  # Default for no submissions
    
    return {
        'avg_score': avg_score,
        'submission_rate': submission_rate,
        'on_time_rate': on_time_rate,
        'participation': participation,
        'assignment_count': total_assignments,
        'days_since_last': min(days_since_last, 30)  # Cap at 30 days
    }


def predict_student_risk(student, classroom):
    """Predict risk level for a student"""
    try:
        models = load_models()
        if not models:
            return {
                'risk_level': 'Medium',
                'risk_score': 0.5,
                'recommendations': ['ML models not available']
            }
        
        # Collect features
        features = collect_student_features(student, classroom)
        
        # Prepare input
        feature_values = [
            features['avg_score'],
            features['submission_rate'], 
            features['on_time_rate'],
            features['participation'],
            features['assignment_count'],
            features['days_since_last']
        ]
        
        X = np.array(feature_values).reshape(1, -1)
        X_scaled = models['risk_scaler'].transform(X)
        
        # Make prediction
        risk_pred = models['risk_model'].predict(X_scaled)[0]
        risk_proba = models['risk_model'].predict_proba(X_scaled)[0]
        
        # Map to text
        risk_levels = ['Low', 'Medium', 'High', 'Critical']
        risk_level = risk_levels[min(risk_pred, len(risk_levels)-1)]
        risk_score = float(risk_proba[min(risk_pred, len(risk_proba)-1)])
        
        # Generate recommendations
        recommendations = []
        if features['avg_score'] < 60:
            recommendations.append("Focus on improving assignment quality")
        if features['submission_rate'] < 70:
            recommendations.append("Submit assignments more consistently")
        if features['on_time_rate'] < 70:
            recommendations.append("Improve time management for deadlines")
        if features['days_since_last'] > 7:
            recommendations.append("Stay more engaged with recent assignments")
        
        if not recommendations:
            recommendations.append("Keep up the good work!")
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'recommendations': recommendations,
            'features': features
        }
    except Exception as e:
        print(f"Error in predict_student_risk: {e}")
        return {
            'risk_level': 'Medium',
            'risk_score': 0.5,
            'recommendations': ['Error calculating risk assessment'],
            'features': {}
        }


def predict_student_grade(student, classroom):
    """Predict final grade for a student"""
    try:
        models = load_models()
        if not models:
            return {
                'predicted_grade': 'B',
                'predicted_score': 75.0,
                'confidence': 0.5
            }
        
        # Collect features
        features = collect_student_features(student, classroom)
        
        # Prepare input
        feature_values = [
            features['avg_score'],
            features['submission_rate'],
            features['on_time_rate'], 
            features['participation'],
            features['assignment_count'],
            features['days_since_last']
        ]
        
        X = np.array(feature_values).reshape(1, -1)
        X_scaled = models['grade_scaler'].transform(X)
        
        # Make prediction
        predicted_score = models['grade_model'].predict(X_scaled)[0]
        predicted_score = np.clip(predicted_score, 0, 100)
        
        # Convert to letter grade
        if predicted_score >= 90:
            predicted_grade = 'A+'
        elif predicted_score >= 80:
            predicted_grade = 'A'
        elif predicted_score >= 70:
            predicted_grade = 'B+'
        elif predicted_score >= 60:
            predicted_grade = 'B'
        elif predicted_score >= 50:
            predicted_grade = 'C+'
        elif predicted_score >= 40:
            predicted_grade = 'C'
        elif predicted_score >= 30:
            predicted_grade = 'D'
        else:
            predicted_grade = 'F'
        
        # Simple confidence based on current performance
        current_avg = features['avg_score']
        confidence = 0.7 + 0.3 * (features['submission_rate'] / 100)
        
        return {
            'predicted_grade': predicted_grade,
            'predicted_score': round(float(predicted_score), 1),
            'confidence': round(confidence, 2),
            'features': features
        }
    except Exception as e:
        print(f"Error in predict_student_grade: {e}")
        return {
            'predicted_grade': 'B',
            'predicted_score': 75.0,
            'confidence': 0.5,
            'features': {}
        }


def get_student_analytics(student, classroom):
    """Get complete analytics for a student"""
    risk_analysis = predict_student_risk(student, classroom)
    grade_analysis = predict_student_grade(student, classroom)
    
    # Determine trend
    features = risk_analysis['features']
    if features['avg_score'] >= 75 and features['submission_rate'] >= 80:
        trend = 'Excellent'
    elif features['avg_score'] >= 60 and features['submission_rate'] >= 70:
        trend = 'Good'
    elif features['avg_score'] >= 50:
        trend = 'Average'
    else:
        trend = 'Needs Improvement'
    
    return {
        'risk_analysis': risk_analysis,
        'grade_analysis': grade_analysis,
        'performance_trend': trend,
        'summary': f"Risk: {risk_analysis['risk_level']}, Predicted: {grade_analysis['predicted_grade']}, Trend: {trend}"
    }