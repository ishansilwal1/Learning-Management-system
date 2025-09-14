"""
Simple ML training script for student risk assessment and grade prediction.
"""
import os
import numpy as np
import pandas as pd
import joblib
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score

# Get the project base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ML_DIR = os.path.join(BASE_DIR, 'ml')


def generate_synthetic_data(n_samples=2000):
    """Generate synthetic student performance data"""
    np.random.seed(42)
    
    data = []
    for i in range(n_samples):
        # Base academic ability (affects all metrics)
        ability = np.random.normal(0.7, 0.2)
        ability = np.clip(ability, 0.1, 1.0)
        
        # Motivation level
        motivation = np.random.normal(0.75, 0.15)
        motivation = np.clip(motivation, 0.2, 1.0)
        
        # Generate correlated features
        avg_score = ability * 90 + np.random.normal(0, 5)
        submission_rate = motivation * 95 + np.random.normal(0, 8)
        on_time_rate = (ability + motivation) / 2 * 90 + np.random.normal(0, 10)
        participation = motivation * 80 + np.random.normal(0, 10)
        
        # Clip values to reasonable ranges
        avg_score = np.clip(avg_score, 0, 100)
        submission_rate = np.clip(submission_rate, 0, 100)
        on_time_rate = np.clip(on_time_rate, 0, 100)
        participation = np.clip(participation, 0, 100)
        
        # Create risk level based on performance
        risk_score = 0
        if avg_score < 40: risk_score += 3
        elif avg_score < 60: risk_score += 2
        elif avg_score < 70: risk_score += 1
        
        if submission_rate < 50: risk_score += 2
        elif submission_rate < 70: risk_score += 1
        
        if on_time_rate < 50: risk_score += 2
        elif on_time_rate < 70: risk_score += 1
        
        # Map to risk levels
        if risk_score == 0: risk_level = 0  # Low
        elif risk_score <= 2: risk_level = 1  # Medium  
        elif risk_score <= 4: risk_level = 2  # High
        else: risk_level = 3  # Critical
        
        # Generate final grade
        final_grade = (avg_score * 0.4 + submission_rate * 0.2 + 
                      on_time_rate * 0.2 + participation * 0.2)
        final_grade = np.clip(final_grade + np.random.normal(0, 5), 0, 100)
        
        data.append({
            'avg_score': avg_score,
            'submission_rate': submission_rate,
            'on_time_rate': on_time_rate,
            'participation': participation,
            'assignment_count': np.random.randint(5, 20),
            'days_since_last': np.random.exponential(5),
            'risk_level': risk_level,
            'final_grade': final_grade
        })
    
    return pd.DataFrame(data)


def train_risk_model(data):
    """Train risk assessment model"""
    print("Training risk assessment model...")
    
    # Prepare features
    features = ['avg_score', 'submission_rate', 'on_time_rate', 'participation', 
               'assignment_count', 'days_since_last']
    X = data[features]
    y = data['risk_level']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Risk model accuracy: {accuracy:.3f}")
    
    # Save model and scaler
    models_dir = os.path.join(ML_DIR, 'models')
    joblib.dump(model, os.path.join(models_dir, 'risk_model.pkl'))
    joblib.dump(scaler, os.path.join(models_dir, 'risk_scaler.pkl'))
    
    return model, scaler, accuracy


def train_grade_model(data):
    """Train grade prediction model"""
    print("Training grade prediction model...")
    
    # Prepare features  
    features = ['avg_score', 'submission_rate', 'on_time_rate', 'participation',
               'assignment_count', 'days_since_last']
    X = data[features]
    y = data['final_grade']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = GradientBoostingRegressor(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"Grade model R²: {r2:.3f}, MSE: {mse:.3f}")
    
    # Save model and scaler
    models_dir = os.path.join(ML_DIR, 'models')
    joblib.dump(model, os.path.join(models_dir, 'grade_model.pkl'))
    joblib.dump(scaler, os.path.join(models_dir, 'grade_scaler.pkl'))
    
    return model, scaler, r2


def train_and_save_models(samples=2000):
    """Train and save ML models with specified number of samples."""
    print(f"Starting ML model training with {samples} samples...")
    
    # Generate synthetic data
    print("Generating synthetic data...")
    data = generate_synthetic_data(samples)
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(ML_DIR, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Save data
    data.to_csv(os.path.join(data_dir, 'training_data.csv'), index=False)
    print(f"Data saved to {data_dir}/training_data.csv")
    
    # Train models
    risk_model, risk_scaler, risk_acc = train_risk_model(data)
    grade_model, grade_scaler, grade_r2 = train_grade_model(data)
    
    # Save metadata
    metadata = {
        'training_date': datetime.now().isoformat(),
        'samples': len(data),
        'risk_accuracy': float(risk_acc),
        'grade_r2': float(grade_r2),
        'features': ['avg_score', 'submission_rate', 'on_time_rate', 'participation',
                    'assignment_count', 'days_since_last']
    }
    
    import json
    models_dir = os.path.join(ML_DIR, 'models')
    with open(os.path.join(models_dir, 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\nTraining completed!")
    print(f"Risk model accuracy: {risk_acc:.3f}")
    print(f"Grade model R²: {grade_r2:.3f}")
    print(f"Models saved to: {models_dir}")
    
    return True


def main():
    """Main training function"""
    train_and_save_models(2000)
    
    # Save metadata
    metadata = {
        'training_date': datetime.now().isoformat(),
        'samples': len(data),
        'risk_accuracy': risk_acc,
        'grade_r2': grade_r2,
        'features': ['avg_score', 'submission_rate', 'on_time_rate', 'participation',
                    'assignment_count', 'days_since_last']
    }
    
    import json
    with open(os.path.join(ML_DIR, 'models', 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\nTraining completed!")
    print(f"Risk model accuracy: {risk_acc:.3f}")
    print(f"Grade model R²: {grade_r2:.3f}")
    print(f"Models saved to: {os.path.join(ML_DIR, 'models')}")


if __name__ == '__main__':
    main()