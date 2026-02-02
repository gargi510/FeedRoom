"""
Utility functions used across the application
"""
import pandas as pd
import json
import re
import streamlit as st

# ========================================================================
# DATA VALIDATION FUNCTIONS
# ========================================================================

def normalize_volume(volume_str):
    """Convert volume string to number"""
    if pd.isna(volume_str) or volume_str == "":
        return 0
    
    volume_str = str(volume_str).strip().upper()
    volume_str = re.sub(r'[^\d.KMB]', '', volume_str)
    
    if not volume_str:
        return 0
    
    try:
        if 'K' in volume_str:
            return int(float(volume_str.replace('K', '')) * 1000)
        elif 'M' in volume_str:
            return int(float(volume_str.replace('M', '')) * 1_000_000)
        elif 'B' in volume_str:
            return int(float(volume_str.replace('B', '')) * 1_000_000_000)
        else:
            return int(float(volume_str))
    except:
        return 0

def validate_trend_schema(trend, platform='google'):
    """Validate and normalize a single trend"""
    required = {
        'google': ['region', 'rank', 'keyword', 'search_volume', 'category', 'velocity'],
        'twitter': ['region', 'rank', 'keyword', 'mention_volume', 'category', 'velocity']
    }
    
    errors = []
    normalized = trend.copy()
    
    # Check required fields
    for field in required[platform]:
        if field not in trend or trend[field] is None or str(trend[field]).strip() == '':
            errors.append(f"Missing or empty: {field}")
    
    if errors:
        return False, errors, None
    
    # Validate region
    if trend['region'] not in ['USA', 'India']:
        errors.append(f"Invalid region: {trend['region']}")
    
    # Validate rank
    try:
        normalized['rank'] = int(trend['rank'])
    except:
        errors.append(f"Invalid rank: {trend.get('rank')}")
    
    # Normalize keyword
    normalized['keyword'] = str(trend['keyword']).strip()
    
    # Platform-specific normalization
    if platform == 'google':
        normalized['search_volume'] = normalize_volume(trend.get('search_volume', 0))
        normalized['public_sentiment'] = str(trend.get('public_sentiment', 'curious')).lower()
        normalized['sentiment_score'] = int(trend.get('sentiment_score', 50))
        normalized['trend_type'] = str(trend.get('trend_type', 'search'))
        
        # Handle related searches
        related = trend.get('related_searches', [])
        if isinstance(related, str):
            normalized['related_searches'] = [s.strip() for s in related.split(',') if s.strip()]
        elif isinstance(related, list):
            normalized['related_searches'] = related
        else:
            normalized['related_searches'] = []
            
    else:  # twitter
        normalized['mention_volume'] = normalize_volume(trend.get('mention_volume', 0))
        
        # Sentiment mapping
        sentiment_map = {
            'positive': 'excited',
            'negative': 'concerned',
            'neutral': 'curious',
            'mixed': 'controversial'
        }
        primary_sent = str(trend.get('primary_sentiment', 'curious')).lower()
        normalized['primary_sentiment'] = sentiment_map.get(primary_sent, primary_sent)
        
        normalized['sentiment_intensity'] = str(trend.get('sentiment_intensity', 'moderate')).lower()
        normalized['hashtag_type'] = str(trend.get('hashtag_type', 'keyword'))
        
        # Sentiment breakdown
        breakdown = trend.get('sentiment_breakdown', {})
        if not breakdown or not isinstance(breakdown, dict):
            # Generate default breakdown
            if normalized['primary_sentiment'] == 'excited':
                breakdown = {'excited': 70, 'curious': 20, 'celebrating': 10}
            elif normalized['primary_sentiment'] == 'concerned':
                breakdown = {'concerned': 70, 'curious': 20, 'controversial': 10}
            elif normalized['primary_sentiment'] == 'celebrating':
                breakdown = {'celebrating': 70, 'excited': 20, 'curious': 10}
            elif normalized['primary_sentiment'] == 'controversial':
                breakdown = {'controversial': 60, 'concerned': 20, 'curious': 20}
            else:
                breakdown = {'curious': 60, 'excited': 20, 'concerned': 20}
        
        normalized['sentiment_excited'] = int(breakdown.get('excited', 0))
        normalized['sentiment_concerned'] = int(breakdown.get('concerned', 0))
        normalized['sentiment_curious'] = int(breakdown.get('curious', 0))
        normalized['sentiment_celebrating'] = int(breakdown.get('celebrating', 0))
        normalized['sentiment_controversial'] = int(breakdown.get('controversial', 0))
        
        # Aggregate for DB
        normalized['sentiment_positive'] = normalized['sentiment_excited'] + normalized['sentiment_celebrating']
        normalized['sentiment_neutral'] = normalized['sentiment_curious']
        normalized['sentiment_negative'] = normalized['sentiment_concerned'] + normalized['sentiment_controversial']
        
        # Handle related hashtags
        related = trend.get('related_hashtags', [])
        if isinstance(related, str):
            normalized['related_hashtags'] = [s.strip() for s in related.split(',') if s.strip()]
        elif isinstance(related, list):
            normalized['related_hashtags'] = related
        else:
            normalized['related_hashtags'] = []
    
    # Common fields
    normalized['velocity'] = str(trend.get('velocity', 'steady')).lower().replace(' ', '_').replace('-', '_')
    normalized['category'] = str(trend.get('category', 'Unknown'))
    normalized['context'] = str(trend.get('context', ''))
    normalized['why_trending'] = str(trend.get('why_trending', ''))
    
    return len(errors) == 0, errors, normalized

def validate_and_normalize_trends(trends, platform='google'):
    """Validate and normalize a list of trends"""
    valid = []
    report = {'total': len(trends), 'valid': 0, 'invalid': 0, 'errors': []}
    
    for idx, trend in enumerate(trends):
        try:
            is_valid, errors, normalized = validate_trend_schema(trend, platform)
            
            if is_valid and normalized:
                valid.append(normalized)
                report['valid'] += 1
            else:
                report['invalid'] += 1
                report['errors'].append({
                    'index': idx,
                    'keyword': trend.get('keyword', 'Unknown'),
                    'errors': errors
                })
        except Exception as e:
            report['invalid'] += 1
            report['errors'].append({
                'index': idx,
                'keyword': trend.get('keyword', 'Unknown'),
                'errors': [f"Validation error: {str(e)}"]
            })
    
    return valid, report

# ========================================================================
# JSON PARSING
# ========================================================================

def parse_json_input(text):
    """Parse JSON from AI responses - handles markdown blocks and extra text"""
    if not text:
        return None
    
    try:
        # Clean markdown blocks
        clean_text = text.strip()
        
        # Remove markdown code blocks
        if '```json' in clean_text:
            clean_text = clean_text.split('```json')[1].split('```')[0]
        elif '```' in clean_text:
            clean_text = clean_text.split('```')[1].split('```')[0]
        
        # Remove any leading/trailing text
        clean_text = clean_text.strip()
        
        # Find first { and last }
        start_idx = clean_text.find('{')
        end_idx = clean_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            clean_text = clean_text[start_idx:end_idx+1]
        
        return json.loads(clean_text)
        
    except Exception as e:
        print(f"JSON parse error: {str(e)}")
        return None
# ========================================================================
# UI HELPERS
# ========================================================================

def create_modern_metric_card(value, label, icon="📊", color="#667eea"):
    """Create a modern metric card"""
    return f"""
    <div style="background: linear-gradient(135deg, {color} 0%, {color}dd 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        <div style="font-size: 2rem;">{icon}</div>
        <div style="font-size: 2.5rem; font-weight: 700; margin: 0.5rem 0;">{value}</div>
        <div style="font-size: 0.9rem; opacity: 0.9;">{label}</div>
    </div>
    """

# ========================================================================
# DATABASE OPERATIONS
# ========================================================================

def push_to_supabase(supabase, google_trends, twitter_trends):
    """Push validated data to Supabase"""
    if not supabase:
        return False, "Supabase not configured"
    
    try:
        from datetime import datetime, timezone
        
        collection_date = datetime.now().date().isoformat()
        collection_timestamp = datetime.now(timezone.utc).isoformat()
        
        # Prepare Google Trends
        google_records = []
        for trend in google_trends:
            record = {
                'collection_date': collection_date,
                'collection_timestamp': collection_timestamp,
                'region': trend['region'],
                'rank': trend['rank'],
                'keyword': trend['keyword'],
                'search_volume': trend['search_volume'],
                'category': trend['category'],
                'velocity': trend['velocity'],
                'trend_type': trend.get('trend_type', 'search'),
                'context': trend.get('context', ''),
                'why_trending': trend.get('why_trending', ''),
                'related_searches': trend.get('related_searches', [])
            }
            google_records.append(record)
        
        # Prepare Twitter Trends
        twitter_records = []
        for trend in twitter_trends:
            record = {
                'collection_date': collection_date,
                'collection_timestamp': collection_timestamp,
                'region': trend['region'],
                'rank': trend['rank'],
                'keyword': trend['keyword'],
                'mention_volume': trend['mention_volume'],
                'hashtag_type': trend.get('hashtag_type', 'keyword'),
                'category': trend['category'],
                'velocity': trend['velocity'],
                'sentiment': trend.get('primary_sentiment', 'curious'),
                'sentiment_positive': trend.get('sentiment_positive', 0),
                'sentiment_neutral': trend.get('sentiment_neutral', 0),
                'sentiment_negative': trend.get('sentiment_negative', 0),
                'context': trend.get('context', ''),
                'why_trending': trend.get('why_trending', ''),
                'related_hashtags': trend.get('related_hashtags', []),
                'top_entities': trend.get('top_entities', [])
            }
            twitter_records.append(record)
        
        # Push to Supabase
        if google_records:
            supabase.table('google_trends').insert(google_records).execute()
        if twitter_records:
            supabase.table('twitter_trends').insert(twitter_records).execute()
        
        return True, f"✅ Saved {len(google_records)} Google + {len(twitter_records)} Twitter trends"
    
    except Exception as e:
        return False, f"Database error: {str(e)}"