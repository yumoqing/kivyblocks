from kivy.uix.camera import Camera
from kivy.properties import BooleanProperty, NumericProperty
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
import kivy
import numpy as np
import cv2
from kivy.base import Builder
from .image_processing.image_processing import face_detection

btxt = """<CustomCamera>:
	resolution: (1920,1050)
	play: True
	keep_ratio: True
	allow_stretch: True
	canvas.before:
		PushMatrix
		Rotate:
			angle: root.angle
			axis: 0, 0, 1
			origin: root.center
	canvas.after:
		PopMatrix
"""

class CustomCamera(Camera):
	detectFaces = BooleanProperty(False)
	angle = NumericProperty(0)
	def __init__(self, **kwargs):
		super(CustomCamera, self).__init__(**kwargs)

		self.isAndroid = kivy.platform == "android"
		if self.isAndroid:
			self.angle = -90

	def change_index(self, *args):
		new_index = 1 if self.index == 0 else 0
		self._camera._set_index(new_index)
		self.index = new_index
		self.angle = -90 if self.index == 0 else 90


	def on_tex(self, *l):
		image = np.frombuffer(self.texture.pixels, dtype='uint8')
		image = image.reshape(self.texture.height, self.texture.width, -1)
		image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)

		if self.detectFaces:
			image, faceRect = face_detection(image, (0, 255, 0, 255), self.angle)

		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGBA)
		numpy_data = image.tostring()
		self.texture.blit_buffer(numpy_data, bufferfmt="ubyte", colorfmt='rgba')
		super(CustomCamera, self).on_tex(self.texture)

	def get_cameras_count(self):
		cameras = 1
		if self.isAndroid:
			cameras = self._camera.get_camera_count()
		return cameras

class QrReader(Camera):
	def __init__(self, **kw):
		super(QrReader, self).__init__(**kw)
		self.qr_reader = cv2.QRCodeDetector()
		self.register_event_type('on_data')
		self.qr_result = None

	def getValue(self):
		return {
			"qr_result":self.qr_result
		}

	def on_data(self, d):
		print('data=',d)

	def on_tex(self, *l):
		image = np.frombuffer(self.texture.pixels, dtype='uint8')
		image = image.reshape(self.texture.height, self.texture.width, -1)
		image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
		self.qr_result, bbox,_ = self.qr_reader.detectAndDecode(image)
		if self.qr_result:
			print('qr read done')
			self.dispatch('on_data',self.qr_result)
		super(QrReader, self).on_tex(self.texture)

Builder.load_string(btxt)
