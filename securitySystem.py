#!/usr/bin/python

import cv2
import numpy as np
import sys

PIXINCR=80
BUFFERSIZE=4 #Must be divisible by 3 APPARENTLY NOT
DIFFBITSTHRESH=300
DIFFBLOCKTHRESH=2
POSTMOTIONCYCLES=6


detect_buffer = None #buffer used for detecting in get_diffs_bw
raw_buffer = None #colored buffer taken alongside detect buffer for avi output
recording_buffer = None #frames from raw_buffer when detecting motion

def get_diffs_bw(detect_buffer):
  temp_buff = detect_buffer
  temp_buff_size = temp_buff.shape[0]
  diff_buff = None
  count = 0

  #Store contents of detect_buffer into a temp array
  #absdiff every third capture and throw it into a new temp array
  #Repeat until temp array has a size of 2, then return the bitwise and.
  while True:
    if temp_buff_size == 2:
      cummulativeFrames = cv2.bitwise_and(temp_buff[0], temp_buff[1])
      break
    else:
      count = 0 
      while count < (temp_buff_size / 3):

        diff1 = np.array([cv2.absdiff(temp_buff[(count*3)+2], temp_buff[(count*3)+1])])
        diff2 = np.array([cv2.absdiff(temp_buff[(count*3)+1], temp_buff[(count*3)+0])])

        if diff_buff == None:
          diff_buff = np.concatenate((diff1,diff2),axis=0)
        else:
          diff_buff = np.concatenate((diff_buff,diff1,diff2),axis=0)

        count+=1
    temp_buff = diff_buff 
    diff_buff = None
    temp_buff_size = temp_buff.shape[0]

  return cummulativeFrames


def get_num_diffs(cummulativeFrames):
  shape = cummulativeFrames.shape
  xMax = shape[0]
  yMax = shape[1]

  numBlocks = (xMax * yMax / PIXINCR)
  print numBlocks
  totalDiffs = np.sum(cummulativeFrames)
  totalDiffsAvg = totalDiffs / numBlocks
  print totalDiffsAvg

  xPos = 0 
  yPos = 0

  allDiffs = []

  #print "Starting diffs.."
  diff_count = 0
  while yPos < yMax:
    xPos = 0
    while xPos < xMax:
      chunk = cummulativeFrames[xPos:xPos+PIXINCR, yPos:yPos+PIXINCR]
      diffs = np.sum(chunk)
      diffs=1
      allDiffs.append(diffs)
      xPos+=PIXINCR

    yPos+=PIXINCR
   
    for diff in allDiffs: 
      if diff > totalDiffsAvg:
        diff_count+=1
  return diff_count

cam = cv2.VideoCapture(0)

winName = "Movement Indicator"
cv2.namedWindow(winName, cv2.CV_WINDOW_AUTOSIZE)


#detect_buffer = np.array([cv2.cvtColor(cam.read()[1], cv2.COLOR_RGB2GRAY)])
stop_count = 0
currently_recording = False
while True:
  print "STARTING FRAME CAPTURE"
  raw_buffer = np.array([cam.read()[1]])
  detect_buffer = np.array([cv2.cvtColor(raw_buffer[0], cv2.COLOR_RGB2GRAY)])
  #raw_buffer = rawCameraFrame
  print "ENDING INITIAL"

  for i in xrange(1,BUFFERSIZE):

    rawCameraFrame = np.array([cam.read()[1]])
    singleFrame = np.array([cv2.cvtColor(rawCameraFrame[0], cv2.COLOR_RGB2GRAY)])

    detect_buffer = np.concatenate((detect_buffer,singleFrame),axis=0)
    raw_buffer = np.concatenate((raw_buffer,rawCameraFrame),axis=0)

  print "GETTING BITWISE DIFFS"
  #Get bitwise of diffs from frames
  detect_buffer_diffs = get_diffs_bw(detect_buffer)

  #scans pixel block by pixel block for non b/w frames
  num_diffs = get_num_diffs(detect_buffer_diffs)
  if num_diffs > DIFFBLOCKTHRESH:
    stop_count = 0
    if currently_recording:
      print "Already recording. Adding block to buffer.."
      temp_buffer = np.concatenate((recording_buffer,raw_buffer),axis=0)
      recording_buffer = temp_buffer
    else:
      print "Starting new block from detect_buffer"
      recording_buffer = raw_buffer
      currently_recording = True
  else:
    if currently_recording:
      stop_count += 1
      if stop_count >= 5:
        print "Reached max time for no activity. Resetting recording buffer."

        fourcc = cv2.cv.CV_FOURCC(*'XVID')
        out = cv2.VideoWriter('output.avi',fourcc, 10, (640,480))
        
        num_frames = recording_buffer.shape[0]
        for i in xrange(0,num_frames):
          out.write(recording_buffer[i])

        currently_recording = False
        recording_buffer = None
        stop_count = 0
      else:
        print "Stop count at " + str(stop_count) + " out of 6. Adding to buffer.."
        temp_buffer = np.concatenate((recording_buffer,raw_buffer),axis=0)
        recording_buffer = temp_buffer

  cv2.imshow(winName,detect_buffer_diffs)

  key = cv2.waitKey(10)
  if key == 27:
    if recording_buffer:
      num_frames = recording_buffer.shape[0]
      for i in xrange(0,num_frames):
        out.write(recording_buffer[i])
 
    cv2.destroyWindow(winName)
    break

print "Goodbye"
