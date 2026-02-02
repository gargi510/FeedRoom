"""
Database operations for Deep Dive Research
FIXED VERSION: Better error handling for JSON fields
"""
from datetime import datetime, timezone
import json


def save_deepdive_to_db(supabase, deepdive_data, status='needs_finetuning'):
    """
    Save a complete deep dive to Supabase
    
    Args:
        supabase: Supabase client
        deepdive_data: Dict with all deep dive information
        status: 'needs_finetuning' or 'finalized'
    
    Returns:
        (success: bool, message: str, record_id: str)
    """
    try:
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Helper function to safely get values
        def safe_get(data, key, default=''):
            """Safely get value from dict, handle None/missing"""
            val = data.get(key, default)
            return val if val is not None else default
        
        # Helper function for JSON fields
        def safe_json(data, key, default=None):
            """Safely get JSON field, ensure proper type"""
            val = data.get(key, default if default is not None else {})
            # Ensure it's a dict or list, not None
            if val is None:
                return default if default is not None else {}
            return val
        
        record = {
            'created_at': timestamp,
            'updated_at': timestamp,
            'status': status,
            'finalized_at': timestamp if status == 'finalized' else None,
            
            # Keyword Info
            'keyword': safe_get(deepdive_data, 'keyword'),
            'region': safe_get(deepdive_data, 'region'),
            'platform': safe_get(deepdive_data, 'platform'),
            'search_volume': deepdive_data.get('search_volume', 0),
            'velocity': safe_get(deepdive_data, 'velocity'),
            'sentiment': safe_get(deepdive_data, 'sentiment'),
            'category': safe_get(deepdive_data, 'category'),
            'character': safe_get(deepdive_data, 'character', ''),
            
            # Research Data - JSON fields
            'research_data': safe_json(deepdive_data, 'research_data'),
            'sources_summary': safe_get(deepdive_data, 'sources_summary'),
            
            # Story
            'title': safe_get(deepdive_data, 'title'),
            'subtitle': safe_get(deepdive_data, 'subtitle'),
            'anomaly': safe_get(deepdive_data, 'anomaly'),
            'approved_story': safe_get(deepdive_data, 'approved_story'),
            
            # Script & Metadata
            'script_final': safe_get(deepdive_data, 'script_final'),
            'youtube_title': safe_get(deepdive_data, 'youtube_title'),
            'youtube_description': safe_get(deepdive_data, 'youtube_description'),
            'youtube_hook': safe_get(deepdive_data, 'youtube_hook'),
            'hashtags': deepdive_data.get('hashtags', []),
            'thumbnail_prompt': safe_get(deepdive_data, 'thumbnail_prompt'),
            'image_prompts': safe_json(deepdive_data, 'image_prompts'),
            
            # MoviePy Spec (if included) - JSON fields
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
    """
    Retrieve all deep dives with a specific status
    
    Args:
        supabase: Supabase client
        status: 'finalized', 'needs_finetuning', or 'published'
    
    Returns:
        List of deep dive records
    """
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
    """
    Retrieve a specific deep dive by ID
    
    Args:
        supabase: Supabase client
        deepdive_id: UUID of the deep dive
    
    Returns:
        Deep dive record or None
    """
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
    """
    Update the status of a deep dive
    
    Args:
        supabase: Supabase client
        deepdive_id: UUID of the deep dive
        new_status: 'finalized', 'needs_finetuning', or 'published'
    
    Returns:
        (success: bool, message: str)
    """
    try:
        timestamp = datetime.now(timezone.utc).isoformat()
        
        update_data = {
            'status': new_status,
            'updated_at': timestamp
        }
        
        # If finalizing, set finalized_at timestamp
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


def delete_deepdive(supabase, deepdive_id):
    """
    Delete a deep dive from the database
    
    Args:
        supabase: Supabase client
        deepdive_id: UUID of the deep dive
    
    Returns:
        (success: bool, message: str)
    """
    try:
        result = supabase.table('deep_dive_research')\
            .delete()\
            .eq('id', deepdive_id)\
            .execute()
        
        return True, "✅ Deep dive deleted successfully"
            
    except Exception as e:
        return False, f"❌ Error: {str(e)}"


def get_deepdives_by_keyword(supabase, keyword):
    """
    Retrieve all deep dives for a specific keyword
    
    Args:
        supabase: Supabase client
        keyword: The keyword to search for
    
    Returns:
        List of deep dive records
    """
    try:
        result = supabase.table('deep_dive_research')\
            .select('*')\
            .eq('keyword', keyword)\
            .order('created_at', desc=True)\
            .execute()
        
        if result.data:
            return result.data
        else:
            return []
            
    except Exception as e:
        print(f"Error fetching deep dives by keyword: {str(e)}")
        return []


def get_all_deepdives(supabase, limit=100):
    """
    Retrieve all deep dives (with optional limit)
    
    Args:
        supabase: Supabase client
        limit: Maximum number of records to return
    
    Returns:
        List of deep dive records
    """
    try:
        result = supabase.table('deep_dive_research')\
            .select('*')\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        if result.data:
            return result.data
        else:
            return []
            
    except Exception as e:
        print(f"Error fetching all deep dives: {str(e)}")
        return []


def update_deepdive_content(supabase, deepdive_id, updated_fields):
    """
    Update specific fields of a deep dive
    
    Args:
        supabase: Supabase client
        deepdive_id: UUID of the deep dive
        updated_fields: Dict with fields to update
    
    Returns:
        (success: bool, message: str)
    """
    try:
        timestamp = datetime.now(timezone.utc).isoformat()
        updated_fields['updated_at'] = timestamp
        
        result = supabase.table('deep_dive_research')\
            .update(updated_fields)\
            .eq('id', deepdive_id)\
            .execute()
        
        if result.data:
            return True, "✅ Deep dive updated successfully"
        else:
            return False, "❌ Failed to update deep dive"
            
    except Exception as e:
        return False, f"❌ Error: {str(e)}"


def fetch_deepdive_from_db(supabase, keyword):
    """
    Fetch the most recent deep dive for a keyword
    
    Args:
        supabase: Supabase client
        keyword: Keyword to search for
    
    Returns:
        Deep dive record or None
    """
    try:
        result = supabase.table('deep_dive_research')\
            .select('*')\
            .eq('keyword', keyword)\
            .order('created_at', desc=True)\
            .limit(1)\
            .execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        else:
            return None
            
    except Exception as e:
        print(f"Error fetching deep dive: {str(e)}")
        return None