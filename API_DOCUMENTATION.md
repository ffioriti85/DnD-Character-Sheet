# API Documentation

This document provides comprehensive documentation for all routes and endpoints in the D&D Character Sheet Application.

## 🔗 Base URL

- **Development**: `http://localhost:5000`
- **Production**: `https://your-domain.com`

## 📋 Authentication

The application uses session-based authentication. No API keys are required for basic functionality.

## 🎭 Character Management Routes

### Create Character

#### `POST /create/<name>`
Creates a new character with the specified name.

**Parameters:**
- `name` (path): Character name
- `race` (form): Character race
- `height` (form): Character height in feet
- `weight` (form): Character weight
- `movement_speed` (form): Base movement speed
- `ST`, `DX`, `CN`, `CH`, `IN`, `WP` (form): Ability scores
- `vitality_points` (form): Comma-separated VP dice rolls
- `wound_points` (form): Maximum wound points
- `hit_dice` (form): Character hit dice

**Response:** Redirects to character creation part 2

---

#### `POST /finish_creation/<name>`
Completes character creation and redirects to character view.

**Parameters:**
- `name` (path): Character name

**Response:** Redirects to character view

---

### View Character

#### `GET /character/<name>`
Displays the character sheet for the specified character.

**Parameters:**
- `name` (path): Character name
- `view` (query): View mode ('mobile' or 'desktop')

**Response:** Renders character sheet template

---

### Update Character

#### `POST /character/<name>/update`
Updates character stats and recalculates derived values.

**Parameters:**
- `name` (path): Character name
- Various form fields for stat updates

**Response:** Redirects to updated character view

---

#### `POST /character/<name>/level_up`
Handles character level up with new hit dice and wound points.

**Parameters:**
- `name` (path): Character name
- `hit_dice_roll` (form): New hit dice roll
- `increase_wound_points` (form): Additional wound points

**Response:** Redirects to level up confirmation

---

#### `POST /confirm_level_up/<name>`
Confirms level up and adds new vitality points.

**Parameters:**
- `name` (path): Character name
- `vp_roll` (form): New VP dice roll
- `wp` (form): Additional wound points

**Response:** Redirects to character view

---

## 🎒 Inventory Management Routes

### Add Item

#### `POST /character/<name>/inventory/add_item`
Adds a new item to the character's inventory.

**Parameters:**
- `name` (path): Character name
- `item_name` (form): Name of the item
- `units` (form): Number of units
- `weight_per_unit` (form): Weight per unit
- `additional_info` (form): Additional item information
- `is_container` (form): Whether item is a container
- `container_capacity` (form): Container weight capacity
- `weight_reduction` (form): Weight reduction percentage
- `is_armor` (form): Whether item is armor
- `ac_value` (form): Armor class value
- `dx_modifier` (form): Whether armor allows DX modifier
- `is_weapon` (form): Whether item is a weapon
- `damage_dice` (form): Weapon damage dice
- `weapon_stat_modifier` (form): Weapon stat modifier

**Response:** Redirects to character view

---

### Unit Management

#### `POST /character/<name>/inventory/add_unit`
Adds one unit to an existing item.

**Parameters:**
- `name` (path): Character name
- `item_name` (form): Name of the item

**Response:** Redirects to character view

---

#### `POST /character/<name>/inventory/remove_unit`
Removes one unit from an existing item. Removes item entirely if units reach 0.

**Parameters:**
- `name` (path): Character name
- `item_name` (form): Name of the item

**Response:** Redirects to character view

---

### Item Actions

#### `POST /character/<name>/inventory/drop_item`
Drops an item from inventory to the ground.

**Parameters:**
- `name` (path): Character name
- `item_name` (form): Name of the item

**Response:** Redirects to character view

---

#### `POST /character/<name>/inventory/store_item`
Stores an item from inventory to home storage.

**Parameters:**
- `name` (path): Character name
- `item_name` (form): Name of the item

**Response:** Redirects to character view

---

#### `POST /character/<name>/inventory/pick_up`
Picks up an item from ground or home storage.

**Parameters:**
- `name` (path): Character name
- `item_name` (form): Name of the item

**Response:** Redirects to character view

---

### Container Management

#### `POST /character/<name>/inventory/move_to_container`
Moves an item into a container.

**Parameters:**
- `name` (path): Character name
- `item_name` (form): Name of the item to move
- `container_name` (form): Name of the container

**Response:** Redirects to character view

---

#### `POST /character/<name>/inventory/remove_from_container`
Removes an item from a container back to inventory.

**Parameters:**
- `name` (path): Character name
- `item_name` (form): Name of the item to remove
- `container_name` (form): Name of the container

**Response:** Redirects to character view

---

### Storage Management

#### `POST /character/<name>/inventory/reset_on_the_ground`
Clears all items from ground storage.

**Parameters:**
- `name` (path): Character name

**Response:** Redirects to character view

---

#### `POST /character/<name>/inventory/reset_home_storage`
Clears all items from home storage.

**Parameters:**
- `name` (path): Character name

**Response:** Redirects to character view

---

## ⚔️ Equipment Routes

### Armor Management

#### `POST /character/<name>/equip_armor`
Equips armor from inventory.

**Parameters:**
- `name` (path): Character name
- `selected_armor` (form): Name of armor to equip

**Response:** Redirects to character view

---

#### `POST /character/<name>/toggle_shield`
Toggles shield equipped status.

**Parameters:**
- `name` (path): Character name
- `shield_equipped` (form): Whether shield is equipped

**Response:** Redirects to character view

---

#### `POST /character/<name>/update_temporary_armor_modifier`
Updates temporary armor modifier.

**Parameters:**
- `name` (path): Character name
- `temporary_armor_modifier` (form): Temporary modifier value

**Response:** Redirects to character view

---

### Weapon Management

#### `POST /character/<name>/equip_weapon`
Equips weapon from inventory.

**Parameters:**
- `name` (path): Character name
- `selected_weapon` (form): Name of weapon to equip

**Response:** Redirects to character view

---

#### `POST /character/<name>/apply_weapon_proficiency`
Applies weapon proficiency to equipped weapon.

**Parameters:**
- `name` (path): Character name
- `selected_weapon_proficiency` (form): Proficiency skill name

**Response:** Redirects to character view

---

## 🎯 Skills and Abilities Routes

### Skill Management

#### `POST /character/<name>/add_custom_skill`
Adds a custom skill to the character.

**Parameters:**
- `name` (path): Character name
- `custom_skill_name` (form): Name of the skill

**Response:** Redirects to character view

---

#### `POST /character/<name>/add_custom_skill_from_creation`
Adds a custom skill during character creation.

**Parameters:**
- `name` (path): Character name
- `custom_skill_name` (form): Name of the skill
- `custom_skill_stat` (form): Associated ability score

**Response:** Renders character creation part 2

---

#### `POST /character/<name>/remove_skill`
Removes a skill from the character.

**Parameters:**
- `name` (path): Character name
- `skill_to_remove` (form): Name of the skill to remove

**Response:** Redirects to character view

---

#### `POST /character/<name>/update_proficiency_bonus`
Updates proficiency bonus for all skills.

**Parameters:**
- `name` (path): Character name

**Response:** Redirects to character view

---

### Trait Management

#### `POST /add_trait/<name>`
Adds a trait to the character.

**Parameters:**
- `name` (path): Character name
- `trait_name` (form): Name of the trait
- `trait_description` (form): Description of the trait

**Response:** Redirects to character view

---

#### `POST /add_trait_from_creation/<name>`
Adds a trait during character creation.

**Parameters:**
- `name` (path): Character name
- `trait_name` (form): Name of the trait
- `trait_description` (form): Description of the trait

**Response:** Renders character creation part 2

---

#### `POST /edit_trait/<name>/<trait_id>`
Updates an existing trait.

**Parameters:**
- `name` (path): Character name
- `trait_id` (path): ID of the trait
- `trait_name` (form): New name of the trait
- `trait_description` (form): New description of the trait

**Response:** Redirects to character view

---

#### `POST /remove_trait/<name>/<trait_id>`
Removes a trait from the character.

**Parameters:**
- `name` (path): Character name
- `trait_id` (path): ID of the trait

**Response:** Redirects to character view

---

### Ability Management

#### `POST /add_active_ability/<name>`
Adds an active ability to the character.

**Parameters:**
- `name` (path): Character name
- `ability_name` (form): Name of the ability
- `ability_description` (form): Description of the ability
- `ability_dc` (form): Difficulty class
- `rest_type` (form): Rest type for recharging
- `ability_uses` (form): Number of uses per rest

**Response:** Redirects to character view

---

#### `POST /add_active_ability_from_creation/<name>`
Adds an active ability during character creation.

**Parameters:**
- `name` (path): Character name
- `ability_name` (form): Name of the ability
- `ability_description` (form): Description of the ability
- `ability_dc` (form): Difficulty class
- `ability_uses` (form): Number of uses per rest

**Response:** Renders character creation part 2

---

#### `POST /use_ability/<name>/<ability_id>`
Uses an active ability, reducing its uses.

**Parameters:**
- `name` (path): Character name
- `ability_id` (path): ID of the ability

**Response:** Redirects to character view

---

#### `POST /remove_active_ability/<name>/<ability_id>`
Removes an active ability from the character.

**Parameters:**
- `name` (path): Character name
- `ability_id` (path): ID of the ability

**Response:** Redirects to character view

---

#### `POST /change_dc/<name>/<ability_id>/<int:change>`
Changes the DC of an ability.

**Parameters:**
- `name` (path): Character name
- `ability_id` (path): ID of the ability
- `change` (path): Amount to change DC by

**Response:** Redirects to character view

---

#### `POST /decrease_dc/<name>/<ability_id>`
Decreases the DC of an ability by 1.

**Parameters:**
- `name` (path): Character name
- `ability_id` (path): ID of the ability

**Response:** Redirects to character view

---

#### `POST /increase_dc/<name>/<ability_id>`
Increases the DC of an ability by 1.

**Parameters:**
- `name` (path): Character name
- `ability_id` (path): ID of the ability

**Response:** Redirects to character view

---

## 💰 Currency Management Routes

#### `POST /character/<name>/`
Updates character's currency.

**Parameters:**
- `name` (path): Character name
- `amount` (form): Amount to add/subtract
- `currency` (form): Type of currency (gold, silver, copper)
- `operation` (form): Operation type (add or subtract)

**Response:** Redirects to character view

---

## 🏥 Rest and Recovery Routes

#### `POST /short_rest/<name>`
Performs a short rest, healing VP and recharging abilities.

**Parameters:**
- `name` (path): Character name
- `hit_dice_roll` (form): Hit dice roll for healing

**Response:** Redirects to character view

---

#### `POST /long_rest/<name>`
Performs a long rest, fully healing VP and recharging all abilities.

**Parameters:**
- `name` (path): Character name

**Response:** Redirects to character view

---

## 📝 Notes Management Routes

#### `POST /character/<name>/add_note`
Adds a new note to the character.

**Parameters:**
- `name` (path): Character name
- `note_content` (form): Content of the note

**Response:** Redirects to character view

---

#### `POST /character/<name>/edit_note`
Edits an existing note.

**Parameters:**
- `name` (path): Character name
- `note_id` (form): ID of the note
- `note_content` (form): New content of the note

**Response:** Redirects to character view

---

#### `POST /character/<name>/delete_note/<note_id>`
Deletes a note from the character.

**Parameters:**
- `name` (path): Character name
- `note_id` (path): ID of the note

**Response:** Redirects to character view

---

## 🎭 Debuff Management Routes

#### `POST /character/<name>/add_debuff`
Adds a debuff or buff to the character.

**Parameters:**
- `name` (path): Character name
- `debuff_name` (form): Name of the debuff/buff
- `debuff_value` (form): Value of the debuff/buff
- `debuff_reason` (form): Reason for the debuff/buff
- `operation` (form): Operation type (buff or debuff)

**Response:** Redirects to character view

---

#### `POST /character/<name>/remove_debuff/<debuff_id>`
Removes a debuff from the character.

**Parameters:**
- `name` (path): Character name
- `debuff_id` (path): ID of the debuff

**Response:** Redirects to character view

---

## 🎓 Proficiency Management Routes

#### `POST /character/<name>/delete_proficiency`
Deletes a proficiency from the character.

**Parameters:**
- `name` (path): Character name
- `proficiency_index` (JSON): Index of the proficiency to delete

**Response:** JSON response with success message

---

#### `POST /character/<name>/update_proficiency`
Updates a proficiency's name and description.

**Parameters:**
- `name` (path): Character name
- `proficiency_index` (JSON): Index of the proficiency to update
- `new_name` (JSON): New name for the proficiency
- `new_description` (JSON): New description for the proficiency

**Response:** JSON response with success message

---

#### `POST /character/<name>/increase_proficiency/<proficiency_id>`
Increases a proficiency bonus by 1.

**Parameters:**
- `name` (path): Character name
- `proficiency_id` (path): ID of the proficiency

**Response:** Redirects to character view

---

#### `POST /character/<name>/decrease_proficiency/<proficiency_id>`
Decreases a proficiency bonus by 1.

**Parameters:**
- `name` (path): Character name
- `proficiency_id` (path): ID of the proficiency

**Response:** Redirects to character view

---

## 🔄 Utility Routes

#### `GET /`
Main page for character selection and creation.

**Response:** Renders main page template

---

#### `GET /gm_cheatsheet`
GM cheatsheet page (requires GM password).

**Response:** Renders GM cheatsheet template

---

#### `POST /delete_character/<name>`
Deletes a character.

**Parameters:**
- `name` (path): Character name

**Response:** Redirects to main page

---

#### `GET /api/character/<name>/stats`
API endpoint for character stats.

**Parameters:**
- `name` (path): Character name

**Response:** JSON with character stats

---

## 📊 Response Formats

### HTML Responses
Most routes return HTML responses by rendering templates or redirecting to other pages.

### JSON Responses
Some API endpoints return JSON responses:

```json
{
    "message": "Success message",
    "status": "success"
}
```

### Redirect Responses
Many routes redirect to the character view after completing operations:

```
302 Found
Location: /character/<name>
```

## 🚨 Error Handling

### 404 Errors
- Character not found
- Item not found in inventory
- Invalid route

### 500 Errors
- Server-side processing errors
- Invalid data format
- Database/file system errors

### Validation Errors
- Invalid form data
- Missing required fields
- Invalid numeric values

## 🔒 Security Considerations

- Session-based authentication
- Input validation on all forms
- CSRF protection (built into Flask)
- No sensitive data exposure in URLs
- Secure file handling for character data

## 📱 Mobile Considerations

- Responsive design for all routes
- Touch-friendly form controls
- Mobile-optimized layouts
- View mode detection and switching

---

**Note**: This API documentation covers all current routes in the application. For the most up-to-date information, please refer to the source code in `app.py`. 