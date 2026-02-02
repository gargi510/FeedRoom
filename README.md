# Pivot Note - Production Deployment Guide

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10 or higher
- Git
- API Keys: Gemini, SerpAPI, Supabase

### 2. Installation

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

### 3. Environment Setup

Create `.env` file in project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
SERPAPI_KEY=your_serpapi_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
```

### 4. **CRITICAL: Fix Hindi Word Cloud Rendering**

The issue with Hindi characters not appearing in word clouds is due to missing Unicode font support in matplotlib. Here's how to fix it:

#### Solution 1: Install Noto Sans Devanagari (Recommended)

**Linux/Ubuntu:**
```bash
# Install Noto fonts
sudo apt-get install fonts-noto

# Clear matplotlib cache
rm -rf ~/.cache/matplotlib
```

**Windows:**
```bash
# Download Noto Sans Devanagari from Google Fonts
# https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari

# Install the font:
# 1. Extract the downloaded .zip file
# 2. Right-click on NotoSansDevanagari-Regular.ttf
# 3. Click "Install for all users"

# Then clear matplotlib cache:
# Delete folder: C:\Users\<YourUsername>\.matplotlib
```

**Mac:**
```bash
# Install Noto fonts via Homebrew
brew tap homebrew/cask-fonts
brew install --cask font-noto-sans-devanagari

# Clear matplotlib cache
rm -rf ~/.matplotlib
```

#### Solution 2: Manual Font Setup

If automatic installation doesn't work:

1. **Download Font**: Get Noto Sans Devanagari from [Google Fonts](https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari)

2. **Create fonts folder**:
```bash
mkdir -p fonts
```

3. **Copy font file**: Place `NotoSansDevanagari-Regular.ttf` in the `fonts/` folder

4. **Update code**: The analytics module will automatically use the font from `fonts/` directory

#### Verify Font Installation

Run this test script:

```python
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

# Check available fonts
fonts = [f.name for f in fm.fontManager.ttflist if 'Devanagari' in f.name or 'Noto' in f.name]
print("Available Devanagari fonts:", fonts)

# Test Hindi rendering
fig, ax = plt.subplots()
ax.text(0.5, 0.5, 'हिन्दी परीक्षण', fontsize=20)
plt.show()
```

If you see "हिन्दी परीक्षण" correctly rendered, the fix worked! ✅

### 5. Run Application

```bash
streamlit run app.py
```

Access at: `http://localhost:8501`

---

## 📁 Project Structure

```
pivotnote_production/
├── app.py                          # Main application
├── prompts.py                      # AI prompts (2 segments + 1 outlier logic)
├── utils.py                        # Utility functions
├── database_deepdive.py            # Deep dive database operations
├── voice_cloning.py                # TTS voice generation
├── prompt_updater.py               # Prompt fine-tuning (FIXED)
│
├── tab_collection.py               # Tab 1: Data Collection
├── tab_intelligence_analysis.py   # Tab 2: Intelligence Analysis
├── tab_intelligence_dashboard.py  # Tab 3: Dashboard + Production
├── tab_deepdive_research.py       # Tab 4: Deep Dive
├── tab_weekly_insights.py          # Tab 5: Weekly Dashboard
│
├── fonts/                          # Font files (for Hindi support)
│   └── NotoSansDevanagari-Regular.ttf
│
├── images/                         # Runtime files (auto-created)
├── backups/                        # Prompt backups (auto-created)
│
├── requirements.txt                # Dependencies
├── .env                            # API keys (create this)
├── .gitignore                      # Git ignore file
└── README.md                       # This file
```

---

## 🎯 Tab Overview

### Tab 1: Data Collection
- ✅ Auto-fetch Google Trends (USA + India)
- ✅ Auto-enrich with Gemini
- ✅ Manual Twitter data entry
- ✅ Push to Supabase

### Tab 2: Intelligence Analysis
- ✅ Phase 0: Generate intelligence grids
- ✅ 2 themes + 2 anomalies per region (updated logic)
- ✅ Fine-tune prompts (FIXED)

### Tab 3: Intelligence Dashboard
- ✅ Display parsed intelligence
- ✅ Analytics visualizations
- ✅ Script generation (2 segments + 1 outlier)
- ✅ Audio generation
- ✅ Raw data tables (collapsed)
- ✅ Push to database

### Tab 4: Deep Dive Research
- ✅ Keyword selection
- ✅ Strategic clash research
- ✅ Script generation
- ✅ Audio recording/upload
- ❌ NO MoviePy (removed)

### Tab 5: Weekly Insights
- ✅ Weekly analytics dashboard
- ✅ Trend patterns over time
- ✅ Performance metrics

---

## ⚙️ Configuration

### Supabase Tables Required

#### `google_trends`
```sql
CREATE TABLE google_trends (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  collection_date DATE NOT NULL,
  collection_timestamp TIMESTAMPTZ NOT NULL,
  region TEXT NOT NULL,
  rank INTEGER,
  keyword TEXT NOT NULL,
  search_volume BIGINT,
  category TEXT,
  velocity TEXT,
  trend_type TEXT,
  context TEXT,
  why_trending TEXT,
  related_searches TEXT[]
);
```

#### `twitter_trends`
```sql
CREATE TABLE twitter_trends (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  collection_date DATE NOT NULL,
  collection_timestamp TIMESTAMPTZ NOT NULL,
  region TEXT NOT NULL,
  rank INTEGER,
  keyword TEXT NOT NULL,
  mention_volume BIGINT,
  hashtag_type TEXT,
  category TEXT,
  velocity TEXT,
  sentiment TEXT,
  sentiment_positive INTEGER,
  sentiment_neutral INTEGER,
  sentiment_negative INTEGER,
  context TEXT,
  why_trending TEXT,
  related_hashtags TEXT[],
  top_entities TEXT[]
);
```

#### `daily_content_records`
```sql
CREATE TABLE daily_content_records (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  publish_date DATE NOT NULL UNIQUE,
  intelligence_grid_india JSONB,
  intelligence_grid_usa JSONB,
  script_assembly_india JSONB,
  script_assembly_usa JSONB,
  youtube_metadata_india JSONB,
  youtube_metadata_usa JSONB,
  visual_prompts_india JSONB,
  visual_prompts_usa JSONB,
  audio_script_india TEXT,
  audio_script_usa TEXT,
  raw_data_summary JSONB
);
```

#### `deep_dive_research`
```sql
CREATE TABLE deep_dive_research (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  status TEXT DEFAULT 'needs_finetuning',
  finalized_at TIMESTAMPTZ,
  keyword TEXT NOT NULL,
  region TEXT NOT NULL,
  platform TEXT,
  search_volume BIGINT,
  velocity TEXT,
  sentiment TEXT,
  category TEXT,
  character TEXT,
  research_data JSONB,
  sources_summary TEXT,
  title TEXT,
  subtitle TEXT,
  anomaly TEXT,
  approved_story TEXT,
  script_final TEXT,
  youtube_title TEXT,
  youtube_description TEXT,
  youtube_hook TEXT,
  hashtags TEXT[],
  thumbnail_prompt TEXT,
  image_prompts JSONB
);
```

---

## 🔧 Troubleshooting

### Hindi Characters Not Showing in Word Clouds

**Problem**: Word clouds show boxes (□) instead of Hindi text

**Solution**: Follow the "Fix Hindi Word Cloud Rendering" section above. The key is:
1. Install Noto Sans Devanagari font system-wide
2. Clear matplotlib cache
3. Restart application

**Verify Font is Loaded**:
```python
import matplotlib.font_manager as fm
print([f.name for f in fm.fontManager.ttflist if 'Devanagari' in f.name])
# Should output: ['Noto Sans Devanagari']
```

### Prompt Fine-Tuner Not Working

**Problem**: Region parameter error when updating assembly prompts

**Fixed**: Updated `prompt_updater.py` now properly handles region parameter. Make sure to:
1. Pull latest version
2. Clear any cached sessions
3. Use the fine-tuner from within the app (not standalone)

### Gemini Quota Exhausted

**Fallback**: Use manual enrichment mode
1. Copy prompt from UI
2. Paste in Gemini web interface
3. Copy JSON response back
4. Parse in application

---

## 🚀 Deployment

### Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy from repo
4. Add secrets (API keys) in Settings

### Docker (Alternative)

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install font for Hindi support
RUN apt-get update && apt-get install -y fonts-noto

COPY . .

CMD ["streamlit", "run", "app.py"]
```

---

## 📊 Script Logic Changes

### Old Logic (Removed):
- 3 Segments + 1 Anomaly
- Total: 4 main sections

### New Logic (Production):
- **2 Segments** (Primary + Secondary theme)
- **1 Outlier** (Breakout signal)
- Total: 3 main sections
- **Duration**: 60 seconds (~150 words)

**Format**: Intro (4s) → Segment 1 (15s) → Segment 2 (15s) → Outlier (13s) → Bridge (7s) → Outro (6s)

---

## 📝 Changes from V12

### Removed:
- ❌ All MoviePy code (video assembly)
- ❌ Chart generation phase (Phase 2)
- ❌ Asset checklist
- ❌ Video rendering

### Updated:
- ✅ Script logic: 3→2 segments
- ✅ Analysis: Still generates 2 anomalies
- ✅ Production: Uses 1 outlier in script
- ✅ Prompt updater: Fixed region handling
- ✅ Word clouds: Hindi font support

### New:
- ✅ Unified Intelligence Dashboard (Tab 3)
- ✅ Weekly Insights Dashboard (Tab 5)
- ✅ Production-grade structure
- ✅ Better error handling
- ✅ Comprehensive documentation

---

## 💡 Best Practices

1. **Data Collection**: Run daily at consistent time
2. **Backups**: Prompt updater auto-backs up before changes
3. **Database**: Regular backups of Supabase data
4. **Monitoring**: Check logs for API quota usage
5. **Quality**: Review intelligence grids before script generation

---

## 🆘 Support

For issues or questions:
1. Check this README first
2. Review code comments
3. Check backups folder for prompt history
4. Test with minimal data first

---

## 📄 License

Proprietary - All Rights Reserved

---

**Ready to Deploy!** 🚀

Run `streamlit run app.py` and start generating daily intelligence reports!