import json
import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

DATASET_DIR = "training_datasets"
PIPELINE_OUTPUT_PATH = "models/hybrid_pipeline.joblib"
ENCODER_OUTPUT_PATH = "models/label_encoder.pkl"

TEXT_FEATURE = 'text'
STRUCTURAL_FEATURES = [
    'features.font_size', 'features.is_centered', 'features.char_count',
    'features.x0_norm', 'features.height_norm',
    'features.has_leading_digit_or_bullet', 'features.relative_font_size_to_page_avg'
]

def main():
    all_data = []
    print(f"Loading all datasets from '{DATASET_DIR}'...")
    if not os.path.isdir(DATASET_DIR):
        raise FileNotFoundError(f"Error: The directory '{DATASET_DIR}' was not found.")
    for filename in os.listdir(DATASET_DIR):
        if filename.endswith((".json", ".jsonl")):
            filepath = os.path.join(DATASET_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                if filename.endswith(".json"):
                    data = json.load(f)
                    all_data.extend(data)
                else:
                    for line in f:
                        all_data.append(json.loads(line))
            print(f"  - Loaded records from {filename}")
    print(f"\nTotal records loaded: {len(all_data)}")

    df = pd.json_normalize(all_data)
    if TEXT_FEATURE not in df.columns:
        raise ValueError(f"'{TEXT_FEATURE}' column not found in the dataset.")

    X = df
    y = df['label']
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    preprocessor = ColumnTransformer(
        transformers=[
            ('text', TfidfVectorizer(ngram_range=(1, 2)), TEXT_FEATURE),
            ('struct', 'passthrough', STRUCTURAL_FEATURES)
        ])

    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    print("Training the hybrid model pipeline...")
    pipeline.fit(X_train, y_train)
    print("Pipeline training complete.")

    print("Evaluating hybrid model...")
    y_pred = pipeline.predict(X_test)
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

    os.makedirs(os.path.dirname(PIPELINE_OUTPUT_PATH), exist_ok=True)
    joblib.dump(pipeline, PIPELINE_OUTPUT_PATH)
    joblib.dump(label_encoder, ENCODER_OUTPUT_PATH)
    print("Successfully trained and saved the hybrid pipeline.")

if __name__ == "__main__":
    main()
