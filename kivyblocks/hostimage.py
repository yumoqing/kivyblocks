import tempfile
from kivyblocks.baseWidget import HTTPDataHandler
from kivyblocks.utils import blocksImage, absurl

from kivy.uix.image import Image

class HostImage(Image):
	def __init__(self, target,**kwargs):
		self.options = kwargs
		self.target = target
		kwargs['source'] = blocksImage('running.gif')
		url = kwargs.get('url')
		del kwargs['url']
		super().__init__(**kwargs)
		self.downloadImage(url)

	def downloadImage(url):
		realurl = absurl(url,self.target.parenturl)
		loader = HTTPDataHandler(url,stream=True)
		loader.bind(on_success=self.createTmpfile)
		loader.bind(on_failed=self.showBadImage)
		loader.handle()
	
	def showBadImage(self,o,e):
		self.source = blocksImage('break.png')
		
	def createTmpfile(self,o,resp):
		fn = tempfile.NamedTemporaryFile(delete=True)
		with open(fn, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    # f.flush()
		self.source = fn

