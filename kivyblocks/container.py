# container is ScrollView with a dataloader
from kivy.uix.scrollview import ScroppView
from kivy.properties import DictProperty, ListProperty, BooleanProperty
from .paging import Paging, RelatedLoader

class LayoutBuildFailed(Exception):
	def __init__(self, desc):
		self.desc = desc
	
	def __str__(self):
		return str(self.desc)
	
	def __expr__(self):
		return str(self)

class Container(ScrollView):
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
	loader = DictProperty({})
	data = ListProperty(None)
	layout = DictProperty({})
	viewer = DictProperty({})
	extend_x = BooleanProperty(False)
	content = None
	def __init__(self, **kw):
		super(Container, self).__init__(**kw)
		self.content = Blocks.widgetBuild(self.layout, self)
		if not self.content:
			raise LayoutBuildFailed
		if self.do_scroll_x:
			self.content.bind(minimum_height=layout.setter('width'))
		if self.do_scroll_y:
			self.content.bind(minimum_height=layout.setter('height'))
		super().add_widget(self.content)
		self.dataloader = RelatedLoader(target=self, **self.loader)
		self.dataloader.bind(on_deletepage=self.delete_page)
		self.dataloader.bind(on_pageloaded=self.add_page)
		self.dataloader.bind(on_pageloaded=self.update_tailer_info)
		self.dataloader.bind(on_newbegin=self.clearRows)

	def delete_page(self, ):
	def add_page(self, ):
	def clear_records(self, ):

	def add_widget(self, w, index=0):
		return self.content.add_widget(w,index=index)
	
	def remove_widget(self, w):
		return self.content.remove_widget(w)
	
	def clear_widgets(self):
		return self.content.clear_widgets()
	
	def add_data(self, row_data):
		desc = self.transfer(row_data)
		w = Blocks.widgetBuild(desc)
		if w:
			self.add_widget(w)
