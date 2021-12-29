import traceback

from kivy.clock import Clock
from kivy.factory import Factory
from kivy.properties import ListProperty, BooleanProperty, \
			StringProperty, DictProperty
from kivy.uix.treeview import TreeView, TreeViewNode, TreeViewLabel
from kivy.uix.boxlayout import BoxLayout

from .threadcall import HttpClient
from .scrollpanel import ScrollPanel
from .clickable import SingleCheckBox
from .baseWidget import Text

class TreeViewComplexNode(BoxLayout, TreeViewLabel):
	otext = StringProperty(None)
	checkbox = BooleanProperty(False)
	icon = StringProperty(None)
	def __init__(self, **kw):
		super(TreeViewComplexNode, self).__init__(**kw)
		self.orientation = 'horizontal'
		if self.checkbox:
			cb = SingleCheckBox(size_hint=(None,None))
			cb.bind(on_press=self.set_checked)
			self.add_widget(cb)
		if self.icon:
			img = AsyncImage(source=self.icon)
			self.add_widget(img)
		txt = Text(otext=self.otext, i18n=True)
		txt.texture_update()
		txt.size = txt.texture_size
		self.add_widget(txt)
		
	def set_checked(self, o):
		if o.state():
			self.data['checked'] = True
		else:
			self.data['checked'] = False
			
class Hirarchy(ScrollPanel):
	url = StringProperty(None)
	params = DictProperty(None)
	method = StringProperty('get')
	idField = StringProperty(None)
	textField = StringProperty(None)
	data = ListProperty(None)
	checkbox = BooleanProperty(False)
	icon = StringProperty(None)
	def __init__(self, **kw):
		self.tree = TreeView(hide_root=True)
		self.tree.size_hint_y = None
		self.tree.bind(on_node_expand=self.check_load_subnodes)
		super(Hirarchy, self).__init__(inner=self.tree, **kw)
		if self.url:
			self.data = self.get_remote_data()

	def check_load_subnodes(self, treeview, node):
		if node.is_loaded:
			return
		data = self.get_remote_data(node)
		for d in data:
			self.create_new_node(d, node)
		node.is_loaded = True

	def create_new_node(self, data, node=None):
		n = TreeViewComplexNode(otext=data[self.textField],
			checkbox=self.checkbox,
			icon=self.icon
		)
		n.data = data
		if self.checkbox:
			cb = SingleCheckBox()
			n.add_widget(cb, index=len(n.children))
		if node:
			self.tree.add_node(n, node)
		else:
			self.tree.add_node(n)
		
	def get_remote_data(self, node=None):
		hc = HttpClient()
		params = self.params.copy() if self.params else {}
		if node:
			params['id'] = node.data[self.idField]
		d = hc(self.url, method=self.method, params=params)
		if isinstance(d, list):
			return d
		if isinstance(d, dict):
			return d['rows']
		return None

	def on_data(self, o, d=None):
		if not self.data:
			return
		for d in self.data:
			self.create_new_node(d)
			
Factory.register('Hirarchy', Hirarchy)
