# Pivot Note - Complete Production Deployment Guide

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Project Structure](#project-structure)
3. [Database Schema](#database-schema)
4. [Module Versions](#module-versions)
5. [Configuration](#configuration)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Git
- API Keys: Gemini, SerpAPI, Supabase
- Node.js (for local Supabase CLI, optional)

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd pivotnote_production

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

Create `.env` file in project root:

```env
# Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here

# SerpAPI (for Google Trends)
SERPAPI_KEY=your_serpapi_key_here

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here

# Optional: Voice Cloning (only if using voice version)
# PLAYHT_API_KEY=your_playht_key
# ELEVENLABS_API_KEY=your_elevenlabs_key
```

### Run Application

```bash
streamlit run app.py
```

Access at: `http://localhost:8501`

---

## 📁 Project Structure

```
pivotnote_production/
├── app.py                              # Main Streamlit application
├── requirements.txt                    # Python dependencies
├── .env                                # API keys (create this, not in repo)
├── .gitignore                          # Git ignore patterns
│
├── Core Modules
│   ├── prompts.py                      # AI prompt templates (2 segments + 1 outlier)
│   ├── utils.py                        # Utility functions & validation
│   └── db_operations.py                # Database CRUD operations (FIXED)
│
├── Tab Modules (Production - Without Voice)
│   ├── tab_collection.py               # Tab 1: Data Collection
│   ├── tab_intelligence_analysis.py    # Tab 2: Intelligence Analysis
│   ├── tab_intelligence_dashboard.py   # Tab 3: Dashboard + Production
│   ├── tab_daily_analysis.py           # Tab 4: Daily Analysis (NO VOICE)
│   ├── tab_deepdive.py                 # Tab 5: Deep Dive (NO VOICE)
│   └── tab_weekly_insights.py          # Tab 6: Weekly Insights
│
├── Tab Modules (Alternative - With Voice Cloning)
│   ├── tab_daily_analysis_VOICE.py     # Tab 4: With XTTS v2 + gTTS
│   ├── tab_deepdive_VOICE.py           # Tab 5: With XTTS v2 + gTTS
│   └── voice_cloning.py                # Voice generation utilities
│
├── Runtime Directories (auto-created)
│   ├── audio/                          # Voice samples & generated audio
│   ├── images/                         # Generated visualizations
│   ├── backups/                        # Prompt version backups
│   └── ffmpeg_bin/                     # FFmpeg DLLs (Windows, for voice)
│
└── Documentation
    ├── README.md                       # This file
    └── DEPLOYMENT.md                   # Deployment-specific notes
```

---

## 🗄️ Database Schema

### Complete Supabase Schema

```sql
-- ============================================================================
-- GOOGLE TRENDS TABLE
-- ============================================================================
CREATE TABLE public.google_trends (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  collection_date date NOT NULL,
  collection_timestamp timestamp with time zone NOT NULL,
  region character varying NOT NULL,
  rank integer NOT NULL,
  keyword text NOT NULL,
  search_volume bigint,
  category character varying,
  velocity character varying,
  trend_type character varying,
  context text,
  why_trending text,
  related_searches text[],
  public_sentiment text,
  sentiment_score bigint
);

-- Indexes for performance
CREATE INDEX idx_google_trends_date ON public.google_trends(collection_date);
CREATE INDEX idx_google_trends_region ON public.google_trends(region);
CREATE INDEX idx_google_trends_keyword ON public.google_trends(keyword);

-- ============================================================================
-- TWITTER/X TRENDS TABLE
-- ============================================================================
CREATE TABLE public.twitter_trends (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  collection_date date NOT NULL,
  collection_timestamp timestamp with time zone NOT NULL,
  region character varying NOT NULL,
  rank integer NOT NULL,
  keyword text NOT NULL,
  mention_volume bigint,
  hashtag_type character varying,
  category character varying,
  velocity character varying,
  sentiment character varying,
  sentiment_positive integer,
  sentiment_neutral integer,
  sentiment_negative integer,
  context text,
  why_trending text,
  related_hashtags jsonb,
  top_entities jsonb
);

-- Indexes
CREATE INDEX idx_twitter_trends_date ON public.twitter_trends(collection_date);
CREATE INDEX idx_twitter_trends_region ON public.twitter_trends(region);
CREATE INDEX idx_twitter_trends_keyword ON public.twitter_trends(keyword);

-- ============================================================================
-- DAILY INSIGHTS TABLE (Intelligence Grids - Flattened)
-- ============================================================================
CREATE TABLE public.daily_insights (
  id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  analysis_date date NOT NULL,
  region character varying NOT NULL,
  
  -- Theme 1
  theme_1_title text,
  theme_1_category text,
  theme_1_keywords text[],
  theme_1_mood text,
  theme_1_data_signal text,
  theme_1_context text,
  theme_1_deep_why text,
  theme_1_big_question text,
  
  -- Theme 2
  theme_2_title text,
  theme_2_category text,
  theme_2_keywords text[],
  theme_2_mood text,
  theme_2_data_signal text,
  theme_2_context text,
  theme_2_deep_why text,
  theme_2_big_question text,
  
  -- Anomaly 1
  anomaly_1_keyword text,
  anomaly_1_velocity text,
  anomaly_1_explanation text,
  anomaly_1_big_question text,
  
  -- Anomaly 2
  anomaly_2_keyword text,
  anomaly_2_velocity text,
  anomaly_2_explanation text,
  anomaly_2_big_question text,
  
  -- Production Mood
  overall_sentiment double precision,
  vibe_color_hex text,
  vocal_tone text,
  visual_background_prompt text,
  
  created_at timestamp with time zone DEFAULT now()
);

-- Indexes
CREATE INDEX idx_daily_insights_date ON public.daily_insights(analysis_date);
CREATE INDEX idx_daily_insights_region ON public.daily_insights(region);

-- Unique constraint: one record per date per region
CREATE UNIQUE INDEX idx_daily_insights_date_region ON public.daily_insights(analysis_date, region);

-- ============================================================================
-- DAILY CONTENT RECORDS TABLE (Scripts & Production)
-- ============================================================================
CREATE TABLE public.daily_content_records (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  created_at timestamp with time zone DEFAULT now(),
  publish_date date NOT NULL UNIQUE,
  
  -- Scripts
  script_usa text,
  script_india text,
  
  -- Intelligence Grids (JSONB for complex nested data)
  intelligence_grid_usa jsonb,
  intelligence_grid_india jsonb,
  
  -- Script Assembly
  script_assembly_usa jsonb,
  script_assembly_india jsonb,
  
  -- Visual Prompts
  visual_prompts_usa jsonb,
  visual_prompts_india jsonb,
  
  -- YouTube Metadata (Individual Fields - CRITICAL FOR WEEKLY ANALYSIS)
  youtube_title_usa text,
  youtube_title_india text,
  youtube_description_usa text,
  youtube_description_india text,
  youtube_hook_usa text,
  youtube_hook_india text,
  youtube_hashtags_usa text[],
  youtube_hashtags_india text[],
  thumbnail_prompt_usa text,
  thumbnail_prompt_india text,
  
  -- YouTube Metadata (JSON - Backward Compatibility)
  youtube_metadata_usa jsonb,
  youtube_metadata_india jsonb,
  
  -- Executive Summary
  executive_summary text,
  
  -- Anomalies & Entities
  anomalies_detected jsonb,
  entities jsonb,
  
  -- Production Status
  production_status character varying DEFAULT 'draft',
  completed_at timestamp with time zone
);

-- Indexes
CREATE INDEX idx_daily_content_date ON public.daily_content_records(publish_date);
CREATE INDEX idx_daily_content_status ON public.daily_content_records(production_status);

-- ============================================================================
-- ENTITIES TABLE (Tracked Entities Across Days)
-- ============================================================================
CREATE TABLE public.entities (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  analysis_date date NOT NULL,
  entity_type character varying NOT NULL,
  entity_name character varying NOT NULL,
  keywords text[] NOT NULL,
  total_mentions text,
  regions text[] NOT NULL,
  context text,
  sentiment character varying,
  role character varying,
  trend_velocity text,
  source_platform text,
  created_at timestamp with time zone DEFAULT now()
);

-- Indexes
CREATE INDEX idx_entities_date ON public.entities(analysis_date);
CREATE INDEX idx_entities_name ON public.entities(entity_name);
CREATE INDEX idx_entities_type ON public.entities(entity_type);

-- ============================================================================
-- DEEP DIVE RESEARCH TABLE
-- ============================================================================
CREATE TABLE public.deep_dive_research (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone,
  
  -- Status
  status character varying DEFAULT 'researched',
  finalized_at timestamp with time zone,
  published_at timestamp with time zone,
  
  -- Keyword Info
  keyword text NOT NULL,
  region character varying NOT NULL,
  platform character varying NOT NULL,
  search_volume bigint,
  velocity character varying,
  sentiment character varying,
  category character varying,
  
  -- Research Data (JSONB - Complex Strategic Clash Object)
  research_data jsonb,
  sources_summary text,
  
  -- Script
  script_final text,
  
  -- YouTube Metadata (Individual Fields ONLY - NO JSON)
  -- CRITICAL: For weekly analysis queries
  youtube_title text,
  youtube_description text,
  youtube_hook text,
  hashtags text[],
  thumbnail_prompt text,
  
  -- Visual Prompts (JSONB - Multiple prompts)
  image_prompts jsonb,
  
  -- Notes
  notes text
);

-- Indexes
CREATE INDEX idx_deepdive_keyword ON public.deep_dive_research(keyword);
CREATE INDEX idx_deepdive_region ON public.deep_dive_research(region);
CREATE INDEX idx_deepdive_status ON public.deep_dive_research(status);
CREATE INDEX idx_deepdive_created ON public.deep_dive_research(created_at);

-- ============================================================================
-- ENABLE ROW LEVEL SECURITY (Optional but recommended)
-- ============================================================================
ALTER TABLE public.google_trends ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.twitter_trends ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_insights ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_content_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.deep_dive_research ENABLE ROW LEVEL SECURITY;

-- Create policies (example - adjust based on your needs)
CREATE POLICY "Enable read access for authenticated users" ON public.google_trends
  FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "Enable insert for authenticated users" ON public.google_trends
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Repeat for other tables as needed
```

### Key Schema Notes

#### 1. **Daily Content Records**
- **Has BOTH**: Individual YouTube fields + JSON fields
- **Reason**: Individual fields for easy queries, JSON for backward compatibility
- **Query Example**:
  ```sql
  -- Easy weekly analysis
  SELECT publish_date, youtube_title_india, youtube_title_usa 
  FROM daily_content_records 
  WHERE publish_date >= CURRENT_DATE - 7;
  ```

#### 2. **Deep Dive Research**
- **Has ONLY**: Individual YouTube fields (NO JSON `youtube_metadata`)
- **Reason**: Clean structure optimized for weekly analysis
- **Query Example**:
  ```sql
  -- Get all deep dive titles from last month
  SELECT keyword, youtube_title, region, created_at
  FROM deep_dive_research
  WHERE created_at >= CURRENT_DATE - 30
  ORDER BY created_at DESC;
  ```

#### 3. **Daily Insights**
- **Flattened structure**: No nested JSON
- **Reason**: Fast queries for analytics dashboard
- **Creates**: 2 rows per analysis date (one for India, one for USA)

---

## 🔧 Module Versions

### **Current Deployment: WITHOUT Voice Cloning**

| Module | Filename | Description | Voice? |
|--------|----------|-------------|--------|
| Tab 1 | `tab_collection.py` | Data Collection | N/A |
| Tab 2 | `tab_intelligence_analysis.py` | Intelligence Analysis | N/A |
| Tab 3 | `tab_intelligence_dashboard.py` | Dashboard + Analytics | N/A |
| Tab 4 | `tab_daily_analysis.py` | Daily Script (NO VOICE) | ❌ |
| Tab 5 | `tab_deepdive.py` | Deep Dive (NO VOICE) | ❌ |
| Tab 6 | `tab_weekly_insights.py` | Weekly Dashboard | N/A |
| Core | `db_operations.py` | Database Ops (FIXED) | N/A |
| Core | `prompts.py` | AI Prompts (FIXED) | N/A |

### **Alternative: WITH Voice Cloning**

If you want to enable voice cloning later:

| Module | Filename | Description | Voice? |
|--------|----------|-------------|--------|
| Tab 4 | `tab_daily_analysis_VOICE.py` | With XTTS v2 + gTTS | ✅ |
| Tab 5 | `tab_deepdive_VOICE.py` | With XTTS v2 + gTTS | ✅ |
| Core | `voice_cloning.py` | Voice utilities | ✅ |

**Voice Features:**
- ✅ XTTS v2 voice cloning (local, D: Drive protected)
- ✅ gTTS AI voice (cloud, fast)
- ✅ Multi-sample blending for accent stability
- ✅ Speed/temperature controls
- ✅ Number-to-word normalization

**To Enable Voice:**
1. Replace `tab_daily_analysis.py` with `tab_daily_analysis_VOICE.py`
2. Replace `tab_deepdive.py` with `tab_deepdive_VOICE.py`
3. Add voice samples to `audio/` folder (sample1.wav, sample2.wav, etc.)
4. Install additional dependencies:
   ```bash
   pip install TTS gtts pydub --break-system-packages
   ```
5. On Windows: Place FFmpeg DLLs in `ffmpeg_bin/` folder

---

## ⚙️ Configuration

### API Keys Setup

#### 1. Gemini API
- Get from: https://makersuite.google.com/app/apikey
- Models used: `gemini-1.5-pro-latest`, `gemini-1.5-flash-latest`
- Quota: Check your limits

#### 2. SerpAPI
- Get from: https://serpapi.com/manage-api-key
- Used for: Google Trends data collection
- Free tier: 100 searches/month

#### 3. Supabase
- Get from: https://app.supabase.com/project/_/settings/api
- Need: Project URL + Anon/Public Key
- RLS: Configure based on your needs

### Application Settings

#### Script Logic (Production)
```python
# Intelligence Grid: 2 Themes + 2 Anomalies per region
themes = ["Theme 1", "Theme 2"]
anomalies = ["Anomaly 1", "Anomaly 2"]

# Script Assembly: 2 Segments + 1 Outlier
segments = ["Segment 1", "Segment 2"]
outlier = "Outlier (from Anomaly 1)"

# Format: Intro → Segment 1 → Segment 2 → Outlier → Outro
# Duration: ~60 seconds (~150-200 words)
```

#### File Paths (Auto-created)
```python
AUDIO_DIR = "audio/"           # Voice samples & generated audio
IMAGES_DIR = "images/"         # Visualizations & charts
BACKUPS_DIR = "backups/"       # Prompt version backups
FFMPEG_DIR = "ffmpeg_bin/"     # FFmpeg DLLs (Windows only)
```

---

## 🚀 Deployment

### Local Development

```bash
# 1. Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 2. Set environment variables
export GEMINI_API_KEY="your_key"
export SERPAPI_KEY="your_key"
export SUPABASE_URL="your_url"
export SUPABASE_KEY="your_key"

# 3. Run application
streamlit run app.py

# 4. Access
# http://localhost:8501
```

### Streamlit Cloud Deployment

#### Step 1: Push to GitHub
```bash
git add .
git commit -m "Production deployment"
git push origin main
```

#### Step 2: Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io
2. Click "New app"
3. Select your repository
4. Main file: `app.py`
5. Python version: 3.10

#### Step 3: Add Secrets
In Streamlit Cloud dashboard → Settings → Secrets:

```toml
GEMINI_API_KEY = "your_gemini_key"
SERPAPI_KEY = "your_serpapi_key"
SUPABASE_URL = "your_supabase_url"
SUPABASE_KEY = "your_supabase_key"
```

#### Step 4: Configure Advanced Settings
- Python version: 3.10
- Resources: Standard (or scale up if needed)
- Custom domain (optional)

### Docker Deployment (Alternative)

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    fonts-noto \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t pivotnote .
docker run -p 8501:8501 --env-file .env pivotnote
```

---

## 🧪 Testing & Verification

### Test Checklist

#### ✅ Data Collection (Tab 1)
```python
# Test SerpAPI connection
- [ ] Fetch Google Trends USA
- [ ] Fetch Google Trends India
- [ ] Enrich with Gemini
- [ ] Validate data structure
- [ ] Push to Supabase
```

#### ✅ Intelligence Analysis (Tab 2)
```python
# Test intelligence generation
- [ ] Generate intelligence grid (India + USA)
- [ ] Verify 2 themes per region
- [ ] Verify 2 anomalies per region
- [ ] Check executive summary
- [ ] Save to Supabase
```

#### ✅ Script Generation (Tab 3/4)
```python
# Test script assembly
- [ ] Generate script India
- [ ] Generate script USA
- [ ] Verify structure: 2 segments + 1 outlier
- [ ] Word count: 150-200 words
- [ ] Save to database
```

#### ✅ Deep Dive (Tab 5)
```python
# Test deep dive workflow
- [ ] Select keyword
- [ ] Generate research
- [ ] Generate script (120-130 words)
- [ ] Verify YouTube metadata extraction
- [ ] Save to database
- [ ] Check individual fields populated (NOT JSON)
```

#### ✅ Database Verification
```sql
-- Check daily content
SELECT publish_date, youtube_title_india, youtube_title_usa 
FROM daily_content_records 
ORDER BY publish_date DESC LIMIT 5;

-- Check deep dive
SELECT keyword, youtube_title, youtube_description 
FROM deep_dive_research 
ORDER BY created_at DESC LIMIT 5;

-- Verify NO NULL values in YouTube fields
SELECT COUNT(*) 
FROM daily_content_records 
WHERE youtube_title_india IS NULL OR youtube_title_usa IS NULL;
-- Should return 0

SELECT COUNT(*) 
FROM deep_dive_research 
WHERE youtube_title IS NULL;
-- Should return 0
```

---

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 1. YouTube Metadata Not Saving

**Symptom**: Individual YouTube fields (youtube_title, youtube_description) are NULL

**Solution**: 
- ✅ Use `db_operations_FIXED.py` (extracts to individual fields)
- ✅ Verify assembly structure has `youtube_metadata` object
- ✅ Check debug statements in save function

**Verify**:
```python
assembly = st.session_state['assembly_India']
print("YouTube metadata:", assembly.get('youtube_metadata'))
# Should show: {'title': '...', 'description': '...', ...}
```

#### 2. Prompt Fine-Tuner Region Error

**Symptom**: `TypeError: get_assembly_prompt_india() takes 1 positional argument but 2 were given`

**Solution**: 
- ✅ Use updated `prompts.py` (FIXED version)
- ✅ Assembly prompts now take `(intelligence_grid, production_mood)`
- ✅ Analysis prompt unchanged

#### 3. Hindi Characters in Word Clouds

**Symptom**: Word clouds show boxes (□) instead of Hindi text

**Solution**:
```bash
# Linux/Ubuntu
sudo apt-get install fonts-noto
rm -rf ~/.cache/matplotlib

# Windows
# Download from: https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari
# Install font system-wide
# Delete: C:\Users\<Username>\.matplotlib

# Mac
brew install --cask font-noto-sans-devanagari
rm -rf ~/.matplotlib
```

#### 4. Gemini API Quota Exceeded

**Solution**:
- Use manual mode: Copy prompt → Paste in Gemini web → Copy JSON back
- Upgrade API quota
- Switch to Flash model for non-critical operations

#### 5. Supabase Connection Failed

**Check**:
```python
# Test connection
from supabase import create_client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
result = supabase.table('google_trends').select("*").limit(1).execute()
print("Connection OK" if result.data else "Connection Failed")
```

#### 6. Voice Cloning DLL Error (Windows)

**Symptom**: `DLL load failed` when using XTTS

**Solution**:
1. Download FFmpeg: https://www.gyan.dev/ffmpeg/builds/
2. Extract `bin/` folder contents to `ffmpeg_bin/`
3. Verify files: `avcodec-*.dll`, `avformat-*.dll`, `avutil-*.dll`
4. Restart application

---

## 📊 Script Logic Reference

### Intelligence Grid Structure

```json
{
  "executive_summary": "2-3 sentences comparing USA vs India",
  "entities": [...],
  "india_intelligence": {
    "weather_grid": [
      {
        "slot": 1,
        "category": "Entertainment",
        "theme": "3-word theme",
        "keywords": ["kw1", "kw2"],
        "mood": "Critical",
        "data_signal": "+300% search spike",
        "context": "Factual reality",
        "deep_why": "Psychological insight",
        "big_question": "Provocative question"
      },
      {
        "slot": 2,
        "category": "Sports",
        "theme": "3-word theme",
        ...
      }
    ],
    "anomalies": [
      {
        "rank": 1,
        "keyword": "exact keyword",
        "velocity": "+5000% Breakout",
        "explanation": "Why this matters",
        "big_question": "Future question"
      },
      {
        "rank": 2,
        ...
      }
    ],
    "production_mood": {
      "overall_sentiment": 0.5,
      "vibe_color_hex": "#FFBF00",
      "vocal_tone": "authoritative",
      "visual_background_prompt": "..."
    }
  },
  "usa_intelligence": {
    // Same structure as India
  }
}
```

### Script Assembly Structure (Daily Analysis)

```json
{
  "script_assembly": {
    "intro": "The last 24 decoded in 60. Here's what's trending?",
    "segment_1": "30-50 words about Theme 1 with rhetorical question",
    "segment_2": "35-50 words about Theme 2 with rhetorical question",
    "outlier": "35-50 words about Anomaly 1 with rhetorical question",
    "outro": "What's on your feed today? Comment below!"
  },
  "youtube_metadata": {
    "title": "60-char title",
    "description": "150-word description",
    "hook": "First 10 seconds",
    "hashtags": ["#tag1", "#tag2", "#tag3"]
  },
  "visual_prompts": {
    "intro_visual": "AI image prompt",
    "segment_1_visual": "AI image prompt",
    "segment_2_visual": "AI image prompt",
    "outlier_visual": "AI image prompt",
    "outro_visual": "AI image prompt"
  }
}
```

### Script Assembly Structure (Deep Dive)

```json
{
  "audio_script": "Complete 120-130 word flowing script (single text, no segments)",
  "youtube_metadata": {
    "title": "Provocative question with metric",
    "description": "Deep dive analysis summary",
    "hook": "First 15-20 words of audio_script",
    "hashtags": ["#PivotNote", "#DeepDive"],
    "thumbnail_prompt": "Cinematic dashboard --ar 16:9"
  },
  "visual_prompts": {
    "hook_visual": "Cinematic shot --ar 9:16",
    "side_a_visual": "Innovation visual --ar 9:16",
    "side_b_visual": "Traditional concern visual --ar 9:16",
    "analysis_visual": "Secret sauce visual --ar 9:16",
    "conclusion_visual": "Binary choice visual --ar 9:16"
  }
}
```

---

## 📈 Performance & Scaling

### Current Limits
- Daily data collection: ~50 trends (20 Google + 30 Twitter)
- Intelligence generation: ~2-3 minutes per region
- Script generation: ~30 seconds per script
- Database: Unlimited (Supabase free tier: 500MB)

### Optimization Tips
1. Use Flash model for enrichment (faster, cheaper)
2. Use Pro model for intelligence/scripts (higher quality)
3. Cache prompt templates (done automatically)
4. Batch database operations where possible

### Scaling Considerations
- **10+ users**: Upgrade Supabase plan
- **100+ daily records**: Add database indexes
- **Voice generation**: Consider external service (ElevenLabs/Play.HT)
- **API quotas**: Monitor and upgrade as needed

---

## 📝 Change Log

### v2.0 (Current - Production Without Voice)
- ✅ Fixed YouTube metadata extraction (individual fields)
- ✅ Updated script logic (2 segments + 1 outlier)
- ✅ Fixed prompt fine-tuner region parameter
- ✅ Separated voice/non-voice versions
- ✅ Complete database schema documentation
- ✅ Production-ready deployment guide

### v1.5 (Previous - With Voice)
- ✅ Added XTTS v2 voice cloning
- ✅ Added gTTS AI voice
- ✅ Multi-sample blending
- ✅ D: Drive model protection

### v1.0 (Initial)
- ✅ Core data collection
- ✅ Intelligence analysis
- ✅ Script generation
- ✅ Deep dive research

---

## 🔐 Security Notes

### API Keys
- ✅ Never commit `.env` to repository
- ✅ Use Streamlit secrets for cloud deployment
- ✅ Rotate keys periodically
- ✅ Monitor usage for anomalies

### Database
- ✅ Enable Row Level Security (RLS)
- ✅ Create proper policies based on user roles
- ✅ Regular backups
- ✅ Monitor for unauthorized access

### Code
- ✅ Input validation on all user data
- ✅ Sanitize SQL queries (using Supabase client)
- ✅ Rate limit API calls
- ✅ Error handling without exposing internals

---

## 📄 License

Proprietary - All Rights Reserved

---

## 🆘 Support & Contact

For issues or questions:
1. Check Troubleshooting section above
2. Review schema documentation
3. Check version compatibility
4. Test with minimal data first
5. Review error logs in Streamlit

---

## ✅ Pre-Deployment Checklist

- [ ] All API keys configured in `.env` or Streamlit secrets
- [ ] Database schema created in Supabase
- [ ] Tables indexed for performance
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Test data collection workflow
- [ ] Test intelligence generation
- [ ] Test script generation (both regions)
- [ ] Test deep dive workflow
- [ ] Verify YouTube metadata saves to individual fields
- [ ] Test weekly insights dashboard
- [ ] Check all database queries return expected results
- [ ] Backup prompts before any fine-tuning
- [ ] Document any custom changes

---

**🚀 Ready to Deploy!**

Current deployment: **WITHOUT voice cloning**  
Alternative available: **WITH voice cloning** (see Module Versions section)

Run `streamlit run app.py` and start generating daily intelligence reports!