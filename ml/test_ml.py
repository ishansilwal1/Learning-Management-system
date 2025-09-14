"""Simple test script to verify ML functionality."""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LMS.settings')
django.setup()

from ml.predictions import get_student_analytics, load_models
from django.contrib.auth import get_user_model
from classes.models import ClassRoom

User = get_user_model()

def test_ml_system():
    """Test the ML system functionality."""
    print("Testing ML System...")
    
    # Test model loading
    print("\n1. Testing model loading...")
    models = load_models()
    if models:
        print("Models loaded successfully!")
        print(f"   - Risk model: {type(models['risk_model']).__name__}")
        print(f"   - Grade model: {type(models['grade_model']).__name__}")
    else:
        print("Failed to load models")
        return
    
    # Test with a real user and classroom if available
    print("\n2. Testing with real data...")
    try:
        users = User.objects.filter(user_type='normal')
        classrooms = ClassRoom.objects.all()
        
        if users.exists() and classrooms.exists():
            user = users.first()
            classroom = classrooms.first()
            
            print(f"   Testing with user: {user.username}")
            print(f"   Testing with classroom: {classroom.name}")
            
            analytics = get_student_analytics(user, classroom)
            
            print("Analytics generated successfully!")
            print(f"   - Risk Level: {analytics['risk_analysis']['risk_level']}")
            print(f"   - Predicted Grade: {analytics['grade_analysis']['predicted_grade']}")
            print(f"   - Performance Trend: {analytics['performance_trend']}")
            print(f"   - Summary: {analytics['summary']}")
            
        else:
            print("No users or classrooms found for testing")
            
    except Exception as e:
        print(f"Error during analytics test: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nML System test completed!")

if __name__ == '__main__':
    test_ml_system()