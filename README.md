# Physics Simulation

A physics-based ball simulation featuring dynamic collision detection, synchronized audio synthesis, and automated video generation. Built with Pygame and Box2D.

## Demo

<video src="output.mp4" width="320" height="568" controls></video>

## Overview

This project simulates balls bouncing within a series of rotating concentric rings. When a ball passes through a ring's opening, it triggers a chain reaction—spawning new balls and creating an emergent, visually captivating physics display. The simulation includes procedurally generated audio that synchronizes with collision events and exports to high-quality video.

## Key Features

- **Real-time Physics Simulation**: Powered by Box2D with custom frictionless, perfectly elastic collisions
- **Dynamic Ring System**: Six independently rotating rings with configurable angular velocity and gap sizes
- **Procedural Audio Engine**: Synchronized sound effects triggered by physics events with WAV synthesis and mixing
- **Automated Video Export**: Frame-by-frame rendering pipeline integrated with FFmpeg for 1080x1920 60FPS output
- **Emergent Gameplay**: Recursive ball spawning mechanics create evolving simulation patterns
- **Visual Effects**: HSL color-cycling rings with smooth gradient transitions

## Technical Stack

| Component | Technology |
|-----------|------------|
| Physics Engine | Box2D (pybox2d) |
| Rendering | Pygame |
| Audio Processing | NumPy, PyAudio, Wave |
| Video Encoding | OpenCV, FFmpeg |
| Language | Python 3 |

## Architecture

```
Game.py          → Main simulation loop, ball spawning logic
Ball.py          → Physics body wrapper with collision fixtures
Ring.py          → Rotating edge-chain obstacles with openings
MyContactListener.py → Box2D collision event detection
Sounds.py        → Event-driven audio synthesis and WAV export
export_video.py  → Headless rendering pipeline
utils.py         → Coordinate conversion, HSL color utilities
```

## Physics Implementation

- **Sub-stepping**: Fixed timestep with accumulator pattern for deterministic physics
- **Contact Detection**: Custom `b2ContactListener` for ring-ball collision events
- **Coordinate Mapping**: PPM (pixels-per-meter) conversion between screen and physics world
- **Restitution**: Perfectly elastic collisions (restitution=1.0) for perpetual motion

## Audio System

The audio engine captures collision events during simulation and:
1. Records timestamps of each collision
2. Loads and resamples sound assets to a consistent 44.1kHz
3. Mixes multiple simultaneous events with proper time alignment
4. Exports synchronized WAV audio for video muxing

## Video Export Pipeline

```python
# Headless SDL rendering at 4x simulation speed
# Frame extraction → PNG sequence → FFmpeg encode with AAC audio
# Output: 1080x1920 60FPS MP4 (portrait orientation)
```

## Running the Simulation

```bash
# Install dependencies
pip install pygame pybox2d numpy opencv-python pyaudiowpatch

# Run interactive simulation
python Game.py

# Export video (headless rendering)
python export_video.py
```

## Skills Demonstrated

- **Physics Programming**: Rigid body dynamics, collision detection, constraint solving
- **Real-time Systems**: Fixed timestep loops, event-driven architecture
- **Audio DSP**: Sample-rate conversion, multi-track mixing, WAV format handling
- **Graphics Programming**: Double-buffered rendering, coordinate transforms
- **Pipeline Development**: Automated media generation, FFmpeg integration
- **Object-Oriented Design**: Component-based entity system, separation of concerns

## Project Structure

```
├── Game.py                 # Main simulation controller
├── Ball.py                 # Ball physics entity
├── Ring.py                 # Rotating obstacle rings
├── MyContactListener.py    # Collision event handler
├── Sounds.py               # Audio synthesis engine
├── AudioRecorder.py        # System audio capture (loopback)
├── export_video.py         # Video generation script
├── utils.py                # Shared utilities singleton
├── assets/                 # Sound effect files
├── frames/                 # Rendered frame output
└── output.mp4              # Demo video (generated)
```

---

*Developed as a showcase of real-time simulation, physics programming, and multimedia pipeline development.*