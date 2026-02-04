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

# NOTE: python-dotenv and load_dotenv() are removed as we now use st.secrets

# Initialize API clients
def init_clients():
    """Initialize all API clients using st.secrets"""
    # Gemini
    # Accessing st.secrets safely with .get() to avoid KeyErrors
    gemini_api_key = st.secrets.get('GEMINI_API_KEY')
    gemini_pro = None
    gemini_flash = None
    
    if gemini_api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_api_key)
            gemini_flash = genai.GenerativeModel('gemini-3-flash-preview')
            gemini_pro = genai.GenerativeModel('gemini-3-pro-preview')
        except Exception as e:
            st.sidebar.error(f"Gemini initialization failed: {str(e)}")
    
    # SerpAPI
    serpapi_key = st.secrets.get('SERPAPI_KEY')
    
    # Supabase
    supabase = None
    supabase_url = st.secrets.get('SUPABASE_URL')
    supabase_key = st.secrets.get('SUPABASE_KEY')
    
    if supabase_url and supabase_key:
        try:
            from supabase import create_client
            # .strip() prevents common "Invalid URL" errors from hidden spaces in TOML
            supabase = create_client(supabase_url.strip(), supabase_key.strip())
        except Exception as e:
            st.sidebar.error(f"Supabase initialization failed: {str(e)}")
    
    return gemini_pro, gemini_flash, serpapi_key, supabase

with st.sidebar:
    st.title("📊 The FeedRoom")
    st.caption("Trend Intelligence Platform")
    st.divider()
    
    st.markdown("### 🔌 API Status")
    
    gemini_status = "✅" if "GEMINI_API_KEY" in st.secrets else "❌"
    serpapi_status = "✅" if "SERPAPI_KEY" in st.secrets else "❌"
    supabase_status = "✅" if ("SUPABASE_URL" in st.secrets and "SUPABASE_KEY" in st.secrets) else "❌"
    
    st.caption(f"{gemini_status} Gemini API")
    st.caption(f"{serpapi_status} SerpAPI")
    st.caption(f"{supabase_status} Supabase")
    
    st.divider()
    
    st.caption(f"📅 {date.today().strftime('%B %d, %Y')}")

gemini_pro, gemini_flash, serpapi_key, supabase = init_clients()

st.title("📊 The FeedRoom - Trend Intelligence Platform")
st.caption("**Daily Intelligence Pipeline: Collect → Analyze → Dashboard → Scripts → Deep Dive**")
st.divider()

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📥 Data Collection",
    "🧠 Intelligence Analysis", 
    "📊 Intelligence Dashboard",
    "🇮🇳 India Dashboard",
    "🎬 Daily Analysis",
    "🔬 Deep Dive Research",
    "📈 Weekly Insights"
])

with tab1:
    from tab_collection import render_collection_tab
    render_collection_tab(serpapi_key, gemini_flash, supabase)

with tab2:
    from tab_intelligence_analysis import render_intelligence_analysis_tab
    render_intelligence_analysis_tab(gemini_pro, gemini_flash, supabase)

with tab3:
    from tab_intelligence_dashboard import render_intelligence_dashboard_tab
    render_intelligence_dashboard_tab(gemini_pro, gemini_flash, supabase)

with tab4: 
    from tab_india_dashboard import render_india_intelligence_dashboard
    render_india_intelligence_dashboard(supabase)
    
with tab5:
    from tab_daily_analysis import render_daily_analysis_tab
    render_daily_analysis_tab(gemini_pro, gemini_flash, supabase)

with tab6:
    from tab_deepdive_research import render_deepdive_research_tab
    render_deepdive_research_tab(gemini_pro, gemini_flash, supabase)

with tab7:
    from tab_weekly_insights import render_weekly_insights_tab
    render_weekly_insights_tab(supabase)

st.divider()
st.caption("The FeedRoom v2.1 - Production | Powered by Gemini, SerpAPI, Supabase")
