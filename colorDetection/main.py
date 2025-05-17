import cv2
import numpy as np
import os

#lets try a dynamic cropping and fall into static cropping if it does not work too well
def cropStaticFurnaces(imagePath):
    readImage = cv2.imread(imagePath)
    x, y, w, h = 290, 475, 50, 100

    cropped = readImage[y: y+h, x: x+w]
    return cropped


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

    #detects the color using shortcircuiting
    mask_combined = cv2.bitwise_or(mask_red1, mask_red2) 
    mask_combined = cv2.bitwise_or(mask_combined, mask_orange) 
    mask_combined = cv2.bitwise_or(mask_combined, mask_green)

    cv2.imwrite("preprocess/processedImage.png", mask_combined)
    return "preprocess/processedImage.png"

def classifyColor(image):
    img = cv2.imread(image, cv2.IMREAD_GRAYSCALE)

    if img is None:
        print("file not found")

    height, width = img.shape
    section = height // 3

    top = img[0: section, :]
    middle = img[section : section * 2, :]
    bottom = img[section * 2: , :]

    if(np.any(top == 255)):
        print("GREEN ON")
    if(np.any(middle == 255)):
        print("ORANGE ON")
    if(np.any(bottom == 255)):
        print("RED ON")



def show_coordinates(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"X: {x}, Y: {y}")

    img = cv2.imread("images/fullfurnace.jpeg")
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", show_coordinates)

    while True:
        cv2.imshow("image", img)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cv2.destroyAllWindows()



# img = cv2.imread("images/stack.jpeg")
# detectLight(img)
# processedPath = "preprocess/processedImage.png"
# classifyColor(processedPath)
# textinput = input("q to quit(): ")
# if(textinput == 'q'):
#     os.remove("preprocess/processedImage.png")



croppedImg = cropStaticFurnaces("images/fullfurnace.jpeg")
filePath = detectLight(croppedImg)
classifyColor(filePath)

