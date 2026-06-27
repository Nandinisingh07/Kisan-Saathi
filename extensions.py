from data_fetcher import mandi_bp
from weather_service import weather_bp
from firebase_service import firebase_bp
from model_service import model_bp
from chatbot_service import chat_bp
from ivr_service import ivr_bp

def register_blueprints(app):
    app.register_blueprint(mandi_bp)
    app.register_blueprint(weather_bp)
    app.register_blueprint(firebase_bp)
    app.register_blueprint(model_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(ivr_bp)
