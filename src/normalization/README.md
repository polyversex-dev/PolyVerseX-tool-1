# Market Normalization Module

This module processes raw Polymarket data and creates normalized, enriched representations for efficient semantic search and matching.

## Two Normalization Approaches

### 1. Full Normalization (`normalize_markets.py`)

- **Output**: `normalized_markets.json` (~29 MB)
- **Best for**: Maximum context, detailed analysis, comprehensive matching
- **Features**: Abbreviation expansion, entity extraction, detailed text cleaning

### 2. Simple Normalization (`simple_normalize.py`)

- **Output**: `simple_normalized_markets.json` (~15 MB, 48% smaller)
- **Best for**: Fast lookups, embeddings, human-readable debugging
- **Features**: Essential keywords, clean categories, compact format

## Features

### Text Normalization

- **Cleaning**: Removes extra whitespace, normalizes quotes, strips special characters
- **Abbreviation Expansion**: Expands common abbreviations (BTC → Bitcoin, POTUS → President of the United States, etc.)
- **Boilerplate Removal**: Minimizes repetitive resolution language
- **URL Simplification**: Converts long URLs to domain names

### Entity Extraction

- **Tickers**: Crypto and stock tickers ($BTC, ETH, etc.)
- **Prices**: Dollar amounts and percentages ($70k, 5%, etc.)
- **Dates**: Temporal expressions (Q1 2025, December 31 2024, etc.)
- **Comparators**: Threshold statements (above $70k, more than 50 seats, etc.)

### Category Inference

Automatically categorizes markets into:

- Politics (elections, candidates, government)
- Crypto (Bitcoin, Ethereum, DeFi, NFTs)
- Economics (GDP, recession, inflation, Fed)
- Sports (NBA, NFL, UEFA, championships)
- Finance (stocks, IPOs, earnings)
- Technology (AI, software, tech companies)
- Weather (climate, temperature, natural disasters)
- Entertainment (movies, awards, box office)
- Other

### Date Normalization

- Parses ISO format dates
- Extracts dates from descriptions
- Normalizes to YYYY-MM-DD format

## Output Formats

### Simple Format (Recommended)

```json
{
  "id": "market-identifier",
  "question": "Fed rate hike in 2025?",
  "slug": "fed-rate-hike-2025",
  "search_text": "[economics] fed rate hike in 2025 this market will resolve...",
  "keywords": ["fed", "rate", "hike", "federal", "funds", "meeting"],
  "category": "economics",
  "tickers": [],
  "numbers": ["2025"],
  "years": ["2025"],
  "end_date": "2025-12-31",
  "active": true,
  "closed": false,
  "icon": "https://..."
}
```

### Full Format

Each normalized market contains:

```json
{
  "question": "Original question text",
  "market_slug": "market-identifier",
  "question_normalized": "Cleaned question",
  "description_normalized": "Cleaned description without boilerplate",
  "searchable_text": "[category] Expanded question. Expanded description...",
  "entities": {
    "tickers": ["BTC", "ETH"],
    "prices": ["$70000", "5%"],
    "dates": ["December 31, 2025"],
    "comparators": ["above $70k"]
  },
  "category": "crypto",
  "end_date": "2025-12-31",
  "active": true,
  "closed": false,
  "has_liquidity_data": true
}
```

## Usage

### Full Normalization

```bash
# From the project root
python src/normalization/normalize_markets.py
```

### Simple Normalization (Recommended)

```bash
# From the project root
python src/normalization/simple_normalize.py
```

The script will:

1. Load `src/data/current_markets.json`
2. Process and normalize all markets
3. Save output to `src/data/normalized_markets.json`
4. Display statistics about categories and entities

## Next Steps

After normalization, the data is ready for:

1. **Vector Embedding Generation**: Create embeddings from `searchable_text`
2. **Index Building**: Build FAISS/HNSW index for fast KNN retrieval
3. **Feature Extraction**: Use extracted entities for reranking
4. **Search Pipeline**: Match tweets/articles to markets

## Performance

- Processes ~14,000 markets in under 30 seconds
- Extracts entities from 100% of markets
- Infers categories with high accuracy
- Minimal false positives in entity extraction

## Comparison: Simple vs Full

| Feature                    | Simple                          | Full                                           |
| -------------------------- | ------------------------------- | ---------------------------------------------- |
| **File Size**              | 15 MB                           | 29 MB                                          |
| **Processing Time**        | ~20 sec                         | ~30 sec                                        |
| **Keywords per Market**    | ~20                             | N/A                                            |
| **Abbreviation Expansion** | No                              | Yes (BTC → Bitcoin)                            |
| **Entity Extraction**      | Basic (tickers, numbers, years) | Detailed (tickers, prices, dates, comparators) |
| **Boilerplate Removal**    | Minimal                         | Extensive                                      |
| **Use Case**               | Embeddings, fast search         | Detailed analysis, reranking                   |
| **Readability**            | High (compact, clean)           | Medium (verbose)                               |
| **Recommended For**        | Production search               | Research, debugging                            |

### When to Use Each:

**Use Simple Normalization when:**

- Building semantic search (embeddings)
- Need fast processing and smaller files
- Want human-readable output for debugging
- Focusing on keyword-based matching

**Use Full Normalization when:**

- Need maximum context for analysis
- Building advanced reranking features
- Want detailed entity extraction
- Researching market patterns
