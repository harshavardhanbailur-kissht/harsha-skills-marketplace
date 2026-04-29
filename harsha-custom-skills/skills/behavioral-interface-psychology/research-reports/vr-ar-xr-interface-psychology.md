# VR/AR/XR Interface Psychology Research

## Executive Summary

This report synthesizes research on spatial computing, virtual reality, augmented reality, and mixed reality interface psychology from IEEE VR, CHI conferences, and industry guidelines from Meta, Apple, and Microsoft.

---

## 1. Spatial Interaction Fundamentals

### 3D Pointing Accuracy (Fitts' Law in VR)

- Fitts' Law is applicable in VR for pointing with handheld controllers
- Aggregated regression constants: **a = 0.1700, b = 0.4071**
- Target size has greater impact than target distance
- Models accounting for depth improve predictive power

### Vergence-Accommodation Conflict (VAC)

- Occurs when brain receives mismatching cues between vergence and accommodation
- Major contributor to VR sickness, visual fatigue, headaches
- Makes it impossible to focus on close objects in VR

**Solutions:** Multifocal displays, light field displays

### Hand Tracking Precision (Meta Quest 2)

| Metric | Value |
|--------|-------|
| Average fingertip positional error | 1.1 cm |
| Average joint angle error | 9.6 degrees |
| Average temporal delay | 45.0 ms |

### Controller vs Hand Tracking

| Factor | Controllers | Hand Tracking |
|--------|------------|---------------|
| Speed | Faster (simple tasks) | Slower |
| Precision | High, tactile feedback | Lower, context-dependent |
| Learnability | Higher | Lower |
| Cognitive Load | Lower | Higher |
| Natural Feel | Less natural | More intuitive for some |

---

## 2. Motion Sickness & Comfort

### Vection and Cybersickness

- Vection is necessary but not sufficient for cybersickness
- **Unexpected vection** increases likelihood and severity
- Motion sickness susceptibility is most prominent predictor
- Pupil dilation emerged as significant predictor

### Frame Rate Requirements

| Standard | Value |
|----------|-------|
| Minimum target | 90 FPS |
| Motion-to-photon latency | <20 ms |
| Sony PSVR | <18 ms |
| Meta (90Hz) | 13 ms |

### Field of View Effects

- Larger FOV increases immersion but can increase cybersickness
- **Dynamic FOV restriction** significantly reduces cybersickness
- Excessively narrow FOV decreases immersion

### Locomotion Method Comparison

| Method | Comfort | Performance | Preference |
|--------|---------|-------------|------------|
| Teleportation | Highest | Lower efficiency | Lower |
| Smooth/Linear | Lowest | Highest efficiency | Highest |
| Joystick | Moderate | Best balance | High |

**Cybersickness Reduction:**
- Rotation snapping: **40% reduction**
- Translation snapping: **50% reduction**

### Rest Frames

- Visual references stable in relation to physical environment
- Reduce discomfort during virtual travel
- Promote better eye-gaze stability

---

## 3. Spatial UI Layout

### Optimal Distance for UI Elements

| Guideline | Distance |
|-----------|----------|
| Recommended placement | ~1 meter |
| Eye strain onset | <0.5 meters |
| Oculus minimum | 0.75 meters |
| Comfortable viewing | 2-3 meters |

### Curved vs Flat UI Panels

- For visual search at 50 cm: **600R curvature radius** recommended
- Curved monitors reduce eye strain by maintaining consistent distance
- For wide VR UI panels: slight curvature keeps edges at equal distance

### Eye Comfort Zones

- Most fixations fall within **±15 degrees** of straight ahead
- Comfortable head rotation: **20 degrees up, 12 degrees down**
- Content placement: **40 degrees below** to **10 degrees above** eye level
- Horizontal FOV without neck movement: ~**60 degrees**

### Text Legibility in VR

- Recommended angular size: **41 dmm ±14 dmm**
- Minimum readable: **1.33 degrees**
- Traditional 12-32pt fonts are too small at 2-3 meter distances

| Distance | Recommended Font |
|----------|------------------|
| 5 meters | 32-40 pt |
| 10 meters | 36-56 pt |
| 15 meters | 56-68 pt |

---

## 4. Input Modalities in XR

### Gaze-Based Interaction

- Eye gaze with **500 ms dwell time** matches controller performance
- Eye tracking accuracy: **<1 degree** with low-cost devices
- Target size has greater impact than distance

### Hand Gesture Vocabulary

**Basic Patterns:**
1. Thumb-to-finger (pinch)
2. Grasping and closure (grab)
3. Swinging and extension
4. Tapping and striking
5. Shaping and symbolizing

**Design Principles:**
- Low-effort gestures (pinch, poke) for frequent use
- Higher-effort gestures (grab) used sparingly to avoid fatigue

### Haptic Feedback Requirements

| Specification | Value |
|---------------|-------|
| Vibration range | 0-125 Hz |
| Force amplitude | 1.2 N at 125 Hz |

- Skin-stretch more accurate than vibrotactile
- Vibrotactile preferred due to familiarity
- Bimodal feedback (haptic + visual) enhances presence

---

## 5. AR-Specific Patterns

### World-Locked vs Head-Locked UI

| Aspect | World-Locked | Head-Locked |
|--------|-------------|-------------|
| Position | Anchored to environment | Fixed in HMD view |
| Strength | Contextually relevant | Efficient for focused tasks |
| Weakness | Divided attention | Can cause discomfort |
| Best For | Spatial awareness | Salient warnings |

### Spatial Anchor Comprehension (HoloLens)

- Stage frame: **<5 meter** diameter experiences
- Beyond 5 meters: spatial anchors needed
- Holograms **>3 meters** from anchor may have positional errors

---

## 6. Presence & Immersion

### Presence Measurement (iGroup Presence Questionnaire)

- 14 questions, 3 subscales: Spatial Presence, Involvement, Realness
- Over 2500 citations

**Key Distinction:**
- **Immersion:** Technology variable (objective)
- **Presence:** User experience variable (subjective)

### Break-in-Presence Factors

1. Removing Social Presence cues
2. Removing Self-Presence cues
3. Removing Physical Presence cues
4. Physical breakdowns (collision with real environment)
5. Questionnaire administration during VR

### Avatar Embodiment

**Three Components:**
1. Sense of Agency
2. Sense of Ownership
3. Self-Location

- First-person perspective sufficient for embodiment illusion
- Illusion stronger for human-like hands

### Social VR Psychology

**Enhancing Factors:**
- Realistic avatars
- Natural interaction (moving, gestures)
- Spatialized audio
- Recognizable avatars
- Collaborative tasks

---

## 7. Accessibility in XR

### One-Handed Mode Requirements

- Provide remappable inputs for left and right hands
- Support single controller operation
- Variable hold/release times

**Statistics:** >42% of XR users cite non-standard hand usage, but <15% of experiences provide full mapping flexibility.

### Vision Accessibility

- Color vision affects 1 in 12 men, 1 in 200 women
- Minimum target: **22mm x 22mm / 48dp x 48dp / 3 degrees FOV at 0.42m**

### Arm Fatigue (Gorilla Arm Syndrome)

- Extended arm positions: ~3.77x more shoulder torque
- Only 25% complete 30-minute mid-air gesture sessions

**Solutions:**
- Supported gestures allowing arm resting
- Horizontal movements preferable to vertical

---

## 8. Platform-Specific Guidelines

### Meta Quest Design Guidelines

| Metric | Value |
|--------|-------|
| Optimal UI distance | ~1 meter |
| FOV without neck movement | 60 degrees |
| Minimum interactive element | 22mm x 22mm |

### Apple Vision Pro HIG

| Element | Value |
|---------|-------|
| Minimum target area | 60x60pt |
| UI elements (optical) | 44x44pt |
| Default volume size | 1280 points |

**Scaling Behavior:**
- Windows: scale up at distance to maintain apparent size
- Volumes: fixed scale for sense of presence

### Microsoft HoloLens

- Stage frame: <5 meter experiences
- Anchors needed beyond 5 meters
- Error increases >3 meters from anchor origin

---

## Critical Timing Thresholds

| Metric | Threshold |
|--------|-----------|
| Motion-to-photon latency | <20 ms |
| Minimum frame rate | 90 FPS |
| Sony PSVR latency | <18 ms |
| Meta (90Hz) latency | 13 ms |
| Gaze dwell time | 500 ms |
| Hand tracking delay | 45 ms |
| Foveated rendering tolerance | 50-70 ms |
| Spatial audio latency | <20 ms |

---

## Distance & Angular Guidelines

| Element | Measurement |
|---------|-------------|
| Recommended UI distance | 1 meter |
| Minimum comfortable distance | 0.75 meter |
| Eye strain onset | <0.5 meter |
| Spatial anchor stability | <3 meters from origin |
| Text angular size | 1.33 degrees minimum |
| Comfort FOV | 60 degrees horizontal |
| Content placement | 40° below to 10° above |

---

## Cybersickness Measurement (SSQ)

- 16 items, 0-3 scale (none, slight, moderate, severe)
- Three subscales: Nausea, Oculomotor, Disorientation

**Limitation:** Not optimal for commercial HMD VR; disorientation predominant (not nausea).

**Alternatives:** CSQ, VRSQ, CSQ-VR (better internal consistency)

---

## Sources

- IEEE VR Conference Proceedings
- ACM CHI Conference Proceedings
- Meta MR Design Guidelines
- Apple Human Interface Guidelines - Spatial Layout
- Microsoft Mixed Reality Design Guidance
- W3C XR Accessibility User Requirements
- iGroup Presence Questionnaire
