''' Kivy Widget that accepts data and displays qrcode
'''

from threading import Thread
from functools import partial

from kivy.factory import Factory
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty, StringProperty, ListProperty,\
	BooleanProperty, NumericProperty
from kivy.lang import Builder
from kivy.clock import Clock

from .baseWidget import VBox
import qrcode

class QRCodeWidget(VBox):
	data = StringProperty(None, allow_none=True)
	''' Data using which the qrcode is generated.

	:data:`data` is a :class:`~kivy.properties.StringProperty`, defaulting to
	`None`.
	'''

	loading_image = StringProperty('data/images/image-loading.gif')
	'''Intermediate image to be displayed while the widget ios being loaded.
	
	:data:`loading_image` is a :class:`~kivy.properties.StringProperty`,
	defaulting to `'data/images/image-loading.gif'`.
	'''

	version = NumericProperty(40)
	box_size = NumericProperty(20)
	err_level = StringProperty('L')
	border = NumericProperty(1)
	error_correct_values = {
		'L':qrcode.constants.ERROR_CORRECT_L,
		'M':qrcode.constants.ERROR_CORRECT_M,
		'Q':qrcode.constants.ERROR_CORRECT_Q,
		'H':qrcode.constants.ERROR_CORRECT_H
	}
	def __init__(self, **kwargs):
		self.qrimage = Image(allow_stretch=True, keep_ratio=True)
		self.addr = None
		super(QRCodeWidget, self).__init__(**kwargs)
		self.background_color = [1,1,1,1]
		self.qr = None
		self._qrtexture = None
		self.add_widget(self.qrimage)
	
	def on_size(self,o,s):
		self.qrimage.width = self.width
		self.qrimage.height = self.height
		self.on_data(None,self.data)

	def on_data(self, instance, value):
		if not (self.canvas or value):
			return
		img = self.qrimage
		img.anim_delay = .25
		img.source = self.loading_image
		self.generate_qr(value)

	def generate_qr(self, value):
		self.set_addr(value)
		self.update_qr()

	def set_addr(self, addr):
		if self.addr == addr:
			return
		MinSize = 500 #210 if len(addr) < 128 else 500
		self.setMinimumSize((MinSize, MinSize))
		self.addr = addr
		self.qr = None

	def update_qr(self):
		if not self.addr and self.qr:
			return
		QRCode = qrcode.QRCode
		L = qrcode.constants.ERROR_CORRECT_L
		addr = self.addr
		print('self.box_size=', self.box_size)
		errv = self.error_correct_values.get(self.err_level)
		if not errv:
			errv=self.error_corrent_values.get('L')

		try:
			self.qr = qr = QRCode(
				version=self.version,
				error_correction=errv,
				box_size=self.box_size,
				border=self.border,
				)
			qr.add_data(addr)
			qr.make(fit=True)
			self.qr = qr
			self.update_texture()
		except Exception as e:
			print('eeeee',e)
			self.qr=None

	def setMinimumSize(self, size):
		# currently unused, do we need this?
		self._texture_size = size

	def _create_texture(self, k):
		self._qrtexture = texture = Texture.create(size=(k,k), colorfmt='rgb')
		# don't interpolate texture
		texture.min_filter = 'nearest'
		texture.mag_filter = 'nearest'

	def update_texture(self):
		if not self.addr:
			return

		matrix = self.qr.get_matrix()
		k = len(matrix)
		self._create_texture(k)
		
		
		cr, cg, cb = 255, 255, 255
		###used bytearray for python 3.5 eliminates need for btext
		buff = bytearray()
		for r in range(k):
			for c in range(k):
				buff.extend([0, 0, 0] if matrix[r][c] else [cr, cg, cb])

		# then blit the buffer
		# join not neccesarry when using a byte array 
		# buff =''.join(map(chr, buff))
		# update texture in UI thread.
		self._upd_texture(buff)

	def _upd_texture(self, buff):
		texture = self._qrtexture
		if not texture:
			# if texture hasn't yet been created delay the texture updation
			Clock.schedule_once(lambda dt: self._upd_texture(buff))
			return
		
		texture.blit_buffer(buff, colorfmt='rgb', bufferfmt='ubyte')
		texture.flip_vertical()
		img = self.qrimage
		img.anim_delay = -1
		img.texture = texture
		img.canvas.ask_update()

if __name__ == '__main__':
	from kivy.app import runTouchApp
	import sys
	data = str(sys.argv[1:])
	data = """{
	"host":"122.22.22.33",
	"port":12345
	}"""
	runTouchApp(Factory.QRCodeWidget(data=data))
