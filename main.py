"""
PJECZ Delphinus Flask
"""

import os

import uvicorn
from dotenv import load_dotenv

load_dotenv()
FLASK_APP = os.getenv("FLASK_APP", "pjecz_delphinus_flask.app") + ":app"
FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))


def main():
    uvicorn.run(FLASK_APP, host=FLASK_HOST, port=FLASK_PORT, reload=True)


if __name__ == "__main__":
    main()
