"""
Populate entities table from trends data
"""
from datetime import date
from collections import Counter


def extract_and_save_entities(supabase, google_df, twitter_df):
    """Extract entities and save to entities table"""
    try:
        today = date.today().isoformat()
        
        entities_to_save = []
        
        # Process all trends
        combined = pd.concat([google_df, twitter_df])
        
        # Group by keyword to find cross-platform entities
        for keyword, group in combined.groupby('keyword'):
            regions = group['region'].unique().tolist()
            categories = group['category'].unique().tolist()
            
            # Determine entity type (simple heuristic)
            entity_type = 'keyword'
            if len(keyword.split()) <= 2 and keyword[0].isupper():
                entity_type = 'person'
            elif '#' in keyword:
                entity_type = 'hashtag'
            elif any(word in keyword.lower() for word in ['election', 'government', 'minister']):
                entity_type = 'political'
            elif any(word in keyword.lower() for word in ['company', 'stock', 'market']):
                entity_type = 'business'
            
            # Calculate mentions
            total_mentions = 0
            for _, row in group.iterrows():
                if 'search_volume' in row:
                    total_mentions += row['search_volume']
                elif 'mention_volume' in row:
                    total_mentions += row['mention_volume']
            
            # Get sentiment
            sentiments = []
            if 'public_sentiment' in group.columns:
                sentiments.extend(group['public_sentiment'].dropna().tolist())
            if 'primary_sentiment' in group.columns:
                sentiments.extend(group['primary_sentiment'].dropna().tolist())
            
            dominant_sentiment = Counter(sentiments).most_common(1)[0][0] if sentiments else 'curious'
            
            # Context
            contexts = group['context'].dropna().tolist() if 'context' in group.columns else []
            context = contexts[0] if contexts else ''
            
            entities_to_save.append({
                'analysis_date': today,
                'entity_type': entity_type,
                'entity_name': keyword,
                'keywords': [keyword],
                'total_mentions': str(total_mentions),
                'regions': regions,
                'context': context,
                'sentiment': dominant_sentiment,
                'role': categories[0] if categories else 'unknown'
            })
        
        if entities_to_save:
            # Delete old entities for today
            supabase.table('entities').delete().eq('analysis_date', today).execute()
            
            # Insert new
            supabase.table('entities').insert(entities_to_save).execute()
            
            return True, f"✅ Saved {len(entities_to_save)} entities"
        else:
            return False, "❌ No entities to save"
        
    except Exception as e:
        return False, f"❌ Error: {str(e)}"