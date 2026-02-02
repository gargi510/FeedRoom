"""
The FeedRoom - Production Application
Restructured for deployment with 5 main tabs
"""
import streamlit as st
import os
from datetime import date

# Page config
st.set_page_config(
    page_title="The FeedRoom - Trend Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.google_data = []
    st.session_state.twitter_data = []

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize API clients
def init_clients():
    """Initialize all API clients"""
    # Gemini
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    gemini_pro = None
    gemini_flash = None
    
    if gemini_api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_api_key)
            gemini_pro = genai.GenerativeModel('gemini-1.5-pro-latest')
            gemini_flash = genai.GenerativeModel('gemini-1.5-flash-latest')
        except Exception as e:
            st.sidebar.error(f"Gemini initialization failed: {str(e)}")
    
    # SerpAPI
    serpapi_key = os.getenv('SERPAPI_KEY')
    
    # Supabase
    supabase = None
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if supabase_url and supabase_key:
        try:
            from supabase import create_client
            supabase = create_client(supabase_url, supabase_key)
        except Exception as e:
            st.sidebar.error(f"Supabase initialization failed: {str(e)}")
    
    return gemini_pro, gemini_flash, serpapi_key, supabase

# Sidebar
with st.sidebar:
    st.title("📊 The FeedRoom")
    st.caption("Trend Intelligence Platform")
    st.divider()
    
    # API Status
    st.markdown("### 🔌 API Status")
    
    gemini_status = "✅" if os.getenv('GEMINI_API_KEY') else "❌"
    serpapi_status = "✅" if os.getenv('SERPAPI_KEY') else "❌"
    supabase_status = "✅" if (os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_KEY')) else "❌"
    
    st.caption(f"{gemini_status} Gemini API")
    st.caption(f"{serpapi_status} SerpAPI")
    st.caption(f"{supabase_status} Supabase")
    
    st.divider()
    
    # Date
    st.caption(f"📅 {date.today().strftime('%B %d, %Y')}")

# Initialize clients
gemini_pro, gemini_flash, serpapi_key, supabase = init_clients()

# Main app header
st.title("📊 The FeedRoom - Trend Intelligence Platform")
st.caption("**Daily Intelligence Pipeline: Collect → Analyze → Produce**")
st.divider()

# Tab structure
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📥 Data Collection",
    "🧠 Intelligence Analysis", 
    "📊 Intelligence Dashboard",
    "🔬 Deep Dive Research",
    "📈 Weekly Insights"
])

# TAB 1: Data Collection
with tab1:
    from tab_collection import render_collection_tab
    render_collection_tab(serpapi_key, gemini_flash, supabase)

# TAB 2: Intelligence Analysis (Phase 0)
with tab2:
    from tab_intelligence_analysis import render_intelligence_analysis_tab
    render_intelligence_analysis_tab(gemini_pro, gemini_flash)

# TAB 3: Intelligence Dashboard (Combined analytics + production)
with tab3:
    from tab_intelligence_dashboard import render_intelligence_dashboard_tab
    render_intelligence_dashboard_tab(gemini_pro, gemini_flash, supabase)

# TAB 4: Deep Dive Research
with tab4:
    from tab_deepdive_research import render_deepdive_research_tab
    render_deepdive_research_tab(gemini_pro, gemini_flash, supabase)

# TAB 5: Weekly Insights
with tab5:
    from tab_weekly_insights import render_weekly_insights_tab
    render_weekly_insights_tab(supabase)

# Footer
st.divider()
st.caption("The FeedRoom v2.0 - Production | Powered by Gemini, SerpAPI, Supabase")