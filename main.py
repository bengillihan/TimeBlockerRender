import os
from app import app

if __name__ == "__main__":
    # Railway assigns port 5000 in networking configuration
    port = 5000
    app.run(host="0.0.0.0", port=port, debug=True)