import cv2
import pickle
import cvzone
import numpy as np

cap = cv2.VideoCapture('carPark.mp4')
width, height = 103, 43  # Dimensions for each parking slot

# Try to load parking slot positions (from the polygons.txt file)
try:
    with open('polygons.txt', 'rb') as f:
        posList = pickle.load(f)
except FileNotFoundError:
    print("polygons.txt file not found.")
    posList = []  # Initialize as empty if the file is missing
except pickle.UnpicklingError:
    print("Error unpickling the polygons file. It might be corrupted.")
    posList = []

# Empty function for trackbars
def empty(a):
    pass

# Create a window with trackbars for tuning
cv2.namedWindow("Vals")
cv2.resizeWindow("Vals", 640, 240)
cv2.createTrackbar("Val1", "Vals", 25, 50, empty)
cv2.createTrackbar("Val2", "Vals", 16, 50, empty)
cv2.createTrackbar("Val3", "Vals", 5, 50, empty)

# Function to check available spaces and detect cars
def checkSpaces():
    spaces = 0
    white_cars = 0
    black_cars = 0

    # Loop through each parking slot and check its occupancy
    for pos in posList:
        x, y = pos
        w, h = width, height

        imgCrop = imgThres[y:y + h, x:x + w]
        count = cv2.countNonZero(imgCrop)

        # Check if the parking space is occupied or free
        if count < 900:
            color = (0, 200, 0)  # Free space: Green
            thic = 5
            spaces += 1
        else:
            color = (0, 0, 200)  # Occupied space: Red
            thic = 2

        # Draw rectangle around parking spaces
        cv2.rectangle(img, (x, y), (x + w, y + h), color, thic)
        cvzone.putTextRect(img, str(count), (x, y + h - 6), cv2.FONT_HERSHEY_PLAIN, 1, color, 2)

        # Detecting cars based on color
        imgCropColor = img[y:y + h, x:x + w]
        hsv = cv2.cvtColor(imgCropColor, cv2.COLOR_BGR2HSV)

        # Detect white cars
        lower_white = np.array([0, 0, 0])
        upper_white = np.array([180, 255, 60])
        white_mask = cv2.inRange(hsv, lower_white, upper_white)
        if cv2.countNonZero(white_mask) > 500:  # You can adjust the threshold here
            white_cars += 1

        # Detect black cars
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([180, 255, 60])
        black_mask = cv2.inRange(hsv, lower_black, upper_black)
        if cv2.countNonZero(black_mask) > 500:  # You can adjust the threshold here
            black_cars += 1

    # Display the result of free spaces and detected cars
    cvzone.putTextRect(img, f'Free: {spaces}/{len(posList)}', (50, 60), thickness=3, offset=20, colorR=(0, 200, 0))
    cvzone.putTextRect(img, f'White Cars: {white_cars}', (50, 100), thickness=2, offset=20, colorR=(255, 255, 255))
    cvzone.putTextRect(img, f'Black Cars: {black_cars}', (50, 150), thickness=2, offset=20, colorR=(0, 0, 0))

# Main loop to process the video frame
while True:
    success, img = cap.read()
    if not success:
        break

    # Convert image to grayscale and apply blur
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)

    # Get the trackbar values for thresholding parameters
    val1 = cv2.getTrackbarPos("Val1", "Vals")
    val2 = cv2.getTrackbarPos("Val2", "Vals")
    val3 = cv2.getTrackbarPos("Val3", "Vals")
    if val1 % 2 == 0: val1 += 1
    if val3 % 2 == 0: val3 += 1

    # Adaptive thresholding
    imgThres = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY_INV, val1, val2)
    imgThres = cv2.medianBlur(imgThres, val3)
    kernel = np.ones((3, 3), np.uint8)
    imgThres = cv2.dilate(imgThres, kernel, iterations=1)

    # Check spaces and count cars
    checkSpaces()

    # Display the processed frame
    cv2.imshow("Image", img)

    # Optional reset with key press
    key = cv2.waitKey(1)
    if key == ord('r'):
        pass

cap.release()
cv2.destroyAllWindows()
