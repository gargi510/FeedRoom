"""
Prompt Updater - Production Grade
FIXED: Proper region handling for assembly prompts
"""
import os
import shutil
from datetime import datetime
import re


def backup_prompts_file():
    """Create timestamped backup of prompts.py"""
    try:
        if not os.path.exists('prompts.py'):
            return False, "❌ prompts.py not found"
        
        # Create backups folder
        if not os.path.exists('backups'):
            os.makedirs('backups')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"backups/prompts_{timestamp}.py"
        
        shutil.copy('prompts.py', backup_path)
        return True, f"✅ Backup created: {backup_path}"
        
    except Exception as e:
        return False, f"❌ Backup failed: {str(e)}"


def update_analysis_prompt(**kwargs):
    """
    Update get_analysis_prompt() sections
    
    Args:
        identity: Identity block text
        mission: Mission block text
        exec_summary: Executive summary instruction
        weather_grid: Weather grid instruction
        india_intel: India intelligence categories
        usa_intel: USA intelligence categories
        rules: Critical rules
    """
    try:
        with open('prompts.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the function
        pattern = r'def get_analysis_prompt\(data_summary\):.*?(?=\ndef |\nclass |\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            return False, "❌ Could not find get_analysis_prompt function"
        
        original_func = match.group(0)
        updated_func = original_func
        
        # Update sections
        if 'identity' in kwargs:
            updated_func = re.sub(
                r'<identity>.*?</identity>',
                f'<identity>\n{kwargs["identity"]}\n</identity>',
                updated_func,
                flags=re.DOTALL
            )
        
        if 'mission' in kwargs:
            updated_func = re.sub(
                r'<mission>.*?</mission>',
                f'<mission>\n{kwargs["mission"]}\n</mission>',
                updated_func,
                flags=re.DOTALL
            )
        
        if 'rules' in kwargs:
            updated_func = re.sub(
                r'<rules>.*?</rules>',
                f'<rules>\n{kwargs["rules"]}\n</rules>',
                updated_func,
                flags=re.DOTALL
            )
        
        # Replace in content
        content = content.replace(original_func, updated_func)
        
        # Write back
        with open('prompts.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, "✅ Analysis prompt updated successfully"
        
    except Exception as e:
        return False, f"❌ Update failed: {str(e)}"


def update_assembly_prompt(region, **kwargs):
    """
    Update get_assembly_prompt_india() or get_assembly_prompt_usa()
    
    FIXED: Proper region handling
    
    Args:
        region: 'India' or 'USA'
        tone_negative: Tone for negative sentiment
        tone_positive: Tone for positive sentiment
        tone_neutral: Tone for neutral sentiment
        identity: Identity block
        script_constraints: Script logic constraints
        production: Production directive
        youtube_meta: YouTube metadata format
        script_assembly: Script assembly format
        critical_rules: Critical rules
    """
    try:
        with open('prompts.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Determine function name based on region
        if region == 'India':
            func_name = 'get_assembly_prompt_india'
        elif region == 'USA':
            func_name = 'get_assembly_prompt_usa'
        else:
            return False, f"❌ Invalid region: {region}. Must be 'India' or 'USA'"
        
        # Find the function
        pattern = f'def {func_name}\\(intelligence_grid, production_mood\\):.*?(?=\\ndef |\\nclass |\\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            return False, f"❌ Could not find {func_name} function"
        
        original_func = match.group(0)
        updated_func = original_func
        
        # Update tone sections
        if 'tone_negative' in kwargs:
            updated_func = re.sub(
                r'if sentiment < -0\.6:.*?emotion_tag = .*?\n',
                f'if sentiment < -0.6:\n        tone_directive = "{kwargs["tone_negative"]}"\n        emotion_tag = "[EMOTION: GRAVITY/URGENCY]"\n',
                updated_func,
                flags=re.DOTALL
            )
        
        if 'tone_positive' in kwargs:
            updated_func = re.sub(
                r'elif sentiment > 0\.4:.*?emotion_tag = .*?\n',
                f'elif sentiment > 0.4:\n        tone_directive = "{kwargs["tone_positive"]}"\n        emotion_tag = "[EMOTION: EXCITEMENT/VIBRANCE]"\n',
                updated_func,
                flags=re.DOTALL
            )
        
        if 'tone_neutral' in kwargs:
            updated_func = re.sub(
                r'else:.*?tone_directive = .*?emotion_tag = .*?\n',
                f'else:\n        tone_directive = "{kwargs["tone_neutral"]}"\n        emotion_tag = "[EMOTION: SKEPTICAL/WITTY]"\n',
                updated_func,
                flags=re.DOTALL
            )
        
        # Update identity
        if 'identity' in kwargs:
            updated_func = re.sub(
                r'<identity>.*?</identity>',
                f'<identity>\n{kwargs["identity"]}\n</identity>',
                updated_func,
                flags=re.DOTALL
            )
        
        # Update script constraints
        if 'script_constraints' in kwargs:
            updated_func = re.sub(
                r'<script_logic_constraints>.*?</script_logic_constraints>',
                f'<script_logic_constraints>\n{kwargs["script_constraints"]}\n</script_logic_constraints>',
                updated_func,
                flags=re.DOTALL
            )
        
        # Update production directive
        if 'production' in kwargs:
            updated_func = re.sub(
                r'<production_directive>.*?</production_directive>',
                f'<production_directive>\n{kwargs["production"]}\n</production_directive>',
                updated_func,
                flags=re.DOTALL
            )
        
        # Update critical rules
        if 'critical_rules' in kwargs:
            updated_func = re.sub(
                r'<critical_rules>.*?</critical_rules>',
                f'<critical_rules>\n{kwargs["critical_rules"]}\n</critical_rules>',
                updated_func,
                flags=re.DOTALL
            )
        
        # Replace in content
        content = content.replace(original_func, updated_func)
        
        # Write back
        with open('prompts.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, f"✅ {region} assembly prompt updated successfully"
        
    except Exception as e:
        return False, f"❌ Update failed: {str(e)}"


def update_deepdive_research_prompt(**kwargs):
    """
    Update get_deepdive_research_prompt()
    
    Args:
        research_goal: Research goal section
        output_req: Output requirements
        language_rules: Language rules
    """
    try:
        with open('prompts.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the function
        pattern = r'def get_deepdive_research_prompt\(.*?\):.*?(?=\ndef |\nclass |\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            return False, "❌ Could not find get_deepdive_research_prompt function"
        
        original_func = match.group(0)
        updated_func = original_func
        
        # Update sections
        if 'research_goal' in kwargs:
            updated_func = re.sub(
                r'=== RESEARCH GOAL: THE STRATEGIC CLASH ===.*?(?=Your job:)',
                f'=== RESEARCH GOAL: THE STRATEGIC CLASH ===\n{kwargs["research_goal"]}\n\n',
                updated_func,
                flags=re.DOTALL
            )
        
        if 'language_rules' in kwargs:
            updated_func = re.sub(
                r'=== CRITICAL RULES ===.*?(?==== DATA PROVIDED ===)',
                f'=== CRITICAL RULES ===\n{kwargs["language_rules"]}\n\n',
                updated_func,
                flags=re.DOTALL
            )
        
        # Replace in content
        content = content.replace(original_func, updated_func)
        
        # Write back
        with open('prompts.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, "✅ Deep dive research prompt updated successfully"
        
    except Exception as e:
        return False, f"❌ Update failed: {str(e)}"


def update_deepdive_script_prompt(**kwargs):
    """
    Update get_deepdive_script_prompt()
    
    Args:
        script_structure: Script structure
        word_count: Word count target
        hook_formula: Hook formula
        lang_rules: Language rules
    """
    try:
        with open('prompts.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find the function
        pattern = r'def get_deepdive_script_prompt\(.*?\):.*?(?=\ndef |\nclass |\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            return False, "❌ Could not find get_deepdive_script_prompt function"
        
        original_func = match.group(0)
        updated_func = original_func
        
        # Update sections
        if 'script_structure' in kwargs:
            updated_func = re.sub(
                r'\*\*STRUCTURE:\*\* .*?\n',
                f'**STRUCTURE:** {kwargs["script_structure"]}\n',
                updated_func
            )
        
        if 'word_count' in kwargs:
            updated_func = re.sub(
                r'\*\*SCRIPT LENGTH:\*\* .*?\n',
                f'**SCRIPT LENGTH:** {kwargs["word_count"]}\n',
                updated_func
            )
        
        # Replace in content
        content = content.replace(original_func, updated_func)
        
        # Write back
        with open('prompts.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True, "✅ Deep dive script prompt updated successfully"
        
    except Exception as e:
        return False, f"❌ Update failed: {str(e)}"


# Test function
if __name__ == "__main__":
    print("Prompt Updater - Production Grade")
    print("=" * 50)
    
    # Test backup
    success, msg = backup_prompts_file()
    print(msg)
    
    if success:
        print("\n✅ Prompt updater is working correctly")
        print("💡 Use this module in your Streamlit fine-tuner UI")