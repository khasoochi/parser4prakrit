"""
Flask application entry point for Vercel deployment.

This module imports the Flask app from verb_analyzer and exposes it
as the WSGI application for Vercel.
"""

from verb_analyzer import app

# Vercel looks for an 'app' variable
# The app is already created in verb_analyzer.py

if __name__ == "__main__":
    # This won't run on Vercel, but useful for local testing
    import os
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
