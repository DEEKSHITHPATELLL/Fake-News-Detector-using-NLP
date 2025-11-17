import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import importlib

# Optional spaCy for entity normalization (lazy-loaded)
_SPACY = None

def _get_spacy():
    global _SPACY
    if _SPACY is None:
        try:
            import spacy
            try:
                _SPACY = spacy.load('en_core_web_sm')
            except Exception:
                # try to download small model
                from spacy.cli import download as spacy_download
                spacy_download('en_core_web_sm')
                _SPACY = spacy.load('en_core_web_sm')
        except Exception:
            _SPACY = None
    return _SPACY

# Ensure required NLTK data is available (will download if missing)
def ensure_nltk():
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
        nltk.data.find('corpora/wordnet')
        nltk.data.find('taggers/averaged_perceptron_tagger')
    except LookupError:
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('wordnet')
        nltk.download('omw-1.4')
        nltk.download('averaged_perceptron_tagger')
        nltk.download('averaged_perceptron_tagger_eng')

ensure_nltk()

STOPWORDS = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def clean_text(text: str) -> str:
    """Lowercase, remove non-alphanumeric (excluding spaces), and collapse whitespace."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def tokenize_and_lemmatize(text: str):
    tokens = nltk.word_tokenize(text)
    lemmas = []
    for token, pos in nltk.pos_tag(tokens):
        if token in STOPWORDS:
            continue
        pos_short = pos[0].lower()
        if pos_short == 'j':
            wn_pos = 'a'
        elif pos_short == 'v':
            wn_pos = 'v'
        elif pos_short == 'n':
            wn_pos = 'n'
        elif pos_short == 'r':
            wn_pos = 'r'
        else:
            wn_pos = 'n'
        lemmas.append(lemmatizer.lemmatize(token, wn_pos))
    return lemmas

def preprocess_text_for_vectorizer(text: str, enable_spacy_normalization: bool = False) -> str:
    """Return a cleaned string suitable for TF-IDF vectorizer (joined lemmas).

    enable_spacy_normalization: when True, replace named entities with entity-label tokens using spaCy.
    This can be slow over large datasets; default is False to keep training fast.
    """
    # Optional entity normalization
    if enable_spacy_normalization:
        try:
            spacy_model = _get_spacy()
            if spacy_model is not None:
                doc = spacy_model(text)
                ent_map = {}
                for ent in doc.ents:
                    ent_map[(ent.start_char, ent.end_char)] = f"__{ent.label_}__"
                if ent_map:
                    i = 0
                    out = ''
                    while i < len(text):
                        replaced = False
                        for (s, e), token in ent_map.items():
                            if i == s:
                                out += token
                                i = e
                                replaced = True
                                break
                        if not replaced:
                            out += text[i]
                            i += 1
                    text = out
        except Exception:
            pass

    cleaned = clean_text(text)
    lemmas = tokenize_and_lemmatize(cleaned)
    return " ".join(lemmas)
