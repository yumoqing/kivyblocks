
from ..baseWidget import FloatInput
from ..utils import *
from .float import FloatView
from .factory import UiFactory, get_value

def amountstr(amount,dec):
	f = '%%.0%df' % dec
	s = f % amount
	parts = s.split('.')
	p_int = parts[0]
	subs = []
	if p_int[0] == '-':
		subs.append('-')
		p_int = p_int[1:]
	l = [i for i in p_int]
	l.reverse()
	k = []
	for i,c in enumerate(l):
		if i and (i) % 3 == 0:
			k.append(',')
		k.append(c)
	k.reverse()
	subs.append(''.join(k))
	if len(parts) > 1:
		subs.append(f'.{parts[1]}')
	return ''.join(subs)

class AmountView(FloatView):
	def on_value(self, *args):
		if self.value is None:
			self.text = self.nullstr
		else:
			self.text = self.amount_str()
	
	def amount_str(self):
		return amountstr(self.value, self.desc)

	def builder(self, desc, rec=None):
		v = get_value(desc, rec=rec)
		defaultvalue = desc.get('nullstr', '')
		return AmountView(value=v,
						dec=desc.get('dec', 2),
						nullstr=defaultvale,
						font_size=CSize(1), 
						halign='right', 
						valign='middle'
		)

class AmountInput(FloatInput):
	def input_filter(self,substring, from_undo=False):
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
		x = StrInput.insert_text(self,s, from_undo=from_undo)
		y = amountstr(x, self.dec)
		return y

	def getValue(self):
		txt = ''.join(self.text.split(','))
		return float(txt)

	@classmethod
	def builder(self, desc, rec=None):
		v = get_value(desc, rec=rec)
		kw = desc.get('uiparams', {})
		w = AmountInput(**kw)
		if v is not None:
			w.setValue(v)
		return w

UiFactory.register('amount', AmountInput.builder, AmountView.builder)

