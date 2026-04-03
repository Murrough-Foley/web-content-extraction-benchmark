# WCXB: Web Content Extraction Benchmark

**The largest open benchmark for evaluating web content extraction, boilerplate removal, and main content detection across diverse page types.**

WCXB provides 2,008 human-reviewed web pages spanning 7 page types and 1,613 domains, with ground truth annotations, HTML source files, and baseline results from 14 extraction systems. Unlike existing benchmarks that focus exclusively on news articles, WCXB evaluates extraction across the full diversity of the modern web — product pages, forums, documentation, service pages, listings, and collections — where current extractors fail most.

## Why WCXB?

Existing web content extraction benchmarks have critical blind spots:

| Benchmark | Year | Pages | Page Types | Public |
|-----------|------|------:|------------|:------:|
| CleanEval | 2007 | 797 | mixed (untyped) | yes |
| L3S-GN1 | 2010 | 621 | news only | yes |
| Dragnet | 2013 | 143 | articles only | yes |
| ScrapingHub | 2019 | 181 | articles only | yes |
| Google-Trends | 2017 | 180 | mixed (untyped) | yes |
| WebMainBench | 2025 | 7,809 | mixed (untyped) | no |
| **WCXB** | **2026** | **2,008** | **7 labeled types** | **yes** |

On articles, top extraction systems converge within 2-3 F1 points (0.91-0.93). But on forums, products, and collections, the gap widens to **20-30 F1 points** — a difference invisible to article-only benchmarks. WCXB is designed to reveal these blind spots.

## Dataset Overview

| | Development Set | Held-Out Test Set | Total |
|---|---:|---:|---:|
| **Pages** | 1,497 | 511 | 2,008 |
| **Domains** | 1,295 | 472 | 1,613 |
| **SPAs** | 19 | 4 | 23 |

### Page Type Distribution

| Page Type | Dev | Dev % | Test | Test % | Description |
|-----------|----:|------:|-----:|-------:|-------------|
| Article | 793 | 53.0% | 257 | 50.3% | Blog posts, news, editorials, guides, reviews |
| Service | 165 | 11.0% | 59 | 11.5% | SaaS pages, marketing, feature lists, pricing |
| Product | 119 | 7.9% | 28 | 5.5% | Individual product pages, specs, descriptions |
| Collection | 117 | 7.8% | 34 | 6.7% | Category pages, product grids, browse pages |
| Forum | 113 | 7.5% | 51 | 10.0% | Discussion threads, Q&A, community posts |
| Listing | 99 | 6.6% | 40 | 7.8% | Content indexes, course catalogs, review lists |
| Documentation | 91 | 6.1% | 42 | 8.2% | API docs, tutorials, wikis, technical references |

## Directory Structure

```
wcxb/
dev/
  ground-truth/       # 1,497 JSON ground truth files
  html/               # 1,497 gzipped HTML source files (.html.gz)
test/
  ground-truth/       # 511 JSON ground truth files
  html/               # 511 gzipped HTML source files (.html.gz)
metadata.json         # Page types, domains, split assignments
evaluate.py           # Standalone evaluation script
README.md             # This file
LICENSE               # CC-BY-4.0
```

## Ground Truth Format

Each JSON file follows this schema:

```json
{
  "schema_version": "2.0",
  "url": "https://example.com/page",
  "file_id": "0001",
  "_internal": {
    "page_type": {
      "primary": "article",
      "confidence": "verified"
    }
  },
  "ground_truth": {
    "title": "Page Title",
    "author": "Author Name",
    "publish_date": "2025-01-15",
    "main_content": "The full main content as plain text...",
    "with": ["snippet that must appear", "another required snippet"],
    "without": ["boilerplate snippet that must not appear"]
  }
}
```

### Field Descriptions

| Field | Description |
|-------|-------------|
| `main_content` | Complete main content as plain text. Headings on their own lines, paragraphs separated by `\n\n`. No markdown or HTML formatting. Never truncated (max ~50K chars). |
| `with[]` | 3-8 word snippets from the content that a correct extraction must include. Tests content completeness. |
| `without[]` | 3-8 word snippets from boilerplate (nav, ads, cookie banners) that a correct extraction must exclude. Tests boilerplate filtering. |
| `title` | Page title/heading. May be `null`. |
| `author` | Author name. May be `null`. |
| `publish_date` | Publication date. May be `null`. |

## Quick Start

### Evaluate Your Extractor

```python
python evaluate.py --extractor my_extractor --split dev
```

Or evaluate manually:

```python
import json, re
from pathlib import Path
from collections import Counter

def word_f1(predicted: str, reference: str) -> float:
    """Word-level F1 between predicted and reference text."""
    pred = Counter(re.findall(r'\w+', predicted.lower()))
    ref = Counter(re.findall(r'\w+', reference.lower()))
    if not ref:
        return 1.0 if not pred else 0.0
    if not pred:
        return 0.0
    overlap = sum((pred & ref).values())
    p = overlap / sum(pred.values())
    r = overlap / sum(ref.values())
    return 2 * p * r / (p + r) if (p + r) > 0 else 0.0

# Load ground truth
gt_dir = Path("dev/ground-truth")
for gt_file in sorted(gt_dir.glob("*.json")):
    with open(gt_file) as f:
        data = json.load(f)
    reference = data["ground_truth"]["main_content"]
    html_path = Path("dev/html") / f"{gt_file.stem}.html.gz"

    # Your extractor here:
    import gzip
    html = gzip.open(html_path, 'rt', encoding='utf-8').read()
    predicted = your_extractor(html)

    f1 = word_f1(predicted, reference)
    print(f"{gt_file.stem}: F1={f1:.3f}")
```

## Baseline Results

### Development Set (1,497 pages)

| System | Type | F1 | Precision | Recall |
|--------|------|---:|----------:|-------:|
| rs-trafilatura | Rule+ML | **0.859** | 0.863 | 0.890 |
| MinerU-HTML (0.6B) | Neural | 0.827 | 0.845 | 0.840 |
| Trafilatura | Rule | 0.791 | 0.852 | 0.793 |
| dom-smoothie | Rule | 0.762 | 0.806 | 0.768 |
| ReaderLM-v2 (1.5B) | Neural | 0.741 | 0.741 | 0.790 |
| Newspaper4k | Rule | 0.720 | 0.838 | 0.683 |
| magic-html | Rule | 0.719 | 0.813 | 0.713 |
| jusText | Rule | 0.707 | 0.771 | 0.695 |
| BoilerPy3 | Rule | 0.687 | 0.795 | 0.661 |
| Readability | Rule | 0.675 | 0.685 | 0.713 |
| Goose3 | Rule | 0.652 | 0.845 | 0.593 |

### F1 by Page Type (Development Set)

| Page Type | rs-traf | MinerU | Trafilatura | dom-smoothie | Readability |
|-----------|--------:|-------:|------------:|-------------:|------------:|
| Article | **0.932** | 0.928 | 0.926 | 0.908 | 0.825 |
| Documentation | **0.932** | 0.838 | 0.888 | 0.868 | 0.736 |
| Service | **0.844** | 0.824 | 0.763 | 0.714 | 0.604 |
| Forum | **0.808** | 0.794 | 0.585 | 0.530 | 0.466 |
| Collection | **0.716** | 0.506 | 0.553 | 0.504 | 0.445 |
| Listing | 0.707 | **0.710** | 0.589 | 0.596 | 0.496 |
| Product | **0.641** | 0.619 | 0.567 | 0.502 | 0.407 |

**Key finding:** On articles, all top systems converge (F1 0.91-0.93). On structured page types, the gap widens to 20-30 points — forums, collections, products, and service pages are where web content extraction remains unsolved.

### Held-Out Test Set (511 pages)

| System | Dev F1 | Test F1 |
|--------|-------:|--------:|
| rs-trafilatura | 0.859 | **0.893** |
| Trafilatura | 0.791 | 0.833 |
| dom-smoothie | 0.762 | 0.808 |
| Readability | 0.675 | 0.726 |

System rankings are preserved across splits, confirming generalization.

## Annotation Methodology

Ground truth was produced through a multi-stage pipeline:

1. **LLM-assisted drafting** — Claude generates initial annotations from HTML
2. **Multi-pass human review** — 4 independent review passes verify content completeness, boundaries, metadata accuracy, and snippet quality
3. **Automated quality checks** — 21-point scan verifies encoding, length, snippet validity, and boilerplate detection
4. **Adversarial review** — Files where top extractors achieve low F1 are flagged for re-examination (low scores often indicate GT errors, not extraction failures)

## Page Type Taxonomy

WCXB defines page types by **HTML structural differences that affect extraction behavior**, not by semantic content:

- **Article**: Single content container with sequential paragraphs. Standard extraction works well.
- **Forum**: Multiple user posts in sequence. Extractors that filter `class="comment"` elements lose the primary content.
- **Product**: Content often in JSON-LD structured data, not visible DOM. Tabbed interfaces hide content.
- **Collection**: Product grids with interleaved filter/navigation panels that extractors include as content.
- **Listing**: Repeated card elements. Single-node extraction captures one card instead of the full list.
- **Documentation**: Code blocks with sidebar navigation and TOC that extractors fail to exclude.
- **Service**: Content distributed across multiple `<section>` elements (hero, features, testimonials, pricing, FAQ). Single-node extraction captures at most one section.

## Use Cases

WCXB is designed for:

- **Benchmarking web content extractors** — main content extraction, boilerplate removal, text extraction from HTML
- **Evaluating web scraping quality** — how well does your scraper extract the actual content?
- **Training content extraction models** — 2,008 labeled HTML/text pairs across 7 page types
- **RAG pipeline evaluation** — is your retrieval-augmented generation system getting clean content?
- **Search engine indexing** — evaluating content pipelines for web indexing
- **NLP dataset construction** — ensuring clean text extraction from web sources
- **LLM training data curation** — filtering boilerplate from web crawl data

## Citation

```bibtex
@article{foley2026wcxb,
  title={{WCXB}: A Multi-Type Web Content Extraction Benchmark},
  author={Foley, Murrough},
  year={2026},
  url={https://github.com/murroughfoley/wcx}
}
```

## License

This dataset is released under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/) (CC-BY-4.0).

You are free to share and adapt this dataset for any purpose, including commercial use, as long as you provide appropriate attribution.

## Related Resources

- [rs-trafilatura](https://github.com/murroughfoley/rs-trafilatura) — Rust web content extraction library with page-type-aware profiles
- [web-page-classifier](https://crates.io/crates/web-page-classifier) — XGBoost page type classifier (7 types, 87% accuracy)
- [Trafilatura](https://github.com/adbar/trafilatura) — Python web content extraction library
- [MinerU-HTML](https://github.com/opendatalab/MinerU-HTML) — LLM-based HTML content extraction

## Acknowledgments

HTML source files are cached from publicly accessible web pages. Ground truth annotations contain only content visible on the original public pages.
