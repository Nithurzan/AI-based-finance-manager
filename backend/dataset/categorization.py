import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib

# Sample training data
data = {
    "description": [
        "Starbucks coffee", "Uber ride", "Domino's Pizza", "Netflix", "Monthly salary", "Grocery store", "Bus ticket"
    ],
    "category": [
        "Food & Drink", "Travel", "Food & Drink", "Entertainment", "Income", "Groceries", "Travel"
    ]
}

df = pd.DataFrame(data)

# Train the model
model = make_pipeline(TfidfVectorizer(), MultinomialNB())
model.fit(df['description'], df['category'])

# Save the model
joblib.dump(model, "expense_categorizer.pkl")
