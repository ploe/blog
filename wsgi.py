"""gunicorn entrypoint"""
from entrypoint import APP

if __name__ == "__main__":
    APP.run()
