from kivy.uix.image import AsyncImage
from kivy.factory import Factory
from kivy.properties import StringProperty
from urllib.request import urlopen
from kivyblocks.utils import blockImage

class DefaultImage(AsyncImage):
	default_source = StringProperty(None)
	def __init__(self, default_source=None, **kw):
		self.default_source = default_source
		super().__init__(**kw)
		if self.default_source is None:
			self.default_source = blockImage('broken.png')

	def can_access(self, src):
		if os.path.isfile(src):
			return True
		if self.is_uri(src):
			with urlopen(src, timeout=0.5):
				return True
		return None

	def on_source(self, o, s):
		if not self.can_access(s):
			self.source = self.default_source

Factory.register('DefaultImage', DefaultImage)

if __name__ == '__main__':
	import os
	import sys
	from kivy.app import App
	class TestApp(App):
		def build(self):
			return DefaultImage(source=sys.argv[1], default_source='/Volumes/home/ymq/pydev/github/kivyblocks/kivyblocks/imgs/doing.gif')
	
	app = TestApp()
	app.run()
