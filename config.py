import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change'
    DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
    WORDS_FILE = os.path.join(DATA_DIR, 'words.json')