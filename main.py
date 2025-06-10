#THIS IS A 7"69" LINES OF AMALGAMAATION OF STUPDITY, You can CHANGE what you want to, its very modular B)
import pygame
import os
import time
import random
import math
import sys 


# --- PYGAME INITIALIZATION (CRITICAL: MUST BE FIRST) ---
# Initialize pygame modules
# This is crucial for the mixer to be ready before any sound files are loaded.
pygame.init()
pygame.font.init()
pygame.mixer.init()

# --- GLOBAL GAME SETTINGS AND ASSET LOADING ---
# Set up display
WIDTH, HEIGHT = 768 , 768
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# Paths
ASSETS_DIR = "assets"
HIGH_SCORE_FILE = "highscore.txt"

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Game parameters (using constants for easy modification)
INITIAL_LIVES = 5
PLAYER_VEL = 5
ENEMY_INITIAL_VEL = 1
LASER_PLAYER_VEL = -5 # Player lasers move up
LASER_ENEMY_VEL = 3 # Enemy lasers move down
KAMIKAZE_SPEED = 3
KAMIKAZE_DIVE_SPEED = 6
KAMIKAZE_WARNING_DURATION = 60 # 1 second at 60 FPS (assuming 60 FPS)
ENEMY_SHOOT_CHANCE = 3*60 # 1 in 120 frames chance for enemy to shoot
PLAYER_HEALTH_MAX = 100
ENEMY_HEALTH = 100
KAMIKAZE_HEALTH = 50
ENEMY_COLLISION_DAMAGE = 10
KAMIKAZE_COLLISION_DAMAGE = 50
PLAYER_LASER_DAMAGE = 10

MIN_ENEMY_DISTANCE = 80 # Minimum distance between all enemy ships on spawn
MAX_SPAWN_ATTEMPTS = 50 # Max attempts to find a clear spawn spot for new enemies

# Cooldowns (in frames)
PLAYER_COOLDOWN = 30
ENEMY_COOLDOWN = 30


# Load images
def load_image(filename):
    """Load image from the assets directory"""
    return pygame.image.load(resource_path(os.path.join("assets", filename)))

RED_SPACE_SHIP = load_image("pixel_ship_red_small.png")
GREEN_SPACE_SHIP = load_image("pixel_ship_green_small.png")
BLUE_SPACE_SHIP = load_image("pixel_ship_blue_small.png")
YELLOW_SPACE_SHIP = load_image("pixel_ship_yellow.png")
KAMIKAZE_SHIP = load_image("Kamikaze.png") # Loaded here to get its width for spawning

RED_LASER = load_image("pixel_laser_red.png")
GREEN_LASER = load_image("pixel_laser_green.png")
BLUE_LASER = load_image("pixel_laser_blue.png")
YELLOW_LASER = load_image("pixel_laser_yellow.png")

BG = pygame.transform.scale(load_image("background-black.png"), (WIDTH, HEIGHT))

# Load sound effects

LASER_SOUND = pygame.mixer.Sound(resource_path(os.path.join("bgm", "laser.mp3")))
EXPLOSION_SOUND = pygame.mixer.Sound(resource_path(os.path.join("bgm", "explosion.mp3")))

# Music files (paths only, loaded dynamically when played)

MAIN_MENU_MUSIC = resource_path(os.path.join("bgm", "MainScreen.mp3"))
PAUSE_MUSIC = resource_path(os.path.join("bgm", "Loading_Screen.mp3"))
GAME_MUSIC = resource_path(os.path.join("bgm", "8bit-spaceshooter.mp3"))


# Global sound/music toggle settings
SOUND_ENABLED = True
MUSIC_ENABLED = True

# --- UTILITY FUNCTIONS ---
def play_music(music_file, loops=-1, volume=0.7):
    """Play background music if music is enabled."""
    if MUSIC_ENABLED:
        try:
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
        except pygame.error:
            print(f"Error: Could not load or play music file: {music_file}")

def stop_music():
    """Stop background music."""
    pygame.mixer.music.stop()

def play_sfx(sound):
    """Play a sound effect if SFX is enabled."""
    if SOUND_ENABLED:
        sound.play()

def load_high_score():
    """Loads the high score from a file."""
    if os.path.exists(HIGH_SCORE_FILE):
        with open(HIGH_SCORE_FILE, "r") as file:
            try:
                return int(file.read())
            except ValueError: # Handle cases where file might contain non-integer data
                return 0
    return 0

def save_high_score(score):
    """Saves the current high score to a file."""
    with open(HIGH_SCORE_FILE, "w") as file:
        file.write(str(score))

def is_far_enough(x, y, others):
    """
    Checks if a new position (x, y) is far enough from existing objects
    to prevent overlapping spawns.
    """
    for enemy in others:
        # Calculate distance from the center of the new potential enemy
        # to the center of existing enemies. Using a rough estimate for
        # ship size (e.g., 50px offset to approximate center).
        dist = math.hypot(
            (x + 50) - (enemy.x + enemy.get_width() / 2),
            (y + 50) - (enemy.y + enemy.get_height() / 2)
        )
        if dist < MIN_ENEMY_DISTANCE:
            return False
    return True

def collide(obj1, obj2):
    """Checks for collision between two Pygame objects using masks."""
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None

# --- GAME OBJECT CLASSES ---
class Laser:
    """Represents a laser projectile fired by ships."""
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        """Draws the laser on the game window."""
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        """Moves the laser by the given velocity."""
        self.y += vel

    def off_screen(self, height_limit):
        """Checks if the laser has moved off screen."""
        return not (0 <= self.y <= height_limit)

    def collision(self, obj):
        """Checks if this laser is colliding with another object."""
        return collide(self, obj)

class Ship:
    """Base class for all ships (Player and Enemies)."""
    COOLDOWN = 30 # Default cooldown between shots in frames

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        """Draws the ship and its lasers on the game window."""
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        """
        Moves the ship's lasers and handles collisions with a single target object.
        Used for enemy lasers hitting the player.
        """
        self.cooldown()
        for laser in self.lasers[:]: # Iterate over a copy to allow modification
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= PLAYER_LASER_DAMAGE # Lasers deal a fixed damage
                play_sfx(EXPLOSION_SOUND) # Play explosion sound on hit
                if laser in self.lasers: # Ensure laser is still in list before removing
                    self.lasers.remove(laser)

    def cooldown(self):
        """Manages the cooldown timer for shooting."""
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        """Fires a laser if the cooldown allows."""
        if self.cool_down_counter == 0:
            # Position the laser to be centered on the ship
            laser = Laser(self.x + self.get_width()//2 - self.laser_img.get_width()//2, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        """Returns the width of the ship's image."""
        return self.ship_img.get_width()

    def get_height(self):
        """Returns the height of the ship's image."""
        return self.ship_img.get_height()

class Player(Ship):
    """Represents the player's spaceship."""
    def __init__(self, x, y, health=PLAYER_HEALTH_MAX):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.score = 0
        self.COOLDOWN = PLAYER_COOLDOWN # Player specific cooldown

    def move_lasers(self, vel, enemies_list, kamikaze_enemies_list):
        """
        Moves player's lasers and handles collisions with both regular
        and kamikaze enemies.
        """
        self.cooldown()
        for laser in self.lasers[:]:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                hit_something = False
                # Check collision with regular enemies
                for enemy in enemies_list[:]:
                    if laser.collision(enemy):
                        enemies_list.remove(enemy)
                        play_sfx(EXPLOSION_SOUND)
                        self.score += 10 # Regular enemies worth 10 points
                        hit_something = True
                        break # Laser can only hit one enemy

                # If laser didn't hit a regular enemy, check kamikaze enemies
                if not hit_something:
                    for kamikaze in kamikaze_enemies_list[:]:
                        if laser.collision(kamikaze):
                            kamikaze_enemies_list.remove(kamikaze)
                            play_sfx(EXPLOSION_SOUND)
                            self.score += 20 # Kamikaze enemies worth more points
                            hit_something = True
                            break # Laser can only hit one enemy

                if hit_something and laser in self.lasers: # Remove laser if it hit anything
                    self.lasers.remove(laser)
    
    def shoot(self):
        """Fires a player laser and plays sound."""
        if self.cool_down_counter == 0:
            laser = Laser(self.x + self.get_width()//2 - self.laser_img.get_width()//2, self.y, self.laser_img)
            self.lasers.append(laser)
            play_sfx(LASER_SOUND) # Play laser sound effect
            self.cool_down_counter = 1

    def draw(self, window):
        """Draws the player ship and its health bar."""
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        """Draws the player's health bar below the ship."""
        # Red background for health bar
        pygame.draw.rect(window, RED, (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        # Green foreground for current health
        pygame.draw.rect(window, GREEN, (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Enemy(Ship):
    """Represents a regular enemy spaceship."""
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=ENEMY_HEALTH):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.COOLDOWN = ENEMY_COOLDOWN # Enemy specific cooldown

    def move(self, vel):
        """Moves the enemy ship downwards."""
        self.y += vel

    def shoot(self):
        """Fires an enemy laser (without sound in this context)."""
        # Overrides base Ship.shoot to ensure appropriate laser image
        if self.cool_down_counter == 0:
            laser = Laser(self.x + self.get_width()//2 - self.laser_img.get_width()//2, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

class KamikazeEnemy(Ship):
    """Represents a kamikaze enemy that dives towards the player."""
    def __init__(self, x, y, health=KAMIKAZE_HEALTH):
        super().__init__(x, y, health)
        self.ship_img = KAMIKAZE_SHIP
        self.laser_img = None  # Kamikaze ships don't shoot lasers
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.target_x = None
        self.target_y = None
        self.speed = KAMIKAZE_SPEED
        self.dive_speed = KAMIKAZE_DIVE_SPEED
        self.is_diving = False
        self.warning_timer = 0
        self.warning_duration = KAMIKAZE_WARNING_DURATION

    def set_target(self, player_x, player_y):
        """Sets the target position for the kamikaze dive."""
        self.target_x = player_x
        self.target_y = player_y
        self.is_diving = True
        self.warning_timer = self.warning_duration

    def move(self, vel, player):
        """Moves the kamikaze enemy, either normal descent or diving towards player."""
        if not self.is_diving:
            # Normal movement downward - slightly faster than regular enemies
            self.y += vel + 1
            # Check if should start diving (when close to player vertically)
            # Added a small random chance to prevent all kamikazes from diving at once.
            if self.y > player.y - 200 and self.y < player.y and random.random() < 0.01:
                self.set_target(player.x + player.get_width()//2, player.y + player.get_height()//2)
        else:
            # Diving toward target - much faster
            if self.target_x is not None and self.target_y is not None:
                # Calculate direction to target
                dx = self.target_x - (self.x + self.get_width()//2)
                dy = self.target_y - (self.y + self.get_height()//2)

                # Normalize the direction vector and apply dive speed
                distance = (dx**2 + dy**2)**0.5
                if distance > 0: # Avoid division by zero
                    self.x += (dx / distance) * self.dive_speed
                    self.y += (dy / distance) * self.dive_speed

            # Reduce warning timer (for visual flashing)
            if self.warning_timer > 0:
                self.warning_timer -= 1

    def draw(self, window):
        """Draws the kamikaze ship and a warning indicator when diving."""
        window.blit(self.ship_img, (self.x, self.y))

        # Draw flashing red warning indicator when diving
        if self.is_diving and self.warning_timer > 0:
            if self.warning_timer % 10 < 5: # Flashes every 10 frames (5 frames on, 5 frames off)
                warning_surface = pygame.Surface((self.get_width() + 20, self.get_height() + 20))
                warning_surface.set_alpha(100) # Semi-transparent
                warning_surface.fill(RED) # Red color
                window.blit(warning_surface, (self.x - 10, self.y - 10))

        # Lasers are not drawn as kamikaze ships don't shoot
        # The loop "for laser in self.lasers" would be empty here.

    def shoot(self):
        """Kamikaze ships do not shoot, so this method does nothing."""
        pass

# --- MENU FUNCTIONS ---
def pause_menu():
    """
    Displays the pause menu, allows toggling SFX/Music, and handles menu navigation.
    Returns the selected action ("resume", "new_game", "quit").
    """
    global SOUND_ENABLED, MUSIC_ENABLED # Access global sound settings to modify them
    
    play_music(PAUSE_MUSIC, -1, 0.5) # Play pause menu music

    pause_font = pygame.font.SysFont("comicsans", 60)
    option_font = pygame.font.SysFont("comicsans", 40)
    
    # Options list, dynamically updated for SFX/Music toggle
    options = [
        "RESUME",
        "NEW GAME",
        "QUIT",
        f"SFX: {'ON' if SOUND_ENABLED else 'OFF'}",
        f"MUSIC: {'ON' if MUSIC_ENABLED else 'OFF'}"
    ]
    selected_option = 0 # Index of the currently selected option

    while True:
        # Draw background and a semi-transparent overlay to dim the game
        WIN.blit(BG, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128) # 128 out of 255 for transparency
        overlay.fill(BLACK)
        WIN.blit(overlay, (0, 0))

        # Draw "GAME PAUSED" title
        pause_label = pause_font.render("GAME PAUSED", 1, WHITE)
        WIN.blit(pause_label, (WIDTH/2 - pause_label.get_width()/2, 150))

        # Draw menu options, highlighting the selected one
        for i, option in enumerate(options):
            color = YELLOW if i == selected_option else WHITE
            option_label = option_font.render(option, 1, color)
            y_pos = 280 + i * 50 # Spacing between options
            WIN.blit(option_label, (WIDTH/2 - option_label.get_width()/2, y_pos))
        
        # Draw control instructions
        controls_font = pygame.font.SysFont("comicsans", 30)
        controls_label = controls_font.render("Use Arrow Keys and Enter to select", 1, GRAY)
        WIN.blit(controls_label, (WIDTH/2 - controls_label.get_width()/2, 580))
        
        pygame.display.update() # Update the display to show menu

        # Event handling for menu navigation
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit" # User closed the window

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "resume" # Escape key to resume
                elif event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                elif event.key == pygame.K_RETURN: # Enter key to select
                    if selected_option == 0:  # RESUME
                        return "resume"
                    elif selected_option == 1:  # NEW GAME
                        return "new_game"
                    elif selected_option == 2:  # QUIT
                        return "quit"
                    elif selected_option == 3:  # SFX TOGGLE
                        SOUND_ENABLED = not SOUND_ENABLED # Toggle global SFX setting
                        options[3] = f"SFX: {'ON' if SOUND_ENABLED else 'OFF'}" # Update option text
                    elif selected_option == 4:  # MUSIC TOGGLE
                        MUSIC_ENABLED = not MUSIC_ENABLED # Toggle global Music setting
                        options[4] = f"MUSIC: {'ON' if MUSIC_ENABLED else 'OFF'}" # Update option text
                        if not MUSIC_ENABLED:
                            stop_music() # Stop music if turned off
                        else:
                            play_music(PAUSE_MUSIC, -1, 0.5) # Resume pause music if turned on

def main_menu():
    """
    Displays the main menu of the game.
    Starts the main game loop when the player clicks the mouse.
    """
    play_music(MAIN_MENU_MUSIC, -1, 0.5) # Play main menu music
    title_font = pygame.font.SysFont("comicsans", 70)
    subtitle_font = pygame.font.SysFont("comicsans", 30)
    run = True
    while run:
        WIN.blit(BG, (0,0)) # Draw background

        # Render and draw menu text
        title_label = title_font.render("SPACE SHOOTER", 1, WHITE)
        subtitle_label = subtitle_font.render("Press the mouse to begin...", 1, WHITE)
        controls_label = subtitle_font.render("Controls: WASD to move, SPACE to shoot, ESC to pause", 1, GRAY)
        
        WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 300))
        WIN.blit(subtitle_label, (WIDTH/2 - subtitle_label.get_width()/2, 400))
        WIN.blit(controls_label, (WIDTH/2 - controls_label.get_width()/2, 500))
        
        pygame.display.update() # Update the display

        # Event handling for main menu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_music()
                run = False # Exit main menu loop if window is closed
            if event.type == pygame.MOUSEBUTTONDOWN:
                stop_music()
                main() # Start the main game loop
                return # Exit main menu loop after starting game
    stop_music() # Stop music if main menu loop exits (e.g., via QUIT)
    pygame.quit() # Quit pygame after main menu loop finishes

# --- MAIN GAME LOOP ---
def main():
    """
    The core game loop. Manages game state, enemy spawning, player input,
    collisions, and drawing.
    """
    global SOUND_ENABLED, MUSIC_ENABLED # Access global sound settings
    
    play_music(GAME_MUSIC, -1, 0.6) # Start game music when entering main game loop
    
    run = True
    FPS = 60
    level = 0
    lives = INITIAL_LIVES
    main_font = pygame.font.SysFont("comicsans", 40)
    lost_font = pygame.font.SysFont("comicsans", 60)

    enemies = []
    kamikaze_enemies = []
    wave_length = 0
    enemy_vel = ENEMY_INITIAL_VEL
    player_vel = PLAYER_VEL

    player = Player(300, 630) # Initial player position

    clock = pygame.time.Clock() # For controlling frame rate

    lost = False # Game over state
    lost_count = 0 # Timer for "You Lost!!" screen
    paused = False # Game paused state
    remaining_time = 5
    high_score = load_high_score() # Load high score at the start of the game

    def redraw_window():
        """Draws all game elements on the screen."""
        WIN.blit(BG, (0,0)) # Draw background

        # Draw UI text (Lives, Level, Score, High Score, Sound/Music status)
        lives_label = main_font.render(f"Lives: {lives}", 1, WHITE)
        level_label = main_font.render(f"Level: {level}", 1, WHITE)
        score_label = main_font.render(f"Score: {player.score}", 1, WHITE)
        high_score_label = main_font.render(f"High Score: {high_score}", 1, WHITE)
        sound_label = main_font.render(f"SFX: {'ON' if SOUND_ENABLED else 'OFF'} | Music: {'ON' if MUSIC_ENABLED else 'OFF'}", 1, WHITE)

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))
        WIN.blit(score_label, (10, 50))
        WIN.blit(high_score_label, (WIDTH - high_score_label.get_width() - 10, 50))
        WIN.blit(sound_label, (10, 90))

        # Draw all enemies and kamikaze enemies
        for enemy in enemies:
            enemy.draw(WIN)
        for kamikaze in kamikaze_enemies:
            kamikaze.draw(WIN)

        player.draw(WIN) # Draw player ship

        # Display "You Lost!!" screen if game is over
        if lost:
            lost_label = lost_font.render("You Lost!!", 1, WHITE)
            final_score_label = main_font.render(f"Final Score: {player.score}", 1, WHITE)
            high_score_display = main_font.render(f"High Score: {high_score}", 1, WHITE)
            
            restart_label = main_font.render(f"Press R to restart ", 1, WHITE)
            menu_label = main_font.render(f"Press M to return to menu", 1, WHITE)
            quit_label = main_font.render(f"Press Q to quit", 1, WHITE)
            
            center_x = WIDTH // 2 - lost_label.get_width() // 2

            WIN.blit(lost_label, (center_x, 250))
            WIN.blit(final_score_label, (center_x, 300))
            WIN.blit(high_score_display, (center_x, 350))
            WIN.blit(restart_label, (center_x, 400))
            WIN.blit(menu_label, (center_x, 450))
            WIN.blit(quit_label, (center_x, 500))




            
        pygame.display.update() # Update the entire screen

    # Main game loop
    while run:
        clock.tick(FPS) # Cap frame rate

        if not paused:
            redraw_window() # Only redraw if not paused

        # Check for game over condition
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
            if player.score > high_score:
                high_score = player.score
                save_high_score(high_score) # Save new high score

        # Handle game over state (waiting for restart/quit)
        if lost:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        stop_music()
                        main()  # Restart the game
                        return   # Exit current main loop
                    elif event.key == pygame.K_q:
                        stop_music()
                        run = False
                    elif event.key == pygame.K_m:
                        stop_music()
                        main_menu()  # Return to main menu
                        return        # Exit current main loop
            continue  # Skip normal game logic if game is over


        # Spawn new waves of enemies if all are cleared
        if len(enemies) == 0 and len(kamikaze_enemies) == 0:
            level += 1
            wave_length += 4 # Increase number of enemies per wave

            all_enemies = [] # Temporarily hold all enemies to check for spawn overlaps

            # Spawn regular enemies
            for _ in range(wave_length):
                attempts = 0
                while True: # Loop until a valid spawn position is found
                    x = random.randrange(50, WIDTH - 100) # Keep initial x within reasonable bounds
                    y = random.randrange(-300*level, -100) # Spawn well above the screen
                    if is_far_enough(x, y, all_enemies) or attempts > MAX_SPAWN_ATTEMPTS:
                        break # Found a spot or max attempts reached
                    attempts += 1
                enemy = Enemy(x, y, random.choice(["red", "blue", "green"]))
                enemies.append(enemy)
                all_enemies.append(enemy)

            # Spawn kamikaze enemies (after level 2)
            if level >= 2:
                kamikaze_count = random.randint(1, min(3, level // 2 + 1)) # 1 to 3 kamikazes, scales with level
                for _ in range(kamikaze_count):
                    attempts = 0
                    while True:
                        # Calculate maximum x-coordinate to ensure the entire kamikaze ship
                        # is visible on screen, with a 50px padding from the right edge.
                        max_x = WIDTH - KAMIKAZE_SHIP.get_width() - 50
                        x = random.randrange(50, max_x) # Adjusted upper bound for X
                        
                        y = random.randrange(-300*level, -100) # Spawn above screen
                        if is_far_enough(x, y, all_enemies) or attempts > MAX_SPAWN_ATTEMPTS:
                            break
                        attempts += 1
                    kamikaze = KamikazeEnemy(x, y)
                    kamikaze_enemies.append(kamikaze)
                    all_enemies.append(kamikaze)


        # Event handling (Keyboard input and Quit)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False # Stop game loop if window is closed
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_k]:
                    paused = True # Set game to paused state
                    if MUSIC_ENABLED:
                        paused_music_pos = pygame.mixer.music.get_pos() / 1000.0  # Convert ms to seconds
                        pygame.mixer.music.stop()
                        play_music(PAUSE_MUSIC, -1, 0.5)

                    action = pause_menu() # Enter the pause menu loop
                    
                    # Handle action returned from pause menu
                    if action == "resume":
                        paused = False
                        if MUSIC_ENABLED:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load(GAME_MUSIC)
                            pygame.mixer.music.play(-1, start=paused_music_pos)

                    elif action == "new_game":
                        stop_music()
                        main() # Start a new game
                        return # Exit current main loop
                    elif action == "quit":
                        stop_music()
                        run = False # Quit game
                    paused = False # Ensure paused state is reset after menu interaction

        # --- GAME LOGIC (ONLY IF NOT PAUSED) ---
        if not paused:
            # Player movement based on WASD keys or arrow keys
            keys = pygame.key.get_pressed()

            # Move Left
            if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and player.x - player_vel > 0:
                player.x -= player_vel

            # Move Right
            if (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and player.x + player_vel + player.get_width() < WIDTH:
                player.x += player_vel

            # Move Up
            if (keys[pygame.K_w] or keys[pygame.K_UP]) and player.y - player_vel > 0:
                player.y -= player_vel

            # Move Down (with padding for UI like health bar)
            if (keys[pygame.K_s] or keys[pygame.K_DOWN]) and player.y + player_vel + player.get_height() + 15 < HEIGHT:
                player.y += player_vel

            # Shoot
            if keys[pygame.K_SPACE]:
                player.shoot()


            # Move and update regular enemies
            for enemy in enemies[:]:
                enemy.move(enemy_vel) # Move enemy downwards
                enemy.move_lasers(LASER_ENEMY_VEL, player) # Move enemy lasers and check collision with player

                # Randomly make enemy shoot
                if random.randrange(0, ENEMY_SHOOT_CHANCE) == 1:
                    enemy.shoot()

                # Handle enemy collision with player
                if collide(enemy, player):
                    player.health -= ENEMY_COLLISION_DAMAGE
                    play_sfx(EXPLOSION_SOUND)
                    enemies.remove(enemy) # Remove enemy after collision
                elif enemy.y + enemy.get_height() > HEIGHT: # Enemy went off screen
                    lives -= 1 # Lose a life
                    enemies.remove(enemy)
            
            # Move and update kamikaze enemies
            for kamikaze in kamikaze_enemies[:]:
                kamikaze.move(enemy_vel, player) # Kamikaze targets player
                
                # Handle kamikaze collision with player
                if collide(kamikaze, player):
                    player.health -= KAMIKAZE_COLLISION_DAMAGE # Kamikaze deals more damage
                    play_sfx(EXPLOSION_SOUND)
                    kamikaze_enemies.remove(kamikaze) # Remove kamikaze after collision
                elif kamikaze.y + kamikaze.get_height() > HEIGHT: # Kamikaze went off screen
                    lives -= 1
                    kamikaze_enemies.remove(kamikaze)
                    
                # --- Laser vs Laser Collision ---
            for enemy in enemies:
                for enemy_laser in enemy.lasers[:]:
                    for player_laser in player.lasers[:]:
                        if enemy_laser.collision(player_laser):
                            if enemy_laser in enemy.lasers:
                                enemy.lasers.remove(enemy_laser)
                            if player_laser in player.lasers:
                                player.lasers.remove(player_laser)
                            break  # Break inner loop once collision occurs

            # Move player's lasers and handle collisions with enemies
            player.move_lasers(LASER_PLAYER_VEL, enemies, kamikaze_enemies)

    # --- GAME END ---
    stop_music() # Stop any playing music
    pygame.quit() # Uninitialize pygame modules

# --- GAME START ---
if __name__ == "__main__":
    main_menu() # Start the game from the main menu
