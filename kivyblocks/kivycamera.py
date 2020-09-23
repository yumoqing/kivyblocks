from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.factory import Factory
import cv2

class KivyCamera(Image):
	def __init__(self, fps=25.0, face_detect=Falsem **kwargs):
		super(KivyCamera, self).__init__(**kwargs)
		self.capture = cv2.VideoCapture(0)
		self.face_detect = face_detect
		self.faceCascade = None
		if face_detect:
			self.faceCascade = cv2.CascadeClassifier("Resources/haarcascades/haarcascade_frontalface_default.xml")  # added
		Clock.schedule_interval(self.update, 1.0 / fps)

	def add_face_detech(self,frame):
		frameGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		faces = self.faceCascade.detectMultiScale(frameGray, 1.1, 4)
		for (x, y, w, h) in faces:  # added
			cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)


	def update(self, dt):
		ret, frame = self.capture.read()
		if ret:
			if self.faceCascade:
				frame = self.add_face_detech(frame)
			# convert it to texture
			buf1 = cv2.flip(frame, 0)
			buf = buf1.tostring()
			image_texture = Texture.create(
				size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
			image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
			# display image from the texture
			self.texture = image_texture

Factory.register('Camera',KivyCamera)
