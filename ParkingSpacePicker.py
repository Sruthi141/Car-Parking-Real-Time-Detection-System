import cv2
import pickle
import os

img = cv2.imread('carParkImg.png')

width, height = 107, 48
posList = []

# Load the saved positions if the file exists
if os.path.exists('carParkPos'):
    with open('carParkPos', 'rb') as f:
        posList = pickle.load(f)


def mouseClick(events, x, y, flags, params):
    if events == cv2.EVENT_LBUTTONDOWN:
        posList.append((x, y))
    if events == cv2.EVENT_RBUTTONDOWN:
        for i, pos in enumerate(posList):
            x1, y1 = pos
            if x1 < x < x1 + width and y1 < y < y1 + height:
                posList.pop(i)

if img is None:
    print("Error: Could not load image.")
else:
    while True:
        img_copy = img.copy()  # Make a fresh copy of the image in each loop iteration

        # Draw rectangles on the copied image
        for pos in posList:
            cv2.rectangle(img_copy, pos, (pos[0] + width, pos[1] + height), (255, 0, 255), 2)

        # Display the image
        cv2.imshow("image", img_copy)

        # Set the mouse callback for the window
        cv2.setMouseCallback("image", mouseClick)

        # Exit on pressing 'esc'
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # 27 is the ASCII code for the escape key
            break

# Save the positions when the user exits
with open('carParkPos', 'wb') as f:
    pickle.dump(posList, f)

cv2.destroyAllWindows()
