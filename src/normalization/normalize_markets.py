"""
Market Normalization Script

This script processes raw Polymarket data and creates normalized, enriched representations
for each market to enable efficient semantic search and matching.

Normalization includes:
- Text cleaning and standardization
- Entity extraction (people, orgs, locations, tickers)
- Date parsing and normalization
- Numeric threshold extraction
- Abbreviation expansion
- Category tagging
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class MarketNormalizer:
    """Normalizes and enriches market data for semantic search"""
    
    def __init__(self):
        # Common abbreviations in crypto/politics/sports
        self.abbreviations = {
            'POTUS': 'President of the United States',
            'SCOTUS': 'Supreme Court of the United States',
            'VP': 'Vice President',
            'PM': 'Prime Minister',
            'CEO': 'Chief Executive Officer',
            'BTC': 'Bitcoin',
            'ETH': 'Ethereum',
            'SOL': 'Solana',
            'GDP': 'Gross Domestic Product',
            'CPI': 'Consumer Price Index',
            'Fed': 'Federal Reserve',
            'FOMC': 'Federal Open Market Committee',
            'SEC': 'Securities and Exchange Commission',
            'NFT': 'Non-Fungible Token',
            'DeFi': 'Decentralized Finance',
            'AI': 'Artificial Intelligence',
            'UEFA': 'Union of European Football Associations',
            'NBA': 'National Basketball Association',
            'NFL': 'National Football League',
            'MLB': 'Major League Baseball',
            'GDP': 'Gross Domestic Product',
            'IPO': 'Initial Public Offering',
            'Q1': 'First Quarter',
            'Q2': 'Second Quarter',
            'Q3': 'Third Quarter',
            'Q4': 'Fourth Quarter',
        }
        
        # Regex patterns
        self.ticker_pattern = re.compile(r'\$[A-Z]{2,5}|[A-Z]{2,5}(?=/USD)|(?:BTC|ETH|SOL|DOGE|USDT|USDC|ADA|DOT|MATIC)')
        self.price_pattern = re.compile(r'\$[\d,]+(?:\.\d{1,2})?|\d+(?:,\d{3})*(?:\.\d+)?%?')
        self.date_pattern = re.compile(r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}|\d{1,2}/\d{1,2}/\d{2,4}|Q[1-4]\s+\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s+\d{1,2},?\s+\d{4}', re.IGNORECASE)
        self.comparator_pattern = re.compile(r'(?:above|below|over|under|more than|less than|at least|no more than|exceed|surpass|reach)\s+(?:\$?[\d,]+(?:\.\d+)?|[\d.]+%)', re.IGNORECASE)
        
        # Common boilerplate phrases to remove or minimize
        self.boilerplate_phrases = [
            'This market will resolve to',
            'Otherwise, this market will resolve to',
            'The resolution source will be',
            'The primary resolution source',
            'however a consensus of credible reporting may also be used',
            'Please refer to',
        ]
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove URLs but keep the domain for context
        text = re.sub(r'https?://(?:www\.)?([^/\s]+)[^\s]*', r'\1', text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\$%\.,;:\-/()\'\"]+', ' ', text)
        
        return text.strip()
    
    def expand_abbreviations(self, text: str) -> str:
        """Expand common abbreviations"""
        expanded = text
        for abbr, full in self.abbreviations.items():
            # Word boundary matching to avoid partial replacements
            pattern = r'\b' + re.escape(abbr) + r'\b'
            expanded = re.sub(pattern, f"{abbr} ({full})", expanded, flags=re.IGNORECASE)
        return expanded
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract entities from text using pattern matching"""
        entities = {
            'tickers': [],
            'prices': [],
            'dates': [],
            'comparators': []
        }
        
        # Extract crypto/stock tickers
        tickers = self.ticker_pattern.findall(text)
        entities['tickers'] = list(set([t.upper().replace('$', '') for t in tickers]))
        
        # Extract prices and percentages
        prices = self.price_pattern.findall(text)
        entities['prices'] = list(set(prices))
        
        # Extract dates
        dates = self.date_pattern.findall(text)
        entities['dates'] = list(set(dates))
        
        # Extract comparative statements
        comparators = self.comparator_pattern.findall(text)
        entities['comparators'] = list(set(comparators))
        
        return entities
    
    def parse_end_date(self, end_date_iso: Optional[str], description: str) -> Optional[str]:
        """Parse and normalize end date"""
        if end_date_iso:
            try:
                # Try parsing ISO format
                dt = datetime.fromisoformat(end_date_iso.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%d')
            except:
                pass
        
        # Try extracting from description
        dates = self.date_pattern.findall(description)
        if dates:
            # Return the last mentioned date as likely resolution date
            return dates[-1]
        
        return None
    
    def infer_category(self, question: str, description: str, category: Optional[str]) -> str:
        """Infer or clean category"""
        if category:
            return category.lower().strip()
        
        # Infer from keywords
        combined = (question + " " + description).lower()
        
        if any(word in combined for word in ['election', 'president', 'senate', 'congress', 'vote', 'candidate', 'political']):
            return 'politics'
        elif any(word in combined for word in ['btc', 'eth', 'crypto', 'bitcoin', 'ethereum', 'defi', 'nft', 'blockchain']):
            return 'crypto'
        elif any(word in combined for word in ['gdp', 'recession', 'inflation', 'rate', 'fed', 'economy', 'unemployment']):
            return 'economics'
        elif any(word in combined for word in ['nba', 'nfl', 'mlb', 'uefa', 'world cup', 'championship', 'game', 'match', 'team']):
            return 'sports'
        elif any(word in combined for word in ['stock', 'market', 'nasdaq', 's&p', 'dow', 'earnings', 'ipo']):
            return 'finance'
        elif any(word in combined for word in ['ai', 'chatgpt', 'technology', 'tech', 'software', 'openai', 'google', 'meta']):
            return 'technology'
        elif any(word in combined for word in ['weather', 'climate', 'temperature', 'hurricane', 'earthquake']):
            return 'weather'
        elif any(word in combined for word in ['movie', 'oscar', 'emmy', 'grammy', 'box office', 'film']):
            return 'entertainment'
        
        return 'other'
    
    def minimize_boilerplate(self, description: str) -> str:
        """Remove or minimize boilerplate text"""
        minimized = description
        
        # Remove common boilerplate phrases
        for phrase in self.boilerplate_phrases:
            minimized = minimized.replace(phrase, '')
        
        # Remove resolution source details (usually at the end)
        if 'resolution source' in minimized.lower():
            parts = re.split(r'The (?:primary )?resolution source', minimized, flags=re.IGNORECASE)
            minimized = parts[0]
        
        return minimized.strip()
    
    def create_searchable_text(self, market: Dict[str, Any]) -> str:
        """Create rich searchable text representation"""
        question = market.get('question', '')
        description = market.get('description', '')
        category = market.get('category', '')
        
        # Clean and expand
        question_clean = self.clean_text(question)
        description_clean = self.minimize_boilerplate(self.clean_text(description))
        
        # Expand abbreviations
        question_expanded = self.expand_abbreviations(question_clean)
        description_expanded = self.expand_abbreviations(description_clean)
        
        # Combine with category
        searchable = f"{question_expanded}. {description_expanded}"
        if category:
            searchable = f"[{category}] {searchable}"
        
        return searchable
    
    def normalize_market(self, market: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a single market"""
        question = market.get('question', '')
        description = market.get('description', '')
        category = market.get('category')
        end_date_iso = market.get('end_date_iso')
        
        # Create normalized representation
        normalized = {
            # Original identifiers
            'question': question,
            'market_slug': market.get('market_slug'),
            'condition_id': market.get('condition_id'),
            'question_id': market.get('question_id'),
            
            # Normalized text
            'question_normalized': self.clean_text(question),
            'description_normalized': self.minimize_boilerplate(self.clean_text(description)),
            
            # Rich searchable text (with abbreviation expansion)
            'searchable_text': self.create_searchable_text(market),
            
            # Extracted entities
            'entities': self.extract_entities(question + " " + description),
            
            # Category
            'category': self.infer_category(question, description, category),
            
            # Dates
            'end_date': self.parse_end_date(end_date_iso, description),
            'end_date_iso': end_date_iso,
            'game_start_time': market.get('game_start_time'),
            
            # Market metadata
            'active': market.get('active', False),
            'closed': market.get('closed', False),
            'archived': market.get('archived', False),
            'accepting_orders': market.get('accepting_orders', False),
            
            # Additional fields for ranking
            'icon': market.get('icon'),
            'tokens': market.get('tokens', []),
            'rewards': market.get('rewards'),
            
            # Market activity indicators (for future enhancement)
            'has_liquidity_data': market.get('tokens') is not None and len(market.get('tokens', [])) > 0,
        }
        
        return normalized
    
    def normalize_markets_file(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """Normalize all markets from input file and save to output file"""
        print(f"Loading markets from {input_path}...")
        
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        markets = data.get('markets', [])
        total = len(markets)
        
        print(f"Processing {total} markets...")
        
        normalized_markets = []
        failed_count = 0
        
        for i, market in enumerate(markets):
            try:
                normalized = self.normalize_market(market)
                normalized_markets.append(normalized)
                
                # Progress update
                if (i + 1) % 1000 == 0:
                    print(f"Processed {i + 1}/{total} markets...")
            except Exception as e:
                print(f"Error processing market {i}: {e}")
                failed_count += 1
        
        # Create output structure
        output_data = {
            'timestamp': data.get('timestamp'),
            'normalized_at': datetime.now().isoformat(),
            'only_open_markets': data.get('only_open_markets'),
            'total_markets': len(normalized_markets),
            'failed_count': failed_count,
            'markets': normalized_markets
        }
        
        print(f"Saving normalized markets to {output_path}...")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Successfully normalized {len(normalized_markets)} markets")
        print(f"✓ Failed: {failed_count}")
        print(f"✓ Output saved to {output_path}")
        
        return output_data


def main():
    """Main execution"""
    # Set up paths
    base_dir = Path(__file__).parent.parent
    input_file = base_dir / 'data' / 'current_markets.json'
    output_file = base_dir / 'data' / 'normalized_markets.json'
    
    # Create normalizer
    normalizer = MarketNormalizer()
    
    # Process markets
    result = normalizer.normalize_markets_file(str(input_file), str(output_file))
    
    # Print statistics
    print("\n=== Normalization Statistics ===")
    print(f"Total markets: {result['total_markets']}")
    
    # Category distribution
    categories = {}
    for market in result['markets']:
        cat = market['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nCategory distribution:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")
    
    # Entity statistics
    total_with_tickers = sum(1 for m in result['markets'] if m['entities']['tickers'])
    total_with_dates = sum(1 for m in result['markets'] if m['entities']['dates'])
    total_with_prices = sum(1 for m in result['markets'] if m['entities']['prices'])
    
    print(f"\nMarkets with extracted entities:")
    print(f"  With tickers: {total_with_tickers}")
    print(f"  With dates: {total_with_dates}")
    print(f"  With prices/numbers: {total_with_prices}")


if __name__ == '__main__':
    main()

