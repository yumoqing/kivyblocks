import locale
from kivy.app import App
from kivy.properties import StringProperty
from appPublic.Singleton import SingletonDecorator
from appPublic.jsonConfig import getConfig
from .baseWidget import Text

@SingletonDecorator
class I18n:
	def __init__(self,url):
		self.kvlang={}
		self.loadUrl = url
		self.lang = locale.getdefaultlocale()[0]
		self.loadI18n(self.lang)
		self.i18nWidgets = []

	def addI18nWidget(self,w):
		self.i18nWidgets.append(w)
	
	def loadI18n(self,lang):
		if not self.loadUrl:
			self.kvlang[lang] = {}
			return
		app = App.get_running_app()
		d = app.hc.get('%s?lang=%s' % (self.loadUrl,lang))
		self.kvlang[lang] = d
		
	def __call__(self,msg,lang=None):
		if lang is None:
			lang = self.lang
		d = self.kvlang.get(lang,{})
		return d.get(msg,msg)
	
	def changeLang(self,lang):
		d = self.kvlang.get(lang)
		if not d:
			self.loadI18n(lang)
		self.lang = lang
		for w in self.i18nWidgets:
			w.changeLang(lang)
	
def getI18n(url=None):
	i18n=I18n(url)
	return i18n

class I18nText(Text):
	lang=StringProperty('')
	otext=StringProperty('')

	def __init__(self,**kw):
		self.options = kw.copy()
		otext = kw.get('otext',kw.get('text'))
		if kw.get('otext'):
			del kw['otext']
		super().__init__(**kw)
		self.i18n = getI18n()
		self.i18n.addI18nWidget(self)
		self.otext = otext

	def on_otext(self,o,v=None):
		self.text = self.i18n(self.otext)
	
	def changeLang(self,lang):
		self.lang = lang

	def on_lang(self,o,lang):
		self.text = self.i18n(self.otext)

