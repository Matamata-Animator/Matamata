from PIL import Image
import sys
import cv2 as cv
import numpy as np

'''
###########################
#! IMPORTANT

The format of opencv is (h, w) and pillow Image is (w, h)

#! IMPORTANT
###########################
'''


facePath = "faces/dumb-smile.png"
mouthPath = "mouths/smile.png"
image = cv.imread(facePath, 0)
print(image.shape)
width = image.shape[1]
height = image.shape[0]

# cv.imshow('yeet', image)

mouthPos = [0, 0]
for w in range(width - 1):
    for h in range(height - 1):
        pixel = image[h, w]
        if pixel != 255 and pixel != 0:
            print(pixel)
            mouthPos = [w, h]
            print(mouthPos)











face =  Image.open(facePath).convert("RGBA")
mouth = Image.open(mouthPath).convert("RGBA")



face.paste(mouth, (int(mouthPos[0] - mouth.size[0]/2), int(mouthPos[1] - mouth.size[1]/2)), mouth)
face.save('reeeee.png',"png")



cv.waitKey(0)
cv.destroyAllWindows()
