import sys
import re
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.switch import Switch
from kivy.metrics import sp,dp
from kivy.app import App
from kivy.properties import BooleanProperty

from ..threadcall import HttpClient
from ..utils import CSize

class BoolInput(Switch):
	change = BooleanProperty(False)
	def __init__(self,**kw):
		a = DictObject()
		if kw.get('defaultvalue',None) is None:
			a.active = False
		else:
			a.active = kw.get('defaultvalue')
		if kw.get('value',None) is not None:
			a.active = kw.get('value')

		super().__init__(**a)
		self.bind(active=on_active)
		self.bind(change=self.on_change)

	def on_change(self,t,v):
		pass

	def on_active(self,t,v):
		change = True
		
	def getValue(self):
		return self.active

	def setValue(self,v):
		self.active = v
	
class StrInput(TextInput):
	change = BooleanProperty(False)
	def __init__(self,**kv):
		if kv is None:
			kv = {}
		a = {
			# "allow_copy":True,
			"font_size":CSize(1),
			"multiline":False,
			"halign":"left",
			"hint_text":"",
			"size_hint_y":None,
			"height":CSize(2)
		}
		if kv.get('tip'):
			a['hint_text'] = kv['tip']
		a.update(kv)
		a['multiline'] = False
		super(StrInput,self).__init__(**a)
		self.bind(focus=self.on_focus)
		self.bind(text=self.on_text)
		self.bind(change=self.on_change)

	def on_change(self,t,v):
		if v:
			pass
		
	def on_text(self,t,v):
		self.change = True

	def on_focus(self,t,v):
		self.change = False

	def getValue(self):
		return self.text

	def setValue(self,v):
		self.text = v

class Password(StrInput):
	def __init__(self, **kw):
		kw['password'] = True
		super().__init__(**kw)

class IntegerInput(StrInput):
	def __init__(self,**kw):
		a = {}
		a.update(kw)
		a['halign'] = 'right'
		super().__init__(**a)

	pat = re.compile('[^0-9]')
	def insert_text(self, substring, from_undo=False):
		pat = self.pat
		s = re.sub(pat, '', substring)
		return StrInput.insert_text(self,s, from_undo=from_undo)
	
class FloatInput(IntegerInput):
	pat = re.compile('[^0-9]')
	def filter(self,substring):
		pat = self.pat
		if '.' in self.text:
			s = re.sub(pat, '', substring)
		else:
			s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
		return s

	def insert_text(self, substring, from_undo=False):
		s = self.filter(substring)
		return StrInput.insert_text(self,s, from_undo=from_undo)

class AmountInput(FloatInput):
	def filter(self,substring):
		s = super(AmountInput,self).filter(substring)
		a = s.split('.')
		b = a[0]
		if len(b)>3:
			k = []
			while len(b)>3:
				x = b[-3:]
				k.insert(0,x)
				b = b[:-3]
			a[0] = ','.join(k)
		s = '.'.join(a)
		return '.'.join(a)

	def insert_text(self, substring, from_undo=False):
		s = self.filter(substring)
		return StrInput.insert_text(self,s, from_undo=from_undo)
			
class MyDropDown(DropDown):
	def __init__(self,**kw):
		super(MyDropDown,self).__init__()
		self.options = kw
		self.textField = kw.get('textField',None)
		self.valueField = kw.get('valueField',None)
		if kw.get('url') is not None:
			self.url = kw.get('url')
			self.setDataByUrl(self.url)
		else:
			self.si_data = kw.get('data')
			self.setData(self.si_data)
		self.bind(on_select=lambda instance, x: self.selectfunc(x))

	def selectfunc(self,v):
		f = self.options.get('on_select')
		if f is not None:
			return f(v)
			
	def getTextByValue(self,v):
		for d in self.si_data:
			if d[self.valueField] == v:
				return d[self.textField]
		return str(v)
		
	def getValueByText(self,v):
		for d in self.si_data:
			if d[self.textField]  == v:
				return d[self.valueField]
		return ''
		
	def setData(self,data):
		self.si_data = data
		self.clear_widgets()
		for d in data:
			dd = (d[self.valueField],d[self.textField])
			b = Button(text=d[self.textField],font_size=CSize(1),
				size_hint_y=None, 
				height=CSize(1.8))
			setattr(b,'kw_data',dd)
			b.bind(on_release=lambda btn: self.select(btn.kw_data))
			self.add_widget(b)
			#print(dd)
			
	def setDataByUrl(self,url,params={}):
		def x(obj,resp):
			if resp.status_code == 200:
				d = resp.json()
				self.setData(d)

		app = App.get_running_app()
		app.hc.get(url,params=params,callback=x)
		
			
	def showme(self,w):
		#print('show it ',w)
		self.target = w
		self.open(w)
		
class SelectInput(BoxLayout):
	def __init__(self,**kw):
		super(SelectInput,self).__init__(orientation='horizontal',						size_hint_y=None,height=CSize(1.8))
		self.tinp = StrInput()
		self.tinp.readonly = True
		newkw = {}
		newkw.update(kw)
		newkw.update({'on_select':self.setData})
		self.dropdown = MyDropDown(**newkw)
		if kw.get('value'):
			self.si_data = kw.get('value')
			self.text = self.dropdown.getTextByValue(self.si_data)
		else:
			self.si_data = ''
			self.text = ''
		self.add_widget(self.tinp)
		self.tinp.bind(focus=self.showDropdown)
		
	def showDropdown(self,instance,yn):
		# if self.collide_point(*touch.pos):
		if yn:
			self.tinp.focus = False
			self.dropdown.showme(self)
		
	def setData(self,d):
		self.tinp.si_data = d[0]
		self.tinp.text = d[1]

	def setValue(self,v):
		self.tinp.si_value = v
		self.tinp.text = self.dropdown.getTextByValue(v)
		
	def getValue(self):
		return self.tinp.si_value
		
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
			
		
