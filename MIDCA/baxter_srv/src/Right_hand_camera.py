#!/usr/bin/env python

import roslib;roslib.load_manifest('baxter_srv')
import rospy
import baxter_interface
from sensor_msgs.msg import Image
from baxter_srv.srv import ImageSrv, ImageSrvResponse

class ImgService:
	def imgReceived(self, message):
		"""
		Callback for when an image is received.

		"""
		self.lastImage = message
		#print("Sending image")
		#self.pub.publish(self.lastImage)

	def getLastImage(self, request):
		"""
		Return the last image

		"""
		return ImageSrvResponse(self.lastImage)

	def __init__(self):
		"""
		Construtor: initializes node, subscribe to Baxter's right hand camera
		topic and create the service.

		"""
		self.lastImage = None;
		rospy.init_node('right_hand_camera')
		
		cameraController = baxter_interface.CameraController("right_hand_camera")
		#cameraController.close()
		#cameraController.resolution= (1280,800)
		#cameraController.open()

		rospy.Subscriber("/cameras/right_hand_camera/image", Image, self.imgReceived)
		#self.pub = rospy.Publisher('/image_cmd', Image, queue_size=10)
		
		rospy.Service('last_image', ImageSrv, self.getLastImage)

	def run(self):
		rospy.spin()

if __name__ == '__main__':
	node = ImgService()
	node.run()



