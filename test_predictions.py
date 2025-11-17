#!/usr/bin/env python
"""Demo script showing how to use the fake news detector."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from predict import predict
import json

# Test cases
test_cases = [
    ("Scientists confirm that vaccines reduce COVID risk by 90 percent", "Credible scientific claim"),
    ("Government approves new environmental policy to reduce carbon emissions", "Official news"),
    ("Miracle cure discovered that pharma companies are hiding from public", "Conspiracy claim"),
    ("Breaking: Celebrity X dies from secret government experiment", "Sensational fake"),
    ("City council approves new infrastructure project", "Local news"),
]

def main():
    print("=" * 80)
    print("FAKE NEWS DETECTOR - MODEL PREDICTIONS")
    print("=" * 80)
    print(f"\nTest Results (Label 0=Fake, Label 1=True):\n")
    
    for text, description in test_cases:
        print(f"\n[TEST] {description}")
        print(f"Text: {text}")
        
        result = predict(text, use_api=False)
        
        pred_label = result['predicted_label']
        prob_fake = result['probabilities'][0]
        prob_true = result['probabilities'][1]
        wn_hits = result['wordnet_hits']
        wn_total = result['wordnet_total_tokens']
        
        prediction = "🚨 FAKE NEWS" if pred_label == 0 else "✅ CREDIBLE"
        confidence = max(prob_fake, prob_true) * 100
        
        print(f"\nResult: {prediction} (Confidence: {confidence:.1f}%)")
        print(f"  - Fake probability:     {prob_fake:.3f}")
        print(f"  - True probability:     {prob_true:.3f}")
        print(f"  - WordNet match score:  {wn_hits}/{wn_total} tokens found")
        print("-" * 80)

if __name__ == '__main__':
    main()
