# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 22:56:05 2019

@author: letitia
"""

import numpy as np
import cv2

#路径名中有中文，cv2.imread()读出来会是nonetype
path = r'20190420205149.png'
img = cv2.imread(path) 

img_BRG = img[...,[0,2,1]]  #opencv转换后为BGR
cv2.namedWindow("Image")   
cv2.imshow("Image", img_BRG)   
cv2.waitKey (0)  
cv2.destroyAllWindows() 

#18023050：（18，02）（18+30，02+50）
#img_BRG[18:48, 2:52] = [0,0,255]   #是个矩形
img_BRG[18:48, 2] = [0,0,255]
img_BRG[18:48, 52] = [0,0,255]
img_BRG[18, 2:52] = [0,0,255]
img_BRG[48, 2:52] = [0,0,255]
cv2.namedWindow("Image")   
cv2.imshow("Image", img_BRG)   
cv2.waitKey (0)  
cv2.destroyAllWindows() 


cv2.imwrite('20190420205149_BRG.png', img_BRG)
