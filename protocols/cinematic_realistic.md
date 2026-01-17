# CINEMATIC REALISTIC PROTOCOL
> Production-grade prompt engineering for semi-realistic 3D cinematics.
> Used for: Third-person narratives, character stories, environmental storytelling.

---

## PROMPT WRITING STYLE (CRITICAL)

### Write Cinematic Prose, NOT Checklists

Generate prompts as **single, cinematic scene descriptions**:
- Write in dense, film-language paragraphs
- Prioritize concrete visuals, spatial detail, atmosphere, and motion
- Describe what is seen, how it moves, and how it feels moment-to-moment

### Integrate Naturally
- Environment + subject + camera + lighting + motion in flowing prose
- Engine-aware details (UE5, semi-realistic 3D) inside the description
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
**Scene:** A man stands at the edge of a cliff, silhouetted against a 
burning sunset, his torn jacket flapping in the wind. **Visuals:** 
Semi-realistic 3D graphics rendered in Unreal Engine 5 style. Realistic 
proportions with slightly smooth game-engine facial details. Muted, 
natural colors with soft cinematic lighting and clean global illumination. 
**Camera:** Medium shot at eye level, shallow depth of field, the figure 
sharp against a heavily blurred ocean background. **Audio:** Wind howls 
across the cliffs. Distant seagulls. A low, melancholic orchestral drone 
builds slowly. His breath is steady. Accepting.
```

---

## ART STYLE: CLEAN STOCK 3D (PRIMARY)

> For corny cursed advice content — clean, professional, The Sims-like aesthetic.

### Core Keywords
```
High-quality 3D render, semi-realistic but smooth, Cinema 4D or Blender Cycles 
aesthetic, clean soft lighting, realistic human proportions, slightly plastic/
smooth skin texture like The Sims, professional stock footage quality, neutral 
to mild facial expressions, muted natural colors, corporate explainer video 
aesthetic, clean and polished render, NOT cartoony, NOT exaggerated.
```

### Character Rendering
- **Realistic proportions** (normal human body ratios)
- **Smooth plastic-like skin** (The Sims / stock 3D feel)
- **Neutral expressions** (subtle, not exaggerated)
- **Clean simple clothing** (readable, not detailed)

### Expressions (Subtle, Not Cartoony)
- **Curiosity**: Slight head tilt, mild interest
- **Realization**: Eyes widen slightly, pause
- **Concern**: Mild frown, raised eyebrow
- **Reaction**: Subtle, understated — let narrator carry comedy

### Environment Rendering
- Clean, professional backgrounds
- Soft focus on non-essential elements
- Muted, natural color palette
- Stock footage / explainer video quality

### Lighting
- Soft, diffused studio lighting
- No harsh shadows
- Natural daylight feel
- Clean and professional

### What to AVOID
- ❌ Cartoony / exaggerated proportions
- ❌ Big expressive eyes
- ❌ Vibrant saturated colors
- ❌ Dark moody lighting
- ❌ Photorealistic (too detailed)

---

## ART STYLE: SEMI-REALISTIC AAA (ALTERNATE)

> For serious/dramatic content only. NOT for corny cursed advice.

### Core Keywords
```
Semi-realistic 3D rendered scene, Unreal Engine–style, realistic proportions 
with slightly smooth game-engine facial details, soft cinematic lighting, 
muted natural colors, realistic PBR materials, subtle depth of field, 
clean global illumination, polished and professional, AAA game cutscene quality.
```

### When to Use
- Serious survival stories
- Emotional drama
- Horror with dread (not comedy)
- Character-driven narratives

---

## SEQUENTIAL IMAGE GENERATION (CRITICAL)

> **NEVER generate all images in parallel!** This causes visual inconsistencies.

### Two Types of References

| Reference Type | Purpose | Which Frame to Use |
|----------------|---------|-------------------|
| **STYLE Reference** | Character look, art style, lighting | Frame 1 (always) |
| **POSITION Reference** | Where character is, what they're doing | PREVIOUS frame |

### ⚠️ CRITICAL: Position Continuity

If the character **changes location** between frames, use the **PREVIOUS frame** as reference:

```
❌ WRONG (causes teleportation):
Frame 3: Character ON LAVA
Frame 4: Reference = Frame 1 (on cliff) → Character teleports back to cliff

✅ CORRECT:
Frame 3: Character ON LAVA  
Frame 4: Reference = Frame 3 (on lava) → Character stays on lava
```

### The Chained Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  FRAME 1: Generate standalone                               │
│      ↓                                                      │
│  FRAME 2: Reference = Frame 1 (style + position same)       │
│      ↓                                                      │
│  FRAME 3: If position CHANGES → Reference = Frame 2         │
│           If position SAME → Reference = Frame 1            │
│      ↓                                                      │
│  FRAME 4: If position CHANGES → Reference = Frame 3         │
│           If position SAME → Reference = Frame 1            │
└─────────────────────────────────────────────────────────────┘
```

### Rule of Thumb
- **Same location throughout?** → Always use Frame 1
- **Character moves to new location?** → Use the frame where they ARE in that location

### Required Prompt Keywords for Chaining
- `SAME EXACT scene as reference` (for position continuity)
- `Same character as reference` (for style consistency)
- `Same lighting style`
- `Same art style`
- `Maintain visual consistency`

---

## CAMERA CONTROL THROUGH KEYFRAMES (ENGAGEMENT)

> **Keyframes control camera movement, not just character action.**
> Dynamic camera = engaged viewer. Static camera = boring.

### The Technique

Control camera motion by varying **framing** between start/end frames:

| Start Frame | End Frame | Veo Creates |
|-------------|-----------|-------------|
| Wide shot | Close-up | **ZOOM IN** |
| Close-up | Wide shot | **ZOOM OUT** |
| Left side | Right side | **PAN** |
| High angle | Low angle | **TILT** |

### Why This Matters

- Static talking head = viewer scrolls away
- Dynamic camera = keeps attention
- Each clip should have **visual movement**

### Example: The Lava Jump

```
Clip 1: Wide (at edge) → Wide (on lava)     = Character movement
Clip 2: Wide (smug) → Close-up (boots)      = ZOOM IN (engaging!)  
Clip 3: Close-up → Wide (uh oh)             = ZOOM OUT (reveal)
Clip 4: Wide (concern) → Wide (dancing)     = Character movement
```

### Rule of Thumb

- Alternate between **wide** and **close-up** frames
- Don't repeat same framing for multiple clips
- Close-ups for **detail moments** (boots, face, object)
- Wide shots for **action moments** (jumping, dancing)

---

## CAMERA OPTIONS

### Shot Types
| Shot | Description | Keywords |
|------|-------------|----------|
| **Wide** | Full environment + character | `wide establishing shot`, `full body visible` |
| **Medium** | Waist-up | `medium shot`, `waist-up framing` |
| **Close-up** | Face/expression focus | `close-up`, `face fills frame` |
| **Over-shoulder** | Behind character | `over-the-shoulder`, `back of head visible` |
| **Low Angle** | Looking up at character | `low angle`, `heroic framing` |
| **High Angle** | Looking down | `high angle`, `vulnerable framing` |

### Camera Movement
| Movement | Keywords |
|----------|----------|
| Static | `locked camera`, `static shot`, `no movement` |
| Slow push | `slow dolly in`, `gentle push forward` |
| Orbit | `slow orbit`, `circling the subject` |
| Tracking | `tracking shot`, `following movement` |

### Depth of Field
- `shallow depth of field` — Character sharp, background blurred
- `deep focus` — Everything sharp
- `rack focus` — Focus shifts between subjects

---

## AUDIO LAYERS (5-LAYER STANDARD)

Every clip should define:

1. **[MUSIC]** — Score, drone, emotional tone
2. **[AMBIENT]** — Environment sounds (wind, room tone, nature)
3. **[SFX]** — Specific sound effects (footsteps, impacts, door creaks)
4. **[VOICE]** — Character dialogue (with emotion/delivery direction)
5. **[NARRATOR]** — Optional voiceover (if story uses narration)

### Audio in Prose (Preferred)
```
**Audio:** A low orchestral drone underscores the tension. Wind 
whistles through broken windows. His boots crunch on broken glass. 
He mutters, "This is it." The narrator: "He had one chance left."
```

---

## ANTI-ARTIFACT DIRECTIVES

### Character Consistency
- `Maintain exact character appearance`
- `Same facial features throughout`
- `Consistent clothing/outfit`
- `No hand deformation`

### Environment Consistency
- `Geometry LOCKED`
- `No texture morphing`
- `Consistent lighting direction`
- `Same color palette throughout`

### General
- `Consistent perspective`
- `Natural physics`
- `Realistic body movement`

---

## GENRE PRESETS

### Drama/Emotional
```
Soft cinematic lighting, muted earth tones, shallow depth of field, 
close-up emotional framing, quiet ambient audio, minimal score.
```

### Action/Thriller
```
High contrast lighting, dynamic camera angles, motion blur on action, 
punchy sound design, bass-heavy score, quick cuts.
```

### Survival/Isolation
```
Muted natural colors, harsh environmental lighting, wide lonely shots, 
environmental audio dominant, minimal dialogue, ambient score.
```

### Mystery/Suspense
```
Chiaroscuro lighting, shadows hiding details, slow camera movement, 
silence punctuated by sounds, tension drone, whispered dialogue.
```

---

## SCRIPT WRITING STYLE: CORNY CURSED ADVICE

### The Formula

```
┌──────────────────────────────────────────────────────┐
│  [0:00-0:03] HYPOTHETICAL HOOK                       │
│     "If you were stranded on an island..."           │
│     Relatable scenario, invites curiosity            │
├──────────────────────────────────────────────────────┤
│  [0:03-0:07] ABSURD BUT LOGICAL ADVICE               │
│     "You could shave your head bald..."              │
│     Sounds stupid but presenter is serious           │
├──────────────────────────────────────────────────────┤
│  [0:07-0:15] ESCALATE WITH "APPLICATIONS"            │
│     "The reflection could signal planes!"            │
│     Builds credibility, viewer starts believing      │
├──────────────────────────────────────────────────────┤
│  [0:15-0:21] CORNY DARK TWIST                        │
│     "...you might burn your head"                    │
│     Dad-joke energy, self-aware, meme-worthy         │
└──────────────────────────────────────────────────────┘
```

### Tone Rules

| DO | DON'T |
|----|-------|
| Deadpan delivery | Never acknowledge absurdity |
| Corny punchline | Not edgy or shock-value |
| Self-aware silly | Not trying too hard |
| "Wait what?" moment | Not predictable |
| Light-hearted dark | Not disturbing |

### Voice Direction
- **NARRATOR ONLY** — Narrator carries all the comedy
- **Tone**: Calm, informative, educational (like a documentary)
- **Delivery**: Completely serious throughout (never breaks)
- **Pacing**: Steady build, quick twist at end
- **Duration**: 15-25 seconds ideal

### Character Audio Rule (CRITICAL)

> Characters do NOT speak words. They make **non-verbal reaction sounds** only.

**Think**: Minions, Shaun the Sheep, Mr. Bean, early Disney shorts

| Emotion | Sound | Example |
|---------|-------|---------|
| Curiosity | "Hmm?" | Looking at lava |
| Interest | "Ooh!" | Seeing it works |
| Thinking | "Hmm..." | Nodding along |
| Surprise | *gasp* | When it goes wrong |
| Realization | "Uh oh" | Feet on fire |
| Confusion | "Uhh...?" | Processing |
| Pain | "Ahh!" / wince | Comedic hurt |

**NO actual words, sentences, or dialogue.**
**YES to grunts, gasps, sighs, and reaction sounds.**

### Visual Reactions (USER PREFERENCE: EXPRESSIVE)

> Reactions should be **BIG and PHYSICAL**, not subtle. Think cartoon comedy.

**Preferred Reaction Style:**
- ✅ **Expressive faces** — eyes WIDE, mouth OPEN, clear emotions
- ✅ **Physical comedy** — hot feet dance, arms flailing, hopping
- ✅ **Exaggerated body language** — not subtle, easily readable
- ✅ **Comedic desperation** — funny panic, not realistic terror

**Classic Cartoon Reactions to Use:**
| Situation | Reaction |
|-----------|----------|
| Hot/burning | "Hot feet dance" — hopping foot to foot, arms flailing |
| Shock | Arms raised, eyes bulging, mouth in "O" |
| Realization | Slow look down, freeze, then panic |
| Pain | Comedic wince, jumping, "Ah! Ah! Ah!" sounds |
| Confusion | Head scratch, question mark expression |
| Pride (before fall) | Arms crossed, smug grin, confident stance |

**NOT Preferred:**
- ❌ Subtle expressions (hard to read)
- ❌ Realistic terror/fear (too dark)
- ❌ Static poses during twist moments

### Example Script
```
[0:00] "If you were stuck in quicksand..."
[0:02] "You could drink the sand to lower the level."
[0:05] "Sand contains minerals your body needs."
[0:08] "The more you drink, the lower you sink."
[0:11] "Eventually you'd reach solid ground."
[0:14] "Also, you'd be full of sand."
[0:17] "But at least you'd be alive."
[0:19] "For about five minutes."
```

### Meme-Worthy Endings
- Self-harm that sounds logical
- The "advice" backfiring hilariously
- Understated dark consequences
- "But at least..." false comfort

---

## USAGE

When creating a cinematic kit, reference this protocol:
```
Protocol: core/protocols/cinematic_realistic.md
```

Apply to any formula by ensuring prompts follow the prose style
and sequential generation workflow.
