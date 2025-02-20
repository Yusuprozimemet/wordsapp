import os
import shutil

def create_directory(path):
    os.makedirs(path, exist_ok=True)

def create_file(path, content=''):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def generate_app_structure():
    # Define the base project structure
    directories = [
        'app',
        'app/routes',
        'app/models',
        'app/services',
        'app/static/css',
        'app/static/js',
        'app/static/img',
        'app/templates',
        'app/templates/errors',
        'app/utils',
        'data',
        'tests'
    ]

    # Create directories
    for directory in directories:
        create_directory(directory)

    # Create __init__.py files
    init_files = [
        'app/__init__.py',
        'app/routes/__init__.py',
        'app/models/__init__.py',
        'app/services/__init__.py',
        'app/utils/__init__.py',
        'tests/__init__.py'
    ]

    for init_file in init_files:
        create_file(init_file)

    # Create configuration files
    create_file('config.py', '''
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
    WORDS_FILE = os.path.join(DATA_DIR, 'words.json')
'''.strip())

    create_file('requirements.txt', '''
Flask==2.0.1
Werkzeug==2.0.1
gunicorn==20.1.0
python-dotenv==0.19.0
Flask-WTF==0.15.1
'''.strip())

    create_file('.gitignore', '''
venv/
__pycache__/
*.pyc
.env
data/*.json
.DS_Store
'''.strip())

    create_file('run.py', '''
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
'''.strip())

    # Create app initialization file
    create_file('app/__init__.py', '''
from flask import Flask
from config import Config
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure the data directory exists
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)

    # Initialize empty words file if it doesn't exist
    if not os.path.exists(app.config['WORDS_FILE']):
        with open(app.config['WORDS_FILE'], 'w') as f:
            f.write('[]')

    # Register blueprints
    from app.routes import main, api
    app.register_blueprint(main.bp)
    app.register_blueprint(api.bp, url_prefix='/api')

    return app
'''.strip())

    # Create route files
    create_file('app/routes/main.py', '''
from flask import Blueprint, render_template
from app.services.word_service import WordService

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')
'''.strip())

    create_file('app/routes/api.py', '''
from flask import Blueprint, jsonify, request
from app.services.word_service import WordService

bp = Blueprint('api', __name__)
word_service = WordService()

@bp.route('/words', methods=['GET'])
def get_words():
    words = word_service.get_all_words()
    return jsonify(words)

@bp.route('/words', methods=['POST'])
def add_word():
    word_data = request.json
    word_service.add_word(word_data)
    return jsonify({"message": "Word added successfully"})

@bp.route('/words/<int:index>', methods=['DELETE'])
def delete_word(index):
    success = word_service.delete_word(index)
    if success:
        return jsonify({"message": "Word deleted successfully"})
    return jsonify({"error": "Invalid index"}), 404

@bp.route('/words/<int:index>', methods=['PUT'])
def update_word(index):
    word_data = request.json
    success = word_service.update_word(index, word_data)
    if success:
        return jsonify({"message": "Word updated successfully"})
    return jsonify({"error": "Invalid index"}), 404

@bp.route('/download')
def download_words():
    return word_service.download_words()
'''.strip())

    # Create service file
    create_file('app/services/word_service.py', '''
import json
from flask import current_app, send_file

class WordService:
    def get_all_words(self):
        with open(current_app.config['WORDS_FILE'], 'r') as f:
            return json.load(f)

    def add_word(self, word_data):
        words = self.get_all_words()
        words.append(word_data)
        self._save_words(words)

    def delete_word(self, index):
        words = self.get_all_words()
        if 0 <= index < len(words):
            words.pop(index)
            self._save_words(words)
            return True
        return False

    def update_word(self, index, word_data):
        words = self.get_all_words()
        if 0 <= index < len(words):
            words[index] = word_data
            self._save_words(words)
            return True
        return False

    def download_words(self):
        return send_file(current_app.config['WORDS_FILE'], as_attachment=True)

    def _save_words(self, words):
        with open(current_app.config['WORDS_FILE'], 'w') as f:
            json.dump(words, f)
'''.strip())

    # Create template files
    create_file('app/templates/base.html', '''
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}{% endblock %} - Vocabulary App</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
    <div class="content">
        {% block content %}{% endblock %}
    </div>
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
</body>
</html>
'''.strip())

    create_file('app/templates/index.html', '''
{% extends "base.html" %}

{% block title %}Home{% endblock %}

{% block content %}
<div id="wordContainer">
    <select id="languageSelector">
        <option value="en-US">English</option>
        <option value="fr-FR">French</option>
        <option value="es-ES">Spanish</option>
        <option value="de-DE">German</option>
    </select>
    
    <h2 id="word" contenteditable="false">Word</h2>
    <i id="pronounce-icon" class="fas fa-volume-up"></i>
    <p id="sentence" contenteditable="false">Sentence</p>
    
    <div class="stats-container">
        <div class="stat-item">
            <i class="fas fa-fire"></i>
            <span id="streak">Streak: 0</span>
        </div>
        <div class="stat-item">
            <i class="fas fa-check"></i>
            <span id="accuracy">Accuracy: 0%</span>
        </div>
    </div>

    <div id="typingContainer" class="typing-container hidden">
        <input type="text" id="typingInput" placeholder="Type the word here..." autocomplete="off">
        <div id="feedback"></div>
    </div>
    
    <div id="navigation">
        <button id="previous" title="Previous"><i class="fas fa-chevron-left"></i></button>
        <button id="next" title="Next"><i class="fas fa-chevron-right"></i></button>
        <button id="toggleTyping" title="Toggle Typing Practice"><i class="fas fa-keyboard"></i></button>
        <button id="remove" title="Remove"><i class="fas fa-trash-alt"></i></button>
        <button id="download" title="Download"><i class="fas fa-download"></i></button>
    </div>
    
    <p id="message"></p>
</div>
{% endblock %}
'''.strip())

    # Create static files
    create_file('app/static/css/style.css', '''
body {
    font-family: Arial, sans-serif;
    margin: 20px;
    background-color: #f5f5f5;
}

#wordContainer {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

#word {
    font-size: 2em;
    margin: 10px 0;
    display: inline-block;
}

#pronounce-icon {
    cursor: pointer;
    margin-left: 10px;
    color: #666;
}

#sentence {
    font-size: 1.2em;
    color: #666;
    margin: 10px 0;
}

#navigation {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin: 20px 0;
}

button {
    padding: 8px 16px;
    border: none;
    background-color: #f0f0f0;
    border-radius: 4px;
    cursor: pointer;
}

button:hover {
    background-color: #e0e0e0;
}

.stats-container {
    display: flex;
    justify-content: space-around;
    margin: 20px 0;
}

.typing-container {
    margin: 20px 0;
}

.typing-container.hidden {
    display: none;
}

#typingInput {
    width: 100%;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
}
'''.strip())

    create_file('app/static/js/app.js', '''
let currentIndex = 0;
let words = [];
let typingMode = false;
let streakCount = 0;

document.addEventListener('DOMContentLoaded', () => {
    loadWords();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('previous').addEventListener('click', previousWord);
    document.getElementById('next').addEventListener('click', nextWord);
    document.getElementById('remove').addEventListener('click', removeWord);
    document.getElementById('download').addEventListener('click', downloadWords);
    document.getElementById('toggleTyping').addEventListener('click', toggleTypingMode);
    document.getElementById('pronounce-icon').addEventListener('click', pronounceWord);
    document.getElementById('typingInput').addEventListener('input', checkTyping);
}

async function loadWords() {
    try {
        const response = await fetch('/api/words');
        words = await response.json();
        updateWordDisplay();
    } catch (error) {
        console.error('Failed to load words:', error);
    }
}

function updateWordDisplay() {
    if (words.length === 0) {
        document.getElementById('word').textContent = 'No words available';
        document.getElementById('sentence').textContent = '';
        return;
    }

    const currentWord = words[currentIndex];
    document.getElementById('word').textContent = currentWord.word;
    document.getElementById('sentence').textContent = currentWord.sentence;
}

// Add the rest of your JavaScript functions here
'''.strip())

    print("Flask application structure generated successfully!")

if __name__ == "__main__":
    generate_app_structure()