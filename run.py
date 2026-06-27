from app_factory import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", True), host="127.0.0.1", port=5000)
