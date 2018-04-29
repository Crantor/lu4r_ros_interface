#!/usr/bin/env python
# NOTE: this example requires PyAudio because it uses the Microphone class

import sys
import select
import os
import speech_recognition as sr
import json
import rospy
from std_msgs.msg import String

r = None
m = None

def init():
	global r
	global m
	global pub
	rospy.init_node('audiolistener', anonymous=True)
	r = sr.Recognizer()
	m = sr.Microphone()
	with m as source:
		r.adjust_for_ambient_noise(source)
	pub = rospy.Publisher('/audio',String, queue_size = 1000)


def listen():
	with m as source:
		audio = r.listen(source)
	try:
		voice_command = r.recognize_google(audio, None, "en", True)
	except sr.UnknownValueError:
		print("Google Speech Recognition could not understand audio")
	except sr.RequestError as e:
		print("Could not request results from Google Speech Recognition service; {0}".format(e))

	if isinstance(voice_command,dict):
		print voice_command
		j = 1
		for i in voice_command['alternative']:
			i['rank'] = j # the first one will always take rank 1, the most realiable transcription.
			j = j + 1
			if not 'confidence' in i.keys():
				i['confidence'] = 0 # As google just returns one value with confidence it has to be added
		voice_command = json.dumps(voice_command['alternative']) # converted into json format
		voice_command = '{"hypotheses":' + voice_command.replace("transcript","transcription")+'}' # transcript key changed to transcription, added hypo key
		print "Voice command string: " + voice_command
		pub.publish(voice_command)
	else:
		print voice_command

if __name__ == '__main__':
	init()
	while True:
		print "Press Enter to start listening, type \"quit\" to exit..."
		line = raw_input()
		if "quit" in line:
			break
		print "..say something!"
		listen()
