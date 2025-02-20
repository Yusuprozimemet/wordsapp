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