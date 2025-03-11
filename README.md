# D&D Character Sheet Application

A Flask-based web application for managing D&D character sheets.

## Features

- Create and manage multiple characters
- Track vital statistics (HP, VP, etc.)
- Manage inventory with weight calculations
- Handle skills and proficiencies
- Track active abilities and their uses
- Manage character traits
- Take and manage character notes
- Handle short and long rests
- Track currency (gold, silver, copper)

## Technical Stack

- Python 3.x
- Flask web framework
- Flask-Bootstrap5 for styling
- SQLAlchemy for database management
- JSON for character data storage

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Unix/MacOS: `source .venv/bin/activate`
4. Install dependencies:
   ```bash
   pip install flask flask-bootstrap flask-sqlalchemy
   ```
5. Run the application:
   ```bash
   python app.py
   ```

## Development

The project maintains two main branches:
- `master`: Stable release version
- `unstable`: Development branch with latest features

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Deployment on Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Use the following settings:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Port**: 10000

## Environment Variables

Set the following environment variables in Render:
- `SECRET_KEY`: A secure secret key for Flask sessions
- `ADMIN_PASSWORD`: The password for accessing the application 