import cv2
import numpy as np
import os
import time

#lets try a dynamic cropping and fall into static cropping if it does not work too well
def cropStaticFurnaces(imagePath, tube):
    readImage = cv2.imread(imagePath)
    dimensionArray = [
    [285, 378, 25, 55],
    [283, 500, 25, 55],
    [284, 620, 25, 55],
    [291, 732, 25, 55],
    [904, 354, 25, 55],
    [902, 485, 25, 55],
    [904, 617, 25, 55],
    [906, 750, 25, 55],
    [1327, 354, 25, 55],
    [1331, 484, 25, 55],
    [1332, 606, 25, 55],
    [1331, 736, 25, 55]
    ] 


    x, y, w, h = dimensionArray[tube][0], dimensionArray[tube][1], dimensionArray[tube][2], dimensionArray[tube][3]

    cropped = readImage[y: y+h, x: x+w]
    # cropped = mitigate_bleeding(cropped)
    cv2.imwrite(f"preprocess/croppedimg{tube}.jpg",  cropped)
    return cropped

#processes the image into black and white
def detectLight(image, tube):

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_white = np.array([0, 0, 200])
    upper_white = np.array([180, 40, 255])

    mask_combined = cv2.inRange(hsv, lower_white, upper_white)

    kernel = np.ones((2, 2), np.uint8)
    mask_eroded = cv2.erode(mask_combined, kernel, iterations=1)

    mask_bgr = cv2.cvtColor(mask_eroded, cv2.COLOR_GRAY2BGR)

    height, width = mask_bgr.shape[:2]


    border_color = (0, 0, 255)  # Red in BGR
    thickness = 2
    cv2.rectangle(mask_bgr, (0, 0), (width - 1, height - 1), border_color, thickness)


    third = height // 3
    cv2.line(mask_bgr, (0, third), (width, third), border_color, 1)
    cv2.line(mask_bgr, (0, third * 2), (width, third * 2), border_color, 1)




    save_path = f"preprocess/processedImage{tube}.png"
    cv2.imwrite(save_path, mask_bgr)

    return save_path


    # cv2.imwrite(f"preprocess/processedImage{tube}.png", mask_combined)
    # return f"preprocess/processedImage{tube}.png"



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

 
    if(top_sum > 100):
        # print(f"tube {tube+1}: RED ON")
        red = True
    if(middle_sum > 100):
        # print(f"tube {tube+1}: ORANGE ON")
        orange =  True
    if(bottom_sum > 100):
        # print(f"tube {tube+1}: GREEN ON")
        green = True

    # print(f"TUBE {tube + 1}: ", top_sum, middle_sum, bottom_sum)

    if(not red and not orange and not green):
        print(f"tube {tube + 1}: VIEW OBSTRUCTED!")    
    else:
        if orange and green:
            print(f"Tube {tube+1}: Waiting for USER Input")
        elif green and red:
            print(f"Tube {tube+1}: Waiting for USER Input")
        else:
            if red:
                print(f"Tube {tube+1}: ERROR! CONTACT STAFF")
            elif green:
                print(f"Tube {tube+1}: Running Recipe")
            elif orange:
                print(f"Tube {tube+1}: IDLE & Ready")


    print('--------------------------------------------')

def mitigate_bleeding(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    kernel = np.ones((3, 3), np.uint8)

    cleaned = cv2.erode(thresh, kernel, iterations = 1)
    print("got here")
    return cleaned 

def configure_points():
    def show_coordinates(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"X: {x}, Y: {y}")

    img = cv2.imread("images/highres.jpg")
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

# capture1080p()
# configure_points()

for x in range(1):
    capture1080p()
    capture1080p()
    capture1080p()
    for i in range(0, 12):
        croppedImg = cropStaticFurnaces("images/highres.jpg", i)
        filePath = detectLight(croppedImg, i)
        # filePath = f"preprocess/processedImage{i}.png"
        classifyColor(filePath, i)
    
    time.sleep(5)


# for i in range(5):
#     capture1080p(i)




