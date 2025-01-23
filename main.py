import cv2
import pickle
import cvzone
import numpy as np

# Video feed
cap = cv2.VideoCapture('carPark.mp4')

# Load parking slot positions from pickle file
with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)

# Constants for parking lot dimensions
width, height = 107, 48

# Initialize counters for white, black, and red cars
whiteCarCounter = 0
blackCarCounter = 0
redCarCounter = 5  # Start with 5 red cars (predefined)
carStatus = {}  # Dictionary to track the status (empty or occupied) of each parking space
carColorStatus = {}  # Dictionary to track which car color is occupying the space

# Predefined car limits
max_white_cars = 25
max_black_cars = 39
max_red_cars = 5
total_slots = len(posList)

# Initial free slots = 12 out of 69
initial_free_slots = 12  # Predefined number of free slots
current_free_slots = initial_free_slots  # Set the current free slots to 12 initially


# Function to check parking space occupancy
def checkParkingSpace(imgPro):
    global whiteCarCounter, blackCarCounter, redCarCounter, current_free_slots

    occupied_slots = 0  # Counter to track occupied slots

    for pos in posList:
        x, y = pos

        # Crop the parking space from the processed image
        imgCrop = imgPro[y:y + height, x:x + width]
        count = cv2.countNonZero(imgCrop)

        # Checking for free/occupied space
        if count < 900:  # Free space
            color = (0, 255, 0)  # Green
            thickness = 5

            # If the space was previously occupied, decrease the appropriate car counter
            if carStatus.get(pos, False):  # It was occupied before
                carStatus[pos] = False  # Mark this space as free
                car_color = carColorStatus.get(pos, None)  # Get the car color occupying the space
                if car_color == 'white' and whiteCarCounter > 0:
                    whiteCarCounter -= 1
                elif car_color == 'black' and blackCarCounter > 0:
                    blackCarCounter -= 1
                elif car_color == 'red' and redCarCounter > 0:
                    redCarCounter -= 1
                carColorStatus[pos] = None  # Reset the car color for this space

        else:  # Occupied space
            color = (0, 0, 255)  # Red
            thickness = 2
            occupied_slots += 1

            # If the space was previously free, increase the appropriate car counter
            if not carStatus.get(pos, False):  # It was free before
                carStatus[pos] = True  # Mark this space as occupied

                # Detect white, black, or red car based on the color in the space
                imgCropColor = img[y:y + height, x:x + width]
                hsv = cv2.cvtColor(imgCropColor, cv2.COLOR_BGR2HSV)

                # Detect white cars
                mask_white = cv2.inRange(hsv, np.array([0, 0, 180]), np.array([180, 20, 255]))
                if cv2.countNonZero(mask_white) > 500 and whiteCarCounter < max_white_cars:
                    whiteCarCounter += 1
                    carColorStatus[pos] = 'white'

                # Detect black cars
                mask_black = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 60]))
                if cv2.countNonZero(mask_black) > 500 and blackCarCounter < max_black_cars:
                    blackCarCounter += 1
                    carColorStatus[pos] = 'black'

                # Detect red cars
                mask_red1 = cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255]))
                mask_red2 = cv2.inRange(hsv, np.array([170, 120, 70]), np.array([180, 255, 255]))
                if cv2.countNonZero(cv2.bitwise_or(mask_red1, mask_red2)) > 500 and redCarCounter < max_red_cars:
                    redCarCounter += 1
                    carColorStatus[pos] = 'red'

        # Draw the rectangle around parking space
        cv2.rectangle(img, (x, y), (x + width, y + height), color, thickness)

        # Display the count of non-zero pixels in the space
        cvzone.putTextRect(img, str(count), (x, y + height - 3), scale=1, thickness=2, offset=0, colorR=color)

    # Update the number of free slots
    current_free_slots = total_slots - occupied_slots

    # Display the current free slots count
    cvzone.putTextRect(img, f'Free: {current_free_slots}/{total_slots}', (100, 50), scale=3, thickness=5, offset=20,
                       colorR=(0, 200, 0))

    # Display white, black, and red car counts
    cvzone.putTextRect(img, f'White Cars: {whiteCarCounter}/{max_white_cars}', (100, 100), scale=2, thickness=3,
                       offset=20, colorR=(0, 0, 0))
    cvzone.putTextRect(img, f'Black Cars: {blackCarCounter}/{max_black_cars}', (100, 150), scale=2, thickness=3,
                       offset=20, colorR=(0, 0, 0))
    cvzone.putTextRect(img, f'Red Cars: {redCarCounter}/{max_red_cars}', (100, 200), scale=2, thickness=3, offset=20,
                       colorR=(0, 0, 0))


# Main loop to process video frames
while True:
    # Reset video to the first frame if at the end
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    success, img = cap.read()
    if not success:
        break

    # Convert the image to grayscale, blur, and threshold
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    # Check parking space occupancy and detect white, black, and red cars
    checkParkingSpace(imgDilate)

    # Show the processed video frame
    cv2.imshow("Parking Lot", img)

    # Exit the video feed when 'q' is pressed
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
