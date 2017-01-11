1- create a ros package. Here baxter_srv is the package name

       roscreate-pkg baxter_srv std_msgs rospy roscpp baxter_interface  sensor_msgs
       
       rosmake baxter_srv
       
       adjust your CMakeLists.txt file you have to uncomment rosbuild_genmsg() and rosbuild_gensrv()


2-add srv file:

       sensor_msgs/Image last_image



Right_hand_camera.py is the serive which should be running constantly and it gets the image from baxter' right-hand camera. 

To get the last image you should:

       rospy.wait_for_service('last_image')

       self.rightHandCamera = rospy.ServiceProxy('last_image', ImageSrv)

       request = self.rightHandCamera()

       imgmsg = request.last_image


An example to use this service is baxter.py in MIDCA/examples in Baxter branch
       
Getting help from this link:
http://nildo.github.io/organizer-baxter/
