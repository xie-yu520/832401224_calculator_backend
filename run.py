"""后端启动入口：python run.py"""

from src.app import create_app
from src.config import Config

app = create_app()

if __name__ == "__main__":
    print(f"Calculator backend is running at http://{Config.HOST}:{Config.PORT}")
    print(f"SQLite database: {Config.DB_PATH}")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
