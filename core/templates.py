"""Templates for production kit creation."""
from pathlib import Path

SCRIPT_TEMPLATES = {
    'loop': """[SCRIPT]
Watch this until the end... The process is continuous. Every time it melts, it reforms. The cycle never breaks, just like your attention span. So watch this until the end...

[METADATA]
TITLE: {name} Loop 🔁 #shorts
DESCRIPTION: Satisfying loop for your brain.
#satisfying #loop #relaxing
""",
    'cinematic': """[VOICEOVER SCRIPT - TTS READY]
(Raw text for TTS Engine - Neutral/Deep Voice)

[COLD OPEN]
"Narrative hook goes here..."

[BODY]
"Context and build up..."

[CLIMAX]
"The payoff line."
""",
    'voxel': """# {name} Voxel Horror Script

## [ESTABLISHING - 0:00-0:04]
Peaceful voxel scene. Everything seems normal.

## [ANOMALY - 0:04-0:12]
Something is wrong. Subtle shift.

## [HORROR REVEAL - 0:12-0:16]
Full reveal of the anomaly.

## [AUDIO DIRECTION]
🔊 Silence -> Ambient dread -> Sudden horror sting
"""
}

FORMULAS = {
    'stitch_2clip': {
        'dirs': ['forward', 'reverse'],
        'slots': [
            'forward/start_frame.png', 'forward/end_frame.png',
            'reverse/start_frame.png', 'reverse/end_frame.png'
        ],
        'prompt_prefix': 'stich'
    },
    'loop_circular': {
        'dirs': ['loop_source'],
        'slots': ['loop_source/start_frame.png', 'loop_source/end_frame.png'],
        'prompt_prefix': 'circular'
    },
    'loop_boomerang': {
        'dirs': ['boomerang_source'],
        'slots': ['boomerang_source/start_frame.png'],
        'prompt_prefix': 'boomerang'
    },
    'fpp_narrative': {
        'dirs': ['assets'],
        'slots': [
            'assets/clip_01.png', 'assets/clip_02.png', 'assets/clip_03.png', 
            'assets/clip_04.png', 'assets/clip_05.png', 'assets/clip_06.png',
            'assets/clip_07.png', 'assets/clip_08.png'
        ],
        'prompt_prefix': 'fpp_universal'
    },
    'fpp_short': {
        'dirs': ['assets'],
        'slots': [
            'assets/clip_01.png', 'assets/clip_02.png', 'assets/clip_03.png'
        ],
        'prompt_prefix': 'fpp_short'
    },
    'cinematic_4shot': {
        'dirs': ['shot1_overhead', 'shot2_action', 'shot3_macro', 'shot4_reveal'],
        'slots': [
            'shot1_overhead/start_frame.png',
            'shot2_action/start_frame.png', 'shot2_action/end_frame.png',
            'shot3_macro/start_frame.png',
            'shot4_reveal/start_frame.png', 'shot4_reveal/end_frame.png'
        ],
        'prompt_prefix': 'cinematic_montage'
    }
}

PROMPT_TEMPLATES = {
    'loop': {
        'stich': """## Forward (0s -> 8s)
Cinematic macro shot, 8K resolution.
{name} in pristine starting state.
CONTINUOUS TRANSFORMATION toward peak state.
ANTI-AI REALISM: Natural micro-imperfections, organic motion blur.
NO fades. NO dissolves. Pure physics simulation.

## Reverse (8s -> 0s)
Same shot in reverse. Peak state returning to original.
Maintain exact framing and lighting.
""",
        'circular': """## Circular Loop (Single Clip)
Subject: {name}
Action: Continuous cyclical motion.
Camera: STATIC.
Condition: Start Frame MUST match End Frame EXACTLY.
Motion: Fluid, seamless transition.
""",
        'boomerang': """(BOOMERANG LOOP — PHYSICALLY REVERSIBLE)

[SETUP]
Start Image: start_frame.png ({name} Pristine)
Loop Type: Seamless Boomerang (End → Start → End)

[STYLE]
Cinematic macro shot, 8k resolution, {name},
black mirror surface, extreme contrast, strong refraction and caustics,
wet liquid-metal texture.

[ANTI-AI REALISM]
Subtle 16mm film grain (looped, fixed seed),
gentle handheld camera breathing (sinusoidal, perfectly looped),
light atmospheric haze, surface imperfections,
chromatic aberration, natural weight and momentum.

[ACTION]
CONTINUOUS PHYSICAL TRANSFORM — NO FADE, NO DISSOLVE.
The {name} melts/transforms like ice on a hot surface.
Rigid structures soften, liquefy, and flow.
The structure collapses into a splashing pool via viscous fluid dynamics, not a video transition.
The motion then reverses using the same physical simulation.

[PHYSICS]
Time-reversible simulation.
Hard-to-liquid phase change with controlled viscosity.
Gravity, splashing, surface tension, and momentum preserved.
No secondary splashes near loop boundary.
No volume loss or gain across the loop.

[CAMERA]
Stationary macro lens.
Subtle breathing motion using a looped sine curve.
No camera cuts or reframing.

[LOOP CONSTRAINT]
Final frame must be physically and visually identical to the first frame.
Lighting, grain, camera noise, and geometry must match exactly.
Designed for seamless infinite boomerang playback with no temporal seams.
""",
        'cinematic_montage': """(CINEMATIC MONTAGE — 4 SHOT SEQUENCE)

[STYLE]
Masterchef Aesthetic. High Contrast. 8K.
Lighting: Rembrandt Key Light + Rim Light on textures.

[SHOT 1: OVERHEAD ESTABLISH] (Single Image)
Subject: {name} Ingredients / Setup.
Action: Slow Pan (Left to Right).
Focus: Organized chaos, mise-en-place.

[SHOT 2: THE ACTION] (Start -> End)
Subject: The main cooking process (Searing, Pouring, Mixing).
Start Frame: Raw/Unmixed state.
End Frame: Cooked/Mixed state.
Action: High-Speed Sizzle / Splash / Transformation.
Note: Ensure continuity of lighting between frames.

[SHOT 3: MACRO TEXTURE] (Single Image)
Subject: Extreme close-up of the "Money Detail" (Crust, Bubble, Drip).
Action: Subtle breathing zoom or focus pull.
Focus: Texture MUST be tangible (Steam, Gloss, Crunch).

[SHOT 4: THE REVEAL] (Start -> End)
Subject: Plated Dish / Cross-Section.
Start Frame: Whole Dish.
End Frame: Cut open / Bite taken.
Action: Knife slice or Fork lift reveal.
"""
    },
    'cinematic': {
        'stich': """## Cinematic Sequence (16s)
Epic wide establishing shot, cinematic color grading.
{name} as the central subject.
Dramatic lighting shifts throughout.
ANTI-AI REALISM: Film grain, lens breathing, natural color science.
Camera: Slow dolly forward with subtle parallax.
""",
        'circular': """## Cinematic Loop (Single Clip)
Subject: {name}
Action: Subtle environmental motion (wind, light, flow).
Camera: STATIC.
Start/End: Seamless match.
""",
        'boomerang': """## Cinematic Boomerang
Subject: {name}
Action: Dramatic slow-motion reveal.
""",
        'cinematic_montage': """(CINEMATIC MONTAGE — 4 SHOT SEQUENCE)
[SYSTEM: VEO-3 OPTIMIZED | PHYSICS-FIRST | TEMPORAL-LOCKED]

[GLOBAL STABILITY DIRECTIVE]
Prioritize temporal coherence. Subject scale and lighting LOCKED.

[SHOT 1: OVERHEAD ESTABLISH] (VIDEO GENERATION)
INPUT: Start Frame (shot1_overhead/start_frame.png)
SUBJECT: {name} Setup / Ingredients.
CAMERA: Slow Linear Truck Right (10% speed). No rotation.
PHYSICS: Static scene. Dust motes only.
AUDIO TEXTURE: Ambient room tone, specific prop sounds (e.g. rustling).
NEGATIVE: Shifting textures, moving objects.

[SHOT 2: THE ACTION] (VIDEO GENERATION)
INPUT: Start Frame (shot2_action/start_frame.png)
SUBJECT: {name} Process (The Cut / The Pour).
ACTION PHYSICS: High Viscosity / Brittle Fracture.
LIGHTING: Backlit for Translucency/SSS.
CAMERA: 100mm Macro. Lock focus on action point.
AUDIO TEXTURE: Wet squelch, sizzling, or sharp cutting sound (High Fidelity).
NEGATIVE: Watery liquid, morphing tools.

[SHOT 3: MACRO TEXTURE] (VIDEO GENERATION)
INPUT: Start Frame (shot3_macro/start_frame.png)
SUBJECT: Extreme Close-up "Money Shot".
ACTION: Rack Focus (Background -> Foreground) OR Slow Drip.
PHYSICS: Surface Tension dominant. Micro-bubbles.
AUDIO TEXTURE: Bubble popping, liquid stretching, low frequency hum.
NEGATIVE: Anti-gravity, rapid movement.

[SHOT 4: THE REVEAL] (VIDEO GENERATION)
INPUT: Start Frame (shot4_reveal/start_frame.png)
SUBJECT: {name} Final Plating / Cross-Section.
CAMERA: Slow Turntable Rotation (15 deg/sec).
PHYSICS: Thermal melting or steam rising.
AUDIO TEXTURE: Steam hiss, crunch, appetizing mouthfeel sounds.
NEGATIVE: Distortion, texture swimming.
""",
        'fpp_universal': """# FPP NARRATIVE — 8 CLIP SEQUENCE
# Each clip below is SELF-CONTAINED for individual Veo generation.
# Copy the content inside each PROMPT block directly to Veo.

Concept: Linear First Person Narrative of {name}.

---

## CLIP 1: THE APPROACH
Source: assets/clip_01.png

### PROMPT (Copy to Veo)
```
First-person POV, 35mm lens, shallow depth of field f/2.0, 9:16 vertical, 24fps, cinematic color grade.

VISUAL: Hands visible, moving towards destination. Establishing shot. Background heavily blurred (bokeh).

CAMERA: Gimbal-stabilized slow walk. Center-weighted sharpness, peripheral blur. Visible hands throughout.

LIGHTING: Diegetic sources only. NO studio lighting.

ANTI-ARTIFACT: NO texture morphing. Geometry LOCKED. Maintain hand position. NO face reveals.

AUDIO: [MUSIC] Low sub-bass drone + [AMBIENT] Environment hum + [SFX] Footsteps + [VOICE] Heavy breathing + [NARRATOR] Opening line.
```

---

## CLIP 2: THE ENTRY
Source: assets/clip_02.png

### PROMPT (Copy to Veo)
```
First-person POV, 35mm lens, shallow depth of field f/2.0, 9:16 vertical, 24fps, cinematic color grade.

VISUAL: Crossing threshold. Lighting shift (bright to dark). Hands interact with door/barrier. Background blurred.

CAMERA: Push forward, rack focus from hands to interior. Visible hands throughout.

LIGHTING: Diegetic sources only. Lighting transition moment.

ANTI-ARTIFACT: NO texture morphing. Geometry LOCKED. Maintain hand position. NO face reveals.

AUDIO: [MUSIC] Tension builds + [AMBIENT] Room tone change + [SFX] Door mechanism + [VOICE] Breath catch + [NARRATOR] Context.
```

---

## CLIP 3: THE DETAILS
Source: assets/clip_03.png

### PROMPT (Copy to Veo)
```
First-person POV, 35mm lens, EXTREME shallow depth of field f/1.8, 9:16 vertical, 24fps, cinematic color grade.

VISUAL: Macro focus on specific object/texture. Hands reach toward subject. Only subject sharp, everything else creamy blur.

CAMERA: Rack focus, locked perspective. Visible hands throughout.

LIGHTING: Diegetic sources only.

ANTI-ARTIFACT: NO texture morphing. Geometry LOCKED. Maintain hand position. NO face reveals.

AUDIO: [MUSIC] Minimal pulses + [AMBIENT] Low hum + [SFX] Tactile sounds + [VOICE] Whisper + [NARRATOR] Detail.
```

---

## CLIP 4: THE ACTIVITY
Source: assets/clip_04.png

### PROMPT (Copy to Veo)
```
First-person POV, 35mm lens, shallow depth of field f/2.0, 9:16 vertical, 24fps, cinematic color grade.

VISUAL: Observing environment's function. Movement in scene. POV tracks action. Background blurred.

CAMERA: Pan or tilt following action. Visible hands throughout.

LIGHTING: Diegetic sources only.

ANTI-ARTIFACT: NO texture morphing. Geometry LOCKED. Maintain hand position. NO face reveals.

AUDIO: [MUSIC] Rhythm begins + [AMBIENT] Activity sounds + [SFX] Event noise + [VOICE] Reaction + [NARRATOR] Build.
```

---

## CLIP 5: THE INTENSITY
Source: assets/clip_05.png

### PROMPT (Copy to Veo)
```
First-person POV, 35mm lens, shallow depth of field f/2.0, 9:16 vertical, 24fps with motion blur, high contrast.

VISUAL: Environment reacts. Fast camera movement. Chaos begins. Motion blur on edges, center sharp.

CAMERA: Handheld shake, quick snap movements. Visible hands throughout.

LIGHTING: Diegetic sources only. Dynamic/flickering acceptable.

ANTI-ARTIFACT: Motion blur acceptable. NO texture morphing. NO face reveals.

AUDIO: [MUSIC] Crescendo + [AMBIENT] Tension drone + [SFX] Impact/crash + [VOICE] Panic + [NARRATOR] Escalation.
```

---

## CLIP 6: THE ENCOUNTER
Source: assets/clip_06.png

### PROMPT (Copy to Veo)
```
First-person POV, 35mm lens, EXTREME shallow depth of field f/1.4, 9:16 vertical, 24fps, dramatic lighting.

VISUAL: Hero shot of subject/entity. Full reveal. Maximum impact. ONLY SUBJECT IN SHARP FOCUS, everything else heavily blurred.

CAMERA: Locked focus on subject. Frozen POV. Visible hands in foreground (blurred acceptable).

LIGHTING: Dramatic/horror lighting. Diegetic sources.

ANTI-ARTIFACT: Subject geometry LOCKED. NO morphing. This is PEAK MOMENT.

AUDIO: [MUSIC] Full climax + [AMBIENT] Overwhelming + [SFX] Signature sound + [VOICE] Scream/gasp + [NARRATOR] Peak line.
```

---

## CLIP 7: THE REACTION
Source: assets/clip_07.png

### PROMPT (Copy to Veo)
```
First-person POV, 35mm lens, shallow depth of field f/2.0, 9:16 vertical, 24fps with heavy motion blur, strobe lighting acceptable.

VISUAL: Retreating or interacting. Dynamic motion. POV in chaos. Hands frantically doing something.

CAMERA: Handheld shake, slalom movement. Visible hands throughout.

LIGHTING: Diegetic sources. Strobe/flickering acceptable.

ANTI-ARTIFACT: Motion blur acceptable. Maintain core geometry.

AUDIO: [MUSIC] Pursuit beat + [AMBIENT] Chaos + [SFX] Rapid impacts + [VOICE] Commands/screams + [NARRATOR] Action line.
```

---

## CLIP 8: THE CONCLUSION
Source: assets/clip_08.png

### PROMPT (Copy to Veo)
```
First-person POV, 35mm lens, depth of field relaxing, 9:16 vertical, 24fps slow motion feel, desaturated color grade.

VISUAL: Final state. Resolution or aftermath. Calm or dread. Hands visible at edges.

CAMERA: Slow dolly out, stabilized. Peaceful or ominous framing.

LIGHTING: Diegetic sources. Mood shift from previous clips.

ANTI-ARTIFACT: NO texture morphing. Geometry LOCKED.

AUDIO: [MUSIC] Fade out or silence + [AMBIENT] Calm/static + [SFX] Final sound + [VOICE] Closing line + [NARRATOR] Outro.
```

---

## REFERENCE
Protocol: core/protocols/fpp_cinematography.md
""",
        'fpp_short': """# FPP SHORT — 3 CLIP SEQUENCE (STYLIZED)
# Each clip is SELF-CONTAINED for individual Veo generation.
# Total: 24 seconds (3 clips × 8 seconds)
# ART STYLE: Stylized game graphics (NOT photorealistic)

Concept: Short First Person Narrative of {name}.

---

## CLIP 1: THE SETUP
Source: assets/clip_01.png

### PROMPT (Copy to Veo)
```
First-person POV, stylized 3D graphics, Unreal Engine 5 style, video game aesthetic, 9:16 vertical, 24fps.

VISUAL: Establishing shot. Hands visible, entering the environment. Clean render, smooth textures. Background slightly blurred.

CAMERA: Stable movement. Visible hands throughout. Game-like camera.

LIGHTING: Dramatic game lighting. Strong shadows. Clean light sources.

STYLE: Stylized NOT realistic. Clean geometry. Consistent textures. NO photorealism.

AUDIO: [MUSIC] Low ambient + [AMBIENT] Environment + [SFX] Entry sounds + [VOICE] Casual + [NARRATOR] Hook.
```

---

## CLIP 2: THE TENSION
Source: assets/clip_02.png

### PROMPT (Copy to Veo)
```
First-person POV, stylized 3D graphics, Unreal Engine 5 style, video game aesthetic, 9:16 vertical, 24fps.

VISUAL: Something is wrong. Hands react. Environment shifts. Tension building. Same art style as Clip 1.

CAMERA: Slight jitter. Quick movements. Visible hands throughout. Game-like camera.

LIGHTING: Darker. More dramatic. Horror game lighting.

STYLE: Stylized NOT realistic. Maintain visual consistency with Clip 1. Same textures.

AUDIO: [MUSIC] Tension rising + [AMBIENT] Unsettling + [SFX] Warning sounds + [VOICE] Worried + [NARRATOR] Build.
```

---

## CLIP 3: THE PAYOFF
Source: assets/clip_03.png

### PROMPT (Copy to Veo)
```
First-person POV, stylized 3D graphics, Unreal Engine 5 style, video game aesthetic, 9:16 vertical, 24fps.

VISUAL: The reveal/climax. Maximum impact. Subject in focus. Same art style as previous clips.

CAMERA: Dramatic framing. Peak moment. Visible hands (can be blurred).

LIGHTING: Maximum drama. Horror game peak lighting.

STYLE: Stylized NOT realistic. Maintain consistency. This is PEAK MOMENT.

AUDIO: [MUSIC] Climax or silence + [AMBIENT] Overwhelming or quiet + [SFX] Signature sound + [VOICE] Reaction + [NARRATOR] Final line.
```

---

## REFERENCE
Protocol: core/protocols/fpp_cinematography.md
"""
    },
    'voxel': {
        'stich': """## Voxel Horror (16s)
Isometric voxel art style, Minecraft-adjacent aesthetic.
{name} environment with hidden horror element.
LIGHTING SHIFT: Warm daylight -> Cold night -> Red warning glow.
ANTI-AI REALISM: Chunky pixels, consistent geometry, no morphing.
""",
        'circular': """## Voxel Loop
Subject: {name}
Style: Isometric Voxel Art.
Action: Mechanical repetition or glitch cycle.
""",
        'boomerang': """## Voxel Boomerang
Subject: {name}
Action: Building/Collapsing structure.
"""
    }
}

def create_kit_files(kit_path: Path, name: str, theme: str, formula: str = 'stitch_2clip', strategy: str = None) -> None:
    """Creates all files for a new production kit."""
    # Get formula config
    f_config = FORMULAS.get(formula, FORMULAS['stitch_2clip'])
    
    # Create directories
    kit_path.mkdir(parents=True, exist_ok=True)
    for d in f_config['dirs']:
        (kit_path / d).mkdir(exist_ok=True)
    
    # Create script
    script_template = SCRIPT_TEMPLATES.get(theme, SCRIPT_TEMPLATES['loop'])
    script_content = script_template.format(name=name.replace('_', ' ').title())
    (kit_path / 'script.txt').write_text(script_content, encoding='utf-8')
    
    # Create prompt
    # Nested lookup: Theme -> Formula Prefix
    prompt_theme = PROMPT_TEMPLATES.get(theme, PROMPT_TEMPLATES['loop'])
    # Handle legacy string templates if not updated, or dicts
    if isinstance(prompt_theme, str):
        prompt_template = prompt_theme 
    else:
        prompt_template = prompt_theme.get(f_config['prompt_prefix'], prompt_theme.get('stich', ""))
        
    prompt_content = prompt_template.format(name=name.replace('_', ' ').title())
    
    # INJECT STRATEGY
    if strategy:
        prompt_content = f"## [STRATEGIC DIRECTION]\n{strategy}\n\n" + prompt_content
        
    (kit_path / 'prompt.txt').write_text(prompt_content, encoding='utf-8')
    
    # Create kit.yaml metadata (skeleton)
    import yaml
    from datetime import datetime
    kit_yaml = {
        'id': kit_path.name.split('_')[0],
        'name': name,
        'created': datetime.now().strftime("%Y-%m-%d"),
        'ingredients': {
            'theme': theme,
            'formula': formula
        },
        'status': 'draft'
    }
    with open(kit_path / 'kit.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(kit_yaml, f, default_flow_style=False)
