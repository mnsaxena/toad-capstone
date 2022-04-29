# MIT License
# Copyright (c) 2019-2022 JetsonHacks

# A simple code snippet
# Using two  CSI cameras (such as the Raspberry Pi Version 2) connected to a
# NVIDIA Jetson Nano Developer Kit with two CSI ports (Jetson Nano, Jetson Xavier NX) via OpenCV
# Drivers for the camera and OpenCV are included in the base image in JetPack 4.3+

# This script will open a window and place the camera stream from each camera in a window
# arranged horizontally.
# The camera streams are each read in their own thread, as when done sequentially there
# is a noticeable lag

from re import T
from time import sleep
import cv2
import threading
import numpy as np
import socket

class CSI_Camera:

    def __init__(self):
        # Initialize instance variables
        # OpenCV video capture element
        self.video_capture = None
        # The last captured image from the camera
        self.frame = None
        self.grabbed = False
        # The thread where the video capture runs
        self.read_thread = None
        self.read_lock = threading.Lock()
        self.running = False
        # Aruco Vars
        self.arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
        self.arucoParams = cv2.aruco.DetectorParameters_create()

        #socket Config
        self.sockrunning = False
        self.socket = socket.socket()
        self.HOST = '192.168.1.5' #Configured Static IP of the raspi
        self.PORT = 2022 #Must be the same number as the raspi port
        self.connReset = False

    def open(self, gstreamer_pipeline_string):
        try:
            self.video_capture = cv2.VideoCapture(
                gstreamer_pipeline_string, cv2.CAP_GSTREAMER
            )
            # Grab the first frame to start the video capturing
            self.grabbed, self.frame = self.video_capture.read()

        except RuntimeError:
            self.video_capture = None
            print("Unable to open camera")
            print("Pipeline: " + gstreamer_pipeline_string)


    def start(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            if self.sockrunning:
                print("ERROR | Socket is already running")
            else:    
                attempt = 0            
                while attempt < 200:
                    try:
                        attempt += 1
                        print("INFO | Attempting to Connect to Server... Attempt", attempt)
                        self.socket.connect((self.HOST, self.PORT))
                        print("INFO | Connected")
                        self.sockrunning = True
                        break
                    except ConnectionRefusedError:
                        pass
                    
                    sleep(2)
                
                if not self.sockrunning:
                    raise ConnectionRefusedError("Connection Timed out")
                

        except RuntimeError as error:
            print("ERROR | Occured when connecting to server: ", error)
            
        if self.running:
            print('Video capturing is already running')
            return None
        # create a thread to read the camera image
        if self.video_capture != None:
            self.running = True
            self.read_thread = threading.Thread(target=self.updateCamera)
            self.read_thread.start()
        return self

    def stop(self):
        self.running = False
        # Kill the thread
        self.read_thread.join()
        self.read_thread = None

    def updateCamera(self):
        # This is the thread to read images from the camera
        while self.running:
            try:
                grabbed, frame = self.video_capture.read()
                with self.read_lock:
                    self.grabbed = grabbed
                    self.frame = frame #cv2.fastNlMeansDenoisingColored(frame, None, 10, 10, 7, 21)
                (corners, ids, rejected) = cv2.aruco.detectMarkers(self.frame, self.arucoDict, parameters=self.arucoParams)
                if len(corners) > 0:
                    ids = ids.flatten()
                    for (marker_corner, marker_id) in zip(corners, ids):
                        # Extract the marker corners
                        corners = marker_corner.reshape((4, 2))
                        (top_left, top_right, bottom_right, bottom_left) = corners
                        
                        # Convert the (x,y) coordinate pairs to integers
                        top_right = (int(top_right[0]), int(top_right[1]))
                        bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
                        bottom_left = (int(bottom_left[0]), int(bottom_left[1]))
                        top_left = (int(top_left[0]), int(top_left[1]))
                        
                        # Draw the bounding box of the ArUco detection
                        cv2.line(self.frame, top_left, top_right, (0, 255, 0), 2)
                        cv2.line(self.frame, top_right, bottom_right, (0, 255, 0), 2)
                        cv2.line(self.frame, bottom_right, bottom_left, (0, 255, 0), 2)
                        cv2.line(self.frame, bottom_left, top_left, (0, 255, 0), 2)
                        
                        # Calculate and draw the center of the ArUco marker
                        center_x = int((top_left[0] + bottom_right[0]) / 2.0)
                        center_y = int((top_left[1] + bottom_right[1]) / 2.0)
                        cv2.circle(self.frame, (center_x, center_y), 4, (0, 0, 255), -1)

                        message = str((center_x,center_y)) + str(top_left) + str(bottom_right)
                        # message = (center_x,center_y),top_left,bottom_right
                        message = str(message)
                        #print('-------'+ message+ '`----')
                        try:
                            self.socket.send(message.encode())
                        except ConnectionResetError:
                            self.connReset = True
                            raise

                        # Draw the ArUco marker ID on the video frame
                        # The ID is always located at the top_left of the ArUco marker
                        cv2.putText(self.frame, str(marker_id), 
                        (top_left[0], top_left[1] - 15),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (0, 255, 0), 2)    
                else:
                    #print("NaN") 
                    message = "NaN"
                    try:
                        self.socket.send(message.encode())   
                    except ConnectionResetError:
                        self.connReset = True
                        raise
            except RuntimeError:
                print("Could not read image from camera")
        # FIX ME - stop and cleanup thread
        # Something bad happened

    def read(self):
        with self.read_lock:
            frame = self.frame.copy()
            grabbed = self.grabbed
            errorstate = self.connReset
        return grabbed, frame, errorstate

    def release(self):
        if self.video_capture != None:
            self.video_capture.release()
            self.video_capture = None
        if self.socket != None:
            if not self.connReset:
                message = "stop"
                self.socket.send(message.encode())   
                self.socket.shutdown(socket.SHUT_RDWR)
                self.socket.close()
        # Now kill the thread
        if self.read_thread != None:
            self.read_thread.join()


""" 
gstreamer_pipeline returns a GStreamer pipeline for capturing from the CSI camera
Flip the image by setting the flip_method (most common values: 0 and 2)
display_width and display_height determine the size of each camera pane in the window on the screen
Default 1920x1080
"""


def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1920,
    capture_height=1080,
    display_width=1920,
    display_height=1080,
    framerate=25,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d ! "
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


def run_cameras():
    window_title = "Dual CSI Cameras"
    left_camera = CSI_Camera()
    left_camera.open(
        gstreamer_pipeline(
            sensor_id=0,
            capture_width=1920,
            capture_height=1080,
            flip_method=0,
            display_width=1920, #960,
            display_height=1080, #540,
        )
    )
    left_camera.start()

    '''
    right_camera = CSI_Camera()
    right_camera.open(
        gstreamer_pipeline(
            sensor_id=1,
            capture_width=1920,
            capture_height=1080,
            flip_method=0,
            display_width=960,
            display_height=540,
        )
    )
    right_camera.start()
    '''

    if left_camera.video_capture.isOpened(): #and right_camera.video_capture.isOpened():

        cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE)

        try:
            while True:
                _, left_image, errorstate = left_camera.read()
                #_, right_image = right_camera.read()
                # Use numpy to place images next to each other
                camera_images = left_image #np.hstack((left_image, right_image)) 
                # Check to see if the user closed the window
                # Under GTK+ (Jetson Default), WND_PROP_VISIBLE does not work correctly. Under Qt it does
                # GTK - Substitute WND_PROP_AUTOSIZE to detect if window has been closed by user
                if cv2.getWindowProperty(window_title, cv2.WND_PROP_AUTOSIZE) >= 0:
                    cv2.imshow(window_title, camera_images)
                else:
                    break

                # This also acts as
                keyCode = cv2.waitKey(30) & 0xFF
                # Stop the program on the ESC key
                if keyCode == 27:
                    break
                if errorstate:
                    break
        finally:

            left_camera.stop()
            left_camera.release()
            #right_camera.stop()
            #right_camera.release()
        cv2.destroyAllWindows()
    else:
        print("Error: Unable to open both cameras")
        left_camera.stop()
        left_camera.release()
        #right_camera.stop()
        #right_camera.release()



if __name__ == "__main__":
    while True:
        run_cameras()
        print("Camera Closed, Waiting before restart...")
        sleep(6)
