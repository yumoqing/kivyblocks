from appPublic.timeUtils import curDateString, monthMaxDay

from kivy.clock import Clock
from kivy.factory import Factory
from kivy.properties import NumericProperty, BooleanProperty, \
			OptionProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivyblocks.baseWidget import SelectInput, HBox
from kivyblocks.utils import CSize

date_format_info = {
	'yyyy-mm-dd':{
		'ystart':0,
		'mstart':5,
		'dstart':8
	},
	'mm-dd-yyyy':{
		'ystart':6,
		'mstart':0,
		'dstart':3
	},
	'dd-mm-yyyy':{
		'ystart':6,
		'mstart':3,
		'dstart':0
	},
	'yyyymmdd':{
		'ystart':0,
		'mstart':4,
		'dstart':6
	},
	'mmddyyyy':{
		'ystart':4,
		'mstart':0,
		'dstart':2
	},
	'ddmmyyyy':{
		'ystart':4,
		'mstart':2,
		'dstart':0
	}
}
def get_datestr(y, m, d, dateformat):
	def replace_slice(s, v, pos,length):
		x = '%0' + str(length) + 'd'
		sv = x % v
		d = ''
		if pos > 0:
			d = s[0:pos]
		d = d + sv
		d = d + s[pos+length:]
		return d
	if y is None:
		return None

	info = date_format_info.get(dateformat)
	if info is None:
		return None
	ret = dateformat
	ret = replace_slice(ret, y, info['ystart'], 4)
	ret = replace_slice(ret, m, info['mstart'], 4)
	ret = replace_slice(ret, d, info['dstart'], 4)
	return ret

def get_ymd(dstr, dateformat):
	if not dstr:
		return None, None, None

	info = date_format_info.get(dateformat)
	if info is None:
		return None, None, None
	y = int(dstr[info['ystart'], info['ystart']+4])
	m = int(dstr[info['mstart'], info['mstart']+2])
	d = int(dstr[info['dstart'], info['dstart']+2])
	return y, m, d

class YearInput(SelectInput):
	nullable = BooleanProperty(True)
	e_year = NumericProperty(None)
	def __init__(self, show_years=10, **kw):
		super(YearInput, self).__init__(**kw)
		self.show_years = show_years
		self.showed_min = None
		self.showed_max = None
		self.valueField = self.dropdown.valueField
		self.textField = self.dropdown.textField
		self.reopen = False
		self.dropdown.bind(on_dismiss=self.reopen_dropdown)

	def e_year_change(self, y):
		self.e_year = y
		smin = self.e_year - int((self.show_years)/2)
		smax = smin + self.show_years
		self.set_selectable_data(self.years_data(smin, smax))
		
	def years_data(self, smin, smax):
		d = [
			{
				self.valueField:-10000,
				self.textField:'-'
			}
		]
		self.showed_min = smin
		self.showed_max = smax
		while smin < smax:
			d.append({
				self.valueField:smin,
				self.textField:'%4d' % smin
			})
			smin += 1
		if self.nullable:
			d.append({
				None, ''
			})
		d.append({
			self.valueField:10000,
			self.textField:'+'
		})
		return d

	def reopen_dropdown(self, *args):
		if not self.reopen:
			return
		self.dropdown.open(self)

	def dropdown_select(self, o, d):
		if d[0] == -10000:
			smin = self.showed_min - self.show_years
			if smin < 0:
				smin = 0
			smax = smin + self.show_years
			self.set_selectable_data(self.years_data(smin, smax))
			self.reopen = True
			return
		if d[0] == 10000:
			smax = self.showed_max + self.show_years
			if smax > 9999:
				smax = 9999
			smin = smax - self.show_years
			self.set_selectable_data(self.years_data(smin, smax))
			self.reopen = True
			return
		super().dropdown_select(o,d)
		self.reopen = False

	def setValue(self, v):
		if v is None:
			super().setValue('')
			return

		super().setValue(v)
		self.e_year_change(v)

class DateInput(HBox):
	default_date = OptionProperty(None, options=[None, 'today'])
	date_format = OptionProperty('yyyy-mm-dd', options=[k for k in date_format_info.keys() ])
	def __init__(self, allow_copy=True, **kw):
		print('DateInput():kw=', kw)
		kw['size_hint_x'] = None
		kw['width'] = 10
		super(DateInput, self).__init__(**kw)
		self.register_event_type('on_changed')
		self.old_datestr = None
		value = kw.get('value',self.defaultdate())
		y, m, d = get_ymd(value, 'yyyy-mm-dd')
		months_data = []
		days_data = []
		for i in range(12):
			j = i + 1
			months_data.append({
				'text':'%02d' % j,
				'value':j
			})
		for i in range(31):
			j = i + 1
			days_data.append({
				'text':'%02d' % j,
				'value':j
			})
		self.days_data = days_data
		nullable = False
		if value is None:
			nullable = True
		self.yw = YearInput(data=[], nullable=nullable,
						size_hint_x=None, width=3.6)
		self.mw = SelectInput(size_hint_x=None, width=2,
						data=months_data)
		self.dw = SelectInput( size_hint_x=None, width=2,
						data=days_data)
		self.mw.set_selectable_data(months_data)
		self.dw.set_selectable_data(days_data)
		self.yw.setValue(y)
		self.mw.setValue(m)
		self.dw.setValue(d)
		self.add_widget(self.yw)
		self.add_widget(Label(text='-',size_hint_x=None, width=CSize(1)))
		self.add_widget(self.mw)
		self.add_widget(Label(text='-',size_hint_x=None, width=CSize(1)))
		self.add_widget(self.dw)
		self.yw.bind(on_changed=self.data_changed)
		self.mw.bind(on_changed=self.data_changed)
		self.dw.bind(on_changed=self.data_changed)
		self.on_size()

	def defaultdate(self):
		if self.default_date == 'today':
			return curDateString()
		return None

	def on_size(self, *args):
		if not hasattr(self, 'yw'):
			return 
		self.yw.height = self.height
		self.mw.height = self.height
		self.dw.height = self.height

	def str2ymd(self, datestr):
		if datestr is None or datestr == '':
			return None, None, None
		return get_ymd(datestr, self.dateformat)

	def ymd2str(self, y, m, d):
		if y is None:
			return None

		return get_datestr(y, m, d, self.dateformat)

	def data_changed(self, o, d):
		datestr = None
		if y is not None:
			y = self.yw.getValue()
			m = self.mw.getValue()
			d = self.dw.getValue()
			mdays = monthMaxDay(y,m)
			if o == self.yw or o == self.mw:
				data = self.days_data[:mdays]
				self.dw.set_selectable_data(data)
			if d <= mdays and d>0:
				datestr = self.ymd2str(y,m,d)

		if self.old_datestr != datestr:
			self.old_datestr = datestr
			self.dispatch('on_changed', datestr)

	def on_changed(self, *args):
		pass

	def getValue(self):
		y = self.yw.getValue()
		if y is not None:
			m = self.mw.getValue()
			d = self.dw.getValue()
			mdays = monthMaxDay(y,m)
			if d <= mdays and d>0:
				return self.ymd2str(y,m,d)
		return None

	def setValue(self, datestr):
		if datestr == '' or datestr is None:
			datestr = self.defaultdate()
		self.old_value = datestr
		y, m, d = self.str2ymd(datestr)
		self.yw.setValue(y)
		self.mw.setValue(m)
		self.dw.setValue(d)
