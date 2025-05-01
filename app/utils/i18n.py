import os
import json

def load_translations(lang):
    try:
        path = os.path.join('app', 'translations', f'messages_{lang}.json')
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}