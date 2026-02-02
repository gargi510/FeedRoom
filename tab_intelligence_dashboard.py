"""
Tab 3: Intelligence Dashboard (The FeedRoom)
Combined: Parsed Intelligence + Analytics Visualizations + Script Generation + Audio + Raw Tables
"""
import streamlit as st
import pandas as pd
from datetime import date
from prompts import get_assembly_prompt_india, get_assembly_prompt_usa
from utils import parse_json_input


def render_intelligence_dashboard_tab(gemini_pro, gemini_flash, supabase):
    """Main dashboard - intelligence + analytics + production tools"""
    
    st.header("📊 Intelligence Dashboard")
    st.caption("**The FeedRoom Production Hub - Complete Intelligence & Production**")
    
    if 'google_data' not in st.session_state or 'twitter_data' not in st.session_state:
        st.info("📥 Collect data first")
        return
    
    if st.session_state.get('dashboard_finetune_mode', False):
        render_dashboard_finetuner()
        return
    
    st.divider()
    
    # SECTION 1: Parsed Intelligence Summary
    render_parsed_intelligence_section()
    
    st.divider()
    
    # SECTION 2: Analytics (copy from tab_analytics.py - word clouds, charts, etc.)
    render_analytics_section()
    
    st.divider()
    
    # SECTION 3: Script Generation + Audio
    render_script_production_section(gemini_pro, gemini_flash, supabase)
    
    st.divider()
    
    # SECTION 4: Raw Data Tables (collapsed)
    render_raw_data_tables()


def render_parsed_intelligence_section():
    """Display intelligence grids from Tab 2"""
    st.markdown("### 📊 Intelligence Grid Summary")
    
    if 'intelligence_India' not in st.session_state:
        st.warning("⚠️ Generate intelligence in **Intelligence Analysis** tab first")
        return
    
    if 'executive_summary' in st.session_state:
        st.info(f"**Summary:** {st.session_state['executive_summary']}")
    
    col_india, col_usa = st.columns(2)
    
    with col_india:
        st.markdown("#### 🇮🇳 India")
        intel = st.session_state.get('intelligence_India', {})
        for theme in intel.get('weather_grid', []):
            st.markdown(f"**{theme.get('slot')}. {theme.get('theme')}**")
            st.caption(f"💡 {theme.get('big_question', '')}")
        st.markdown("**🚨 Anomalies:**")
        for a in intel.get('anomalies', []):
            st.caption(f"• {a.get('keyword')}")
    
    with col_usa:
        st.markdown("#### 🇺🇸 USA")
        intel = st.session_state.get('intelligence_USA', {})
        for theme in intel.get('weather_grid', []):
            st.markdown(f"**{theme.get('slot')}. {theme.get('theme')}**")
            st.caption(f"💡 {theme.get('big_question', '')}")
        st.markdown("**🚨 Anomalies:**")
        for a in intel.get('anomalies', []):
            st.caption(f"• {a.get('keyword')}")


def render_analytics_section():
    """Analytics visualizations - COPY FROM tab_analytics.py"""
    st.markdown("### 📈 Analytics Dashboard")
    st.info("💡 **Note:** Copy all analytics functions from tab_analytics.py here (word clouds, charts, cross-platform analysis, etc.)")
    
    # You should copy these functions from the uploaded tab_analytics.py:
    # - create_regional_insight_cards()
    # - create_cross_platform_analysis()
    # - create_category_wordclouds_section()
    # - create_velocity_breakdown_chart()
    # - create_sentiment_breakdown_chart()
    # etc.
    
    st.caption("Placeholder - implement analytics from tab_analytics.py")


def render_script_production_section(gemini_pro, gemini_flash, supabase):
    """Script generation + audio + DB push"""
    st.markdown("### 🎬 Script Generation & Production")
    
    # Region selector
    selected_region = st.selectbox("Select Region:", ["", "India", "USA"], key='script_region')
    
    if not selected_region:
        st.info("👆 Select a region to generate script")
        return
    
    intelligence = st.session_state.get(f'intelligence_{selected_region}', {})
    
    if not intelligence:
        st.error(f"❌ No intelligence for {selected_region}. Generate in Tab 2 first.")
        return
    
    col_auto, col_manual, col_finetune = st.columns(3)
    
    with col_auto:
        if st.button("🤖 Generate Script", type="primary", use_container_width=True, key=f'gen_{selected_region}'):
            with st.spinner("🎬 Generating script..."):
                try:
                    prod_mood = intelligence.get('production_mood', {})
                    prompt_func = get_assembly_prompt_india if selected_region == 'India' else get_assembly_prompt_usa
                    prompt = prompt_func(intelligence, prod_mood)
                    response = gemini_pro.generate_content(prompt)
                    assembly = parse_json_input(response.text)
                    
                    if assembly:
                        st.session_state[f'assembly_{selected_region}'] = assembly
                        script = assembly.get('script_assembly', {})
                        full_script = f"{script.get('intro', '')}\n\n{script.get('segment_1', '')}\n\n{script.get('segment_2', '')}\n\n{script.get('outlier', '')}\n\n{script.get('outro', '')}"
                        st.session_state[f'script_full_{selected_region}'] = full_script
                        st.success("✅ Script generated!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ {str(e)}")
    
    with col_manual:
        if st.button("📋 Manual", use_container_width=True, key=f'man_{selected_region}'):
            prod_mood = intelligence.get('production_mood', {})
            prompt_func = get_assembly_prompt_india if selected_region == 'India' else get_assembly_prompt_usa
            st.session_state[f'manual_prompt_{selected_region}'] = prompt_func(intelligence, prod_mood)
        
        if f'manual_prompt_{selected_region}' in st.session_state:
            st.text_area("Prompt:", st.session_state[f'manual_prompt_{selected_region}'], height=80, key=f'p_{selected_region}')
            
            manual_json = st.text_area("Paste JSON:", height=80, key=f'j_{selected_region}')
            
            if st.button("Parse", key=f'parse_{selected_region}'):
                assembly = parse_json_input(manual_json)
                if assembly:
                    st.session_state[f'assembly_{selected_region}'] = assembly
                    script = assembly.get('script_assembly', {})
                    full_script = f"{script.get('intro', '')}\n\n{script.get('segment_1', '')}\n\n{script.get('segment_2', '')}\n\n{script.get('outlier', '')}\n\n{script.get('outro', '')}"
                    st.session_state[f'script_full_{selected_region}'] = full_script
                    st.rerun()
    
    with col_finetune:
        if st.button("⚙️ Fine-Tune", type="secondary", use_container_width=True, key=f'ft_{selected_region}'):
            st.session_state['dashboard_finetune_mode'] = True
            st.session_state['finetune_region'] = selected_region
            st.rerun()
    
    # Display script editor
    if f'assembly_{selected_region}' in st.session_state:
        st.divider()
        display_script_editor(selected_region, supabase)


def display_script_editor(region, supabase):
    """Editable script + audio upload"""
    st.markdown("### ✏️ Edit Script")
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("**📝 EDIT:**")
        edited_script = st.text_area(
            "Script:",
            st.session_state[f'script_full_{region}'],
            height=400,
            key=f'edit_{region}',
            label_visibility="collapsed"
        )
        st.session_state[f'script_full_{region}'] = edited_script
    
    with col_right:
        st.markdown("**📄 PREVIEW:**")
        st.markdown(f"""<div style="background:#1a1a1a; padding:20px; border-radius:10px; border-left:4px solid {'#ff9933' if region == 'India' else '#4285f4'}; max-height:400px; overflow-y:auto; font-size:16px; line-height:1.8; color:#f0f0f0;">{edited_script.replace(chr(10), '<br><br>')}</div>""", unsafe_allow_html=True)
        
        word_count = len(edited_script.split())
        st.caption(f"📊 {word_count} words | ⏱️ ~{word_count/150:.1f} min")
    
    st.divider()
    
    # Audio upload
    st.markdown("### 🎙️ Audio Upload")
    uploaded_audio = st.file_uploader(f"Upload voiceover for {region}:", type=['mp3', 'wav', 'm4a'], key=f'audio_{region}')
    
    if uploaded_audio:
        audio_path = f"audio/voiceover_{region.lower()}.mp3"
        import os
        if not os.path.exists('audio'):
            os.makedirs('audio')
        with open(audio_path, 'wb') as f:
            f.write(uploaded_audio.getbuffer())
        st.success(f"✅ Audio saved to {audio_path}")
        st.audio(uploaded_audio)
        st.session_state[f'audio_uploaded_{region}'] = True
    
    st.divider()
    
    # Push to DB
    if st.session_state.get(f'audio_uploaded_{region}', False):
        if st.button(f"💾 Push {region} to Database", type="primary", use_container_width=True):
            if supabase:
                with st.spinner("💾 Saving..."):
                    try:
                        today = date.today().isoformat()
                        intelligence = st.session_state.get(f'intelligence_{region}', {})
                        assembly = st.session_state.get(f'assembly_{region}', {})
                        
                        db_record = {
                            'publish_date': today,
                            f'intelligence_grid_{region.lower()}': intelligence,
                            f'script_assembly_{region.lower()}': assembly.get('script_assembly', {}),
                            f'youtube_metadata_{region.lower()}': assembly.get('youtube_metadata', {}),
                            f'visual_prompts_{region.lower()}': assembly.get('visual_prompts', {}),
                            f'audio_script_{region.lower()}': edited_script
                        }
                        
                        existing = supabase.table('daily_content_records').select('id').eq('publish_date', today).execute()
                        
                        if existing.data:
                            supabase.table('daily_content_records').update(db_record).eq('id', existing.data[0]['id']).execute()
                        else:
                            supabase.table('daily_content_records').insert(db_record).execute()
                        
                        st.success(f"✅ {region} data saved to database!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
            else:
                st.error("❌ Supabase not configured")


def render_raw_data_tables():
    """Collapsed raw data tables"""
    st.markdown("### 📋 Raw Data Tables")
    
    tab_g, tab_t = st.tabs(["🔍 Google Trends", "🐦 Twitter Trends"])
    
    with tab_g:
        google_df = pd.DataFrame(st.session_state.get('google_data', []))
        if len(google_df) > 0:
            st.dataframe(google_df, use_container_width=True, height=400)
        else:
            st.info("No Google data")
    
    with tab_t:
        twitter_df = pd.DataFrame(st.session_state.get('twitter_data', []))
        if len(twitter_df) > 0:
            st.dataframe(twitter_df, use_container_width=True, height=400)
        else:
            st.info("No Twitter data")


def render_dashboard_finetuner():
    """Fine-tune assembly prompts"""
    st.markdown("### ⚙️ Fine-Tune Script Prompt")
    
    region = st.session_state.get('finetune_region', 'India')
    
    st.info(f"Fine-tuning prompt for: **{region}**")
    st.caption("Copy editable sections from old tab_ai_insights.py finetune_assembly_prompt() function")
    
    # Placeholder - copy from old file
    st.warning("💡 Implement fine-tuner sections from old tab_ai_insights.py")
    
    if st.button("❌ Exit", type="secondary"):
        st.session_state['dashboard_finetune_mode'] = False
        st.rerun()