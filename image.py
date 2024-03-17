import cv2 as cv
from imageai.Detection import ObjectDetection

import numpy as np
import requests as req
import os as os

dir = "archive/human detection dataset/pics"

# img = cv.imread('0.png')
# window_name = 'image'
# cv.imshow(window_name, img)
# cv.waitKey(0)
# cv.destroyAllWindows()

def showImage(img):
    window_name = 'image'
    cv.imshow(window_name, img)
    cv.waitKey(0)
    cv.destroyAllWindows()

modelRetinaNet = 'https://github.com/OlafenwaMoses/ImageAI/releases/download/1.0/resnet50_coco_best_v2.0.1.h5'
modelYOLOv3 = 'https://github.com/OlafenwaMoses/ImageAI/releases/download/1.0/yolo.h5'
modelTinyYOLOv3 = 'https://github.com/OlafenwaMoses/ImageAI/releases/download/1.0/yolo-tiny.h5'

if not os.path.exists('yolo.h5'):
    r = req.get(modelYOLOv3, timeout=0.5)
    with open('yolo.h5', 'wb') as outfile:
        outfile.write(r.content)

detector = ObjectDetection()
detector.setModelTypeAsYOLOv3()
detector.setModelPath('yolo.h5')
detector.loadModel()

import random
peopleImages = os.listdir(dir)
randomFile = peopleImages[random.randint(0, len(peopleImages) - 1)]

peopleOnly = detector.CustomObjects(person=True)
detectedImage, detections = detector.detectCustomObjectsFromImage(custom_objects=peopleOnly, output_type="array", input_image=dir+"/{0}".format(randomFile), minimum_percentage_probability=30)
convertedImage = cv.cvtColor(detectedImage, cv.COLOR_RGB2BGR)
showImage(convertedImage)

for eachObject in detections:
    print(eachObject["name"] , " : ", eachObject["percentage_probability"], " : ", eachObject["box_points"] )
    print("--------------------------------")
