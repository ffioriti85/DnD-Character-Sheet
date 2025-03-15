import os
import sys
import webbrowser
from threading import Timer
from app import app

def open_browser():
    webbrowser.open('http://127.0.0.1:5000/')

if __name__ == '__main__':
    if getattr(sys, 'frozen', False):
        # If we're running as a PyInstaller bundle
        application_path = sys._MEIPASS
    else:
        # If we're running as a normal Python script
        application_path = os.path.dirname(os.path.abspath(__file__))
    
    # Set the working directory
    os.chdir(application_path)
    
    # Open browser after a short delay
    Timer(1.5, open_browser).start()
    
    # Run the Flask application
    app.run(host='0.0.0.0', port=5000, debug=False) 