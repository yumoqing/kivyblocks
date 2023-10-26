# container is ScrollView with a dataloader
import json
from appPublic.myTE import MyTemplateEngine
from kivy.uix.scrollview import ScrollView
from kivy.properties import DictProperty, ListProperty, BooleanProperty, StringProperty, NumericProperty
from kivy.clock import Clock
from kivyblocks.blocks import Blocks
from kivyblocks.paging import RelatedLoader
from kivyblocks.widget_css import WidgetCSS

class LayoutBuildFailed(Exception):
	def __init__(self, desc):
		self.desc = desc
	
	def __str__(self):
		return str(self.desc)
	
	def __expr__(self):
		return str(self)

class Container(WidgetCSS, ScrollView):
	"""
		"loader":{
			"page":1,
			"rows":60,
			"dataurl":"eeee",
			"params":{
				k:v
			}
		},
	"""
	idField = StringProperty('id')
	loader = DictProperty({})
	data = ListProperty(None)
	layout = DictProperty({})
	viewer = DictProperty({})
	min_threhold = NumericProperty(0.01)
	max_htrehold = NumericProperty(0.99)
	extend_x = BooleanProperty(False)
	content = None
	def __init__(self, **kw):
		self.dataloader = None
		self.engine = MyTemplateEngine('.')
		self.id_widget = {}
		super(Container, self).__init__(**kw)
		self.content = Blocks().widgetBuild(self.layout)
		if not self.content:
			raise LayoutBuildFailed
		if self.do_scroll_x:
			self.content.bind(minimum_width=self.content.setter('width'))
		if self.do_scroll_y:
			self.content.bind(minimum_height=self.content.setter('height'))
		self.add_widget(self.content)
		self.viewer_tmpl = json.dumps(self.viewer)
		self.bind(on_scroll_stop = self.on_scrollstop)
		if self.data:
			d = {
				"dir":"down",
				"rows":self.data,
				"total":len(self.data)
			}
			self.add_page(d)
		
		if self.loader:
			self.dataloader = RelatedLoader(target=self, **self.loader)
			self.dataloader.bind(on_deletepage=self.delete_page)
			self.dataloader.bind(on_pageloaded=self.add_page)
			self.dataloader.bind(on_newbegin=self.clear_records)
			Clock.schedule_once(self.loadData, 0.5)

	def print_info(self, *args):
		print(f"{self.scroll_distance=}, {self.scroll_timeout=}, {self.do_scroll_x=} {self.do_scroll_y=}, {self.scroll_x=}, {self.scroll_y=}, {self.content.size=}")

	def parse_viewer(self, rec):
		return json.loads(self.engine.renders(self.viewer_tmpl, rec))

	def loadData(self, *args, **kw):
		kw['page'] = 1
		self.dataloader.do_search(None,kw)

	def add_record(self, rec, tail=True):
		desc = self.parse_viewer(rec)
		w = Blocks().widgetBuild(desc)
		if w:
			idx = 0
			if not tail:
				idx = -1
			id = rec.get(self.idField)
			self.id_widget[id] = w
			self.content.add_widget(w, index=idx)
		else:
			print(f'create widget error {self.viewer_tmpl=}, {rec=}')

	def delete_record(self, rec):
		id = rec.get(self.idField)
		w = self.id_widget.get(id)
		if w:
			self.content.remove_widget(w)
		del self.id_widget[id]

	def delete_page(self, o, d):
		# print(f'delete_page():{o=}, {d=}')
		for r in d:
			self.delete_record(r)

	def add_page(self, o, d):
		# print(f'add_page():{o=},{d=}')
		dir = d.get('dir', 'down')
		recs = d.get('data', [])
		tail = True
		if dir != 'down':
			tail = False
			recs.reverse()

		for r in recs:
			self.add_record(r, tail=tail)
		if self.extend_x:
			self.scroll_x = d['locator']
		else:
			self.scroll_y = d['locator']

	def clear_records(self, o):
		# print(f'clear_records():{o=}')
		self.content.clear_widgets()
		self.id_Widget = {}

	def on_scrollstop(self, o, d=None):
		if self.dataloader is None:
			return
		if self.extend_x:
			if self.scroll_x < self.min_threhold:
				self.dataloader.loadNextPage()
			if self.scroll_x > self.max_htrehold:
				self.dataloader.loadPreviousPage()
			print('return here ...')
			return
		if self.dataloader.loading:
			print('loading is True')
			return
		if self.scroll_y < self.min_threhold:
			print('load next page ...')
			self.dataloader.loadNextPage()
		if self.scroll_y > self.max_htrehold:
			print('load previous page ...')
			self.dataloader.loadPreviousPage()

