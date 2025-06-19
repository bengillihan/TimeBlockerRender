from app_factory import create_app
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = create_app()

if __name__ == "__main__":
    # ALWAYS serve the app on port 5000
    app.run(host="0.0.0.0", port=5000, debug=True)