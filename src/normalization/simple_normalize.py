"""
Simple Market Normalization Script

A lightweight, focused normalization that creates clean, compact market representations
optimized for semantic search and human readability.

Key differences from full normalization:
- Smaller output size (focused on essentials)
- Simpler keyword extraction
- Cleaner text without expansion verbosity
- More readable for debugging
"""

import json
import re
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from pathlib import Path


class SimpleMarketNormalizer:
    """Simplified normalizer focusing on essentials for semantic matching"""
    
    def __init__(self):
        # Category keywords (simpler, more direct)
        self.category_keywords = {
            'politics': ['election', 'president', 'senate', 'congress', 'vote', 'trump', 'biden', 
                        'republican', 'democrat', 'governor', 'political', 'politic'],
            'crypto': ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'solana', 'sol', 'usdt',
                      'defi', 'nft', 'blockchain', 'coin', 'token', 'wallet'],
            'economics': ['gdp', 'recession', 'inflation', 'fed', 'federal reserve', 'interest rate',
                         'unemployment', 'economy', 'economic', 'cpi', 'jobs report'],
            'sports': ['nba', 'nfl', 'mlb', 'nhl', 'uefa', 'world cup', 'super bowl', 'championship',
                      'playoffs', 'game', 'match', 'team', 'player', 'sport'],
            'finance': ['stock', 'market', 'nasdaq', 's&p', 'dow', 'earnings', 'ipo', 'revenue',
                       'profit', 'share', 'investor', 'trading'],
            'technology': ['ai', 'chatgpt', 'openai', 'google', 'meta', 'apple', 'amazon', 'microsoft',
                          'tech', 'software', 'app', 'platform'],
            'entertainment': ['movie', 'film', 'oscar', 'emmy', 'grammy', 'box office', 'album',
                             'actor', 'artist', 'tv show', 'netflix'],
        }
    
    def clean_text(self, text: str) -> str:
        """Basic text cleaning - just the essentials"""
        if not text:
            return ""
        
        # Lowercase and remove extra whitespace
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)
        
        # Remove URLs completely
        text = re.sub(r'https?://\S+', '', text)
        
        # Keep only basic characters
        text = re.sub(r'[^\w\s\$%\.\,\-]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords from text"""
        # Remove common stop words
        stop_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for',
            'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by',
            'from', 'they', 'we', 'say', 'her', 'she', 'or', 'an', 'will', 'my', 'one', 'all',
            'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get',
            'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him',
            'know', 'take', 'people', 'into', 'year', 'your', 'some', 'could', 'them', 'see',
            'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think',
            'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well',
            'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most', 'us',
            'is', 'are', 'was', 'were', 'been', 'being', 'has', 'had', 'does', 'did', 'doing'
        }
        
        # Tokenize and filter
        words = text.lower().split()
        keywords = []
        
        for word in words:
            # Clean word
            word = re.sub(r'[^\w]', '', word)
            
            # Skip if too short, is stop word, or is number
            if len(word) < 3 or word in stop_words or word.isdigit():
                continue
            
            keywords.append(word)
        
        # Remove duplicates while preserving order
        seen: Set[str] = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)
        
        # Limit to top 20 keywords
        return unique_keywords[:20]
    
    def categorize(self, question: str, description: str) -> str:
        """Simple category inference based on keyword matching"""
        combined = (question + " " + description).lower()
        
        # Count keyword matches for each category
        scores = {}
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in combined)
            if score > 0:
                scores[category] = score
        
        # Return category with highest score, or 'other'
        if scores:
            return max(scores, key=scores.get)
        return 'other'
    
    def extract_key_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract only the most important entities - lightweight version"""
        entities = {
            'tickers': [],
            'numbers': [],
            'dates': []
        }
        
        # Crypto/stock tickers (simple patterns)
        ticker_pattern = r'\b(?:BTC|ETH|SOL|USDT|USDC|DOGE|ADA|DOT|MATIC|AVAX|LINK|UNI)\b'
        entities['tickers'] = list(set(re.findall(ticker_pattern, text.upper())))
        
        # Important numbers (prices, percentages)
        number_pattern = r'\$\d+[,\d]*(?:\.\d+)?[kKmMbB]?|\d+(?:\.\d+)?%'
        entities['numbers'] = list(set(re.findall(number_pattern, text)))[:5]  # Top 5
        
        # Year mentions (simple)
        year_pattern = r'\b20\d{2}\b'
        entities['dates'] = list(set(re.findall(year_pattern, text)))[:3]  # Top 3
        
        return entities
    
    def extract_simple_date(self, end_date_iso: Optional[str]) -> Optional[str]:
        """Extract simple date format"""
        if not end_date_iso:
            return None
        
        try:
            dt = datetime.fromisoformat(end_date_iso.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d')
        except:
            return None
    
    def create_search_text(self, question: str, description: str, category: str) -> str:
        """Create simple search text - question + key description parts"""
        # Clean both
        q_clean = self.clean_text(question)
        d_clean = self.clean_text(description)
        
        # Take first 200 chars of description (most relevant part)
        d_short = d_clean[:200] if len(d_clean) > 200 else d_clean
        
        # Combine with category tag
        return f"[{category}] {q_clean} {d_short}"
    
    def generate_id_from_question(self, question: str) -> str:
        """Generate a stable ID from question text"""
        # Create a hash of the question for a stable identifier
        return hashlib.md5(question.encode('utf-8')).hexdigest()[:16]
    
    def create_slug_from_question(self, question: str) -> str:
        """Create a URL-friendly slug from question"""
        # Lowercase and remove special characters
        slug = question.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        # Limit length
        slug = slug[:60]
        return slug.strip('-')
    
    def normalize_market(self, market: Dict[str, Any]) -> Dict[str, Any]:
        """Create simple normalized market record"""
        question = market.get('question', '')
        description = market.get('description', '')
        
        # Basic fields
        category = self.categorize(question, description)
        keywords = self.extract_keywords(question + " " + description)
        entities = self.extract_key_entities(question + " " + description)
        
        # Extract identifiers - try multiple fields
        condition_id = market.get('condition_id')
        question_id = market.get('question_id')
        market_slug = market.get('market_slug')
        
        # Generate fallback identifiers if API didn't provide them
        if not condition_id and not question_id and not market_slug:
            # Use question hash as stable ID
            market_id = self.generate_id_from_question(question)
            if not market_slug:
                market_slug = self.create_slug_from_question(question)
        else:
            # Use first non-null identifier
            market_id = condition_id or question_id or market_slug
        
        return {
            # Core identifiers
            'id': market_id,
            'condition_id': condition_id,
            'question_id': question_id,
            'question': question,
            'slug': market_slug,
            
            # Search optimized
            'search_text': self.create_search_text(question, description, category),
            'keywords': keywords,
            'category': category,
            
            # Entities
            'tickers': entities['tickers'],
            'numbers': entities['numbers'],
            'years': entities['dates'],
            
            # Metadata
            'end_date': self.extract_simple_date(market.get('end_date_iso')),
            'active': market.get('active', False),
            'closed': market.get('closed', False),
            
            # Optional
            'icon': market.get('icon'),
        }
    
    def normalize_markets_file(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """Normalize all markets - simple version"""
        print(f"Loading markets from {input_path}...")
        
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        markets = data.get('markets', [])
        total = len(markets)
        
        print(f"Processing {total} markets (simple normalization)...")
        
        normalized_markets = []
        failed_count = 0
        seen_ids = {}  # Track IDs and add index for duplicates
        
        for i, market in enumerate(markets):
            try:
                normalized = self.normalize_market(market)
                
                # Handle duplicate IDs by adding an index
                original_id = normalized['id']
                if original_id in seen_ids:
                    seen_ids[original_id] += 1
                    # Append index to make unique
                    normalized['id'] = f"{original_id}_{seen_ids[original_id]}"
                else:
                    seen_ids[original_id] = 0
                
                normalized_markets.append(normalized)
                
                # Progress update
                if (i + 1) % 1000 == 0:
                    print(f"Processed {i + 1}/{total} markets...")
            except Exception as e:
                print(f"Error processing market {i}: {e}")
                failed_count += 1
        
        # Create compact output
        output_data = {
            'timestamp': data.get('timestamp'),
            'normalized_at': datetime.now().isoformat(),
            'normalization_type': 'simple',
            'total_markets': len(normalized_markets),
            'failed_count': failed_count,
            'markets': normalized_markets
        }
        
        print(f"Saving normalized markets to {output_path}...")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        # Calculate file sizes
        import os
        output_size_mb = os.path.getsize(output_path) / (1024 * 1024)
        
        print(f"\n✓ Successfully normalized {len(normalized_markets)} markets")
        print(f"✓ Failed: {failed_count}")
        print(f"✓ Output size: {output_size_mb:.1f} MB")
        print(f"✓ Output saved to {output_path}")
        
        return output_data


def main():
    """Main execution"""
    # Set up paths
    base_dir = Path(__file__).parent.parent
    input_file = base_dir / 'data' / 'current_markets.json'
    output_file = base_dir / 'data' / 'simple_normalized_markets.json'
    
    # Create normalizer
    normalizer = SimpleMarketNormalizer()
    
    # Process markets
    result = normalizer.normalize_markets_file(str(input_file), str(output_file))
    
    # Print statistics
    print("\n=== Simple Normalization Statistics ===")
    print(f"Total markets: {result['total_markets']}")
    
    # Category distribution
    categories = {}
    for market in result['markets']:
        cat = market['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nCategory distribution:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")
    
    # Keyword stats
    total_keywords = sum(len(m['keywords']) for m in result['markets'])
    avg_keywords = total_keywords / len(result['markets']) if result['markets'] else 0
    
    print(f"\nKeyword statistics:")
    print(f"  Average keywords per market: {avg_keywords:.1f}")
    
    # Entity stats
    with_tickers = sum(1 for m in result['markets'] if m['tickers'])
    with_numbers = sum(1 for m in result['markets'] if m['numbers'])
    with_years = sum(1 for m in result['markets'] if m['years'])
    
    print(f"\nEntity extraction:")
    print(f"  Markets with tickers: {with_tickers}")
    print(f"  Markets with numbers: {with_numbers}")
    print(f"  Markets with years: {with_years}")
    
    # Sample output
    print("\n=== Sample Normalized Market ===")
    if result['markets']:
        sample = result['markets'][0]
        print(json.dumps(sample, indent=2))


if __name__ == '__main__':
    main()

