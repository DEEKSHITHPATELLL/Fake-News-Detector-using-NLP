from typing import List
import nltk
from nltk.tokenize import sent_tokenize

# Ensure punkt is available (train.py already triggers NLTK downloads, but be safe)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

def extract_candidate_claims(text: str, min_words: int = 3) -> List[str]:
    """Extract candidate claim sentences from a larger article text.

    This is a heuristic: split into sentences; filter by word count.
    min_words: minimum words per claim (default 3 for short phrases)
    """
    sents = sent_tokenize(text)
    candidates = []
    for s in sents:
        words = [w for w in s.split() if w.strip()]
        if len(words) >= min_words and len(s) < 400:
            candidates.append(s.strip())
    return candidates
