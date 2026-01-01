import json
import os

_base = os.path.dirname(__file__)
_templates_path = os.path.join(_base, 'templates.json')
_state_path = os.path.join(_base, 'last_prompt.json')

def load_templates():
    try:
        with open(_templates_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        # fallback defaults
        return {
            'sad': "Aap thoda udaas lag rahe hain. Kya aap batayenge ki aap kyun udaas hain?",
            'happy': "Aap khush dikh rahe hain! Kya aap kuch achha share karna chahenge?",
            'neutral': "Aap bilkul theek lag rahe hain. Kya main aapki madad kar sakta hoon?",
            'angry': "Aap gusse mein lag rahe hain. Kya aap batayenge ki kya hua?",
            'surprise': "Aap pareshaan ya chakit dikh rahe hain. Kya sab theek hai?",
            'working': "Aap kaam mein vyast lag rahe hain — aap kya kar rahe hain abhi?",
            'generic': "Maine aapka mood '{mood}' detect kiya. Kya aap kuch share karna chahenge?",
        }

def save_last_prompt_timestamp(ts: float):
    try:
        with open(_state_path, 'w', encoding='utf-8') as f:
            json.dump({'last_prompt': ts}, f)
        return True
    except Exception:
        return False

def load_last_prompt_timestamp():
    try:
        with open(_state_path, 'r', encoding='utf-8') as f:
            obj = json.load(f)
            return float(obj.get('last_prompt', 0))
    except Exception:
        return 0.0
