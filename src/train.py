import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report, accuracy_score
from sklearn.calibration import CalibratedClassifierCV
import joblib
from preprocess import preprocess_text_for_vectorizer

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'dataset.csv')
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'model.joblib')
VECT_PATH = os.path.join(os.path.dirname(__file__), '..', 'vectorizer.joblib')

def load_dataset(path=DATA_PATH):
    df = pd.read_csv(path)
    # Handle various column names
    if 'text' not in df.columns:
        raise ValueError('Dataset must contain a text column')
    if 'label' not in df.columns:
        raise ValueError('Dataset must contain a label column')
    # Optionally use title + text combined for richer features
    if 'title' in df.columns:
        df['combined_text'] = df['title'].fillna('') + ' ' + df['text'].fillna('')
        df['text'] = df['combined_text']
    return df

def prepare_X(df: pd.DataFrame, enable_spacy_normalization: bool = False):
    return df['text'].apply(lambda t: preprocess_text_for_vectorizer(t, enable_spacy_normalization)).tolist()

def train_and_save():
    df = load_dataset()
    X = prepare_X(df, enable_spacy_normalization=False)
    y = df['label'].values

    # Use stratified split with more validation data for better calibration
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # TF-IDF + Logistic Regression pipeline with adjusted hyperparameters
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1,2), min_df=2, max_df=0.8)
    # Use lower C value for less aggressive regularization, allowing model to adapt better
    clf = LogisticRegression(max_iter=1000, class_weight='balanced', C=0.5, solver='lbfgs')

    pipeline = make_pipeline(vectorizer, clf)

    # Wrap pipeline in a calibrated classifier with cross-validation for better probability estimates
    # Using isotonic regression for more flexible probability calibration
    calibrated = CalibratedClassifierCV(estimator=pipeline, cv=5, method='isotonic')
    calibrated.fit(X_train, y_train)

    # Evaluate (use calibrated predictions)
    preds = calibrated.predict(X_test)
    print('Accuracy:', accuracy_score(y_test, preds))
    print(classification_report(y_test, preds))
    
    # Also print probabilities to diagnose calibration
    probas = calibrated.predict_proba(X_test)
    print(f'Probability statistics (class 0):\n  Mean: {probas[:, 0].mean():.4f}\n  Std: {probas[:, 0].std():.4f}')
    print(f'Probability statistics (class 1):\n  Mean: {probas[:, 1].mean():.4f}\n  Std: {probas[:, 1].std():.4f}')

    # Save both the raw pipeline (for explainability) and the calibrated model (for prediction)
    RAW_PIPELINE_PATH = os.path.join(os.path.dirname(__file__), '..', 'pipeline_raw.joblib')
    joblib.dump(pipeline, RAW_PIPELINE_PATH)
    joblib.dump(calibrated, MODEL_PATH)
    print(f'Saved raw pipeline to {RAW_PIPELINE_PATH}')
    print(f'Saved calibrated pipeline to {MODEL_PATH}')

if __name__ == '__main__':
    train_and_save()
