import numpy as np
import cv2
from kivy.app import App
from kivy.properties import BooleanProperty
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.uix.image import Image
from kivy.clock import Clock

class QRCodeReader(Image):
	opened = BooleanProperty(False)
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.register_event_type('on_data')
		self.task = None
		if self.opened:
			self.open()

	def open(self):
		self.opened = True
		self.cam = cv2.VideoCapture(0)
		self.detector = cv2.QRCodeDetector()
		self.task = Clock.schedule_interval(self.read,1.0/30.0)
		Window.add_widget(self)

	def on_data(self,d):
		print('QRCodeReader().on_data(),data=',d)
		self.dismiss()

	def on_touch_down(self,touch):
		if not self.colide_point(*touch.pos):
			self.dismiss()
		super().on_touch_down(touch)

	def dismiss(self, *args, **kw):
		if not self.opened:
			return
		self.opened = False
		self.task.cancel()
		self.task = None
		self.cam.release()
		cv2.destroyAllWindows()
		Window.remove_widget(self)

	def showImage(self,img):
		image = np.rot90(np.swapaxes(img,0,1))
		tex = Texture.create(size=(image.shape[1], image.shape[0]), 
						colorfmt='rgb')
		tex.blit_buffer(image.tostring(),colorfmt='rgb', bufferfmt='ubyte')
		self.texture = tex

	def read(self,p):
		_, img = self.cam.read()
		self.showImage(img)
		data,bbox,_ = self.detector.detectAndDecode(img)
		if data:
			d = {
				'data':data
			}
			self.dispatch('on_data',d)

if __name__ == '__main__':
	class MyApp(App):
		def build(self):
			r = QRCodeReader()
			return r
	myapp = MyApp()
	myapp.run()

