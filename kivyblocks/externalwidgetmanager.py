# -*- utf-8 -*-
"""
模板文件以wrdesc结尾
界面描述文件以uidesc结尾
"""
import os
import sys
import codecs
from kivy.app import App

from appPublic.folderUtils import ProgramPath,listFile
from appPublic.jsonConfig import getConfig

import json

class ExternalWidgetManager:
	def __init__(self):
		#self.register_root = os.path.join(ProgramPath(),'widgets')
		#self.ui_root = os.path.join(ProgramPath(),'ui')
		self.ui_root = './ui'
		self.register_root = './widgets'
		
	def loadJson(self,filepath):
		with codecs.open(filepath,'r','utf-8') as f:
			return json.load(f)
	
	def travalRegisterDesc(self,func):
		return
		for f in listFile(self.register_root,suffixs=['.wrdesc'],rescursive=True):
			desc = self.loadJson(f)
			return func(desc)
			
	def loadWidgetDesc(self,desc):
		def text2Json(d):
			j = json.loads(d)
			return j

		# print(desc)
		if desc.get('filename'):
			path = desc.get('filename')
			if path.endswith('.uidesc'):
				f = FileDataLoader()
				f.bind(on_dataloaded=text2Json)
				if path.startswith('/'):
					path = path[1:]
				fn = os.path.join(self.ui_root,path)
				return text2Json(f.loadData(fn))
			raise Exception('file error',path)

		if desc.get('url'):
			url = desc.get('url')
			headers = desc.get('headers',{})
			params = desc.get('params',{})
			app = App.get_running_app()
			resp = app.hc.sync_get(url,params=params,headers=headers)
			if resp.status_code == 200:
				d = resp.json()
				if d.get('status') == 'OK':
					return d['data']
				raise Exception('ui desc loaded failed %s' % url)

		raise Exception('ui desc loaded failed' , desc)
	
