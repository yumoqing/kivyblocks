import time
try:
    import ujson as json
except:
	import json
from functools import partial

from kivy.logger import Logger
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.graphics import Fbo
from kivy.uix.button import ButtonBehavior
from kivy.clock import Clock
from kivy.properties import BooleanProperty, StringProperty, \
		OptionProperty, DictProperty, NumericProperty, ListProperty
from kivy.properties import ListProperty
from kivy.graphics import Color, Rectangle
from kivy.app import App
from kivy.factory import Factory

from appPublic.dictObject import DictObject
from appPublic.uniqueID import getID
from appPublic.myTE import string_template_render

from .utils import *
from .baseWidget import Text, HBox, VBox
from .scrollpanel import ScrollPanel
from .paging import Paging, RelatedLoader
from .ready import WidgetReady
from .toolbar import Toolbar
from .bgcolorbehavior import BGColorBehavior
from .widget_css import WidgetCSS
from .uitype.factory import UiFactory

class BLabel(ButtonBehavior, Text):
	def __init__(self, **kw):
		ButtonBehavior.__init__(self)
		Text.__init__(self,**kw)
		self.csscls = 'dummy'
		
class Cell(ButtonBehavior, WidgetCSS, BoxLayout):
	colume_name = StringProperty(None)
	cell_type = OptionProperty('data', \
			options=['data', 'header'])
	def __init__(self,row,desc, **kw):
		"""
		desc:{
			width,
			datatype:fff
			value:
			format:
			on_press:
		}
		"""
		self.desc = desc
		self.row = row
		super().__init__(size_hint=(None,None),
							width = self.desc['width'],
							height = self.row.part.datagrid.rowHeight()
		)
		self.csscls=self.row.part.datagrid.row_normal_css
		if self.row.header:
			self.csscls=self.row.part.datagrid.header_css
		if desc['header']:
			bl = Text(i18n=True, text=str(desc['value']),
				font_size=CSize(1),wrap=True,
				halign='left', valign='middle'
			)
			self.cell_type = 'header'
		else:
			self.cell_type = 'data'
			bl = UiFactory.build_view_widget(desc,self.row.row_data) 
		self.colume_name = desc['name']
		if bl:
			self.add_widget(bl)

class Row(BoxLayout):
	def __init__(self,part, rowdesc,header=False,data=None, **kw):
		"""
		rowdesc=[
			{
				width,
				name
				value
				on_press
			}

		"""
		self.part = part
		self.header = header
		self.row_data = data
		self.row_id = None
		self.linewidth = self.part.datagrid.linewidth
		self.rowdesc = rowdesc
		opts = kw.copy()
		opts.update({
			"spacing":self.linewidth,
			"orientation":"horizontal"
		})
		super(Row, self).__init__(**opts)
		self.height = self.part.datagrid.rowHeight()
		self.init(0)

	def on_row_press(self, *args):
		pass

	def init(self,t):
		w = 0
		h = 0
		for c in self.rowdesc:
			c['header'] = self.header
			cell = Cell(self,c)
			self.add_widget(cell)
			cell.bind(on_press=self.part.datagrid.cell_pressed)
			w += cell.width
		self.size_hint = None,None
		self.width = w + self.linewidth * (len(self.rowdesc)+1)

	def unselected(self):
		self.select(False)

	def selected(self):
		self.select(True)

	def select(self, flag):
		for c in self.children:
			if flag:
				c.csscls = self.part.datagrid.row_selected_css
			else:
				c.csscls = self.part.datagrid.row_normal_css

class Header(WidgetReady, ScrollPanel):
	def __init__(self,part,**kw):
		SUPER(Header, self, kw)
		self.part = part
		self.init(1)
		self.bind(on_scroll_stop=self.part.datagrid.scrollstop)
		if self.part.freeze_flag:
			self.bar_width = 0
		self.bar_width = 0

	def init(self,t):
		rd = [ f.copy() for f in self.part.rowdesc ]
		[ f.update({'value':self.part.fields[i].get('label', \
							self.part.fields[i].get('name'))}) \
							for i,f in enumerate(rd) ]
		self.header = Row(self.part,rd,header=True)
		self.add_widget(self.header)
		self.height = self.header.height

class Body(WidgetReady, ScrollPanel):
	def __init__(self,part,**kw):
		self.part = part
		SUPER(Body, self, kw)
		self._inner.spacing = self.part.datagrid.linewidth
		self.size_hint=(1,1)
		self.idRow = {}
		self.bind(on_scroll_stop=self.part.datagrid.scrollstop)
		if self.part.freeze_flag:
			self.bar_width = 0

	def addRow(self,id, data,index=0):
		rd = [ f.copy() for f in self.part.rowdesc ]
		[ f.update({'value':data.get(f['name'])}) for f in rd ]
		row = Row(self.part,rd,data=data)
		row.row_id = id
		self.add_widget(row,index=index)
		self.idRow[id] = row
		return row
	
	def clearRows(self):
		self.idRow = {}
		self.clear_widgets()

	def delRowById(self,id):
		row = self.idRow.get(id)
		if row:
			self.remove_widget(row)
		if self.idRow.get(id):
			del self.idRow[id]

	def getRowData(self,rowid):
		return self.idRow[rowid].row_data

	def getRowHeight(self):
		return self.part.datagrid.rowHeight()

	def get_row_by_id(self, rowid):
		return self.idRow.get(rowid)

class DataGridPart(WidgetReady, BoxLayout):
	def __init__(self,dg, freeze_flag, fields):
		self.datagrid = dg
		self.fields = fields
		self.freeze_flag = freeze_flag
		self.fields_width = None
		BoxLayout.__init__(self, orientation='vertical')
		WidgetReady.__init__(self)
		self.init(0)

	def setWidth(self):
		if self.freeze_flag:
			self.size_hint_x = None
			self.width = self.getFieldsWidth()

	def getFieldsWidth(self):
		if not self.fields_width:
			width = 0
			for f in self.rowdesc:
				width += f['width']
			self.fields_width =  width
		return self.fields_width

	def init(self,t):
		rd = []
		for f in self.fields:
			r = f.copy()
			r['width'] = CSize(f.get('width',10))
			rd.append(r)
		self.rowdesc = rd
		self.setWidth()
		kw = {}
		if self.freeze_flag:
			kw['width'] = self.fields_width
			kw['size_hint'] = (None,None)
		else:
			kw['size_hint'] = (1,None)
		kw['height'] = self.datagrid.rowHeight()
			
		self.header = None
		if not self.datagrid.noheader:
			self.header = Header(self,**kw)
			self.add_widget(self.header)
		inner = {
			"widgettype":"VBox",
			"options":{
			}
		}
		self.body = Body(self)
		self.add_widget(self.body)
		if not self.freeze_flag:
			self.body.bind(pos=self.datagrid.bodyOnSize,
							size=self.datagrid.bodyOnSize)
		
	def clearRows(self):
		return self.body.clearRows()

	def addRow(self,id, data):
		return self.body.addRow(id, data)

	def on_size(self, o, s=None):
		if not hasattr(self, 'body'):
			return
		if hasattr(self, '_toolbar'):
			if self._toolbar is not None:
				self._toolbar.width = self.width
		self.body.size_hint_y = None
		if self.header:
			self.body.height = self.height - self.header.height
		else:
			self.body.height = self.height


class DataGrid(VBox):
	"""
	DataGrid data format:
	{
		"widgettype":"DataGrid",
		"dataloader":{
			"page":1,
			"rows":60,
			"dataurl":"eeee",
			"params":{
			}
		},
		"tailer":{
			"options":{
			}
			"info":[
				"total_cnt",
				"total_page",
				"page_rows",
				"curpage"
			],
			"others":{
			}
		},
		"row_height": CSize,
		"header_css":"default",
		"body_css":"default",
		"spacing":1,
		"fields":[
			{
				"name":"field1",
				"label":"Field1",
				"datatype":"str",
				"uitype":"code",
				"value_field":,
				"text_field":
			},
			{
				"name":"field2",
				"label":"Field2",
				"viewer":{
					block dic
				}
			}
			...
		]
		"binds":[
		]
	}
	"""
	row_selected = BooleanProperty(False)
	row_normal_css = StringProperty('default')
	row_selected_css = StringProperty('default')
	header_css = StringProperty('default')
	body_css = StringProperty('default')
	row_height = NumericProperty(2)
	noheader = BooleanProperty(False)
	linewidth = NumericProperty(1)
	toolbar = DictProperty(None)
	dataloader = DictProperty(None)
	fields = ListProperty(None)
	tailer = DictProperty(None)
	def __init__(self,**options):
		self.select_rowid = None
		self.rowheight = None
		self.on_sizeTask = None
		self.selected_rowid = None
		self.show_rows = 0
		self._toolbar = None
		self.freeze_part = None
		self.normal_part = None
		SUPER(DataGrid, self, options)
		self.freeze_fields = self.getPartFields(freeze_flag=True)
		self.normal_fields = self.getPartFields(freeze_flag=False)
		if not self.dataloader:
			raise Exception('DataGrid need a DataLoader')
		self._dataloader = RelatedLoader(target=self, **self.dataloader)
		self._dataloader.bind(on_deletepage=self.delete_page)
		self._dataloader.bind(on_pageloaded=self.add_page)
		self._dataloader.bind(on_pageloaded=self.update_tailer_info)
		self._dataloader.bind(on_newbegin=self.clearRows)
		self.register_event_type('on_selected')
		self.register_event_type('on_rowpress')
		self.register_event_type('on_cellpress')
		self.register_event_type('on_headerpress')
		self.createDataGridPart()
		self.createToolbar()
		if self._toolbar:
			self.add_widget(self._toolbar)
		
		b = BoxLayout(orientation='horizontal')
		if self.freeze_part:
			b.add_widget(self.freeze_part)
		if self.normal_part:
			b.add_widget(self.normal_part)
		self.add_widget(b)
		if self.tailer:
			self.tailer_widgets = {}
			self.build_tailer(self.tailer)

	def on_rowpress(self, *args):
		print('on_rowpress fire, args=', args)

	def on_cellpress(self, *args):
		print('on_cesspress fire, args=', args)

	def on_headerpress(self, *args):
		print('on_headerpress fire, args=', args)

	def cell_pressed(self, o):
		if o.cell_type == 'header':
			self.dispatch('on_headerpress', o.colume_name)
			return
		row = o.row
		if self.selected_rowid:
			self.unselect_row(self.selected_rowid)
		
		self.selected_rowid = row.row_id
		self.select_row(row.row_id)
		self.dispatch('on_cellpress', o)
		self.dispatch('on_rowpress', row)
		self.dispatch('on_selected', row)

	def unselect_row(self, row_id):
		if self.freeze_part:
			row = self.freeze_part.body.get_row_by_id(row_id)
			if not row:
				return
			row.unselected()
		row = self.normal_part.body.get_row_by_id(row_id)
		if not row:
			return
		row.unselected()

	def select_row(self, row_id):
		if self.freeze_part:
			row = self.freeze_part.body.get_row_by_id(row_id)
			row.selected()
		row = self.normal_part.body.get_row_by_id(row_id)
		row.selected()
		
	def on_ready(self, *args):
		self.loadData()

	def build_tailer(self, tailer_desc):
		kw = tailer_desc.get('options', {})
		kw.update({
			'size_hint_y':None,
			'height':self.rowheight
		})
		w = HBox(**kw)
		self.add_widget(w)
		self.show_infos(w, tailer_desc.get('info'))
		if tailer_desc.get('others'):
			w1 = self.build_tailer_other(tailer_desc.get('others'))
			if w1:
				w.add_widget(w1)
	
	def update_tailer_info(self, *args):
		if not hasattr(self, 'tailer_widgets'):
			return
		for n,w in self.tailer_widgets.items():
			w.text = self.loader_info(n)

	def show_infos(self, tailer_widget, info_names):
		for n in info_names:
			desc = {
				"widgettype":"Text",
				"options":{
					"text":n,
					"i18n":True,
				}
			}
			w = Factory.Blocks().widgetBuild(desc)
			tailer_widget.add_widget(w)
			tailer_widget.add_widget(Label(text=':'))
			self.tailer_widgets[n] = Label(text=self.loader_info(n))
			tailer_widget.add_widget(self.tailer_widgets[n])

	def build_tailer_others(desc):
		return Factory.Blocks().widgetBuild(desc)

	def loader_info(self, n):
		if hasattr(self._dataloader, n):
			txt=getattr(self._dataloader, n, 0)
			if txt is None:
				txt = '0'
			txt = str(txt)
			return txt

	def locater(self,pos):
		self.normal_part.body.scroll_y = pos
		if self.freeze_part:
			self.freeze_part.body.scroll_y = pos

	def scrollstop(self,o,v=None):
		if not self.noheader and o == self.normal_part.header:
			self.normal_part.body.scroll_x = o.scroll_x
			return
		if o == self.normal_part.body:
			if not self.noheader:
				self.normal_part.header.scroll_x = o.scroll_x
			if self.freeze_part:
				self.freeze_part.body.scroll_y = o.scroll_y
		if self.freeze_part and o == self.freeze_part.body:
			self.normal_part.body.scroll_y = o.scroll_y

		if o.scroll_y <= 0.01:
			self._dataloader.loadNextPage()
		if o.scroll_y >= 0.99:
			self._dataloader.loadPreviousPage()

	def getValue(self):
		if not self.select_rowid:
			return None
		return self._getRowData(self.select_rowid)
	
	def _getRowData(self, rowid):
		d = {}
		if self.freeze_part:
			d.update(self.freeze_part.body.getRowData(rowid))
		d.update(self.normal_part.body.getRowData(rowid))
		return DictObject(**d)

	def bodyOnSize(self,o,s):
		if self.on_sizeTask is not None:
			self.on_sizeTask.cancel()
		self.on_sizeTask = Clock.schedule_once(self.calculateShowRows,0.3)

	def rowHeight(self):
		if not self.rowheight:
			self.rowheight = CSize(self.row_height)
		return self.rowheight
	
	def calculateShowRows(self,t):
		self.getShowRows()
		self._dataloader.setPageRows(self.show_rows * 2)

	def getShowRows(self):
		if self.show_rows == 0:
			return 60
		self.show_rows = int(self.rowHeight() / self.normal_part.body.height)
		return self.show_rows * 2

	def clearRows(self, *args):
		if self.freeze_part:
			self.freeze_part.body.clearRows()
		self.normal_part.body.clearRows()

	def add_page(self,o,data):
		dir = data['dir']
		if not self.show_rows:	
			self.getShowRows()

		ids = []
		recs = data['data']
		idx = 0
		if dir == 'up':
			recs.reverse()
			idx = -1
		recs1 = recs[:self.show_rows]
		recs2 = recs[self.show_rows:]
		self._fbo = Fbo(size=self.size)
		with self._fbo:
			self._background_color = Color(0,0,0,1)
			self._background_rect = Rectangle(size=self.size)
		for r in recs1:
			id = self.addRow(r,index=idx)
			ids.append(id)
		with self.canvas:
			self._fbo_rect = Rectangle(size=self.size,
								texture=self._fbo.texture)

		data['idx'] = idx
		data['ids'] = ids
		data['data'] = recs2
		f = partial(self.add_page_delay,data)
		Clock.schedule_once(f, 0)

	def add_page_delay(self, data, *args):
		recs = data['data']
		page = data['page']
		idx = data['idx']
		ids = data['ids']
		self._fbo = Fbo(size=self.size)
		with self._fbo:
			self._background_color = Color(0,0,0,1)
			self._background_rect = Rectangle(size=self.size)
		for r in recs:
			id = self.addRow(r,index=idx)
			ids.append(id)
		with self.canvas:
			self._fbo_rect = Rectangle(size=self.size,
								texture=self._fbo.texture)
		self._dataloader.bufferObjects(page,ids)
		x = self._dataloader.getLocater()
		self.locater(x)

	def delete_page(self,o,data):
		for id in data:
			self.delRow(id)

	def addRow(self,data, **kw):
		id = getID()
		f_row = None
		if self.freeze_part:
			self.freeze_part.body.addRow(id, data, **kw)
		self.normal_part.body.addRow(id, data, **kw)
		return id

	def delRow(self,id,**kw):
		if self.freeze_part:
			self.freeze_part.body.delRowById(id)
		self.normal_part.body.delRowById(id)

	def createToolbar(self):
		if self.toolbar:
			self._toolbar = Toolbar(**self.toolbar)

	def on_selected(self,row):
		print("DataGrid():on_selected fire")

	def loadData(self,*args, **kwargs):
		kwargs['page'] = 1
		self.selected_rowid = None
		self._dataloader.do_search(None,kwargs)

	def createDataGridPart(self):
		self.freeze_part = None
		self.normal_part = None
		if self.freeze_fields:
			self.freeze_part = DataGridPart(self,True, self.freeze_fields)
		if self.normal_fields:
			self.normal_part = DataGridPart(self, False, self.normal_fields)

	def getPartFields(self,freeze_flag:bool=False) -> list:
		fs = []
		for f in self.fields:
			if freeze_flag:
				if f.get('freeze',False):
					fs.append(f)
			else:
				if not f.get('freeze',False):
					fs.append(f)
		return fs
	
	def get_selected_data(self):
		if not self.selected_rowid:
			return {}
		data = {}
		row_id = self.selected_rowid
		if self.freeze_part:
			row = self.freeze_part.body.get_row_by_id(row_id)
			data.update(row.row_data)
		row = self.normal_part.body.get_row_by_id(row_id)
		data.update(row.row_data)
		return data
