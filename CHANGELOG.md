# Changelog

All notable changes to the D&D Character Sheet Application will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-12-19

### ✨ Added
- **Advanced Inventory Management System**
  - Unit management with + and - buttons for every item
  - Automatic stacking of identical items when picked up
  - Support for containers with weight reduction
  - Ground storage system for dropped items
  - Home storage system for permanent item storage
  - Item categories: weapons, armor, containers, general items

- **Dynamic Encumbrance System**
  - Size-based threshold calculations (Tiny, Small, Medium, Large, Huge, Gargantuan)
  - Automatic encumbrance level determination based on character height
  - Strength-based weight thresholds for all size categories
  - Powerful Build trait support (uses next larger size thresholds)
  - Real-time encumbrance updates with inventory changes
  - Movement speed penalties based on encumbrance level

- **Mobile-Responsive Interface**
  - Mobile-first design with collapsible sections
  - Touch-friendly controls and navigation
  - Overview section with encumbrance display
  - Rules reference tables for injury fatigue and encumbrance
  - View mode toggle between mobile and desktop layouts

- **Enhanced Character Management**
  - Injury fatigue system with automatic debuffs
  - Exhaustion tracking with cumulative effects
  - Debuff management with reasons and IDs
  - Weapon proficiency system
  - Enhanced skill management with stat-based bonuses

### 🔧 Changed
- **Inventory System Overhaul**
  - Replaced simple item list with advanced management system
  - Added unit tracking for all stackable items
  - Implemented weight-based encumbrance calculations
  - Enhanced item properties and metadata

- **User Interface Improvements**
  - Redesigned character sheet layout for better usability
  - Added color-coded encumbrance indicators
  - Improved button styling and placement
  - Enhanced mobile responsiveness

- **Data Structure Updates**
  - Enhanced character data model for new features
  - Added inventory item properties (is_container, weight_reduction, etc.)
  - Improved debuff and effect tracking

### 🐛 Fixed
- **Python 3.13 Compatibility**
  - Removed SQLAlchemy dependencies (not used in application)
  - Updated Flask to version 3.0.2
  - Fixed import compatibility issues

- **Inventory Management Issues**
  - Fixed item stacking logic
  - Corrected weight calculations for containers
  - Resolved unit management button functionality

### 🗑️ Removed
- **Unused Dependencies**
  - Removed Flask-SQLAlchemy (not used)
  - Removed SQLAlchemy (not used)
  - Cleaned up requirements.txt

## [1.5.0] - 2024-12-18

### ✨ Added
- **Basic Character Management**
  - Character creation and editing
  - Basic inventory system
  - Skill and ability tracking
  - Character traits and notes

- **Core Game Mechanics**
  - Vitality Points (VP) and Wound Points (WP) tracking
  - Rest and recovery system
  - Basic debuff management
  - Currency tracking (gold, silver, copper)

### 🔧 Changed
- **Initial Application Structure**
  - Flask-based web application
  - JSON-based data storage
  - Basic HTML templates
  - Simple CSS styling

## [1.0.0] - 2024-12-17

### ✨ Added
- **Project Foundation**
  - Basic Flask application structure
  - Character data model
  - Simple web interface
  - Basic routing system

---

## Version History Summary

- **v2.0.0**: Major feature release with inventory management, encumbrance system, and mobile interface
- **v1.5.0**: Core character management and game mechanics
- **v1.0.0**: Initial project foundation

## Migration Notes

### From v1.5.0 to v2.0.0
- Character data structure has been enhanced with new inventory properties
- Existing characters will automatically gain new inventory management features
- Encumbrance calculations will be applied to all characters
- Mobile interface is now the default view mode

### From v1.0.0 to v2.0.0
- Complete overhaul of the application architecture
- New inventory and encumbrance systems
- Mobile-responsive design implementation
- Enhanced character data model

---

## Future Roadmap

### Planned Features (v2.1.0)
- [ ] Spell management system
- [ ] Equipment sets and quick-swapping
- [ ] Character import/export functionality
- [ ] Multiplayer support for shared campaigns
- [ ] Advanced combat tracking

### Long-term Goals (v3.0.0)
- [ ] Campaign management
- [ ] NPC and monster tracking
- [ ] Advanced rule systems
- [ ] API for third-party integrations
- [ ] Mobile app development

---

**Note**: This changelog tracks all significant changes to the application. For detailed technical changes, please refer to the git commit history. 