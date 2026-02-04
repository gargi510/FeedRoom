"""
Tab 2: Intelligence Analysis - UPDATED WITH SAVE BUTTON
Added: Save Complete Analysis button that pushes intelligence + insights + entities to DB
"""
import streamlit as st
import pandas as pd
from datetime import datetime, date
from prompts import get_analysis_prompt
from utils import parse_json_input


def fetch_latest_trends_from_db(supabase):
    """Fetch last 10 trends per region from today's data"""
    try:
        today = date.today().isoformat()
        
        google_latest = supabase.table('google_trends')\
            .select('collection_timestamp')\
            .eq('collection_date', today)\
            .order('collection_timestamp', desc=True)\
            .limit(1)\
            .execute()
        
        if google_latest.data and len(google_latest.data) > 0:
            latest_timestamp = google_latest.data[0]['collection_timestamp']
            
            google_usa = supabase.table('google_trends')\
                .select('*')\
                .eq('collection_date', today)\
                .eq('collection_timestamp', latest_timestamp)\
                .eq('region', 'USA')\
                .order('rank')\
                .limit(10)\
                .execute()
            
            google_india = supabase.table('google_trends')\
                .select('*')\
                .eq('collection_date', today)\
                .eq('collection_timestamp', latest_timestamp)\
                .eq('region', 'India')\
                .order('rank')\
                .limit(10)\
                .execute()
            
            google_data = google_usa.data + google_india.data if google_usa.data and google_india.data else []
        else:
            google_data = []
        
        twitter_latest = supabase.table('twitter_trends')\
            .select('collection_timestamp')\
            .eq('collection_date', today)\
            .order('collection_timestamp', desc=True)\
            .limit(1)\
            .execute()
        
        if twitter_latest.data and len(twitter_latest.data) > 0:
            latest_timestamp = twitter_latest.data[0]['collection_timestamp']
            
            twitter_usa = supabase.table('twitter_trends')\
                .select('*')\
                .eq('collection_date', today)\
                .eq('collection_timestamp', latest_timestamp)\
                .eq('region', 'USA')\
                .order('rank')\
                .limit(10)\
                .execute()
            
            twitter_india = supabase.table('twitter_trends')\
                .select('*')\
                .eq('collection_date', today)\
                .eq('collection_timestamp', latest_timestamp)\
                .eq('region', 'India')\
                .order('rank')\
                .limit(10)\
                .execute()
            
            twitter_data = twitter_usa.data + twitter_india.data if twitter_usa.data and twitter_india.data else []
        else:
            twitter_data = []
        
        return google_data, twitter_data, None
        
    except Exception as e:
        return None, None, f"Database error: {str(e)}"


def prepare_data_summary():
    """Prepare data summary for AI analysis"""
    try:
        google_df = pd.DataFrame(st.session_state.get('google_data', []))
        twitter_df = pd.DataFrame(st.session_state.get('twitter_data', []))
        
        if google_df.empty or twitter_df.empty:
            return {}

        usa_google = google_df[google_df['region'] == 'USA'].nlargest(10, 'search_volume')
        india_google = google_df[google_df['region'] == 'India'].nlargest(10, 'search_volume')
        usa_twitter = twitter_df[twitter_df['region'] == 'USA'].nlargest(10, 'mention_volume')
        india_twitter = twitter_df[twitter_df['region'] == 'India'].nlargest(10, 'mention_volume')
        
        combined = pd.concat([google_df, twitter_df])
        breakouts = combined[combined['velocity'].str.lower().isin(['breakout', 'spike'])] if 'velocity' in combined.columns else pd.DataFrame()
        
        usa_breakouts = breakouts[breakouts['region'] == 'USA']['keyword'].tolist()[:5] if len(breakouts) > 0 else []
        india_breakouts = breakouts[breakouts['region'] == 'India']['keyword'].tolist()[:5] if len(breakouts) > 0 else []
        
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'usa_google_summary': f"Top 10: {usa_google['keyword'].tolist()}",
            'india_google_summary': f"Top 10: {india_google['keyword'].tolist()}",
            'usa_twitter_summary': f"Top 10: {usa_twitter['keyword'].tolist()}",
            'india_twitter_summary': f"Top 10: {india_twitter['keyword'].tolist()}",
            'breakout_trends': f"USA: {usa_breakouts}, India: {india_breakouts}",
        }
    except Exception as e:
        st.error(f"Error preparing data summary: {str(e)}")
        return {}


def render_intelligence_analysis_tab(gemini_pro, gemini_flash, supabase):
    """Main render function for Intelligence Analysis tab"""
    st.header("🧠 Intelligence Analysis")
    st.caption("**The FeedRoom Intelligence Grid - Powered by Gemini**")
    
    col_fetch, col_fresh = st.columns(2)
    
    with col_fetch:
        if st.button("📥 Fetch Latest 10 Trends from DB", type="secondary", use_container_width=True):
            if not supabase:
                st.error("❌ Supabase not configured")
            else:
                with st.spinner("🔄 Fetching latest 10 trends per region..."):
                    google_data, twitter_data, error = fetch_latest_trends_from_db(supabase)
                    
                    if error:
                        st.error(error)
                    elif not google_data and not twitter_data:
                        st.warning(f"⚠️ No data found for {date.today().isoformat()}. Please collect fresh data first.")
                    else:
                        st.session_state['google_data'] = google_data
                        st.session_state['twitter_data'] = twitter_data
                        st.success(f"✅ Loaded: {len(google_data)} Google + {len(twitter_data)} Twitter trends")
                        st.rerun()
    
    with col_fresh:
        if st.button("🔄 Use Fresh Collection Data", type="secondary", use_container_width=True):
            if 'google_data' in st.session_state and 'twitter_data' in st.session_state:
                st.success("✅ Using fresh collection data from session")
                st.rerun()
            else:
                st.warning("⚠️ No fresh data in session. Please collect data first.")
    
    if 'google_data' not in st.session_state or 'twitter_data' not in st.session_state:
        st.info("📥 Collect data in **Data Collection** tab or fetch from DB")
        return
    
    if st.session_state.get('finetune_mode', False):
        render_prompt_finetuner()
        return
    
    st.divider()
    render_phase0_combined_analysis(gemini_pro, gemini_flash, supabase)


def render_phase0_combined_analysis(gemini_pro, gemini_flash, supabase):
    """Generate intelligence for BOTH regions and display side-by-side"""
    st.markdown("### 📊 Combined Intelligence Generation")
    st.caption("Analyze data for BOTH India and USA together")
    
    col_auto, col_manual = st.columns(2)
    
    with col_auto:
        st.info("🤖 **Auto-Generate**")
        model_choice = st.selectbox("Model:", ["Gemini Pro", "Gemini Flash"], key='model_both')
        
        if st.button("🚀 Generate Intelligence (Both Regions)", type="primary", use_container_width=True, key='gen_both'):
            with st.spinner("🧠 Analyzing trends for both regions..."):
                try:
                    data_summary = prepare_data_summary()
                    if not data_summary:
                        st.error("❌ No data available for analysis")
                        return
                    
                    prompt = get_analysis_prompt(data_summary)
                    model = gemini_flash if "Flash" in model_choice else gemini_pro
                    response = model.generate_content(prompt)
                    data = parse_json_input(response.text)
                    
                    if data and 'india_intelligence' in data and 'usa_intelligence' in data:
                        st.session_state['intelligence_India'] = data['india_intelligence']
                        st.session_state['intelligence_USA'] = data['usa_intelligence']
                        st.session_state['executive_summary'] = data.get('executive_summary', '')
                        st.session_state['entities'] = data.get('entities', [])  # CRITICAL: Extract entities
                        st.success("✅ Intelligence Generated for Both Regions!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid response structure. Expected 'india_intelligence' and 'usa_intelligence'")
                except Exception as e:
                    st.error(f"❌ Generation failed: {str(e)}")
    
    with col_manual:
        st.warning("📋 **Manual Mode**")
        if st.button("1️⃣ Generate Prompt", use_container_width=True, key='generate_prompt_btn'):
            data_summary = prepare_data_summary()
            if data_summary:
                st.session_state['manual_prompt'] = get_analysis_prompt(data_summary)
            else:
                st.error("❌ No data available")
        
        if 'manual_prompt' in st.session_state:
            st.text_area("Copy to Gemini:", st.session_state['manual_prompt'], height=80, key='prompt_display')
        
        manual_json = st.text_area("2️⃣ Paste JSON:", height=80, key='manual_json')

        if st.button("3️⃣ Parse & Save", use_container_width=True, key='parse'):
            if not manual_json.strip():
                st.error("❌ Please paste JSON response")
                return
            
            data = parse_json_input(manual_json)
            if data and 'india_intelligence' in data and 'usa_intelligence' in data:
                st.session_state['intelligence_India'] = data['india_intelligence']
                st.session_state['intelligence_USA'] = data['usa_intelligence']
                st.session_state['executive_summary'] = data.get('executive_summary', '')
                st.session_state['entities'] = data.get('entities', [])  # CRITICAL: Extract entities
                st.success("✅ Intelligence saved!")
                st.rerun()
            else:
                st.error("❌ Invalid JSON. Expected 'india_intelligence' and 'usa_intelligence'")

    if 'intelligence_India' in st.session_state and 'intelligence_USA' in st.session_state:
        st.divider()
        st.markdown("### 📊 Intelligence Grid Analysis")
        
        if 'executive_summary' in st.session_state:
            st.info(f"**Executive Summary:** {st.session_state['executive_summary']}")
        
        col_india, col_usa = st.columns(2)
        
        with col_india:
            st.markdown("#### 🇮🇳 India Intelligence")
            display_intelligence_full(st.session_state['intelligence_India'], 'India')
        
        with col_usa:
            st.markdown("#### 🇺🇸 USA Intelligence")
            display_intelligence_full(st.session_state['intelligence_USA'], 'USA')
        
        st.divider()
        
        # CRITICAL: Save Complete Analysis Button
        st.markdown("### 💾 Save Complete Analysis to Database")
        st.caption("Save intelligence grids + insights + entities to Supabase")
        
        if st.button("💾 Save Intelligence + Insights + Entities", type="primary", use_container_width=True):
            if supabase:
                with st.spinner("💾 Saving complete analysis..."):
                    try:
                        from db_operations import save_complete_daily_analysis
                        
                        results = save_complete_daily_analysis(
                            supabase,
                            st.session_state['intelligence_India'],
                            st.session_state['intelligence_USA'],
                            st.session_state['executive_summary'],
                            st.session_state.get('entities', []),
                            date.today().isoformat()
                        )
                        
                        # Display results
                        if results['insights']['success']:
                            st.success(results['insights']['message'])
                        else:
                            st.error(results['insights']['message'])
                        
                        if results['content']['success']:
                            st.success(results['content']['message'])
                        else:
                            st.error(results['content']['message'])
                        
                        if results['entities']['success']:
                            st.success(results['entities']['message'])
                        else:
                            st.warning(results['entities']['message'])
                        
                        if all([results['insights']['success'], 
                               results['content']['success']]):
                            st.balloons()
                            
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.error("❌ Supabase not configured")
        
        st.divider()
        
        col_finetune = st.columns([2, 1])[1]
        with col_finetune:
            if st.button("⚙️ Fine-Tune Prompt", type="secondary", use_container_width=True):
                st.session_state['finetune_mode'] = True
                st.session_state['finetune_type'] = 'analysis'
                st.rerun()


def display_intelligence_full(intelligence, region):
    """Display intelligence grid with full details"""
    try:
        st.markdown("**📌 Weather Grid (Themes)**")
        for theme in intelligence.get('weather_grid', [])[:2]:  # Only 2 themes
            with st.expander(f"Theme {theme.get('slot')}: {theme.get('theme', 'N/A')}", expanded=True):
                st.markdown(f"**Category:** {theme.get('category', 'N/A')}")
                st.markdown(f"**Keywords:** {', '.join(theme.get('keywords', []))}")
                st.markdown(f"**Mood:** {theme.get('mood', 'N/A')}")
                st.markdown(f"**Data Signal:** {theme.get('data_signal', 'N/A')}")
                st.info(f"**Context:** {theme.get('context', 'N/A')}")
                st.success(f"**Deep Why:** {theme.get('deep_why', 'N/A')}")
                st.warning(f"**Big Question:** {theme.get('big_question', 'N/A')}")
        
        st.markdown("**🚨 Anomalies**")
        for outlier in intelligence.get('anomalies', [])[:2]:  # 2 anomalies
            with st.expander(f"Anomaly {outlier.get('rank')}: {outlier.get('keyword', 'N/A')}", expanded=True):
                st.markdown(f"**Velocity:** {outlier.get('velocity', 'N/A')}")
                st.info(f"**Explanation:** {outlier.get('explanation', 'N/A')}")
                st.warning(f"**Big Question:** {outlier.get('big_question', 'N/A')}")
        
        st.markdown("**🎨 Production Mood**")
        prod_mood = intelligence.get('production_mood', {})
        with st.expander("View Production Settings", expanded=False):
            st.markdown(f"**Overall Sentiment:** {prod_mood.get('overall_sentiment', 0)}")
            st.markdown(f"**Vibe Color:** {prod_mood.get('vibe_color_hex', '#000000')}")
            st.markdown(f"**Vocal Tone:** {prod_mood.get('vocal_tone', 'N/A')}")
            st.markdown(f"**Visual Background:** {prod_mood.get('visual_background_prompt', 'N/A')}")
    except Exception as e:
        st.error(f"Error displaying intelligence: {str(e)}")


def render_prompt_finetuner():
    """Enhanced fine-tuner with complete sections"""
    st.markdown("### ⚙️ Prompt Fine-Tuner")
    st.caption("Edit prompt sections while keeping structure locked")
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("**📖 Current Prompt Structure**")
        st.info("View-only: Shows the structure of the prompt")
        
        with st.expander("View Full Prompt", expanded=False):
            try:
                prompt_text = get_analysis_prompt(prepare_data_summary())
                st.code(prompt_text, language='text')
            except Exception as e:
                st.error(f"Error loading prompt: {str(e)}")
    
    with col_right:
        st.markdown("**✏️ Editable Sections**")
        
        identity = st.text_area(
            "1️⃣ Identity Block:",
            "You are the Lead Intelligence Analyst for The FeedRoom. Your mission is to synthesize raw data into high-fidelity strategic insights for daily trend reports.",
            height=100,
            key='identity_edit'
        )
        
        mission = st.text_area(
            "2️⃣ Mission Block:",
            """1. ANALYZE: Review global data to find regional contrasts and cultural ripples.
2. CLUSTER: Group data into EXACTLY 2 major themes per region.
3. DETECT: Identify EXACTLY 2 distinct anomalies per region (low volume, breakout velocity).
4. SYNTHESIZE: For every theme, follow the 'Chain of Logic': Data Signal -> Factual Context -> Deep Why -> The Big Question.""",
            height=150,
            key='mission_edit'
        )
        
        exec_summary = st.text_area(
            "3️⃣ Executive Summary Instruction:",
            "2-3 sentences: Compare the Global (USA) vs. Local (India) pulse for today.",
            height=60,
            key='exec_summary_edit'
        )
        
        weather_grid = st.text_area(
            "4️⃣ Weather Grid Instruction:",
            "EXACTLY 2 major themes per region with sharp 3-word titles. Each slot must have: category, theme, keywords, mood, data_signal, context, deep_why, big_question",
            height=100,
            key='weather_grid_edit'
        )
        
        rules = st.text_area(
            "5️⃣ Critical Rules:",
            """- Use ONLY keywords found in the provided data sources.
- Provide EXACTLY 2 themes and 2 anomalies for BOTH India and USA.
- Every slot must be complete; no empty strings or placeholders.
- Return ONLY valid JSON within the markdown block.""",
            height=120,
            key='rules_edit'
        )
        
        st.divider()
        
        if st.button("💾 Save & Update prompts.py", type="primary", use_container_width=True):
            with st.spinner("📝 Updating prompts.py..."):
                try:
                    from prompt_updater import update_analysis_prompt, backup_prompts_file
                    
                    backup_success, backup_msg = backup_prompts_file()
                    if backup_success:
                        st.info(backup_msg)
                    
                    success, message = update_analysis_prompt(
                        identity=identity,
                        mission=mission,
                        exec_summary=exec_summary,
                        weather_grid=weather_grid,
                        rules=rules
                    )
                    
                    if success:
                        st.success(message)
                        st.balloons()
                        st.info("🔄 Restart the app to use the updated prompt")
                    else:
                        st.error(message)
                        
                except ImportError:
                    st.error("❌ prompt_updater.py not found")
                except Exception as e:
                    st.error(f"❌ Update failed: {str(e)}")
    
    if st.button("❌ Exit Fine-Tuner", type="secondary"):
        st.session_state['finetune_mode'] = False
        st.rerun()