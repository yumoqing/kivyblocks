
from kivy.uix.label import Label
from kivy.properties import NumericProperty, ColorProperty
from kivy.factory import Factory

from kivyblocks.uitype import view_register, get_value

class PriceView(Label):
	dec = NumericProperty(4)
	old_price = NumericProperty(None)
	price = NumericProperty(None)
	nor_color = ColorProperty([0.9,0.9,0.9,1]) # white
	inc_color = ColorProperty([0.9,0,0,1]) 	# red
	dec_color = ColorProperty([0,0.9,0,1])	# green
	def __init__(self, **kw):
		super(PriceView, self).__init__(text='', **kw)

	def on_price(self, price):
		if self.price is None:
			return
		if not isinstance(self.price, float) and \
					not isinstance(self.price, int):
			return

		f = '%%.0%df' % self.dec
		self.text = f % price
		if self.old_price is None:
			self.color = self.nor_color
		elif self.price > self.old_price:
			self.color = self.inc_color
		elif self.price < self.old_price:
			self.color = self.dec_color
		else:
			self.color = nor_color
		self.old_price = self.price

	def getValue(self):
		return self.price

	def setValue(self, v):
		self.price = v

Factory.register('PriceView', PriceView)

def build_view_price_widget(desc, rec=None):
	v = get_value(desc, rec=rec)
	return Factory.PriceView(price=v,
					font_size=CSize(1),
					halign='right',
					valign='middle'
	)

view_register('price', build_view_price_widget)
