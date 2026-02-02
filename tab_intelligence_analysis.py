"""
Tab 2: Intelligence Analysis - Phase 0 Only (The FeedRoom)
Features:
- Generate intelligence grids for BOTH regions (India + USA)
- Display side-by-side with full details
- Fine-tune analysis prompts
- Executive summary
- NO script generation (moved to Tab 3)
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from prompts import get_analysis_prompt
from utils import parse_json_input


def prepare_data_summary():
    """Prepare data summary for AI analysis"""
    google_df = pd.DataFrame(st.session_state.get('google_data', []))
    twitter_df = pd.DataFrame(st.session_state.get('twitter_data', []))
    
    if google_df.empty or twitter_df.empty:
        return {}

    usa_google = google_df[google_df['region'] == 'USA'].nlargest(10, 'search_volume')
    india_google = google_df[google_df['region'] == 'India'].nlargest(10, 'search_volume')
    usa_twitter = twitter_df[twitter_df['region'] == 'USA'].nlargest(10, 'mention_volume')
    india_twitter = twitter_df[twitter_df['region'] == 'India'].nlargest(10, 'mention_volume')
    
    combined = pd.concat([google_df, twitter_df])
    breakouts = combined[combined['velocity'].str.lower().isin(['breakout', 'spike'])]
    
    usa_breakouts = breakouts[breakouts['region'] == 'USA']['keyword'].tolist()[:5]
    india_breakouts = breakouts[breakouts['region'] == 'India']['keyword'].tolist()[:5]
    
    summary = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'usa_google_summary': f"Top 10: {usa_google['keyword'].tolist()}",
        'india_google_summary': f"Top 10: {india_google['keyword'].tolist()}",
        'usa_twitter_summary': f"Top 10: {usa_twitter['keyword'].tolist()}",
        'india_twitter_summary': f"Top 10: {india_twitter['keyword'].tolist()}",
        'breakout_trends': f"USA: {usa_breakouts}, India: {india_breakouts}",
    }
    
    return summary


def render_intelligence_analysis_tab(gemini_pro, gemini_flash):
    """Main render function for Intelligence Analysis tab"""
    
    st.header("🧠 Intelligence Analysis")
    st.caption("**The FeedRoom Intelligence Grid - Powered by Gemini**")
    
    # Check data availability
    if 'google_data' not in st.session_state or 'twitter_data' not in st.session_state:
        st.info("📥 Collect data in **Data Collection** tab first")
        return
    
    # Check if we're in fine-tune mode
    if st.session_state.get('finetune_mode', False):
        render_prompt_finetuner()
        return
    
    st.divider()
    
    # Phase 0: Combined analysis for both regions
    render_phase0_combined_analysis(gemini_pro, gemini_flash)


def render_phase0_combined_analysis(gemini_pro, gemini_flash):
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
                    prompt = get_analysis_prompt(data_summary)
                    model = gemini_flash if "Flash" in model_choice else gemini_pro
                    response = model.generate_content(prompt)
                    data = parse_json_input(response.text)
                    
                    if data and 'india_intelligence' in data and 'usa_intelligence' in data:
                        st.session_state['intelligence_India'] = data['india_intelligence']
                        st.session_state['intelligence_USA'] = data['usa_intelligence']
                        st.session_state['executive_summary'] = data.get('executive_summary', '')
                        st.success("✅ Intelligence Generated for Both Regions!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid response structure. Expected 'india_intelligence' and 'usa_intelligence'")
                except Exception as e:
                    st.error(f"❌ {str(e)}")
    
    with col_manual:
        st.warning("📋 **Manual Mode**")
        if st.button("1️⃣ Generate Prompt", use_container_width=True, key='generate_prompt_btn'):
            st.session_state['manual_prompt'] = get_analysis_prompt(prepare_data_summary())
        
        if 'manual_prompt' in st.session_state:
            st.text_area("Copy to Gemini:", st.session_state['manual_prompt'], height=80, key='prompt_display')
        
        manual_json = st.text_area("2️⃣ Paste JSON:", height=80, key='manual_json')

        if st.button("3️⃣ Parse & Save", use_container_width=True, key='parse'):
            data = parse_json_input(manual_json)
            if data and 'india_intelligence' in data and 'usa_intelligence' in data:
                st.session_state['intelligence_India'] = data['india_intelligence']
                st.session_state['intelligence_USA'] = data['usa_intelligence']
                st.session_state['executive_summary'] = data.get('executive_summary', '')
                st.rerun()
            else:
                st.error("❌ Invalid JSON. Expected 'india_intelligence' and 'usa_intelligence'")

    # Display intelligence if exists - SIDE BY SIDE with FULL DETAILS
    if 'intelligence_India' in st.session_state and 'intelligence_USA' in st.session_state:
        st.divider()
        st.markdown("### 📊 Intelligence Grid Analysis")
        
        # Executive Summary
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
        
        # Fine-tune button
        col_finetune = st.columns([2, 1])[1]
        with col_finetune:
            if st.button("⚙️ Fine-Tune Prompt", type="secondary", use_container_width=True):
                st.session_state['finetune_mode'] = True
                st.session_state['finetune_type'] = 'analysis'
                st.rerun()


def display_intelligence_full(intelligence, region):
    """Display intelligence grid with FULL DETAILS"""
    
    # Weather Grid (2 themes as per new logic)
    st.markdown("**📌 Weather Grid (Themes)**")
    for theme in intelligence.get('weather_grid', []):
        with st.expander(f"Slot {theme.get('slot')}: {theme.get('theme', 'N/A')}", expanded=True):
            st.markdown(f"**Category:** {theme.get('category')}")
            st.markdown(f"**Keywords:** {', '.join(theme.get('keywords', []))}")
            st.markdown(f"**Mood:** {theme.get('mood')}")
            st.markdown(f"**Data Signal:** {theme.get('data_signal')}")
            st.info(f"**Context:** {theme.get('context', '')}")
            st.success(f"**Deep Why:** {theme.get('deep_why', '')}")
            st.warning(f"**Big Question:** {theme.get('big_question', '')}")
            st.code(f"Chart Type: {theme.get('chart_requirement')}")
    
    # Anomalies (2 anomalies per region)
    st.markdown("**🚨 Anomalies**")
    for anomaly in intelligence.get('anomalies', []):
        with st.expander(f"Anomaly {anomaly.get('rank')}: {anomaly.get('keyword', 'N/A')}", expanded=True):
            st.markdown(f"**Velocity:** {anomaly.get('velocity')}")
            st.info(f"**Explanation:** {anomaly.get('explanation', '')}")
            st.warning(f"**Big Question:** {anomaly.get('big_question', '')}")
            st.code(f"Chart Type: {anomaly.get('chart_requirement')}")
    
    # Production Mood
    st.markdown("**🎨 Production Mood**")
    prod_mood = intelligence.get('production_mood', {})
    with st.expander("View Production Settings", expanded=False):
        st.markdown(f"**Overall Sentiment:** {prod_mood.get('overall_sentiment', 0)}")
        st.markdown(f"**Vibe Color:** {prod_mood.get('vibe_color_hex', '#000000')}")
        st.markdown(f"**Vocal Tone:** {prod_mood.get('vocal_tone', 'N/A')}")
        st.markdown(f"**Visual Background:** {prod_mood.get('visual_background_prompt', 'N/A')}")


def render_prompt_finetuner():
    """Enhanced fine-tuner with complete sections"""
    
    st.markdown("### ⚙️ Prompt Fine-Tuner")
    st.caption("Edit prompt sections while keeping structure locked")
    
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.markdown("**📖 Current Prompt Structure**")
        st.info("View-only: Shows the structure of the prompt")
        
        with st.expander("View Full Prompt", expanded=False):
            prompt_text = get_analysis_prompt(prepare_data_summary())
            st.code(prompt_text, language='text')
    
    with col_right:
        st.markdown("**✏️ Editable Sections**")
        
        # 1. Identity Block
        st.markdown("**1️⃣ Identity Block**")
        identity = st.text_area(
            "Identity:",
            "You are the Lead Intelligence Analyst for The FeedRoom. Your mission is to synthesize raw data into high-fidelity strategic insights for daily trend reports.",
            height=100,
            key='identity_edit'
        )
        
        # 2. Mission Block
        st.markdown("**2️⃣ Mission Block**")
        mission = st.text_area(
            "Mission:",
            """1. ANALYZE: Review global data to find regional contrasts and cultural ripples.
2. CLUSTER: Group data into EXACTLY 2 major themes per region.
3. DETECT: Identify EXACTLY 2 distinct anomalies per region (low volume, breakout velocity).
4. SYNTHESIZE: For every theme, follow the 'Chain of Logic': Data Signal -> Factual Context -> Deep Why (Psychological/Systemic Reason) -> The Big Question.""",
            height=150,
            key='mission_edit'
        )
        
        # 3. Output Format
        st.markdown("**3️⃣ Output Format**")
        
        st.markdown("**3.1 Executive Summary**")
        exec_summary = st.text_area(
            "Executive Summary Instruction:",
            "2-3 sentences: Compare the Global (USA) vs. Local (India) pulse for today.",
            height=60,
            key='exec_summary_edit'
        )
        
        st.markdown("**3.2 Weather Grid (Per Region)**")
        weather_grid = st.text_area(
            "Weather Grid Instruction:",
            "EXACTLY 2 major themes per region with sharp 3-word titles. Each slot must have: category, theme, keywords, mood, data_signal, context, deep_why, big_question, chart_requirement",
            height=100,
            key='weather_grid_edit'
        )
        
        st.markdown("**3.3 India Intelligence**")
        india_intel = st.text_area(
            "India Intelligence Categories:",
            "Slot 1: PRIMARY (Entertainment/OTT/Culture OR National/Social/Politics), Slot 2: SECONDARY (Sports/Tech/Finance OR remaining major cluster)",
            height=60,
            key='india_intel_edit'
        )
        
        st.markdown("**3.4 USA Intelligence**")
        usa_intel = st.text_area(
            "USA Intelligence Categories:",
            "Slot 1: PRIMARY (Politics/Economics/Tech OR Culture/Lifestyle/Media), Slot 2: SECONDARY (Sports/Science/Global OR remaining major cluster)",
            height=60,
            key='usa_intel_edit'
        )
        
        # 4. Critical Rules
        st.markdown("**4️⃣ Critical Rules**")
        rules = st.text_area(
            "Critical Rules:",
            """- Use ONLY keywords found in the provided data sources.
- Provide EXACTLY 2 themes and 2 anomalies for BOTH India and USA.
- Every slot must be complete; no empty strings or placeholders.
- chart_requirement must specify which chart type to generate
- Return ONLY valid JSON within the markdown block.""",
            height=150,
            key='rules_edit'
        )
        
        st.divider()
        
        if st.button("💾 Save & Update prompts.py", type="primary", use_container_width=True):
            with st.spinner("📝 Updating prompts.py..."):
                try:
                    from prompt_updater import update_analysis_prompt, backup_prompts_file
                    
                    # Create backup first
                    backup_success, backup_msg = backup_prompts_file()
                    if backup_success:
                        st.info(backup_msg)
                    
                    # Update the prompt
                    success, message = update_analysis_prompt(
                        identity=identity,
                        mission=mission,
                        exec_summary=exec_summary,
                        weather_grid=weather_grid,
                        india_intel=india_intel,
                        usa_intel=usa_intel,
                        rules=rules
                    )
                    
                    if success:
                        st.success(message)
                        st.balloons()
                        st.info("🔄 Restart the app to use the updated prompt")
                    else:
                        st.error(message)
                        
                except Exception as e:
                    st.error(f"❌ Update failed: {str(e)}")
                    st.warning("💡 Make sure prompt_updater.py is in the same directory")
    
    # Exit button
    if st.button("❌ Exit Fine-Tuner", type="secondary"):
        st.session_state['finetune_mode'] = False
        st.rerun()