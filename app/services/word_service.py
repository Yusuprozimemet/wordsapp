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