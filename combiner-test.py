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
image = cv.imread(facePath, 0)
print(image.shape)
width = image.shape[1]
height = image.shape[0]

# cv.imshow('yeet', image)

mouth = [0, 0]
for w in range(width - 1):
    for h in range(height - 1):
        pixel = image[h, w]
        if pixel != 255 and pixel != 0:
            print(pixel)
            mouth = [w, h]
            print(mouth)











face =  Image.open(facePath).convert("RGBA")
cat = Image.open("cat 1.jpg").convert("RGBA")



face.paste(cat, (int(mouth[0] - cat.size[0]/2), int(mouth[1] - cat.size[1]/2)), cat)
face.save('reeeee.png',"png")



cv.waitKey(0)
cv.destroyAllWindows()
