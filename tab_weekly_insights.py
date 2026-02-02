"""
Tab 5: Weekly Insights Dashboard (The FeedRoom)
7-day trend analysis from Supabase
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date
from collections import Counter


def render_weekly_insights_tab(supabase):
    """Weekly insights dashboard"""
    
    st.header("📈 Weekly Insights Dashboard")
    st.caption("**The FeedRoom 7-Day Trend Analysis**")
    
    if not supabase:
        st.error("❌ Supabase not configured")
        return
    
    st.divider()
    
    # Fetch last 7 days data
    with st.spinner("🔄 Fetching last 7 days of data..."):
        google_data, twitter_data, error = fetch_weekly_data(supabase)
    
    if error:
        st.error(f"❌ {error}")
        return
    
    if not google_data and not twitter_data:
        st.warning("⚠️ No data found for the last 7 days")
        return
    
    google_df = pd.DataFrame(google_data)
    twitter_df = pd.DataFrame(twitter_data)
    
    st.success(f"✅ Loaded {len(google_df)} Google + {len(twitter_df)} Twitter trends from last 7 days")
    
    st.divider()
    
    # Weekly Summary
    render_weekly_summary(google_df, twitter_df)
    
    st.divider()
    
    # Trend Patterns Over Time
    render_trend_patterns(google_df, twitter_df)
    
    st.divider()
    
    # Volume Charts
    render_volume_charts(google_df, twitter_df)
    
    st.divider()
    
    # Category Performance
    render_category_performance(google_df, twitter_df)
    
    st.divider()
    
    # Sentiment Trends
    render_sentiment_trends(google_df, twitter_df)
    
    st.divider()
    
    # Top Performing Keywords
    render_top_keywords(google_df, twitter_df)


def fetch_weekly_data(supabase):
    """Fetch data from last 7 days"""
    try:
        today = date.today()
        seven_days_ago = today - timedelta(days=7)
        
        today_str = today.isoformat()
        seven_days_str = seven_days_ago.isoformat()
        
        # Fetch Google Trends
        google_result = supabase.table('google_trends')\
            .select('*')\
            .gte('collection_date', seven_days_str)\
            .lte('collection_date', today_str)\
            .execute()
        
        google_data = google_result.data if google_result.data else []
        
        # Fetch Twitter Trends
        twitter_result = supabase.table('twitter_trends')\
            .select('*')\
            .gte('collection_date', seven_days_str)\
            .lte('collection_date', today_str)\
            .execute()
        
        twitter_data = twitter_result.data if twitter_result.data else []
        
        return google_data, twitter_data, None
        
    except Exception as e:
        return None, None, f"Database error: {str(e)}"


def render_weekly_summary(google_df, twitter_df):
    """Weekly summary metrics"""
    st.markdown("### 📊 Weekly Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_trends = len(google_df) + len(twitter_df)
        st.metric("Total Trends", f"{total_trends:,}")
    
    with col2:
        unique_days = len(pd.concat([google_df, twitter_df])['collection_date'].unique())
        st.metric("Days Tracked", unique_days)
    
    with col3:
        combined = pd.concat([google_df, twitter_df])
        if 'velocity' in combined.columns:
            breakouts = len(combined[combined['velocity'].str.lower().isin(['breakout', 'spike'])])
        else:
            breakouts = 0
        st.metric("Breakouts", breakouts)
    
    with col4:
        regions = len(combined['region'].unique())
        st.metric("Regions", regions)


def render_trend_patterns(google_df, twitter_df):
    """Trend patterns over time"""
    st.markdown("### 📈 Trend Patterns Over Time")
    
    combined = pd.concat([google_df, twitter_df])
    
    if 'collection_date' not in combined.columns:
        st.warning("No date information available")
        return
    
    # Group by date
    daily_counts = combined.groupby(['collection_date', 'region']).size().reset_index(name='count')
    
    fig = px.line(
        daily_counts,
        x='collection_date',
        y='count',
        color='region',
        title='Daily Trend Volume by Region',
        markers=True,
        color_discrete_map={'India': '#ff9933', 'USA': '#4285f4'}
    )
    
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Number of Trends',
        hovermode='x unified',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_volume_charts(google_df, twitter_df):
    """Volume trends over time"""
    st.markdown("### 📊 Volume Trends")
    
    tab_g, tab_t = st.tabs(["🔍 Google Search Volume", "🐦 Twitter Mention Volume"])
    
    with tab_g:
        if 'collection_date' in google_df.columns and 'search_volume' in google_df.columns:
            daily_volume = google_df.groupby(['collection_date', 'region'])['search_volume'].sum().reset_index()
            
            fig = px.bar(
                daily_volume,
                x='collection_date',
                y='search_volume',
                color='region',
                title='Daily Google Search Volume',
                color_discrete_map={'India': '#ff9933', 'USA': '#4285f4'},
                barmode='group'
            )
            
            fig.update_layout(
                xaxis_title='Date',
                yaxis_title='Total Search Volume',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No volume data available")
    
    with tab_t:
        if 'collection_date' in twitter_df.columns and 'mention_volume' in twitter_df.columns:
            daily_volume = twitter_df.groupby(['collection_date', 'region'])['mention_volume'].sum().reset_index()
            
            fig = px.bar(
                daily_volume,
                x='collection_date',
                y='mention_volume',
                color='region',
                title='Daily Twitter Mention Volume',
                color_discrete_map={'India': '#ff9933', 'USA': '#4285f4'},
                barmode='group'
            )
            
            fig.update_layout(
                xaxis_title='Date',
                yaxis_title='Total Mention Volume',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No volume data available")


def render_category_performance(google_df, twitter_df):
    """Category performance over the week"""
    st.markdown("### 📂 Category Performance")
    
    combined = pd.concat([google_df, twitter_df])
    
    if 'category' not in combined.columns:
        st.warning("No category data available")
        return
    
    # Category counts
    category_counts = combined['category'].value_counts().reset_index()
    category_counts.columns = ['category', 'count']
    
    fig = px.bar(
        category_counts.head(15),
        x='count',
        y='category',
        orientation='h',
        title='Top 15 Categories (Last 7 Days)',
        color='count',
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        xaxis_title='Number of Trends',
        yaxis_title='Category',
        showlegend=False,
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_sentiment_trends(google_df, twitter_df):
    """Sentiment trends over time"""
    st.markdown("### 💭 Sentiment Trends")
    
    # Check which sentiment columns exist
    sentiment_data = []
    
    if 'public_sentiment' in google_df.columns and 'collection_date' in google_df.columns:
        google_sent = google_df[['collection_date', 'public_sentiment', 'region']].copy()
        google_sent.columns = ['date', 'sentiment', 'region']
        sentiment_data.append(google_sent)
    
    if 'primary_sentiment' in twitter_df.columns and 'collection_date' in twitter_df.columns:
        twitter_sent = twitter_df[['collection_date', 'primary_sentiment', 'region']].copy()
        twitter_sent.columns = ['date', 'sentiment', 'region']
        sentiment_data.append(twitter_sent)
    elif 'sentiment' in twitter_df.columns and 'collection_date' in twitter_df.columns:
        twitter_sent = twitter_df[['collection_date', 'sentiment', 'region']].copy()
        twitter_sent.columns = ['date', 'sentiment', 'region']
        sentiment_data.append(twitter_sent)
    
    if not sentiment_data:
        st.info("No sentiment data available")
        return
    
    combined_sent = pd.concat(sentiment_data, ignore_index=True)
    
    # Daily sentiment distribution
    daily_sent = combined_sent.groupby(['date', 'sentiment']).size().reset_index(name='count')
    
    fig = px.bar(
        daily_sent,
        x='date',
        y='count',
        color='sentiment',
        title='Daily Sentiment Distribution',
        barmode='stack',
        color_discrete_map={
            'excited': '#f59e0b',
            'celebrating': '#10b981',
            'curious': '#6366f1',
            'concerned': '#ef4444',
            'controversial': '#ec4899'
        }
    )
    
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Count',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_top_keywords(google_df, twitter_df):
    """Top performing keywords of the week"""
    st.markdown("### 🏆 Top Performing Keywords")
    
    tab_india, tab_usa = st.tabs(["🇮🇳 India", "🇺🇸 USA"])
    
    with tab_india:
        st.markdown("#### Top Google Searches")
        if 'region' in google_df.columns and 'search_volume' in google_df.columns:
            india_google = google_df[google_df['region'] == 'India']
            top_google = india_google.nlargest(10, 'search_volume')[['keyword', 'search_volume', 'category']]
            st.dataframe(top_google, use_container_width=True, hide_index=True)
        else:
            st.info("No data")
        
        st.markdown("#### Top Twitter Trends")
        if 'region' in twitter_df.columns and 'mention_volume' in twitter_df.columns:
            india_twitter = twitter_df[twitter_df['region'] == 'India']
            top_twitter = india_twitter.nlargest(10, 'mention_volume')[['keyword', 'mention_volume', 'category']]
            st.dataframe(top_twitter, use_container_width=True, hide_index=True)
        else:
            st.info("No data")
    
    with tab_usa:
        st.markdown("#### Top Google Searches")
        if 'region' in google_df.columns and 'search_volume' in google_df.columns:
            usa_google = google_df[google_df['region'] == 'USA']
            top_google = usa_google.nlargest(10, 'search_volume')[['keyword', 'search_volume', 'category']]
            st.dataframe(top_google, use_container_width=True, hide_index=True)
        else:
            st.info("No data")
        
        st.markdown("#### Top Twitter Trends")
        if 'region' in twitter_df.columns and 'mention_volume' in twitter_df.columns:
            usa_twitter = twitter_df[twitter_df['region'] == 'USA']
            top_twitter = usa_twitter.nlargest(10, 'mention_volume')[['keyword', 'mention_volume', 'category']]
            st.dataframe(top_twitter, use_container_width=True, hide_index=True)
        else:
            st.info("No data")