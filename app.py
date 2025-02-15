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

app = Flask(__name__)
DATA_FOLDER = 'characters'
characters = {}
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)


def save_character(character):
    filename = os.path.join(DATA_FOLDER, f"{character['name']}.json")
    with open(filename, 'w') as file:
        json.dump(character, file)
    filename = os.path.join(DATA_FOLDER, f"{character['name']}_baseline.json")
    with open(filename, 'w') as file:
        json.dump(character, file)

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
                'debuff_ST':0,
                'DX': int(request.form['DX']),
                'active_DX': int(request.form['DX']),
                'debuff_DX': 0,
                'CN': int(request.form['CN']),
                'active_CN': int(request.form['CN']),
                'debuff_CN': 0,
                'CH': int(request.form['CH']),
                'active_CH': int(request.form['CH']),
                'debuff_CH': 0,
                'IN': int(request.form['IN']),
                'active_IN': int(request.form['IN']),
                'debuff_IN': 0,
                'WP': int(request.form['WP']),
                'active_WP': int(request.form['WP']),
                'debuff_WP': 0,
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

@app.route('/character/<name>')
def view_character(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404
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
        "0": "+5 being Unencumbered",
        "1": "Normal Movement Speed",
        "2": "-10 being Lightly Encumbered",
        "3":"-15 being Mederately Encumbered",
        "4": "-20 being Heavily Encumbered",
        "5": "-100 being Extremely Encumbered",
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
    # Update the character data
    injury_fatigue_ST_debuff=0
    injury_fatigue_DX_debuff = 0
    base_movement_speed=int(character['movement_speed'])
    injury_fatigue_movement_debuff = 0
    injury_fatigue_movement_debuff_text = ""
    injury_fatigue_extra_effects=""
    if total_debuff == 0:
        injury_fatigue_movement_debuff_text ="None"
        character['injury_fatigue_debuffs']="None"

    if total_debuff == 1:
        injury_fatigue_ST_debuff= - 1
        injury_fatigue_DX_debuff = -1
        injury_fatigue_movement_debuff = -5
        injury_fatigue_movement_debuff_text = "-5ft "
        injury_fatigue_extra_effects = "Disadvantage of Physical ability checks or contests. <br>10% Chance of Spell Failure"

    if total_debuff == 2:
        injury_fatigue_ST_debuff= - 3
        injury_fatigue_DX_debuff = - 3
        injury_fatigue_movement_debuff = -10

        injury_fatigue_movement_debuff_text = "-10ft "

        injury_fatigue_extra_effects = "Disadvantage of all ability checks or contests. <br>30% Chance of Spell Failure"

    if total_debuff == 3:
        injury_fatigue_ST_debuff= - 5
        injury_fatigue_DX_debuff = - 5
        injury_fatigue_movement_debuff = -15
        injury_fatigue_movement_debuff_text ="-15ft"
        injury_fatigue_extra_effects = "Disadvantage of all ability checks or contests, attacks and saving throws. <br>50% Chance of Spell Failure"

    if total_debuff == 4:
        injury_fatigue_ST_debuff= - 5
        injury_fatigue_DX_debuff = - 5
        base_movement_speed=0
        injury_fatigue_movement_debuff_text = "Incapacitated"
        injury_fatigue_extra_effects = "Can't take actions or reactions."

    if total_debuff == 5:
        injury_fatigue_ST_debuff = - 5
        injury_fatigue_DX_debuff = - 5
        base_movement_speed = 0
        injury_fatigue_movement_debuff_text = "Incapacitated"


    if total_debuff == 6:
        character['active_ST'] = int(character['ST']) - 5
        injury_fatigue_DX_debuff = - 5
        base_movement_speed = 0
        injury_fatigue_movement_debuff_text = "Dead"

    character['active_ST'] = int(character['ST']) - injury_fatigue_ST_debuff + character['debuff_ST']
    character['active_DX'] = int(character['DX']) -injury_fatigue_DX_debuff + character['debuff_DX']
    character['active_IN'] = int(character['IN']) + character['debuff_IN']
    character['active_WP'] = int(character['WP']) + character['debuff_WP']
    character['active_CH'] = int(character['CH']) + character['debuff_CH']
    character['active_CN'] = int(character['CN']) + character['debuff_CN']

    character['encumbrance'] = calculate_encumbrance_level(name, character['active_ST'])
    character['active_movement_speed'] = update_movement_speed(base_movement_speed, injury_fatigue_movement_debuff,int(calculate_encumbrance_penalty(character['encumbrance'])))+character["debuff_movement"]
    character['encumbrance_penalty_explained'] = explain_encumbrance_penalty(character['encumbrance'])
    character['active_movement_debuffs'] =  injury_fatigue_movement_debuff_text
    character['injury_fatigue_debuffs'] = injury_fatigue_extra_effects
    character['active_vitality_points'] = active_vitality



    character['max_vitality_points'] = calculate_vitality_points(character['vitality_points_dice_rolls'],
                                                                 character['level'], active_wound) + character['debuff_max_vp']
    character["active_vitality_points"] = min(character["active_vitality_points"], character["max_vitality_points"])


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


@app.route('/character/<name>/add_trait', methods=['POST'])
def add_trait(name):
    # Your logic to add a trait
    pass

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

@app.route('/character/<name>/add_active_ability', methods=['POST'])
def add_active_ability(name):
    # Your logic to add an active ability
    pass

@app.route('/character/<name>/add_debuff', methods=['POST'])
def add_debuff(name):
    character = load_character(name)
    if not character:
        return "Character not found", 404
    if character:
        debuff_name = request.form["debuff_name"]
        debuff_value = int(request.form["debuff_value"])
        debuff_reason = request.form["debuff_reason"]

        # Store debuff as a dictionary
        character["debuffs"].append({"name": debuff_name, "value": debuff_value, "reason":debuff_reason})

        # Appply debuff
        if debuff_name == "debuff_st":
            character["debuff_ST"]+= debuff_value
        if debuff_name == "debuff_dx":
            character["debuff_DX"]+= debuff_value
        if debuff_name == "debuff_cn":
            character["debuff_CN"]+= debuff_value
        if debuff_name == "debuff_ch":
            character["debuff_CH"]+= debuff_value
        if debuff_name == "debuff_in":
            character["debuff_IN"]+= debuff_value
        if debuff_name == "debuff_wp":
            character["debuff_WP"]+= debuff_value
        if debuff_name == "debuff_movement":
            character["debuff_movement"]+= debuff_value
        if debuff_name == "debuff_height":
            character["debuff_height"]+= debuff_value
        if debuff_name == "debuff_max_vp":

            character["debuff_max_vp"]+= debuff_value
        if debuff_name == "debuff_max_wp":
            character['max_wound_points'] += debuff_value

        save_character(character)
        update_character(name)
    return redirect(url_for("view_character", name=name))

@app.route('/character/<name>/remove_debuff/<debuff_name>', methods=['POST'])
def remove_debuff(name, debuff_name):
    character = load_character(name)
    if not character:
        return "Character not found", 404

    # Find the debuff entry in the list
    debuff_to_remove = next((debuff for debuff in character["debuffs"] if debuff["name"] == debuff_name), None)

    if debuff_to_remove:
        debuff_value = debuff_to_remove["value"]  # Store the debuff value before removal
        character["debuffs"].remove(debuff_to_remove)  # Remove the debuff entry

        # Withdraw the debuff value from the affected stat
        if debuff_name == "debuff_st":
            character["debuff_ST"] -= debuff_value
        elif debuff_name == "debuff_dx":
            character["debuff_DX"] -= debuff_value
        elif debuff_name == "debuff_cn":
            character["debuff_CN"] -= debuff_value
        elif debuff_name == "debuff_ch":
            character["debuff_CH"] -= debuff_value
        elif debuff_name == "debuff_in":
            character["debuff_IN"] -= debuff_value
        elif debuff_name == "debuff_wp":
            character["debuff_WP"] -= debuff_value
        elif debuff_name == "debuff_movement":
            character["debuff_movement"] -= debuff_value
        elif debuff_name == "debuff_height":
            character["debuff_height"] -= debuff_value

        elif debuff_name == "debuff_max_wp":
            character['max_wound_points'] -= debuff_value
        elif debuff_name == "debuff_max_vp":
            character["debuff_max_vp"] -= debuff_value
        # Ensure no stat goes below its original value
        character["debuff_ST"] = max(character["debuff_ST"], 0)
        character["debuff_DX"] = max(character["debuff_DX"], 0)
        character["debuff_CN"] = max(character["debuff_CN"], 0)
        character["debuff_CH"] = max(character["debuff_CH"], 0)
        character["debuff_IN"] = max(character["debuff_IN"], 0)
        character["debuff_WP"] = max(character["debuff_WP"], 0)


        save_character(character)
        update_character(name)

    return redirect(url_for("view_character", name=name))

if __name__ == '__main__':
    app.run(debug=True)
