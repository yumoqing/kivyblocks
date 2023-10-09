
from kivy.uix.label import Label
from kivy.properties import NumericProperty, ColorProperty
from kivy.factory import Factory

from .baseWidget import FloatInput

from .uitype.factory import UiFactory, get_value

class PriceView(Label):
	dec = NumericProperty(4)
	compare_price = NumericProperty(None)
	price = NumericProperty(None)
	nor_color = ColorProperty([0.9,0.9,0.9,1]) # white
	inc_color = ColorProperty([0.9,0,0,1]) 	# red
	dec_color = ColorProperty([0,0.9,0,1])	# green
	def __init__(self, **kw):
		super(PriceView, self).__init__(text='', **kw)

	def on_compare_price(self, *args):
		self.on_price()
	def on_price(self, *args):
		if self.price is None:
			return
		if not isinstance(self.price, float) and \
					not isinstance(self.price, int):
			return

		f = '%%.0%df' % self.dec
		self.text = f % self.price
		if self.compare_price is None:
			self.color = self.nor_color
		elif self.price > self.compare_price:
			self.color = self.inc_color
		elif self.price < self.compare_price:
			self.color = self.dec_color
		else:
			self.color = nor_color

	def getValue(self):
		return self.price

	def setValue(self, v):
		self.price = v

	@classmethod
	def builder(desc, rec=None):
		v = get_value(desc, rec=rec)
		return PriceView(price=v,
						font_size=CSize(1),
						halign='right',
						valign='middle'
		)

class PriceInput(FloatInput):
	@classmethod
	def builder(self, desc, rec=None):
		v = get_value(desc, rec=rec)
		kw = desc.get('uiparams', {})
		w = PriceInput(**kw)
		if v is not None:
			w.setValue(v)
		return w
		
Factory.register('PriceView', PriceView)


UiFactory.register('price', PriceInput.builder, PriceView.builder)
