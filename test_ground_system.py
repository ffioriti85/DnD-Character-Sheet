import unittest
import os
import json
import shutil
from app import app

class TestGroundSystem(unittest.TestCase):
    
    def setUp(self):
        # Configure app for testing
        app.config['TESTING'] = True
        self.client = app.test_client()
        
        # Create test storage directory
        if not os.path.exists('storage'):
            os.makedirs('storage')
        
        # Initialize empty ground items
        self.init_empty_ground()
        
        # Create test character
        self.create_test_character()
    
    def tearDown(self):
        # Clean up test files
        if os.path.exists('characters/TestChar.json'):
            os.remove('characters/TestChar.json')
        
        # Clean up storage directory
        if os.path.exists('storage/OnTheGround.json'):
            os.remove('storage/OnTheGround.json')
    
    def init_empty_ground(self):
        # Create empty ground storage
        with open('storage/OnTheGround.json', 'w') as f:
            json.dump([], f)
    
    def create_test_character(self):
        # Create a basic test character with inventory
        test_char = {
            "name": "TestChar",
            "level": 1,
            "race": "Human",
            "ST": 10,
            "DX": 10, 
            "CN": 10,
            "CH": 10,
            "IN": 10,
            "WP": 10,
            "active_vitality_points": 10,
            "vitality_points": 10,
            "max_vitality_points": 10,
            "wound_points": 5,
            "active_wound_points": 5,
            "max_wound_points": 5,
            "active_ST": 10,
            "active_DX": 10,
            "active_CN": 10,
            "active_CH": 10,
            "active_IN": 10,
            "active_WP": 10,
            "ST_modifier": 0,
            "DX_modifier": 0,
            "CN_modifier": 0,
            "CH_modifier": 0,
            "IN_modifier": 0,
            "WP_modifier": 0,
            "vitality_points_dice_rolls": ["6"],
            "injury_fatigue": 0,
            "exhaustion": 0,
            "extra_injury_fatigue": 0,
            "encumbrance": 0,
            "debuff_max_vp": 0,
            "debuff_max_wp": 0,
            "debuff_DX": 0,
            "debuff_ST": 0,
            "debuff_CN": 0,
            "debuff_CH": 0,
            "debuff_IN": 0,
            "debuff_WP": 0,
            "debuff_height": 0,
            "debuff_movement": 0,
            "movement_speed": "30",
            "height": "6",
            "weight": "180",
            "powerful_build": False,
            "is_inspired": False,
            "active_movement_debuffs": "None",
            "active_movement_speed": 30,
            "temp_armor_modifier": 0,
            "ac_buff": 0,
            "armor": {
                "name": "None",
                "ac_value": 10,
                "dx_modifier": True,
                "modifiers": 0,
                "conditions": ""
            },
            "shield_equipped": False,
            "weapon": {
                "name": "None",
                "damage_dice": "1",
                "weapon_stat_modifier": "Strength",
                "weapon_modifiers": 0
            },
            "skills": {},
            "inventory": [
                {
                    "item_name": "Test Sword",
                    "units": 1,
                    "weight_per_unit": 3.0,
                    "total_weight": 3.0,
                    "additional_info": "A test sword"
                }
            ],
            "on_the_ground": [],
            "house_inventory": []
        }
        
        with open('characters/TestChar.json', 'w') as f:
            json.dump(test_char, f)
    
    def test_drop_item_to_ground(self):
        # Test dropping an item adds it to global ground storage
        response = self.client.post('/character/TestChar/inventory/drop_item', 
                                    data={'item_name': 'Test Sword'}, 
                                    follow_redirects=True)
        
        # Verify character inventory is empty
        with open('characters/TestChar.json', 'r') as f:
            character = json.load(f)
            self.assertEqual(len(character['inventory']), 0)
        
        # Verify item was added to global ground
        with open('storage/OnTheGround.json', 'r') as f:
            ground_items = json.load(f)
            self.assertEqual(len(ground_items), 1)
            self.assertEqual(ground_items[0]['item_name'], 'Test Sword')
    
    def test_pickup_item_from_ground(self):
        # First drop an item
        self.client.post('/character/TestChar/inventory/drop_item', 
                         data={'item_name': 'Test Sword'}, 
                         follow_redirects=True)
        
        # Then pick it up
        response = self.client.post('/character/TestChar/inventory/pick_up', 
                                    data={'item_name': 'Test Sword'}, 
                                    follow_redirects=True)
        
        # Verify item was moved back to character inventory
        with open('characters/TestChar.json', 'r') as f:
            character = json.load(f)
            self.assertEqual(len(character['inventory']), 1)
            self.assertEqual(character['inventory'][0]['item_name'], 'Test Sword')
        
        # Verify ground is empty
        with open('storage/OnTheGround.json', 'r') as f:
            ground_items = json.load(f)
            self.assertEqual(len(ground_items), 0)
    
    def test_reset_ground_items(self):
        # First drop an item
        self.client.post('/character/TestChar/inventory/drop_item', 
                         data={'item_name': 'Test Sword'}, 
                         follow_redirects=True)
        
        # Then reset ground items
        response = self.client.post('/character/TestChar/inventory/reset_on_the_ground', 
                                    follow_redirects=True)
        
        # Verify ground is empty
        with open('storage/OnTheGround.json', 'r') as f:
            ground_items = json.load(f)
            self.assertEqual(len(ground_items), 0)

if __name__ == '__main__':
    unittest.main() 