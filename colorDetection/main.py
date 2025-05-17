import cv2
import numpy as np


def detectLight(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])


    lower_orange = np.array([11, 100, 100])
    upper_orange = np.array([25, 255, 255])


    lower_green = np.array([40, 100, 100])
    upper_green = np.array([80, 255, 255])


    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)
    mask_green = cv2.inRange(hsv, lower_green, upper_green)


    mask_combined = cv2.bitwise_or(mask_red1, mask_red2) #detects the color that is on using short circuiting
    mask_combined = cv2.bitwise_or(mask_combined, mask_orange) 
    mask_combined = cv2.bitwise_or(mask_combined, mask_green)

    return mask_combined

img = cv2.imread("images/stack.jpeg")
result = detectLight(img)

cv2.imshow("OUTPUT", result)
cv2.waitKey(0)
cv2.destroyAllWindows()