"""
Tab 4: Deep Dive Research - PRODUCTION VERSION
Strategic Clash Research + Script Generation + Database Save
"""
import streamlit as st
import pandas as pd
from datetime import date
from prompts import get_deepdive_research_prompt, get_deepdive_script_prompt
from utils import parse_json_input
import os


def render_deepdive_research_tab(gemini_pro, gemini_flash, supabase):
    """Main deep dive tab - research, script, and database save workflow"""
    
    st.header("🔬 Deep Dive Research")
    st.caption("**The FeedRoom Strategic Clash Analysis**")
    
    if st.session_state.get('deepdive_finetune_mode', False):
        render_deepdive_finetuner()
        return
    
    st.divider()
    
    render_keyword_selector_dropdown(supabase)
    
    if 'deepdive_keyword' not in st.session_state:
        return
    
    st.divider()
    
    phase = st.session_state.get('deepdive_phase', 1)
    
    phase_cols = st.columns(2)
    phases = [(1, "Research"), (2, "Script & Save")]
    
    for idx, (phase_num, phase_name) in enumerate(phases):
        with phase_cols[idx]:
            if phase >= phase_num:
                st.success(f"✅ {phase_num}: {phase_name}")
            else:
                st.info(f"⏳ {phase_num}: {phase_name}")
    
    st.divider()
    
    if phase == 1:
        render_phase1_research(gemini_pro, gemini_flash)
    elif phase == 2:
        render_phase2_script_and_save(gemini_pro, gemini_flash, supabase)


def render_keyword_selector_dropdown(supabase):
    """Dropdown selector: Date → Region → Platform → Keyword"""
    st.markdown("### 🎯 Select Keyword for Deep Dive")
    
    col_date1, col_date2 = st.columns([3, 1])
    
    with col_date1:
        selected_date = st.date_input(
            "📅 Select Data Date:",
            value=date.today(),
            max_value=date.today(),
            key='deepdive_data_date',
            help="Choose which day's trending data to analyze"
        )
    
    with col_date2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
    
    google_data = fetch_google_trends_for_date(supabase, selected_date.isoformat())
    twitter_data = fetch_twitter_trends_for_date(supabase, selected_date.isoformat())
    
    if not google_data and not twitter_data:
        st.warning(f"⚠️ No data found for {selected_date.isoformat()}")
        st.info("💡 Try selecting a different date or collect data first in the Data Collection tab")
        return
    
    google_df = pd.DataFrame(google_data) if google_data else pd.DataFrame()
    twitter_df = pd.DataFrame(twitter_data) if twitter_data else pd.DataFrame()
    
    if len(google_df) > 0:
        google_df['platform'] = 'Google Trends'
    if len(twitter_df) > 0:
        twitter_df['platform'] = 'Twitter/X'
    
    combined_df = pd.concat([google_df, twitter_df], ignore_index=True)
    
    if len(combined_df) == 0:
        st.warning("No data available")
        return
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        regions = sorted(combined_df['region'].unique().tolist())
        selected_region = st.selectbox("1️⃣ Region:", [""] + regions, key='dd_region')
    
    if not selected_region:
        return
    
    region_df = combined_df[combined_df['region'] == selected_region]
    
    with col2:
        platforms = sorted(region_df['platform'].unique().tolist())
        selected_platform = st.selectbox("2️⃣ Platform:", [""] + platforms, key='dd_platform')
    
    if not selected_platform:
        return
    
    platform_df = region_df[region_df['platform'] == selected_platform]
    
    if 'search_volume' in platform_df.columns and selected_platform == 'Google Trends':
        platform_df = platform_df.sort_values('search_volume', ascending=False)
        vol_col = 'search_volume'
    elif 'mention_volume' in platform_df.columns:
        platform_df = platform_df.sort_values('mention_volume', ascending=False)
        vol_col = 'mention_volume'
    else:
        vol_col = None
    
    with col3:
        keywords = platform_df['keyword'].unique().tolist()
        selected_keyword = st.selectbox("3️⃣ Keyword:", [""] + keywords[:50], key='dd_keyword')
    
    if not selected_keyword:
        return
    
    keyword_row = platform_df[platform_df['keyword'] == selected_keyword].iloc[0]
    
    st.divider()
    
    st.markdown("### 📋 Selected Keyword")
    
    col_meta1, col_meta2 = st.columns(2)
    
    with col_meta1:
        st.markdown(
            f"""<div style="background:linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); 
            padding:20px; border-radius:12px; color:white;">
            <h3 style="margin:0;">🎯 {selected_keyword}</h3></div>""",
            unsafe_allow_html=True
        )
        st.markdown(f"**📅 Date:** {selected_date.isoformat()}")
        st.markdown(f"**🌍 Region:** {selected_region}")
        st.markdown(f"**📱 Platform:** {selected_platform}")
        st.markdown(f"**📂 Category:** {keyword_row.get('category', 'N/A')}")
    
    with col_meta2:
        volume = keyword_row.get(vol_col, 0) if vol_col else 0
        st.markdown(
            f"""<div style="background:linear-gradient(135deg, #10b981 0%, #059669 100%); 
            padding:20px; border-radius:12px; color:white;">
            <h3 style="margin:0;">📊 {volume:,}</h3></div>""",
            unsafe_allow_html=True
        )
        st.markdown(f"**🚀 Velocity:** {keyword_row.get('velocity', 'steady')}")
        st.markdown(f"**💭 Sentiment:** {keyword_row.get('public_sentiment', keyword_row.get('primary_sentiment', 'curious'))}")
    
    st.info(f"**Context:** {keyword_row.get('context', 'N/A')}")
    st.success(f"**Why Trending:** {keyword_row.get('why_trending', 'N/A')}")
    
    st.divider()
    
    if st.button("✅ Confirm & Start", type="primary", use_container_width=True):
        st.session_state['deepdive_keyword'] = {
            'keyword': selected_keyword,
            'region': selected_region,
            'platform': selected_platform,
            'category': keyword_row.get('category', ''),
            'context': keyword_row.get('context', ''),
            'why_trending': keyword_row.get('why_trending', ''),
            'volume': volume,
            'velocity': keyword_row.get('velocity', 'steady'),
            'sentiment': keyword_row.get('public_sentiment', keyword_row.get('primary_sentiment', 'curious')),
            'data_date': selected_date.isoformat()
        }
        st.session_state['deepdive_phase'] = 1
        st.rerun()


def fetch_google_trends_for_date(supabase, date_str):
    """Fetch Google trends for specific date from session state or database"""
    if 'google_data' in st.session_state:
        google_df = pd.DataFrame(st.session_state['google_data'])
        if 'collection_date' in google_df.columns:
            filtered = google_df[google_df['collection_date'] == date_str]
            if len(filtered) > 0:
                return filtered.to_dict('records')
    
    if supabase:
        try:
            result = supabase.table('google_trends')\
                .select('*')\
                .eq('collection_date', date_str)\
                .execute()
            return result.data if result.data else []
        except:
            pass
    
    return []


def fetch_twitter_trends_for_date(supabase, date_str):
    """Fetch Twitter trends for specific date from session state or database"""
    if 'twitter_data' in st.session_state:
        twitter_df = pd.DataFrame(st.session_state['twitter_data'])
        if 'collection_date' in twitter_df.columns:
            filtered = twitter_df[twitter_df['collection_date'] == date_str]
            if len(filtered) > 0:
                return filtered.to_dict('records')
    
    if supabase:
        try:
            result = supabase.table('twitter_trends')\
                .select('*')\
                .eq('collection_date', date_str)\
                .execute()
            return result.data if result.data else []
        except:
            pass
    
    return []


def render_phase1_research(gemini_pro, gemini_flash):
    """Phase 1: Strategic clash research"""
    st.markdown("### 🔬 Phase 1: Strategic Clash Research")
    
    kw = st.session_state['deepdive_keyword']
    st.info(f"**Analyzing:** {kw['keyword']} ({kw['region']} - {kw['platform']})")
    
    col_auto, col_manual, col_ft = st.columns(3)
    
    with col_auto:
        if st.button("🚀 Research", type="primary", use_container_width=True):
            with st.spinner("🔍 Researching..."):
                try:
                    prompt = get_deepdive_research_prompt(
                        kw['keyword'], 
                        kw['region'], 
                        kw.get('context', ''), 
                        kw.get('why_trending', ''), 
                        kw.get('volume', 0), 
                        kw.get('velocity', 'steady'), 
                        kw.get('sentiment', 'curious')
                    )
                    response = gemini_pro.generate_content(prompt)
                    research_data, error = parse_deepdive_research(response.text)
                    
                    if error:
                        st.error(f"❌ {error}")
                    else:
                        st.session_state['deepdive_research'] = research_data
                        st.success("✅ Research completed!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ {str(e)}")
    
    with col_manual:
        if st.button("📋 Manual", use_container_width=True):
            prompt = get_deepdive_research_prompt(
                kw['keyword'], 
                kw['region'], 
                kw.get('context', ''), 
                kw.get('why_trending', ''), 
                kw.get('volume', 0), 
                kw.get('velocity', 'steady'), 
                kw.get('sentiment', 'curious')
            )
            st.session_state['dd_research_prompt'] = prompt
        
        if 'dd_research_prompt' in st.session_state:
            st.text_area("Prompt:", st.session_state['dd_research_prompt'], height=80, key='dd_p')
            manual_json = st.text_area("Paste JSON:", height=100, key='dd_j')
            
            if st.button("Parse", use_container_width=True):
                research_data, error = parse_deepdive_research(manual_json)
                if error:
                    st.error(f"❌ {error}")
                else:
                    st.session_state['deepdive_research'] = research_data
                    st.rerun()
    
    with col_ft:
        if st.button("⚙️ Fine-Tune", type="secondary", use_container_width=True):
            st.session_state['deepdive_finetune_mode'] = True
            st.session_state['deepdive_finetune_type'] = 'research'
            st.rerun()
    
    if 'deepdive_research' in st.session_state:
        st.divider()
        display_research_summary(st.session_state['deepdive_research'])
        
        st.divider()
        
        if st.button("✅ Proceed to Script", type="primary", use_container_width=True):
            st.session_state['deepdive_phase'] = 2
            st.rerun()


def parse_deepdive_research(research_json):
    """Parse and validate research JSON structure"""
    try:
        data = parse_json_input(research_json)
        
        if not data:
            return None, "Failed to parse JSON"
        
        required = ['keyword', 'simple_clash', 'lead_metric', 'strategic_clash', 'sources']
        missing = [f for f in required if f not in data]
        if missing:
            return None, f"Missing fields: {', '.join(missing)}"
        
        clash = data.get('strategic_clash', {})
        if not isinstance(clash, dict):
            return None, "'strategic_clash' must be an object"
        
        required_clash = ['side_a_logic', 'side_b_fear', 'the_deep_why']
        missing_clash = [f for f in required_clash if f not in clash]
        if missing_clash:
            return None, f"Missing in strategic_clash: {', '.join(missing_clash)}"
        
        return data, None
    except Exception as e:
        return None, f"Parse error: {str(e)}"


def display_research_summary(research):
    """Display strategic clash research summary"""
    st.markdown("### 📊 Research Summary")
    
    st.markdown(
        f"""<div style="background:linear-gradient(135deg, #f59e0b 0%, #ef4444 100%); 
        padding:30px; border-radius:15px; color:white; text-align:center; margin:20px 0;">
        <h2 style="margin:0;">📊 LEAD METRIC</h2>
        <h1 style="font-size:48px; margin:20px 0;">{research.get('lead_metric', 'N/A')}</h1>
        </div>""",
        unsafe_allow_html=True
    )
    
    st.info(f"**🎯 Simple Clash:** {research.get('simple_clash', 'N/A')}")
    
    if 'visual_concept' in research:
        st.success(f"🎬 **Visual:** {research['visual_concept']}")
    
    st.divider()
    
    st.markdown("### ⚔️ The Strategic Clash")
    
    clash = research.get('strategic_clash', {})
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("#### ✅ Side A: New Logic")
        st.markdown(
            f"""<div style="background:linear-gradient(135deg, #10b981 0%, #059669 100%); 
            padding:20px; border-radius:10px; color:white; min-height:150px;">
            <p style="font-size:15px; line-height:1.6;">{clash.get('side_a_logic', 'N/A')}</p>
            </div>""",
            unsafe_allow_html=True
        )
    
    with col_b:
        st.markdown("#### ⚠️ Side B: Traditional Fear")
        st.markdown(
            f"""<div style="background:linear-gradient(135deg, #ef4444 0%, #dc2626 100%); 
            padding:20px; border-radius:10px; color:white; min-height:150px;">
            <p style="font-size:15px; line-height:1.6;">{clash.get('side_b_fear', 'N/A')}</p>
            </div>""",
            unsafe_allow_html=True
        )
    
    st.markdown("#### 🔑 The Secret Sauce")
    st.markdown(
        f"""<div style="background:linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); 
        padding:25px; border-radius:10px; color:white;">
        <p style="font-size:17px; line-height:1.7;">{clash.get('the_deep_why', 'N/A')}</p>
        </div>""",
        unsafe_allow_html=True
    )
    
    sources = research.get('sources', [])
    if sources:
        with st.expander("📚 Sources", expanded=False):
            for idx, src in enumerate(sources, 1):
                st.markdown(
                    f"**{idx}. [{src.get('title', 'Source')}]({src.get('url', '#')})** - "
                    f"Reliability: {src.get('reliability', 'N/A')}"
                )


def render_phase2_script_and_save(gemini_pro, gemini_flash, supabase):
    """Phase 2: Script generation, editing, and database save"""
    st.markdown("### 🎬 Phase 2: Script Generation & Database Save")
    
    research = st.session_state.get('deepdive_research', {})
    kw = st.session_state.get('deepdive_keyword', {})
    
    if not research:
        st.error("❌ No research available. Return to Phase 1.")
        if st.button("⬅️ Back to Research"):
            st.session_state['deepdive_phase'] = 1
            st.rerun()
        return
    
    col_auto, col_manual, col_ft = st.columns(3)
    
    with col_auto:
        if st.button("🚀 Generate Script", type="primary", use_container_width=True):
            with st.spinner("📝 Generating script..."):
                try:
                    prompt = get_deepdive_script_prompt(research, kw['keyword'], kw['region'])
                    response = gemini_pro.generate_content(prompt)
                    assembly = parse_json_input(response.text)
                    
                    if assembly and 'audio_script' in assembly:
                        st.session_state['deepdive_assembly'] = assembly
                        st.session_state['deepdive_script'] = assembly.get('audio_script', '')
                        st.success("✅ Script generated!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid script structure")
                except Exception as e:
                    st.error(f"❌ {str(e)}")
    
    with col_manual:
        if st.button("📋 Manual", use_container_width=True):
            prompt = get_deepdive_script_prompt(research, kw['keyword'], kw['region'])
            st.session_state['dd_script_prompt'] = prompt
        
        if 'dd_script_prompt' in st.session_state:
            st.text_area("Prompt:", st.session_state['dd_script_prompt'], height=80, key='dd_sp')
            manual_json = st.text_area("Paste JSON:", height=100, key='dd_sj')
            
            if st.button("Parse", use_container_width=True):
                assembly = parse_json_input(manual_json)
                if assembly and 'audio_script' in assembly:
                    st.session_state['deepdive_assembly'] = assembly
                    st.session_state['deepdive_script'] = assembly.get('audio_script', '')
                    st.rerun()
                else:
                    st.error("❌ Invalid script structure")
    
    with col_ft:
        if st.button("⚙️ Fine-Tune", type="secondary", use_container_width=True):
            st.session_state['deepdive_finetune_mode'] = True
            st.session_state['deepdive_finetune_type'] = 'script'
            st.rerun()
    
    if 'deepdive_assembly' in st.session_state:
        st.divider()
        display_script_editor(supabase)


def display_script_editor(supabase):
    """Script editor with preview and database save"""
    st.markdown("### ✏️ Edit Script")
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("**📝 EDIT:**")
        if 'deepdive_script' not in st.session_state:
            st.session_state['deepdive_script'] = st.session_state['deepdive_assembly'].get('audio_script', '')
        
        edited = st.text_area(
            "Script:",
            st.session_state['deepdive_script'],
            height=400,
            key='dd_edit',
            label_visibility="collapsed"
        )
        st.session_state['deepdive_script'] = edited
    
    with col_right:
        st.markdown("**📄 PREVIEW:**")
        st.markdown(
            f"""<div style="background:#1a1a1a; padding:20px; border-radius:10px; 
            border-left:4px solid #8b5cf6; max-height:400px; overflow-y:auto; 
            font-size:16px; line-height:1.8; color:#f0f0f0;">
            {edited.replace(chr(10), '<br><br>')}</div>""",
            unsafe_allow_html=True
        )
        
        wc = len(edited.split())
        duration = wc / 150
        
        st.markdown(
            f"""<div style="background:#10b981; padding:10px; border-radius:8px; 
            color:white; text-align:center; margin-top:10px;">
            <strong>📊 Script Stats</strong> | {wc} words | ⏱️ ~{duration:.1f} min</div>""",
            unsafe_allow_html=True
        )
    
    st.divider()
    
    st.markdown("### 💾 Save to Database")
    st.caption("Save complete deep dive research, script, and metadata")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Back to Research", type="secondary", use_container_width=True):
            st.session_state['deepdive_phase'] = 1
            st.rerun()
    
    with col2:
        if st.button("💾 Save to Database", type="primary", use_container_width=True):
            if supabase:
                with st.spinner("💾 Saving to database..."):
                    try:
                        success, message = save_deepdive_to_database(supabase)
                        if success:
                            st.success(message)
                            st.balloons()
                        else:
                            st.error(message)
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.error("❌ Supabase not configured")


def save_deepdive_to_database(supabase):
    """Save complete deep dive to database with proper field mapping"""
    try:
        from db_operations import save_deepdive_to_db
        
        kw = st.session_state.get('deepdive_keyword', {})
        research = st.session_state.get('deepdive_research', {})
        assembly = st.session_state.get('deepdive_assembly', {})
        script = st.session_state.get('deepdive_script', '')
        
        youtube_metadata = assembly.get('youtube_metadata', {})
        
        deepdive_data = {
            'keyword': kw.get('keyword', ''),
            'region': kw.get('region', ''),
            'platform': kw.get('platform', ''),
            'search_volume': kw.get('volume', 0),
            'velocity': kw.get('velocity', ''),
            'sentiment': kw.get('sentiment', ''),
            'category': kw.get('category', ''),
            'research_data': research,
            'sources_summary': ', '.join([src.get('title', '') for src in research.get('sources', [])]),
            'script_final': script,
            'youtube_title': youtube_metadata.get('title', ''),
            'youtube_description': youtube_metadata.get('description', ''),
            'youtube_hook': youtube_metadata.get('hook', ''),
            'hashtags': youtube_metadata.get('hashtags', []),
            'thumbnail_prompt': youtube_metadata.get('thumbnail_prompt', ''),
            'image_prompts': assembly.get('visual_prompts', {})
        }
        
        success, message, record_id = save_deepdive_to_db(supabase, deepdive_data, status='finalized')
        
        return success, message
        
    except Exception as e:
        return False, f"Failed to save: {str(e)}"


def render_deepdive_finetuner():
    """Fine-tune deep dive prompts"""
    st.markdown("### ⚙️ Fine-Tune Deep Dive Prompts")
    
    ft_type = st.session_state.get('deepdive_finetune_type', 'research')
    
    st.info(f"Fine-tuning: **{ft_type}** prompt")
    st.caption("Configure prompt parameters for optimal results")
    
    if st.button("❌ Exit Fine-Tune Mode", type="secondary"):
        st.session_state['deepdive_finetune_mode'] = False
        st.rerun()