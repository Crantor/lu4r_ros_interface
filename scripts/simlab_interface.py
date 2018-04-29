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

connection = None
semantic_map = {}
goal = Pose2D()
HEADERS = {'content-type': 'application/json'}
rospack = rospkg.RosPack()
directory = rospack.get_path('lu4r_ros_interface')

#Subscriber
sub = None

#default values for connection
lu4r_ip = '127.0.0.1'
lu4r_port = '9090'
lu4r_url = 'http://127.0.0.1:9090/service/nlu'

#entities set to none by default
entities = None

def inputaudiocallback(data):
	print 'Received: ' + data.data
	to_send = {'hypo': data.data, 'entities': entities}
	response = requests.post(lu4r_url, to_send, headers=HEADERS)
	print response.text
	#predicates = xdg.find_predicates(response.text)
	# connection.send(predicates+'\r\n')
	#print predicates

def listener():
	global semantic_map
	global connection
	global sub
	global lu4r_ip
	global lu4r_port
	global lu4r_url
	global entities

	rospy.init_node('simlab_interface', anonymous=True)
	rospy.Subscriber('/audio', String, inputaudiocallback)

	lu4r_ip = rospy.get_param("~lu4r_ip", '127.0.0.1')
	lu4r_port = rospy.get_param("~lu4r_port", '9090')
	lu4r_url = 'http://' + lu4r_ip + ':' + str(lu4r_port) + '/service/nlu'

	#loading entities
	sem_map = rospy.get_param('~semantic_map', 'semantic_map1.txt')
	entities = open(directory + "/semantic_maps/" + sem_map).read()
	json_string = json.loads(entities)
	print 'Entities into the semantic map:'
	for entity in json_string['entities']:
		semantic_map[entity['type']] = Pose2D()
		semantic_map[entity['type']].x = entity["coordinate"]["x"]
		semantic_map[entity['type']].y = entity["coordinate"]["y"]
		semantic_map[entity['type']].theta = entity["coordinate"]["angle"]
		print '\t' + entity['type']
		print str(semantic_map[entity['type']])
		print

	rospy.spin()

if __name__ == '__main__':
	listener()
