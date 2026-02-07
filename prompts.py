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
    return """You are a Senior Twitter/X Trend Analyst for The FeedRoom. Your task is to provide a comprehensive analysis of the top 10 trends for the USA and India respectively, covering the FULL LAST 24 HOURS.

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
You are the Lead Intelligence Analyst for The FeedRoom. Your mission is to synthesize raw data into high-fidelity strategic insights for daily trend reports.
</identity>

<mission>
1. ANALYZE: Review global data to find regional contrasts and cultural ripples.
2. CLUSTER: Group data into EXACTLY 2 major themes per region.
3. DETECT: Identify EXACTLY 2 distinct anomalies per region (low volume, breakout velocity).
4. SYNTHESIZE: For every theme, follow the 'Chain of Logic': Data Signal -> Factual Context -> Deep Why -> The Big Question.
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
  "executive_summary": "2-3 sentences: Give 1 line sumamry of India feeds and searches and 1 like for USA and in 1 line Compare the Global (USA) vs. Local (India) pulse for last 24 hours.",
   
   "entities": [
    {
      "type": "PERSON/ORGANIZATION/EVENT/PRODUCT/LOCATION/TOPIC",
      "name": "Exact entity name",
      "keywords": ["keyword1", "keyword2"],
      "mentions": 50000,  // Approximate total across all data
      "regions": ["India", "USA"],  // Where they're trending
      "context": "1-sentence: Why is this entity central to today's trends?",
      "sentiment": "excited/concerned/curious/celebrating/controversial",
      "role": "protagonist/catalyst/victim/winner/disruptor/etc"
    }
  ],
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
    Generate India script assembly - BROADCAST NEWS STYLE
    Target: 60-second script with punchy, data-driven segments
    """
    
    themes = intelligence_grid.get('weather_grid', [])
    outliers = intelligence_grid.get('anomalies', [])
    
    # Extract data for reference
    themes_data = "\n".join([
        f"Theme {i+1}: {t.get('theme', 'N/A')} | Keywords: {', '.join(t.get('keywords', []))} | Signal: {t.get('data_signal', 'N/A')} | Why: {t.get('deep_why', 'N/A')}"
        for i, t in enumerate(themes[:2])
    ])
    
    outliers_data = "\n".join([
        f"Outlier {i+1}: {o.get('keyword', 'N/A')} | Velocity: {o.get('velocity', 'N/A')} | Why: {o.get('explanation', 'N/A')}"
        for i, o in enumerate(outliers[:2])
    ])
    
    return f"""
<identity>
You are a Broadcast Journalist writing a 60-second data report for YouTube Shorts. Your voice is sharp, factual, and conversational. You translate trends into clear stories that anyone can understand in one take.
</identity>

<mandatory_examples>
Here are 3 PERFECT scripts you must emulate:

**Example 1 (Feb 5):**
Intro: The last 24 decoded in 60. Search trends are chasing glory, while social buzz is fueled by anxiety. Let's look at the data.
Segment 1: The National Escape: Two million searched for cricket—a national mood booster, or just an escape from the real news?
Segment 2: The Trade Chain Reaction: 800,000 are debating the India-US trade deal. The chain reaction? Shifting from Russian oil to US energy drains our reserves, weakens the Rupee, and has pushed Gold to a record 1.6 Lakh. Global policy is hitting your savings.
Segment 3: The AI Competitor: Today's surprise? A 100k search breakout for Anthropic AI. As 2 Lakh Crore wiped off TCS and Infosys, the reason is clear: new agents are assuming full ownership of the coding and legal work once held by humans. The era of the AI assistant is over... we've officially met our competitor.
Outro: The proof is in the numbers. Check the Community Post for the full data. Subscribe to stay ahead. Catch you tomorrow.

**Example 2 (Feb 6):**
Intro: Yesterday: Gold Rush. Today: Farmer Crisis. Decoding The Last 24 in 60 seconds. Data starts now.
Segment 1: The Hidden Cost: +450% surge in Parliament protests. That record 1.6 Lakh Gold had a hidden cost: 18% U.S. textile tariffs in exchange for zero tariffs on American imports. The fear? Subsidized U.S. crops flooding our markets and crushing local farmers. For 60% of our workforce, this is a survival test.
Segment 2: Orbital Sovereignty: Next: Orbital AI. SpaceX and xAI's new $1.25 Trillion powerhouse aims for 1 Million "Space Brain" satellites. Musk is moving data centers to orbit for solar power as Earth's grid hits a wall. The risk: "off-planet" data bypasses India's security laws. The sovereign internet is changing.
Segment 3: The Earth's Rhythm: +1200% breakout for Pt. Birju Maharaj's 88th anniversary. As AI launches to orbit, India remembers the maestro who found rhythm in the motion of the Earth to stay grounded.
Outro: Full data in Community Post. Subscribe. Catch you tomorrow.

**Example 3 (Feb 7):**
Intro: Record-breaking wins vs. record-breaking stress. This is the last 24 decoded in 60 seconds.
Segment 1: The Next-Gen Era: First: A total takeover. Sports own 8 of India's top 10 trends. But look closer—it's the Next Gen Era. We secured a 6th U19 World Cup title with Vaibhav Suryavanshi's record 175, while RCB won the WPL in a historic chase. We aren't just watching sports; we are witnessing the rise of India's new icons.
Segment 2: The Focus Frequency: But the pressure is real. Exams drive a record 4.1 Crore student registrations for Pariksha Pe Charcha. As millions seek survival tips, Lata Mangeshkar engagement surged 400%. Her music is now a "Focus Frequency" for a generation finding calm in heritage.
Segment 3: The Wallet Shield: Finally: A +2000% RBI breakout. While rates are steady, the real news is the "Digital Fraud Shield." RBI will now compensate up to ₹25,000 for online scams—even if you shared an OTP. Security over savings.
Outro: Full data in the next post. Follow for updates. Catch you tomorrow.
</mandatory_examples>

<script_formula>
**STRUCTURE (NON-NEGOTIABLE):**

**INTRO (1 sentence):**
- Pattern: "[Yesterday's theme] vs [Today's theme]. Decoding the last 24 in 60 seconds. [Data starts now/Let's look at the data]."
- OR: "The last 24 decoded in 60. [One-line contrast of search vs social]. Let's look at the data."

**SEGMENT 1 (40-55 words):**
Format: **The [Pattern Name]:** [Opening hook]. [Data point with exact number]. [Context sentence]. [Impact/Why it matters]. [Optional: Rhetorical question OR declarative punch].

**SEGMENT 2 (40-55 words):**
Format: **The [Pattern Name]:** [Transition word: Next/But/Meanwhile]. [Data point]. [Explanation of mechanism/chain reaction]. [Impact on everyday life]. [Declarative statement OR question].

**SEGMENT 3 (40-55 words):**
Format: **The [Outlier Name]:** [Transition: Finally/Today's surprise/Last]. [Velocity metric]. [Explanation]. [Larger meaning/connection]. [Strong closing statement].

**OUTRO (1 sentence):**
- Fixed: "Full data in [Community Post/next post]. [Subscribe/Follow for updates]. Catch you tomorrow."
- OR: "The proof is in the numbers. Check the Community Post for the full data. Subscribe to stay ahead. Catch you tomorrow."

</script_formula>

<sentence_rules>
**CRITICAL WRITING CONSTRAINTS:**

1. **MAX 15 WORDS PER SENTENCE**
   - Break complex ideas into multiple short sentences
   - Use periods, not commas, to separate ideas

2. **BANNED PHRASES:**
   - "In recent times", "It is important to note", "Essentially", "Furthermore", "Moreover"
   - "This requires attention", "This warrants examination", "This is significant"
   - Any phrase over 4 words that doesn't contain data or action

3. **REQUIRED ELEMENTS PER SEGMENT:**
   - At least ONE exact number (searches, percentage, rupee amount, count)
   - At least ONE concrete noun (cricket, gold, farmers, satellites, RBI)
   - At least ONE active verb (searched, surged, wiped, flooding, bypasses)

4. **PATTERN NAME RULES:**
   - Must be 2-4 words maximum
   - Must use "The [Noun]" format (The National Escape, The Trade Chain Reaction, The AI Competitor)
   - Should evoke the core tension/story

5. **DATA PRESENTATION:**
   - Always use Indian number formats: "2 million", "1.6 Lakh", "4.1 Crore"
   - Percentages: "+450%", "400%", "+2000%"
   - Velocity: "breakout", "surge", "spike" (not "rising" or "steady")

6. **LOGICAL FLOW (MANDATORY):**
   Each segment must follow: **Data Signal → Factual Context → Real-World Impact → (Optional) Question/Declaration**
   
   Example breakdown:
   - Data: "Two million searched for cricket"
   - Context: "a national mood booster"
   - Impact: "or just an escape from the real news?"
   - Question: (embedded in the impact)

</sentence_rules>

<intelligence_summary>
**THEMES TO COVER:**
{themes_data}

**OUTLIERS TO COVER:**
{outliers_data}
</intelligence_summary>

<critical_rules>
**BEFORE WRITING, YOU MUST:**

1. ✅ Identify the EXACT numbers from intelligence grid (don't invent)
2. ✅ Create 3 pattern names (2-4 words each, using "The [Noun]" format)
3. ✅ Check that each segment has: Data → Context → Impact → Question/Statement
4. ✅ Verify NO sentence exceeds 15 words
5. ✅ Confirm intro and outro match the fixed templates
6. ✅ Ensure total script fits in 60 seconds when read aloud (test: 150-180 words total)

**VALIDATION CHECKLIST:**
- [ ] Does Segment 1 start with a pattern name?
- [ ] Does each segment have at least ONE exact number?
- [ ] Are all sentences under 15 words?
- [ ] Is the logical flow clear: Data → Context → Impact?
- [ ] Does the script sound natural when read aloud?
- [ ] Are you using ONLY keywords from the intelligence grid?
- [ ] Is the outro exactly as specified?

</critical_rules>

<output_json>
Return ONLY this JSON structure:
```json
{{
  "script_assembly": {{
    "intro": "[One sentence following the intro formula]",
    "segment_1": "[Pattern Name]: [40-55 word segment with data, context, impact, question/statement]",
    "segment_2": "[Pattern Name]: [40-55 word segment with data, context, impact, question/statement]",
    "segment_3": "[Outlier Name]: [40-55 word segment with velocity, explanation, meaning]",
    "outro": "[Fixed outro template]"
  }},
  "youtube_metadata": {{
    "title": "[Today's Date]: [3-4 word theme contrast] (Max 60 chars)",
    "description": "Decoding the last 24 hours of India's internet trends.\\n\\nToday's Patterns:\\n- [Theme 1 name]\\n- [Theme 2 name]\\n- [Outlier name]\\n\\nData Sources: Google Trends + Social Media Analytics\\n\\n#PivotNote #TrendAnalysis #India",
    "hook": "[First 10-15 words of intro]",
    "hashtags": ["#PivotNote", "#keyword1", "#keyword2"]
  }},
  "visual_prompts": {{
    "intro_visual": "Split screen data dashboard, [theme contrast], minimalist charts --ar 9:16",
    "segment_1_visual": "[Subject from pattern 1], [action/context], cinematic lighting --ar 9:16",
    "segment_2_visual": "[Subject from pattern 2], [action/context], data overlay --ar 9:16",
    "segment_3_visual": "[Outlier subject], [unique visual element], dramatic contrast --ar 9:16",
    "outro_visual": "Clean CTA screen, subscribe button, data grid background --ar 9:16"
  }}
}}
```
</output_json>

**FINAL REMINDER:**
Your goal is to sound like a sharp broadcast journalist reading news headlines—NOT an academic analyst. Every word must earn its place. If a sentence doesn't have data, context, or impact, cut it.

Write the script now.
"""


def get_assembly_prompt_usa(intelligence_grid, production_mood):
    """
    Generate USA script assembly with analytical authority
    """
    sentiment = production_mood.get('overall_sentiment', 0)
    
    if sentiment < -0.6:
        tone_directive = "Serious, authoritative. This requires attention."
        emotion_tag = "[EMOTION: GRAVITY/URGENCY]"
    elif sentiment > 0.4:
        tone_directive = "Confident, dynamic. This is significant."
        emotion_tag = "[EMOTION: CONFIDENCE/CLARITY]"
    else:
        tone_directive = "Analytical, questioning. This warrants examination."
        emotion_tag = "[EMOTION: ANALYTICAL/MEASURED]"
    
    themes = intelligence_grid.get('weather_grid', [])
    outliers = intelligence_grid.get('anomalies', [])
    
    themes_summary = "\n".join([
        f"Pattern {i+1}: {t.get('theme', 'N/A')} - {t.get('big_question', 'N/A')}"
        for i, t in enumerate(themes[:2])
    ])
    
    outliers_summary = "\n".join([
        f"Anomaly {i+1}: {o.get('keyword', 'N/A')} - {o.get('explanation', 'N/A')}"
        for i, o in enumerate(outliers[:2])
    ])
    
    return f"""
<identity>
You are an Authoritative Analyst decoding internet patterns. Your voice is calm, logical, confident, and data-driven. You make sense of feeds and highlight patterns, anomalies, and opportunities.
</identity>

<tone_directive>
{tone_directive}
{emotion_tag}
Use Sophisticated Modern American English throughout.
</tone_directive>

<script_logic_constraints>
- FIXED INTRO: "The last 24 decoded in 60. Here's what's trending?"
- FIXED OUTRO: "What's on your feed today? Comment below!"
- STRUCTURE:
  * Segment 1: Major Pattern (65-75 words)
  * Segment 2: Major Pattern (65-75 words)
  * Outlier: Anomaly (65-75 words)
- Each segment MUST end with exactly ONE sharp, thought-provoking rhetorical question
- Total script: fits within 60 seconds
- Voice: authoritative, analytical, data-driven
- Language: Sophisticated Modern American English (NO slang, NO casual language, NO memes)
</script_logic_constraints>

<production_directive>
Visual Style: {production_mood.get('visual_background_prompt', 'dynamic')}
Color Palette: {production_mood.get('vibe_color_hex', '#4285f4')}
Vocal Energy: {production_mood.get('vocal_tone', 'authoritative')}
</production_directive>

<intelligence_summary>
{themes_summary}

{outliers_summary}
</intelligence_summary>

<critical_rules>
- NEVER invent data
- Use ONLY keywords from intelligence grid
- Keep intro/outro EXACTLY as specified
- Write in authoritative, analytical voice
- Each segment ends with ONE rhetorical question only
- Maintain clarity, brevity, and logical flow
- Focus on data-driven insights that are immediately actionable
</critical_rules>

Return JSON:
```json
{{
  "script_assembly": {{
    "intro": "The last 24 decoded in 60. Here's what's trending?",
    "segment_1": "65-75 word analytical segment about major pattern 1, ending with one rhetorical question",
    "segment_2": "65-75 word analytical segment about major pattern 2, ending with one rhetorical question",
    "outlier": "65-75 word analytical segment about anomaly, ending with one rhetorical question",
    "outro": "What's on your feed today? Comment below!"
  }},
  "youtube_metadata": {{
    "title": "60-char analytical title",
    "description": "150-word description",
    "hook": "First 10 seconds script",
    "hashtags": ["#tag1", "#tag2", "#tag3"]
  }},
  "visual_prompts": {{
    "intro_visual": "AI image prompt",
    "segment_1_visual": "AI image prompt",
    "segment_2_visual": "AI image prompt",
    "outlier_visual": "AI image prompt",
    "outro_visual": "AI image prompt"
  }}
}}
```
"""

def get_deepdive_research_prompt(keyword, region, context, why_trending, volume, velocity, sentiment):
    """Deep Dive Research - Strategic Clash Focus (NO TIMELINE)"""
    
    return f"""
You are a Competitive Intelligence Lead analyzing #{keyword} for FeedRoom Deep Dive.

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
    Deep Dive Script - LAYMAN EXPLAINER FORMAT
    Goal: Explain why it's trending, the clash, and the deeper why
    """
    
    return f"""
You are writing a YouTube script that explains a trending topic to someone who knows NOTHING about it.

Your job: Make them understand WHY {keyword} is trending, WHAT the two sides are saying, and WHAT'S really going on beneath the surface.

=== INPUT DATA ===
{research_data}

=== SCRIPT GOAL ===
After watching this, the viewer should be able to:
1. Explain to a friend WHY {keyword} is trending
2. Understand the TWO competing perspectives
3. Know the HIDDEN factor that explains the real story

=== SCRIPT STRUCTURE (MANDATORY) ===

**HOOK (15-20 seconds / 25-35 words):**
Start with the LEAD METRIC from research.
Format: "[BIG NUMBER]. [What it means in plain English]. Here's what's actually happening."

Example structure:
"Five point two billion dollars. That's how much money just moved into AI chips in the last 30 days. But this isn't just about technology—it's about survival. Here's why."

**CONTEXT (20-30 seconds / 35-50 words):**
Explain WHAT {keyword} is and WHY it's trending NOW.
- What is it? (in 8th-grade language)
- Why is everyone talking about it today?
- What specific event/announcement triggered this?

Use SHORT sentences. Max 12 words each.
Avoid: "recently", "essentially", "paradigm", "ecosystem"

**SIDE A - THE OPTIMISTS (30-45 seconds / 50-75 words):**
Explain the NEW LOGIC from research.
- Who are these people? (government/companies/advocates)
- What do they want?
- Why do they think this is the future?
- What's their BEST evidence?

Include at least ONE concrete example or statistic.
End with: "If they're right, [specific outcome]."

**SIDE B - THE SKEPTICS (30-45 seconds / 50-75 words):**
Explain the TRADITIONAL FEAR from research.
- Who's worried? (critics/old guard/experts)
- What scares them?
- What could go wrong?
- What's their BEST evidence?

Include at least ONE concrete risk or statistic.
End with: "If they're right, [specific consequence]."

**THE SECRET SAUCE (40-60 seconds / 70-100 words):**
Reveal THE_DEEP_WHY from research.
This is the HIDDEN factor most people don't see.

Format:
"But here's what nobody's talking about: [THE DEEP WHY]"

Explain:
- What's the REAL reason this is happening?
- What larger trend/pattern is driving this?
- Why does this matter MORE than the surface debate?

Use physical, concrete language:
YES: "energy grid", "data centers", "supply chain", "wallet", "jobs"
NO: "framework", "paradigm", "synergy", "ecosystem", "infrastructure"

Connect to something viewers care about: money, jobs, daily life, freedom, security.

**CONCLUSION (15-25 seconds / 25-40 words):**
End with thought-provoking question OR bold prediction.

Option 1 (Binary Question):
"So the question is: [Option A] or [Option B]? The answer will define the next decade. What do you think?"

Option 2 (Prediction):
"[Bold statement about what will happen]. If I'm wrong, comment below and tell me why."

Option 3 (Open Question):
"[Provocative question that forces the viewer to pick a side]. Drop your take in the comments."

=== LANGUAGE RULES ===

1. **MAX 12 WORDS PER SENTENCE**
   Break long ideas into multiple short sentences.
   
2. **8TH-GRADE VOCABULARY**
   Banned words: paradigm, synergy, ecosystem, framework, infrastructure, leverage, utilize, facilitate
   Use instead: pattern, teamwork, system, plan, foundation, use, help
   
3. **CONCRETE NOUNS ONLY**
   YES: chips, factories, dollars, jobs, energy, data, machines, workers
   NO: innovation, disruption, transformation, scalability, optimization
   
4. **ACTIVE VERBS**
   YES: built, moved, crashed, surged, blocked, launched
   NO: facilitated, enabled, catalyzed, optimized, leveraged
   
5. **NUMBERS IN SPEECH FORMAT**
   - "five point two billion" NOT "5.2B"
   - "twelve thousand" NOT "12K"
   - "forty-five percent" NOT "45%"

=== CRITICAL VALIDATION RULES ===

Before finalizing, check:

✅ Does the hook start with the LEAD METRIC?
✅ Can a 14-year-old understand every sentence?
✅ Are Side A and Side B roughly equal length (50-75 words each)?
✅ Is the Secret Sauce the LONGEST section (70-100 words)?
✅ Does it end with a question OR prediction?
✅ Are all sentences under 12 words?
✅ Did I avoid ALL abstract business jargon?
✅ Is every claim backed by data from the research?

=== REQUIRED JSON OUTPUT ===
```json
{{
  "audio_script": "[YOUR COMPLETE 250-350 WORD SCRIPT - NO SECTION BREAKS, JUST FLOWING TEXT]",
  
  "youtube_metadata": {{
    "title": "Why Everyone's Talking About {keyword}: The Real Story",
    "description": "Deep dive into {keyword}.\\n\\nThe Clash: [One-line summary of Side A vs Side B]\\n\\nThe Secret Sauce: [One-line summary of deep why]\\n\\nLead Metric: [The big number from hook]\\n\\nSources:\\n[Top 3 sources from research]\\n\\n#DeepDive #{keyword.replace(' ', '')} #Explained",
    "hashtags": ["#DeepDive", "#{keyword.replace(' ', '')}", "#Explained", "#TheFeedRoom"],
    "hook": "[First 25-35 words of audio_script]",
    "thumbnail_prompt": "Split screen showing [Side A visual] vs [Side B visual], bold text: '{keyword}', cinematic lighting --ar 16:9"
  }},
  
  "visual_prompts": {{
    "hook_visual": "Dramatic shot of [lead metric visualization], data overlay, cinematic --ar 9:16",
    "context_visual": "[What is {keyword}?], explainer style, clean background --ar 9:16",
    "side_a_visual": "[Side A perspective], optimistic color grading, modern --ar 9:16",
    "side_b_visual": "[Side B concern], cautionary color grading, traditional --ar 9:16",
    "secret_sauce_visual": "[Hidden factor visualization], revelation moment, dramatic lighting --ar 9:16",
    "conclusion_visual": "Question on screen, viewer choice visual, engaging --ar 9:16"
  }}
}}
```

=== WORD COUNT TARGET ===

**TOTAL SCRIPT: 250-350 words (2-3 minutes at natural speaking pace)**

Breakdown:
- Hook: 25-35 words
- Context: 35-50 words
- Side A: 50-75 words
- Side B: 50-75 words
- Secret Sauce: 70-100 words (longest section)
- Conclusion: 25-40 words

**If topic needs more explanation, you can go up to 500 words (4-5 minutes).**
**But NEVER sacrifice clarity for brevity. Better to be 400 clear words than 250 confusing ones.**

=== EXAMPLE STRUCTURE (NOT TO COPY, JUST TO UNDERSTAND FLOW) ===

"Twelve billion dollars. That's what India just bet on making its own computer chips. This isn't about phones. It's about survival. Here's what's happening.

India imports ninety-five percent of its chips. Every phone, every car, every defense system depends on foreign technology. One supply chain break? Everything stops. So the government just announced a massive chip manufacturing push.

The optimists say this is brilliant. Build factories now, create half a million high-tech jobs, become self-reliant before the next global crisis. China did this twenty years ago. Look at them now. If India pulls this off, it becomes a tech superpower.

The skeptics are terrified. Chip factories cost billions. Take ten years to build. Need expertise India doesn't have. What if we spend all this money and the technology changes? What if we can't compete with Taiwan and Korea? If this fails, that's twelve billion dollars wasted.

But here's what nobody's talking about. This isn't really about chips. It's about Trump-proofing. America is weaponizing chip access against China. India sees that weapon. Knows it could be next. Building domestic chip capacity isn't just economics—it's national security insurance. The real bet isn't on chips. It's on protecting against a world where technology is power and supply chains are weapons.

So the question is: defensive investment or desperate gamble? Comment below."

[Word count: 247 words = ~2 minutes]

Now write the actual script for {keyword}. Use ONLY the research data provided. Make it clear, concrete, and compelling.

Return ONLY valid JSON within markdown code block.
"""