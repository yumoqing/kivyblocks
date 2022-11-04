import os
import codecs
from weakref import ref
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
		if self.lang is None:
			self.lang = 'en_US'
		self.languages = None
		self.loadI18n(self.lang)
		self.i18nWidgets = []

	def addI18nWidget(self,w):
		self.i18nWidgets.append(ref(w))
	
	def loadI18nFromI18nFolder(self, lang):
		config = getConfig()
		fpath =  os.path.join(config.i18n_folder,lang,'msg.txt')
		print('fpath=', fpath, type(fpath))
		with codecs.open(fpath,'r','utf-8') as f:
			line = f.readline()
			d = {}
			while line:
				if line.startswith('#'):
					line = readline()
					continue
				k,v = line.split(':',1)
				d.update({k:v})
				line = f.readline()
			return d

	def get_languages(self):
		if self.languages:
			return self.languages
		self.languages = self.getLanguages()
		return self.languages

	def getLanguages(self):
		config = getConfig()
		if config.i18n_folder:
			langs = []
			for f in os.listdir(config.i18n_folder):
				p = os.path.join(config.i18n_folder, f)
				if os.path.isdir(p):
					langs.append(os.path.basename(f))
			return langs

		if config.i18n_url:
			url = '%s%s' % (config.uihome, config.i18n_url)
			hc = HttpClient()
			d = hc.get(url)
			if isinstance(d, list):
				return d
		return []
			
	def loadI18n(self,lang):
		app = App.get_running_app()
		config = getConfig()
		self.kvlang[lang] = {}
		if config.i18n_folder:
			self.kvlang[lang] = self.loadI18nFromI18nFolder(lang)
			return

		if config.i18n_url:
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
		ws = [ w for w in self.i18nWidgets if w() is not None ]
		for w in ws:
			w().changeLang(lang)
		self.i18nWidgets = ws
	
