#!/usr/bin/env python
# encoding=utf8

import rospy
from std_msgs.msg import String
import sys
import os

reload(sys)
sys.setdefaultencoding('utf8')

#Subscriber
sub_interpreter = None
sub_arnl = None

# Publisher (RosARNL)
pub = None

possible_actions = ['ARRIVING',                	# 0
				'ATTACHING',    			   	# 1
				'BEING_IN_CATEGORY',			# 2
				'BEING_LOCATED', 				# 3
				'BRINGING', 					# 4
				'CHANGE_DIRECTION', 			# 5
				'CHANGE_OPERATIONAL_STATE', 	# 6
				'CLOSURE', 						# 7
				'COTHEME', 						# 8
				'GIVING', 						# 9
				'INSPECTING',					# 10
				'LOCATING', 					# 11
				'MANIPULATING', 				# 12
				'MOTION', 						# 13
				'PERCEPTION_ACTIVE',			# 14
				'PLACING', 						# 15
				'RELEASING',					# 16
				'TAKING'						# 17
				]

command_list = []
goals = [
	["Goal0","initial","start","beginning"],
	["Goal1","kitchen"],
	["Goal2","bathroom","toilet","bath","sink"],
	["Goal3","exit","door","escape"]]

objects = [
	["Goal0","book"],
	["Goal1","knife","oven","spoon","fork","food"],
	["Goal2","toothbrush","soap"],
	["Goal3","mobile"]]

isWorking = False
current_target = ("","")
last_target = ("","")
objects_to_be_taken = []

def interpretercallback(data):
	global isWorking
	global current_target
	global last_target
	global command_list
	global objects_to_be_taken

	def getContent():
		return data.data.split('(')[1].split(')')[0]

	print 'Received: ' + data.data
	action = data.data.split('(')[0]
	# content = data.data.split('(')[1].split(')')[0]

	# BRINGING
	# Example of transcription received: BRINGING(beneficiary:"me",theme:"the book")
	if action == possible_actions[4]:
		# Getting whole content
		content = getContent()
		content = content.split("theme:")[1]
		content = content.replace("\"","")
		# Splitting content into words
		content = content.split(" ")

		# Checking if any of the words is an object
		for word in content:
			index = checkList(word, objects)
			if index != -1:
				objects_to_be_taken.append(word)
				break

		if index != -1:
			goal = goals[index][0]

			# Giving order to go to the indicated goal
			print("BRINGING: Bring the " + objects_to_be_taken[len(objects_to_be_taken)-1])

			if last_target == ("",""):
				last_target = ("BRINGING1","start")

			if len(command_list) > 0:
				return_object_to = command_list[len(command_list)-1][1]
			elif current_target == ("",""):
				return_object_to = last_target[1]
			else:
				return_object_to = current_target[1]

			command_list.append((action+"1", goal))
			command_list.append((action+"2", return_object_to))

		else:
			print("I did not understand you, please repeat.")

    # CHANGE_OPERATIONAL_STATE (STOP)
	if action == possible_actions[6]:
		command_list = []
		isWorking = False
		last_target = current_target
		current_target = ("","")
		objects_to_be_taken = []
		os.system('rosservice call /rosarnl_node/stop')

	# MOTION
	# Example of transcription received: MOTION(goal:"to the bathroom")
	if action == possible_actions[13]:
		# Getting whole content
		content = getContent()
		content = content.split(":")[1]
		content = content.replace("\"","")
		# Splitting content into words
		content = content.split(" ")

		# Checking if any of the words is a goal
		for word in content:
			index = checkList(word, goals)
			if index != -1:
				break

		if index != -1:
			goal = goals[index][0]
			# Giving order to go to the indicated goal
			print("MOTION: Going to ",goal)
			command_list.append((action, goal))

		else:
			print("I did not understand you, please repeat.")

	# RELEASING
	# Example of transcription received: RELEASING(theme:"the Kraken")


	if not isWorking and len(command_list) is not 0:
		isWorking = True
		# Sending work to the arnl node
		current_target = command_list.pop(0)
		last_target = current_target
		pub.publish(current_target[1]) # Getting First command.

def stateCallback(data):
	global isWorking
	global current_target
	global last_target
	global command_list
	global objects_to_be_taken

	if(data.data) == "REACHED_GOAL":

		last_target = current_target

		if len(command_list) == 0:
			isWorking = False
			current_target = ("","")
		else:

			if (current_target[0] == "BRINGING1"):
				print("Give me the " + objects_to_be_taken.pop(0))

			current_target = command_list.pop(0)
			pub.publish(current_target[1])

def checkList(x,l):
	for elem in l:
		if x in elem:
			return l.index(elem)
	return -1

def listener():
	global sub_interpreter
	global sub_arnl
	global pub

	rospy.init_node('simlab_interpreter', anonymous=True)
	sub_interpreter = rospy.Subscriber('/interpretation', String, interpretercallback)
	sub_arnl = rospy.Subscriber('/rosarnl_node/arnl_path_state', String, stateCallback)
	pub = rospy.Publisher('/rosarnl_node/goalname',String, queue_size = 1000)

	rospy.spin()

if __name__ == '__main__':
	listener()
