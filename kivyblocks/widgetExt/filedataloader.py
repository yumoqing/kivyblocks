import codecs
from .dataloader import DataLoader

class FileDataLoader(DataLoader):
	def loadData(self,filename):
		try:
			with codecs.open(filename,'r','utf8') as f:
				self.dataLoaded(text)
				return f.read()
		except Exception as e:
			self.loadError(e)


