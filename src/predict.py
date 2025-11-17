import os
import joblib
import requests
from preprocess import preprocess_text_for_vectorizer, tokenize_and_lemmatize
from nltk.corpus import wordnet as wn
from claims import extract_candidate_claims
from typing import List
import math

# Lazy load sentence-transformers model for semantic matching
_ST_MODEL = None
def _load_st_model():
    global _ST_MODEL
    if _ST_MODEL is None:
        from sentence_transformers import SentenceTransformer
        _ST_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
    return _ST_MODEL

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'model.joblib')

# Fact-check API settings - using Google Fact Check API
FACTCHECK_API_URL = 'https://factchecktools.googleapis.com/v1alpha1/claims:search'
API_KEY_FILE = os.path.join(os.path.dirname(__file__), '..', 'Api key.txt')

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f'Model not found at {MODEL_PATH}. Run training first.')
    pipeline = joblib.load(MODEL_PATH)
    return pipeline

def wordnet_keyword_score(text):
    """Return a simple score based on how many tokens have WordNet synsets (proxy for 'known' keywords)."""
    tokens = tokenize_and_lemmatize(text)
    hits = 0
    for t in tokens:
        if wn.synsets(t):
            hits += 1
    return hits, len(tokens)

def call_factcheck_api(text):
    # Read API key
    if not os.path.exists(API_KEY_FILE):
        return {'error': 'API key file not found', 'ok': False}
    with open(API_KEY_FILE, 'r', encoding='utf-8') as f:
        api_key = f.read().strip()
    if not api_key:
        return {'error': 'API key file empty', 'ok': False}

    # Google Fact Check API: query for claims similar to the given text
    params = {
        'query': text[:256],  # API limits query length
        'key': api_key,
        'languageCode': 'en'
    }
    try:
        resp = requests.get(FACTCHECK_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        result = resp.json()
        # Extract claim review info if available
        claims = result.get('claims', [])
        reviews = []
        for claim in claims[:3]:  # Top 3 matching claims
            for review in claim.get('claimReview', []):
                reviews.append({
                    'text': claim.get('text'),
                    'verdict': review.get('textualRating'),
                    'url': review.get('url')
                })
        return {'ok': True, 'matched_claims': reviews, 'raw': result}
    except Exception as e:
        return {'ok': False, 'error': str(e)}


def check_claims_with_api(text: str, similarity_threshold: float = 0.72, use_semantic_matching: bool = False):
    """Extract candidate claims from text, query API per-claim, optionally with semantic matching.

    use_semantic_matching: when True, uses embeddings for better matching (slower, requires transformers).
    When False, uses string-based matching only (fast, no external dependencies).
    Returns a combined api_result similar to call_factcheck_api but aggregated across claims.
    """
    claims = extract_candidate_claims(text)
    if not claims:
        return {'ok': False, 'error': 'no candidate claims found'}

    aggregated_reviews = []
    raw_results = []
    
    # Load semantic model only if requested
    st = None
    if use_semantic_matching:
        try:
            st = _load_st_model()
            claim_embs = st.encode(claims, convert_to_tensor=True)
        except Exception as e:
            # If semantic matching fails, fall back to string-based matching
            st = None
    
    for i, claim in enumerate(claims):
        api_res = call_factcheck_api(claim)
        raw_results.append({'claim': claim, 'api': api_res})
        if not api_res.get('ok'):
            continue
        matched = api_res.get('matched_claims', [])
        if not matched:
            continue
        
        # If semantic matching is enabled and available
        if st is not None and use_semantic_matching:
            try:
                texts = [m.get('text') or '' for m in matched]
                if not any(texts):
                    continue
                matched_embs = st.encode(texts, convert_to_tensor=True)
                # compute cosine similarities
                from numpy import dot
                from numpy.linalg import norm
                import numpy as np
                ce = claim_embs[i].cpu().numpy()
                me = matched_embs.cpu().numpy()
                sims = (me @ ce) / (np.linalg.norm(me, axis=1) * np.linalg.norm(ce) + 1e-8)
                # find best match
                best_idx = int(sims.argmax())
                best_sim = float(sims[best_idx])
                if best_sim >= similarity_threshold:
                    aggregated_reviews.append(matched[best_idx])
            except Exception:
                # On error, add first match anyway
                aggregated_reviews.append(matched[0])
        else:
            # String-based matching: just add first match
            aggregated_reviews.append(matched[0])

    if not aggregated_reviews:
        return {'ok': True, 'matched_claims': [], 'raw': raw_results}
    return {'ok': True, 'matched_claims': aggregated_reviews, 'raw': raw_results}


def interpret_api_verdict(api_result):
    """Interpret the Google Fact Check API result and return a numeric label and confidence.

    Returns (label, confidence, details) where label is 0 (fake) or 1 (true) or None if no clear verdict.
    confidence is a 0..1 float representing fraction of matched reviews that support the label.
    details contains matched reviews for debugging.
    """
    if not api_result or not api_result.get('ok'):
        return None, 0.0, api_result

    reviews = api_result.get('matched_claims', [])
    if not reviews:
        return None, 0.0, api_result

    # Map textual verdicts to votes
    votes = []
    for r in reviews:
        v = r.get('verdict')
        if not v:
            continue
        v_low = v.lower()
        if 'false' in v_low or 'pants' in v_low or 'fake' in v_low:
            votes.append(0)
        elif 'true' in v_low or 'correct' in v_low or 'accurate' in v_low or 'true' in v_low:
            votes.append(1)
        elif 'mixture' in v_low or 'partly' in v_low or 'mixed' in v_low:
            # ambiguous - skip
            continue
        else:
            # unknown textual rating - skip
            continue

    if not votes:
        return None, 0.0, {'matched_claims': reviews}

    # majority vote
    true_votes = sum(votes)
    total = len(votes)
    label = 1 if true_votes >= (total / 2.0) else 0
    confidence = true_votes / total if label == 1 else (total - true_votes) / total
    return label, float(confidence), {'matched_claims': reviews}

def predict(text: str, use_api=False):
    pipeline = load_model()
    cleaned = preprocess_text_for_vectorizer(text, enable_spacy_normalization=False)
    pred = pipeline.predict([cleaned])[0]
    proba = pipeline.predict_proba([cleaned])[0].tolist() if hasattr(pipeline, 'predict_proba') else None

    wn_hits, total = wordnet_keyword_score(text)

    api_result = None
    api_label = None
    api_conf = 0.0
    decision_source = 'model'

    if use_api:
        # Use claim-level checking + semantic matching for better recall
        api_result = check_claims_with_api(text)
        api_label, api_conf, api_details = interpret_api_verdict(api_result)
        # If API produced a clear verdict, prefer it as authoritative
        if api_label is not None:
            final_label = int(api_label)
            decision_source = 'api'
        else:
            final_label = int(pred)
            decision_source = 'model'
    else:
        final_label = int(pred)

    return {
        'text': text,
        'predicted_label': int(pred),            # model's raw prediction
        'probabilities': proba,
        'wordnet_hits': wn_hits,
        'wordnet_total_tokens': total,
        'factcheck_api': api_result,
        'api_label': api_label,
        'api_confidence': api_conf,
        'final_label': final_label,
        'decision_source': decision_source,
    }


def explain_prediction(text: str, top_n: int = 10):
    """Return the top contributing features for the prediction (positive -> supports label 1).

    This helps diagnose why the model labeled a piece of text as fake/true.
    """
    pipeline = load_model()
    base = pipeline
    if hasattr(pipeline, 'estimator'):
        try:
            base = pipeline.estimator
        except Exception:
            base = pipeline
    vectorizer = None
    clf = None
    if hasattr(base, 'named_steps'):
        for name, step in base.named_steps.items():
            if hasattr(step, 'transform') and hasattr(step, 'get_feature_names_out'):
                vectorizer = step
            if hasattr(step, 'coef_'):
                clf = step
    else:
        # fallback: assume base is a sequence of steps
        try:
            vectorizer, clf = base.steps
        except Exception:
            pass

    if vectorizer is None or clf is None:
        return {'error': 'Could not locate vectorizer and classifier inside the saved pipeline.'}

    cleaned = preprocess_text_for_vectorizer(text, enable_spacy_normalization=False)
    Xv = vectorizer.transform([cleaned])

    feature_names = vectorizer.get_feature_names_out()

    # For binary logistic regression clf.coef_.shape == (1, n_features)
    coefs = clf.coef_
    if coefs.ndim == 2 and coefs.shape[0] == 1:
        coefs = coefs[0]

    # contribution = tfidf_value * coef
    try:
        arr = Xv.toarray()[0]
    except Exception:
        arr = Xv.todense().A1

    contrib = arr * coefs

    # Get top features supporting class 1 (positive contrib) and class 0 (negative contrib)
    top_pos_idx = contrib.argsort()[::-1][:top_n]
    top_neg_idx = contrib.argsort()[:top_n]

    def fmt(indices):
        res = []
        for i in indices:
            if arr[i] == 0:
                continue
            res.append({'feature': feature_names[i], 'tfidf': float(arr[i]), 'coef': float(coefs[i]), 'contrib': float(contrib[i])})
        return res

    return {
        'cleaned_text': cleaned,
        'top_positive_features': fmt(top_pos_idx),
        'top_negative_features': fmt(top_neg_idx),
    }

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('text', help='Text to classify')
    parser.add_argument('--api', action='store_true', help='Call external fact-check API (requires Api key.txt and valid URL)')
    parser.add_argument('--explain', action='store_true', help='Show top contributing features for the prediction')
    args = parser.parse_args()
    if args.explain:
        expl = explain_prediction(args.text, top_n=12)
        print('Explanation:')
        if 'error' in expl:
            print(expl['error'])
        else:
            print('\nCleaned text:')
            print(expl['cleaned_text'])
            print('\nTop features supporting TRUE (label=1):')
            for f in expl['top_positive_features']:
                print(f"  {f['feature']:20} tfidf={f['tfidf']:.4f} coef={f['coef']:.4f} contrib={f['contrib']:.4f}")
            print('\nTop features supporting FAKE (label=0):')
            for f in expl['top_negative_features']:
                print(f"  {f['feature']:20} tfidf={f['tfidf']:.4f} coef={f['coef']:.4f} contrib={f['contrib']:.4f}")
    else:
        out = predict(args.text, use_api=args.api)
        print(out)
