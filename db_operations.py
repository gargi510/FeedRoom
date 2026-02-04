"""
Database operations - PRODUCTION FIXED VERSION
FIXES:
1. YouTube metadata now extracted to individual fields in daily_content_records
2. Added entities extraction helper function
3. Added executive summary to daily_insights
"""
from datetime import datetime, timezone, date, timedelta
import json
from collections import Counter


# ========================================================================
# DAILY CONTENT RECORDS OPERATIONS
# ========================================================================

def save_regional_script_to_db(supabase, region, script_data, publish_date=None):
    """
    Save a single region's script and metadata to daily content records
    FIXED: Now extracts YouTube metadata to individual fields
    
    Args:
        supabase: Supabase client
        region: 'USA' or 'India'
        script_data: Dict with script, assembly, intelligence, etc.
        publish_date: Optional date string
    
    Returns:
        (success: bool, message: str, record_id: int)
    """
    try:
        if not publish_date:
            publish_date = date.today().isoformat()
        
        timestamp = datetime.now(timezone.utc).isoformat()
        region_lower = region.lower()
        
        assembly = script_data.get('assembly', {})
        youtube_metadata = assembly.get('youtube_metadata', {})
        
        # ✅ FIXED: Extract YouTube metadata to individual fields
        record = {
            'publish_date': publish_date,
            f'script_{region_lower}': script_data.get('script_full', ''),
            f'intelligence_grid_{region_lower}': script_data.get('intelligence', {}),
            f'script_assembly_{region_lower}': assembly.get('script_assembly', {}),
            f'visual_prompts_{region_lower}': assembly.get('visual_prompts', {}),
            f'youtube_metadata_{region_lower}': youtube_metadata,
            
            # ✅ NEW: Individual YouTube fields for easier querying
            f'youtube_title_{region_lower}': youtube_metadata.get('title', ''),
            f'youtube_description_{region_lower}': youtube_metadata.get('description', ''),
            f'youtube_hook_{region_lower}': youtube_metadata.get('hook', ''),
            f'youtube_hashtags_{region_lower}': youtube_metadata.get('hashtags', []),
            f'thumbnail_prompt_{region_lower}': youtube_metadata.get('thumbnail_prompt', '')
        }
        
        existing = supabase.table('daily_content_records')\
            .select('id')\
            .eq('publish_date', publish_date)\
            .execute()
        
        if existing.data and len(existing.data) > 0:
            record_id = existing.data[0]['id']
            result = supabase.table('daily_content_records')\
                .update(record)\
                .eq('id', record_id)\
                .execute()
            
            if result.data:
                return True, f"✅ {region} script saved for {publish_date}", record_id
            else:
                return False, f"❌ Failed to save {region} script", None
        else:
            result = supabase.table('daily_content_records')\
                .insert(record)\
                .execute()
            
            if result.data and len(result.data) > 0:
                record_id = result.data[0]['id']
                return True, f"✅ {region} script saved for {publish_date}", record_id
            else:
                return False, f"❌ Failed to create record for {region}", None
                
    except Exception as e:
        return False, f"❌ Database error: {str(e)}", None


def save_daily_content_to_db(supabase, content_data, publish_date=None):
    """
    Save or update daily content record to Supabase
    
    Args:
        supabase: Supabase client
        content_data: Dict with all daily content information
        publish_date: Optional date string (YYYY-MM-DD), defaults to today
    
    Returns:
        (success: bool, message: str, record_id: int)
    """
    try:
        if not publish_date:
            publish_date = date.today().isoformat()
        
        timestamp = datetime.now(timezone.utc).isoformat()
        
        def safe_get(data, key, default=''):
            val = data.get(key, default)
            return val if val is not None else default
        
        def safe_json(data, key, default=None):
            """Safely get JSON field, return None for empty to avoid JSONB errors"""
            val = data.get(key, default)
            # Supabase JSONB accepts NULL but rejects empty JSON objects {}
            if val is None:
                return None
            if isinstance(val, dict) and len(val) == 0:
                return None
            if isinstance(val, list) and len(val) == 0:
                return None
            return val
        
        record = {
            'publish_date': publish_date,
            'created_at': timestamp,
            'script_usa': safe_get(content_data, 'script_usa'),
            'script_india': safe_get(content_data, 'script_india'),
            'intelligence_grid_usa': safe_json(content_data, 'intelligence_grid_usa'),
            'intelligence_grid_india': safe_json(content_data, 'intelligence_grid_india'),
            'script_assembly_usa': safe_json(content_data, 'script_assembly_usa'),
            'script_assembly_india': safe_json(content_data, 'script_assembly_india'),
            'visual_prompts_usa': safe_json(content_data, 'visual_prompts_usa'),
            'visual_prompts_india': safe_json(content_data, 'visual_prompts_india'),
            'youtube_metadata_usa': safe_json(content_data, 'youtube_metadata_usa'),
            'youtube_metadata_india': safe_json(content_data, 'youtube_metadata_india'),
            'executive_summary': safe_get(content_data, 'executive_summary'),
            'anomalies_detected': safe_json(content_data, 'anomalies_detected'),
            'entities': safe_json(content_data, 'entities'),
            'production_status': safe_get(content_data, 'production_status', 'draft'),
            'completed_at': content_data.get('completed_at')
        }
        
        existing = supabase.table('daily_content_records')\
            .select('id')\
            .eq('publish_date', publish_date)\
            .execute()
        
        if existing.data and len(existing.data) > 0:
            record_id = existing.data[0]['id']
            result = supabase.table('daily_content_records')\
                .update(record)\
                .eq('id', record_id)\
                .execute()
            
            if result.data:
                return True, f"✅ Daily content updated for {publish_date}", record_id
            else:
                return False, "❌ Failed to update daily content", None
        else:
            result = supabase.table('daily_content_records')\
                .insert(record)\
                .execute()
            
            if result.data and len(result.data) > 0:
                record_id = result.data[0]['id']
                return True, f"✅ Daily content saved for {publish_date}", record_id
            else:
                return False, "❌ Failed to save daily content", None
                
    except Exception as e:
        return False, f"❌ Database error: {str(e)}", None


def get_daily_content_by_date(supabase, publish_date=None):
    """Retrieve daily content record for a specific date"""
    try:
        if not publish_date:
            publish_date = date.today().isoformat()
        
        result = supabase.table('daily_content_records')\
            .select('*')\
            .eq('publish_date', publish_date)\
            .execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        else:
            return None
            
    except Exception as e:
        print(f"Error fetching daily content: {str(e)}")
        return None


def update_production_status(supabase, publish_date, status, completed=False):
    """Update production status for a daily content record"""
    try:
        update_data = {'production_status': status}
        
        if completed:
            update_data['completed_at'] = datetime.now(timezone.utc).isoformat()
        
        result = supabase.table('daily_content_records')\
            .update(update_data)\
            .eq('publish_date', publish_date)\
            .execute()
        
        if result.data:
            return True, f"✅ Status updated to '{status}'"
        else:
            return False, "❌ Failed to update status"
            
    except Exception as e:
        return False, f"❌ Error: {str(e)}"


# ========================================================================
# DAILY INSIGHTS OPERATIONS
# ========================================================================

def save_daily_insights_to_db(supabase, insights_data, analysis_date=None):
    """
    Save daily insights - Creates 2 rows: one for India, one for USA
    FIXED: Now includes executive_summary
    """
    try:
        if not analysis_date:
            analysis_date = date.today().isoformat()
        
        india_intel = insights_data.get('india_intelligence', {})
        usa_intel = insights_data.get('usa_intelligence', {})
        executive_summary = insights_data.get('executive_summary', '')
        
        def safe_get(data, key, default=''):
            val = data.get(key, default)
            return val if val is not None else default
        
        def create_regional_record(region, intelligence):
            themes = intelligence.get('weather_grid', [])
            anomalies = intelligence.get('anomalies', [])
            prod_mood = intelligence.get('production_mood', {})
            
            theme_1 = themes[0] if len(themes) > 0 else {}
            theme_2 = themes[1] if len(themes) > 1 else {}
            anomaly_1 = anomalies[0] if len(anomalies) > 0 else {}
            anomaly_2 = anomalies[1] if len(anomalies) > 1 else {}
            
            return {
                'analysis_date': analysis_date,
                'region': region,
                'excecutive_summary': executive_summary,  # Note: typo in DB schema
                'theme_1_title': safe_get(theme_1, 'theme'),
                'theme_1_category': safe_get(theme_1, 'category'),
                'theme_1_keywords': theme_1.get('keywords', []),
                'theme_1_mood': safe_get(theme_1, 'mood'),
                'theme_1_data_signal': safe_get(theme_1, 'data_signal'),
                'theme_1_context': safe_get(theme_1, 'context'),
                'theme_1_deep_why': safe_get(theme_1, 'deep_why'),
                'theme_1_big_question': safe_get(theme_1, 'big_question'),
                'theme_2_title': safe_get(theme_2, 'theme'),
                'theme_2_category': safe_get(theme_2, 'category'),
                'theme_2_keywords': theme_2.get('keywords', []),
                'theme_2_mood': safe_get(theme_2, 'mood'),
                'theme_2_data_signal': safe_get(theme_2, 'data_signal'),
                'theme_2_context': safe_get(theme_2, 'context'),
                'theme_2_deep_why': safe_get(theme_2, 'deep_why'),
                'theme_2_big_question': safe_get(theme_2, 'big_question'),
                'anomaly_1_keyword': safe_get(anomaly_1, 'keyword'),
                'anomaly_1_velocity': safe_get(anomaly_1, 'velocity'),
                'anomaly_1_explanation': safe_get(anomaly_1, 'explanation'),
                'anomaly_1_big_question': safe_get(anomaly_1, 'big_question'),
                'anomaly_2_keyword': safe_get(anomaly_2, 'keyword'),
                'anomaly_2_velocity': safe_get(anomaly_2, 'velocity'),
                'anomaly_2_explanation': safe_get(anomaly_2, 'explanation'),
                'anomaly_2_big_question': safe_get(anomaly_2, 'big_question'),
                'overall_sentiment': prod_mood.get('overall_sentiment', 0),
                'vibe_color_hex': safe_get(prod_mood, 'vibe_color_hex'),
                'vocal_tone': safe_get(prod_mood, 'vocal_tone'),
                'visual_background_prompt': safe_get(prod_mood, 'visual_background_prompt')
            }
        
        india_record = create_regional_record('India', india_intel)
        usa_record = create_regional_record('USA', usa_intel)
        
        for region, record in [('India', india_record), ('USA', usa_record)]:
            existing = supabase.table('daily_insights')\
                .select('id')\
                .eq('analysis_date', analysis_date)\
                .eq('region', region)\
                .execute()
            
            if existing.data and len(existing.data) > 0:
                record_id = existing.data[0]['id']
                supabase.table('daily_insights')\
                    .update(record)\
                    .eq('id', record_id)\
                    .execute()
            else:
                supabase.table('daily_insights')\
                    .insert(record)\
                    .execute()
        
        return True, f"✅ Daily insights saved for India + USA on {analysis_date}", None
        
    except Exception as e:
        return False, f"❌ Database error: {str(e)}", None


def get_daily_insights_by_date(supabase, analysis_date=None):
    """Retrieve daily insights for a specific date"""
    try:
        if not analysis_date:
            analysis_date = date.today().isoformat()
        
        result = supabase.table('daily_insights')\
            .select('*')\
            .eq('analysis_date', analysis_date)\
            .execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        else:
            return None
            
    except Exception as e:
        print(f"Error fetching daily insights: {str(e)}")
        return None


def get_recent_insights(supabase, limit=7):
    """Get recent daily insights (last N days)"""
    try:
        result = supabase.table('daily_insights')\
            .select('*')\
            .order('analysis_date', desc=True)\
            .limit(limit)\
            .execute()
        
        if result.data:
            return result.data
        else:
            return []
            
    except Exception as e:
        print(f"Error fetching recent insights: {str(e)}")
        return []


# ========================================================================
# ENTITIES OPERATIONS
# ========================================================================

def save_entities_to_db(supabase, entities_list, analysis_date=None):
    """Save detected entities to the entities table"""
    try:
        if not analysis_date:
            analysis_date = date.today().isoformat()
        
        timestamp = datetime.now(timezone.utc).isoformat()
        
        records = []
        for entity in entities_list:
            record = {
                'analysis_date': analysis_date,
                'created_at': timestamp,
                'entity_type': entity.get('type', entity.get('entity_type', 'unknown')),
                'entity_name': entity.get('name', entity.get('entity_name', '')),
                'keywords': entity.get('keywords', []),
                'total_mentions': str(entity.get('mentions', entity.get('total_mentions', 0))),
                'regions': entity.get('regions', []),
                'context': entity.get('context', ''),
                'sentiment': entity.get('sentiment', 'neutral'),
                'role': entity.get('role', '')
            }
            records.append(record)
        
        if records:
            result = supabase.table('entities')\
                .insert(records)\
                .execute()
            
            if result.data:
                return True, f"✅ Saved {len(records)} entities", len(records)
            else:
                return False, "❌ Failed to save entities", 0
        else:
            return True, "⚠️ No entities to save", 0
            
    except Exception as e:
        return False, f"❌ Database error: {str(e)}", 0


def extract_and_save_entities_from_trends(supabase, google_trends, twitter_trends):
    """
    ✅ NEW: Extract entities from trends data and save to entities table
    
    Args:
        supabase: Supabase client
        google_trends: List of Google trend dicts
        twitter_trends: List of Twitter trend dicts
    
    Returns:
        (success: bool, message: str, count: int)
    """
    try:
        today = date.today().isoformat()
        
        entities_to_save = []
        all_trends = {}
        
        # Group by keyword
        for trend in google_trends + twitter_trends:
            keyword = trend['keyword']
            if keyword not in all_trends:
                all_trends[keyword] = {
                    'regions': set(),
                    'categories': set(),
                    'mentions': 0,
                    'sentiments': [],
                    'contexts': []
                }
            
            all_trends[keyword]['regions'].add(trend['region'])
            all_trends[keyword]['categories'].add(trend.get('category', 'Unknown'))
            all_trends[keyword]['mentions'] += trend.get('search_volume', trend.get('mention_volume', 0))
            
            if 'public_sentiment' in trend:
                all_trends[keyword]['sentiments'].append(trend['public_sentiment'])
            elif 'primary_sentiment' in trend:
                all_trends[keyword]['sentiments'].append(trend['primary_sentiment'])
            
            if 'context' in trend and trend['context']:
                all_trends[keyword]['contexts'].append(trend['context'])
        
        # Convert to entity records
        for keyword, data in all_trends.items():
            # Determine entity type
            entity_type = 'keyword'
            keyword_lower = keyword.lower()
            
            if len(keyword.split()) <= 2 and keyword[0].isupper():
                entity_type = 'person'
            elif '#' in keyword:
                entity_type = 'hashtag'
            elif any(word in keyword_lower for word in ['election', 'government', 'minister', 'president', 'minister']):
                entity_type = 'political'
            elif any(word in keyword_lower for word in ['company', 'stock', 'market', 'shares', 'ipo']):
                entity_type = 'business'
            elif any(word in keyword_lower for word in ['movie', 'actor', 'actress', 'film', 'show', 'series']):
                entity_type = 'entertainment'
            elif any(word in keyword_lower for word in ['cricket', 'football', 'tennis', 'sports', 'match', 'game']):
                entity_type = 'sports'
            
            # Get dominant sentiment
            sentiments = data['sentiments']
            dominant_sentiment = Counter(sentiments).most_common(1)[0][0] if sentiments else 'curious'
            
            # Get context (first non-empty)
            context = data['contexts'][0] if data['contexts'] else ''
            
            # Get category (most common)
            category = list(data['categories'])[0] if data['categories'] else 'Unknown'
            
            entities_to_save.append({
                'entity_type': entity_type,
                'entity_name': keyword,
                'keywords': [keyword],
                'total_mentions': str(data['mentions']),
                'regions': list(data['regions']),
                'context': context[:500] if context else '',  # Limit context length
                'sentiment': dominant_sentiment,
                'role': category
            })
        
        if entities_to_save:
            return save_entities_to_db(supabase, entities_to_save)
        else:
            return True, "⚠️ No entities to save", 0
        
    except Exception as e:
        return False, f"❌ Error extracting entities: {str(e)}", 0


def get_entities_by_date(supabase, analysis_date=None):
    """Get all entities for a specific date"""
    try:
        if not analysis_date:
            analysis_date = date.today().isoformat()
        
        result = supabase.table('entities')\
            .select('*')\
            .eq('analysis_date', analysis_date)\
            .execute()
        
        if result.data:
            return result.data
        else:
            return []
            
    except Exception as e:
        print(f"Error fetching entities: {str(e)}")
        return []


def get_entity_by_name(supabase, entity_name, days_back=7):
    """Track an entity across multiple days"""
    try:
        from_date = (date.today() - timedelta(days=days_back)).isoformat()
        
        result = supabase.table('entities')\
            .select('*')\
            .eq('entity_name', entity_name)\
            .gte('analysis_date', from_date)\
            .order('analysis_date', desc=True)\
            .execute()
        
        if result.data:
            return result.data
        else:
            return []
            
    except Exception as e:
        print(f"Error fetching entity: {str(e)}")
        return []


# ========================================================================
# COMBINED OPERATIONS
# ========================================================================

def save_complete_daily_analysis(supabase, 
                                  intelligence_india, 
                                  intelligence_usa, 
                                  executive_summary,
                                  entities_list,
                                  publish_date=None):
    """
    Save complete daily analysis: insights + content records + entities
    
    Args:
        supabase: Supabase client
        intelligence_india: India intelligence grid
        intelligence_usa: USA intelligence grid
        executive_summary: Executive summary text
        entities_list: List of detected entities
        publish_date: Date string
    
    Returns:
        Dict with results from all operations
    """
    results = {
        'insights': {'success': False, 'message': '', 'id': None},
        'content': {'success': False, 'message': '', 'id': None},
        'entities': {'success': False, 'message': '', 'count': 0}
    }
    
    # Prepare insights data
    insights_data = {
        'executive_summary': executive_summary,
        'india_intelligence': intelligence_india,
        'usa_intelligence': intelligence_usa,
        'entities': entities_list
    }
    
    # Save insights
    success, message, record_id = save_daily_insights_to_db(
        supabase, insights_data, publish_date
    )
    results['insights'] = {'success': success, 'message': message, 'id': record_id}
    
    # Save initial content record (without scripts yet)
    content_data = {
        'executive_summary': executive_summary,
        'intelligence_grid_india': intelligence_india,
        'intelligence_grid_usa': intelligence_usa,
        'anomalies_detected': {
            'india': intelligence_india.get('anomalies', []),
            'usa': intelligence_usa.get('anomalies', [])
        },
        'entities': entities_list,
        'production_status': 'draft'
    }
    
    success, message, record_id = save_daily_content_to_db(
        supabase, content_data, publish_date
    )
    results['content'] = {'success': success, 'message': message, 'id': record_id}
    
    # Save entities
    success, message, count = save_entities_to_db(
        supabase, entities_list, publish_date
    )
    results['entities'] = {'success': success, 'message': message, 'count': count}
    
    return results


# ========================================================================
# DEEP DIVE RESEARCH OPERATIONS
# ========================================================================

def save_deepdive_to_db(supabase, deepdive_data, status='needs_finetuning'):
    """Save a complete deep dive to Supabase"""
    try:
        timestamp = datetime.now(timezone.utc).isoformat()
        
        def safe_get(data, key, default=''):
            val = data.get(key, default)
            return val if val is not None else default
        
        def safe_json(data, key, default=None):
            """Safely get JSON field, return None for empty to avoid JSONB errors"""
            val = data.get(key, default)
            # Supabase JSONB accepts NULL but rejects empty JSON objects {}
            if val is None:
                return None
            if isinstance(val, dict) and len(val) == 0:
                return None
            if isinstance(val, list) and len(val) == 0:
                return None
            return val
        
        record = {
            'created_at': timestamp,
            'updated_at': timestamp,
            'status': status,
            'finalized_at': timestamp if status == 'finalized' else None,
            'keyword': safe_get(deepdive_data, 'keyword'),
            'region': safe_get(deepdive_data, 'region'),
            'platform': safe_get(deepdive_data, 'platform'),
            'search_volume': deepdive_data.get('search_volume', 0),
            'velocity': safe_get(deepdive_data, 'velocity'),
            'sentiment': safe_get(deepdive_data, 'sentiment'),
            'category': safe_get(deepdive_data, 'category'),
            'research_data': safe_json(deepdive_data, 'research_data'),
            'sources_summary': safe_get(deepdive_data, 'sources_summary'),
            'title': safe_get(deepdive_data, 'title'),
            'subtitle': safe_get(deepdive_data, 'subtitle'),
            'anomaly': safe_get(deepdive_data, 'anomaly'),
            'approved_story': safe_get(deepdive_data, 'approved_story'),
            'script_final': safe_get(deepdive_data, 'script_final'),
            'youtube_title': safe_get(deepdive_data, 'youtube_title'),
            'youtube_description': safe_get(deepdive_data, 'youtube_description'),
            'youtube_hook': safe_get(deepdive_data, 'youtube_hook'),
            'hashtags': deepdive_data.get('hashtags', []),
            'thumbnail_prompt': safe_get(deepdive_data, 'thumbnail_prompt'),
            'image_prompts': safe_json(deepdive_data, 'image_prompts'),
            'moviepy_spec': safe_json(deepdive_data, 'moviepy_spec'),
            'moviepy_spec_file': safe_get(deepdive_data, 'moviepy_spec_file')
        }
        
        result = supabase.table('deep_dive_research').insert(record).execute()
        
        if result.data and len(result.data) > 0:
            record_id = result.data[0]['id']
            return True, f"✅ Deep dive saved successfully (ID: {record_id})", record_id
        else:
            return False, "❌ Failed to save deep dive", None
            
    except Exception as e:
        return False, f"❌ Database error: {str(e)}", None


def get_deepdives_by_status(supabase, status='finalized'):
    """Retrieve all deep dives with a specific status"""
    try:
        result = supabase.table('deep_dive_research')\
            .select('*')\
            .eq('status', status)\
            .order('created_at', desc=True)\
            .execute()
        
        if result.data:
            return result.data
        else:
            return []
            
    except Exception as e:
        print(f"Error fetching deep dives: {str(e)}")
        return []


def get_deepdive_by_id(supabase, deepdive_id):
    """Retrieve a specific deep dive by ID"""
    try:
        result = supabase.table('deep_dive_research')\
            .select('*')\
            .eq('id', deepdive_id)\
            .execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        else:
            return None
            
    except Exception as e:
        print(f"Error fetching deep dive: {str(e)}")
        return None


def update_deepdive_status(supabase, deepdive_id, new_status):
    """Update the status of a deep dive"""
    try:
        timestamp = datetime.now(timezone.utc).isoformat()
        
        update_data = {
            'status': new_status,
            'updated_at': timestamp
        }
        
        if new_status == 'finalized':
            update_data['finalized_at'] = timestamp
        
        result = supabase.table('deep_dive_research')\
            .update(update_data)\
            .eq('id', deepdive_id)\
            .execute()
        
        if result.data:
            return True, f"✅ Status updated to '{new_status}'"
        else:
            return False, "❌ Failed to update status"
            
    except Exception as e:
        return False, f"❌ Error: {str(e)}"