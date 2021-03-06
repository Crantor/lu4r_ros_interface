#!/usr/bin/env python
# encoding=utf8

import rospy
from std_msgs.msg import String
import sys
import requests
import rospkg
import json
from geometry_msgs.msg import Pose2D

reload(sys)
sys.setdefaultencoding('utf8')

semantic_map = {}
HEADERS = {'content-type': 'application/json'}
rospack = rospkg.RosPack()
directory = rospack.get_path('lu4r_ros_interface')

#Subscriber (Audio)
sub = None

#Publisher (Interpreter)
pub = None

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
	if(response.text is not 'NO FRAME(S) FOUND'):
		pub.publish(response.text)
	else:
		print('Lu4r server could not understand the command.')


def listener():
	global semantic_map
	global sub
	global lu4r_ip
	global lu4r_port
	global lu4r_url
	global entities
	global pub

	rospy.init_node('simlab_interface', anonymous=True)
	rospy.Subscriber('/audio', String, inputaudiocallback)
	pub = rospy.Publisher('/interpretation',String, queue_size = 1000)

	lu4r_ip = rospy.get_param("~lu4r_ip", '127.0.0.1')
	print lu4r_ip
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
