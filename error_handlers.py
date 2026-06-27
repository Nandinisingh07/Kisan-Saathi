import os
import logging
from logging.handlers import RotatingFileHandler
from flask import jsonify

def setup_logger():
    # Create logs directory if it does not exist
    os.makedirs("logs", exist_ok=True)
    
    # Configure rotating file handler: max 5MB, 3 backups
    log_file = os.path.join("logs", "kisan_saathi.log")
    handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
    
    # Custom log format
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s [%(pathname)s:%(lineno)d]: %(message)s"
    )
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    
    # Configure logger "kisan_saathi"
    logger = logging.getLogger("kisan_saathi")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    
    # Also add standard output stream to logger for CLI visibility
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    
    logger.info("Structured logger registered successfully.")

def register_error_handlers(app):
    
    @app.errorhandler(400)
    def bad_request(e):
        logger = logging.getLogger("kisan_saathi")
        logger.error(f"400 Bad Request error handler triggered: {e}")
        return jsonify({
            "success": False,
            "error_code": "BAD_REQUEST",
            "error": "The server could not understand the request due to invalid syntax."
        }), 400
        
    @app.errorhandler(404)
    def page_not_found(e):
        logger = logging.getLogger("kisan_saathi")
        logger.error(f"404 Not Found error handler triggered: {e}")
        return jsonify({
            "success": False,
            "error_code": "NOT_FOUND",
            "error": "The requested resource could not be found on the server."
        }), 404
        
    @app.errorhandler(500)
    def internal_server_error(e):
        logger = logging.getLogger("kisan_saathi")
        logger.error(f"500 Internal Server error handler triggered: {e}")
        return jsonify({
            "success": False,
            "error_code": "INTERNAL_SERVER_ERROR",
            "error": "An unexpected error occurred on the server. Please try again later."
        }), 500
