"""
Match Ratio Tuner - Test different thresholds to find the sweet spot
Helps find the optimal min_match_ratio for fuzzy matching
"""

import numpy as np
from collections import Counter


from utils.relevant_match import fuzzy_match_score

# Test cases: (search_term, listing_title, should_match)
# should_match = True means we want this listing included
# should_match = False means we want to exclude this listing

TEST_CASES = [
    # Suzuki cases - from actual logs
    ("Suzuki DS 250 SX V-STROM", "Suzuki 250 V-Strom", True),
    ("Suzuki DS 250 SX V-STROM", "2025 Suzuki V-STROM DS 250 SX", True),
    ("Suzuki DS 250 SX V-STROM", "Suzuki Vstrom 250", True),
    ("Suzuki DS 250 SX V-STROM", "Suzuki Dl1000 Vstrom", False),  # Wrong model
    
    # Honda cases
    ("Honda CB500X", "2022 Honda CB500X", True),
    ("Honda CB500X", "Honda CB 500X", True),
    ("Honda CB500X", "2014 Honda CRF", False),  # Wrong model
    
    # Kawasaki cases - with false positives from logs
    ("Kawasaki Ninja 400", "2023 Kawasaki Ninja 400 SE ABS Demo", True),
    ("Kawasaki Ninja 400", "2024 Kawasaki Ninja", True),
    ("Kawasaki Ninja 400", "Kawasaki KFX 400", False),  # ATV, not motorcycle!
    ("Kawasaki Ninja 400", "1988 Kawasaki Eliminator SE 400", False),  # Wrong model
    ("Kawasaki Ninja 400", "2024 Kawasaki Ninja 250", False),  # Wrong model number
    
    # BMW cases - with false positives from logs
    ("BMW G 310", "2022 BMW G 310 RS Sport", True),
    ("BMW G 310", "BMW G310", True),
    ("BMW G 310", "2021 bmw GS 310", False),  # GS not G
    ("BMW G 310", "2009 BMW 310 / 45 / G450", False),  # Old model, not G 310
    ("BMW G 310", "BMW 310", False),  # Too generic, could be many models
    ("BMW G 310", "BMW GS 310", False),  # GS not G
    
    # BMW GS 310 cases
    ("BMW GS 310", "2022 Bmw Gs 310 Rallye Limited Edition", True),
    ("BMW GS 310", "BMW 310", False),  # Too generic
    
    # Triumph cases
    ("Triumph Scrambler 400", "2025 Triumph Scrambler 400", True),
    ("Triumph Scrambler 400", "Triumph Scrambler", True),
    ("Triumph Scrambler 400", "Triumph Speed 400", False),  # Wrong model
    
    # Ducati cases
    ("Ducati Scrambler", "2015 Ducati Scrambler Urban Enduro", True),
    ("Ducati Scrambler", "2015 Ducati X Scrambler", True),
    
    # Yamaha cases
    ("Yamaha MT-07", "2025 Yamaha MT-07", True),
    ("Yamaha MT-07", "Yamaha MT07", True),
    ("Yamaha MT-07", "Yamaha MT-09", False),  # Wrong model
]


def test_threshold(min_ratio):
    """Test a specific threshold and report accuracy"""
    correct = 0
    incorrect = 0
    false_positives = []  # Should NOT match but did
    false_negatives = []  # Should match but didn't
    all_scores = []
    
    print(f"\n{'='*80}")
    print(f"Testing threshold: {min_ratio}")
    print(f"{'='*80}")
    
    for search_term, listing_title, should_match in TEST_CASES:
        score = fuzzy_match_score(search_term, listing_title)
        would_match = score >= min_ratio
        
        if would_match == should_match:
            correct += 1
            status = "✓"
        else:
            incorrect += 1
            status = "✗"
            
            if would_match and not should_match:
                false_positives.append((search_term, listing_title, score))
            else:
                false_negatives.append((search_term, listing_title, score))
        
        match_str = "MATCH" if would_match else "SKIP "
        should_str = "✓" if should_match else "✗"
        print(f"{status} [{match_str}] score={score:.3f} | {search_term[:25]:25} → {listing_title[:40]:40} (want={should_str})")
    
    accuracy = (correct / len(TEST_CASES)) *100

    tp = sum(1 for s, l, m in TEST_CASES if fuzzy_match_score(s, l) >= min_ratio and m)
    fp = sum(1 for s, l, m in TEST_CASES if fuzzy_match_score(s, l) >= min_ratio and not m)
    fn = sum(1 for s, l, m in TEST_CASES if fuzzy_match_score(s, l) < min_ratio and m)

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0



    print(f"\n{'─'*80}")
    print(f"Accuracy: {accuracy:.1f}% | Precision: {precision:.3f} | Recall: {recall:.3f} | F1: {f1:.3f}")
    print(f"False Positives: {len(false_positives)} | False Negatives: {len(false_negatives)}")
    print(f"{'─'*80}")

    if false_positives:
        print("\nFalse Positives (matched when shouldn’t):")
        for search, listing, score in false_positives:
            print(f"  ✗ {search[:25]} → {listing[:40]} (score={score:.3f})")

    if false_negatives:
        print("\nFalse Negatives (missed valid match):")
        for search, listing, score in false_negatives:
            print(f"  ✗ {search[:25]} → {listing[:40]} (score={score:.3f})")

    return {
        "threshold": min_ratio,
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_pos": len(false_positives),
        "false_neg": len(false_negatives)
    }


def find_best_threshold():
    """Test multiple thresholds and find the best F1 score"""
    print("\n" + "="*80)
    print("MATCH RATIO TUNER - Finding optimal threshold")
    print("="*80)

    # Use dynamic threshold range
    thresholds = np.arange(0.35, 0.60, 0.005)
    results = []

    for threshold in thresholds:
        res = test_threshold(threshold)
        results.append(res)

    # Pick the best one based on F1 score
    best = max(results, key=lambda x: x["f1"])

    print("\n" + "="*80)
    print("SUMMARY - All Thresholds")
    print("="*80)
    print(f"{'Threshold':<12} {'Acc%':<8} {'Prec':<8} {'Rec':<8} {'F1':<8} {'F+':<6} {'F-':<6}")
    print("─" * 60)

    for r in results:
        marker = " ← BEST" if r["threshold"] == best["threshold"] else ""
        print(f"{r['threshold']:<12.3f} {r['accuracy']:<8.1f} {r['precision']:<8.2f} {r['recall']:<8.2f} {r['f1']:<8.2f} {r['false_pos']:<6} {r['false_neg']:<6}{marker}")

    print("\n" + "="*80)
    print(f"RECOMMENDATION: Use min_match_ratio = {best['threshold']:.3f}")
    print(f"  Accuracy:  {best['accuracy']:.1f}%")
    print(f"  Precision: {best['precision']:.3f}")
    print(f"  Recall:    {best['recall']:.3f}")
    print(f"  F1 Score:  {best['f1']:.3f}")
    print(f"  False Positives: {best['false_pos']}")
    print(f"  False Negatives: {best['false_neg']}")
    print("="*80 + "\n")

    return best["threshold"]



if __name__ == "__main__":
    best_threshold = find_best_threshold()
    
    print("NEXT STEPS:")
    print("1. Update utils/relevant_match.py:")
    print(f"   Change: min_match_ratio=0.35")
    print(f"   To:     min_match_ratio={best_threshold}")
    print("\n2. Update trackers/gumtreeTracker.py:")
    print(f"   Change: min_match_ratio=0.40")
    print(f"   To:     min_match_ratio={best_threshold}")
    print("\n3. Run: python main.py")
    print("\n4. Check tracker.log for improvements")