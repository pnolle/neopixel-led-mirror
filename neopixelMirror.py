#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neopixel LED Mirror Code (Neopixel LED Mirror - Super Make Something Episode 20)
by: Alex - Super Make Something
date: November 18, 2019
license: Creative Commons - Attribution - Non Commercial.  More information at: http://creativecommons.org/licenses/by-nc/3.0/
"""

# Import required libraries
from picamera import PiCamera
from picamera.array import PiRGBArray
from time import sleep
import numpy as np
import board
import neopixel
import time
import logging


def extractROI(image,windowSize):
    roiImage=image[:windowSize[0],:windowSize[1],:]
    logging.debug('extractROI image.shape {} {} {}'.format(image.shape[0], image.shape[1], image.shape[2])) 
    # logging.debug('\nextractROI {}\n{}\n-----------------------\n{}'.format(windowSize, image, roiImage)) 
    # logging.debug('####\nimage0 {} / image1 {} => len(image) {}'.format(image[0], image[1], len(image)))
    # logging.debug('####\nroiImage0 {} / roiImage1 {} => len(roiImage) {}'.format(roiImage[0], roiImage[1], len(roiImage)))
    return roiImage


def discretizeImage(image,noLevels):

    normalizedImage=image/255
    discretizedImage=np.floor(normalizedImage*noLevels).astype(int)
    multiplier=255/noLevels
    discretizedImage=np.floor(discretizedImage*multiplier).astype(np.uint8) #Rescale to range 0-255
    return discretizedImage


def imageToLEDNoColor(discreteImageRaw,pixels):

    pixelArray=np.zeros((len(discreteImageRaw),3))

    discreteImage0=discreteImageRaw[:,:,0]
    discreteImage0=discreteImage0.flatten()
    pixelArray[:,0]=discreteImage0
    discreteImage1=discreteImageRaw[:,:,1]
    discreteImage1=discreteImage1.flatten()
    pixelArray[:,1]=discreteImage1
    discreteImage2=discreteImageRaw[:,:,2]
    discreteImage2=discreteImage2.flatten()
    pixelArray[:,2]=discreteImage2

    pixelArray=pixelArray.astype(int) # Convert to int
    pixelTuple=[tuple(x) for x in pixelArray] #Convert to correctly dimensioned tuple array
    pixels[:]=pixelTuple
        
    return pixels

def imageToLED(discreteImageRaw,pixels,colorVal):
    
    discreteImage=discreteImageRaw[:,:,1]
    discreteImage=discreteImage.flatten()
    pixelArray=np.zeros((len(discreteImage),3))
    pixelArray[:,colorVal]=discreteImage
    pixelArray=pixelArray.astype(int) # Convert to int
    pixelTuple=[tuple(x) for x in pixelArray] #Convert to correctly dimensioned tuple array
    pixels[:]=pixelTuple
        
    return pixels
    

logging.basicConfig(level=logging.DEBUG)

#Parameters
xImageRes=400 #Desired x resolution of captured image
yImageRes=400 #120 #Desired y resolution of captured image
noLevels=255 #No of LED brightness discretization levels
numNeopixels_x = 400 #Declare number of Neopixels in grid
numNeopixels_y = 1
windowSize=(numNeopixels_x,numNeopixels_y) #Define extracted ROI size
xCenter=67#70 #x center location of ROI
yCenter=75#71 #y center location of ROI
thresh=50 #Threshold value for background subtraction
threshLower=0
threshUpper=200

colorVal=2 #R=0, G=1, B=2

pixelPin=board.D18
numPixels=numNeopixels_x*numNeopixels_y
colorOrder = neopixel.GRB
#pixels = neopixel.NeoPixel(pixelPin, numPixels, auto_write=False, pixel_order=colorOrder)

pixels = neopixel.NeoPixel(pixelPin, numPixels, brightness = 0.2)

logging.debug('numPixels %d', numPixels) 

#Initialize camera and fix settings
camera = PiCamera()
camera.resolution=(xImageRes,yImageRes)
# camera.framerate=30
rawCapture = PiRGBArray(camera, size=(xImageRes,yImageRes))
# #camera.vflip=True
# #camera.color_effects=(128,128) #Grayscale
# camera.contrast=100 #Contrast
# camera.brightness=1 #Brightness
# camera.iso = 600
# camera.meter_mode = 'matrix'
# sleep(2)
# camera.shutter_speed = camera.exposure_speed
# camera.exposure_mode = 'off'
# g = camera.awb_gains
# camera.awb_mode = 'off'
# camera.awb_gains = g
# sleep(1) #allow the camera to warm up


#Capture and process image
camera.capture(rawCapture,format="rgb",use_video_port=True) #Capture image
rawCapture.truncate(0) #Clear buffer for next frame capture

# image = rawCapture.array
# logging.debug('image {}'.format(image.shape)) 
# roiImage=image[:windowSize[0],:windowSize[1]]
# arri = np.array([[1,2,3,4,5], [5,6,7,8,9]])
# logging.debug('roiImage {}'.format(roiImage.shape)) 
# logging.debug('image.shape012 {} {} {}'.format(image.shape[0], image.shape[1], image.shape[2])) 

# newImageROI = extractROI(image,windowSize)
# pixels=imageToLED(newImageROI,pixels) #Convert the image to an LED value array and assign them to the string of Neopixels
# pixels.show() #Light up the LEDs



while 1:
    camera.capture(rawCapture,format="rgb",use_video_port=True) #Capture image
    newImage=rawCapture.array #Retrieve array of captured image as array
    newImageROI = extractROI(newImage,windowSize)
    discretizedImage=discretizeImage(newImageROI,noLevels) #Discretize image and scale values  
    pixels=imageToLED(discretizedImage,pixels,colorVal) #Convert the image to an LED value array and assign them to the string of Neopixels
    # pixels=imageToLEDNoColor(discretizedImage,pixels) #Convert the image to an LED value array and assign them to the string of Neopixels
    pixels.show() #Light up the LEDs
    rawCapture.truncate(0) #Clear stream to prepare for next frame

camera.close()