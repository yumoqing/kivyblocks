import os
from kivy.properties import StringProperty, ListProperty
from kivyblocks.utils import blockImage, CSize
import requests
from plyer import filechooser
from .i18n import I18n
from .clickable import ClickableIconText
from .baseWidget import Running
from .message import Error

class UploadFile(ClickableIconText):
	upload_url = StringProperty(None)
	name = StringProperty('upfile')
	# suffixes = ListProperty([])
	def __init__(self, **kw):
		super().__init__(**kw)
		self.otext = 'please select file'
		self.img_kw = {
			"size_hint":[None, None],
			"width":CSize(1),
			"height":CSize(1)
		}
		self.source = blockImage('upload.png')
		self.file_url = None
		self.running = None

	def getValue(self):
		return {
			self.name:self.file_url
		}

	def on_press(self, *args):
		i18n = I18n()
		filechooser.open_file(title=i18n('open file'),
								on_selection=self.file_selected)

	def file_selected(self, files):
		running = Running(self)
		def readfile(f):	
			with open(f, 'rb') as o:
				d = o.read(102400)
				if not d:
					return
				yield d
		fpath = files[0]
		fn = os.path.basename(fpath)
		print('fn=', fn)
		headers={
			'Content-Type': 'application/octet-stream',
			'Content-Disposition':'attachments;filename={}'.format(fn)
		}
		r = requests.post(self.upload_url, 
					data=readfile(files[0]),
					headers=headers
		)
		running.dismiss()

