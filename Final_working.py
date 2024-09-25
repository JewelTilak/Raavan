import cv2
import mediapipe as mp
import pygame
import random
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Pygame Initialization
pygame.init()
screen = pygame.display.set_mode((800, 600))  # Fixed size for the game window
pygame.display.set_caption('Ravana-Dahan')

# Load PNG image for the mole
mole_image = pygame.image.load(r'ravana.png').convert_alpha() # Load your PNG image
mole_image = pygame.transform.scale(mole_image, (200, 200))  # Resize to an appropriate size

# Load Background Image
background_image = pygame.image.load(r'Background.jpg')
background_image = pygame.transform.scale(background_image, (800, 600))  # Scale to window size



# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Mole Variables
mole_radius = 120  # Used to calculate hit detection area
mole_pos = [random.randint(mole_radius, 800 - mole_radius), random.randint(mole_radius, 600 - mole_radius)]
score = 0

# Timing for mole appearance
mole_appearance_time = 2  # Mole appears every 5 seconds
last_mole_time = time.time()

# Webcam Capture
cap = cv2.VideoCapture(0)

# Game Loop
running = True
while running:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Flip the frame horizontally for natural hand movement (mirroring)
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Hand gesture recognition using MediaPipe
    result = hands.process(frame_rgb)
    
    index_finger_tip = None
    
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Get the coordinates of the index finger tip (landmark 8)
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            x = int(index_finger_tip.x * w)
            y = int(index_finger_tip.y * h)
            
            # Draw a circle on the index finger tip in the webcam feed
            cv2.circle(frame, (x, y), 10, (0, 255, 0), cv2.FILLED)
    
    # Show the webcam feed in a separate OpenCV window
    cv2.imshow('Webcam Feed', frame)

    # Pygame Logic (for drawing moles and interaction)
    screen.fill(WHITE)
    screen.blit(background_image, (0, 0))


    # Check if enough time has passed to reposition the mole
    current_time = time.time()
    if current_time - last_mole_time > mole_appearance_time:
        # Relocate the mole every 1.5 seconds
        mole_pos = [random.randint(mole_radius, 800 - mole_radius), random.randint(mole_radius, 600 - mole_radius)]
        last_mole_time = current_time  # Reset the timer

    # Check if mole is hit
    if index_finger_tip:
        # Scale the finger coordinates to the Pygame window size
        finger_x = int(index_finger_tip.x * 800)  # Scale X to match Pygame's width
        finger_y = int(index_finger_tip.y * 600)  # Scale Y to match Pygame's height

        # Check if the index finger overlaps with the mole (hit detection)
        if ((finger_x - mole_pos[0]) ** 2 + (finger_y - mole_pos[1]) ** 2) ** 0.5 < mole_radius:
            score += 1
            # Immediately relocate the mole after a hit
            mole_pos = [random.randint(mole_radius, 800 - mole_radius), random.randint(mole_radius, 600 - mole_radius)]
            last_mole_time = current_time  # Reset the timer

    # Draw the mole (PNG image) at its current position
    screen.blit(mole_image, (mole_pos[0] - mole_radius, mole_pos[1] - mole_radius))
    
    # Display the score
    font = pygame.font.Font(None, 36)
    score_text = font.render(f'Score: {score}', True, BLACK)
    screen.blit(score_text, (10, 10))
    
    # Pygame display update
    pygame.display.flip()

    # Exit conditions
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:  # Press 'Esc' to exit
            running = False

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
pygame.quit()
hands.close()
cv2.destroyAllWindows()
