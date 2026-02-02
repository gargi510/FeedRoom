"""
Tab 4: Deep Dive Research (The FeedRoom)
Strategic Clash Research + Script Generation + Audio (NO MoviePy)
"""
import streamlit as st
import pandas as pd
import os
from datetime import date
from prompts import get_deepdive_research_prompt, get_deepdive_script_prompt
from utils import parse_json_input


def render_deepdive_research_tab(gemini_pro, gemini_flash, supabase):
    """Main deep dive tab"""
    
    st.header("🔬 Deep Dive Research")
    st.caption("**The FeedRoom Strategic Clash Analysis**")
    
    if 'google_data' not in st.session_state or 'twitter_data' not in st.session_state:
        st.info("📥 Collect data first")
        return
    
    if st.session_state.get('deepdive_finetune_mode', False):
        render_deepdive_finetuner()
        return
    
    st.divider()
    
    # Keyword selector
    render_keyword_selector_dropdown()
    
    if 'deepdive_keyword' not in st.session_state:
        return
    
    st.divider()
    
    # Phase navigation
    phase = st.session_state.get('deepdive_phase', 1)
    
    phase_cols = st.columns(3)
    phases = [(1, "Research"), (2, "Script"), (3, "Audio")]
    
    for idx, (phase_num, phase_name) in enumerate(phases):
        with phase_cols[idx]:
            if phase >= phase_num:
                st.success(f"✅ {phase_num}: {phase_name}")
            else:
                st.info(f"⏳ {phase_num}: {phase_name}")
    
    st.divider()
    
    # Render phase
    if phase == 1:
        render_phase1_research(gemini_pro, gemini_flash)
    elif phase == 2:
        render_phase2_script(gemini_pro, gemini_flash)
    elif phase == 3:
        render_phase3_audio(supabase)


def render_keyword_selector_dropdown():
    """Dropdown selector: Region → Platform → Keyword"""
    st.markdown("### 🎯 Select Keyword for Deep Dive")
    
    google_df = pd.DataFrame(st.session_state.get('google_data', []))
    twitter_df = pd.DataFrame(st.session_state.get('twitter_data', []))
    
    google_df['platform'] = 'Google Trends'
    twitter_df['platform'] = 'Twitter/X'
    
    combined_df = pd.concat([google_df, twitter_df], ignore_index=True)
    
    if len(combined_df) == 0:
        st.warning("No data")
        return
    
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
    
    # Display metadata
    st.markdown("### 📋 Selected Keyword")
    
    col_meta1, col_meta2 = st.columns(2)
    
    with col_meta1:
        st.markdown(f"""<div style="background:linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); padding:20px; border-radius:12px; color:white;"><h3 style="margin:0;">🎯 {selected_keyword}</h3></div>""", unsafe_allow_html=True)
        st.markdown(f"**🌍 Region:** {selected_region}")
        st.markdown(f"**📱 Platform:** {selected_platform}")
        st.markdown(f"**📂 Category:** {keyword_row.get('category', 'N/A')}")
    
    with col_meta2:
        volume = keyword_row.get(vol_col, 0) if vol_col else 0
        st.markdown(f"""<div style="background:linear-gradient(135deg, #10b981 0%, #059669 100%); padding:20px; border-radius:12px; color:white;"><h3 style="margin:0;">📊 {volume:,}</h3></div>""", unsafe_allow_html=True)
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
            'sentiment': keyword_row.get('public_sentiment', keyword_row.get('primary_sentiment', 'curious'))
        }
        st.session_state['deepdive_phase'] = 1
        st.rerun()


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
                    prompt = get_deepdive_research_prompt(kw['keyword'], kw['region'], kw.get('context', ''), kw.get('why_trending', ''), kw.get('volume', 0), kw.get('velocity', 'steady'), kw.get('sentiment', 'curious'))
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
            prompt = get_deepdive_research_prompt(kw['keyword'], kw['region'], kw.get('context', ''), kw.get('why_trending', ''), kw.get('volume', 0), kw.get('velocity', 'steady'), kw.get('sentiment', 'curious'))
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
    
    # Display research
    if 'deepdive_research' in st.session_state:
        st.divider()
        display_research_summary(st.session_state['deepdive_research'])
        
        st.divider()
        
        if st.button("✅ Proceed to Script", type="primary", use_container_width=True):
            st.session_state['deepdive_phase'] = 2
            st.rerun()


def parse_deepdive_research(research_json):
    """Parse research JSON with strategic_clash structure"""
    try:
        data = parse_json_input(research_json)
        
        if not data:
            return None, "Failed to parse JSON"
        
        required = ['keyword', 'simple_clash', 'lead_metric', 'strategic_clash', 'sources']
        missing = [f for f in required if f not in data]
        if missing:
            return None, f"Missing: {', '.join(missing)}"
        
        clash = data.get('strategic_clash', {})
        if not isinstance(clash, dict):
            return None, "'strategic_clash' must be object"
        
        required_clash = ['side_a_logic', 'side_b_fear', 'the_deep_why']
        missing_clash = [f for f in required_clash if f not in clash]
        if missing_clash:
            return None, f"Missing in strategic_clash: {', '.join(missing_clash)}"
        
        return data, None
    except Exception as e:
        return None, f"Parse error: {str(e)}"


def display_research_summary(research):
    """Display strategic clash research"""
    st.markdown("### 📊 Research Summary")
    
    # Lead Metric
    st.markdown(f"""<div style="background:linear-gradient(135deg, #f59e0b 0%, #ef4444 100%); padding:30px; border-radius:15px; color:white; text-align:center; margin:20px 0;"><h2 style="margin:0;">📊 LEAD METRIC</h2><h1 style="font-size:48px; margin:20px 0;">{research.get('lead_metric', 'N/A')}</h1></div>""", unsafe_allow_html=True)
    
    st.info(f"**🎯 Simple Clash:** {research.get('simple_clash', 'N/A')}")
    
    if 'visual_concept' in research:
        st.success(f"🎬 **Visual:** {research['visual_concept']}")
    
    st.divider()
    
    # Strategic Clash
    st.markdown("### ⚔️ The Strategic Clash")
    
    clash = research.get('strategic_clash', {})
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.markdown("#### ✅ Side A: New Logic")
        st.markdown(f"""<div style="background:linear-gradient(135deg, #10b981 0%, #059669 100%); padding:20px; border-radius:10px; color:white; min-height:150px;"><p style="font-size:15px; line-height:1.6;">{clash.get('side_a_logic', 'N/A')}</p></div>""", unsafe_allow_html=True)
    
    with col_b:
        st.markdown("#### ⚠️ Side B: Traditional Fear")
        st.markdown(f"""<div style="background:linear-gradient(135deg, #ef4444 0%, #dc2626 100%); padding:20px; border-radius:10px; color:white; min-height:150px;"><p style="font-size:15px; line-height:1.6;">{clash.get('side_b_fear', 'N/A')}</p></div>""", unsafe_allow_html=True)
    
    st.markdown("#### 🔑 The Secret Sauce")
    st.markdown(f"""<div style="background:linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); padding:25px; border-radius:10px; color:white;"><p style="font-size:17px; line-height:1.7;">{clash.get('the_deep_why', 'N/A')}</p></div>""", unsafe_allow_html=True)
    
    # Sources
    sources = research.get('sources', [])
    if sources:
        with st.expander("📚 Sources", expanded=False):
            for idx, src in enumerate(sources, 1):
                st.markdown(f"**{idx}. [{src.get('title', 'Source')}]({src.get('url', '#')})** - Reliability: {src.get('reliability', 'N/A')}")


def render_phase2_script(gemini_pro, gemini_flash):
    """Phase 2: Script generation"""
    st.markdown("### 🎬 Phase 2: Script Generation")
    
    research = st.session_state.get('deepdive_research', {})
    kw = st.session_state.get('deepdive_keyword', {})
    
    if not research:
        st.error("❌ No research. Return to Phase 1.")
        if st.button("⬅️ Back"):
            st.session_state['deepdive_phase'] = 1
            st.rerun()
        return
    
    col_auto, col_manual, col_ft = st.columns(3)
    
    with col_auto:
        if st.button("🚀 Generate Script", type="primary", use_container_width=True):
            with st.spinner("📝 Generating..."):
                try:
                    prompt = get_deepdive_script_prompt(research, kw['keyword'], kw['region'])
                    response = gemini_pro.generate_content(prompt)
                    assembly = parse_json_input(response.text)
                    
                    if assembly and 'assembly_logic' in assembly:
                        st.session_state['deepdive_assembly'] = assembly
                        logic = assembly.get('assembly_logic', {})
                        st.session_state['deepdive_script'] = logic.get('audio_script', '')
                        st.success("✅ Script generated!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid structure")
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
                if assembly and 'assembly_logic' in assembly:
                    st.session_state['deepdive_assembly'] = assembly
                    logic = assembly.get('assembly_logic', {})
                    st.session_state['deepdive_script'] = logic.get('audio_script', '')
                    st.rerun()
                else:
                    st.error("❌ Invalid structure")
    
    with col_ft:
        if st.button("⚙️ Fine-Tune", type="secondary", use_container_width=True):
            st.session_state['deepdive_finetune_mode'] = True
            st.session_state['deepdive_finetune_type'] = 'script'
            st.rerun()
    
    # Display editor
    if 'deepdive_assembly' in st.session_state:
        st.divider()
        display_script_editor()


def display_script_editor():
    """Script editor"""
    st.markdown("### ✏️ Edit Script")
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("**📝 EDIT:**")
        if 'deepdive_script' not in st.session_state:
            logic = st.session_state['deepdive_assembly'].get('assembly_logic', {})
            st.session_state['deepdive_script'] = logic.get('audio_script', '')
        
        edited = st.text_area("Script:", st.session_state['deepdive_script'], height=400, key='dd_edit', label_visibility="collapsed")
        st.session_state['deepdive_script'] = edited
    
    with col_right:
        st.markdown("**📄 PREVIEW:**")
        st.markdown(f"""<div style="background:#1a1a1a; padding:20px; border-radius:10px; border-left:4px solid #8b5cf6; max-height:400px; overflow-y:auto; font-size:16px; line-height:1.8; color:#f0f0f0;">{edited.replace(chr(10), '<br><br>')}</div>""", unsafe_allow_html=True)
        
        wc = len(edited.split())
        color = "#10b981" if 120 <= wc <= 135 else "#f59e0b" if 110 <= wc <= 145 else "#ef4444"
        status = "✅ Perfect" if 120 <= wc <= 135 else "⚠️ Close" if 110 <= wc <= 145 else "❌ Revise"
        
        st.markdown(f"""<div style="background:{color}; padding:10px; border-radius:8px; color:white; text-align:center; margin-top:10px;"><strong>{status}</strong> | {wc} words | ⏱️ ~{wc/150:.1f} min</div>""", unsafe_allow_html=True)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Back to Research", type="secondary", use_container_width=True):
            st.session_state['deepdive_phase'] = 1
            st.rerun()
    
    with col2:
        if st.button("✅ Proceed to Audio", type="primary", use_container_width=True):
            st.session_state['deepdive_phase'] = 3
            st.rerun()


def render_phase3_audio(supabase):
    """Phase 3: Audio upload + DB save"""
    st.markdown("### 🎙️ Phase 3: Audio Upload")
    
    if 'deepdive_script' in st.session_state:
        with st.expander("📄 View Script", expanded=True):
            st.markdown(st.session_state['deepdive_script'])
            wc = len(st.session_state['deepdive_script'].split())
            st.caption(f"📊 {wc} words (~{wc/150:.1f} min)")
    
    uploaded = st.file_uploader("Upload audio:", type=['mp3', 'wav', 'm4a'], key='dd_audio')
    
    if uploaded:
        kw = st.session_state['deepdive_keyword']['keyword']
        audio_path = f"images/deepdive_{kw[:20].replace(' ', '_')}_audio.mp3"
        
        if not os.path.exists('images'):
            os.makedirs('images')
        
        with open(audio_path, 'wb') as f:
            f.write(uploaded.getbuffer())
        
        st.success(f"✅ Saved to {audio_path}")
        st.audio(uploaded)
        st.session_state['deepdive_audio_path'] = audio_path
        st.session_state['deepdive_audio_uploaded'] = True
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Back to Script", type="secondary", use_container_width=True):
            st.session_state['deepdive_phase'] = 2
            st.rerun()
    
    with col2:
        if st.session_state.get('deepdive_audio_uploaded', False):
            if st.button("💾 Save to Database", type="primary", use_container_width=True):
                if supabase:
                    with st.spinner("💾 Saving..."):
                        try:
                            kw = st.session_state['deepdive_keyword']
                            research = st.session_state['deepdive_research']
                            assembly = st.session_state['deepdive_assembly']
                            
                            record = {
                                'keyword': kw['keyword'],
                                'region': kw['region'],
                                'platform': kw.get('platform', 'N/A'),
                                'category': kw['category'],
                                'research_data': research,
                                'audio_script': st.session_state.get('deepdive_script', ''),
                                'youtube_metadata': assembly.get('youtube_metadata', {}),
                                'publish_date': date.today().isoformat()
                            }
                            
                            result = supabase.table('deep_dive_research').insert(record).execute()
                            
                            if result.data:
                                st.success("✅ Saved to database!")
                                st.balloons()
                            else:
                                st.error("❌ Save failed")
                        except Exception as e:
                            st.error(f"❌ {str(e)}")
                else:
                    st.error("❌ Supabase not configured")


def render_deepdive_finetuner():
    """Fine-tune deep dive prompts"""
    st.markdown("### ⚙️ Fine-Tune Deep Dive Prompts")
    
    ft_type = st.session_state.get('deepdive_finetune_type', 'research')
    
    st.info(f"Fine-tuning: **{ft_type}** prompt")
    st.caption("💡 Copy sections from old tab_deepdive.py finetune functions")
    
    if st.button("❌ Exit", type="secondary"):
        st.session_state['deepdive_finetune_mode'] = False
        st.rerun()