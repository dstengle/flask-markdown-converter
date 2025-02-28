#!/usr/bin/env python
"""
Run script for the Flask application.
"""
from app import create_app

app = create_app()

def main():
    """
    Main entry point for the application when run through Poetry.
    """
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()