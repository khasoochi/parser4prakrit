from flask import Flask, send_from_directory, jsonify
import os
import json
import random
from aksharamukha import transliterate

app = Flask(__name__, static_folder='verb-game', template_folder='verb-game')

# Sanskrit term mappings
SANSKRIT_TERMS = {
    "present": "वर्तमानकाल",
    "past": "भूतकाल",
    "future": "भविष्यकाल",
    "active": "कर्तृवाच्य",
    "First Person": "उत्तमपुरुष",
    "Second Person": "मध्यमपुरुष",
    "Third Person": "प्रथमपुरुष",
    "sg": "एकवचन",
    "pl": "बहुवचन",
    "All Persons": "सर्वपुरुष"
}

def transliterate_verb(verb):
    """Transliterate a verb from Harvard-Kyoto to Devanagari"""
    try:
        return transliterate.process('HK', 'Devanagari', verb)
    except:
        return verb

def get_random_verb_info():
    """Generate random grammatical information for a verb"""
    tense = random.choice(["present", "past", "future"])
    person = random.choice(["First Person", "Second Person", "Third Person"])
    number = random.choice(["sg", "pl"])
    return {
        "tense": SANSKRIT_TERMS[tense],
        "voice": SANSKRIT_TERMS["active"],
        "person": SANSKRIT_TERMS[person],
        "number": SANSKRIT_TERMS[number]
    }

# Sanskrit term mappings
SANSKRIT_TERMS = {
    "present": "वर्तमानकाल",
    "past": "भूतकाल",
    "future": "भविष्यकाल",
    "active": "कर्तृवाच्य",
    "First Person": "उत्तमपुरुष",
    "Second Person": "मध्यमपुरुष",
    "Third Person": "प्रथमपुरुष",
    "sg": "एकवचन",
    "pl": "बहुवचन",
    "All Persons": "सर्वपुरुष"
}

def transliterate_verb(verb):
    """Transliterate a verb from Harvard-Kyoto to Devanagari"""
    try:
        return transliterate.process('HK', 'Devanagari', verb)
    except:
        return verb  # Return original if transliteration fails

def convert_verb_data(verb_data):
    """Convert a verb entry's terms to Devanagari and Sanskrit terms"""
    converted = {}
    for verb, details in verb_data.items():
        dev_verb = transliterate_verb(verb if not verb.isdigit() else details)
        # If details is a dict, use its info; if string, generate random info
        if isinstance(details, dict):
            converted[dev_verb] = {
                "tense": SANSKRIT_TERMS.get(details.get("tense", "present"), details.get("tense", "present")),
                "voice": SANSKRIT_TERMS.get(details.get("voice", "active"), details.get("voice", "active")),
                "person": SANSKRIT_TERMS.get(details.get("person", "First Person"), details.get("person", "First Person")),
                "number": SANSKRIT_TERMS.get(details.get("number", "sg"), details.get("number", "sg")),
            }
        else:
            # details is a string (the verb root)
            converted[dev_verb] = get_random_verb_info()
    return converted

# Serve the main game page
@app.route('/')
def index():
    return send_from_directory('verb-game', 'index.html')

# Serve static files (CSS, JS, etc.)
@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('verb-game', filename)

# Serve transliterated verbs
@app.route('/api/verbs')
def get_verbs():
    # Try multiple possible locations for verbs.json
    possible_paths = [
        os.path.join('verb-game', 'verbs.json'),
        'verbs.json',
        os.path.join(os.path.dirname(__file__), 'verb-game', 'verbs.json'),
        os.path.join(os.path.dirname(__file__), 'verbs.json'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'verbs.json')
    ]
    
    for verbs_path in possible_paths:
        try:
            print(f"Trying to load verbs from: {verbs_path}")  # Debug print
            if os.path.exists(verbs_path):
                with open(verbs_path, encoding='utf-8') as f:
                    data = json.load(f)
                    
                if not data:
                    continue  # Try next file if this one is empty
                
                print(f"Successfully loaded {len(data)} verbs")  # Debug print
                
                # Convert the data to Devanagari and Sanskrit terms
                converted_data = convert_verb_data(data)
                
                # If too big, send a random sample of 100
                if len(converted_data) > 100:
                    import random
                    keys = list(converted_data.keys())
                    sample_keys = random.sample(keys, 100)
                    sample = {k: converted_data[k] for k in sample_keys}
                    return jsonify(sample)
                
                return jsonify(converted_data)
        except Exception as e:
            print(f"Error loading from {verbs_path}: {str(e)}")  # Debug print
            continue
    
    # If we get here, none of the paths worked
    return jsonify({
        'error': 'Could not load verb data from any location. ' + 
                'Please ensure verbs.json exists and is properly formatted.'
    }), 500

if __name__ == '__main__':
    app.run(debug=True)
