# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 22:56:05 2019

@author: letitia
"""

import numpy as np
import cv2

#路径名中有中文，cv2.imread()读出来会是nonetype
path = r'1.jpg'
img = cv2.imread(path)

img_new = np.zeros(img.shape)
print(img.shape)
img_BRG = img[...,[0,2,1]]  #opencv转换后为BGR
cv2.namedWindow("Image")   
cv2.imshow("Image", img_BRG)   
cv2.waitKey (0)  
cv2.destroyAllWindows() 

#18020032：（18，02）（18+00，02+32）
#img_BRG[18:18,2:34] = [0,0,255]   #是个矩形
img_BRG[18:28, 2] = [0,0,255]
img_BRG[18:28, 52] = [0,0,255]
img_BRG[18, 2:52] = [0,0,255]
img_BRG[28, 2:52] = [0,0,255]
cv2.namedWindow("Image")   
cv2.imshow("Image", img_BRG)   
cv2.waitKey (0)  
cv2.destroyAllWindows() 


cv2.imwrite('2.jpg', img_BRG)
