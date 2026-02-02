"""
Tab 1: Data Collection - Combined SerpAPI Fetch + Manual Enrichment Fallback
- Single button fetches USA (10) + India (10) trends together
- Auto-enriches with Gemini (single API call) if quota available
- Falls back to manual copy-paste if quota expires
- Split display: India (left) + USA (right)
"""
import streamlit as st
import pandas as pd
import json
from serpapi import GoogleSearch
from datetime import datetime, date
from prompts import get_google_enrichment_prompt, get_twitter_prompt
from utils import parse_json_input, validate_and_normalize_trends, push_to_supabase


def parse_serpapi_traffic(traffic_str):
    """Convert SerpAPI traffic string to numeric volume"""
    if not traffic_str or traffic_str == "Unknown":
        return 0
    
    traffic_str = str(traffic_str).upper().replace('+', '').replace(',', '')
    
    try:
        if 'M' in traffic_str:
            return int(float(traffic_str.replace('M', '')) * 1_000_000)
        elif 'K' in traffic_str:
            return int(float(traffic_str.replace('K', '')) * 1000)
        else:
            return int(traffic_str)
    except:
        return 0


def fetch_google_trends_serpapi(api_key, region='US', count=10):
    """Fetch real-time Google Trends using SerpAPI"""
    try:
        params = {
            "engine": "google_trends_trending_now",
            "geo": region,
            "hours": 24,
            "api_key": api_key
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "error" in results:
            return None, f"SerpAPI Error: {results['error']}"
        
        trending_data = results.get("trending_searches", [])
        
        if not trending_data:
            return None, "No trending searches found"
        
        trends_data = []
        region_name = "USA" if region == "US" else "India"
        
        for idx, trend in enumerate(trending_data[:count], 1):
            query = trend.get("query", "")
            search_volume_str = trend.get("search_volume", "Unknown")
            volume = parse_serpapi_traffic(search_volume_str)
            is_breakout = volume > 500000 or "breakout" in str(search_volume_str).lower()
            
            related = trend.get("related_queries", [])
            if isinstance(related, list):
                related = [q.get("query", q) if isinstance(q, dict) else str(q) for q in related[:5]]
            else:
                related = []
            
            trend_data = {
                'region': region_name,
                'rank': idx,
                'keyword': query,
                'search_volume_raw': search_volume_str,
                'search_volume': volume,
                'is_breakout': is_breakout,
                'related_searches': related
            }
            
            trends_data.append(trend_data)
        
        return trends_data, None
        
    except Exception as e:
        return None, f"Error: {str(e)}"


def send_to_gemini_for_combined_enrichment(gemini_model, usa_data, india_data):
    """Send BOTH regions to Gemini in a single API call"""
    try:
        # Build combined CSV
        csv_lines = ["Rank,Region,Keyword,Search Volume,Is Breakout,Related"]
        
        for trend in usa_data:
            related = '; '.join(trend.get('related_searches', [])[:3])
            csv_lines.append(
                f"{trend['rank']},USA,{trend['keyword']},{trend['search_volume_raw']},"
                f"{trend['is_breakout']},{related}"
            )
        
        for trend in india_data:
            related = '; '.join(trend.get('related_searches', [])[:3])
            csv_lines.append(
                f"{trend['rank']},India,{trend['keyword']},{trend['search_volume_raw']},"
                f"{trend['is_breakout']},{related}"
            )
        
        csv_data = "\n".join(csv_lines)
        prompt = get_google_enrichment_prompt("USA and India", csv_data)
        
        response = gemini_model.generate_content(prompt)
        response_text = response.text
        
        data = parse_json_input(response_text)
        
        if not data or 'trends' not in data:
            return None, None, "Failed to parse Gemini response"
        
        enriched = data['trends']
        
        # Split by region and merge
        usa_enriched = []
        india_enriched = []
        
        for e in enriched:
            if e.get('region') == 'USA':
                # Find matching raw data
                match = next((t for t in usa_data if t['rank'] == e.get('rank')), None)
                if match:
                    combined = match.copy()
                    combined.update({
                        'category': e.get('category', 'Unknown'),
                        'velocity': e.get('velocity', 'steady'),
                        'context': e.get('context', ''),
                        'why_trending': e.get('why_trending', ''),
                        'public_sentiment': e.get('public_sentiment', 'curious'),
                        'sentiment_score': e.get('sentiment_score', 50)
                    })
                    usa_enriched.append(combined)
            
            elif e.get('region') == 'India':
                match = next((t for t in india_data if t['rank'] == e.get('rank')), None)
                if match:
                    combined = match.copy()
                    combined.update({
                        'category': e.get('category', 'Unknown'),
                        'velocity': e.get('velocity', 'steady'),
                        'context': e.get('context', ''),
                        'why_trending': e.get('why_trending', ''),
                        'public_sentiment': e.get('public_sentiment', 'curious'),
                        'sentiment_score': e.get('sentiment_score', 50)
                    })
                    india_enriched.append(combined)
        
        return usa_enriched, india_enriched, None
        
    except Exception as e:
        return None, None, f"Gemini error: {str(e)}"


def display_trend_summary(trends, region):
    """Display summary + top 5 trends for a region"""
    if not trends:
        st.info(f"⏳ No {region} data")
        return
    
    # Calculate metrics
    total = len(trends)
    breakouts = sum(1 for t in trends if t.get('is_breakout', False))
    total_volume = sum(t.get('search_volume', 0) for t in trends)
    
    # Categories
    categories = {}
    for t in trends:
        cat = t.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
    top_category = max(categories.items(), key=lambda x: x[1])[0] if categories else 'N/A'
    
    st.markdown(f"**📊 {region} Summary**")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Trends", total)
        st.metric("Breakouts", breakouts)
    with col2:
        st.metric("Total Volume", f"{total_volume:,}")
        st.metric("Top Category", top_category)
    
    st.markdown(f"**🔥 Top 5 Trends**")
    for i, t in enumerate(trends[:5], 1):
        emoji = "🔥" if t.get('is_breakout') else "📈"
        st.markdown(f"{i}. {emoji} **{t['keyword']}**")
        st.caption(f"   Volume: {t.get('search_volume_raw')} | {t.get('category', 'N/A')}")


def render_google_serpapi_section(api_key, gemini_model):
    """Render combined SerpAPI Google Trends section"""
    st.markdown("### 🔍 Google Trends (Auto-Fetch Both Regions)")
    st.info("✨ Fetches USA (10) + India (10) trends together. Auto-enriches if quota available.")
    
    # Single fetch button
    if st.button("🌍 Fetch USA + India Trends", type="primary", use_container_width=True, key='fetch_both'):
        if not api_key:
            st.error("❌ SERPAPI_KEY not configured")
        else:
            with st.spinner("🔄 Fetching trends from both regions..."):
                # Fetch USA
                usa_data, usa_error = fetch_google_trends_serpapi(api_key, region='US', count=10)
                # Fetch India
                india_data, india_error = fetch_google_trends_serpapi(api_key, region='IN', count=10)
                
                if usa_error or india_error:
                    st.error(f"❌ Fetch errors: USA: {usa_error}, India: {india_error}")
                else:
                    st.success(f"✅ Fetched {len(usa_data)} USA + {len(india_data)} India trends")
                    
                    # Store raw data
                    st.session_state['temp_usa_raw'] = usa_data
                    st.session_state['temp_india_raw'] = india_data
                    
                    # Try auto-enrichment with SINGLE Gemini call
                    if gemini_model:
                        with st.spinner("🤖 Auto-enriching with Gemini (combined call)..."):
                            usa_enriched, india_enriched, enrich_error = send_to_gemini_for_combined_enrichment(
                                gemini_model, usa_data, india_data
                            )
                            
                            if enrich_error:
                                st.error(f"❌ Auto-enrichment failed: {enrich_error}")
                                st.warning("⚠️ Use manual enrichment section below")
                            else:
                                st.success("✅ Auto-enrichment complete!")
                                
                                # Save to session
                                if 'google_data' not in st.session_state:
                                    st.session_state['google_data'] = []
                                
                                # Remove old data for these regions
                                st.session_state['google_data'] = [
                                    t for t in st.session_state['google_data'] 
                                    if t.get('region') not in ['USA', 'India']
                                ]
                                
                                st.session_state['google_data'].extend(usa_enriched)
                                st.session_state['google_data'].extend(india_enriched)
                                
                                # Clear temp
                                del st.session_state['temp_usa_raw']
                                del st.session_state['temp_india_raw']
                                
                                # Display split preview
                                st.markdown("---")
                                col_left, col_right = st.columns(2)
                                
                                with col_left:
                                    display_trend_summary(india_enriched, "India")
                                
                                with col_right:
                                    display_trend_summary(usa_enriched, "USA")
                                
                                st.balloons()
                    else:
                        st.warning("⚠️ Gemini not configured - use manual enrichment below")
    
    # === MANUAL ENRICHMENT FALLBACK ===
    if 'temp_usa_raw' in st.session_state or 'temp_india_raw' in st.session_state:
        st.divider()
        st.markdown("### 🔄 Manual Enrichment (Quota Exhausted / Fallback)")
        st.warning("⚠️ Auto-enrichment unavailable. Use manual process:")
        st.info("💡 Copy prompt → Paste in Gemini → Copy JSON response → Paste back here")
        
        # Combine pending data
        pending_data = []
        if 'temp_usa_raw' in st.session_state:
            pending_data.extend(st.session_state['temp_usa_raw'])
        if 'temp_india_raw' in st.session_state:
            pending_data.extend(st.session_state['temp_india_raw'])
        
        if pending_data:
            # Build CSV
            csv_lines = ["Rank,Region,Keyword,Search Volume,Is Breakout,Related"]
            for t in pending_data:
                related = '; '.join(t.get('related_searches', [])[:3])
                csv_lines.append(f"{t['rank']},{t['region']},{t['keyword']},{t['search_volume_raw']},{t['is_breakout']},{related}")
            csv_data = "\n".join(csv_lines)
            
            manual_prompt = f"""You are an expert trend analyst. Enrich these USA and India Google Trends.

🚨 INSTRUCTIONS:
1. Use ONLY keywords from CSV
2. Google Search each for current news
3. Provide factual context

=== DATA ===
{csv_data}

=== OUTPUT (JSON) ===
```json
{{
  "trends": [
    {{
      "region": "USA/India",
      "rank": 1,
      "keyword": "exact keyword",
      "category": "Sports/Politics/Entertainment/Tech/News/Weather/Health/Business",
      "velocity": "breakout/rising/steady",
      "context": "What is this? Who/what involved?",
      "why_trending": "Why NOW? Cite events.",
      "public_sentiment": "excited/concerned/curious/celebrating/controversial",
      "sentiment_score": 0-100
    }}
  ]
}}
```

SENTIMENT GUIDE:
Sports Victory→celebrating(90), Pre-game→excited(75)
Crisis→concerned(20-30)
Entertainment Release→excited(70)
Tech Launch→excited(75)

Return ONLY valid JSON:"""
            
            # Display prompt
            st.text_area("📋 Copy to Gemini:", manual_prompt, height=400, key='manual_prompt')
            
            st.download_button(
                "💾 Download Prompt",
                manual_prompt,
                file_name=f"gemini_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                use_container_width=True
            )
            
            st.markdown("---")
            
            # Response input
            manual_json = st.text_area(
                "📥 Paste Gemini Response:",
                height=300,
                key='manual_response',
                placeholder='Paste JSON here...'
            )
            
            if st.button("✅ Process Response", type="primary", use_container_width=True):
                if not manual_json or len(manual_json.strip()) < 10:
                    st.error("❌ Paste JSON first")
                else:
                    try:
                        data = parse_json_input(manual_json)
                        
                        if not data or 'trends' not in data:
                            st.error("❌ Invalid JSON")
                        else:
                            enriched = data['trends']
                            
                            # Merge with raw data
                            final = []
                            for e in enriched:
                                match = next((t for t in pending_data if t['rank']==e.get('rank') and t['region']==e.get('region')), None)
                                if match:
                                    combined = match.copy()
                                    combined.update({
                                        'category': e.get('category', 'Unknown'),
                                        'velocity': e.get('velocity', 'steady'),
                                        'context': e.get('context', ''),
                                        'why_trending': e.get('why_trending', ''),
                                        'public_sentiment': e.get('public_sentiment', 'curious'),
                                        'sentiment_score': e.get('sentiment_score', 50)
                                    })
                                    final.append(combined)
                                else:
                                    final.append(e)
                            
                            # Save
                            if 'google_data' not in st.session_state:
                                st.session_state['google_data'] = []
                            
                            # Remove old data for both regions
                            st.session_state['google_data'] = [
                                t for t in st.session_state['google_data'] 
                                if t.get('region') not in ['USA', 'India']
                            ]
                            
                            st.session_state['google_data'].extend(final)
                            
                            # Clear temp
                            if 'temp_usa_raw' in st.session_state:
                                del st.session_state['temp_usa_raw']
                            if 'temp_india_raw' in st.session_state:
                                del st.session_state['temp_india_raw']
                            
                            st.success(f"✅ Enriched {len(final)} trends!")
                            
                            # Display split preview
                            usa_final = [t for t in final if t.get('region') == 'USA']
                            india_final = [t for t in final if t.get('region') == 'India']
                            
                            st.markdown("---")
                            col_left, col_right = st.columns(2)
                            
                            with col_left:
                                display_trend_summary(india_final, "India")
                            
                            with col_right:
                                display_trend_summary(usa_final, "USA")
                            
                            st.balloons()
                            st.rerun()
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    # Display current data if exists
    elif 'google_data' in st.session_state and len(st.session_state['google_data']) > 0:
        st.divider()
        st.markdown("### ✅ Current Google Trends Data")
        
        usa_trends = [t for t in st.session_state['google_data'] if t.get('region') == 'USA']
        india_trends = [t for t in st.session_state['google_data'] if t.get('region') == 'India']
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            display_trend_summary(india_trends, "India")
        
        with col_right:
            display_trend_summary(usa_trends, "USA")


def render_twitter_section():
    """Twitter/X Trends Collection with split display"""
    st.markdown("### 🐦 Twitter/X Trends (Manual)")
    
    with st.expander("📋 Copy Grok Prompt", expanded=False):
        st.text_area("Copy to Grok:", get_twitter_prompt(), height=400, key='twitter_prompt')
    
    st.markdown("---")
    
    twitter_json = st.text_area("📥 Paste Grok JSON:", height=300, key='twitter_input', placeholder='Paste JSON...')
    
    if st.button("✅ Parse Twitter", type="primary", use_container_width=True):
        if not twitter_json:
            st.error("❌ Paste JSON")
        else:
            try:
                data = parse_json_input(twitter_json)
                
                if not data or 'trends' not in data:
                    st.error("❌ No trends found")
                else:
                    valid, report = validate_and_normalize_trends(data['trends'], 'twitter')
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total", report['total'])
                    col2.metric("Valid", report['valid'])
                    col3.metric("Invalid", report['invalid'])
                    
                    if valid:
                        st.session_state['twitter_data'] = valid
                        st.success(f"✅ Loaded {len(valid)} trends!")
                        
                        # Split display
                        usa_twitter = [t for t in valid if t.get('region') == 'USA']
                        india_twitter = [t for t in valid if t.get('region') == 'India']
                        
                        st.markdown("---")
                        col_left, col_right = st.columns(2)
                        
                        with col_left:
                            display_twitter_summary(india_twitter, "India")
                        
                        with col_right:
                            display_twitter_summary(usa_twitter, "USA")
                        
                        st.balloons()
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    # Display current data if exists
    elif 'twitter_data' in st.session_state and len(st.session_state['twitter_data']) > 0:
        st.divider()
        st.markdown("### ✅ Current Twitter Trends Data")
        
        usa_twitter = [t for t in st.session_state['twitter_data'] if t.get('region') == 'USA']
        india_twitter = [t for t in st.session_state['twitter_data'] if t.get('region') == 'India']
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            display_twitter_summary(india_twitter, "India")
        
        with col_right:
            display_twitter_summary(usa_twitter, "USA")


def display_twitter_summary(trends, region):
    """Display summary + top 5 Twitter trends for a region"""
    if not trends:
        st.info(f"⏳ No {region} data")
        return
    
    # Calculate metrics
    total = len(trends)
    total_mentions = sum(t.get('mention_volume', 0) for t in trends)
    
    # Categories
    categories = {}
    for t in trends:
        cat = t.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
    top_category = max(categories.items(), key=lambda x: x[1])[0] if categories else 'N/A'
    
    # Sentiment
    sentiments = {}
    for t in trends:
        sent = t.get('primary_sentiment', 'curious')
        sentiments[sent] = sentiments.get(sent, 0) + 1
    top_sentiment = max(sentiments.items(), key=lambda x: x[1])[0] if sentiments else 'N/A'
    
    st.markdown(f"**📊 {region} Summary**")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Trends", total)
        st.metric("Total Mentions", f"{total_mentions:,}")
    with col2:
        st.metric("Top Category", top_category)
        st.metric("Top Sentiment", top_sentiment)
    
    st.markdown(f"**🔥 Top 5 Trends**")
    for i, t in enumerate(trends[:5], 1):
        st.markdown(f"{i}. **{t['keyword']}**")
        st.caption(f"   Mentions: {t.get('mention_volume', 0):,} | {t.get('category', 'N/A')} | {t.get('primary_sentiment', 'N/A')}")


def render_collection_tab(serpapi_key, gemini_model, supabase):
    """Main render"""
    st.header("📥 Data Collection")
    st.markdown("**Sophia's Logic Grid + Sonia's Pattern Hunt**")
    
    st.info("🎯 Fetch Google Trends (auto-enriches or manual fallback) + Paste Twitter data!")
    
    st.divider()
    
    render_google_serpapi_section(serpapi_key, gemini_model)
    
    st.divider()
    
    render_twitter_section()
    
    st.markdown("---")
    st.subheader("📊 Overall Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        count = len(st.session_state.get('google_data', []))
        if count > 0:
            st.success(f"✅ Google: {count}")
        else:
            st.info("⏳ No Google data")
    
    with col2:
        count = len(st.session_state.get('twitter_data', []))
        if count > 0:
            st.success(f"✅ Twitter: {count}")
        else:
            st.info("⏳ No Twitter data")
    
    with col3:
        total = len(st.session_state.get('google_data', [])) + len(st.session_state.get('twitter_data', []))
        if total > 0:
            st.success(f"✅ Total: {total}")
        else:
            st.warning("⚠️ No data")
    
    # Push Data Button
    if total > 0:
        st.divider()
        
        col_push, col_clear = st.columns(2)
        
        with col_push:
            if st.button("📤 Push to Database", type="primary", use_container_width=True):
                if not supabase:
                    st.error("❌ Supabase not configured")
                else:
                    with st.spinner("🔄 Pushing data to database..."):
                        success, message = push_to_supabase(
                            supabase,
                            st.session_state.get('google_data', []),
                            st.session_state.get('twitter_data', [])
                        )
                        
                        if success:
                            st.success(message)
                            st.balloons()
                        else:
                            st.error(message)
        
        with col_clear:
            if st.button("🗑️ Clear All", type="secondary", use_container_width=True):
                for key in ['google_data', 'twitter_data', 'ai_analysis', 'script', 'temp_usa_raw', 'temp_india_raw']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.success("✅ Cleared")
                st.rerun()