import pandas as pd
import string
import pickle
import os

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download NLTK data
nltk.download('stopwords')
nltk.download('wordnet')

# Load dataset
df = pd.read_csv("dataset/spam.csv", encoding='latin-1')
df = df[['v1', 'v2']]
df.columns = ['label', 'message']

# Convert labels
df['label'] = df['label'].map({'ham':0, 'spam':1})

# NLP preprocessing
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess(text):

    text = text.lower()

    text = text.translate(str.maketrans('', '', string.punctuation))

    words = text.split()

    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words]

    return " ".join(words)

df['message'] = df['message'].apply(preprocess)

X = df['message']
y = df['label']

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Models
models = {
    "Naive Bayes": MultinomialNB(),
    "Logistic Regression": LogisticRegression(max_iter=1000),
    "SVM": SVC(probability=True)
}

best_model = None
best_accuracy = 0

for name, model in models.items():

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('classifier', model)
    ])

    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)

    acc = accuracy_score(y_test, predictions)

    print(f"{name} Accuracy: {acc}")

    if acc > best_accuracy:
        best_accuracy = acc
        best_model = pipeline

# Save model
os.makedirs("saved_model", exist_ok=True)

pickle.dump(best_model, open("saved_model/best_model.pkl", "wb"))

print("Best model saved successfully!")

import matplotlib.pyplot as plt

model_names = []
accuracies = []

for name, model in models.items():

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer()),
        ('classifier', model)
    ])

    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)

    acc = accuracy_score(y_test, predictions)

    model_names.append(name)
    accuracies.append(acc)

plt.bar(model_names, accuracies)

plt.title("Model Accuracy Comparison")

plt.ylabel("Accuracy")

plt.savefig("static/model_comparison.png")