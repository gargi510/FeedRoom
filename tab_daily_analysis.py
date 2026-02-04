"""
Tab 4: Daily Analysis - PRODUCTION VERSION
Script Generation + Editing + Database Save
"""
import streamlit as st
from datetime import date
from prompts import get_assembly_prompt_india, get_assembly_prompt_usa
from utils import parse_json_input


def render_daily_analysis_tab(gemini_pro, gemini_flash, supabase):
    """Script generation, editing, and database save workflow"""
    st.header("🎬 Daily Analysis - Script Generation")
    st.caption("**Generate scripts, edit, and save to database**")
    
    if 'intelligence_India' not in st.session_state or 'intelligence_USA' not in st.session_state:
        st.warning("⚠️ Generate intelligence in **Intelligence Analysis** tab first")
        return
    
    st.divider()
    
    selected_region = st.selectbox("Select Region:", ["India", "USA"], key='script_region')
    
    intelligence = st.session_state.get(f'intelligence_{selected_region}', {})
    
    if not intelligence:
        st.error(f"❌ No intelligence for {selected_region}. Generate in Intelligence Analysis first.")
        return
    
    st.markdown(f"### 📝 Script Generation for {selected_region}")
    
    col_auto, col_manual = st.columns(2)
    
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
                        full_script = (
                            f"{script.get('intro', '')}\n\n"
                            f"{script.get('segment_1', '')}\n\n"
                            f"{script.get('segment_2', '')}\n\n"
                            f"{script.get('outlier', '')}\n\n"
                            f"{script.get('outro', '')}"
                        )
                        st.session_state[f'script_full_{selected_region}'] = full_script
                        st.session_state[f'parsed_assembly_{selected_region}'] = assembly
                        st.success("✅ Script generated!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ {str(e)}")
    
    with col_manual:
        if st.button("📋 Manual Mode", use_container_width=True, key=f'man_{selected_region}'):
            prod_mood = intelligence.get('production_mood', {})
            prompt_func = get_assembly_prompt_india if selected_region == 'India' else get_assembly_prompt_usa
            st.session_state[f'manual_prompt_{selected_region}'] = prompt_func(intelligence, prod_mood)
        
        if f'manual_prompt_{selected_region}' in st.session_state:
            st.text_area("Prompt:", st.session_state[f'manual_prompt_{selected_region}'], height=80, key=f'p_{selected_region}')
            
            manual_json = st.text_area("Paste JSON:", height=80, key=f'j_{selected_region}')
            
            if st.button("Parse JSON", key=f'parse_{selected_region}'):
                assembly = parse_json_input(manual_json)
                if assembly:
                    st.session_state[f'assembly_{selected_region}'] = assembly
                    script = assembly.get('script_assembly', {})
                    full_script = (
                        f"{script.get('intro', '')}\n\n"
                        f"{script.get('segment_1', '')}\n\n"
                        f"{script.get('segment_2', '')}\n\n"
                        f"{script.get('outlier', '')}\n\n"
                        f"{script.get('outro', '')}"
                    )
                    st.session_state[f'script_full_{selected_region}'] = full_script
                    st.session_state[f'parsed_assembly_{selected_region}'] = assembly
                    st.success("✅ Parsed successfully!")
                    st.rerun()
    
    if f'parsed_assembly_{selected_region}' in st.session_state:
        st.divider()
        display_parsed_assembly(selected_region)
    
    if f'assembly_{selected_region}' in st.session_state:
        st.divider()
        display_script_editor(selected_region, supabase)


def display_parsed_assembly(region):
    """Display parsed JSON assembly details"""
    st.markdown("### 📊 Parsed Assembly Details")
    
    assembly = st.session_state.get(f'parsed_assembly_{region}', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📝 Script Assembly")
        script = assembly.get('script_assembly', {})
        with st.expander("View Script Segments", expanded=True):
            st.markdown(f"**Intro:** {script.get('intro', 'N/A')}")
            st.markdown(f"**Segment 1:** {script.get('segment_1', 'N/A')}")
            st.markdown(f"**Segment 2:** {script.get('segment_2', 'N/A')}")
            st.markdown(f"**Outlier:** {script.get('outlier', 'N/A')}")
            st.markdown(f"**Outro:** {script.get('outro', 'N/A')}")
        
        st.markdown("#### 🎨 Visual Prompts")
        visuals = assembly.get('visual_prompts', {})
        with st.expander("View Visual Prompts", expanded=False):
            for key, value in visuals.items():
                st.caption(f"**{key}:** {value}")
    
    with col2:
        st.markdown("#### 📺 YouTube Metadata")
        metadata = assembly.get('youtube_metadata', {})
        with st.expander("View Metadata", expanded=True):
            st.markdown(f"**Title:** {metadata.get('title', 'N/A')}")
            st.markdown(f"**Description:** {metadata.get('description', 'N/A')}")
            st.markdown(f"**Hook:** {metadata.get('hook', 'N/A')}")
            st.markdown(f"**Hashtags:** {', '.join(metadata.get('hashtags', []))}")
            if 'thumbnail_prompt' in metadata:
                st.markdown(f"**Thumbnail Prompt:** {metadata.get('thumbnail_prompt', 'N/A')}")


def display_script_editor(region, supabase):
    """Editable script with preview and database save"""
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
        region_color = '#ff9933' if region == 'India' else '#4285f4'
        st.markdown(
            f"""<div style="background:#1a1a1a; padding:20px; border-radius:10px; 
            border-left:4px solid {region_color}; max-height:400px; overflow-y:auto; 
            font-size:16px; line-height:1.8; color:#f0f0f0;">
            {edited_script.replace(chr(10), '<br><br>')}</div>""",
            unsafe_allow_html=True
        )
        
        word_count = len(edited_script.split())
        st.caption(f"📊 {word_count} words | ⏱️ ~{word_count/150:.1f} min")
    
    st.divider()
    
    st.markdown("### 💾 Save Script to Database")
    st.caption(f"Save {region} script and metadata to daily_content_records")
    
    if st.button(f"💾 Save {region} Script to Database", type="primary", use_container_width=True):
        if supabase:
            with st.spinner("💾 Saving to database..."):
                try:
                    today = date.today().isoformat()
                    intelligence = st.session_state.get(f'intelligence_{region}', {})
                    assembly = st.session_state.get(f'assembly_{region}', {})
                    
                    from db_operations import save_regional_script_to_db
                    
                    script_data = {
                        'script_full': edited_script,
                        'intelligence': intelligence,
                        'assembly': assembly
                    }
                    
                    success, message, record_id = save_regional_script_to_db(
                        supabase, region, script_data, today
                    )
                    
                    if success:
                        st.success(message)
                        st.balloons()
                        st.session_state[f'script_saved_{region}'] = True
                    else:
                        st.error(message)
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.error("❌ Supabase not configured")