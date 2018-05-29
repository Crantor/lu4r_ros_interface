lu4r\_ros\_interface
==============

This package enables for the communication between the [LU4R system][lu4r] and [ROS][ros]. This project is in charge of receiving the list of transcriptions from an external ASR and forward it to LU4R, and afterwards interpret each command to be able to move around a Pioneer 3-DX.

This ROS package provides tree different ROS nodes:

* `audiolistener`
* `simlab_interface`
* `simlab_interpreter`
* `rosarnl_node`[rosarnl]

In case of a simulation [MobileSim][mobilesim] will also be needed.


## `audiolistener`

Listens to what the user has to say, and communicates with an external ASR to receive a transcript. This transcript is later used by the simlab\_interface

## `simlab_interface`

Receives a transcript and communicates with the [LU4R server][lu4r], it then receives a parsed command. It will be interpreted by the simlab\_interpreter

#### Requirements

* [ROS][ros]
* [Python 2.7][python]
* [docker][docker] (Optional)


#### Run

Place the ROS package `lu4r_ros_interface` in your `catkin_ws/src` folder. Then, run

~~~
roscore
~~~

to start the ROS master. To start the [LU4R server][lu4r] In another terminal, run:

~~~
java -jar -Xmx1G lu4r.jar [type] [output] [language] [port] #in lu4r server path
~~~

Or if you want to use [docker][docker], add the LU4R server documents into a folder with the Dockerfile found in /docker folder and run the following commands in a terminal:

~~~
cd [PATH_TO_LU4R_DOCKER_FOLDER]
docker build --tag=lu4r-server .
docker run -it --rm -p 9090:9090 lu4r-server
~~~

Now all you have to do is run the roslaunch file. If you are running a simulation, run the following command in a terminal:

~~~
MobileSim -m [PATH_TO_MAP]
~~~

And run the roslaunch in another terminal
~~~
roslaunch lu4r_ros_interface simlab_launch_simulated.launch 
lu4r_ip:=[lu4r_ip_address] lu4r_port:=[lu4r_port] semantic_map:=[semantic_map]
~~~

where:

* `\_lu4r\_ip\_address`: the ip address of LU4R server. If the LU4R and the LU4R ROS interface are on the same machine, ignore this argument, as it is set to 127.0.0.1 by default.

* `\_lu4r\_port`: the listening port of LU4R server. It is set to 9090 by default.

* `\_semantic\_map`: the semantic map to be used, among the ones available into semantic\_maps. Semantic maps are in JSON format, representing the configuration of the environment (e.g. objects, locations,...) in which the robot is operating. Whenever a simple configuration of LU4R is chosen, the interpretation process is sensitive to different semantic maps. By default "semantic\_map1.txt".

---

If it's going to be runned in a Pioneer 3-DX robot, you have to make the robot run the following in serveral terminals:
~~~
roscore
~~~
and 

~~~
rosrun rosarnl rosarnl_node
~~~

Make sure that the host where the other nodes will be running has their ROS variables correctly definded. Run these commands to set them:

~~~
export ROS_IP=XXX.XXX.XXX.XXX # our IP
export ROS_HOSTNAME=XXX.XXX.XXX.XXX # our IP
export ROS_MASTER_URI=http://YYY.YYY.YYY.YYY:PORT # the remote machine IP (PORT by default is 11311, but it depends on the robot's configuration you use).
~~~

Once everything has beed configured, run 

~~~
roslaunch lu4r_ros_interface simlab_launch.launch 
lu4r_ip:=[lu4r_ip_address] lu4r_port:=[lu4r_port] semantic_map:=[semantic_map]
~~~

For more information, please visit the [LU4R system][lu4r] website, or take a look to the documentation found in the docs folder of this repository.

[lu4r]: http://sag.art.uniroma2.it/sluchain.html
[python]: https://www.python.org/
[ros]: http://www.ros.org/
[docker]: https://www.docker.com/
[rosarnl]: https://github.com/MobileRobots/ros-arnl
[mobilesim]: http://robots.mobilerobots.com/wiki/MobileSim
