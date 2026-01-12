# Web Content Extraction Benchmark

**A large-scale benchmark for evaluating web content extraction and boilerplate removal algorithms.**

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.6+](https://img.shields.io/badge/Python-3.6+-green.svg)](https://www.python.org/)
[![Dataset: 1,507 pages](https://img.shields.io/badge/Dataset-1%2C507%20pages-orange.svg)](#dataset)

This benchmark provides **1,507 modern web pages** (collected in 2026) with AI-generated ground truth annotations for evaluating article body extraction quality. It uses the same evaluation methodology as the widely-cited [ScrapingHub Article Extraction Benchmark](https://github.com/scrapinghub/article-extraction-benchmark), enabling direct comparison while providing 8× more test pages from the modern web.

---

## Table of Contents

- [Results](#results)
- [Quick Start](#quick-start)
- [Dataset](#dataset)
- [Evaluation Methodology](#evaluation-methodology)
- [Open-Source Libraries](#open-source-libraries)
- [Running Your Extractor](#running-your-extractor)
- [Comparison with ScrapingHub Benchmark](#comparison-with-scrapinghub-benchmark)
- [Why This Benchmark?](#why-this-benchmark)
- [Data Format](#data-format)
- [Installation](#installation)
- [License](#license)
- [Citation](#citation)
- [Acknowledgments](#acknowledgments)

---

## Results

Results of evaluation on **1,507 modern web pages** (January 2026):

| Extractor | F1 Score | Precision | Recall | With% ↑ | Without% ↓ |
|-----------|----------|-----------|--------|---------|------------|
| **[rs-trafilatura](https://github.com/Murrough-Foley/rs-trafilatura)** | **0.688** | 0.622 | **0.870** | **56.8%** | 6.6% |
| [trafilatura](https://github.com/adbar/trafilatura) | 0.657 | 0.616 | 0.818 | 55.9% | **5.6%** |
| [dom-smoothie](https://crates.io/crates/dom-smoothie) | 0.654 | 0.604 | 0.823 | 54.8% | 5.6% |
| [go-trafilatura](https://github.com/markusmobius/go-trafilatura) | 0.620 | 0.537 | 0.733 | 56.5% | 6.3% |
| [go-readability](https://github.com/go-shiori/go-readability) | 0.608 | 0.521 | 0.729 | 55.1% | 6.0% |
| [dom-content-extraction](https://crates.io/crates/dom_content_extraction) | 0.605 | 0.556 | 0.814 | 51.5% | 17.3% |
| [boilerpy3](https://github.com/jmriebold/BoilerPy3) (DefaultExtractor) | 0.602 | 0.543 | 0.789 | 50.9% | 13.6% |
| [boilerpy3](https://github.com/jmriebold/BoilerPy3) (ArticleExtractor) | 0.584 | **0.574** | 0.700 | 41.7% | 7.5% |
| [beautifulsoup](https://www.crummy.com/software/BeautifulSoup/) | 0.576 | 0.554 | 0.745 | 38.8% | 8.9% |
| [readability-lxml](https://github.com/buriy/python-readability) | 0.503 | 0.399 | 0.834 | 36.0% | 12.0% |

**Metric explanations:**
- **F1 Score**: Harmonic mean of precision and recall (higher is better)
- **Precision**: Fraction of extracted content that is actual article text (higher is better)
- **Recall**: Fraction of article text that was successfully extracted (higher is better)
- **With%**: Percentage of "must-include" sentences found in extraction (higher is better)
- **Without%**: Percentage of boilerplate text found in extraction (lower is better)

### Key Findings

1. **rs-trafilatura achieves the highest F1 score (0.688)** on this modern web benchmark, with excellent recall (87%)
2. **trafilatura (Python)** follows closely with F1 of 0.657 and the lowest boilerplate leakage (5.6%)
3. **Rust-based extractors** (rs-trafilatura, dom-smoothie, dom-content-extraction) show competitive performance
4. **Modern web is challenging**: All extractors score lower on 2026 web pages compared to legacy benchmarks

> **Note on legacy HTML:** On the [ScrapingHub benchmark](https://github.com/scrapinghub/article-extraction-benchmark) (184 pages from 2019), **trafilatura (Python) achieves F1 of 0.958**, outperforming most other libraries on legacy web pages. The modern web benchmark presented here tests against 2026 design patterns, which pose different challenges. We recommend evaluating extractors on both benchmarks for comprehensive assessment.

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Murrough-Foley/web-content-extraction-benchmark.git
cd web-content-extraction-benchmark

# 2. Run your extractor on the HTML files and save output to output/
python your_extractor_script.py  # outputs to output/my-extractor.json

# 3. Evaluate
python evaluate.py
```

**Output:**
```
Extractor                F1             Precision      Recall         Accuracy
--------------------------------------------------------------------------------
my-extractor             0.725 +/- 0.009  0.698 +/- 0.011  0.754 +/- 0.008  0.142 +/- 0.025
```

---

## Dataset

### Overview

| Property | Value |
|----------|-------|
| **Total pages** | 1,507 |
| **Unique domains** | 1,507 (100% diverse) |
| **Collection date** | 2026 |
| **Ground truth method** | AI-generated with quality review |
| **HTML storage** | Gzip-compressed |
| **Total size** | ~83 MB |

### Content Types

The dataset includes diverse content from across the web:

- **News articles** and journalism
- **Blog posts** and opinion pieces
- **Technical documentation** and tutorials
- **How-to guides** and educational content
- **Product reviews** and comparisons
- **Corporate pages** and about pages
- **Research summaries** and reports

### Content Statistics

| Metric | Value |
|--------|-------|
| Min content length | 505 characters |
| Max content length | 38,600 characters |
| Median content length | 3,350 characters |
| Mean content length | 6,198 characters |
| HTML file size range | 15 KB – 8.5 MB |

### Dataset Curation

Pages were carefully filtered to ensure benchmark quality:

- ✅ **Included**: Article pages with substantial main content
- ❌ **Excluded**: Category/archive pages, product listings, directory pages
- ❌ **Excluded**: Pages with very short content (<500 characters)

---

## Evaluation Methodology

This benchmark uses the same evaluation approach as the [ScrapingHub Article Extraction Benchmark](https://github.com/scrapinghub/article-extraction-benchmark), enabling direct comparison of results.

### Metrics

| Metric | Description | Formula |
|--------|-------------|---------|
| **Precision** | What fraction of extracted text is actual article content? | TP / (TP + FP) |
| **Recall** | What fraction of the article was successfully extracted? | TP / (TP + FN) |
| **F1 Score** | Harmonic mean of precision and recall | 2 × (P × R) / (P + R) |
| **Accuracy** | Exact match after tokenization | extracted_tokens == ground_truth_tokens |

### Shingle-Based Matching

Unlike simple word overlap, this benchmark uses **4-gram shingle matching**:

1. Text is tokenized into words
2. Words are grouped into overlapping 4-word sequences (shingles)
3. Shingles are compared between extraction and ground truth
4. True positives, false positives, and false negatives are computed

**Why shingles?** Simple word overlap ignores word order. Shingle matching penalizes extractors that capture the right words but in the wrong order or context.

### Bootstrap Confidence Intervals

All metrics include ± standard deviation computed via bootstrap resampling (1,000 iterations), enabling statistically meaningful comparisons.

### Snippet Validation

In addition to standard metrics, this benchmark provides **snippet-based validation**:

- **"With" snippets**: Sentences that MUST appear in a good extraction
- **"Without" snippets**: Boilerplate text that should NOT appear

This catches edge cases where an extractor might score well on aggregate metrics but miss critical content or include obvious boilerplate.

---

## Open-Source Libraries

The following content extraction libraries have been evaluated on this benchmark:

### Python Libraries

| Library | Description | GitHub |
|---------|-------------|--------|
| **trafilatura** | Fast and accurate extraction with metadata support | [adbar/trafilatura](https://github.com/adbar/trafilatura) |
| **readability-lxml** | Python port of Mozilla's Readability.js | [buriy/python-readability](https://github.com/buriy/python-readability) |
| **boilerpy3** | Python port of boilerpipe (Java) | [jmriebold/BoilerPy3](https://github.com/jmriebold/BoilerPy3) |
| **beautifulsoup** | HTML/XML parsing library (baseline) | [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/) |

### Rust Libraries

| Library | Description | Crates.io |
|---------|-------------|-----------|
| **rs-trafilatura** | Rust port of trafilatura | [rs-trafilatura](https://github.com/Murrough-Foley/rs-trafilatura) |
| **dom-smoothie** | Readability-based extraction | [dom-smoothie](https://crates.io/crates/dom-smoothie) |
| **dom_content_extraction** | CETR/CETD algorithm implementation | [dom_content_extraction](https://crates.io/crates/dom_content_extraction) |

### Go Libraries

| Library | Description | GitHub |
|---------|-------------|--------|
| **go-trafilatura** | Go port of trafilatura | [markusmobius/go-trafilatura](https://github.com/markusmobius/go-trafilatura) |
| **go-readability** | Go port of Readability.js | [go-shiori/go-readability](https://github.com/go-shiori/go-readability) |

### Other Notable Libraries (Not Yet Benchmarked)

| Library | Language | GitHub |
|---------|----------|--------|
| **Readability.js** | JavaScript | [mozilla/readability](https://github.com/mozilla/readability) |
| **newspaper4k** | Python | [AndyTheFactory/newspaper4k](https://github.com/AndyTheFactory/newspaper4k) |
| **news-please** | Python | [fhamborg/news-please](https://github.com/fhamborg/news-please) |
| **Goose3** | Python | [goose3/goose3](https://github.com/goose3/goose3) |

*Want to add your library? Submit a pull request with your results!*

---

## Running Your Extractor

### Step 1: Process HTML Files

Read each gzipped HTML file, run your extraction, and collect results:

```python
import gzip
import json
from pathlib import Path

results = {}

for html_path in Path('html').glob('*.html.gz'):
    file_id = html_path.stem.replace('.html', '')

    # Read gzipped HTML
    with gzip.open(html_path, 'rt', encoding='utf-8') as f:
        html = f.read()

    # Run your extractor
    extracted_text = your_extractor(html)

    results[file_id] = {'articleBody': extracted_text}

# Save results
with open('output/my-extractor.json', 'w') as f:
    json.dump(results, f, ensure_ascii=False)
```

### Step 2: Output Format

Your output JSON must follow this structure:

```json
{
  "0001": {"articleBody": "Extracted text for page 0001..."},
  "0002": {"articleBody": "Extracted text for page 0002..."},
  "0003": {"articleBody": "Extracted text for page 0003..."}
}
```

- Keys must match file IDs (e.g., `0001`, `0002`)
- Each entry must have an `articleBody` field containing the extracted text

### Step 3: Evaluate

```bash
python evaluate.py
```

### Command-Line Options

```bash
python evaluate.py [OPTIONS]

Options:
  --n-bootstrap N    Bootstrap iterations for confidence intervals (default: 1000)
  --output FILE      Save detailed results to JSON file
  --snippets         Include snippet coverage metrics (With% and Without%)
  --seed N           Random seed for reproducibility (default: 42)
```

**Example with all options:**
```bash
python evaluate.py --snippets --output results.json --n-bootstrap 2000
```

---

## Comparison with ScrapingHub Benchmark

This benchmark follows the methodology established by [ScrapingHub's Article Extraction Benchmark](https://github.com/scrapinghub/article-extraction-benchmark), the most widely-used benchmark in this domain.

### Side-by-Side Comparison

| Aspect | ScrapingHub (2019) | This Benchmark (2026) |
|--------|--------------------|-----------------------|
| **Number of pages** | 184 | **1,507** |
| **Collection year** | 2019 | **2026** |
| **Unique domains** | ~100 | **1,507** |
| **Ground truth method** | Manual annotation | AI + quality review |
| **Evaluation metrics** | P/R/F1/Accuracy | P/R/F1/Accuracy + snippets |
| **Bootstrap CI** | Yes | Yes |
| **Dependencies** | None | None |

### Why Both Benchmarks Matter

**ScrapingHub Benchmark:**
- Established methodology and wide adoption
- Manual annotations (gold standard)
- Good for comparing against historical results

**This Benchmark:**
- Modern web pages (2026 design patterns)
- 8× larger dataset for statistical significance
- Tests against contemporary challenges (SPAs, paywalls, cookie banners)
- Snippet validation catches edge cases

**Recommendation:** Evaluate on both benchmarks for comprehensive assessment.

---

## Why This Benchmark?

### The Problem

Extracting main content from web pages is deceptively difficult. Modern websites contain:

- **Navigation menus** with dozens of links
- **Sidebars** with ads, related articles, and widgets
- **Cookie consent banners** and GDPR notices
- **Paywalls** and subscription prompts
- **Comment sections** and social sharing buttons
- **Footers** with legal text and site maps

A naive approach extracting all text will capture far more noise than signal. Sophisticated extraction algorithms must understand DOM structure, text density, and semantic signals.

### Why a New Benchmark?

The web has evolved significantly since 2019:

| Challenge | 2019 | 2026 |
|-----------|------|------|
| **JavaScript frameworks** | jQuery, basic React | Next.js, complex SPAs |
| **Layout patterns** | Simple grids | CSS Grid, Flexbox, containers |
| **Cookie banners** | Rare | Ubiquitous (GDPR, CCPA) |
| **Paywalls** | Some news sites | Widespread across content |
| **AI-generated content** | Minimal | Increasingly common |
| **Dark patterns** | Few | Newsletter popups, notification requests |

**Extractors optimized for 2019 web pages may struggle with 2026 patterns.** This benchmark provides a modern testbed.

### Key Features

- ✅ **Modern dataset**: 1,507 pages from 2026
- ✅ **Diverse sources**: Every page from a unique domain
- ✅ **Zero dependencies**: Evaluation uses only Python standard library
- ✅ **Industry-standard metrics**: Compatible with ScrapingHub methodology
- ✅ **Snippet validation**: Catches missed content and boilerplate leakage
- ✅ **Confidence intervals**: Statistical rigor with bootstrap resampling

---

## Data Format

### Ground Truth (ground-truth.json)

```json
{
  "0001": {
    "articleBody": "The main article text that extractors should capture...",
    "url": "https://example.com/article",
    "title": "Article Title",
    "author": "Author Name",
    "publish_date": "2025-01-15",
    "with": [
      "Sentence that MUST appear in extraction",
      "Another critical sentence from the article"
    ],
    "without": [
      "Subscribe to our newsletter",
      "Cookie policy text",
      "© 2025 Example Inc. All rights reserved."
    ]
  }
}
```

### HTML Files (html/*.html.gz)

- Gzip-compressed HTML files
- UTF-8 encoded
- Named by file ID (e.g., `0001.html.gz`)

### Prediction Output (output/*.json)

```json
{
  "0001": {"articleBody": "Your extracted text..."},
  "0002": {"articleBody": "Your extracted text..."}
}
```

---

## Installation

### Requirements

- Python 3.6 or higher
- No external dependencies (evaluation uses only standard library)

### Clone the Repository

```bash
git clone https://github.com/Murrough-Foley/web-content-extraction-benchmark.git
cd web-content-extraction-benchmark
```

### Verify Installation

```bash
python evaluate.py --help
```

---

## License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

You are free to:
- Use the benchmark for commercial and academic purposes
- Modify and distribute the code
- Use the dataset for training and evaluation

---

## Citation

If you use this benchmark in your research or development, please cite:

```bibtex
@misc{web-content-extraction-benchmark-2026,
  title={Web Content Extraction Benchmark},
  author={Foley, Murrough},
  year={2026},
  url={https://github.com/Murrough-Foley/web-content-extraction-benchmark},
  note={A benchmark dataset of 1,507 modern web pages for evaluating content extraction algorithms}
}
```

---

## Acknowledgments

- **Evaluation methodology** based on [ScrapingHub Article Extraction Benchmark](https://github.com/scrapinghub/article-extraction-benchmark)
- **Shingle matching approach** from [Moz Content Extraction Research](https://moz.com/devblog/benchmarking-python-content-extraction-algorithms-dragnet-readability-goose-and-eatiht/)
- **Ground truth generation** powered by frontier AI models with human quality review

---

## Contributing

Contributions are welcome! You can help by:

1. **Adding new extractor results**: Run your library and submit a PR with results
2. **Improving documentation**: Fix typos, add examples, clarify instructions
3. **Reporting issues**: Found a problem with the dataset? Open an issue

---

<p align="center">
  <b>Built for the web scraping and content extraction community</b><br>
  <a href="#results">Results</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#dataset">Dataset</a> •
  <a href="#open-source-libraries">Libraries</a>
</p>
