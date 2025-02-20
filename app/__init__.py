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