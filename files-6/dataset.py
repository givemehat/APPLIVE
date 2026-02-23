import pandas as pd
import numpy as np
import random

np.random.seed(42)
random.seed(42)

N = 1200

ages = np.random.randint(22, 65, N)
monthly_incomes = np.random.choice([5000, 10000, 20000, 35000, 50000, 75000, 100000, 150000, 200000], N)
experience = np.random.randint(0, 30, N)
risk_tolerance = np.random.randint(1, 6, N)
horizon = np.random.randint(6, 360, N)
goals = np.random.choice(['wealth', 'retirement', 'education', 'emergency'], N)
behaviors = np.random.choice(['panic-sell', 'hold', 'buy-more'], N)

def assign_label(row):
    score = 0
    age, income, exp, rt, hor, goal, behavior = row

    # Age: younger = more aggressive
    if age < 30: score += 3
    elif age < 45: score += 2
    else: score += 1

    # Income (monthly)
    if income > 75000: score += 3
    elif income > 30000: score += 2
    else: score += 1

    # Experience
    if exp > 10: score += 3
    elif exp > 3: score += 2
    else: score += 1

    # Risk tolerance (direct)
    score += rt

    # Horizon
    if hor > 120: score += 3
    elif hor > 36: score += 2
    else: score += 1

    # Goal
    goal_map = {'wealth': 3, 'retirement': 2, 'education': 1, 'emergency': 0}
    score += goal_map[goal]

    # Behavior
    behavior_map = {'buy-more': 3, 'hold': 2, 'panic-sell': 0}
    score += behavior_map[behavior]

    # Max score = 3+3+3+5+3+3+3 = 23
    if score <= 9: return 'Conservative'
    elif score <= 16: return 'Moderate'
    else: return 'Aggressive'

data = pd.DataFrame({
    'Age': ages,
    'Monthly_Income': monthly_incomes,
    'Investment_Experience': experience,
    'Risk_Tolerance': risk_tolerance,
    'Investment_Horizon': horizon,
    'Financial_Goal': goals,
    'Loss_Reaction': behaviors,
})

data['Risk_Profile'] = [
    assign_label([ages[i], monthly_incomes[i], experience[i], risk_tolerance[i],
                  horizon[i], goals[i], behaviors[i]])
    for i in range(N)
]

# Add some noise
noise_idx = np.random.choice(N, size=int(N * 0.05), replace=False)
for idx in noise_idx:
    data.at[idx, 'Risk_Profile'] = np.random.choice(['Conservative', 'Moderate', 'Aggressive'])

# Balance the dataset — oversample minority classes
from collections import Counter
counts = Counter(data['Risk_Profile'])
target_count = max(counts.values())

balanced_frames = [data]
for label, count in counts.items():
    deficit = target_count - count
    if deficit > 0:
        minority = data[data['Risk_Profile'] == label]
        extra = minority.sample(deficit, replace=True, random_state=42)
        balanced_frames.append(extra)

data = pd.concat(balanced_frames, ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)

data.to_csv('dataset.csv', index=False)
print("Dataset saved: dataset.csv")
print(data['Risk_Profile'].value_counts())
print(data.head())

if __name__ == '__main__':
    pass
