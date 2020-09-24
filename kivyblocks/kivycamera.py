from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.factory import Factory
import cv2

def set_res(cap, x,y):
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(x))
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(y))
    return cap.get(cv2.CAP_PROP_FRAME_WIDTH),cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

class KivyCamera(Image):
	def __init__(self, camera_id=0, fps=25.0, face_detect=False, **kwargs):
		print('KivyCamera inited')
		self.update_task = None
		self.capture = None
		super(KivyCamera, self).__init__(**kwargs)
		self.capture = cv2.VideoCapture(camera_id)
		self.face_detect = face_detect
		self.camera_id = camera_id
		self.faceCascade = None
		if face_detect:
			# self.faceCascade = cv2.CascadeClassifier("Resources/haarcascades/haarcascade_frontalface_default.xml")  # added
			self.faceCascade = cv2.CascadeClassifier('data/haarcascade/haarcascade_frontalface_default.xml')
		self.update_task = Clock.schedule_interval(self.update, 1.0 / fps)

	def on_size(self,o,size):
		if self.capture:
			self.capture.release()
		self.capture = cv2.VideoCapture(self.camera_id)
		size = set_res(self.capture,self.width,self.height)
		print(size)

	def add_face_detech(self,frame):
		frameGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		faces = self.faceCascade.detectMultiScale(frameGray, 
							scaleFactor = 1.2, minNeighbors = 5)
		# THIS LINE RAISE ERROR 
		# faces = self.faceCascade.detectMultiScale(frameGray, 1.1, 4)
 		# cv2.error: OpenCV(4.2.0) C:\projects\opencv-python\opencv\modules\objdetect\src\cascadedetect.cpp:1689: error: (-215:Assertion failed) !empty() in function 'cv::CascadeClassifier::detectMultiScale'
		for (x, y, w, h) in faces:  # added
			cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
		return frame


	def update(self, dt):
		ret, frame = self.capture.read()
		if ret:
			if self.width / self.height > frame.shape[1] / frame.shape[0]:
				fx = fy = self.height / frame.shape[0]
			else:
				fx = fy = self.width / frame.shape[1] 
			
			frame = cv2.resize(frame, None, 
					fx=fx, fy=fy, 
					interpolation=cv2.INTER_LINEAR)
			if self.faceCascade:
				try:
					frame = self.add_face_detech(frame)
				except:
					pass
			# convert it to texture
			buf1 = cv2.flip(frame, 0)
			buf = buf1.tostring()
			image_texture = Texture.create(
				size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
			image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
			# display image from the texture
			self.texture = image_texture
		else:
			self.update_task.cancel()
			print('failed to read from capture')

	def __del__(self):
		if self.update_task:
			self.update_task.cancel()
			self.update_task = None
		self.cupture.close()

Factory.register('KivyCamera',KivyCamera)
