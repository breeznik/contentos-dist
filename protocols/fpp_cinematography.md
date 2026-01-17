# FPP CINEMATOGRAPHY PROTOCOL
> Research-backed prompt engineering for First-Person Perspective AI video generation.
> Used by: `fpp_narrative` and `fpp_short` formulas in ContentOS.

---

## PROMPT WRITING STYLE (CRITICAL)

### Write Cinematic Prose, NOT Checklists

Generate prompts as **single, cinematic scene descriptions**:
- Write in dense, film-language paragraphs
- Prioritize concrete visuals, spatial detail, atmosphere, and motion
- Describe what is seen, how it moves, and how it feels moment-to-moment

### Integrate Naturally
- Environment + subject + camera + lighting + motion in flowing prose
- Engine-aware details (UE5, stylized 3D) inside the description
- Stylistic constraints embedded naturally, not as headers
- Audio as part of the scene narrative, not as `[TAGS]`

### Avoid
- ❌ Bulleted checklists
- ❌ Redundant restatements
- ❌ Generic labels without sensory detail
- ❌ Over-technical metadata
- ❌ `[AUDIO]` `[CAMERA]` tag formatting

### Example Format
```
**Scene:** A first-person perspective captures gloved hands approaching 
a dirty bathroom mirror in a high-contrast survival horror aesthetic. 
**Visuals:** Stylized 3D graphics rendered in Unreal Engine 5 style 
depict a dark bathroom at night, dominated by grimy teal-blue tiles... 
**Camera:** A 9:16 vertical frame at 24fps executes a slow approach... 
**Audio:** The scene is underscored by a low ambient drone. A whispered 
voice states, "Just checking..." The narrator follows: "She always 
avoided mirrors after dark."
```

Write as if briefing a director + engine simultaneously.

---

## 0. ART STYLE (CRITICAL)

### USE STYLIZED GRAPHICS (NOT REALISM)
AI generates more consistent results with stylized/game-like graphics:

| Style | Keywords |
|-------|----------|
| **Game-like** | `stylized 3D graphics`, `Unreal Engine 5 style`, `video game aesthetic` |
| **Clean** | `clean render`, `smooth textures`, `cel-shading` |
| **Horror Game** | `Outlast style`, `Resident Evil aesthetic`, `survival horror game graphics` |
| **Sci-Fi Game** | `Mass Effect style`, `Dead Space aesthetic`, `sci-fi game graphics` |

### AVOID
- `hyper-realistic`
- `photo-realistic`
- `8k photography`

These cause inconsistent AI outputs and weird artifacts.

---

## 1. SEQUENTIAL IMAGE GENERATION (CRITICAL)

> **NEVER generate all images in parallel!** This causes visual inconsistencies.

### The Chained Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  CLIP 1: Generate standalone                                │
│      ↓                                                      │
│  STUDY: Observe environment, hands, lighting, textures      │
│      ↓                                                      │
│  CLIP 2: Generate using CLIP 1 as ImagePath reference       │
│          Prompt: "SAME EXACT environment as reference..."   │
│      ↓                                                      │
│  STUDY: Verify consistency with Clip 1                      │
│      ↓                                                      │
│  CLIP 3: Generate using CLIP 1 as ImagePath reference       │
│          Prompt: "SAME EXACT environment as reference..."   │
└─────────────────────────────────────────────────────────────┘
```

### Required Prompt Keywords for Chaining
When using a reference image, include these in the prompt:
- `SAME EXACT [environment/bathroom/room] as reference image`
- `Same [hands/gloves/clothing] as reference`
- `Same lighting style`
- `Same art style`
- `Maintain visual consistency`

### Anti-Pattern (DO NOT DO)
```python
# ❌ WRONG - Parallel generation causes inconsistency
generate_image("clip_01", prompt1)
generate_image("clip_02", prompt2)  # No reference!
generate_image("clip_03", prompt3)  # No reference!
```

### Correct Pattern
```python
# ✅ CORRECT - Sequential chained generation
generate_image("clip_01", prompt1)
# STUDY clip_01 output first!
generate_image("clip_02", prompt2, ImagePaths=["clip_01.png"])
# STUDY clip_02 output!
generate_image("clip_03", prompt3, ImagePaths=["clip_01.png"])
```

---

### Action (Smooth)
- `gimbal-stabilized POV`
- `smooth forward motion`
- `controlled pan`
- `natural head bobbing while walking`

### Horror (Unstable)
- `handheld camera shake`
- `unsteady nervous POV`
- `breathing movement`
- `quick snap look`

### Cinematic
- `slow dolly forward`
- `push in`
- `drift right`

---

## 2. LENS & FOV

| Style | Keywords |
|-------|----------|
| Natural Human Vision | `35mm lens`, `natural FOV` |
| Action/Gaming | `24mm wide angle`, `slight barrel distortion` |
| Intimate/Horror | `50mm lens`, `close framing` |

**Anti-Artifact**: Avoid extreme fisheye or telephoto.

---

## 3. DEPTH OF FIELD (Quality Optimization)

### Purpose
- Reduces AI compute on background.
- Hides morphing artifacts in blur.
- Directs viewer attention.

### Keywords
- `shallow depth of field at f/1.8`
- `wide aperture f/2.0`
- `background bokeh blur`
- `creamy defocus`
- `selective focus on [subject]`
- `center-weighted sharpness`
- `peripheral blur`

### Rack Focus
- `rack focus from hands to distance`
- `focus pull to subject`

---

## 4. STABILIZATION

| Genre | Keywords |
|-------|----------|
| Action | `gimbal stabilized`, `smooth glide` |
| Horror | `handheld shake`, `nervous jitter` |
| Tension | `locked static POV`, `held breath stillness` |

---

## 5. LIGHTING (Immersion)

### Diegetic Sources Only
- `flashlight beam illumination`
- `screen glow on face`
- `practical light sources only`
- `muzzle flash lighting`

### Dynamic
- `flickering shadows`
- `moving light source`
- `lens flare from bright object`

### Avoid
- `NO uniform studio lighting`
- `NO flat frontal light`

---

## 6. FRAME RATE

| Genre | Setting |
|-------|---------|
| Cinematic | `24fps natural motion blur` |
| Game-like | `60fps crisp action` |
| Horror | `24fps with occasional stutter` |

---

## 7. AI ANTI-ARTIFACT PROTOCOL

### Camera Lock (Prevents Drift)
- `first-person POV`
- `visible hands in frame`
- `gloved hands gripping controls`
- `legs visible at bottom of frame`

### Temporal Consistency
- `hyper-realistic`
- `photo-realistic`
- `ultra-detailed`
- `consistent perspective throughout`

### Physics Anchoring
- `natural physics`
- `realistic body movement`
- `gravity-grounded motion`

### Anti-Morph Directives
- `NO texture morphing`
- `geometry LOCKED`
- `maintain consistent hand position`
- `NO face deformation`

---

## 8. MASTER TEMPLATE

```
First-person POV, [LENS]mm lens equivalent, shallow depth of field at f/[APERTURE], 
[BODY ANCHOR] visible in frame, hyper-realistic, [STABILIZATION] motion, 
center-weighted sharpness with peripheral blur, [SUBJECT] geometry LOCKED, 
consistent perspective throughout, [FRAME_RATE]fps cinematic motion blur.
[LIGHTING_SOURCE] lighting only. NO texture morphing.
```

---

## USAGE IN CONTENTOS

This protocol is automatically applied when using:
```bash
python contentos.py kit create "project_name" --formula fpp_narrative
```

The `fpp_universal` template in `core/templates.py` includes these keywords.
