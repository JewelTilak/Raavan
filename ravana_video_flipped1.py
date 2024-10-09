import cv2
import mediapipe as mp
import pygame
import random
import time
from moviepy.editor import VideoFileClip

# Initialize MediaPipe Hands for hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Pygame Initialization
pygame.init()
pygame.mixer.init()

# Set up the game window
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption('Ravana-Dahan')

# Load background music and sound effects
pygame.mixer.music.load('ravanbgm.mp3')
pygame.mixer.music.play(-1)
hit_sound = pygame.mixer.Sound('hit01.wav')
vic_sound = pygame.mixer.Sound('Win.wav')

# Load images for the game
mole_image = pygame.image.load(r'ravana.png').convert_alpha()
mole_image = pygame.transform.scale(mole_image, (200, 200))
fire_image = pygame.image.load(r'Fire.png').convert_alpha()
fire_image = pygame.transform.scale(fire_image, (30, 30))
background_image = pygame.image.load(r'scary_forest_bg.png')
background_image = pygame.transform.scale(background_image, (800, 600))

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Mole game variables
mole_radius = 55
mole_pos = [random.randint(mole_radius, 800 - mole_radius), random.randint(mole_radius, 600 - mole_radius)]
score = 0
mole_counter = 0

# Timing variables
mole_appearance_time = 2  # Time between mole appearances
last_mole_time = time.time()
game_duration = 60  # Total game duration
start_time = time.time()

# Webcam capture initialization
cap = cv2.VideoCapture(0)

# Messages displayed upon hitting the mole
hit_messages = [
    "Negativity Destroyed!",
    "Laziness Eliminated!",
    "Down with Anger!",
    "Lust - No More!",
    "Greed Tamed!",
    "Jealousy Killed!",
    "Envy Extinguished!",
    "Delusion Destroyed!",
    "Selfishness Sacrificed!",
    "Evil eliminated!"
]
hit_message_index = 0  # Index for hit messages

# Function to fade out the screen
def fade_out(screen, duration):
    fade_surface = pygame.Surface(screen.get_size())
    fade_surface.fill((0, 0, 0))  # Fill the surface with black
    
    # Gradually increase the alpha value to create a fade-out effect
    for alpha in range(0, 256, 5):
        fade_surface.set_alpha(alpha)
        screen.blit(background_image, (0, 0))  # Draw the background
        screen.blit(fade_surface, (0, 0))  # Draw the fade surface
        pygame.display.flip()
        pygame.time.delay(duration // (256 // 5))  # Control fade speed

# Function to play the MP4 video
def play_video(video_path):
    clip = VideoFileClip(video_path)
    clip = clip.resize(newsize=(800, 600))  # Resize video to fit the window

    for frame in clip.iter_frames(fps=30, dtype='uint8'):
        frame_surface = pygame.surfarray.make_surface(frame)  # Create Pygame surface from the frame
        rotated_frame = pygame.transform.rotate(frame_surface, -90)  # Rotate the frame 90 degrees anticlockwise
        mirrored_frame = pygame.transform.flip(rotated_frame, True, False)
        # Calculate the position to center the rotated frame
        frame_rect = mirrored_frame.get_rect(center=(400, 300))  # Center in the window
        
        screen.blit(rotated_frame, frame_rect.topleft)  # Draw the rotated frame on the screen
        pygame.display.flip()  # Update the display
        pygame.time.delay(int(1000 / 30))  # Delay to match frame rate (30 FPS)







    # for frame in clip.iter_frames(fps=30, dtype='uint8'):
    #     frame_surface = pygame.surfarray.make_surface(frame)  # Create Pygame surface from the frame
    #     mirrored_frame = pygame.transform.flip(frame_surface, True, False)  # Mirror the frame
    #     screen.blit(mirrored_frame, (0, 0))  # Draw the mirrored frame on the screen
    #     pygame.display.flip()  # Update the display
    #     pygame.time.delay(int(1000 / 30))  # Delay to match frame rate (30 FPS)

# Main game loop
running = True
while running:
    # Capture frame from the webcam
    ret, frame = cap.read()
    if not ret:
        break
    
    # Process the frame for hand tracking
    frame = cv2.flip(frame, 1)  # Flip the frame horizontally
    h, w, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(frame_rgb)
    
    index_finger_tip = None  # Initialize index finger tip position
    
    # Detect hand landmarks
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x = int(index_finger_tip.x * w)  # X coordinate of index finger tip
            y = int(index_finger_tip.y * h)  # Y coordinate of index finger tip
            
            # Draw circles at the fingertip for visualization
            cv2.circle(frame, (x, y), 15, (0, 0, 255), cv2.FILLED)
            cv2.circle(frame, (x, y), 10, (0, 165, 255), cv2.FILLED)
            cv2.circle(frame, (x, y), 5, (0, 255, 255), cv2.FILLED)

    # Display the webcam feed
    cv2.imshow('Webcam Feed', frame)

    # Clear the screen and draw the background
    screen.fill(WHITE)
    screen.blit(background_image, (0, 0))

    # Update mole position based on timing
    current_time = time.time()
    if current_time - last_mole_time > mole_appearance_time:
        mole_pos = [random.randint(mole_radius, 800 - mole_radius), random.randint(mole_radius, 600 - mole_radius)]
        last_mole_time = current_time

    # Check for hits on the mole
    if index_finger_tip:
        finger_x = int(index_finger_tip.x * 800)  # Scale X to Pygame's width
        finger_y = int(index_finger_tip.y * 600)  # Scale Y to Pygame's height

        # Check if the index finger is overlapping with the mole
        if ((finger_x - mole_pos[0]) ** 2 + (finger_y - mole_pos[1]) ** 2) ** 0.5 < mole_radius:
            score += 1  # Increase score
            mole_counter += 1  # Increment hit counter
            hit_sound.play()  # Play hit sound
            
            # Display hit message
            hit_message = hit_messages[hit_message_index]
            font = pygame.font.Font(None, 36)
            hit_text = font.render(hit_message, True, BLACK)
            screen.blit(hit_text, (300, 300))
            pygame.display.flip()
            pygame.time.delay(500)  # Delay to show the message
            hit_message_index = (hit_message_index + 1) % len(hit_messages)  # Cycle through messages
            
            # Relocate the mole after a hit
            mole_pos = [random.randint(mole_radius, 800 - mole_radius), random.randint(mole_radius, 600 - mole_radius)]
            last_mole_time = current_time  # Reset the timer

    # Draw the mole image at its current position
    screen.blit(mole_image, (mole_pos[0] - mole_radius, mole_pos[1] - mole_radius))
    
    # Display the score and remaining time
    font = pygame.font.Font(None, 36)
    score_text = font.render(f'Score: {score}', True, BLACK)
    screen.blit(score_text, (10, 10))
    remaining_time = game_duration - (current_time - start_time)
    timer_text = font.render(f'Time Left: {int(remaining_time)}', True, BLACK)
    screen.blit(timer_text, (600, 10))

    # Check if the game is over
    if mole_counter >= 10 or remaining_time <= 0:
        pygame.mixer.music.stop()  # Stop the background music
        fade_out(screen, 2000)  # Fade out the screen
        vic_sound.play()  # Play victory sound
        
        # Play the video
        play_video('dusshera2_flipped.mp4')  # Play the MP4 video

        pygame.time.delay(5000)  # Keep the last frame for 5 seconds
        running = False  # End the game

    # Update the display
    pygame.display.flip()

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  # Exit on window close
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False  # Exit on pressing ESC

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break  # Exit on pressing 'q'

# Cleanup resources
cap.release()  # Release the webcam
pygame.quit()  # Quit Pygame
hands.close()  # Close MediaPipe hands
cv2.destroyAllWindows()  # Destroy all OpenCV windows
