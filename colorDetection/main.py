import cv2
import numpy as np
import os

#lets try a dynamic cropping and fall into static cropping if it does not work too well
def cropStaticFurnaces(imagePath, tube):
    readImage = cv2.imread(imagePath)
    dimensionArray = [[362, 380, 25, 55], [362, 500, 25, 55],  [362,618, 25, 55], [362,737, 25, 55],
                      [979, 353, 25, 55], [980, 486, 25, 55], [981, 619, 25, 55], [983, 749, 25, 55],
                      [1403, 349, 25, 55], [1408, 479, 25, 55], [1407, 608, 25, 55], [1408, 736, 25, 55]] 


    x, y, w, h = dimensionArray[tube][0], dimensionArray[tube][1], dimensionArray[tube][2], dimensionArray[tube][3]

    cropped = readImage[y: y+h, x: x+w]
    cv2.imwrite("preprocess/croppedimg.jpg",  cropped)
    return cropped

#processes the image into black and white
def detectLight(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 40, 255])


    mask_combined = cv2.inRange(hsv, lower_white, upper_white)

    cv2.imwrite("preprocess/processedImage.png", mask_combined)
    return "preprocess/processedImage.png"

#tells us what color is on, based on position of the light
def classifyColor(image, tube):
    img = cv2.imread(image, cv2.IMREAD_GRAYSCALE)

    if img is None:
        print("file not found")

    height, width = img.shape
    
    section = height // 3

    top = img[0: section, :]
    middle = img[section : section * 2, :]
    bottom = img[section * 2: , :]


    top_array = []
    top_sum = 0
    for y in range(top.shape[0]):
        for x in range(top.shape[1]):
            if(top[y, x] ==  255):
                top_array.append(1)
                top_sum+=1
            else:
                top_array.append(0)
    
    middle_sum = 0
    middle_array = []
    for y in range(middle.shape[0]):
        for x in range(middle.shape[1]):
            if(middle[y, x] == 255):
                middle_array.append(1)
                middle_sum+=1
            else:
                middle_array.append(0)
    

        
    bottom_sum = 0
    bottom_array = []
    for y in range(bottom.shape[0]):
        for x in range(bottom.shape[1]):
            if(bottom[y, x] == 255):
                bottom_array.append(1)
                bottom_sum+=1
            else:
                bottom_array.append(0)
        

    # print("top sum: ", top_sum)
    # print("middle_sum: ",  middle_sum)
    # print("bottom_sum: ",  bottom_sum)

    red = False
    orange = False
    green = False


    if(top_sum > 125):
        # print(f"tube {tube+1}: RED ON")
        red = True
    if(middle_sum > 125):
        # print(f"tube {tube+1}: ORANGE ON")
        orange =  True
    if(bottom_sum > 125):
        # print(f"tube {tube+1}: GREEN ON")
        green = True

    if orange and green:
        print(f"Tube {tube+1}: Waiting for USER Input")
    elif green and red:
        print(f"Tube {tube+1}: Ready to load  wafers")
    else:
        if red:
            print(f"Tube {tube+1}: ERROR! CONTACT STAFF")
        elif green:
            print(f"Tube {tube+1}: Running Recipe")
        elif orange:
            print(f"Tube {tube+1}: IDLE & Ready")


    print('--------------------------------------------')

def show_coordinates(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"X: {x}, Y: {y}")

    img = cv2.imread("images/highres0.jpg")
    cv2.namedWindow("image")
    cv2.setMouseCallback("image", show_coordinates)

    while True:
        cv2.imshow("image", img)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cv2.destroyAllWindows()

def capture1080p():
    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    ret, frame = cap.read()

    if not ret:
        print("cant see")
    else:
        height, width = frame.shape[:2]
        print(height, width)


    cv2.imwrite("images/highres.jpg", frame)

    cap.release()



# img = cv2.imread("images/stack.jpeg")
# detectLight(img)
# processedPath = "preprocess/processedImage.png"
# classifyColor(processedPath)
# textinput = input("q to quit(): ")
# if(textinput == 'q'):
#     os.remove("preprocess/processedImage.png")


for i in range(0, 12):
    croppedImg = cropStaticFurnaces("images/highres0.jpg", i)
    filePath = detectLight(croppedImg)
    classifyColor(filePath, i)

# for i in range(5):
#     capture1080p(i)




