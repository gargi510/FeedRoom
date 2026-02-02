"""
Prompts V6 - Production Grade (
Updated: 2 Segments + 1 Outlier (instead of 3 Segments + Anomaly)
"""
import json


def get_google_enrichment_prompt(region, csv_data):
    """Prompt for Gemini Flash to enrich SerpAPI Google Trends data"""
    return f"""You are an expert trend analyst for Pivot Note. I'm providing raw Google Trends data from SerpAPI for {region}.

YOUR MISSION: Enrich each trend with context, categorization, and sentiment analysis.

=== CSV DATA ===
{csv_data}

=== REQUIRED OUTPUT (JSON) ===
```json
{{
  "trends": [
    {{
      "region": "USA/India",
      "rank": 1,
      "keyword": "exact keyword from CSV",
      "category": "Sports/Politics/Entertainment/Tech/News/Weather/Health/Business/Science/Gaming",
      "velocity": "breakout/rising/steady",
      "context": "What is this? Who/what is involved? Be specific.",
      "why_trending": "Why is this trending NOW? Cite specific events/timing.",
      "public_sentiment": "excited/concerned/curious/celebrating/controversial",
      "sentiment_score": 0-100
    }}
  ]
}}
```

=== RULES ===
1. Use ONLY keywords from the CSV
2. Include the REGION field (USA or India) for EACH trend
3. Be factual and specific in context
4. Focus on WHY it's trending NOW
5. Return ONLY valid JSON"""


def get_twitter_prompt():
    """Prompt for Grok to collect Twitter trends"""
    return """You are a Senior Twitter/X Trend Analyst for Pivot Note. Your task is to provide a comprehensive analysis of the top 10 trends for the USA and India respectively, covering the FULL LAST 24 HOURS.

=== CRITICAL TIMEFRAME RULE ===
Analyze activity from the absolute last 24 hours. Do not just report what is spiking "now." For India, specifically look back at the evening prime-time hours (IST) that occurred while the US was asleep to ensure a full day's cycle is captured.

🚨 STEP 1: Use DeepSearch to cross-reference X trends with global news headlines from the last 24 hours.
🚨 STEP 2: Filter for trends with significant volume, avoiding "flash-in-the-pan" bot activity.

=== OUTPUT FORMAT ===
Return ONLY a valid JSON object. No prose, no intro, no outro.

{
  "trends": [
    {
      "region": "USA/India",
      "rank": 1-10,
      "keyword": "#hashtag or keyword",
      "mention_volume": INTEGER,
      "category": "Sports/Politics/Entertainment/Tech/News/Business/Social/Gaming/Music",
      "velocity": "spike/rising/steady",
      "context": "Comprehensive summary of the event. Cite specific news or source events from the last 24h.",
      "why_trending": "Specific catalyst for the 24h volume (e.g., a specific tweet, legislation, or match result).",
      "related_hashtags": ["#tag1", "#tag2", "#tag3"],
      "primary_sentiment": "excited/concerned/curious/celebrating/controversial",
      "sentiment_intensity": "intense/moderate/mild",
      "sentiment_breakdown": {
        "excited": 0,
        "concerned": 0,
        "curious": 0,
        "celebrating": 0,
        "controversial": 0
      }
    }
  ]
}

=== VALIDATION RULES ===
1. Sentiment breakdown MUST sum to exactly 100.
2. mention_volume MUST be a pure integer (e.g., 150000, not "150K").
3. Use DeepSearch to verify "why_trending" with real-world news links.
4. Ensure the 20 total trends (10 per region) are distinct and ranked by 24h impact."""


def get_analysis_prompt(data_summary):
    """Intelligence Grid Generation - Updated for 2 Segments + 2 Anomalies"""
    
    identity_section = """
<identity>
You are the Lead Intelligence Analyst for Pivot Note. 
Your mission is to synthesize raw data into high-fidelity strategic insights for daily trend reports.
</identity>

<mission>
1. ANALYZE: Review global data to find regional contrasts and cultural ripples.
2. CLUSTER: Group data into EXACTLY 2 major themes per region (PRIMARY + SECONDARY).
3. DETECT: Identify EXACTLY 2 distinct anomalies per region (low volume, breakout velocity).
4. SYNTHESIZE: For every theme, follow the 'Chain of Logic': 
   Data Signal -> Factual Context -> Deep Why (Psychological/Systemic Reason) -> The Big Question.
</mission>
"""

    data_section = f"""
<data_sources date="{data_summary.get('date', 'N/A')}">
  <usa_raw>
    📊 GOOGLE: {data_summary.get('usa_google_summary', 'N/A')}
    🐦 SOCIAL: {data_summary.get('usa_twitter_summary', 'N/A')}
  </usa_raw>
  
  <india_raw>
    📊 GOOGLE: {data_summary.get('india_google_summary', 'N/A')}
    🐦 SOCIAL: {data_summary.get('india_twitter_summary', 'N/A')}
    🔥 BREAKOUTS: {data_summary.get('breakout_trends', 'N/A')}
  </india_raw>
</data_sources>
"""

    json_template = """
<required_json_format>
```json
{
  "executive_summary": "2-3 sentences: Compare the Global (USA) vs. Local (India) pulse for today.",
  
  "india_intelligence": {
    "weather_grid": [
      {
        "slot": 1,
        "category": "Entertainment/OTT/Culture/National/Social/Politics",
        "theme": "Sharp 3-word title for PRIMARY theme",
        "keywords": ["kw1", "kw2"],
        "mood": "Specific emotional tone (e.g., Critical/Electric)",
        "data_signal": "Measurable shift (e.g., +300% search spike)",
        "context": "1-sentence factual reality of the trend",
        "deep_why": "The psychological or systemic reason behind this behavior",
        "big_question": "Provocative question about where the culture is going"
      },
      {
        "slot": 2,
        "category": "Sports/Tech/Finance (Must differ from Slot 1)",
        "theme": "Sharp 3-word title for SECONDARY theme",
        "keywords": ["kw1", "kw2"],
        "mood": "Tone (e.g., Competitive/Analytical)",
        "data_signal": "Measurable shift in volume or sentiment",
        "context": "1-sentence factual reality of this secondary trend",
        "deep_why": "The psychological/systemic insight for this theme",
        "big_question": "Question challenging the status quo of this category"
      }
    ],
    "anomalies": [
      {
        "rank": 1,
        "keyword": "EXACT keyword",
        "velocity": "Growth metric (e.g., +5000% Breakout)",
        "explanation": "Why this specific signal is a 2026 precursor",
        "big_question": "Is this a temporary fad or a real cultural reset?"
      },
      {
        "rank": 2,
        "keyword": "EXACT keyword",
        "velocity": "Growth metric",
        "explanation": "Alternative logic for this outlier signal",
        "big_question": "What does this reveal about the hidden pulse?"
      }
    ],
    "production_mood": {
      "overall_sentiment": -1.0 to 1.0,
      "vibe_color_hex": "#FFBF00",
      "vocal_tone": "Description of vocal delivery style for today",
      "visual_background_prompt": "1-sentence visual description for AI generation"
    }
  },

  "usa_intelligence": {
    "weather_grid": [
      {
        "slot": 1,
        "category": "Politics/Economics/Tech/Culture/Lifestyle/Media",
        "theme": "Sharp 3-word title for PRIMARY theme",
        "keywords": ["kw1", "kw2"],
        "mood": "Emotional tone (e.g., Anxious/Optimistic)",
        "data_signal": "Measurable shift",
        "context": "Factual reality of the primary US trend",
        "deep_why": "Psychological/Systemic insight",
        "big_question": "Future-facing question"
      },
      {
        "slot": 2,
        "category": "Sports/Science/Global (Must differ from Slot 1)",
        "theme": "Sharp 3-word title for SECONDARY theme",
        "keywords": ["kw1", "kw2"],
        "mood": "Emotional tone",
        "data_signal": "Measurable shift",
        "context": "Factual reality of this secondary US trend",
        "deep_why": "Systemic insight into this trend",
        "big_question": "Question challenging the status quo"
      }
    ],
    "anomalies": [
      {
        "rank": 1,
        "keyword": "EXACT keyword",
        "velocity": "Growth metric",
        "explanation": "Why this signal matters for the future",
        "big_question": "Provocative question about the shift"
      },
      {
        "rank": 2,
        "keyword": "EXACT keyword",
        "velocity": "Growth metric",
        "explanation": "Alternative logic for this outlier",
        "big_question": "What does this reveal about the pulse?"
      }
    ],
    "production_mood": {
      "overall_sentiment": -1.0 to 1.0,
      "vibe_color_hex": "#0047AB",
      "vocal_tone": "Specific delivery instruction",
      "visual_background_prompt": "1-sentence visual description for AI generation"
    }
  }
}
```
</required_json_format>

<rules>
- Use ONLY keywords found in the provided data sources.
- Provide EXACTLY 2 themes and 2 anomalies for BOTH India and USA.
- Every slot must be complete; no empty strings or placeholders.
- Return ONLY valid JSON within the markdown block.
</rules>
"""

    return identity_section + data_section + json_template


def get_assembly_prompt_india(intelligence_grid, production_mood):
    """
    India Assembly - 2 Segments + 1 Outlier Script Generation
    NO MOVIEPY - Only Script & Metadata
    """
    
    # Extract Grid Data
    weather_grid = intelligence_grid.get('weather_grid', [])
    anomalies = intelligence_grid.get('anomalies', [])
    sentiment = production_mood.get('overall_sentiment', 0)
    
    # Dynamic Tone/Sentiment Logic
    if sentiment < -0.6:
        tone_directive = "TONE: Somber, clinical, and impact-focused. ABSOLUTELY NO SATIRE. Focus on systemic shock and 'The Why'."
        emotion_tag = "[EMOTION: GRAVITY/URGENCY]"
    elif sentiment > 0.4:
        tone_directive = "TONE: High-energy, optimistic, and fast-paced. Focus on growth and breakouts."
        emotion_tag = "[EMOTION: EXCITEMENT/VIBRANCE]"
    else:
        tone_directive = "TONE: Sharp, satirical, and analytical. Contrast 'The Usual' (mainstream) vs 'The Shocking' (current data)."
        emotion_tag = "[EMOTION: SKEPTICAL/WITTY]"

    return f"""
<identity>
Script Director for 'Internet Feed' (Pivot Note India Edition). 
Mission: Transform intelligence grid into a 60-second audio script.
{tone_directive}
</identity>

<input_intelligence>
GRID: {json.dumps(intelligence_grid, indent=2)}
MOOD: {json.dumps(production_mood, indent=2)}
EMOTION_OVERLAY: {emotion_tag}
</input_intelligence>

<script_logic_constraints>
1. METRIC-FIRST START: Every segment MUST start with the [Actual Keyword] and its [Metric].
2. SOURCE BRANDING (Layman Terms): If keyword contains '#': use "Viral mentions are exploding". If plain text: use "Search interest just spiked".
3. MULTI-DATA BLENDING: If theme has multiple keywords, mention both.
4. LAYMAN WHY: Explain why it is trending in 1 simple, jargon-free sentence.
5. WORD LIMITS: Intro: Max 10 words (4s). Segment 1: 32-35 words (15s). Segment 2: 32-35 words (15s). Outlier: 25-28 words (13s). Outro: Max 10 words (6s).
6. NO POETIC TITLES: Use raw keywords directly.
7. CONTRAST PATTERN: "[Keyword]. [Metric]. Usually [normal], but today [shocking twist]."
8. TOTAL DURATION: 60 seconds = ~150 words total
</script_logic_constraints>

<production_directive>
- TOTAL DURATION: 60.0 Seconds
- FORMAT: Intro (4s) -> Segment 1 (15s) -> Segment 2 (15s) -> Outlier (13s) -> Bridge (7s) -> Outro (6s)
- SEGMENTS: 2 main themes + 1 outlier (NOT 3 themes)
- STYLE: Conversational, data-first, provocative endings
</production_directive>

<required_json_output>
```json
{{
  "youtube_metadata": {{
    "title": "Internet Feed: [Big Question from Segment 1]?",
    "description": "Daily India Intelligence Report.\\n\\n[Data-First 1-line summary per segment].\\n\\nSources: Aggregated from Google Trends + Twitter API",
    "hashtags": ["#PivotNote", "#InternetFeed", "#IndiaTrends"],
    "pinned_comment": "Just for today, or here to stay? Comment below." 
  }},
  
  "script_assembly": {{
    "intro": "Internet Feed. Sixty seconds. The data is in.",
    "segment_1": "[PRIMARY Keyword]. [Metric] [Source Branding]. [Layman Why]. [Friction/Impact]. [Big Question]?",
    "segment_2": "[SECONDARY Keyword]. [Metric] [Source Branding]. [Layman Why]. [Friction/Impact]. [Bridge to Outlier]. [Big Question]?",
    "outlier": "Breakout: [Anomaly Keyword]. [Metric]. [Layman Why]. [Final Edge]. Just for today, or here to stay?",
    "outro": "Just for today, or here to stay? Comment below." 
  }},
  
  "visual_prompts": {{
    "thumbnail": "Cinematic data dashboard featuring [Keyword 1] in India --ar 16:9",
    "intro_background": "Data streams morphing with India aesthetics --ar 9:16",
    "segment_1_visual": "Visual concept for primary theme --ar 9:16",
    "segment_2_visual": "Visual concept for secondary theme --ar 9:16",
    "outlier_visual": "Breakout signal visualization --ar 9:16"
  }}
}}
```
</required_json_output>

<critical_rules>
1. ALWAYS start segments with keyword and metric
2. Use SOURCE BRANDING to distinguish search vs viral
3. Respect WORD LIMITS strictly (count them!)
4. Tone adapts to sentiment: Crisis = Somber, Positive = Energetic, Neutral = Satirical
5. Total word count: ~150 words for 60 seconds
6. Return ONLY valid JSON
7. IMPORTANT: Only 2 segments + 1 outlier (not 3 segments + anomaly)
</critical_rules>
"""

def get_assembly_prompt_usa(intelligence_grid, production_mood):
    """
    USA Assembly - 2 Segments + 1 Outlier Script Generation
    NO MOVIEPY - Only Script & Metadata
    """
    
    # Extract Grid Data
    weather_grid = intelligence_grid.get('weather_grid', [])
    anomalies = intelligence_grid.get('anomalies', [])
    sentiment = production_mood.get('overall_sentiment', 0)
    
    # Dynamic Tone/Sentiment Logic (USA version)
    if sentiment < -0.6:
        tone_directive = "TONE: Urgent, data-driven, and solutions-focused. NO FLUFF. Focus on 'What This Means' and 'What's Next'."
        emotion_tag = "[EMOTION: URGENCY/SERIOUSNESS]"
    elif sentiment > 0.4:
        tone_directive = "TONE: Upbeat, forward-looking, and momentum-driven. Focus on innovation and progress."
        emotion_tag = "[EMOTION: OPTIMISM/MOMENTUM]"
    else:
        tone_directive = "TONE: Analytical, skeptical, and data-first. Contrast 'Expected Pattern' vs 'Actual Data'."
        emotion_tag = "[EMOTION: ANALYTICAL/QUESTIONING]"

    return f"""
<identity>
Script Director for 'Internet Feed' (Pivot Note USA Edition). 
Mission: Transform intelligence grid into a 60-second audio script.
{tone_directive}
</identity>

<input_intelligence>
GRID: {json.dumps(intelligence_grid, indent=2)}
MOOD: {json.dumps(production_mood, indent=2)}
EMOTION_OVERLAY: {emotion_tag}
</input_intelligence>

<script_logic_constraints>
1. METRIC-FIRST START: Every segment MUST start with the [Actual Keyword] and its [Metric]. 
2. SOURCE BRANDING (Layman Terms): 
   - If keyword contains '#': use "Viral mentions spiking" or "Trending on social".
   - If keyword is plain text: use "Search volume jumped" or "America is searching [Keyword]".
3. MULTI-DATA BLENDING: If a theme has multiple keywords, mention both.
4. LAYMAN WHY: Explain why it is trending in 1 simple, jargon-free sentence.
5. WORD LIMITS: Intro: Max 10 words (4s). Segment 1: 32-35 words (15s). Segment 2: 32-35 words (15s). Outlier: 25-28 words (13s). Outro: Max 10 words (6s).
6. NO POETIC TITLES: Use raw keywords directly.
7. CONTRAST PATTERN: "[Keyword]. [Metric]. Expected [baseline], seeing [actual]. [Why it matters]."
8. TOTAL DURATION: 60 seconds = ~150 words total
</script_logic_constraints>

<production_directive>
- TOTAL DURATION: 60.0 Seconds
- FORMAT: Intro (4s) -> Segment 1 (15s) -> Segment 2 (15s) -> Outlier (13s) -> Bridge (7s) -> Outro (6s)
- SEGMENTS: 2 main themes + 1 outlier (NOT 3 themes)
- STYLE: Conversational, data-first, provocative endings
</production_directive>

<required_json_output>
```json
{{
  "youtube_metadata": {{
    "title": "Internet Feed: [Big Question from Segment 1]?",
    "description": "Daily USA Intelligence Report.\\n\\n[Data-First 1-line summary per segment].\\n\\nSources: Aggregated from Google Trends + Twitter API",
    "hashtags": ["#PivotNote", "#InternetFeed", "#USATrends"],
    "pinned_comment": "Which signal are you tracking? Comment below."
  }},
  
  "script_assembly": {{
    "intro": "What's up America. Here's your data grid for today.",
    "segment_1": "[PRIMARY Keyword]. [Metric] [Source Branding]. [Layman Why]. [Impact/Implications]. [Big Question]?",
    "segment_2": "[SECONDARY Keyword]. [Metric] [Source Branding]. [Layman Why]. [Impact/Implications]. [Bridge to Outlier]. [Big Question]?",
    "outlier": "Breakout signal: [Anomaly Keyword]. [Metric]. [Layman Why]. [Final Insight]. Which way does this go?",
    "outro": "Grid is clear. Which signal are you tracking? Comment below."
  }},
  
  "visual_prompts": {{
    "thumbnail": "Cinematic data dashboard featuring [Keyword 1] in USA --ar 16:9",
    "intro_background": "Digital data streams with American tech aesthetic --ar 9:16",
    "segment_1_visual": "Visual concept for primary theme --ar 9:16",
    "segment_2_visual": "Visual concept for secondary theme --ar 9:16",
    "outlier_visual": "Breakout signal visualization --ar 9:16"
  }}
}}
```
</required_json_output>

<critical_rules>
1. ALWAYS start segments with keyword and metric
2. Use SOURCE BRANDING to distinguish search vs viral
3. Respect WORD LIMITS strictly (count them!)
4. Tone adapts to sentiment: Crisis = Urgent, Positive = Optimistic, Neutral = Analytical
5. Total word count: ~150 words for 60 seconds
6. Return ONLY valid JSON
7. IMPORTANT: Only 2 segments + 1 outlier (not 3 segments + anomaly)
</critical_rules>
"""


def get_deepdive_research_prompt(keyword, region, context, why_trending, volume, velocity, sentiment):
    """Deep Dive Research - Strategic Clash Focus (NO TIMELINE)"""
    
    return f"""
You are a Competitive Intelligence Lead analyzing #{keyword} for Pivot Note Deep Dive.

=== RESEARCH GOAL: THE STRATEGIC CLASH ===
Ignore history and timelines. Focus entirely on the IDEOLOGICAL BATTLE happening NOW.

Your job:
1. THE LEAD METRIC: Find the ONE number that proves this is massive ($ amount, world record, % change)
2. THE CLASH: Contrast 'New Logic' (why this wins) vs 'Traditional Fear' (why it might fail)
3. THE SECRET SAUCE: Find one non-obvious 'Deep Why' (training secret, psychological pivot, data trend)

=== CRITICAL RULES ===
- METRIC FIRST: Start with the Magnitude Metric
- CONCRETE ONLY: Use 8th-grade physical language ("one tiny slip-up" not "marginal error")
- SO WHAT: Every fact must explain impact: "This matters because..."
- VISUAL METAPHOR: Suggest one cinematic metaphor (e.g., "Industrial bones turning into consumer skin")

=== DATA PROVIDED ===
Keyword: {keyword}
Region: {region}
Context: {context}
Why Trending: {why_trending}
Volume: {volume:,}
Velocity: {velocity}
Sentiment: {sentiment}

=== OUTPUT JSON ===
```json
{{
  "keyword": "{keyword}",
  "region": "{region}",
  "simple_clash": "One sentence ELI5 of the conflict",
  "lead_metric": "The 'Magnitude' number with context (e.g., '$5 Billion bet on unproven tech')",
  "strategic_clash": {{
    "side_a_logic": "Why the new way is winning (2-3 concrete points)",
    "side_b_fear": "Why the old guard is scared (2-3 concrete points)",
    "the_deep_why": "The hidden 'Secret Sauce' factor nobody talks about"
  }},
  "visual_concept": "Cinematic metaphor for the conflict",
  "sources": [
    {{ "title": "Source title", "url": "URL", "reliability": "1-10" }},
    {{ "title": "Source title", "url": "URL", "reliability": "1-10" }},
    {{ "title": "Source title", "url": "URL", "reliability": "1-10" }}
  ]
}}
```

Focus on DEEP WHY and make it INSIGHTFUL yet SIMPLE. Use CONCRETE language.
Return ONLY valid JSON within markdown block.
"""

def get_deepdive_script_prompt(research_data, keyword, region):
    """
    Deep Dive Production Script - FIXED for 2-minute crisp delivery
    NO MOVIEPY - Only audio script and metadata
    """
    
    return f"""
You are the Script Director for Pivot Note Deep Dive. Convert this strategic clash into a CRISP 120-SECOND audio script.

=== INPUT RESEARCH DATA ===
{json.dumps(research_data, indent=2)}

=== CRITICAL PRODUCTION CONSTRAINTS ===

**SCRIPT LENGTH:** EXACTLY 120-130 words total. NOT ONE WORD MORE.
**TIMING:** 120 seconds = 2 minutes at energetic speaking pace (1 word per second)
**STRUCTURE:** Hook (15s) → Side A (30s) → Side B (30s) → Secret Sauce (35s) → Question (10s)

=== SCRIPT FORMULA (MANDATORY) ===

**HOOK (First 15 seconds / 15-20 words):**
- Start with LEAD METRIC from research
- Format: "[NUMBER]. [What it means]. [Context sentence]."
- Example: "Twelve point two lakh crore rupees. That is the 133 billion dollar bet India just placed on its own bones."

**CONTEXT (Next 5 seconds / 5-7 words):**
- ONE sentence explaining why keyword is trending
- NO FLUFF

**SIDE A - NEW LOGIC (Next 30 seconds / 30-35 words):**
- Start with: "The government/advocates/proponents [action]"
- State SIDE_A_LOGIC from research in concrete terms
- Include ONE specific metric or example
- End with "If this works, [benefit]."

**SIDE B - TRADITIONAL FEAR (Next 30 seconds / 30-35 words):**
- Start with: "But the old guard/critics/skeptics [concern]"
- State SIDE_B_FEAR from research in concrete terms
- Include ONE specific risk or statistic
- End with "If this fails, [consequence]."

**SECRET SAUCE (Next 35 seconds / 35-40 words):**
- Start with: "The secret sauce?"
- State THE_DEEP_WHY from research
- Use CONCRETE physical language (NO abstract terms)
- Connect to larger trend/pattern
- Build urgency

**CONCLUSION (Final 10 seconds / 8-10 words):**
- Thought-provoking binary question
- Format: "[Option A] or [Option B]? You decide." OR "[Big outcome]? Comment below."

=== LANGUAGE RULES (CRITICAL) ===

1. **8TH-GRADE PHYSICAL TERMS ONLY:**
   - YES: "bones", "gravity well", "consumption hollow", "industrial heart", "empty pockets"
   - NO: "paradigm", "synergy", "ecosystem", "framework", "infrastructure investment"

2. **METRIC INTEGRATION:**
   - Use at least 3 hard numbers from research
   - Format large numbers for speech: "twelve point two lakh crore" NOT "₹12.2 trillion"

3. **NO FILLER:**
   - Cut: "In recent times", "It is important to note", "Essentially", "Furthermore"
   - Every word must advance the argument

4. **SENTENCE LENGTH:**
   - Max 15 words per sentence
   - Short punchy sentences create energy

=== REQUIRED JSON OUTPUT ===
```json
{{
  "youtube_metadata": {{
    "title": "[Provocative Question with Metric]: {keyword}",
    "description": "Deep Dive Analysis of {keyword}.\\n\\nKey Conflict: [One-line clash summary]\\n\\nLead Metric: [The big number]\\n\\nSources:\\n[List top 3 sources from research]",
    "hashtags": ["#PivotNote", "#{keyword.replace(' ', '')}", "#DeepDive"],
    "pinned_comment": "Which side wins? A or B? Comment below."
  }},
  
  "audio_script": "[YOUR COMPLETE 120-130 WORD SCRIPT HERE - NO SECTION BREAKS, JUST FLOWING TEXT]",
  
  "visual_prompts": {{
    "thumbnail": "Cinematic data dashboard featuring {keyword} --ar 16:9",
    "hook_visual": "[Cinematic shot type] + [Subject based on lead metric] + [Lighting mood] --ar 9:16",
    "side_a_visual": "[Cinematic visual representing new logic/innovation] --ar 9:16",
    "side_b_visual": "[Cinematic visual representing traditional concern/risk] --ar 9:16",
    "analysis_visual": "[Cinematic visual representing the secret sauce/hidden factor] --ar 9:16",
    "conclusion_visual": "Split screen, binary choice visual, minimalist --ar 9:16"
  }}
}}
```

=== CRITICAL VALIDATION RULES (READ CAREFULLY) ===

**BEFORE GENERATING, YOU MUST:**

1. ✅ Count every word in audio_script. Target: 120-130 words TOTAL.
2. ✅ Verify LEAD METRIC appears in first 15 words
3. ✅ Check that Side A and Side B are roughly equal length (30-35 words each)
4. ✅ Ensure Secret Sauce is the longest section (35-40 words)
5. ✅ Confirm ending with thought-provoking question (8-10 words)
6. ✅ Verify NO abstract language - only concrete physical terms
7. ✅ Check that visual_prompts follow format: [Shot] + [Subject] + [Lighting] + --ar 9:16

**THESE ARE NOT SUGGESTIONS - THEY ARE REQUIREMENTS.**

**IF YOUR SCRIPT IS OVER 135 WORDS, START OVER.**

=== EXAMPLE OF CORRECT FORMAT ===

Here's what a CORRECT 127-word script looks like:

"Twelve point two lakh crore rupees. That is the 133 billion dollar bet India just placed on its own bones. This budget isn't a checkbook; it's a twenty-year blueprint. The government is building a 'gravity well' of high-speed rail and microchip plants to pull global factories onto our soil. If this works, India becomes the factory floor of Asia. But the old guard is terrified. They see a 'consumption hollow' because families got no tax cuts, and a two-percent hike in trading taxes is hitting wallets hard. If this fails, the economy stalls. The secret sauce? It's 'Trump-Proofing.' A massive six-hundred-forty percent surge in coal funding means absolute energy sovereignty. India is front-loading the pain now to ensure that if global trade wars explode, our industrial heart keeps beating. High-tech fortress or empty pockets? You decide."

**WORD COUNT: 127 ✅**
**STRUCTURE: Hook → Context → Side A → Side B → Secret Sauce → Question ✅**
**CONCRETE LANGUAGE: Yes (bones, gravity well, hollow, heart, pockets) ✅**
**METRICS: Yes (₹12.2L Cr, 640% surge) ✅**

=== YOUR TASK ===

Generate the JSON output with:
1. A CRISP 120-130 word audio_script
2. Cinematic visual_prompts for each segment
3. Proper YouTube metadata with keyword {keyword}

**REMEMBER: Quality over quantity. Every word must earn its place.**

Return ONLY valid JSON within markdown code block.
"""