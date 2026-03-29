#!/usr/bin/env python3
"""
WCEB Evaluation Script

Evaluate a web content extraction system against the WCEB benchmark.

Usage:
    # Evaluate with a custom extractor function
    python evaluate.py --split dev --extractor trafilatura

    # Evaluate from a results JSON file
    python evaluate.py --split dev --results results.json

    # Show per-page-type breakdown
    python evaluate.py --split dev --results results.json --per-type
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

WCEB_DIR = Path(__file__).parent


def tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase words."""
    if not text:
        return []
    return re.findall(r'\w+', text.lower())


def word_f1(predicted: str, reference: str) -> tuple[float, float, float]:
    """Compute word-level precision, recall, and F1."""
    pred_tokens = tokenize(predicted)
    ref_tokens = tokenize(reference)

    if not ref_tokens:
        return (1.0, 1.0, 1.0) if not pred_tokens else (0.0, 0.0, 0.0)
    if not pred_tokens:
        return (0.0, 0.0, 0.0)

    pred_counts = Counter(pred_tokens)
    ref_counts = Counter(ref_tokens)
    overlap = sum((pred_counts & ref_counts).values())

    precision = overlap / len(pred_tokens)
    recall = overlap / len(ref_tokens)
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return (precision, recall, f1)


def snippet_check(text: str, snippets: list[str]) -> float:
    """Check what fraction of snippets appear in text."""
    if not snippets:
        return 1.0
    text_lower = text.lower()
    found = sum(1 for s in snippets if s.lower() in text_lower)
    return found / len(snippets)


def get_page_type(data: dict) -> str:
    """Extract page type from GT file."""
    internal = data.get('_internal', {}) or {}
    pt_obj = internal.get('page_type', {})
    if isinstance(pt_obj, dict):
        pt = pt_obj.get('primary', 'article')
    elif isinstance(pt_obj, str):
        pt = pt_obj
    else:
        pt = 'article'
    return 'collection' if pt == 'category' else pt


def load_ground_truth(split: str) -> dict:
    """Load all ground truth files for a split."""
    gt_dir = WCEB_DIR / split / "ground-truth"
    if not gt_dir.exists():
        print(f"Error: {gt_dir} does not exist")
        sys.exit(1)

    gt_data = {}
    for f in sorted(gt_dir.glob("*.json")):
        with open(f) as fh:
            data = json.load(fh)
        gt = data.get('ground_truth', {})
        if not isinstance(gt, dict):
            continue
        gt_data[f.stem] = {
            'main_content': gt.get('main_content', '') or '',
            'with': gt.get('with', []) or [],
            'without': gt.get('without', []) or [],
            'title': gt.get('title', ''),
            'page_type': get_page_type(data),
        }
    return gt_data


def evaluate_results(gt_data: dict, predictions: dict, per_type: bool = False):
    """Evaluate predictions against ground truth."""
    results = []
    type_results = defaultdict(list)

    for file_id, gt in sorted(gt_data.items()):
        predicted = predictions.get(file_id, '')
        reference = gt['main_content']

        p, r, f1 = word_f1(predicted, reference)
        with_rate = snippet_check(predicted, gt['with'])
        without_rate = snippet_check(predicted, gt['without'])

        result = {
            'file_id': file_id,
            'page_type': gt['page_type'],
            'precision': p,
            'recall': r,
            'f1': f1,
            'with_rate': with_rate,
            'without_rate': without_rate,
        }
        results.append(result)
        type_results[gt['page_type']].append(result)

    # Overall metrics
    n = len(results)
    avg_p = sum(r['precision'] for r in results) / n
    avg_r = sum(r['recall'] for r in results) / n
    avg_f1 = sum(r['f1'] for r in results) / n
    avg_with = sum(r['with_rate'] for r in results) / n
    avg_without = sum(r['without_rate'] for r in results) / n

    print(f"\nOverall ({n} pages):")
    print(f"  Precision:  {avg_p:.4f}")
    print(f"  Recall:     {avg_r:.4f}")
    print(f"  F1:         {avg_f1:.4f}")
    print(f"  With snippets:    {avg_with:.1%}")
    print(f"  Without snippets: {avg_without:.1%} (lower is better)")

    if per_type:
        TYPE_ORDER = ['article', 'forum', 'product', 'collection',
                      'listing', 'documentation', 'service']
        print(f"\nPer page type:")
        print(f"  {'Type':<16} {'N':>5} {'F1':>7} {'P':>7} {'R':>7}")
        print(f"  {'-'*44}")
        for pt in TYPE_ORDER:
            tr = type_results.get(pt, [])
            if not tr:
                continue
            tf1 = sum(r['f1'] for r in tr) / len(tr)
            tp = sum(r['precision'] for r in tr) / len(tr)
            tr_val = sum(r['recall'] for r in tr) / len(tr)
            print(f"  {pt:<16} {len(tr):>5} {tf1:>7.3f} {tp:>7.3f} {tr_val:>7.3f}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate web content extraction against WCEB benchmark"
    )
    parser.add_argument(
        '--split', default='dev', choices=['dev', 'test'],
        help="Which split to evaluate on (default: dev)"
    )
    parser.add_argument(
        '--results', type=str,
        help="JSON file with predictions: {file_id: extracted_text, ...}"
    )
    parser.add_argument(
        '--per-type', action='store_true',
        help="Show per-page-type breakdown"
    )
    args = parser.parse_args()

    gt_data = load_ground_truth(args.split)
    print(f"Loaded {len(gt_data)} ground truth files ({args.split} split)")

    if args.results:
        with open(args.results) as f:
            predictions = json.load(f)
        print(f"Loaded {len(predictions)} predictions")
    else:
        print("No --results file provided. Run with --results <file.json>")
        print("Expected format: {\"0001\": \"extracted text...\", \"0002\": \"...\"}")
        sys.exit(1)

    evaluate_results(gt_data, predictions, per_type=args.per_type)


if __name__ == "__main__":
    main()
