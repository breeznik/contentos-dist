"""Schema validation for ContentOS data files."""
from typing import Dict, List, Optional, Tuple

# kit.yaml schema definition
KIT_SCHEMA = {
    'required': ['id', 'name', 'status', 'created'],
    'optional': ['video_id', 'video_id_short', 'published_at'],
    'ingredients': {
        'valid_themes': ['loop', 'cinematic', 'home_video', 'cinematic_realistic'],
        'valid_hooks': ['POV_Emotional', 'Question', 'Statement', 'Curiosity', 'Shock'],
        'valid_audio': ['Ambient_Silence', 'Music_Tense', 'Music_Calm', 'ASMR', 'Voiceover'],
        'valid_visual': ['Macro_Closeup', 'Wide_Shot', 'POV_Shot', 'Slow_Motion'],
        'valid_physics': ['Organic_Motion', 'Rigid_Body', 'Fluid', 'None'],
        'valid_formulas': ['stitch_2clip', 'loop_circular', 'loop_boomerang', 'cinematic_4shot', 'fpp_narrative']
    },
    'valid_statuses': ['draft', 'setup', 'pending', 'published', 'archived']
}


def validate_kit_yaml(data: Dict) -> Tuple[bool, List[str]]:
    """Validate a kit.yaml dictionary against schema.
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    if not isinstance(data, dict):
        return False, ["kit.yaml must be a dictionary"]
    
    # Check required fields
    for field in KIT_SCHEMA['required']:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Validate status
    status = data.get('status')
    if status and status not in KIT_SCHEMA['valid_statuses']:
        errors.append(f"Invalid status '{status}'. Valid: {KIT_SCHEMA['valid_statuses']}")
    
    # Validate ingredients
    ingredients = data.get('ingredients', {})
    if ingredients:
        theme = ingredients.get('theme')
        if theme and theme not in KIT_SCHEMA['ingredients']['valid_themes']:
            errors.append(f"Invalid theme '{theme}'. Valid: {KIT_SCHEMA['ingredients']['valid_themes']}")
        
        hook = ingredients.get('hook_type')
        if hook and hook not in KIT_SCHEMA['ingredients']['valid_hooks']:
            errors.append(f"Invalid hook_type '{hook}'. Valid: {KIT_SCHEMA['ingredients']['valid_hooks']}")
        
        formula = ingredients.get('formula')
        if formula and formula not in KIT_SCHEMA['ingredients']['valid_formulas']:
            errors.append(f"Invalid formula '{formula}'. Valid: {KIT_SCHEMA['ingredients']['valid_formulas']}")
    
    return len(errors) == 0, errors


def validate_kit_file(yaml_path) -> Tuple[bool, List[str]]:
    """Validate a kit.yaml file from path."""
    import yaml
    
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        return validate_kit_yaml(data)
    except Exception as e:
        return False, [f"Failed to read {yaml_path}: {str(e)}"]
