"""
Intelligence Dashboard - Production Grade
Consolidated analytics with complete visualizations and database integration
"""
import streamlit as st
import pandas as pd
from datetime import date
from collections import Counter
import plotly.graph_objects as go
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
from difflib import SequenceMatcher


def fetch_latest_trends_from_db(supabase):
    """Fetch last 10 trends per region from today's latest collection"""
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


def setup_font():
    """Setup font for Hindi/Devanagari support"""
    try:
        font_path = os.path.abspath('fonts/NotoSansDevanagari-VariableFont_wdth,wght.ttf')
        if os.path.exists(font_path):
            from matplotlib import font_manager
            font_manager.fontManager.addfont(font_path)
            prop = font_manager.FontProperties(fname=font_path)
            return font_path
    except Exception:
        pass
    
    possible_fonts = [
        '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        'C:\\Windows\\Fonts\\NotoSans-Regular.ttf',
        'C:\\Windows\\Fonts\\Arial.ttf',
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
    ]
    
    for font in possible_fonts:
        if os.path.exists(font):
            return font
    
    return None


def fuzzy_match(str1, str2, threshold=0.8):
    """Check if two strings are similar using fuzzy matching"""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio() >= threshold


def calculate_viral_score(volume, velocity, sentiment):
    """Calculate viral coefficient score"""
    velocity_multipliers = {
        'breakout': 3.0,
        'spike': 3.0,
        'rising': 2.0,
        'rising_fast': 2.5,
        'high': 2.0,
        'steady': 1.0,
        'moderate': 1.0,
        'slow': 0.5,
        'declining': 0.3
    }
    
    sentiment_boost = {
        'excited': 1.1,
        'celebrating': 1.1,
        'controversial': 1.05,
        'concerned': 1.05,
        'curious': 1.0
    }
    
    velocity_key = str(velocity).lower()
    sentiment_key = str(sentiment).lower()
    
    base_score = (volume / 1000) * velocity_multipliers.get(velocity_key, 1.0)
    boosted_score = base_score * sentiment_boost.get(sentiment_key, 1.0)
    
    return min(100, int(boosted_score / 50))


def render_intelligence_dashboard_tab(gemini_pro, gemini_flash, supabase):
    """Main dashboard - intelligence + complete analytics"""
    st.header("📊 Intelligence Dashboard")
    st.caption("**Intelligence Summary + Complete Analytics Visualizations**")
    
    col_fetch, col_fresh = st.columns(2)
    
    with col_fetch:
        if st.button("📥 Fetch Latest 10 Trends from DB", type="secondary", use_container_width=True, key="fetch_trends_button"):
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
        if st.button("🔄 Use Fresh Collection Data", type="secondary", use_container_width=True, key="use_fresh_data_btn"):
            if 'google_data' in st.session_state and 'twitter_data' in st.session_state:
                st.success("✅ Using fresh collection data from session")
                st.rerun()
            else:
                st.warning("⚠️ No fresh data in session. Please collect data first.")
    
    if 'google_data' not in st.session_state or 'twitter_data' not in st.session_state:
        st.info("📥 Please load data using one of the options above")
        return
    
    st.divider()
    
    render_parsed_intelligence_section()
    st.divider()
    
    render_analytics_section()
    st.divider()
    
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
        for theme in intel.get('weather_grid', [])[:2]:
            st.markdown(f"**Theme {theme.get('slot')}. {theme.get('theme')}**")
            st.caption(f"💡 {theme.get('big_question', '')}")
        st.markdown("**🚨 Anomalies:**")
        for outlier in intel.get('anomalies', [])[:2]:
            st.caption(f"• {outlier.get('keyword')}")
    
    with col_usa:
        st.markdown("#### 🇺🇸 USA")
        intel = st.session_state.get('intelligence_USA', {})
        for theme in intel.get('weather_grid', [])[:2]:
            st.markdown(f"**Theme {theme.get('slot')}. {theme.get('theme')}**")
            st.caption(f"💡 {theme.get('big_question', '')}")
        st.markdown("**🚨 Anomalies:**")
        for outlier in intel.get('anomalies', [])[:2]:
            st.caption(f"• {outlier.get('keyword')}")


def render_analytics_section():
    """Complete analytics visualizations"""
    st.markdown("### 📈 Analytics Dashboard")
    
    try:
        google_df = pd.DataFrame(st.session_state.get('google_data', []))
        twitter_df = pd.DataFrame(st.session_state.get('twitter_data', []))
        
        if google_df.empty and twitter_df.empty:
            st.warning("⚠️ No data available for analytics")
            return
        
        create_regional_insight_cards(google_df, twitter_df)
        st.divider()
        
        st.markdown("### 📊 Velocity & Sentiment Analysis")
        st.caption("💡 Hover over bars to see keywords/hashtags")
        
        col1, col2 = st.columns(2)
        with col1:
            if 'velocity' in google_df.columns and 'velocity' in twitter_df.columns:
                fig = create_velocity_breakdown_chart(google_df, twitter_df)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = create_sentiment_breakdown_chart(google_df, twitter_df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        create_cross_platform_analysis(google_df, twitter_df)
        st.divider()
        
        create_sentiment_distribution_wheel(google_df, twitter_df)
        st.divider()
        
        create_viral_trends_section(google_df, twitter_df)
        st.divider()
        
        create_keyword_wordclouds_section(google_df, twitter_df)
        st.divider()
        
        create_category_wordclouds_section(google_df, twitter_df)
        st.divider()
        
        st.markdown("### 📊 Category Breakdown by Region")
        st.caption("💡 Hover over categories to see keywords • Darker colors = Higher volume")
        
        col_india, col_usa = st.columns(2)
        
        with col_india:
            fig_india = create_category_distribution_separate(google_df, twitter_df, 'India')
            if fig_india:
                st.plotly_chart(fig_india, use_container_width=True)
        
        with col_usa:
            fig_usa = create_category_distribution_separate(google_df, twitter_df, 'USA')
            if fig_usa:
                st.plotly_chart(fig_usa, use_container_width=True)
        
        st.divider()
        
        create_top_trends_with_context_section(google_df, twitter_df)
        
    except Exception as e:
        st.error(f"Analytics error: {str(e)}")


def create_regional_insight_cards(google_df, twitter_df):
    """Create regional insight cards with dominant sector"""
    col_india, col_usa = st.columns(2)
    
    with col_india:
        india_google = google_df[google_df['region'] == 'India']
        india_twitter = twitter_df[twitter_df['region'] == 'India']
        india_categories = list(india_google['category']) + list(india_twitter['category'])
        india_dominant = Counter(india_categories).most_common(1)[0][0] if india_categories else 'N/A'
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ea580c 0%, #f59e0b 100%); 
                    padding: 20px; border-radius: 12px; color: white;">
            <div style="font-size: 32px; margin-bottom: 5px;">🇮🇳</div>
            <div style="font-size: 24px; font-weight: bold; margin-bottom: 5px;">India</div>
            <div style="font-size: 14px; opacity: 0.9;">Dominant: {india_dominant}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if len(india_google) > 0:
            top_search = india_google.nlargest(1, 'search_volume').iloc[0]
            st.markdown(f"""
            <div style="background: #fed7aa; padding: 15px; border-radius: 8px; margin-top: 10px;">
                <div style="font-weight: bold; color: #9a3412; margin-bottom: 5px;">🔍 Top Search Query</div>
                <div style="color: #7c2d12; font-size: 16px; font-weight: bold;">{top_search['keyword'][:50]}</div>
                <div style="color: #ea580c; font-size: 14px;">
                    {int(top_search['search_volume']/1000)}K searches
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("💡 Full Context", expanded=False):
                st.caption(f"**Context:** {top_search.get('context', 'N/A')}")
                st.caption(f"**Why Trending:** {top_search.get('why_trending', 'N/A')}")
        
        if len(india_twitter) > 0:
            top_hashtag = india_twitter.nlargest(1, 'mention_volume').iloc[0]
            st.markdown(f"""
            <div style="background: #ffedd5; padding: 15px; border-radius: 8px; margin-top: 10px;">
                <div style="font-weight: bold; color: #9a3412; margin-bottom: 5px;"># Top Trending Topic</div>
                <div style="color: #7c2d12; font-size: 16px; font-weight: bold;">{top_hashtag['keyword'][:50]}</div>
                <div style="color: #ea580c; font-size: 14px;">
                    {int(top_hashtag['mention_volume']/1000)}K mentions
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("💡 Full Context", expanded=False):
                st.caption(f"**Context:** {top_hashtag.get('context', 'N/A')}")
                st.caption(f"**Why Trending:** {top_hashtag.get('why_trending', 'N/A')}")
    
    with col_usa:
        usa_google = google_df[google_df['region'] == 'USA']
        usa_twitter = twitter_df[twitter_df['region'] == 'USA']
        usa_categories = list(usa_google['category']) + list(usa_twitter['category'])
        usa_dominant = Counter(usa_categories).most_common(1)[0][0] if usa_categories else 'N/A'
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); 
                    padding: 20px; border-radius: 12px; color: white;">
            <div style="font-size: 32px; margin-bottom: 5px;">🇺🇸</div>
            <div style="font-size: 24px; font-weight: bold; margin-bottom: 5px;">USA</div>
            <div style="font-size: 14px; opacity: 0.9;">Dominant: {usa_dominant}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if len(usa_google) > 0:
            top_search = usa_google.nlargest(1, 'search_volume').iloc[0]
            st.markdown(f"""
            <div style="background: #dbeafe; padding: 15px; border-radius: 8px; margin-top: 10px;">
                <div style="font-weight: bold; color: #1e40af; margin-bottom: 5px;">🔍 Top Search Query</div>
                <div style="color: #1e3a8a; font-size: 16px; font-weight: bold;">{top_search['keyword'][:50]}</div>
                <div style="color: #60a5fa; font-size: 14px;">
                    {int(top_search['search_volume']/1000)}K searches
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("💡 Full Context", expanded=False):
                st.caption(f"**Context:** {top_search.get('context', 'N/A')}")
                st.caption(f"**Why Trending:** {top_search.get('why_trending', 'N/A')}")
        
        if len(usa_twitter) > 0:
            top_hashtag = usa_twitter.nlargest(1, 'mention_volume').iloc[0]
            st.markdown(f"""
            <div style="background: #e0f2fe; padding: 15px; border-radius: 8px; margin-top: 10px;">
                <div style="font-weight: bold; color: #0369a1; margin-bottom: 5px;"># Top Trending Topic</div>
                <div style="color: #0c4a6e; font-size: 16px; font-weight: bold;">{top_hashtag['keyword'][:50]}</div>
                <div style="color: #0284c7; font-size: 14px;">
                    {int(top_hashtag['mention_volume']/1000)}K mentions
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("💡 Full Context", expanded=False):
                st.caption(f"**Context:** {top_hashtag.get('context', 'N/A')}")
                st.caption(f"**Why Trending:** {top_hashtag.get('why_trending', 'N/A')}")


def create_velocity_breakdown_chart(google_df, twitter_df):
    """Create velocity distribution chart"""
    try:
        combined = pd.concat([
            google_df[['region', 'velocity', 'keyword']],
            twitter_df[['region', 'velocity', 'keyword']]
        ])
        
        velocity_data = []
        for (region, velocity), group in combined.groupby(['region', 'velocity']):
            keywords = group['keyword'].tolist()[:10]
            keywords_text = '<br>'.join([f"  • {kw[:50]}" for kw in keywords])
            
            velocity_data.append({
                'region': region,
                'velocity': velocity,
                'count': len(group),
                'keywords': keywords_text
            })
        
        velocity_df = pd.DataFrame(velocity_data)
        
        fig = px.bar(
            velocity_df,
            x='velocity',
            y='count',
            color='region',
            barmode='group',
            title='📊 Velocity Distribution by Region',
            color_discrete_map={'India': '#ff9933', 'USA': '#4285f4'},
            custom_data=['keywords']
        )
        
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>Count: %{y}<br><br><b>Top Keywords:</b><br>%{customdata[0]}<extra></extra>'
        )
        
        fig.update_layout(height=350, xaxis_title='Velocity', yaxis_title='Count', legend_title='Region')
        return fig
    except Exception:
        return None


def create_sentiment_breakdown_chart(google_df, twitter_df):
    """Create sentiment distribution chart"""
    try:
        google_sentiments = google_df[['region', 'public_sentiment', 'keyword']].rename(columns={'public_sentiment': 'sentiment'}) if 'public_sentiment' in google_df.columns else pd.DataFrame(columns=['region', 'sentiment', 'keyword'])
        
        if 'primary_sentiment' in twitter_df.columns:
            twitter_sentiments = twitter_df[['region', 'primary_sentiment', 'keyword']].rename(columns={'primary_sentiment': 'sentiment'})
        elif 'sentiment' in twitter_df.columns:
            twitter_sentiments = twitter_df[['region', 'sentiment', 'keyword']]
        else:
            twitter_sentiments = pd.DataFrame(columns=['region', 'sentiment', 'keyword'])
        
        combined = pd.concat([google_sentiments, twitter_sentiments])
        
        if len(combined) == 0:
            fig = go.Figure()
            fig.update_layout(title='💭 Sentiment Distribution by Region (No Data)')
            return fig
        
        sentiment_data = []
        for (region, sentiment), group in combined.groupby(['region', 'sentiment']):
            keywords = group['keyword'].tolist()[:10]
            keywords_text = '<br>'.join([f"  • {kw[:50]}" for kw in keywords])
            
            sentiment_data.append({
                'region': region,
                'sentiment': sentiment,
                'count': len(group),
                'keywords': keywords_text
            })
        
        sentiment_df = pd.DataFrame(sentiment_data)
        
        fig = px.bar(
            sentiment_df,
            x='sentiment',
            y='count',
            color='region',
            barmode='group',
            title='💭 Sentiment Distribution by Region',
            color_discrete_map={'India': '#ff9933', 'USA': '#4285f4'},
            custom_data=['keywords']
        )
        
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>Count: %{y}<br><br><b>Keywords/Hashtags:</b><br>%{customdata[0]}<extra></extra>'
        )
        
        fig.update_layout(height=350, xaxis_title='Sentiment', yaxis_title='Count', legend_title='Region')
        return fig
    except Exception:
        return None


def create_cross_platform_analysis(google_df, twitter_df):
    """Comprehensive Cross-Platform Analysis with synergy calculation"""
    st.markdown("### 🔄 Cross-Platform Analysis")
    st.caption("Discover overlaps: Same trends across platforms and regions")
    
    india_google_kw = set(google_df[google_df['region'] == 'India']['keyword'].str.lower())
    india_twitter_kw = set(twitter_df[twitter_df['region'] == 'India']['keyword'].str.lower())
    
    india_overlap = []
    for g_kw in india_google_kw:
        for t_kw in india_twitter_kw:
            if fuzzy_match(g_kw, t_kw, threshold=0.8):
                india_overlap.append((g_kw, t_kw))
                break
    
    usa_google_kw = set(google_df[google_df['region'] == 'USA']['keyword'].str.lower())
    usa_twitter_kw = set(twitter_df[twitter_df['region'] == 'USA']['keyword'].str.lower())
    
    usa_overlap = []
    for g_kw in usa_google_kw:
        for t_kw in usa_twitter_kw:
            if fuzzy_match(g_kw, t_kw, threshold=0.8):
                usa_overlap.append((g_kw, t_kw))
                break
    
    google_india_kw = set(google_df[google_df['region'] == 'India']['keyword'].str.lower())
    google_usa_kw = set(google_df[google_df['region'] == 'USA']['keyword'].str.lower())
    
    google_regional_overlap = []
    for ind_kw in google_india_kw:
        for usa_kw in google_usa_kw:
            if fuzzy_match(ind_kw, usa_kw, threshold=0.8):
                google_regional_overlap.append((ind_kw, usa_kw))
                break
    
    twitter_india_kw = set(twitter_df[twitter_df['region'] == 'India']['keyword'].str.lower())
    twitter_usa_kw = set(twitter_df[twitter_df['region'] == 'USA']['keyword'].str.lower())
    
    twitter_regional_overlap = []
    for ind_kw in twitter_india_kw:
        for usa_kw in twitter_usa_kw:
            if fuzzy_match(ind_kw, usa_kw, threshold=0.8):
                twitter_regional_overlap.append((ind_kw, usa_kw))
                break
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #ea580c 0%, #f59e0b 100%); 
                    padding: 15px; border-radius: 10px; color: white; text-align: center; margin-bottom: 15px;">
            <div style="font-size: 2rem; font-weight: 700;">{len(india_overlap)}</div>
            <div style="font-size: 0.85rem; opacity: 0.9;">🇮🇳 India: Google ∩ Twitter</div>
        </div>
        """, unsafe_allow_html=True)
        
        if india_overlap:
            with st.expander("🔍 View India Cross-Platform Trends", expanded=False):
                for g_kw, t_kw in india_overlap[:10]:
                    if g_kw == t_kw:
                        st.caption(f"• {g_kw.title()}")
                    else:
                        st.caption(f"• {g_kw.title()} ≈ {t_kw.title()}")
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #059669 0%, #10b981 100%); 
                    padding: 15px; border-radius: 10px; color: white; text-align: center;">
            <div style="font-size: 2rem; font-weight: 700;">{len(google_regional_overlap)}</div>
            <div style="font-size: 0.85rem; opacity: 0.9;">🔍 Google: India ∩ USA</div>
        </div>
        """, unsafe_allow_html=True)
        
        if google_regional_overlap:
            with st.expander("🌍 View Google Regional Overlap", expanded=False):
                for ind_kw, usa_kw in google_regional_overlap[:10]:
                    if ind_kw == usa_kw:
                        st.caption(f"• {ind_kw.title()}")
                    else:
                        st.caption(f"• {ind_kw.title()} ≈ {usa_kw.title()}")
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); 
                    padding: 15px; border-radius: 10px; color: white; text-align: center; margin-bottom: 15px;">
            <div style="font-size: 2rem; font-weight: 700;">{len(usa_overlap)}</div>
            <div style="font-size: 0.85rem; opacity: 0.9;">🇺🇸 USA: Google ∩ Twitter</div>
        </div>
        """, unsafe_allow_html=True)
        
        if usa_overlap:
            with st.expander("🔍 View USA Cross-Platform Trends", expanded=False):
                for g_kw, t_kw in usa_overlap[:10]:
                    if g_kw == t_kw:
                        st.caption(f"• {g_kw.title()}")
                    else:
                        st.caption(f"• {g_kw.title()} ≈ {t_kw.title()}")
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%); 
                    padding: 15px; border-radius: 10px; color: white; text-align: center;">
            <div style="font-size: 2rem; font-weight: 700;">{len(twitter_regional_overlap)}</div>
            <div style="font-size: 0.85rem; opacity: 0.9;">🐦 Twitter: India ∩ USA</div>
        </div>
        """, unsafe_allow_html=True)
        
        if twitter_regional_overlap:
            with st.expander("🌍 View Twitter Regional Overlap", expanded=False):
                for ind_kw, usa_kw in twitter_regional_overlap[:10]:
                    if ind_kw == usa_kw:
                        st.caption(f"• {ind_kw.title()}")
                    else:
                        st.caption(f"• {ind_kw.title()} ≈ {usa_kw.title()}")
    
    total_overlaps = len(india_overlap) + len(usa_overlap) + len(google_regional_overlap) + len(twitter_regional_overlap)
    
    st.markdown("---")
    if total_overlaps > 15:
        st.success("🎯 **High Synergy:** Strong cross-platform and cross-regional momentum today!")
    elif total_overlaps > 8:
        st.info("📊 **Moderate Synergy:** Some overlapping themes across platforms/regions")
    else:
        st.warning("🌐 **Low Synergy:** Fragmented interests - need targeted strategies per platform/region")


def create_sentiment_distribution_wheel(google_df, twitter_df):
    """Sentiment distribution wheel for emotional vibe check"""
    st.markdown("### 🎭 Sentiment Distribution Wheel")
    st.caption("Today's emotional landscape by region")
    
    col_india, col_usa = st.columns(2)
    
    for col, region in [(col_india, 'India'), (col_usa, 'USA')]:
        with col:
            sentiments = []
            
            google_region = google_df[google_df['region'] == region]
            twitter_region = twitter_df[twitter_df['region'] == region]
            
            if 'public_sentiment' in google_region.columns:
                sentiments.extend(google_region['public_sentiment'].tolist())
            
            if 'primary_sentiment' in twitter_region.columns:
                sentiments.extend(twitter_region['primary_sentiment'].tolist())
            elif 'sentiment' in twitter_region.columns:
                sentiments.extend(twitter_region['sentiment'].tolist())
            
            sentiment_counts = Counter([s for s in sentiments if s and s != ''])
            
            if not sentiment_counts:
                st.info(f"No sentiment data for {region}")
                continue
            
            labels = list(sentiment_counts.keys())
            values = list(sentiment_counts.values())
            
            color_map = {
                'excited': '#f59e0b',
                'celebrating': '#10b981',
                'curious': '#6366f1',
                'concerned': '#ef4444',
                'controversial': '#ec4899'
            }
            colors = [color_map.get(label, '#9ca3af') for label in labels]
            
            fig = go.Figure(data=[go.Pie(
                labels=[l.title() for l in labels],
                values=values,
                hole=0.4,
                marker=dict(colors=colors),
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
            )])
            
            flag = "🇮🇳" if region == 'India' else "🇺🇸"
            fig.update_layout(
                title=f"{flag} {region}",
                showlegend=True,
                height=350,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            dominant = sentiment_counts.most_common(1)[0]
            st.caption(f"💡 **Dominant Mood:** {dominant[0].title()} ({int((dominant[1]/sum(values))*100)}%)")


def create_viral_trends_section(google_df, twitter_df):
    """Display top viral trends with calculated scores"""
    st.markdown("### 🔥 Viral Trends")
    st.caption("Trends with highest viral coefficient scores")
    
    viral_trends = []
    
    for _, row in google_df.iterrows():
        if 'velocity' in google_df.columns and 'public_sentiment' in google_df.columns:
            score = calculate_viral_score(
                row['search_volume'],
                row.get('velocity', 'steady'),
                row.get('public_sentiment', 'curious')
            )
            viral_trends.append({
                'keyword': row['keyword'],
                'region': row['region'],
                'platform': 'Google',
                'volume': row['search_volume'],
                'score': score
            })
    
    for _, row in twitter_df.iterrows():
        if 'velocity' in twitter_df.columns:
            sentiment = row.get('primary_sentiment') or row.get('sentiment', 'curious')
            score = calculate_viral_score(
                row['mention_volume'],
                row.get('velocity', 'steady'),
                sentiment
            )
            viral_trends.append({
                'keyword': row['keyword'],
                'region': row['region'],
                'platform': 'Twitter',
                'volume': row['mention_volume'],
                'score': score
            })
    
    if viral_trends:
        viral_df = pd.DataFrame(viral_trends).sort_values('score', ascending=False).head(10)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🇮🇳 India Top Viral**")
            india_viral = viral_df[viral_df['region'] == 'India'].head(5)
            for _, trend in india_viral.iterrows():
                st.markdown(f"""
                <div style="background: #fff7ed; padding: 10px; border-left: 4px solid #ea580c; margin-bottom: 8px; border-radius: 4px;">
                    <div style="font-weight: bold; color: #9a3412;">{trend['keyword'][:40]}</div>
                    <div style="font-size: 0.85rem; color: #ea580c;">
                        {trend['platform']} • Score: {trend['score']}/100
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("**🇺🇸 USA Top Viral**")
            usa_viral = viral_df[viral_df['region'] == 'USA'].head(5)
            for _, trend in usa_viral.iterrows():
                st.markdown(f"""
                <div style="background: #eff6ff; padding: 10px; border-left: 4px solid #2563eb; margin-bottom: 8px; border-radius: 4px;">
                    <div style="font-weight: bold; color: #1e40af;">{trend['keyword'][:40]}</div>
                    <div style="font-size: 0.85rem; color: #2563eb;">
                        {trend['platform']} • Score: {trend['score']}/100
                    </div>
                </div>
                """, unsafe_allow_html=True)


def create_keyword_wordclouds_section(google_df, twitter_df):
    """Keyword word clouds by region and platform"""
    st.markdown("### ☁️ Keyword Word Clouds")
    st.caption("💡 Darker color = Higher volume")
    
    font_path = setup_font()
    
    tab_india, tab_usa = st.tabs(["🇮🇳 India", "🇺🇸 USA"])
    
    with tab_india:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Google Keywords**")
            fig = create_keyword_word_cloud(google_df, 'India', 'Google', font_path)
            if fig:
                st.pyplot(fig)
            else:
                st.info("No Google data for India")
        
        with col2:
            st.markdown("**Twitter Keywords**")
            fig = create_keyword_word_cloud(twitter_df, 'India', 'Twitter', font_path)
            if fig:
                st.pyplot(fig)
            else:
                st.info("No Twitter data for India")
    
    with tab_usa:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Google Keywords**")
            fig = create_keyword_word_cloud(google_df, 'USA', 'Google', font_path)
            if fig:
                st.pyplot(fig)
            else:
                st.info("No Google data for USA")
        
        with col2:
            st.markdown("**Twitter Keywords**")
            fig = create_keyword_word_cloud(twitter_df, 'USA', 'Twitter', font_path)
            if fig:
                st.pyplot(fig)
            else:
                st.info("No Twitter data for USA")


def create_keyword_word_cloud(data, region, platform='Google', font_path=None):
    """Create word cloud from keywords with gradient colors"""
    try:
        regional_data = data[data['region'] == region]
        
        if len(regional_data) == 0:
            return None
        
        if platform == 'Google':
            word_freq = {row['keyword']: row['search_volume'] for _, row in regional_data.iterrows()}
        else:
            word_freq = {row['keyword']: row['mention_volume'] for _, row in regional_data.iterrows()}
        
        if region == 'India':
            def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
                volume = word_freq.get(word, 0)
                max_vol = max(word_freq.values()) if word_freq else 1
                lightness = 70 - (40 * (volume / max_vol))
                return f"hsl(30, 100%, {int(lightness)}%)"
        else:
            def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
                volume = word_freq.get(word, 0)
                max_vol = max(word_freq.values()) if word_freq else 1
                lightness = 70 - (40 * (volume / max_vol))
                return f"hsl(217, 89%, {int(lightness)}%)"
        
        wc = WordCloud(
            width=600,
            height=300,
            background_color='white',
            relative_scaling=0.5,
            min_font_size=10,
            color_func=color_func,
            font_path=font_path,
            collocations=False
        ).generate_from_frequencies(word_freq)
        
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(f'{region} {platform} Keywords', fontsize=12, fontweight='bold')
        
        return fig
    except Exception:
        return None


def create_category_wordclouds_section(google_df, twitter_df):
    """Category Word Clouds by Region & Platform"""
    st.markdown("### 📊 Category Distribution Word Clouds")
    st.caption("💡 Darker color = More trends in that category")
    
    font_path = setup_font()
    
    col_india, col_usa = st.columns(2)
    
    with col_india:
        st.markdown("#### 🇮🇳 India")
        
        st.markdown("**Google Search Categories:**")
        wc_result = create_category_word_cloud_by_platform(google_df, 'India', 'Google', font_path)
        if wc_result:
            fig, categories_text = wc_result
            st.pyplot(fig)
            with st.expander("📊 Category Breakdown", expanded=False):
                st.text(categories_text)
        else:
            st.info("No Google data for India")
        
        st.markdown("**Twitter Trend Categories:**")
        wc_result = create_category_word_cloud_by_platform(twitter_df, 'India', 'Twitter', font_path)
        if wc_result:
            fig, categories_text = wc_result
            st.pyplot(fig)
            with st.expander("📊 Category Breakdown", expanded=False):
                st.text(categories_text)
        else:
            st.info("No Twitter data for India")
    
    with col_usa:
        st.markdown("#### 🇺🇸 USA")
        
        st.markdown("**Google Search Categories:**")
        wc_result = create_category_word_cloud_by_platform(google_df, 'USA', 'Google', font_path)
        if wc_result:
            fig, categories_text = wc_result
            st.pyplot(fig)
            with st.expander("📊 Category Breakdown", expanded=False):
                st.text(categories_text)
        else:
            st.info("No Google data for USA")
        
        st.markdown("**Twitter Trend Categories:**")
        wc_result = create_category_word_cloud_by_platform(twitter_df, 'USA', 'Twitter', font_path)
        if wc_result:
            fig, categories_text = wc_result
            st.pyplot(fig)
            with st.expander("📊 Category Breakdown", expanded=False):
                st.text(categories_text)
        else:
            st.info("No Twitter data for USA")


def create_category_word_cloud_by_platform(data, region, platform, font_path=None):
    """Create word cloud of CATEGORIES with trend counts"""
    try:
        regional_data = data[data['region'] == region]
        
        if len(regional_data) == 0:
            return None
        
        category_counts = Counter(regional_data['category'])
        
        if not category_counts:
            return None
        
        if region == 'India':
            def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
                count = category_counts.get(word, 0)
                max_count = max(category_counts.values()) if category_counts else 1
                lightness = 70 - (40 * (count / max_count))
                return f"hsl(30, 100%, {int(lightness)}%)"
        else:
            def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
                count = category_counts.get(word, 0)
                max_count = max(category_counts.values()) if category_counts else 1
                lightness = 70 - (40 * (count / max_count))
                return f"hsl(217, 89%, {int(lightness)}%)"
        
        wc = WordCloud(
            width=600,
            height=300,
            background_color='white',
            relative_scaling=0.5,
            min_font_size=10,
            color_func=color_func,
            font_path=font_path,
            collocations=False
        ).generate_from_frequencies(category_counts)
        
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        
        total_trends = len(regional_data)
        ax.set_title(f'{platform} Categories ({total_trends} trends)',
                    fontsize=12, fontweight='bold', pad=10)
        
        categories_text = "\n".join([f"{cat}: {count} trends" for cat, count in category_counts.most_common(10)])
        
        return fig, categories_text
    except Exception:
        return None


def create_category_distribution_separate(google_df, twitter_df, region):
    """Create category treemap - Dark=High, Light=Low"""
    combined = pd.concat([
        google_df[google_df['region'] == region][['category', 'keyword', 'search_volume']].rename(columns={'search_volume': 'volume'}),
        twitter_df[twitter_df['region'] == region][['category', 'keyword', 'mention_volume']].rename(columns={'mention_volume': 'volume'})
    ])
    
    if len(combined) == 0:
        return None
    
    cat_data = []
    for category, group in combined.groupby('category'):
        keywords = group['keyword'].tolist()[:10]
        total_volume = group['volume'].sum()
        
        cat_data.append({
            'category': category,
            'volume': total_volume,
            'keywords': '<br>'.join([f"  • {kw[:40]}" for kw in keywords]),
            'count': len(group)
        })
    
    cat_df = pd.DataFrame(cat_data)
    
    if region == 'India':
        color_scale = ['#fecaca', '#fca5a5', '#f87171', '#ef4444', '#dc2626', '#b91c1c']
    else:
        color_scale = ['#dbeafe', '#bfdbfe', '#93c5fd', '#60a5fa', '#3b82f6', '#2563eb', '#1e40af', '#1e3a8a']
    
    fig = px.treemap(
        cat_df,
        path=['category'],
        values='volume',
        color='volume',
        color_continuous_scale=color_scale,
        custom_data=['keywords', 'count'],
        title=f"📊 {region} Category Distribution"
    )
    
    fig.update_traces(
        textinfo="label+value",
        textfont_size=14,
        hovertemplate='<b>%{label}</b><br>' +
                     'Volume: %{value:,.0f}<br>' +
                     'Trends: %{customdata[1]}<br><br>' +
                     '<b>Top Keywords:</b><br>%{customdata[0]}<extra></extra>',
        marker=dict(
            line=dict(width=2, color='white'),
            pad=dict(t=50, l=5, r=5, b=5)
        )
    )
    
    fig.update_layout(
        height=400,
        title_font_size=18,
        title_x=0.5,
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    return fig


def create_top_trends_with_context_section(google_df, twitter_df):
    """Top trends bar charts with context and why trending in hover"""
    st.markdown("### 📊 Top Trends with Context")
    st.caption("💡 Hover over bars to see full context and why trending")
    
    tab_india, tab_usa = st.tabs(["🇮🇳 India", "🇺🇸 USA"])
    
    with tab_india:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Google Searches**")
            fig = create_top_trends_with_context(google_df, 'India', 'Google')
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No Google data")
        
        with col2:
            st.markdown("**Twitter Trends**")
            fig = create_top_trends_with_context(twitter_df, 'India', 'Twitter')
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No Twitter data")
    
    with tab_usa:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Google Searches**")
            fig = create_top_trends_with_context(google_df, 'USA', 'Google')
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No Google data")
        
        with col2:
            st.markdown("**Twitter Trends**")
            fig = create_top_trends_with_context(twitter_df, 'USA', 'Twitter')
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No Twitter data")


def create_top_trends_with_context(data, region, platform='Google'):
    """Create bar chart with context on hover"""
    regional_data = data[data['region'] == region]
    
    if platform == 'Google':
        top_data = regional_data.nlargest(10, 'search_volume')
        volume_col = 'search_volume'
    else:
        top_data = regional_data.nlargest(10, 'mention_volume')
        volume_col = 'mention_volume'
    
    if len(top_data) == 0:
        return None
    
    top_data = top_data.copy()
    top_data['keyword_short'] = top_data['keyword'].apply(
        lambda x: x[:30] + '...' if len(x) > 30 else x
    )
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=top_data['keyword_short'][::-1],
        x=top_data[volume_col][::-1],
        orientation='h',
        marker=dict(
            color='#ff9933' if region == 'India' else '#4285f4',
            opacity=0.8
        ),
        text=[f'{int(x/1000)}K' if x < 1000000 else f'{int(x/1000000*10)/10}M'
              for x in top_data[volume_col][::-1]],
        textposition='outside',
        customdata=top_data[['keyword', 'context', 'why_trending', volume_col]][::-1].values,
        hovertemplate='<b>%{customdata[0]}</b><br>' +
                     'Volume: %{customdata[3]:,.0f}<br><br>' +
                     '<b>Context:</b> %{customdata[1]}<br><br>' +
                     '<b>Why Trending:</b> %{customdata[2]}<extra></extra>',
        showlegend=False
    ))
    
    fig.update_layout(
        height=400,
        margin=dict(l=0, r=50, t=30, b=0),
        paper_bgcolor='white',
        plot_bgcolor='#f9fafb',
        xaxis=dict(showgrid=True, gridcolor='#e5e7eb'),
        yaxis=dict(showgrid=False),
        title=dict(
            text=f"Top 10 {platform} Trends",
            font=dict(size=14)
        )
    )
    
    return fig


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