import os
import shutil
import subprocess
import pygame
from Game import Game
from utils import utils
from Sounds import sounds
import numpy as np
import cv2
import Game as GameModule

os.environ["SDL_VIDEODRIVER"] = "dummy"

FPS = 60
SIMULATION_SPEED = 4.0  # 1.0 = normal speed
DT = SIMULATION_SPEED / FPS
DURATION_SECONDS = 30
TOTAL_FRAMES = FPS * DURATION_SECONDS
WIDTH, HEIGHT = 1080, 1920

surface = pygame.Surface((WIDTH, HEIGHT))

utils.dt = DT
GameModule.DT = DT

# Initialize the game
game = Game()

if os.path.exists("frames"):
    shutil.rmtree("frames")

os.makedirs("frames", exist_ok=True)

if os.path.exists("collision_sounds.wav"):
    os.remove("collision_sounds.wav")
    

print(f"Rendering {TOTAL_FRAMES} frames at {FPS} FPS ({DURATION_SECONDS}s)...")

wait_time = 0
for i in range(TOTAL_FRAMES):
    if len(game.rings) == 0:
        wait_time += 1
        if wait_time >= FPS * 2: # 2 seconds after finish
            break
    
    video_time = i / FPS  # Time in video timeline
    
    game.update()
    
    game.simulation_time = video_time
    game._time_override = True  # Flag to prevent auto-increment
    
    # --- render ---
    surface.fill((23, 23, 23))
    game.draw(surface)
    
    # --- extract pixels ---
    frame = pygame.surfarray.array3d(surface)
    frame = np.transpose(frame, (1, 0, 2))
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    cv2.imwrite(f"frames/frame_{i:05d}.png", frame)
    
    if (i + 1) % (FPS * 2) == 0:  # Print every 2 seconds
        print(f"Progress: {i + 1}/{TOTAL_FRAMES} frames ({(i + 1) / FPS:.1f}s)")

# Save collision sounds to file
print("Saving collision sounds...")
sounds.save_recording(duration_seconds=DURATION_SECONDS)

# Create final video
print("Creating final video...")
subprocess.run(
    f"ffmpeg -framerate {FPS} -i frames/frame_%05d.png -i collision_sounds.wav -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest output.mp4 -y",
    shell=True
)

print(f"Done! Exported {TOTAL_FRAMES} frames and collision sounds to output.mp4")