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
				'TAKING',						# 17
				'BRINGING1',					# 18 (CUSTOM MADE)
				'BRINGING2'						# 19 (CUSTOM MADE)

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

# Checks if the robot is working in a task
isWorking = False
# Tuple containing the order and the target the robot needs to go
current_target = ("","")
# Tuple containing the last order executed with the target the robot was.
last_target = ("","")
# Objects the robot needs to take from the environment.
objects_to_be_taken = []


# Bringing function
def bringing_command(action,content):
	global current_target
	global last_target
	global command_list
	global objects_to_be_taken

	# Deparsing the content
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
	# In case the object is recognized
	if index != -1:
		goal = goals[index][0]
		bringing_object = objects_to_be_taken[len(objects_to_be_taken)-1]
		# Giving order to go to the indicated goal
		print("BRINGING: Bring the " + bringing_object)
		# No order given yet. First time executing robot
		if last_target == ("",""):
			# Adding "Bringing1 to last_target"
			last_target = (possible_actions[18],"start")

		#  There are orders in the command list. Gets the last place where the robot is going to be if there are more commands
		if len(command_list) > 0:
			return_object_to = command_list[len(command_list)-1][1]
		# In case the robot has no target go to the last visited target
		elif current_target == ("",""):
			return_object_to = last_target[1]
		# In case the robot is going to a target has to return the object to it
		else:
			return_object_to = current_target[1]


		# Changing the location of the object
		# Removing object from object list
		objects[index].remove(bringing_object)

		# Getting index of the goal
		g_aux = [goals[i][0] for i,_ in enumerate(goals)]
		indexAdd = g_aux.index(return_object_to)
		# Adding the object to the new location
		objects[indexAdd].append(bringing_object)

		# Adding the target and the return target to the command_list.
		command_list.append((possible_actions[18], goal))				# BRINGING1
		command_list.append((possible_actions[19], return_object_to))	# BRINGING2


	# In case the object is not recognized
	else:
		print("I did not understand you, please repeat.")


def motion_command(action,content):
	global command_list

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

def stop_command():
	global isWorking
	global current_target
	global last_target
	global command_list
	global objects_to_be_taken

	# reinitialize variables
	command_list = []
	isWorking = False
	last_target = current_target # last visited target
	current_target = ("","")
	objects_to_be_taken = []

	# stops the robot
	os.system('rosservice call /rosarnl_node/stop')

def release_command(action,content):
	global command_list

	content = content.split(":")[1]
	content = content.replace("\"","")
	# Splitting content into words
	content = content.split(" ")

	# variable to check if a word is found
	found = False
	# Checking if any of the words is kraken
	for word in content:
		if word.lower() == "kraken":
			command_list.append((action, "kraken1"))
			command_list.append((action, "kraken2"))
			command_list.append((action, "kraken3"))
			command_list.append((action, "kraken4"))
			found = True
			break

	# in case it is not found
	if not found:
		print("I did not understand you, please repeat.")
	# reinitialize found
	found = False

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
		# Getting content
		content = getContent()
		# Executing bringing command
		bringing_command(action, content)

    # CHANGE_OPERATIONAL_STATE (STOP)
	if action == possible_actions[6]:
		stop_command()

	# MOTION
	# Example of transcription received: MOTION(goal:"to the bathroom")
	if action == possible_actions[13]:
		# Getting whole content
		content = getContent()
		# Executing Motion Command
		motion_command(action, content)

	# RELEASING
	# Example of transcription received: RELEASING(theme:"the Kraken")
	if action == possible_actions[16]:
		# Getting whole content
		content = getContent()
		release_command(action, content)

	# Start moving when it has stopped, or it's moving for the first time.
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

		# Establishes the last visited target
		last_target = current_target

		# In case there are no commands it stops working
		if len(command_list) == 0:
			isWorking = False
			current_target = ("","")
		# In case it has to do more actions, it does the next one
		else:
			# In case it is a BRINGING1 action, it has to return and request the object
			if (current_target[0] == possible_actions[18]):
				print("Give me the " + objects_to_be_taken.pop(0))
			#elif (current_target[0] == possible_actions[19]):

			# Establishes the new target and publishes it
			current_target = command_list.pop(0)
			pub.publish(current_target[1])

def checkList(x,l):
	for elem in l:
		if x.lower() in elem:
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
