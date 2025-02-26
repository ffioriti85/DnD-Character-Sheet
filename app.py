from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
# from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, Float
import jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import uuid


app = Flask(__name__)
DATA_FOLDER = 'characters'
characters = {}
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# TODO:
#   Implement EDIT Traits
#   Reformat HTML to look more friendly. Add dropdown menues
#   Reformat Inventory to be more friendly
#   If a modifier or a buff is negative then display in RED, zero in black and positive in Green
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
        'total_ac': 0,
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
        'skills': {
            "Athletics": {"stat": "ST", "proficiency_bonus": 0},
            "Acrobatics": {"stat": "DX", "proficiency_bonus": 0},
            "Sleight of Hand": {"stat": "DX", "proficiency_bonus": 0},
            "Stealth": {"stat": "DX", "proficiency_bonus": 0},
            "Arcana": {"stat": "IN", "proficiency_bonus": 0},
            "History": {"stat": "IN", "proficiency_bonus": 0},
            "Investigation": {"stat": "IN", "proficiency_bonus": 0},
            "Nature": {"stat": "IN", "proficiency_bonus": 0},
            "Religion": {"stat": "IN", "proficiency_bonus": 0},
            "Animal Handling": {"stat": "WP", "proficiency_bonus": 0},
            "Insight": {"stat": "WP", "proficiency_bonus": 0},
            "Medicine": {"stat": "WP", "proficiency_bonus": 0},
            "Perception": {"stat": "WP", "proficiency_bonus": 0},
            "Survival": {"stat": "WP", "proficiency_bonus": 0},
            "Deception": {"stat": "CH", "proficiency_bonus": 0},
            "Intimidation": {"stat": "CH", "proficiency_bonus": 0},
            "Performance": {"stat": "CH", "proficiency_bonus": 0},
            "Persuasion": {"stat": "CH", "proficiency_bonus": 0}
        }
    }

    # Ensure all top-level keys exist
    for key, value in default_character.items():
        if key not in character:
            character[key] = value

    # Ensure nested dictionaries exist properly
    if 'armor' not in character:
        character['armor'] = default_character['armor']
    else:
        for key, value in default_character['armor'].items():
            if key not in character['armor']:
                character['armor'][key] = value

    if 'skills' not in character:
        character['skills'] = default_character['skills']
    else:
        for skill, data in default_character['skills'].items():
            if skill not in character['skills']:
                character['skills'][skill] = data
            else:
                for key, value in data.items():
                    if key not in character['skills'][skill]:
                        character['skills'][skill][key] = value
    save_character(character)  # Save the character data to file
    return character

def save_character_active(character):
    filename = os.path.join(DATA_FOLDER, f"{character['name']}.json")
    with open(filename, 'w') as file:
        json.dump(character, file)

def load_character(name):
    filename = os.path.join(DATA_FOLDER, f"{name}.json")
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            character_data = json.load(file)

        # Ensure inventory is a list of dictionaries
        if 'inventory' not in character_data:
            character_data['inventory'] = []
        elif isinstance(character_data['inventory'], list):
            # Check if each item in the list is a dictionary
            character_data['inventory'] = [
                item if isinstance(item, dict) else {} for item in character_data['inventory']
            ]

        return character_data
    return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']

        # Try to load the character, including the inventory
        character = load_character(name)

        if character:
            # Pass the loaded character object including the inventory
            return redirect(url_for('view_character', name=name))
        else:
            return redirect(url_for('create_character', name=name))

    return render_template('index.html')

#Function to Calculate Modifiers
def get_modifier(stat_value):
    return (stat_value - 10) // 2

def calculate_vitality_points(rolls,level,CN):
    total_vitality_points = 0
    for roll in rolls:
        total_vitality_points += int(roll)
    total_vitality_points += level*get_modifier(CN)
    return total_vitality_points

@app.route('/create/<name>', methods=['GET', 'POST'])
def create_character(name):
    if request.method == 'POST':
        try:
            character_data = {
                'name': name,
                'level':2,
                'race': request.form['race'],
                'height': request.form['height'],
                'debuff_height': 0,
                'weight': request.form['weight'],
                'movement_speed': request.form['movement_speed'],
                "active_movement_debuffs":"None",
                'debuff_movement': 0,
                'active_movement_speed': request.form['movement_speed'],
                'ST': int(request.form['ST']),
                'active_ST': int(request.form['ST']),
                'ST_modifier':get_modifier(int(request.form['ST'])),
                'debuff_ST':0,
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
                'gold': int(request.form['gold']),
                'silver': int(request.form['silver']),
                'copper': int(request.form['copper']),
                'vitality_points_dice_rolls': (request.form['vitality_points'].split(',')),
                'vitality_points': 0,
                'active_vitality_points': 0,
                'max_vitality_points':0,
                'debuff_max_vp': 0,
                'wound_points': int(request.form['wound_points']),
                'active_wound_points': int(request.form['wound_points']),
                'max_wound_points':int(request.form['wound_points']),
                'debuff_max_wp': 0,
                'passive_perception': 10,
                'traits': [],
                'proficiencies': [],
                'inventory': [],
                'injury_fatigue': 0,
                'exhaustion': 0,
                'extra_injury_fatigue':0,
                'encumbrance': 0,
                'active_abilities': [],
                'injury_fatigue_debuffs':"None",
                'total_ac':0,
                'armor' : {
                    'name': None,
                    'ac_value': 10,
                    'modifier': 0,
                    'dx_modifier': True,
                    'conditions': None
                        },
            'shield_equipped': False,
            'temp_armor_modifier':0,
            'debuffs': [],
                'skills': {
                    "Athletics": {"stat": "ST", "proficiency_bonus": 0},
                    "Acrobatics": {"stat": "DX", "proficiency_bonus": 0},
                    "Sleight of Hand": {"stat": "DX", "proficiency_bonus": 0},
                    "Stealth": {"stat": "DX", "proficiency_bonus": 0},
                    "Arcana": {"stat": "IN", "proficiency_bonus": 0},
                    "History": {"stat": "IN", "proficiency_bonus": 0},
                    "Investigation": {"stat": "IN", "proficiency_bonus": 0},
                    "Nature": {"stat": "IN", "proficiency_bonus": 0},
                    "Religion": {"stat": "IN", "proficiency_bonus": 0},
                    "Animal Handling": {"stat": "WP", "proficiency_bonus": 0},
                    "Insight": {"stat": "WP", "proficiency_bonus": 0},
                    "Medicine": {"stat": "WP", "proficiency_bonus": 0},
                    "Perception": {"stat": "WP", "proficiency_bonus": 0},
                    "Survival": {"stat": "WP", "proficiency_bonus": 0},
                    "Deception": {"stat": "CH", "proficiency_bonus": 0},
                    "Intimidation": {"stat": "CH", "proficiency_bonus": 0},
                    "Performance": {"stat": "CH", "proficiency_bonus": 0},
                    "Persuasion": {"stat": "CH", "proficiency_bonus": 0}
                }
            }

        except ValueError:
            # Handle the error if any value cannot be converted to int
            return "Invalid input: all stats must be integers.", 400
        total_vitality_points = calculate_vitality_points(character_data['vitality_points_dice_rolls'],character_data['level'],character_data['CN'])
        character_data['vitality_points']=total_vitality_points
        character_data['active_vitality_points']=total_vitality_points
        character_data['max_vitality_points']=total_vitality_points
        save_character(character_data)  # Save the character data to file

        return redirect(url_for('index'))

    return render_template('create_character.html', name=name)

def update_stats_modifiers(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404
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
            debuff["reason"] = debuff_reason  # Optionally update the reason
            return  # Exit function after updating

    # If the debuff_id wasn't found, add a new debuff
    character["debuffs"].append({
        "name": debuff_name,
        "value": debuff_value,
        "reason": debuff_reason,
        "removable": removable,
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


    return(character)

@app.route('/character/<name>')
def view_character(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404
    character = initialize_character(character)
    # Calculate modifiers
    armor_items = [item for item in character['inventory'] if item.get('is_armor')]

    update_character(name)
    save_character(character)
    if 'armor' not in character:
        character['armor'] = {
            'name': 'None',
            'ac_value': 10,
            'dx_modifier': True,
            'modifiers': 0,
            'conditions': ''
        }

    return render_template('view_character.html', character=character, armor_items=armor_items)

def calculate_injury_fatigue(active_wound, max_wound):
    if active_wound < max_wound and active_wound > max_wound*3/4:
        return 1
    elif active_wound <= max_wound * 3 / 4 and active_wound > max_wound*2/4:
        return 2
    elif active_wound <= max_wound * 2 / 4 and active_wound > max_wound*1/4:
        return 3
    elif active_wound <= max_wound * 1 / 4 and active_wound>1:
        return 4
    elif active_wound == 1:
        return 5
    elif active_wound == 0:
        return 6
    else:
        return 0  # Default case if none of the conditions are met
def calculate_encumbrance_level(name,character_ST):
    character = load_character(name)
    if character:
        if len(character['inventory']) == 0:
            total_inventory_weight = 0
        else:
            total_inventory_weight = sum(item['total_weight'] for item in character['inventory'])

        # character_ST = character["active_ST"]

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
    encumbrance_penalty_explanation= {
        "0": "+5 Movement Speed from being Unencumbered",
        "1": "Normal Movement Speed by being Lightly Encumbered",
        "2": "-10 Movement Speed from being Moderately Encumbered",
        "3":"-15 Movement Speed from being Heavily Encumbered",
        "4": "-20 Movement Speed from being Extremely Encumbered",
        "5": "Can't move because of how much you are carrying",
    }
    encumbrance = str(encumbrance)
    return encumbrance_penalty_explanation[encumbrance]
def update_movement_speed(base_movement_speed,modifier_from_debuff,modifier_from_emcumbrance):
    new_movement_speed = int(base_movement_speed + modifier_from_debuff + modifier_from_emcumbrance)
    if new_movement_speed >0:
        return new_movement_speed
    else:
        return 0
def update_armor_values(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404

    if character['armor']['dx_modifier']:

        dx_modifier = int(character['DX_modifier'])

    else:
        dx_modifier = 0
    if character['shield_equipped']:
        shield_modifier = 2
    else:
        shield_modifier = 0
    temporary_modifier = character['temp_armor_modifier']
    total_ac = character['armor']['ac_value'] + dx_modifier + character['armor']['modifier'] + shield_modifier + character['temp_armor_modifier']
    character['total_ac'] = total_ac

    save_character(character)
    return redirect(url_for('view_character', name=name))
@app.route('/character/<name>/update', methods=['POST'])
def update_character(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404

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
            exhaustion -=1
    if 'heal_exhaustion' in request.form:
        exhaustion=0

    if 'increase_extra_injury_fatigue' in request.form:
        extra_injury_fatigue += 1

    if 'decrease_extra_injury_fatigue' in request.form:
        if extra_injury_fatigue > 0:
            extra_injury_fatigue -= 1

    if 'heal_extra_injury_fatigue' in request.form:
        extra_injury_fatigue = 0

    character['active_wound_points'] = active_wound


    # Calculate Injury Fatigue
    character['injury_fatigue'] = calculate_injury_fatigue(active_wound,max_wound)
    character['exhaustion'] = exhaustion
    character['extra_injury_fatigue'] = extra_injury_fatigue
    total_debuff = int(character['injury_fatigue']) + int(character['exhaustion']) +int(character['extra_injury_fatigue'])

    #Calculate Injuty Fatigue Debuffs Based on Wound points
    injury_fatigue_ST_debuff=0
    injury_fatigue_DX_debuff = 0
    base_movement_speed=int(character['movement_speed'])
    injury_fatigue_movement_debuff = 0
    injury_fatigue_movement_debuff_text = ""
    injury_fatigue_extra_effects=""
    injury_fatigue_debuff_reason = "No Injury Fatigue"
    if total_debuff < 1:
        injury_fatigue_movement_debuff_text ="None"
        character['injury_fatigue_debuffs']="None"
        print("No Injury Fatigue, proceed to remove the debuffs")
        character= remove_debuff_incall(character, "ST_Injury_Fatigue")
        character= remove_debuff_incall(character, "DX_Injury_Fatigue")
        character= remove_debuff_incall(character, "movement_Injury_Fatigue")
        print(character['debuffs'])

    if total_debuff == 1:
        injury_fatigue_ST_debuff= - 1
        injury_fatigue_DX_debuff = -1
        injury_fatigue_movement_debuff = -5
        injury_fatigue_movement_debuff_text = "-5ft "
        injury_fatigue_extra_effects = "Disadvantage of Physical ability checks or contests. <br>10% Chance of Spell Failure"
        injury_fatigue_debuff_reason = "One Level of Injury Fatigue"

    if total_debuff == 2:
        injury_fatigue_ST_debuff= - 3
        injury_fatigue_DX_debuff = - 3
        injury_fatigue_movement_debuff = -10
        injury_fatigue_movement_debuff_text = "-10ft "
        injury_fatigue_extra_effects = "Disadvantage of all ability checks or contests. <br>30% Chance of Spell Failure"
        injury_fatigue_debuff_reason = "Two Levels of Injury Fatigue"

    if total_debuff == 3:
        injury_fatigue_ST_debuff= - 5
        injury_fatigue_DX_debuff = - 5
        injury_fatigue_movement_debuff = -15
        injury_fatigue_movement_debuff_text ="-15ft"
        injury_fatigue_extra_effects = "Disadvantage of all ability checks or contests, attacks and saving throws. <br>50% Chance of Spell Failure"
        injury_fatigue_debuff_reason = "Three Levels of Injury Fatigue"
    if total_debuff == 4:
        injury_fatigue_ST_debuff= - 5
        injury_fatigue_DX_debuff = - 5
        base_movement_speed=0
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
    character = apply_debuffs(character)
    print(f"Im printing AFTER returning from applying buff Active ST is{character['active_ST']}")
    # character['active_ST'] = int(character['ST']) - injury_fatigue_ST_debuff + character['debuff_ST']
    # character['active_DX'] = int(character['DX']) -injury_fatigue_DX_debuff + character['debuff_DX']
    # character['active_IN'] = int(character['IN']) + character['debuff_IN']
    # character['active_WP'] = int(character['WP']) + character['debuff_WP']
    # character['active_CH'] = int(character['CH']) + character['debuff_CH']
    # character['active_CN'] = int(character['CN']) + character['debuff_CN']

# Calculate the rest of the stats
    character['encumbrance'] = calculate_encumbrance_level(name, character['active_ST'])
    character['active_movement_speed'] = update_movement_speed(base_movement_speed, injury_fatigue_movement_debuff,int(calculate_encumbrance_penalty(character['encumbrance'])))+character["debuff_movement"]
    character['encumbrance_penalty_explained'] = explain_encumbrance_penalty(character['encumbrance'])
    character['active_movement_debuffs'] =  injury_fatigue_movement_debuff_text
    character['injury_fatigue_debuffs'] = injury_fatigue_extra_effects

#Caculate Vitality Points and Max Vitality Points
    character['max_vitality_points'] = calculate_vitality_points(character['vitality_points_dice_rolls'],
                                                                 character['level'], active_wound) + character['debuff_max_vp']
    character["active_vitality_points"] = min(active_vitality, character["max_vitality_points"])

    save_character(character)
    update_stats_modifiers(name)
    update_armor_values(name)

    return redirect(url_for('view_character', name=name))

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
        is_armor = request.form.get('is_armor') == 'on'

        ac_value = request.form.get('ac_value') if is_armor else None
        dx_modifier = request.form.get('dx_modifier') == 'on' if is_armor else None
        modifiers = request.form.get('modifiers') if is_armor else None
        conditions = request.form.get('conditions') if is_armor else None

        # Create a dictionary for the item and add it to the character's inventory
        item = {
            'item_name': item_name,
            'units': units,
            'weight_per_unit': weight_per_unit,
            'total_weight': total_weight,
            'additional_info':additional_info,
            'is_armor': is_armor,
            'ac_value':ac_value,
            'dx_modifier':dx_modifier,
            'modifiers':modifiers,
            'conditions':conditions
        }
        character['inventory'].append(item)


        # Save the character's updated data
        save_character(character)

        return redirect(url_for('show_inventory', name=name))
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
            return redirect(url_for('show_inventory', name=name))
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
            return redirect(url_for('show_inventory', name=name))
    return "Character not found", 404


@app.route('/character/<name>/inventory/pick_up', methods=['POST'])
def pickup_item(name):
    character = load_character(name)
    if character:
        item_name = request.form['item_name']
        action = request.form['action']

        if action == 'pick_up':
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
            return redirect(url_for('show_inventory', name=name))
    else:
        return "Character not found", 404

@app.route('/character/<name>/inventory/reset_on_the_ground', methods=['POST'])
def reset_on_the_ground(name):
    character = load_character(name)
    if character:
        # Clear the 'on_the_ground' list
        character['on_the_ground'] = []
        save_character(character)
        return redirect(url_for('show_inventory', name=name))
    return "Character not found", 404

@app.route('/character/<name>/toggle_shield', methods=['POST'])
def equip_shield(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404
    shield_equipped = request.form.get('shield_equipped')
    if shield_equipped:
        character['shield_equipped']= True
        total_ac = character['armor']['ac_value'] + get_modifier(character['active_DX']) + character['armor']['modifier'] + 2
        character['total_ac'] = total_ac

    else:
        character['shield_equipped'] = False
        total_ac = character['armor']['ac_value'] + get_modifier(character['active_DX']) + character['armor']['modifier']
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
@app.route("/edit_trait/<name>/<trait_id>", methods=["POST"])
def edit_trait(name, ability_id):
    character = load_character(name)
    if not character:
        return "Character not found", 404

	# TO BE IMPLEMENTED

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
    if character:
        debuff_name = request.form["debuff_name"]
        debuff_value = int(request.form["debuff_value"])
        debuff_reason = request.form["debuff_reason"]
        debuff_id = debuff_name+debuff_reason
        # Store debuff as a dictionary
        add_new_debuff(character, debuff_name, debuff_value, debuff_reason, debuff_id, True)


        save_character(character)
        update_character(name)
    return redirect(url_for("view_character", name=name))

@app.route('/character/<name>/remove_debuff/<debuff_id>', methods=['POST'])
def remove_debuff(name, debuff_id):
    character = load_character(name)
    if not character:
        return "Character not found", 404
    remove_debuff_incall(character,debuff_id)
    # apply_debuffs(character)
    save_character(character)
    update_character(name)
    return redirect(url_for("view_character", name=name))

def remove_debuff_incall(character, debuff_id):
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

    success = update_purse_function(name, amount, currency)

    if not success:
        return "Error: Not enough money!", 400  # Return error if not enough coins


    return redirect(url_for("view_character", name=name))


@app.route("/character/<name>/update_proficiency_bonus", methods=["POST"])
def update_proficiency_bonus(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404
    if character:
        for skill in character['skills']:
            character['skills'][skill]['proficiency_bonus'] = int(request.form.get(skill, 0))

    # Save the updated character data to JSON
    save_character(character)
    update_character(name)
    return redirect(url_for("view_character", name=name))

@app.route("/character/<name>/add_custom_skill", methods=["POST"])
def add_custom_skill(name):
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
        }
        print(f"Ive tried to add the skill {custom_skill_name} that uses {custom_skill_stat}")

        save_character(character)
        update_character(name)  # Ensure updates reflect

    return redirect(url_for("view_character", name=name))

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
        "uses_per_long_rest": int(request.form["ability_uses"]),
        "uses_left": int(request.form["ability_uses"]),  # Start with full uses
    }

    if "active_abilities" not in character:
        character["active_abilities"] = []

    character["active_abilities"].append(new_ability)
    save_character(character)

    return redirect(url_for("view_character", name=name))


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

def reload_abilities_on_long_rest(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404
    print('Im reloading the Active Abilities')
    for ability in character.get("active_abilities", []):

        ability["uses_left"] = ability["uses_per_long_rest"]
    save_character(character)


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

@app.route('/short_rest/<name>', methods=['POST'])
def short_rest(name):
    pass
    return redirect(url_for("view_character", name=name))

@app.route('/long_rest/<name>', methods=['POST'])
def long_rest(name):

    reload_abilities_on_long_rest(name)
    return redirect(url_for("view_character", name=name))
@app.route('/decrease_dc/<name>/<ability_id>', methods=['POST'])
def decrease_dc(name, ability_id):
    change = -1
    print(ability_id)
    modify_ability_dc(name, ability_id, change)
    return redirect(url_for("view_character", name=name))

@app.route('/increase_dc/<name>/<ability_id>', methods=['POST'])
def increase_dc(name, ability_id):
    change = 1
    modify_ability_dc(name, ability_id, change)
    print (ability_id)
    return redirect(url_for("view_character", name=name))

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
if __name__ == '__main__':
    app.run(debug=True)
