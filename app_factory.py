from app import app
from extensions import register_blueprints
from error_handlers import register_error_handlers

def create_app():
    register_blueprints(app)
    register_error_handlers(app)
    return app
