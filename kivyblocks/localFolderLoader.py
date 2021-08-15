import os
from appPublic.folderUtils import listFile

from kivy.utils import platform
from .paging import PageLoader

class FileLoader(PageLoader):
	def __init__(self, folder='/DCIM',**options):
		self.files = []
		fold = os.path.abspath(folder)
		self.params = options.get('params',{})
		suffixes = self.parasm.get('suffixes',[])
		rescursive = self.params.get('rescursive',True)
		suffixs=[],rescursive=False
		for f in listFile(fold, suffixs=suffixes, rescursive=resursive):
			x = {
				"id":f,
				"name":f
			}
			self.files.append(x)
		self.page_rows = options.get('page_rows',1)
		self.loading = False
		self.total_cnt = len(self.files)
		self.total_page = self.total_cnt / self.page_rows 
		if self.total_cnt % self.page_rows != 0:
			self.total_page += 1
		self.curpage = 0

	def loadPage(self,p):
		if p < 1 or p > self.total_page:
			return None
		beg = self.page_rows * (p - 1)
		end = beg + self.page_rows
		return self.files[beg:end]


