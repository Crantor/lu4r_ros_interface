#!/usr/bin/env python
# encoding=utf8

# encoding=utf8

import rospy
from std_msgs.msg import String
import socket
import sys
import requests
import rospkg
import json
from math import radians, sin, cos
from geometry_msgs.msg import Pose2D
from geometry_msgs.msg import Twist
import xmltodict
import xdg_extract as xdg
import netifaces as ni

reload(sys)
sys.setdefaultencoding('utf8')

goal = Pose2D()
HEADERS = {'content-type': 'application/json'}
rospack = rospkg.RosPack()
directory = rospack.get_path('lu4r_ros_interface')

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
	["initial","start","beginning"],
	["kitchen","knife","oven","spoon","fork"],
	["bathroom","toilet","bath","sink","toothbrush",],
	['exit','door','escape']]

#BRINGING(beneficiary:"me",theme:"the book")

def interpretercallback(data):
	print 'Received: ' + data.data
	action = data.data.split('(')[0]
	content = data.data.split('(')[1].split(')')[0]

	# MOTION
	if action == possible_actions[13]:


	#predicates = xdg.find_predicates(response.text)
	# connection.send(predicates+'\r\n')
	#print predicates

def stateCallback(data):
	pass

def checkList(x,l):
	for elem in l:
		if elem == x:
			return True
		if isinstance(elem,list):
			return checkList(x,elem)
	return False


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
