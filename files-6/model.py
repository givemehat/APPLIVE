import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib
import json
import os

def train_model():
    # Generate dataset if not exists
    if not os.path.exists('dataset.csv'):
        import dataset  # runs the generation
        exec(open('dataset.py').read())

    df = pd.read_csv('dataset.csv')

    # Encode categoricals
    le_goal = LabelEncoder()
    le_behavior = LabelEncoder()
    le_label = LabelEncoder()

    df['Financial_Goal_enc'] = le_goal.fit_transform(df['Financial_Goal'])
    df['Loss_Reaction_enc'] = le_behavior.fit_transform(df['Loss_Reaction'])
    df['Label'] = le_label.fit_transform(df['Risk_Profile'])

    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import Pipeline

    features = ['Age', 'Monthly_Income', 'Investment_Experience',
                'Risk_Tolerance', 'Investment_Horizon',
                'Financial_Goal_enc', 'Loss_Reaction_enc']

    X = df[features]
    y = df['Label']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Primary: Logistic Regression with scaling pipeline
    lr = Pipeline([
        ('scaler', StandardScaler()),
        ('clf', LogisticRegression(max_iter=2000, random_state=42, C=1.0))
    ])
    lr.fit(X_train, y_train)
    lr_pred = lr.predict(X_test)
    lr_acc = accuracy_score(y_test, lr_pred)

    # Fallback: Decision Tree
    dt = DecisionTreeClassifier(max_depth=8, random_state=42)
    dt.fit(X_train, y_train)
    dt_pred = dt.predict(X_test)
    dt_acc = accuracy_score(y_test, dt_pred)

    print(f"Logistic Regression Accuracy: {lr_acc:.4f}")
    print(f"Decision Tree Accuracy: {dt_acc:.4f}")

    # Use best model
    best_model = lr if lr_acc >= dt_acc else dt
    best_name = "Logistic Regression" if lr_acc >= dt_acc else "Decision Tree"
    print(f"\nUsing: {best_name}")
    print("\nClassification Report:")
    best_pred = lr_pred if lr_acc >= dt_acc else dt_pred
    print(classification_report(y_test, best_pred, target_names=le_label.classes_))

    # Save model + encoders
    joblib.dump(best_model, 'risk_model.pkl')
    joblib.dump(le_goal, 'le_goal.pkl')
    joblib.dump(le_behavior, 'le_behavior.pkl')
    joblib.dump(le_label, 'le_label.pkl')

    # Save label mapping
    mapping = {int(i): label for i, label in enumerate(le_label.classes_)}
    with open('label_mapping.json', 'w') as f:
        json.dump(mapping, f)

    # Save average profiles per category for comparison chart
    df['Category'] = le_label.inverse_transform(df['Label'])
    avg_profiles = df.groupby('Category')[features[:-2]].mean().to_dict()
    with open('avg_profiles.json', 'w') as f:
        json.dump(avg_profiles, f)

    print("\nModel saved: risk_model.pkl")
    return best_model, le_goal, le_behavior, le_label


def predict_risk(user_data: dict):
    """
    user_data keys: Age, Monthly_Income, Investment_Experience,
                    Risk_Tolerance, Investment_Horizon,
                    Financial_Goal, Loss_Reaction
    Returns: risk_label (str), risk_score (0-100), probabilities (dict)
    """
    model = joblib.load('risk_model.pkl')  # Pipeline (scaler + clf)
    le_goal = joblib.load('le_goal.pkl')
    le_behavior = joblib.load('le_behavior.pkl')
    le_label = joblib.load('le_label.pkl')

    goal_enc = le_goal.transform([user_data['Financial_Goal']])[0]
    behavior_enc = le_behavior.transform([user_data['Loss_Reaction']])[0]

    import pandas as pd
    X = pd.DataFrame([{
        'Age': user_data['Age'],
        'Monthly_Income': user_data['Monthly_Income'],
        'Investment_Experience': user_data['Investment_Experience'],
        'Risk_Tolerance': user_data['Risk_Tolerance'],
        'Investment_Horizon': user_data['Investment_Horizon'],
        'Financial_Goal_enc': goal_enc,
        'Loss_Reaction_enc': behavior_enc
    }])

    pred = model.predict(X)[0]
    proba = model.predict_proba(X)[0]
    label = le_label.inverse_transform([pred])[0]

    # Map to classes
    classes = le_label.classes_  # alphabetical: Aggressive=0, Conservative=1, Moderate=2
    prob_dict = {classes[i]: float(proba[i]) for i in range(len(classes))}

    # Risk score: weighted 0–100
    # Conservative=20, Moderate=55, Aggressive=85 (centers)
    centers = {'Conservative': 20, 'Moderate': 55, 'Aggressive': 85}
    risk_score = sum(prob_dict[k] * centers[k] for k in centers)

    return label, round(risk_score, 1), prob_dict


if __name__ == '__main__':
    train_model()
