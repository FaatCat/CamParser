import cv2
import sys
import thread
import os

from StringIO import StringIO
import requests
from PIL import Image
from bs4 import BeautifulSoup
import numpy

import pyaudio
import wave
import time
CHUNK = 1024
audio = pyaudio.PyAudio()

import pyttsx

from time import gmtime, strftime
	
DCS_IP = "192.168.0.9"
userauth = ('admin', 'Chaos123')
imgurl = "http://"+DCS_IP+"/image/jpeg.cgi"

cascPath = sys.argv[1]
faceCascade = cv2.CascadeClassifier(cascPath)


def main():
	framesIn30s = 0
	currentTime = time.time()
	while True:
		framesIn30s += 1
		if time.time() - currentTime > 30:
			print "FPS: {:6.3f}".format(framesIn30s / 30.0)
			currentTime = time.time()
			framesIn30s = 0
			
		# Capture frame-by-frame
		img = requests.get(imgurl, auth=userauth)
		i = Image.open(StringIO(img.content)).convert('RGB')

		opencv_image = numpy.array(i)
		opencv_image = opencv_image[:,:,::-1].copy()
		
		frame = opencv_image
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		
		faces = faceCascade.detectMultiScale(
			gray,
			scaleFactor=1.1,
			minNeighbors=5,
			minSize=(30, 30),
			flags=cv2.cv.CV_HAAR_SCALE_IMAGE
		)
		# Draw a rectangle around the faces
		for (x, y, w, h) in faces:
			cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
		if len(faces) > 0: 
			timestr = strftime("%Y%m%d%H%M%S", gmtime())
			dir = "fullbody/{}/".format(len(faces))
			ensure_dir(dir)
			cv2.imwrite(dir+timestr+".jpg", frame)
			print dir+timestr+".jpg"
			thread.start_new_thread(saySomething, (str(len(faces)) + " person detected.",))

		# Display the resulting frame
		cv2.imshow('Video', frame)

		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	# When everything is done, release the capture
	cv2.destroyAllWindows()

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)
		
def saySomething(something, voiceNumber=0, rate=70):
	engine = pyttsx.init()
	engine.setProperty('rate', rate)

	voices = engine.getProperty('voices')
	engine.setProperty('voice', voices[voiceNumber].id)
	engine.say(something)
	engine.runAndWait()

def playAudio(filename):
	wf = wave.open(filename,"rb")
	
	def callback(in_data, frame_count, time_info, status):
		data = wf.readframes(frame_count)
		
		return (data, pyaudio.paContinue)

	audioStream = audio.open(format=audio.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                stream_callback=callback)
	if audioStream.is_active():
		audioStream.stop_stream()
	audioStream.start_stream()
	

	# wait for stream to finish (5)
#	while audioStream.is_active():
#		time.sleep(0.1)
	
	
main()