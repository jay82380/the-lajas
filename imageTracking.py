import cv2 as cv
from imageai.Detection import ObjectDetection

import numpy as np
import requests as req
import os as os

dirr = "archive/human detection dataset/pics"

# img = cv.imread('0.png')
# window_name = 'image'
# cv.imshow(window_name, img)
# cv.waitKey(0)
# cv.destroyAllWindows()

def showImage(img):
    window_name = 'image'
    cv.imshow(window_name, img)
    cv.waitKey(1000)
    if cv.waitKey(1) & 0xFF == ord('q'):
        cv.destroyAllWindows()
        exit()
    

modelRetinaNet = 'https://github.com/OlafenwaMoses/ImageAI/releases/download/1.0/resnet50_coco_best_v2.0.1.h5'
modelYOLOv3 = 'https://github.com/OlafenwaMoses/ImageAI/releases/download/1.0/yolo.h5'
modelTinyYOLOv3 = 'https://github.com/OlafenwaMoses/ImageAI/releases/download/1.0/yolo-tiny.h5'

if not os.path.exists('../yolo.h5'):
    r = req.get(modelYOLOv3, timeout=0.5)
    with open('../yolo.h5', 'wb') as outfile:
        outfile.write(r.content)

detector = ObjectDetection()
detector.setModelTypeAsYOLOv3()
detector.setModelPath('../yolo.h5')
detector.loadModel()



image_files = [os.path.join(dirr, file) for file in os.listdir(dirr) if file.endswith('.png')]

tracker_type = 'CSRT'  # Change this to the desired tracker type

# Initialize the tracker
tracker = cv.TrackerCSRT_create() if tracker_type == 'CSRT' else cv.TrackerKCF_create()

frame = cv.imread(image_files[0])


# import random
# randomFile = os.listdir(dir + "/000004.png")
# randomFile = cv.imread(dir + "/000004.png")
# randomFile = peopleImages[random.randint(0, len(peopleImages) - 1)]


peopleOnly = detector.CustomObjects(car=True)
detectedImage, detections = detector.detectCustomObjectsFromImage(custom_objects=peopleOnly, output_type="array", input_image=dirr + "/frame1.png", minimum_percentage_probability=50)
convertedImage = cv.cvtColor(detectedImage, cv.COLOR_RGB2BGR)
showImage(convertedImage)

output_image = detectedImage.copy()

count = 0


trackers = []
for detection in detections:
    x, y, w, h = detection['box_points']
    tracker = cv.TrackerKCF_create()
    tracker.init(frame, (x, y, w, h))
    trackers.append(tracker)

frame_counter = 1
print("check1")
while True:
    print("check3")
    frame_path = dirr + f"/frame{frame_counter}.png"
    if not os.path.exists(frame_path):
        break
    print("check2")
    frame = cv.imread(frame_path)
    if frame is None:
        print("bad")

    count = len(trackers)
    for tracker in trackers:
        success, bbox = tracker.update(frame)
        if success:
            x, y, w, h = [int(v) for v in bbox]
            cv.rectangle(frame, (x, y), (x+w, y+h), (0,255,0),2)
        else:
            count -= 1

    showImage(frame)
    print(count)

    frame_counter += 1



cv.destroyAllWindows()



# detectedImage, detections = detector.detectObjectsFromImage(output_type="array", input_image="archive/human detection dataset/pics/{0}".format(randomFile), minimum_percentage_probability=30)
# convertedImage = cv.cvtColor(detectedImage, cv.COLOR_RGB2BGR)
# showImage(convertedImage)

for eachObject in detections:
    print(eachObject["name"] , " : ", eachObject["percentage_probability"], " : ", eachObject["box_points"] )
    print("--------------------------------")

# print(car["name"], car["percentage_probability"])

