import time
import ujson as json
from functools import partial

from kivy.logger import Logger
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import ButtonBehavior
from kivy.clock import Clock
from kivy.properties import BooleanProperty, StringProperty
from kivy.properties import ListProperty
from kivy.graphics import Color, Rectangle
from kivy.app import App
from kivy.factory import Factory

from appPublic.dictObject import DictObject
from appPublic.timecost import TimeCost
from appPublic.uniqueID import getID
from appPublic.myTE import string_template_render

from .utils import CSize, setSizeOptions, loading, loaded, absurl, alert
from .baseWidget import Text, HBox, VBox
from .scrollpanel import ScrollPanel
from .paging import Paging, RelatedLoader
from .ready import WidgetReady
from .toolbar import Toolbar
from .bgcolorbehavior import BGColorBehavior
from .widget_css import WidgetCSS

def field_widget(desc, rec):
	viewer = desc.get('viewer')
	if viewer:
		if not isinstance(viewer,str):
			viewer = json.dumps(viewer)
		rendered = string_template_render(viewer, rec)
		dic = json.loads(rendered)
		if dic is None:
			return None
		blocks = Factory.Blocks()
		return blocks.widgetBuild(dic)

	uitype = desc.get('uitype', 'str')
	if uitype is None:
		uitype = desc.get('datatype')
	if uitype in [ 'str' 'date', 'time', 'timestamp' ]:
		return Text(text = str(desc['value']), 
					font_size=CSize(1),wrap=True,
					halign='left', valign='middle'
			)
	if uitype in [ 'long', 'int','integer' ]:
		return Text(text=str(desc['value']),
					font_size=CSize(1), wrap=True,
					halign='right', valign='middle'
			)
	if uitype == 'float':
		f = '%%.0%df' % desc.get('dec',2)
		return Text(text=f % float(desc['value']),
					font_size=CSize(1), wrap=True,
					halign='right', valign='middle'
			)
	
	return Text(text = str(desc['value']), 
				font_size=CSize(1),wrap=True,
				halign='left', valign='middle'
		)


class BLabel(ButtonBehavior, Text):
	def __init__(self, **kw):
		ButtonBehavior.__init__(self)
		Text.__init__(self,**kw)
		self.csscls = 'dummy'
		
class Cell(ButtonBehavior, WidgetCSS, BoxLayout):
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
		csscls=self.row.part.datagrid.body_css
		if self.row.header:
			csscls=self.row.part.datagrid.header_css
		super().__init__(size_hint=(None,None),
							width = self.desc['width'],
							height = self.row.part.datagrid.rowHeight(),
							csscls=csscls
		)
		if desc['header']:
			bl = Text(i18n=True, text=str(desc['value']),
				font_size=CSize(1),wrap=True,
				halign='left', valign='middle'
			)
		else:
			bl = field_widget(desc,self.row.row_data) 
		if bl:
			self.add_widget(bl)

	def on_press(self,o=None):
		if not self.row.header:
			self.row.selected()

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


	def init(self,t):
		w = 0
		h = 0
		for c in self.rowdesc:
			c['header'] = self.header
			cell = Cell(self,c)
			self.add_widget(cell)
			w += cell.width
		self.size_hint = None,None
		self.width = w + self.linewidth * (len(self.rowdesc)+1)

	def selected(self):
		if not hasattr(self,'row_data'):
			return # header
		print('row selected',self.row_id, self.row_data)

		self.part.datagrid.row_selected = True
		self.part.datagrid.select_rowid = self.row_id
		self.part.datagrid.select_row = self
		self.part.datagrid.dispatch('on_selected',self)

class Header(WidgetReady, ScrollPanel):
	def __init__(self,part,**kw):
		super(Header, self).__init__(**kw)
		self.part = part
		self.init(1)
		self.bind(on_scroll_stop=self.part.datagrid.on_scrollstop)
		if self.part.freeze_flag:
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
		kw.update({'spacing':self.part.datagrid.linewidth})
		super(Body, self).__init__(**kw)
		self.size_hint=(1,1)
		self.idRow = {}
		self.bind(on_scroll_stop=self.part.datagrid.on_scrollstop)
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
		self.body.size_hint_y = None
		if self.header:
			self.body.height = self.height - self.header.height
		else:
			self.body.height = self.height


class DataGrid(WidgetReady, BoxLayout):
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
	def __init__(self,**options):
		options['orientation'] = 'vertical'
		BoxLayout.__init__(self)
		WidgetReady.__init__(self)
		self.select_rowid = None
		self.options = options
		self.rowheight = None
		self.on_sizeTask = None
		self.selected_rowid = None
		self.show_rows = 0
		self.toolbar = None
		self.freeze_part = None
		self.normal_part = None
		self.page_rows = self.options.get('page_rows', 60)
		self.params = self.options.get('params',{})
		self.total_cnt = 0
		self.max_row = 0
		self.row_height = self.options.get('row_height',2)
		self.header_css = self.options.get('header_css','default')
		self.noheader = self.options.get('noheader',False)
		self.body_css = self.options.get('body_css', 'default')
		self.linewidth = self.options.get('linewidth',1)
		self.curpage = 0
		self.loading = False
		self.freeze_fields = self.getPartFields(freeze_flag=True)
		self.normal_fields = self.getPartFields(freeze_flag=False)
		ldr_desc = options.get('dataloader')
		if not ldr_desc:
			raise Exception('DataGrid need a DataLoader')
		self.dataloader = RelatedLoader(target=self, **ldr_desc)
		self.dataloader.bind(on_deletepage=self.delete_page)
		self.dataloader.bind(on_pageloaded=self.add_page)
		self.dataloader.bind(on_newbegin=self.clearRows)
		self.register_event_type('on_selected')
		self.register_event_type('on_scrollstop')
		self.createDataGridPart()
		self.createToolbar()
		if self.toolbar:
			self.add_widget(self.toolbar)
		
		b = BoxLayout(orientation='horizontal')
		if self.freeze_part:
			b.add_widget(self.freeze_part)
		if self.normal_part:
			b.add_widget(self.normal_part)
		self.add_widget(b)
	
	def locater(self,pos):
		self.normal_part.body.scroll_y = pos
		if self.freeze_part:
			self.freeze_part.body.scroll_y = pos

	def on_scrollstop(self,o,v=None):
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

		if o.scroll_y <= 0.001:
			self.dataloader.loadNextPage()
		if o.scroll_y >= 0.999:
			self.dataloader.loadPreviousPage()

	def getValue(self):
		if not self.select_rowid:
			return None
		return self._getRowData(self.select_rowid)
	
	def _getRowData(self, rowid):
		d = {}
		if self.freeze_part:
			d.update(self.freeze_part.body.getRowData(rowid))
		d.update(self.normal_part.body.getRowData(rowid))
		print('getValue() return=',d)
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
		self.dataloader.setPageRows(self.show_rows * 2)

	def getShowRows(self):
		if self.show_rows == 0:
			return 60
		self.show_rows = int(self.rowHeight() / self.normal_part.body.height)
		return self.show_rows * 2

	def clearRows(self, *args):
		print('dg.py:clearRows() called')
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
		for r in recs1:
			id = self.addRow(r,index=idx)
			ids.append(id)

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
		for r in recs:
			id = self.addRow(r,index=idx)
			ids.append(id)
		self.dataloader.bufferObjects(page,ids)
		x = self.dataloader.getLocater()
		self.locater(x)

	def delete_page(self,o,data):
		print('dg.py:delete_page() called')
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
		if 'toolbar' in self.options.keys():
			tb = self.options['toolbar']
			self.toolbar = Toolbar(**tb)

	def on_selected(self,row):
		print("DataGrid():on_selected fire")

	def loadData(self,*args, **kwargs):
		print('args=', args, 'kwargs=',kwargs)
		kwargs['page'] = 1
		self.dataloader.do_search(None,kwargs)

	def createDataGridPart(self):
		self.freeze_part = None
		self.normal_part = None
		if self.freeze_fields:
			self.freeze_part = DataGridPart(self,True, self.freeze_fields)
		if self.normal_fields:
			self.normal_part = DataGridPart(self, False, self.normal_fields)

	def getPartFields(self,freeze_flag:bool=False) -> list:
		fs = []
		for f in self.options['fields']:
			if freeze_flag:
				if f.get('freeze',False):
					fs.append(f)
			else:
				if not f.get('freeze',False):
					fs.append(f)
		return fs
	
