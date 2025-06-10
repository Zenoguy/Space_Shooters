# 🚀 Space Shooter Game

A classic arcade-style space shooter game built with Python and Pygame, featuring multiple enemy types, power-ups, and progressive difficulty levels.


## Download 
linux -> https://drive.google.com/file/d/1glHPw6BS_xvznkOcH-lrjffHMVsdtlQ9/view?usp=sharing


## Features

- **Classic Space Shooter Gameplay**: Control your spaceship and defend against waves of enemies
- **Multiple Enemy Types**: 
  - Regular enemies (Red, Green, Blue ships) that shoot lasers
  - Kamikaze enemies that dive-bomb toward the player
- **Progressive Difficulty**: Enemy waves increase in size and speed as you advance through levels
- **Health System**: Player health bar with collision damage
- **Score Tracking**: Points system with persistent high score storage
- **Sound Effects**: Laser sounds, explosion effects, and background music
- **Pause Menu**: Full pause functionality with settings options
- **Customizable Audio**: Toggle sound effects and music on/off

## Controls

### Gameplay
- **Movement**: WASD keys or Arrow keys
- **Shoot**: Spacebar
- **Pause**: Escape key

### Menus
- **Arrow Keys**: Navigate menu options
- **Enter**: Select menu option
- **Escape**: Resume game (from pause menu)

### Game Over Screen
- **R**: Restart game
- **M**: Return to main menu
- **Q**: Quit game

## Installation

### Prerequisites
- Python 3.6 or higher
- Pygame library

### Setup
1. Install Python from [python.org](https://python.org)
2. Install Pygame:
   ```bash
   pip install pygame
   ```
3. Download or clone the game files
4. Ensure you have the required assets (see Asset Requirements below)

## Asset Requirements

The game requires the following asset folders and files:

### assets/ folder:
- `pixel_ship_red_small.png` - Red enemy ship
- `pixel_ship_green_small.png` - Green enemy ship  
- `pixel_ship_blue_small.png` - Blue enemy ship
- `pixel_ship_yellow.png` - Player ship
- `Kamikaze.png` - Kamikaze enemy ship
- `pixel_laser_red.png` - Red laser
- `pixel_laser_green.png` - Green laser
- `pixel_laser_blue.png` - Blue laser
- `pixel_laser_yellow.png` - Player laser
- `background-black.png` - Game background

### bgm/ folder:
- `laser.mp3` - Laser sound effect
- `explosion.mp3` - Explosion sound effect
- `MainScreen.mp3` - Main menu music
- `Loading_Screen.mp3` - Pause menu music
- `8bit-spaceshooter.mp3` - Game background music

## How to Play

1. Run the game:
   ```bash
   python space_shooter.py
   ```
2. Click anywhere on the main menu to start
3. Use WASD or arrow keys to move your yellow spaceship
4. Press Spacebar to shoot lasers at incoming enemies
5. Avoid enemy lasers and collision damage
6. Survive waves of enemies to advance to higher levels
7. Watch out for kamikaze enemies (appear after level 2) - they'll dive toward you!

## Game Mechanics

### Scoring
- Regular enemies: 10 points each
- Kamikaze enemies: 20 points each
- High scores are automatically saved

### Health & Lives
- Player starts with 100 health and 5 lives
- Collision with regular enemies: 10 damage
- Collision with kamikaze enemies: 50 damage
- Lose a life when enemies reach the bottom of the screen
- Game over when health reaches 0 or all lives are lost

### Enemy Behavior
- **Regular Enemies**: Move downward and occasionally shoot lasers
- **Kamikaze Enemies**: Initially move downward, then dive toward player position when close enough
- Enemy speed and spawn count increase with each level

## Configuration

The game includes various configurable parameters at the top of the code:

- `INITIAL_LIVES`: Starting number of lives (default: 5)
- `PLAYER_VEL`: Player movement speed (default: 5)
- `ENEMY_INITIAL_VEL`: Enemy movement speed (default: 1)
- `PLAYER_HEALTH_MAX`: Player starting health (default: 100)
- Various damage values and cooldown timers

## File Structure

```
space_shooter/
├── space_shooter.py          # Main game file
├── highscore.txt            # High score storage (auto-generated)
├── assets/                  # Image assets folder
│   ├── pixel_ship_*.png
│   ├── pixel_laser_*.png
│   ├── Kamikaze.png
│   └── background-black.png
└── bgm/                     # Audio assets folder
    ├── laser.mp3
    ├── explosion.mp3
    ├── MainScreen.mp3
    ├── Loading_Screen.mp3
    └── 8bit-spaceshooter.mp3
```

## Troubleshooting

### Common Issues

**Game won't start / Missing assets error**
- Ensure all required image and sound files are in their respective folders
- Check that file names match exactly (case-sensitive on some systems)

**No sound**
- Verify audio files are in the `bgm/` folder
- Check that your system audio is working
- Try toggling sound settings in the pause menu

**Performance issues**
- Close other applications to free up system resources
- The game runs at 60 FPS by default

### System Requirements
- Python 3.6+
- Pygame 2.0+
- Minimum 4MB free disk space for assets
- Audio device for sound effects and music

## Credits

Built with Python and Pygame. This is a classic arcade-style game inspired by traditional space shooter games.

Basic game concept and structure based on the tutorial by **Tech With Tim**. Enhanced with additional features including kamikaze enemies, improved UI, pause menu, and sound system.

## License

This project is for educational and entertainment purposes. Please ensure you have appropriate licenses for any assets used.
