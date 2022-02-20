import traceback

from kivy.clock import Clock
from kivy.factory import Factory
from kivy.properties import ListProperty, BooleanProperty, \
			StringProperty, DictProperty, NumericProperty
from kivy.uix.treeview import TreeView, TreeViewNode, TreeViewLabel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage

from .threadcall import HttpClient
from .scrollpanel import ScrollPanel
from .clickable import SingleCheckBox
from .baseWidget import Text
from .utils import CSize

from appPublic.registerfunction import getRegisterFunctionByName

class TreeViewComplexNode(BoxLayout, TreeViewLabel):
	otext = StringProperty(None)
	checkbox = BooleanProperty(False)
	icon = StringProperty(None)
	data = DictProperty(None)
	def __init__(self, **kw):
		super(TreeViewComplexNode, self).__init__(**kw)
		self.orientation = 'horizontal'
		self.size_hint_x = None
		if self.checkbox:
			cb = SingleCheckBox(size_hint=(None,None))
			cb.bind(on_press=self.set_checked)
			self.add_widget(cb)
		if self.icon:
			img = AsyncImage(source=self.icon, size_hint=(None,None))
			img.size = CSize(1,1)
			self.add_widget(img)
		txt = Text(otext=self.otext, i18n=True)
		txt.texture_update()
		txt.size_hint = (None, None)
		txt.size = txt.texture_size
		self.add_widget(txt)
		
	def set_checked(self, o):
		if not self.data:
			return
		if o.state():
			self.data['checked'] = True
		else:
			self.data['checked'] = False
			
class Hierarchy(ScrollPanel):
	url = StringProperty(None)
	params = DictProperty(None)
	method = StringProperty('get')
	idField = StringProperty(None)
	textField = StringProperty(None)
	data = ListProperty(None)
	checkbox = BooleanProperty(False)
	icon = StringProperty(None)
	single_expand = BooleanProperty(False)
	def __init__(self, **kw):
		self.register_event_type('on_press')
		self.tree = TreeView(hide_root=True)
		self.tree.size_hint = (None, None)
		self.tree.bind(on_node_expand=self.check_load_subnodes)
		self.tree.bind(selected_node=self.node_selected)
		super(Hierarchy, self).__init__(inner=self.tree, **kw)
		if self.url:
			self.data = self.get_remote_data()

	def on_press(self, node):
		print('selected node=', node)

	def node_selected(self, o, v):
		if self.tree.selected_node:
			self.dispatch('on_press', o.selected_node)

	def collapse_others(self, node):
		for n in self.tree.iterate_open_nodes(node=node.parent_node):
			if n != node and n !=node.parent_node and n.is_open:
				self.tree.toggle_node(n)

	def check_load_subnodes(self, treeview, node):
		if self.single_expand:
			self.collapse_others(node)
		if node.is_loaded:
			return
		if not self.url:
			node.is_loaded = True
			return
		data = self.get_remote_data(node)
		for d in data:
			self.create_new_node(d, node)
		node.is_loaded = True

	def create_new_node(self, data, node=None):
		n = TreeViewComplexNode(otext=data[self.textField],
			checkbox=self.checkbox,
			icon=data.get('icon') or self.icon
		)
		n.data = data
		n.width = self.tree.indent_start + \
						self.tree.indent_level * n.level \
						+ sum([i.width for i in n.children])
		if node:
			self.tree.add_node(n, node)
		else:
			self.tree.add_node(n)
		children = data.get('children')
		if not children:
			return
		for c in children:
			self.create_new_node(c, n)
		n.is_loaded = True
		
	def get_remote_data(self, node=None):
		if not self.url:
			return
		hc = HttpClient()
		params = self.params.copy() if self.params else {}
		if node:
			params['id'] = node.data[self.idField]
		print('params=', params)
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
			
class Menu(Hierarchy):
	target = StringProperty(None)
	def __init__(self, **kw):
		self.target_w = None
		super(Menu, self).__init__(**kw)

	def node_selected(self, o, v):
		if not v.is_leaf:
			self.tree.toggle_node(v)
			return
		super().node_selected(o, v)

	def on_press(self, node):
		self.tree.deselect_node()
		data = {}
		dw = node.data.get('datawidget')
		if dw:
			data_widget = Factory.Blocks.getWidgetById(dw)
			if data_widget:
				vn = node.data.get('datamethod', 'getValue')
				if hasattr(data_widget, vn):
					f = getattr(data_widget, vn)
					data = f()
					if not isinstance(data, dict):
						data = {}

		url = node.data.get('url')
		target = Factory.Blocks.getWidgetById(node.data.get('target',self.target),self)
		if url:
			params = node.data.get('params',{})
			params.update(data)
			blocks = Factory.Blocks()
			desc = {
				"widgettype":"urlwidget",
				"options":{
					"url":url,
					"params":params
				}
			}
			w = blocks.widgetBuild(desc)
			if w and target:
				target.add_widget(w)
			return 

		rfname = node.data.get('rfname')
		if rfname:
			f = getRegisterFunctionByName(rfname)
			if f:
				f(self, **data)
			return
		
		script = node.data.get('script')
		if script:
			target_name = node.data.get('target', self.target)
			target =  Factory.Blocks.getWidgetById(target_name, self)
			data.update({'self':target})
			if target:
				eval(script,data)
			return
		
Factory.register('Hierarchy', Hierarchy)
Factory.register('Menu', Menu)
