import locale
from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.label import Label
from appPublic.Singleton import SingletonDecorator
from appPublic.jsonConfig import getConfig
from .threadcall import HttpClient

@SingletonDecorator
class I18n:
	def __init__(self):
		self.kvlang={}
		self.lang = locale.getdefaultlocale()[0]
		self.loadI18n(self.lang)
		self.i18nWidgets = []

	def addI18nWidget(self,w):
		self.i18nWidgets.append(w)
	
	def loadI18n(self,lang):
		app = App.get_running_app()
		config = getConfig()
		url = '%s%s/%s' % (config.uihome, config.i18n_url, lang)
		hc = HttpClient()
		d = hc.get(url)
		print('i18n() %s get data=' % url, d, type(d))
		self.kvlang[lang] = d
		
	def __call__(self,msg,lang=None):
		if lang is None:
			lang = self.lang
		d = self.kvlang.get(lang,{})
		if d is None:
			return msg
		return d.get(msg,msg)
	
	def changeLang(self,lang):
		d = self.kvlang.get(lang)
		if not d:
			self.loadI18n(lang)
		self.lang = lang
		for w in self.i18nWidgets:
			w.changeLang(lang)
	
