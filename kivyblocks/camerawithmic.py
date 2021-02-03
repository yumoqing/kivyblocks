
import kivy
import numpy as np
from .micphone import Micphone
from kivy.uix.camera import Camera
from kivy.properties import NumericProperty
from kivy.event import EventDispatcher

if kivy.platform in [ 'win', 'linux', 'macosx' ]:
	from PIL import ImageGrab
	class ScreenWithMic(Micphone, EventDispatcher):
		def __init__(self, **kw):
			super(ScreenWithMic, self).__init__(**kw)

		def get_image_data(self):
			image = ImageGrab.grab()
			imgdata = image.tostring()
			return imgdata
			
		def get_fps_data(self, *args):
			ad = super(CameraWithMic, self).get_fps_data()
			vd = self.get_image_data()
			d = {
				'v':vd,
				'a':ad
			}
			return d
			
class CameraWithMic(Micphone, Camera):
	angle = NumericProperty(0)
	def __init__(self, **kw):
		super(CameraWithMic, self).__init__(**kw)
		self.isAndroid = kivy.platform == 'android'
		if self.isAndroid:
			self.angle = -90

	def get_image_data(self):
		image = np.frombuffer(self.texture.pixels, dtype='uint8')
		image = image.reshape(self.texture.height, self.texture.width, -1)
		imgdata = image.tostring()
		return imgdata
		
	def get_fps_data(self, *args):
		ad = super(CameraWithMic, self).get_fps_data()
		vd = self.get_image_data()
		d = {
			'v':vd,
			'a':ad
		}
		return d
