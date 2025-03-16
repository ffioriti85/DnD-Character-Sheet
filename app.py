from flask import Flask, request, render_template, redirect, url_for, jsonify, session, flash
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Float
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import uuid
import math
from datetime import datetime

app = Flask(__name__)
Bootstrap(app)
DATA_FOLDER = 'characters'
characters = {}
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Add secret key for sessions
app.secret_key = 'your-secret-key-here'  # Replace with a secure secret key in production

# TODO:
#   Add the items on the ground to be "global"?
#

#
def save_character(character):
    filename = os.path.join(DATA_FOLDER, f"{character['name']}.json")
    with open(filename, 'w') as file:
        json.dump(character, file)


def initialize_character(character):
    """Ensure all expected keys exist in the character dictionary, adding defaults if missing."""

    default_character = {
        'name': "",
        'level': 1,
        'race': "",
        'height': "",
        'debuff_height': 0,
        'weight': "",
        'movement_speed': 0,
        "active_movement_debuffs": "None",
        'debuff_movement': 0,
        'active_movement_speed': 0,
        'ST': 0,
        'active_ST': 0,
        'ST_modifier': 0,
        'debuff_ST': 0,
        'DX': 0,
        'active_DX': 0,
        'debuff_DX': 0,
        'DX_modifier': 0,
        'CN': 0,
        'active_CN': 0,
        'debuff_CN': 0,
        'CN_modifier': 0,
        'CH': 0,
        'active_CH': 0,
        'debuff_CH': 0,
        'CH_modifier': 0,
        'IN': 0,
        'active_IN': 0,
        'debuff_IN': 0,
        'IN_modifier': 0,
        'WP': 0,
        'active_WP': 0,
        'debuff_WP': 0,
        'WP_modifier': 0,
        'gold': 0,
        'silver': 0,
        'copper': 0,
        'vitality_points_dice_rolls': [],
        'vitality_points': 0,
        'active_vitality_points': 0,
        'max_vitality_points': 0,
        'debuff_max_vp': 0,
        'wound_points': 0,
        'active_wound_points': 0,
        'max_wound_points': 0,
        'debuff_max_wp': 0,
        'passive_perception': 10,
        'traits': [],
        'proficiencies': [],
        'inventory': [],
        'injury_fatigue': 0,
        'exhaustion': 0,
        'extra_injury_fatigue': 0,
        'encumbrance': 0,
        'active_abilities': [],
        'injury_fatigue_debuffs': "None",
        'armor': {
            'name': None,
            'ac_value': 10,
            'modifier': 0,
            'dx_modifier': True,
            'conditions': None
        },
        'shield_equipped': False,
        'temp_armor_modifier': 0,
        'debuffs': [],
        'weapon': {
            'name': None,
            'damage_dice': None,
            'weapon_stat_modifier': None,
            'weapon_modifiers': None,
            'weapon_conditions': None,
            'weapon_normal_range': None,
            'weapon_long_range': None
        },
        'skills': {},
        'total_ac': 10,
        'encumbrance_penalty_explained': "",
        'total_inventory_weight': 0,
        'weapon_hit_chances': 0,
        'weapon_total_damage_modifier': 0
    }

    # Ensure all default keys exist in character
    for key, value in default_character.items():
        if key not in character:
            character[key] = value

    # Ensure inventory items have container-related fields
    for item in character.get('inventory', []):
        if 'is_container' not in item:
            item['is_container'] = False
        if 'container_capacity' not in item:
            item['container_capacity'] = None
        if 'weight_reduction' not in item:
            item['weight_reduction'] = None
        if 'contents' not in item:
            item['contents'] = [] if item.get('is_container', False) else None

    return character


def save_character_active(character):
    filename = os.path.join(DATA_FOLDER, f"{character['name']}.json")
    with open(filename, 'w') as file:
        json.dump(character, file)


def load_character(name):
    """Load character data from file, ensuring we always get the latest version."""
    filename = os.path.join(DATA_FOLDER, f"{name}.json")
    if os.path.exists(filename):
        # Always read fresh from file
        with open(filename, 'r') as file:
            character_data = json.load(file)
            
        # Ensure inventory is a list of dictionaries
        if 'inventory' not in character_data:
            character_data['inventory'] = []
        elif isinstance(character_data['inventory'], list):
            character_data['inventory'] = [
                item if isinstance(item, dict) else {} for item in character_data['inventory']
            ]

        # Ensure vitality_points_dice_rolls is a list of strings
        if 'vitality_points_dice_rolls' in character_data:
            character_data['vitality_points_dice_rolls'] = [
                str(roll) for roll in character_data['vitality_points_dice_rolls']
            ]

        # Calculate vitality points using the latest data
        if 'level' in character_data and 'CN' in character_data:
            total_debuff = (int(character_data.get('injury_fatigue', 0)) + 
                          int(character_data.get('exhaustion', 0)) + 
                          int(character_data.get('extra_injury_fatigue', 0)))
            
            # Use wound points for VP calculation if character has injury fatigue
            vp_modifier = character_data['active_wound_points'] if total_debuff > 0 else character_data['CN']
            
            character_data['max_vitality_points'] = calculate_vitality_points(
                character_data['vitality_points_dice_rolls'],
                character_data['level'],
                vp_modifier
            ) + character_data.get('debuff_max_vp', 0)

        return character_data
    return None

@app.route('/delete_character/<name>', methods=['GET', 'POST'])
def delete_character(name):
    filename = os.path.join(DATA_FOLDER, f"{name}.json")
    if os.path.exists(filename):
        os.remove(filename)

    return redirect(url_for('index'))  # Calls the `index` function
def get_character_list():
    """Retrieve a list of character names from the JSON files in DATA_FOLDER."""
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)  # Ensure the folder exists

    # List only .json files and remove the extension
    return [f[:-5] for f in os.listdir(DATA_FOLDER) if f.endswith('.json')]
@app.route('/', methods=['GET', 'POST'])
def index():
    characters = get_character_list()

    if request.method == 'POST':
        name = request.form['name']

        # Check for GM secret word
        if name == "AndyGM":
            return redirect(url_for('gm_cheatsheet'))

        # Try to load the character, including the inventory
        character = load_character(name)

        if character:
            return redirect(url_for('view_character', name=name))
        else:
            return redirect(url_for('create_character', name=name))

    return render_template('index.html', characters=characters)

@app.route('/gm_cheatsheet')
def gm_cheatsheet():
    characters = get_character_list()
    return render_template('gm_cheatsheet.html', characters=characters)

@app.route('/api/character/<name>/stats')
def character_stats(name):
    character = load_character(name)
    if not character:
        return jsonify({"error": "Character not found"}), 404

    return jsonify({
        "active_vitality_points": character["active_vitality_points"],
        "max_vitality_points": character["max_vitality_points"],
        "active_wound_points": character["active_wound_points"],
        "max_wound_points": character["max_wound_points"],
        "injury_fatigue": character["injury_fatigue"],
        "armor_class": character["total_ac"],
        "movement_speed": character["active_movement_speed"]
    })

# Function to Calculate Modifiers
def get_modifier(stat_value):
    return (stat_value - 10) // 2


def calculate_vitality_points(rolls, level, CN):
    total_vitality_points = 0
    
    # print(f"Original rolls: {rolls}")
    # Convert rolls to integers and calculate half rounded up
    for roll in rolls:
        try:
            # Convert string to int if it's a string
            roll_value = int(str(roll).strip())  # Ensure we're working with a clean string
            # Calculate half of the roll rounded up
            half_roll = math.ceil(roll_value / 2)
            total_vitality_points += half_roll
            
        except (ValueError, TypeError) as e:
            # print(f"Error processing roll: {roll}, error: {e}")
            continue

    # Calculate and add the level modifier
    cn_modifier = get_modifier(CN)
    level_bonus = level * cn_modifier
    
    # Add the level bonus to the total
    total_vitality_points += level_bonus
    
    # print(f"Half rolls sum: {total_vitality_points - level_bonus}")
    # print(f"Level: {level}, CN: {CN}, CN Modifier: {cn_modifier}")
    # print(f"Level bonus: {level_bonus}")
    # print(f"Total VP: {total_vitality_points}")
    
    return total_vitality_points


@app.route('/create/<name>', methods=['GET', 'POST'])
def create_character(name):
    if request.method == 'POST':
        try:
            character_data = {
                'name': name,
                'level': 0,
                'race': request.form['race'],
                'height': request.form['height'],
                'debuff_height': 0,
                'powerful_build':False,
                'weight': request.form['weight'],
                'is_inspired': False,
                'movement_speed': request.form['movement_speed'],
                "active_movement_debuffs": "None",
                'debuff_movement': 0,
                'active_movement_speed': request.form['movement_speed'],
                'ST': int(request.form['ST']),
                'active_ST': int(request.form['ST']),
                'ST_modifier': get_modifier(int(request.form['ST'])),
                'debuff_ST': 0,
                'DX': int(request.form['DX']),
                'active_DX': int(request.form['DX']),
                'debuff_DX': 0,
                'DX_modifier': get_modifier(int(request.form['DX'])),
                'CN': int(request.form['CN']),
                'active_CN': int(request.form['CN']),
                'debuff_CN': 0,
                'CN_modifier': get_modifier(int(request.form['CN'])),
                'CH': int(request.form['CH']),
                'active_CH': int(request.form['CH']),
                'debuff_CH': 0,
                'CH_modifier': get_modifier(int(request.form['CH'])),
                'IN': int(request.form['IN']),
                'active_IN': int(request.form['IN']),
                'debuff_IN': 0,
                'IN_modifier': get_modifier(int(request.form['IN'])),
                'WP': int(request.form['WP']),
                'active_WP': int(request.form['WP']),
                'debuff_WP': 0,
                'WP_modifier': get_modifier(int(request.form['WP'])),
                'gold': 0,
                'silver': 0,
                'copper':0,
                'vitality_points_dice_rolls': (request.form['vitality_points'].split(',')),
                'vitality_points': 0,
                'active_vitality_points': 0,
                'max_vitality_points': 0,
                'debuff_max_vp': 0,
                'ac_buff':0,
                'wound_points': int(request.form['wound_points']),
                'active_wound_points': int(request.form['wound_points']),
                'max_wound_points': int(request.form['wound_points']),
                'hit_dice':request.form['hit_dice'],
                'debuff_max_wp': 0,
                'passive_perception': 10,
                'traits': [],
                'proficiencies': [],
                'inventory': [],
                'injury_fatigue': 0,
                'exhaustion': 0,
                'extra_injury_fatigue': 0,
                'encumbrance': 0,
                'active_abilities': [],
                'injury_fatigue_debuffs': "None",
                'armor': {
                    'name': None,
                    'ac_value': 10,
                    'modifier': 0,
                    'dx_modifier': True,
                    'conditions': None
                },
                'shield_equipped': False,
                'temp_armor_modifier': 0,
                'debuffs': [],
                'weapon' : {
                'name': 'Unarmed',
                'damage_dice': 'd4',
                'weapon_stat_modifier': 'Strength',
                'weapon_modifiers': 0,
                'weapon_proficiency':None
                    },
                'skills': {
                    # "Athletics": {"stat": "ST", "proficiency_bonus": 0},
                    # "Acrobatics": {"stat": "DX", "proficiency_bonus": 0},
                    # "Sleight of Hand": {"stat": "DX", "proficiency_bonus": 0},
                    # "Stealth": {"stat": "DX", "proficiency_bonus": 0},
                    # "Arcana": {"stat": "IN", "proficiency_bonus": 0},
                    # "History": {"stat": "IN", "proficiency_bonus": 0},
                    # "Investigation": {"stat": "IN", "proficiency_bonus": 0},
                    # "Nature": {"stat": "IN", "proficiency_bonus": 0},
                    # "Religion": {"stat": "IN", "proficiency_bonus": 0},
                    # "Animal Handling": {"stat": "WP", "proficiency_bonus": 0},
                    # "Insight": {"stat": "WP", "proficiency_bonus": 0},
                    # "Medicine": {"stat": "WP", "proficiency_bonus": 0},
                    # "Perception": {"stat": "WP", "proficiency_bonus": 0},
                    # "Survival": {"stat": "WP", "proficiency_bonus": 0},
                    # "Deception": {"stat": "CH", "proficiency_bonus": 0},
                    # "Intimidation": {"stat": "CH", "proficiency_bonus": 0},
                    # "Performance": {"stat": "CH", "proficiency_bonus": 0},
                    # "Persuasion": {"stat": "CH", "proficiency_bonus": 0}
                }
            }

        except ValueError:
            # Handle the error if any value cannot be converted to int
            return "Invalid input: all stats must be integers.", 400
        total_vitality_points = calculate_vitality_points(character_data['vitality_points_dice_rolls'],
                                                          character_data['level'], character_data['CN'])
     
        character_data['vitality_points'] = total_vitality_points
        character_data['active_vitality_points'] = total_vitality_points
        character_data['max_vitality_points'] = total_vitality_points
        save_character(character_data)
        update_armor_values(character_data)
        update_character(name)
        save_character(character_data)  # Save the character data to file

        return render_template("create_character_part2.html", character=character_data)

    return render_template('create_character.html', name=name)

@app.route('/finish_creation/<name>', methods=['GET', 'POST'])
def finish_creation(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404


    save_character(character)
    update_character(name)
    return redirect(url_for("view_character", name=name))
def update_stats_modifiers(character):
    # Calculate modifiers
    character['ST_modifier'] = get_modifier(int(character.get('active_ST', 10)))
    character['DX_modifier'] = get_modifier(int(character.get('active_DX', 10)))
    character['CN_modifier'] = get_modifier(int(character.get('active_CN', 10)))
    character['CH_modifier'] = get_modifier(int(character.get('active_CH', 10)))
    character['IN_modifier'] = get_modifier(int(character.get('active_IN', 10)))
    character['WP_modifier'] = get_modifier(int(character.get('active_WP', 10)))
    save_character(character)


def add_new_debuff(character, debuff_name, debuff_value, debuff_reason, debuff_id, removable):
    """Adds a new debuff or updates an existing one based on debuff_id."""
    for debuff in character["debuffs"]:
        if debuff["id"] == debuff_id:
            # Update existing debuff value
            debuff["value"] = debuff_value
            debuff["reason"] = debuff_reason
            debuff['applied'] = False
            # Optionally update the reason
            return  # Exit function after updating

    # If the debuff_id wasn't found, add a new debuff

    character["debuffs"].append({
        "name": debuff_name,
        "value": debuff_value,
        "reason": debuff_reason,
        "removable": removable,
        "applied":False,
        "id": debuff_id

    })


def apply_debuffs(character):
    character["active_ST"] = character["ST"]
    character["active_DX"] = character["DX"]
    character["active_CN"] = character["CN"]
    character["active_CH"] = character["CH"]
    character["active_IN"] = character["IN"]
    character["active_WP"] = character["WP"]
    character["active_movement_speed"] = int(character["movement_speed"])
    # Apply all debuffs
    for debuff in character["debuffs"]:

            debuff_name = debuff["name"]
            debuff_value = int(debuff["value"])
            if debuff_name in ["debuff_ST", "debuff_st"]:
                character["active_ST"] += debuff_value
            elif debuff_name in ["debuff_DX", "debuff_dx"]:
                character["active_DX"] += debuff_value
            elif debuff_name in ["debuff_CN", "debuff_cn"]:
                character["active_CN"] += debuff_value
            elif debuff_name in ["debuff_CH", "debuff_ch"]:
                character["active_CH"] += debuff_value
            elif debuff_name in ["debuff_IN", "debuff_in"]:
                character["active_IN"] += debuff_value
            elif debuff_name in ["debuff_WP", "debuff_wp"]:
                character["active_WP"] += debuff_value
            elif debuff_name == "debuff_movement":
                character["active_movement_speed"] += int(debuff_value)
            elif debuff_name == "debuff_AC":
                character['ac_buff'] += int(debuff_value)
            elif debuff_name =="debuff_carry_capacity":
                character['powerful_build'] = True

            elif debuff_name in character["skills"]:
                if not debuff['applied']:
                        skill = character['skills'][debuff_name]
                        # Use get() to safely add to 'buff', defaulting to 0 if 'buff' doesn't exist
                        skill['buff'] = skill.get('buff', 0) + debuff_value
                        debuff['applied']=True
    save_character(character)

def increase_carry_capacity(size):
    pass


@app.route('/character/<name>')
def view_character(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404
    character = initialize_character(character)
    
    # Get view preference from query parameter, fallback to session, then default to desktop
    view_mode = request.args.get('view')
    if view_mode:
        # If view mode is explicitly set in URL, update session
        session['view_mode'] = view_mode
    elif 'view_mode' not in session:
        # If no view mode in session, default to desktop
        session['view_mode'] = 'desktop'
    
    # Use the view mode from session
    current_view_mode = session['view_mode']
    
    armor_items = [item for item in character['inventory'] if item.get('is_armor')]
    weapon_items = [item for item in character['inventory'] if item.get('is_weapon')]
    update_character(name)
    save_character(character)
    
    # Get error message if exists and remove it from session
    purse_error = session.pop('purse_error', None)
    
    if 'armor' not in character:
        character['armor'] = {
            'name': 'None',
            'ac_value': 10,
            'dx_modifier': True,
            'modifiers': 0,
            'conditions': ''
        }

    if 'weapon' not in character:
        character['weapon'] = {
            'name': 'None',
            'damage_dice': 'd4',
            'stat_modifier': 'Strength',
            'modifier': 0
        }

    # Choose template based on view mode from session
    template = 'mobile_character.html' if current_view_mode == 'mobile' else 'view_character.html'
    return render_template(template, character=character, armor_items=armor_items, weapon_items=weapon_items, purse_error=purse_error, view_mode=current_view_mode)


def calculate_injury_fatigue(active_wound, max_wound):
    if active_wound < max_wound and active_wound > max_wound * 3 / 4:
        return 1
    elif active_wound <= max_wound * 3 / 4 and active_wound > max_wound * 2 / 4:
        return 2
    elif active_wound <= max_wound * 2 / 4 and active_wound > max_wound * 1 / 4:
        return 3
    elif active_wound <= max_wound * 1 / 4 and active_wound > 1:
        return 4
    elif active_wound == 1:
        return 5
    elif active_wound == 0:
        return 6
    else:
        return 0  # Default case if none of the conditions are met


def calculate_encumbrance_level_OLDER(name, character_ST):
    character = load_character(name)
    if character:
        if len(character['inventory']) == 0:
            total_inventory_weight = 0
        else:
            total_inventory_weight = sum(item['total_weight'] for item in character['inventory'])

        height = float(character['height'])
        if 2 <= height < 4:
            # return "Small"
            if total_inventory_weight < character_ST * 2 / 3:
                encumbrance = 0
            elif total_inventory_weight < character_ST * 1.5:
                encumbrance = 1
            elif total_inventory_weight < character_ST * 3:
                encumbrance = 2
            elif total_inventory_weight < character_ST * 5:
                encumbrance = 3
            elif total_inventory_weight < character_ST * 7:
                encumbrance = 4
            else:
                encumbrance = 5
        elif 4 <= height < 8:
            # return "Medium"
            if total_inventory_weight < character_ST:
                encumbrance = 0
            elif total_inventory_weight < character_ST * 2.5:
                encumbrance = 1
            elif total_inventory_weight < character_ST * 5:
                encumbrance = 2
            elif total_inventory_weight < character_ST * 7.5:
                encumbrance = 3
            elif total_inventory_weight < character_ST * 11:
                encumbrance = 4
            else:
                encumbrance = 5
        elif 8 <= height < 16:
            # "Large"
            if total_inventory_weight < character_ST * 1.5:
                encumbrance = 0
            elif total_inventory_weight < character_ST * 3:
                encumbrance = 1
            elif total_inventory_weight < character_ST * 6:
                encumbrance = 2
            elif total_inventory_weight < character_ST * 10:
                encumbrance = 3
            elif total_inventory_weight < character_ST * 14:
                encumbrance = 4
            else:
                encumbrance = 5

        return encumbrance
    return "Character not found", 404

def calculate_encumbrance_level(name, character_ST):
    character = load_character(name)
    if not character:
        return "Character not found", 404

    # Calculate total inventory weight
    total_inventory_weight = sum(item['total_weight'] for item in character['inventory']) if character['inventory'] else 0

    height = float(character['height'])
    powerful_build = character['powerful_build']
    # Define size categories and corresponding encumbrance multipliers
    size_thresholds = {
        (2, 4): [2 / 3, 1.5, 3, 5, 7],  # Small
        (4, 8): [1, 2.5, 5, 7.5, 11],  # Medium
        (8, 16): [1.5, 3, 6, 10, 14]  # Large
    }

    # Find the appropriate size category
    applicable_size = None
    for (min_height, max_height), thresholds in size_thresholds.items():
        if min_height <= height < max_height:
            applicable_size = (min_height, max_height)
            break

    if applicable_size is None:
        return "Invalid height", 400  # Return error if height is out of range

    # If Powerful Build is active, shift to the next larger size if possible
    if powerful_build:
        size_keys = list(size_thresholds.keys())
        current_index = size_keys.index(applicable_size)
        if current_index + 1 < len(size_keys):  # Ensure it's not already at the max size
            applicable_size = size_keys[current_index + 1]

    # Get the thresholds for the final applicable size
    thresholds = size_thresholds[applicable_size]

    # Determine encumbrance level based on weight thresholds
    for level, multiplier in enumerate(thresholds):
        if total_inventory_weight < character_ST * multiplier:
            return level

    return 5  # Max encumbrance if all thresholds are exceeded

def calculate_encumbrance_penalty(encumbrance):
    encumbrance_penalties = {
        "0": 5,
        "1": 0,
        "2": -10,
        "3": -15,
        "4": -20,
        "5": -100,
    }
    encumbrance = str(encumbrance)
    return encumbrance_penalties[encumbrance]


def explain_encumbrance_penalty(encumbrance):
    encumbrance_penalty_explanation = {
        "0": "+5 Movement Speed from being Unencumbered",
        "1": "Normal Movement Speed by being Lightly Encumbered",
        "2": "-10 Movement Speed from being Moderately Encumbered",
        "3": "-15 Movement Speed from being Heavily Encumbered",
        "4": "-20 Movement Speed from being Extremely Encumbered",
        "5": "Can't move because of how much you are carrying",
    }
    encumbrance = str(encumbrance)
    return encumbrance_penalty_explanation[encumbrance]


def update_movement_speed(base_movement_speed, modifier_from_debuff, modifier_from_emcumbrance):
    new_movement_speed = int(base_movement_speed + modifier_from_debuff + modifier_from_emcumbrance)
    if new_movement_speed > 0:
        return new_movement_speed
    else:
        return 0


def update_armor_values(character):

    if character['armor']['dx_modifier']:

        dx_modifier = int(character['DX_modifier'])

    else:
        dx_modifier = 0
    if character['shield_equipped']:
        shield_modifier = 2
    else:
        shield_modifier = 0
    temporary_modifier = character['temp_armor_modifier']
    total_ac = character['armor']['ac_value'] + dx_modifier + character['armor']['modifier'] + shield_modifier + \
               character['temp_armor_modifier'] +character['ac_buff']
    character['total_ac'] = total_ac

    save_character(character)



@app.route('/character/<name>/update', methods=['POST'])
def update_character(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404

    # Get the current view mode from the request
    view_mode = request.args.get('view', 'desktop')

    try:
        # Convert current values to integers
        active_vitality = int(character['active_vitality_points'])
        max_vitality = int(character['max_vitality_points'])
        active_wound = int(character['active_wound_points'])
        max_wound = int(character['max_wound_points'])
        extra_injury_fatigue = int(character['extra_injury_fatigue'])
        exhaustion = int(character['exhaustion'])
    except ValueError:
        return "Invalid data in character file.", 500

    # Update vitality points
    if 'increase_vitality' in request.form:
        if active_vitality < max_vitality:
            active_vitality += 1
    if 'decrease_vitality' in request.form:
        if active_vitality > 0:
            active_vitality -= 1
    if 'heal_vitality' in request.form:
        active_vitality = max_vitality

    # Update wound points
    if 'increase_wound' in request.form:
        if active_wound < max_wound:
            active_wound += 1
    if 'decrease_wound' in request.form:
        if active_wound > 0:
            active_wound -= 1
    if 'heal_wound' in request.form:
        active_wound = max_wound

    if 'increase_exhaustion' in request.form:
        exhaustion += 1
    if 'decrease_exhaustion' in request.form:
        if exhaustion > 0:
            exhaustion -= 1
    if 'heal_exhaustion' in request.form:
        exhaustion = 0

    if 'increase_extra_injury_fatigue' in request.form:
        extra_injury_fatigue += 1

    if 'decrease_extra_injury_fatigue' in request.form:
        if extra_injury_fatigue > 0:
            extra_injury_fatigue -= 1

    if 'heal_extra_injury_fatigue' in request.form:
        extra_injury_fatigue = 0

    character['active_wound_points'] = active_wound

    # Calculate Injury Fatigue
    character['powerful_build']=False
    character['ac_buff'] = 0
    character['injury_fatigue'] = calculate_injury_fatigue(active_wound, max_wound)
    character['exhaustion'] = exhaustion
    character['extra_injury_fatigue'] = extra_injury_fatigue
    total_debuff = int(character['injury_fatigue']) + int(character['exhaustion']) + int(
        character['extra_injury_fatigue'])

    # Calculate Injuty Fatigue Debuffs Based on Wound points
    injury_fatigue_ST_debuff = 0
    injury_fatigue_DX_debuff = 0
    base_movement_speed = int(character['movement_speed'])
    injury_fatigue_movement_debuff = 0
    injury_fatigue_movement_debuff_text = ""
    injury_fatigue_extra_effects = ""
    injury_fatigue_debuff_reason = "No Injury Fatigue"
    if total_debuff < 1:
        vp_modifier = character['CN_modifier']
        injury_fatigue_movement_debuff_text = "None"
        character['injury_fatigue_debuffs'] = "None"
        character = remove_debuff_incall(character, "ST_Injury_Fatigue")
        character = remove_debuff_incall(character, "DX_Injury_Fatigue")
        character = remove_debuff_incall(character, "movement_Injury_Fatigue")

    if total_debuff == 1:

        injury_fatigue_ST_debuff = - 1
        injury_fatigue_DX_debuff = -1
        injury_fatigue_movement_debuff = -5
        injury_fatigue_movement_debuff_text = "-5ft "
        injury_fatigue_extra_effects = "Disadvantage of Physical ability checks or contests. <br>10% Chance of Spell Failure"
        injury_fatigue_debuff_reason = "One Level of Injury Fatigue"

    if total_debuff == 2:
        injury_fatigue_ST_debuff = - 3
        injury_fatigue_DX_debuff = - 3
        injury_fatigue_movement_debuff = -10
        injury_fatigue_movement_debuff_text = "-10ft "
        injury_fatigue_extra_effects = "Disadvantage of all ability checks or contests. <br>30% Chance of Spell Failure"
        injury_fatigue_debuff_reason = "Two Levels of Injury Fatigue"

    if total_debuff == 3:
        injury_fatigue_ST_debuff = - 5
        injury_fatigue_DX_debuff = - 5
        injury_fatigue_movement_debuff = -15
        injury_fatigue_movement_debuff_text = "-15ft"
        injury_fatigue_extra_effects = "Disadvantage of all ability checks or contests, attacks and saving throws. <br>50% Chance of Spell Failure"
        injury_fatigue_debuff_reason = "Three Levels of Injury Fatigue"
    if total_debuff == 4:
        injury_fatigue_ST_debuff = - 5
        injury_fatigue_DX_debuff = - 5
        base_movement_speed = 0
        injury_fatigue_movement_debuff_text = "Incapacitated"
        injury_fatigue_extra_effects = "Can't take actions or reactions."
        injury_fatigue_debuff_reason = "Four Levels of Injury Fatigue, you are Incapacitated"
    if total_debuff == 5:
        injury_fatigue_ST_debuff = - 5
        injury_fatigue_DX_debuff = - 5
        base_movement_speed = -10
        injury_fatigue_movement_debuff_text = "Incapacitated"
        injury_fatigue_debuff_reason = "Five Levels of Injury Fatigue, you are Incapacitated"

    if total_debuff == 6:
        character['active_ST'] = int(character['ST']) - 5
        injury_fatigue_DX_debuff = - 5
        base_movement_speed = -10
        injury_fatigue_movement_debuff_text = "Dead"
        injury_fatigue_debuff_reason = "Six Levels of Injury Fatigue, you are DEAD"


    # Apply Debuffs to Stats
    add_new_debuff(character, "debuff_st", injury_fatigue_ST_debuff, injury_fatigue_debuff_reason, "ST_Injury_Fatigue",
                   False)
    add_new_debuff(character, "debuff_dx", injury_fatigue_DX_debuff, injury_fatigue_debuff_reason, "DX_Injury_Fatigue",
                   False)
    add_new_debuff(character, "debuff_movement", injury_fatigue_movement_debuff, injury_fatigue_debuff_reason,
                   "movement_Injury_Fatigue", False)

    apply_debuffs(character)
    if total_debuff > 0:
        vp_modifier = character['active_wound_points']
    else:
        vp_modifier = character['active_CN']
    # Calculate the rest of the stats
    character['encumbrance'] = calculate_encumbrance_level(name, character['active_ST'])
    character['active_movement_speed'] = update_movement_speed(base_movement_speed, injury_fatigue_movement_debuff,
                                                               int(calculate_encumbrance_penalty(
                                                                   character['encumbrance']))) + character[
                                             "debuff_movement"]
    character['encumbrance_penalty_explained'] = explain_encumbrance_penalty(character['encumbrance'])
    character['active_movement_debuffs'] = injury_fatigue_movement_debuff_text
    character['injury_fatigue_debuffs'] = injury_fatigue_extra_effects
    character['total_inventory_weight'] = sum(item['total_weight'] for item in character['inventory'])
    # Caculate Vitality Points and Max Vitality Points
    character['max_vitality_points'] = calculate_vitality_points(character['vitality_points_dice_rolls'],
                                                                 character['level'], vp_modifier) + character[
                                           'debuff_max_vp']
    character["active_vitality_points"] = min(active_vitality, character["max_vitality_points"])
    sorted_skills = dict(sorted(character['skills'].items()))
    character['skills'] = sorted_skills
    save_character(character)
    update_stats_modifiers(character)
    update_armor_values(character)
    update_proficiency_bonus_incall(character)
    character['weapon_hit_chances'] = calculate_hit_chances(character)
    character['weapon_total_damage_modifier'] = calculate_total_weapon_damage_modifier(character)
    character['passive_perception']=10+int(character['WP_modifier'])
    save_character(character)
    
    # Redirect back to the same view mode
    return redirect(url_for('view_character', name=name, view=view_mode))


# Route to display the add item form for a specific character
@app.route('/character/<name>/inventory/add_item', methods=['GET'])
def add_item(name):
    character = load_character(name)
    if character:
        return render_template('add_item.html', character=character)
    else:
        return "Character not found", 404


# Route to handle adding an item to the inventory of a specific character
@app.route('/character/<name>/inventory/add_item', methods=['POST'])
def add_item_post(name):
    character = load_character(name)
    if character:
        item_name = request.form['item_name']
        units = int(request.form['units'])
        weight_per_unit = float(request.form['weight_per_unit'])
        additional_info = request.form['additional_info']
        # Calculate total weight
        total_weight = units * weight_per_unit
        
        # Container properties
        is_container = request.form.get('is_container') == 'on'
        container_capacity = float(request.form.get('container_capacity', 0)) if is_container else None
        weight_reduction = float(request.form.get('weight_reduction', 0)) if is_container else None
        
        is_armor = request.form.get('is_armor') == 'on'
        ac_value = request.form.get('ac_value') if is_armor else None
        dx_modifier = request.form.get('dx_modifier') == 'on' if is_armor else None
        modifiers = request.form.get('modifiers') if is_armor else None
        conditions = request.form.get('conditions') if is_armor else None

        is_weapon = request.form.get('is_weapon') =='on'
        damage_dice = request.form.get('damage_dice') if is_weapon else None
        weapon_modifiers = request.form.get('weapon_modifiers') if is_weapon else None
        weapon_stat_modifier = request.form.get('stat_modifier') if is_weapon else None
        weapon_conditions = request.form.get('weapon_conditions') if is_weapon else None
        weapon_is_ranged = (request.form.get('is_ranged') =='on') if is_weapon else None
        weapon_normal_range = request.form.get('normal_range') if (is_weapon and weapon_is_ranged) else None
        weapon_long_range = request.form.get('long_range') if (is_weapon and weapon_is_ranged) else None

        # Create a dictionary for the item and add it to the character's inventory
        item = {
            'item_name': item_name,
            'units': units,
            'weight_per_unit': weight_per_unit,
            'total_weight': total_weight,  # For containers, this will be updated with contents weight
            'additional_info': additional_info,
            'is_armor': is_armor,
            'ac_value': ac_value,
            'dx_modifier': dx_modifier,
            'modifiers': modifiers,
            'conditions': conditions,
            'is_weapon': is_weapon,
            'damage_dice': damage_dice,
            'weapon_modifiers': weapon_modifiers,
            'weapon_stat_modifier': weapon_stat_modifier,
            'weapon_conditions': weapon_conditions,
            'weapon_is_ranged': weapon_is_ranged,
            'weapon_normal_range': weapon_normal_range,
            'weapon_long_range': weapon_long_range,
            'is_container': is_container,
            'container_capacity': container_capacity,
            'weight_reduction': weight_reduction,
            'contents': [] if is_container else None
        }
        
        # For containers, total_weight is container weight + contents weight
        if is_container:
            item['total_weight'] = total_weight  # Initially just the container's own weight
            
        character['inventory'].append(item)
        save_character(character)
        update_character(character['name'])
        return redirect(url_for('view_character', name=name))
    else:
        return "Character not found", 404


# Route to display the current inventory of a specific character
@app.route('/character/<name>/inventory', methods=['GET'])
def show_inventory(name):
    # Load the character data
    character = load_character(name)
    if not character:
        return "Character not found", 404
    total_inventory_weight = sum(item['total_weight'] for item in character['inventory'])
    # Render the inventory page
    return render_template('inventory.html', character=character, total_inventory_weight=total_inventory_weight)


@app.route('/character/<name>/inventory/drop_item', methods=['POST'])
def drop_item(name):
    character = load_character(name)
    if character:
        item_name = request.form['item_name']
        # Find the item in inventory
        item = next((item for item in character.get('inventory', []) if item['item_name'] == item_name), None)
        if item:
            # Remove the item from inventory and add to 'on_the_ground'
            character['inventory'] = [i for i in character.get('inventory', []) if i['item_name'] != item_name]
            if 'on_the_ground' not in character:
                character['on_the_ground'] = []
            character['on_the_ground'].append(item)

            # Save the updated character
            save_character(character)
            update_character(character['name'])
            return redirect(url_for('view_character', name=name))
    return "Character not found", 404


@app.route('/character/<name>/inventory/store_item', methods=['POST'])
def store_item(name):
    character = load_character(name)
    if character:
        item_name = request.form['item_name']
        # Find the item in inventory
        item = next((item for item in character.get('inventory', []) if item['item_name'] == item_name), None)
        if item:
            # Remove the item from inventory and add to 'house_inventory'
            character['inventory'] = [i for i in character.get('inventory', []) if i['item_name'] != item_name]
            if 'house_inventory' not in character:
                character['house_inventory'] = []
            character['house_inventory'].append(item)

            # Save the updated character
            save_character(character)
            update_character(character['name'])
            return redirect(url_for('view_character', name=name))
    return "Character not found", 404


@app.route('/character/<name>/inventory/pick_up', methods=['POST'])
def pickup_item(name):
    character = load_character(name)
    if character:
        item_name = request.form['item_name']
        # print(f'Im picking up {item_name}')
        # Check if item is in 'on_the_ground'
        item = next((item for item in character.get('on_the_ground', []) if item['item_name'] == item_name), None)
        if item:
            # Remove the item from 'on_the_ground' and add to inventory
            character['on_the_ground'] = [i for i in character.get('on_the_ground', []) if
                                          i['item_name'] != item_name]
            if 'inventory' not in character:
                character['inventory'] = []
            character['inventory'].append(item)

        # Check if item is in 'house_inventory'
        # print(f'Im picking up {item_name}')
        item = next((item for item in character.get('house_inventory', []) if item['item_name'] == item_name), None)
        if item:
            # Remove the item from 'house_inventory' and add to inventory
            character['house_inventory'] = [i for i in character.get('house_inventory', []) if
                                            i['item_name'] != item_name]
            if 'inventory' not in character:
                character['inventory'] = []
            character['inventory'].append(item)

        # Save the updated character
        save_character(character)
        update_character(character['name'])
        return redirect(url_for('view_character', name=name))
    else:
        return "Character not found", 404


@app.route('/character/<name>/inventory/reset_on_the_ground', methods=['POST'])
def reset_on_the_ground(name):
    character = load_character(name)
    if character:
        # Clear the 'on_the_ground' list
        character['on_the_ground'] = []
        save_character(character)
        return redirect(url_for('view_character', name=name))
    return "Character not found", 404


@app.route('/character/<name>/toggle_shield', methods=['POST'])
def equip_shield(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404
    shield_equipped = request.form.get('shield_equipped')
    if shield_equipped:
        character['shield_equipped'] = True
        total_ac = character['armor']['ac_value'] + get_modifier(character['active_DX']) + character['armor'][
            'modifier'] + 2
        character['total_ac'] = total_ac

    else:
        character['shield_equipped'] = False
        total_ac = character['armor']['ac_value'] + get_modifier(character['active_DX']) + character['armor'][
            'modifier']
        character['total_ac'] = total_ac
    # Update AC value based on wether there is a shield equipped or not

    save_character(character)
    update_character(name)
    return redirect(url_for('view_character', name=name))


@app.route('/character/<name>/equip_armor', methods=['POST'])
def equip_armor(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404
    selected_armor_name = request.form.get('selected_armor', 'No Armor')
    armor_items = [item for item in character['inventory'] if item.get('is_armor')]

    if selected_armor_name == 'No Armor':
        character['armor'] = {
            'name': None,
            'ac_value': 10,
            'modifier': 0,
            'dx_modifier': True,
            'conditions': None
        }
    else:
        armor = next((item for item in armor_items if item['item_name'] == selected_armor_name), None)
        if armor:

            character['armor'] = {
                'name': armor['item_name'],
                'ac_value': int(armor['ac_value']) if armor['ac_value'] else 0,
                'modifier': int(armor['modifier']) if armor.get('modifier') else 0,
                'dx_modifier': armor['dx_modifier'],
                'conditions': armor.get('conditions')
            }
        else:
            return "Selected armor not found in inventory", 404

    # Update AC value based on the selected armor and DX modifier

    save_character(character)
    update_character(name)
    return redirect(url_for('view_character', name=name))

@app.route("/character/<name>/apply_weapon_proficiency", methods=["POST"])
def apply_weapon_proficiency(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404
    # print(request.form)
    selected_skill = request.form.get("selected_weapon_proficiency")
    # print(selected_skill)
    if selected_skill == "NO_SELECTION":
        selected_skill = None

    character['weapon']["weapon_proficiency"] = selected_skill  # Store selection
    save_character(character)
    update_character(name)
    return redirect(url_for('view_character', name=name))

@app.route('/character/<name>/equip_weapon', methods=['POST'])
def equip_weapon(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404
    selected_weapon_name = request.form.get('selected_weapon', 'Unarmed')
    weapon_items = [item for item in character['inventory'] if item.get('is_weapon')]

    if selected_weapon_name == 'Unarmed':
        character['weapon'] = {
            'name': 'Unarmed',
            'damage_dice': 'd4',
            'weapon_stat_modifier': 'Strength',
            'weapon_modifiers':0
        }
    else:
        weapon = next((item for item in weapon_items if item['item_name'] == selected_weapon_name), None)
        if weapon:
            character['weapon'] = {
                'name': weapon['item_name'],
                'damage_dice': weapon['damage_dice'],
                'weapon_stat_modifier': (weapon['weapon_stat_modifier']) if weapon.get('weapon_stat_modifier') else None,
                'weapon_modifiers': weapon['weapon_modifiers'],
                'weapon_conditions': weapon.get('weapon_conditions'),
                'weapon_normal_range':weapon.get('weapon_normal_range'),
                'weapon_long_range': weapon.get('weapon_long_range')
            }
        else:
            return "Selected weapon not found in inventory", 404

    # Update AC value based on the selected armor and DX modifier

    save_character(character)
    update_character(name)
    return redirect(url_for('view_character', name=name))

def calculate_hit_chances(character):
    weapon_stat_modifier = 0  # Default value
    if character['weapon'].get('weapon_stat_modifier') == 'Strength':
        weapon_stat_modifier = int(character['ST_modifier'])
    elif character['weapon'].get('weapon_stat_modifier') == 'Dexterity':
        weapon_stat_modifier = int(character['DX_modifier'])

    total_value = 0
    if character.get('weapon', {}).get("weapon_proficiency"):
        total_value = character["skills"].get(character['weapon']["weapon_proficiency"], {}).get("total_value", 0)

    total_modifier = calculate_total_weapon_damage_modifier(character)
    total_increased_hit_chance = total_modifier + int(total_value)
    return total_increased_hit_chance

def calculate_total_weapon_damage_modifier(character):
    weapon_stat_modifier = 0  # Default value
    if character['weapon'].get('weapon_stat_modifier') == 'Strength':
        weapon_stat_modifier = int(character['ST_modifier'])
    elif character['weapon'].get('weapon_stat_modifier') == 'Dexterity':
        weapon_stat_modifier = int(character['DX_modifier'])

    weapon_modifiers = 0  # Default value
    if character['weapon'].get('weapon_modifiers') and character['weapon']['weapon_modifiers'] != "":
        weapon_modifiers = int(character['weapon']['weapon_modifiers'])

    total_increased_hit_chance = weapon_modifiers + weapon_stat_modifier
    return int(total_increased_hit_chance)

@app.route('/character/<name>/update_temporary_armor_modifier', methods=['POST'])
def update_temporary_armor_modifier(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404
    modifier_value = int(request.form.get('temporary_armor_modifier'))
    character['temp_armor_modifier'] = modifier_value

    # Update AC value based on the selected armor and DX modifier

    save_character(character)
    update_character(name)
    return redirect(url_for('view_character', name=name))


@app.route("/add_trait/<name>", methods=["POST"])
def add_trait(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404

    new_trait = {
        "id": str(uuid.uuid4()),  # Unique ID for the ability
        "name": request.form["trait_name"],
        "description": request.form["trait_description"],

    }

    if "traits" not in character:
        character["traits"] = []

    character["traits"].append(new_trait)
    save_character(character)

    return redirect(url_for("view_character", name=name))


@app.route("/add_trait_from_level_up/<name>", methods=["POST"])
def add_trait_from_level_up(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404

    new_trait = {
        "id": str(uuid.uuid4()),  # Unique ID for the ability
        "name": request.form["trait_name"],
        "description": request.form["trait_description"],

    }

    if "traits" not in character:
        character["traits"] = []

    character["traits"].append(new_trait)
    save_character(character)

    return redirect(url_for("level_up", name=name))

@app.route("/add_trait_from_creation/<name>", methods=["POST"])
def add_trait_from_creation(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404

    new_trait = {
        "id": str(uuid.uuid4()),  # Unique ID for the ability
        "name": request.form["trait_name"],
        "description": request.form["trait_description"],

    }

    if "traits" not in character:
        character["traits"] = []

    character["traits"].append(new_trait)
    save_character(character)

    return render_template("create_character_part2.html", character=character)
@app.route("/edit_trait/<name>/<trait_id>", methods=["GET"])
def edit_trait(name, trait_id):
    character = load_character(name)
    if not character:
        return "Character not found", 404

    trait = next((t for t in character.get("traits", []) if t["id"] == trait_id), None)
    if not trait:
        return "Trait not found", 404

    return render_template("edit_trait.html", character=character, trait=trait)


@app.route('/remove_skill/<name>', methods=['POST'])
def remove_skill(name):
    skill_to_remove = request.form.get("skill_to_remove")

    # Load the character (assuming you have a function to get character data)
    character = load_character(name)
    if not character:
        return "Character not found", 404

    if character and (skill_to_remove in character["skills"]):
        del character["skills"][skill_to_remove]  # Remove the skill

        # Save changes (assuming you have a save function)
        save_character(character)

    update_character(name)
    return redirect(url_for("view_character", name=name))

@app.route("/edit_trait/<name>/<trait_id>", methods=["POST"])
def update_trait(name, trait_id):
    character = load_character(name)
    if not character:
        return "Character not found", 404

    trait = next((t for t in character.get("traits", []) if t["id"] == trait_id), None)
    if not trait:
        return "Trait not found", 404

    trait["name"] = request.form["trait_name"]
    trait["description"] = request.form["trait_description"]

    save_character(character)

    return redirect(url_for("view_character", name=name))


# Route to display the add proficiency form for a specific character
@app.route('/character/<name>/add_proficiency', methods=['GET'])
def add_proficiency(name):
    character = load_character(name)
    if character:
        return render_template('add_proficiency.html', character=character)
    else:
        return "Character not found", 404


@app.route('/character/<name>/add_proficiency', methods=['POST'])
def add_proficiency_post(name):
    character = load_character(name)
    if character:
        proficiency_name = request.form['proficiency_name']
        proficiency_description = request.form['proficiency_description']

        proficiency = {
            'proficiency_name': proficiency_name,
            'proficiency_description': proficiency_description,

        }

        character['proficiencies'].append(proficiency)

        # Save the character's updated data
        save_character(character)

        return redirect(url_for('view_character', name=name))
    else:
        return "Character not found", 404


@app.route('/character/<name>/delete_proficiency', methods=['POST'])
def delete_proficiency(name):
    character = load_character(name)
    if character:
        data = request.get_json()
        proficiency_index = int(data['proficiency_index'])

        # Delete the proficiency at the given index
        if proficiency_index < len(character['proficiencies']):
            del character['proficiencies'][proficiency_index]

            # Save the character's updated data
            save_character(character)

            return jsonify({"message": "Proficiency deleted successfully"}), 200
        else:
            return jsonify({"error": "Invalid proficiency index"}), 400
    else:
        return jsonify({"error": "Character not found"}), 404


@app.route('/character/<name>/update_proficiency', methods=['POST'])
def update_proficiency(name):
    character = load_character(name)
    if character:
        data = request.get_json()
        proficiency_index = int(data['proficiency_index'])
        new_name = data['new_name']
        new_description = data['new_description']

        # Update the proficiency data
        character['proficiencies'][proficiency_index]['proficiency_name'] = new_name
        character['proficiencies'][proficiency_index]['proficiency_description'] = new_description

        # Save the character's updated data
        save_character(character)

        return jsonify({"message": "Proficiency updated successfully"}), 200
    else:
        return jsonify({"error": "Character not found"}), 404


@app.route('/character/<name>/add_debuff', methods=['POST'])
def add_debuff(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404

    debuff_name = request.form["debuff_name"]
    debuff_value = float(request.form["debuff_value"])  # Using float to handle decimal values
    debuff_reason = request.form["debuff_reason"]
    operation = request.form.get("operation", "buff")  # Default to buff if not specified
    
    # Make value negative if it's a debuff
    if operation == "debuff":
        debuff_value = -abs(debuff_value)  # Ensure negative
    else:  # buff
        debuff_value = abs(debuff_value)   # Ensure positive
        
    debuff_id = debuff_name + "_" + debuff_reason

    # Handle skill-based debuffs (remove 'debuff_' prefix)
    if debuff_name.startswith("debuff_"):
        skill_name = debuff_name[7:].replace('_', ' ')  # Convert back to normal text
        if skill_name in character["skills"]:
            debuff_name = skill_name  # Store as the actual skill name

    add_new_debuff(character, debuff_name, debuff_value, debuff_reason, debuff_id, True)

    save_character(character)
    update_character(name)
    return redirect(url_for("view_character", name=name))


@app.route('/character/<name>/remove_debuff/<debuff_id>', methods=['POST'])
def remove_debuff(name, debuff_id):
    character = load_character(name)
    if not character:
        return "Character not found", 404
    remove_debuff_incall(character, debuff_id)
   
    # apply_debuffs(character)
    save_character(character)
    update_character(name)
    return redirect(url_for("view_character", name=name))


def remove_debuff_incall(character, debuff_id):
    debuff_name = debuff_id[7:]
    debuffed_skill = debuff_name.split('_')[0]
    debuffed_skill = debuffed_skill.replace('_', '')
    if debuffed_skill in character["skills"]:
        for debuff in character["debuffs"]:
            if debuff['id'] == debuff_id:
                debuff_value = int((debuff['value']))
        skill = character['skills'][debuffed_skill]
        skill['buff'] = skill.get('buff', 0) - debuff_value
    character["debuffs"] = [debuff for debuff in character["debuffs"] if debuff["id"] != debuff_id]
    return character


def update_purse_function(name, amount, currency):
    """Updates character's purse with proper coin conversion."""
    character = load_character(name)
    if not character:
        return "Character not found", 404
    if character:
        # Convert all coins to total copper for easy calculations
        total_copper = character["gold"] * 100 + character["silver"] * 10 + character["copper"]

        # Adjust total copper based on input
        if currency == "gold":
            total_copper += amount * 100
        elif currency == "silver":
            total_copper += amount * 10
        else:  # copper
            total_copper += amount

        # Prevent negative purse values
        if total_copper < 0:
            return False  # Not enough money

        # Convert back to gold, silver, copper
        character["gold"] = total_copper // 100
        character["silver"] = (total_copper % 100) // 10
        character["copper"] = total_copper % 10
        save_character(character)
        update_character(name)
        return True  # Success


@app.route("/character/<name>/", methods=["POST"])
def update_purse(name):
    amount = int(request.form.get("amount"))
    currency = request.form.get("currency")
    operation = request.form.get("operation", "add")

    # If operation is subtract, make amount negative
    if operation == "subtract":
        amount = -amount

    success = update_purse_function(name, amount, currency)

    if not success:
        # Instead of returning error, store it in session and redirect
        session['purse_error'] = f"Not enough {currency}!"
    else:
        # Clear any existing error message
        session.pop('purse_error', None)

    return redirect(url_for("view_character", name=name))


@app.route("/character/<name>/update_proficiency_bonus", methods=["POST"])
def update_proficiency_bonus(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404
    if character:
        update_proficiency_bonus_incall(character)
    update_character(name)
    return redirect(url_for("view_character", name=name))


@app.route("/character/<name>/update_proficiency_bonus_from_level_up", methods=["POST"])
def update_proficiency_bonus_from_level_up(name):
    character = load_character(name)
    update_character(name)
    return render_template("level_up.html", character=character)

@app.route("/character/<name>/update_proficiency_bonus_from_creation", methods=["POST"])
def update_proficiency_bonus_from_creation(name):
    character = load_character(name)
    update_character(name)
    return render_template("create_character_part2.html", character=character)

def update_proficiency_bonus_incall(character):
    for skill in character['skills']:
        # character['skills'][skill]['proficiency_bonus'] = int(request.form.get(skill, 0))
        # remove adding the Stat Modifier here
        # modifier_to_get = character['skills'][skill]['stat'] + "_modifier"
        character['skills'][skill]['total_value'] = (
                int(character['skills'][skill]['proficiency_bonus']) +
                int(character['skills'][skill].get('buff', 0))   # Default to 0 if 'buff' doesn't exist
                # + int((character[modifier_to_get]))
        )
        # Save the updated character data to JSON
    save_character(character)


@app.route("/character/<name>/add_custom_skill", methods=["POST"])
def add_custom_skill(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404

    # Retrieve form data
    custom_skill_name = request.form.get("custom_skill_name")
    # custom_skill_stat = request.form.get("custom_skill_stat")  # e.g., 'DX', 'IN', etc.

    if (custom_skill_name):
    # and custom_skill_stat):
    #     stat_modifier = get_modifier(character[custom_skill_stat])  # Ensure correct stat modifier
        proficiency_bonus = 0  # Default, user can update later

        character["skills"][custom_skill_name] = {
            # "stat": custom_skill_stat,
            "proficiency_bonus": proficiency_bonus,
            "buff": 0
        }

        save_character(character)
        update_character(name)  # Ensure updates reflect

    return redirect(url_for("view_character", name=name))


@app.route("/character/<name>/add_custom_skill_from_creation", methods=["POST"])
def add_custom_skill_from_creation(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404

    # Retrieve form data
    custom_skill_name = request.form.get("custom_skill_name")
    custom_skill_stat = request.form.get("custom_skill_stat")  # e.g., 'DX', 'IN', etc.

    if custom_skill_name and custom_skill_stat:
        stat_modifier = get_modifier(character[custom_skill_stat])  # Ensure correct stat modifier
        proficiency_bonus = 0  # Default, user can update later

        character["skills"][custom_skill_name] = {
            "stat": custom_skill_stat,
            "proficiency_bonus": proficiency_bonus,
            "buff": 0
        }

        save_character(character)
        update_character(name)  # Ensure updates reflect

    return render_template("create_character_part2.html", character=character)
@app.route("/character/<name>/add_custom_skill_from_level_up", methods=["POST"])
def add_custom_skill_from_level_up(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404

    # Retrieve form data
    custom_skill_name = request.form.get("custom_skill_name")
    custom_skill_stat = request.form.get("custom_skill_stat")  # e.g., 'DX', 'IN', etc.

    if custom_skill_name and custom_skill_stat:
        stat_modifier = get_modifier(character[custom_skill_stat])  # Ensure correct stat modifier
        proficiency_bonus = 0  # Default, user can update later

        character["skills"][custom_skill_name] = {
            "stat": custom_skill_stat,
            "proficiency_bonus": proficiency_bonus,
            "buff": 0
        }

        save_character(character)
        update_character(name)  # Ensure updates reflect

    return render_template("level_up.html", character=character)

@app.route("/add_active_ability/<name>", methods=["POST"])
def add_active_ability(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404

    new_ability = {
        "id": str(uuid.uuid4()),  # Unique ID for the ability
        "name": request.form["ability_name"],
        "description": request.form["ability_description"],
        "dc": int(request.form["ability_dc"]),
        "recharges_on": request.form["rest_type"],
        "uses_per_long_rest": int(request.form["ability_uses"]),
        "uses_left": int(request.form["ability_uses"]),  # Start with full uses
    }

    if "active_abilities" not in character:
        character["active_abilities"] = []

    character["active_abilities"].append(new_ability)
    save_character(character)

    return redirect(url_for("view_character", name=name))


@app.route("/add_active_ability_from_level_up/<name>", methods=["POST"])
def add_active_ability_from_level_up(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404

    new_ability = {
        "id": str(uuid.uuid4()),  # Unique ID for the ability
        "name": request.form["ability_name"],
        "description": request.form["ability_description"],
        "dc": int(request.form["ability_dc"]),
        "uses_per_long_rest": int(request.form["ability_uses"]),
        "uses_left": int(request.form["ability_uses"]),  # Start with full uses
    }

    if "active_abilities" not in character:
        character["active_abilities"] = []

    character["active_abilities"].append(new_ability)
    save_character(character)
    return render_template("level_up.html", character=character)

@app.route("/add_active_ability_from_creation/<name>", methods=["POST"])
def add_active_ability_from_creation(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404

    new_ability = {
        "id": str(uuid.uuid4()),  # Unique ID for the ability
        "name": request.form["ability_name"],
        "description": request.form["ability_description"],
        "dc": int(request.form["ability_dc"]),
        "uses_per_long_rest": int(request.form["ability_uses"]),
        "uses_left": int(request.form["ability_uses"]),  # Start with full uses
    }

    if "active_abilities" not in character:
        character["active_abilities"] = []

    character["active_abilities"].append(new_ability)
    save_character(character)
    return render_template("create_character_part2.html", character=character)
@app.route("/use_ability/<name>/<ability_id>", methods=["POST"])
def use_ability(name, ability_id):
    character = load_character(name)
    if not character:
        return "Character not found", 404

    for ability in character.get("active_abilities", []):
        if ability["id"] == ability_id:
            ability["uses_left"] -= 1
            break

    save_character(character)
    return redirect(url_for("view_character", name=name))


@app.route("/remove_active_ability/<name>/<ability_id>", methods=["POST"])
def remove_active_ability(name, ability_id):
    character = load_character(name)
    if not character:
        return "Character not found", 404
    new_active_abilities = []
    for ability in character.get("active_abilities", []):
        if ability["id"] != ability_id:
            new_active_abilities.append(ability)

    character["active_abilities"] = new_active_abilities
    save_character(character)
    return redirect(url_for("view_character", name=name))


@app.route("/remove_trait/<name>/<trait_id>", methods=["POST"])
def remove_trait(name, trait_id):
    character = load_character(name)
    if not character:
        return "Character not found", 404
    new_traits = []
    for trait in character.get("traits", []):
        if trait["id"] != trait_id:
            new_traits.append(trait)

    character["traits"] = new_traits
    save_character(character)
    return redirect(url_for("view_character", name=name))


def reload_abilities_on_long_rest(character):

    for ability in character.get("active_abilities", []):
        ability["uses_left"] = ability["uses_per_long_rest"]
    save_character(character)

def reload_abilities_on_short_rest(character):

    for ability in character.get("active_abilities", []):
        if ability['recharges_on'] == 'short_rest':
            ability["uses_left"] = ability["uses_per_long_rest"]
    save_character(character)
@app.route('/level_up/<name>', methods=['GET', 'POST'])
def level_up(name):
   
    character = load_character(name)
    hit_dice_roll = request.form.get('hit_dice_roll')
    wp_increase = request.form.get('increase_wound_points')

    character['vitality_points_dice_rolls'].append(int(hit_dice_roll))
    character['max_wound_points'] += int(wp_increase)
    character['active_vitality_points'] = character['max_vitality_points']
    character['active_wound_points'] = character['max_wound_points']
    character['level'] +=1
    save_character(character)
    update_character(name)
    return redirect(url_for("view_character", name=name))


@app.route('/change_dc/<name>/<ability_id>/<int:change>', methods=['POST'])
def change_dc(name, ability_id, change):
    character = load_character(name)
    if not character:
        return "Character not found", 404

    # Find the ability and update its DC
    for ability in character.get("active_abilities", []):
        if ability["id"] == ability_id:
            ability["dc"] += change
            break

    save_character(character)
    return redirect(url_for("view_character", name=name))


@app.route('/increase_stat/<name>/<stat_id>', methods=['POST'])
def increase_stat(name, stat_id):
    character = load_character(name)

    if not character:
        return "Character not found", 404

    current_value = int(character[stat_id])
    character[stat_id] = current_value + 1

    save_character(character)
    return render_template("level_up.html", character=character)


@app.route('/confirm_level_up/<name>', methods=['POST'])
def confirm_level_up(name):
    character = load_character(name)

    if not character:
        return "Character not found", 404

    character['vitality_points_dice_rolls'].append(request.form.get('vp_roll'))
    character["max_wound_points"] += int(request.form.get('wp'))
    character['level'] +=1
    save_character(character)
    update_character(name)
    return redirect(url_for("view_character", name=name))


@app.route('/short_rest/<name>', methods=['POST'])
def short_rest(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404

    # Get view mode from query parameter
    view_mode = request.args.get('view', 'desktop')

    if character['active_vitality_points'] < character['max_vitality_points']:
        hit_dice_roll = request.form.get('hit_dice_roll')
        if hit_dice_roll:
            try:
                # Convert to integer and calculate half rounded up
                hit_dice_roll = int(hit_dice_roll)
                healing = math.ceil(hit_dice_roll / 2)
                
                # Apply healing
                character['active_vitality_points'] = min(
                    character['active_vitality_points'] + healing,
                    character['max_vitality_points']
                )
                
                # Save changes
                save_character(character)
            except (ValueError, TypeError) as e:
             
                return "Invalid hit dice roll value", 400

    # Reload abilities that recharge on short rest
    reload_abilities_on_short_rest(character)
    save_character(character)
    
    # Redirect back to the same view mode
    return redirect(url_for("view_character", name=name, view=view_mode))


@app.route('/long_rest/<name>', methods=['POST'])
def long_rest(name):
    character = load_character(name)

    if not character:
        return "Character not found", 404
    character['active_vitality_points'] = character['max_vitality_points']
    character['is_inspired'] = False
    save_character(character)
    reload_abilities_on_long_rest(character)

    return redirect(url_for("view_character", name=name))

@app.route('/is_inspired/<name>', methods=['POST'])
def is_inspired(name):
    character = load_character(name)

    if not character:
        return "Character not found", 404
    character['is_inspired'] = not character['is_inspired']
    save_character(character)
    return redirect(url_for("view_character", name=name))
@app.route('/decrease_dc/<name>/<ability_id>', methods=['POST'])
def decrease_dc(name, ability_id):
    change = -1

    modify_ability_dc(name, ability_id, change)
    return redirect(url_for("view_character", name=name))


@app.route('/increase_dc/<name>/<ability_id>', methods=['POST'])
def increase_dc(name, ability_id):
    change = 1
    modify_ability_dc(name, ability_id, change)

    return redirect(url_for("view_character", name=name))

@app.route('/increase_proficiency/<name>/<proficiency_id>', methods=['POST'])
def increase_proficiency(name, proficiency_id):
    change = 1
    modify_proficiency_value(name, proficiency_id, change)
    update_character(name)
    return redirect(url_for("view_character", name=name))

@app.route('/decrease_proficiency/<name>/<proficiency_id>', methods=['POST'])
def decrease_proficiency(name, proficiency_id):
    change = -1
    modify_proficiency_value(name, proficiency_id, change)
    update_character(name)
    return redirect(url_for("view_character", name=name))
def modify_proficiency_value(name, ability_id, change):
    character = load_character(name)
    if not character:
        return "Character not found", 404
    
    character['skills'][ability_id]['proficiency_bonus'] = int(character['skills'][ability_id]['proficiency_bonus']) + change
    
    save_character(character)
def modify_ability_dc(name, ability_id, change):
    character = load_character(name)
    if not character:
        return "Character not found", 404

    # Find the ability and update its DC
    for ability in character.get("active_abilities", []):
        if ability["id"] == ability_id:
            ability["dc"] += change
            break

    save_character(character)


@app.route('/character/<name>/add_note', methods=['POST'])
def add_note(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404

    # Get note content from form
    note_content = request.form.get('note_content')

    # Initialize notes dictionary if it doesn't exist
    if 'notes' not in character or character['notes'] is None:
        character['notes'] = {}

    # Create a new note with ID, content, and timestamp
    note_id = str(uuid.uuid4())
    note = {
        'content': note_content,
        'date': datetime.now().strftime('%Y-%m-%d %H:%M')
    }

    # Add to character's notes
    character["notes"][note_id] = note

    # Save character
    save_character(character)

    # Redirect back to character sheet
    return redirect(url_for("view_character", name=name))


@app.route('/character/<name>/edit_note', methods=['POST'])
def edit_note(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404

    # Get note details from form
    note_id = request.form.get('note_id')
    note_content = request.form.get('note_content')

    # Check if note exists
    if 'notes' in character and note_id in character['notes']:
        # Update note content
        character["notes"][note_id]['content'] = note_content
        # Optionally update the timestamp to show it was edited
        character["notes"][note_id]['date'] = datetime.now().strftime('%Y-%m-%d %H:%M') + ' (edited)'

        # Save character
        save_character(character)

    # Redirect back to character sheet
    return redirect(url_for("view_character", name=name))


@app.route('/character/<name>/delete_note/<note_id>', methods=['POST'])
def delete_note(name, note_id):
    # Get character
    character = load_character(name)
    if not character:
        return "Character not found", 404

    if 'notes' in character and note_id in character['notes']:
        del character["notes"][note_id]

        # Save character
        save_character(character)

    # Redirect back to character sheet
    return redirect(url_for("view_character", name=name))

@app.route('/character/<name>/inventory/move_to_container', methods=['POST'])
def move_to_container(name):
    character = load_character(name)
    if character:
        item_name = request.form['item_name']
        container_name = request.form['container_name']
        
        # Find the item and container
        item = next((item for item in character['inventory'] if item['item_name'] == item_name), None)
        container = next((container for container in character['inventory'] if container['item_name'] == container_name), None)
        
        if item and container and container['is_container']:
            # Check if there's enough capacity
            current_container_weight = sum(content['total_weight'] for content in container['contents'])
            if current_container_weight + item['total_weight'] <= container['container_capacity']:
                # Remove item from inventory
                character['inventory'] = [i for i in character['inventory'] if i['item_name'] != item_name]
                
                # Store original weight before reduction
                original_weight = item['total_weight']
                
                # Apply weight reduction if any
                if container['weight_reduction'] > 0:
                    reduced_weight = original_weight * (1 - container['weight_reduction'] / 100)
                    item['total_weight'] = reduced_weight
                
                # Add to container contents
                container['contents'].append(item)
                
                # Calculate container's total weight:
                # Container's own weight + sum of contents weights (with reduction already applied)
                container_own_weight = container['weight_per_unit'] * container['units']
                contents_weight = sum(content['total_weight'] for content in container['contents'])
                container['total_weight'] = container_own_weight + contents_weight
                
                save_character(character)
                update_character(character['name'])
                return redirect(url_for('view_character', name=name))
            else:
                flash('Not enough capacity in the container!', 'error')
                return redirect(url_for('view_character', name=name))
    
    return "Character not found", 404

@app.route('/character/<name>/inventory/remove_from_container', methods=['POST'])
def remove_from_container(name):
    character = load_character(name)
    if character:
        item_name = request.form['item_name']
        container_name = request.form['container_name']
        
        # Find the container
        container = next((container for container in character['inventory'] if container['item_name'] == container_name), None)
        
        if container and container['is_container']:
            # Find the item in the container
            item = next((item for item in container['contents'] if item['item_name'] == item_name), None)
            
            if item:
                # Remove weight reduction if any
                if container['weight_reduction'] > 0:
                    item['total_weight'] /= (1 - container['weight_reduction'] / 100)
                
                # Remove from container and add back to inventory
                container['contents'] = [i for i in container['contents'] if i['item_name'] != item_name]
                character['inventory'].append(item)
                
                # Recalculate container's total weight:
                # Container's own weight + (sum of remaining contents weights with reduction applied)
                container_own_weight = container['weight_per_unit'] * container['units']
                contents_weight = sum(content['total_weight'] for content in container['contents'])
                container['total_weight'] = container_own_weight + contents_weight
                
                save_character(character)
                update_character(character['name'])
                return redirect(url_for('view_character', name=name))
    
    return "Character not found", 404

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
