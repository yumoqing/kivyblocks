import sys
import re
from kivy.app import App
from kivy.logger import Logger
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.switch import Switch
from kivy.metrics import sp,dp
from kivy.app import App
from kivy.properties import BooleanProperty, ListProperty, \
			NumericProperty

from ..threadcall import HttpClient
from ..utils import CSize, set_widget_height, set_widget_width
from ..widget_css import WidgetCSS, get_css

class BoolInput(Switch):
	def __init__(self,csscls='input', **kw):
		super().__init__()
		self.register_event_type('on_changed')
		self.bind(active=on_active)

	def on_changed(self,v=None):
		pass

	def on_active(self,t,v):
		self.dispatch('on_changed',v)
		
	def getValue(self):
		return self.active

	def setValue(self,v):
		self.active = v
	
class StrInput(WidgetCSS, TextInput):
	length = NumericProperty(None)
	def __init__(self, **kv):
		if kv is None:
			kv = {}
		a = {
			"allow_copy":True,
			"password":False,
			"multiline":False,
			"halign":"left",
			"hint_text":"test",
			"text_language":"zh_CN",
			"font_size":CSize(1),
			"write_tab":False
		}
		a.update(kv)
		super(StrInput, self).__init__(**a)
		self.text = self.old_value = ''
		self.register_event_type('on_changed')
		self.bind(on_text_validate=self.checkChange)

	def on_bgcolor(self, *args):
		self.background_color = self.bgcolor

	def on_fgcolor(self, *args):
		self.foreground_color = self.fgcolor

	def on_changed(self,v=None):
		pass
		
	def checkChange(self,o,v=None):
		v = self.getValue()
		if v != self.old_value:
			self.old_value = v
			self.dispatch('on_changed',v)

	def insert_text(self, substring, from_undo=False):
		if self.length:
			if len(self.text) + len(substring) > self.length:
				return None
		ret = super().insert_text(substring, from_undo=from_undo)
		# ret is None
		return ret

	def getValue(self):
		return self.text

	def setValue(self,v):
		if v is None:
			v = ''
		self.text = str(v)
		self.old_value = self.text
		
class Password(StrInput):
	def __init__(self, **kw):
		super().__init__(**kw)
		self.password = True

class IntegerInput(StrInput):
	def __init__(self,**kw):
		a = {}
		a.update(kw)
		a['halign'] = 'right'
		super().__init__(**a)
		self.input_filter = 'int'

	def on_focus(self,t,v):
		self.cursor = (0,len(self.text))

	def getValue(self):
		try:
			return int(self.text)
		except:
			pass
		return None

class FloatInput(IntegerInput):
	dec = NumericProperty(2)
	def __init__(self,**kw):
		super(FloatInput, self).__init__(**kw)
		self.input_filter = 'float'

	def getValue(self):
		try:
			return float(self.text)
		except:
			pass
		return None

class MyDropDown(DropDown):
	def __init__(self,csscls='input', **kw):
		super(MyDropDown,self).__init__()
		self.options = kw
		self.textField = kw.get('textField','text')
		self.valueField = kw.get('valueField','value')
		self.loadSelectItems()

	def loadSelectItems(self):
		if self.options.get('url') is not None:
			self.url = self.options.get('url')
			self.setDataByUrl(self.url)
		else:
			self.si_data = self.options.get('data')
			if self.si_data:
				self.setData(self.si_data)
		self.bind(on_select=lambda instance, x: self.selectfunc(x))

	def selectfunc(self,v):
		f = self.options.get('on_select')
		if f is not None:
			return f(v)
			
	def getTextByValue(self,v):
		for d in self.si_data:
			if d.get(self.valueField) == v:
				r = d.get(self.textField)
				return r if r else v
		return str(v)
		
	def getValueByText(self,v):
		for d in self.si_data:
			if d.get(self.textField) == v:
				r = d.get(self.valueField)
				return r
		return None
		
	def setData(self,data):
		self.si_data = data
		self.clear_widgets()
		h = self.options.get('height',2.5)
		a = {}
		a['size_hint_y'] = None
		a['height'] = CSize(2)
		a['font_size'] = CSize(1)
		for d in data:
			v = d.get(self.valueField, None)
			t = d.get(self.textField, None)
			dd = (v,t or v)
			b = Button(text=dd[1],**a)
			setattr(b,'kw_data',dd)
			b.bind(on_release=lambda btn: self.select(btn.kw_data))
			self.add_widget(b)
			
	def setDataByUrl(self,url,kw={}):
		hc = HttpClient()
		params = self.options.get('params', {}).copy()
		params.update(kw)
		d = hc.get(url,params=params)
		self.setData(d)
			
	def showme(self,w):
		self.target = w
		self.open(w)
		
class SelectInput(BoxLayout):
	def __init__(self,csscls='input', **kw):
		a={}
		w = kw.get('width',10)
		h = kw.get('height',2.5)
		if w <= 1:
			a['size_hint_x'] = w
		else:
			a['size_hint_x'] = None
			a['width'] = CSize(w)
		if h <= 1:
			a['size_hint_y'] = h
		else:
			a['size_hint_y'] = None
			a['height'] = CSize(h)

		super(SelectInput,self).__init__(orientation='horizontal',\
				**a)
		self.si_value = ''
		self.tinp = StrInput()
		# self.tinp.readonly = True
		newkw = {}
		newkw.update(kw)
		# newkw.update({'on_select':self.setData})
		self.dropdown = MyDropDown(**newkw)
		if kw.get('value'):
			self.si_data = kw.get('value')
			self.text = self.dropdown.getTextByValue(self.si_data)
		else:
			self.si_data = ''
			self.text = ''
		self.dropdown.bind(on_select=self.dropdown_select)
		self.tinp.text = self.text
		self.add_widget(self.tinp)
		self.old_value = self.si_data
		self.tinp.bind(focus=self.showDropdown)
		self.register_event_type('on_changed')
		
	def dropdown_select(self, o, d):
		self.setData(d)

	def set_selectable_data(self, data):
		self.dropdown.setData(data)

	def on_changed(self,v=None):
		pass

	def showDropdown(self,instance,yn):
		# if self.collide_point(*touch.pos):
		if yn:
			self.tinp.focus = False
			self.dropdown.showme(self)
			self.old_value = self.getValue()
		
	def setData(self,d):
		self.si_value = d[0]
		self.tinp.text = d[1]
		v = self.getValue()
		if v != self.old_value:
			self.dispatch('on_changed',v)

	def setValue(self,v):
		self.si_value = v
		self.tinp.text = self.dropdown.getTextByValue(v)
		
	def getValue(self):
		return self.si_value
		
if __name__ == '__main__':
	from kivy.app import App
	from kivy.uix.boxlayout import BoxLayout
	class MyApp(App):
		def build(self):
			root = BoxLayout(orientation='vertical')
			x = SelectInput(width=CSize(15),value='1',data=[{'value':'1','text':'ban'},{'value':'0','text':'nu'}],textField='text',valueField='value')
			root.add_widget(x)
			b = Button(text='drop', size_hint=(None, None))
			root.add_widget(b)
			dd = MyDropDown(width=CSize(15),value='1',data=[{'value':'1','text':'nan'},{'value':'0','text':'nu'}],textField='text',valueField='value',on_select=x.setData)
			b.bind(on_release=dd.showme)
			return root
	MyApp().run()
			
		
