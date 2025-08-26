# D&D Character Sheet Application

A comprehensive Flask-based web application for managing D&D character sheets with advanced inventory management, encumbrance calculations, and mobile-responsive design.

## ✨ Features

### 🎭 Character Management
- Create and manage multiple characters with detailed profiles
- Track vital statistics (HP, VP, WP, movement speed, etc.)
- Manage character traits and active abilities
- Handle skills and proficiencies with customizable bonuses
- Take and manage character notes with timestamps
- Track currency (gold, silver, copper) with automatic conversion

### 🎒 Advanced Inventory System
- **Unit Management**: Add/remove units for stackable items with + and - buttons
- **Automatic Stacking**: Identical items automatically stack when picked up
- **Container Support**: Items can be stored in containers with weight reduction
- **Weight Tracking**: Real-time weight calculations for encumbrance
- **Item Categories**: Support for weapons, armor, containers, and general items
- **Storage Options**: Drop items to ground, store at home, or carry in inventory

### ⚖️ Dynamic Encumbrance System
- **Size-Based Calculations**: Automatic threshold determination based on character height
- **Strength Integration**: All thresholds calculated using character's Strength stat
- **Powerful Build Support**: Characters with Powerful Build use next larger size thresholds
- **Real-Time Updates**: Encumbrance level updates automatically with inventory changes
- **Movement Penalties**: Automatic movement speed adjustments based on encumbrance level

### 📱 Responsive Design
- **Mobile-First Interface**: Optimized for mobile devices with collapsible sections
- **Desktop Version**: Full-featured interface for larger screens
- **View Mode Toggle**: Switch between mobile and desktop layouts
- **Touch-Friendly Controls**: Large buttons and intuitive navigation

### 🎯 Combat & Abilities
- **Weapon Management**: Equip weapons with damage dice and modifiers
- **Armor System**: Equip armor with AC bonuses and DX modifiers
- **Active Abilities**: Track ability uses with recharge mechanics
- **Rest System**: Short and long rest functionality for healing and ability recovery

### 🔄 Game Mechanics
- **Injury Fatigue System**: Automatic debuffs based on wound points
- **Exhaustion Tracking**: Multiple levels of exhaustion with cumulative effects
- **Debuff Management**: Add/remove temporary modifiers with reasons and IDs
- **Proficiency System**: Customizable skill proficiencies with stat-based bonuses

## 🛠️ Technical Stack

- **Backend**: Python 3.x, Flask web framework
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Data Storage**: JSON-based file system (no database required)
- **Styling**: Custom CSS with responsive design principles
- **Dependencies**: Flask, Flask-Bootstrap, Flask-CKEditor

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DnD-Character-Sheet
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**
   - **Windows**: `.venv\Scripts\activate`
   - **Unix/MacOS**: `source .venv/bin/activate`

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`
   - Create a new character or load an existing one

## 📁 Project Structure

```
DnD-Character-Sheet/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This documentation
├── LICENSE               # MIT License
├── characters/           # Character data storage
├── storage/              # Ground and home storage
├── templates/            # HTML templates
│   ├── view_character.html      # Desktop character sheet
│   ├── mobile_character.html    # Mobile character sheet
│   └── index.html               # Character selection
├── static/               # CSS, JavaScript, and assets
│   └── style.css         # Custom styling
└── venv/                 # Virtual environment
```

## 🎮 Usage Guide

### Creating a Character
1. Enter character name on the main page
2. Fill in basic stats (race, height, weight, ability scores)
3. Add traits, skills, and abilities as needed
4. Complete character creation

### Managing Inventory
- **Add Items**: Use the "Add Item" form with detailed item properties
- **Unit Management**: Use + and - buttons to adjust item quantities
- **Storage**: Drop items to ground, store at home, or use containers
- **Weight Tracking**: Monitor total inventory weight for encumbrance

### Understanding Encumbrance
- **Size Categories**: Tiny, Small, Medium, Large, Huge, Gargantuan
- **Thresholds**: Based on character height and Strength stat
- **Powerful Build**: Characters with this trait use next larger size thresholds
- **Movement Effects**: Encumbrance level affects movement speed

### Mobile Interface
- **Overview Section**: Quick access to vital stats and encumbrance
- **Collapsible Sections**: Tap to expand/collapse different character aspects
- **Rules Reference**: Built-in tables for injury fatigue and encumbrance rules
- **Touch Controls**: Optimized for mobile interaction

## 🔧 Configuration

### Environment Variables
- `SECRET_KEY`: Flask session secret key
- `DEBUG`: Set to `True` for development mode

### Character Data
- All character data is stored in JSON format
- No database setup required
- Data persists between application restarts

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
```bash
gunicorn app:app --bind 0.0.0.0:5000
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
```

## 🧪 Testing

Run the test suite:
```bash
python test_ground_system.py
```

## 📝 Recent Updates

### Version 2.0 - Major Feature Release
- **Inventory Management**: Complete overhaul with unit management and stacking
- **Encumbrance System**: Dynamic size-based calculations with Powerful Build support
- **Mobile Interface**: Responsive design with mobile-optimized character sheet
- **Container System**: Support for storing items in containers with weight reduction
- **Ground Storage**: Global item storage system for dropped items
- **Home Storage**: Permanent storage location for character items

### Version 1.5 - Core Features
- Character creation and management
- Basic inventory system
- Skill and ability tracking
- Rest and recovery mechanics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Flask web framework
- Styled with Bootstrap 5
- Designed for D&D 5e compatibility
- Inspired by tabletop RPG enthusiasts

## 📞 Support

For issues, questions, or feature requests:
1. Check existing issues in the repository
2. Create a new issue with detailed description
3. Include character data and steps to reproduce if applicable

---

**Happy adventuring!** 🎲⚔️🏰 