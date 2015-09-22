from __future__ import print_function

# Import the necessary Python modules
import sys
import math
import numpy as np
import time

# rospy - ROS Python API
import rospy

# baxter_interface - Baxter Python API
import baxter_interface

#Message carrying location of target
from geometry_msgs.msg import Point
from std_msgs.msg import String
from MIDCA import rosrun
from MIDCA.modules._plan.asynch import asynch
from MIDCA.examples.baxter import * 

limb = None
feedbackPub = None
baxter = Baxter() # The object that controls Baxter. Defined in baxter.py.

def midca_feedback(**kwargs):
    msg = rosrun.dict_as_msg(kwargs)
    feedbackPub.publish(msg)

def MoveArm(point):
    
    #o1 = [0.9912059087997489, 0.12898810957822202, -0.016456430713070586, 0.02453772271597873]
    #o1 = [-0.04504873726153096, 0.9983659324956183, 0.020392051958720396, -0.028639837992011533]
    o1 = [-0.03949261067902856, 0.9985084494945174, 0.00941780098092878, -0.03650363015499998]
    print('point =', point)
    
    #[0.9858036680068526, 0.15518960733015813, -0.06358533543017306, 0.008013678255261263]
    return baxter.moveLeftArm(point, o1)
    
    
    
def Grasp():
    baxter.closeLeftGripper()
    return True

def point_2_callback(point, cmd_id = 'point_2_def_id'):
    
    if point.x == 0 and point.y == 0 and point.z == 0:
        rospy.loginfo("Point: got a stop command (all zeros)")
    else:
        rospy.loginfo("Point: setting target to" + str(point))
        
        if(MoveArm(point)== None):
            rospy.loginfo("Point: target out of pointing range " + str(point))
            midca_feedback(cmd_id = cmd_id, code = asynch.FAILED)
        
        else:
            baxter.openLeftGripper()
            midca_feedback(cmd_id = cmd_id, code = asynch.COMPLETE)
            
        #limb.move_to_joint_positions(angles) #blocking
#     else:
#         rospy.loginfo("Point: target out of pointing range " + str(data))
#         midca_feedback(cmd_id = cmd_id, code = asynch.FAILED)

def msg_callback(point, cmd_id = 'grasp_id'):
    
        Grasp()
        
        midca_feedback(cmd_id = cmd_id, code = asynch.COMPLETE)
        #limb.move_to_joint_positions(angles) #blocking
#     else:
#         rospy.loginfo("Point: target out of pointing range " + str(data))
#         midca_feedback(cmd_id = cmd_id, code = asynch.FAILED)

def point_callback(point, cmd_id = 'point_def_id'):
    
    if point.x == 0 and point.y == 0 and point.z == 0:
        rospy.loginfo("Point: got a stop command (all zeros)")
    else:
        rospy.loginfo("Point: setting target to" + str(point))

        if(MoveArm(point)== None):
            rospy.loginfo("Point: target out of pointing range " + str(point))
            midca_feedback(cmd_id = cmd_id, code = asynch.FAILED)
        
        else:
            midca_feedback(cmd_id = cmd_id, code = asynch.COMPLETE)
        #limb.move_to_joint_positions(angles) #blocking
#     else:
#         rospy.loginfo("Point: target out of pointing range " + str(data))
#         midca_feedback(cmd_id = cmd_id, code = asynch.FAILED)
def reaching_callback(data):
    print("got msg:", data)
    msg = data.data
    d = rosrun.msg_as_dict(msg)
    
    if not 'x' in d and 'y' in d and 'z' in d and 'cmd_id' in d:
        rospy.logerr("Msg received by grabbing node, but it does not contain" +
        "keys 'x', 'y', 'z', 'cmd_id'. Msg will be ignored.")
        midca_feedback(cmd_id = d['cmd_id'], code = asynch.FAILED)
    else:
        try:
            point = Point(x = d['x'], y = d['y'], z = d['z'])
            
        except NumberFormatException:
            rospy.logerr("Msg received by grabbing nodes, but target coordinates" +
                         " are not well-formed. Msg will be ignored.")
            midca_feedback(cmd_id = d['cmd_id'], code = asynch.FAILED)
            return
        point_callback(point, d['cmd_id'])
        
def raising_callback(data):
    print("got msg:", data)
    msg = data.data
    d = rosrun.msg_as_dict(msg)
    
    if not 'x' in d and 'y' in d and 'z' in d and 'cmd_id' in d:
        rospy.logerr("Msg received by grabbing node, but it does not contain" +
        "keys 'x', 'y', 'z', 'cmd_id'. Msg will be ignored.")
        midca_feedback(cmd_id = d['cmd_id'], code = asynch.FAILED)
    else:
        try:
            point = Point(x = d['x'], y = d['y'], z = d['z'])
            
            
        except NumberFormatException:
            rospy.logerr("Msg received by grabbing nodes, but target coordinates" +
                         " are not well-formed. Msg will be ignored.")
            midca_feedback(cmd_id = d['cmd_id'], code = asynch.FAILED)
            return
        point_2_callback(point, d['cmd_id'])
        

def grabbing_callback(data):
    print("got msg:", data)
    msg = data.data
    d = rosrun.msg_as_dict(msg)
    
    msg_callback(msg, d['cmd_id'])
    

    
def start_node(targetTopic, limbName = 'left'):
    rospy.init_node('baxter_grabbing')
    rospy.loginfo("Reading point commands from topic " + targetTopic)
    #rospy.Subscriber(targetTopic, String, fake_point) 
    rospy.Subscriber("loc_cmd", String, reaching_callback)    
    rospy.Subscriber("grabbing_cmd", String, grabbing_callback)
    rospy.Subscriber("raise_cmd", String, raising_callback)
    
    baxter.initiate()
    
    #origin = baxter.getLeftArmPosition()
    
    
    global feedbackPub
    feedbackPub = rospy.Publisher(rosrun.FEEDBACK_TOPIC, String, queue_size = 10)
    #limb = baxter_interface.Limb(limbName)
    rospy.spin()


if __name__ == '__main__':
    #test_angle_finder()
    #sys.exit()
    if len(sys.argv) > 2:
        raise Exception("Usage: 1 optional argument giving the topic on which commands are broadcast.")
    elif len(sys.argv) == 2:
        topic = sys.argv[1]
    else:
        topic = "loc_cmd"
    try:
        start_node(topic)
    except rospy.ROSInterruptException:
        pass