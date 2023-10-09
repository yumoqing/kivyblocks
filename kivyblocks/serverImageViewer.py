from appPublic.jsonConfig import getConfig
from kivy.uix.button import ButtonBehavior
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from .baseWidget import *
from .objectViewer import ObjectViewer

class ServerImageViewer(ObjectViewer):
	def showObject(self,rec,**kw):
		blocks = App.get_running_app().blocks
		config = getConfig()
		url = '%s/%s/%s' % ( config.uihome,'thumb',rec['id'])
		desc = self.viewer.copy()
		desc['options'].update({
			"size_hint_x":None,
			"width":self.box_width,
			"keep_ratio":True,
			"source":url
		})
		w = blocks.widgetBuild(desc)
		if w is None:
			print('Error desc=',desc)
			return
		bl = BoxLayout(size_hint=(None,None),size=(self.box_width,self.box_width))
		bl.add_widget(w)
		self.add_widget(bl,**kw)
		print('showObject():add widget',desc,w.size)
		return bl

