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
# from colr import color
# sudo -H pip install colr
import numpy as np
import board
import neopixel
import time
import logging

def extractROI(image,windowSize):
    global xImageRes
    global yImageRes
    x_startIdx=int(xImageRes/2-windowSize[0]/2)
    y_startIdx=int(yImageRes/2-windowSize[1]/2)
    x_endIdx=int(xImageRes/2+windowSize[0]/2)
    y_endIdx=int(yImageRes/2+windowSize[1]/2)
    roiImage=image[x_startIdx:x_endIdx,y_startIdx:y_endIdx,:]

    # roiImage=image[:windowSize[0],:windowSize[1],:]     # get as many columns and lines out of image as defined in windowSize
    # logging.debug('extractROI image {} ... roiImage {} ... windowSize{}'.format(len(image), len(roiImage), windowSize)) 
    # logging.debug('extractROI image {} ... roiImage {} ... windowSize{}'.format(image[:1], roiImage[:2], windowSize)) 
    return roiImage


def discretizeImage(image,noLevels):

    normalizedImage=image/255
    discretizedImage=np.floor(normalizedImage*noLevels).astype(int)
    multiplier=255/noLevels
    discretizedImage=np.floor(discretizedImage*multiplier).astype(np.uint8) #Rescale to range 0-255
    # logging.debug('discretizeImage \n--- image[:,:,0] {}\n--- normalizedImage {}'.format(image[:,:,0], normalizedImage)) 
    return discretizedImage


def imageToLED(discreteImageRaw,pixels):
    if debugItL: debug(time.perf_counter(), '- imageToLED') 
    
    discreteImage=discreteImageRaw[:,:,0]       # take element 0/3 from every discreteImageRaw element, 2 levels down
    discreteImage=discreteImage.flatten()       # image capture comes in single lines, we need everythin in one line for the led strip
    pixelArray=np.zeros((len(discreteImage),3)) # add one of the inner ones to pixelArray: [[0 0 0] [0 0 0] [0 0 0]]
    pixelArray[:,0]=discreteImage               # add flattened array to element 0/3, 1 level down
    if debugItL: debug(time.perf_counter(), '- 0') 

    discreteImage=discreteImageRaw[:,:,1]
    discreteImage=discreteImage.flatten()
    pixelArray[:,1]=discreteImage
    if debugItL: debug(time.perf_counter(), '- 1') 

    discreteImage=discreteImageRaw[:,:,2]
    discreteImage=discreteImage.flatten()
    pixelArray[:,2]=discreteImage
    if debugItL: debug(time.perf_counter(), '- 2') 

    # logging.debug('{} / pixelArray {}'.format(len(discreteImage), pixelArray))
    # logging.debug('x {}'.format(time.perf_counter()))
    # logging.debug('imageToLED pixelArray[0] {}'.format(pixelArray[0]))
    # logging.debug('imageToLED \n--- len(pixelArray) {}\n--- pixelArray[0] {}'.format(len(pixelArray), pixelArray[0]))

    pixelArray=pixelArray.astype(int) # Convert to int
    # logging.debug('pixelArray int {}'.format(pixelArray))
    if debugItL: debug(time.perf_counter(), '- Convert to int')
    # logging.debug('pixelArray {}'.format(pixelArray))

    # pixelTuple=[tuple(x) for x in pixelArray] # Convert to correctly dimensioned tuple array
    # logging.debug('pixelTuple {}'.format(pixelTuple))
    # if debugItL: debug(time.perf_counter(), '- Convert to tuple array') 

    # pixels[:]=pixelTuple    # add every single tuple element into pixels (of type NeoPixel) on level 1 (each one are the colors of a pixel)
    pixels[:]=pixelArray    # add every single array element into pixels (of type NeoPixel) on level 1 (each one are the colors of a pixel)
    # logging.debug('pixels {} / pixelArray {}'.format(pixels, pixelArray))
    if debugItL: debug(time.perf_counter(), '- assign to pixels') 
        
    return pixels


def debug(newtime, msg):
    global comparetime
    logging.debug('{}: ({}) {}'.format(newtime, round(newtime-comparetime, 2), msg))
    comparetime = newtime

logging.basicConfig(level=logging.DEBUG)

#Parameters
xImageRes=50 #Desired x resolution of captured image
yImageRes=50 #120 #Desired y resolution of captured image
noLevels=255 #No of LED brightness discretization levels
numNeopixels_x = 6 #Declare number of Neopixels in grid
numNeopixels_y = 50
windowSize=(numNeopixels_x,numNeopixels_y) #Define extracted ROI size
# xCenter=67#70 #x center location of ROI
# yCenter=75#71 #y center location of ROI
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
sleep(1) #allow the camera to warm up


#Capture and process image
camera.capture(rawCapture,format="rgb",use_video_port=True) #Capture image
rawCapture.truncate(0) #Clear buffer for next frame capture

comparetime = time.perf_counter()
oldtime = time.perf_counter()
fpsCounter = 0

debugMain = False
debugItL = False

while 1:
    if debugMain: debug(time.perf_counter(), '-') 
    camera.capture(rawCapture,format="rgb",use_video_port=True) #Capture image
    if debugMain: debug(time.perf_counter(), 'capture')
    newImage=rawCapture.array #Retrieve array of captured image as array
    if debugMain: debug(time.perf_counter(), 'array')
    newImageROI = extractROI(newImage,windowSize)
    if debugMain: debug(time.perf_counter(), 'roi')
    discretizedImage=discretizeImage(newImageROI,noLevels) #Discretize image and scale values 
    if debugMain: debug(time.perf_counter(), 'discretize') 
    pixels=imageToLED(discretizedImage,pixels) #Convert the image to an LED value array and assign them to the string of Neopixels
    if debugMain: debug(time.perf_counter(), 'imageToLED') 
    pixels.show() #Light up the LEDs
    if debugMain: debug(time.perf_counter(), 'show') 
    rawCapture.truncate(0) #Clear stream to prepare for next frame
    fpsCounter += 1
    newtime = time.perf_counter()
    if (newtime - oldtime > 1):
        logging.debug('{} fps from {} until {}'.format(fpsCounter, oldtime, newtime))
        oldtime = newtime
        fpsCounter = 0


camera.close()