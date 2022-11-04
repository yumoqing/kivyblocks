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
from .command_action import cmd_action

from appPublic.registerfunction import getRegisterFunctionByName

class TreeViewComplexNode(BoxLayout, TreeViewNode):
	otext = StringProperty(None)
	font_size_c = NumericProperty(1)
	node_height = NumericProperty(2)
	checkbox = BooleanProperty(False)
	icon = StringProperty(None)
	data = DictProperty(None)
	def __init__(self, **kw):
		super(TreeViewComplexNode, self).__init__(**kw)
		self.orientation = 'horizontal'
		if self.checkbox:
			cb = SingleCheckBox(size_hint=(None,None))
			cb.bind(on_press=self.set_checked)
			self.add_widget(cb)
		if self.icon:
			img = AsyncImage(source=self.icon, size_hint=(None,None))
			img.size = CSize(self.font_size_c,self.font_size_c)
			self.add_widget(img)
		txt = Text(otext=self.otext, i18n=True, wrap=True,
				font_size=CSize(self.font_size_c),halign='left')
		self.add_widget(txt)
		self.size_hint_x = 1
		self.size_hint_y = None
		self.height = CSize(self.node_height)
		
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
	node_height = NumericProperty(2)
	font_size_c = NumericProperty(1)
	textField = StringProperty(None)
	data = ListProperty(None)
	checkbox = BooleanProperty(False)
	icon = StringProperty(None)
	single_expand = BooleanProperty(False)
	def __init__(self, **kw):
		self.register_event_type('on_press')
		self.tree = TreeView(hide_root=True)
		self.tree.size_hint = (1, None)
		self.tree.bind(on_node_expand=self.check_load_subnodes)
		self.tree.bind(selected_node=self.node_selected)
		super(Hierarchy, self).__init__(inner=self.tree, **kw)
		if self.url:
			self.data = self.get_remote_data()

	def on_size(self, *args):
		self.tree.size_hint_x = 1
		self.tree.width = self.width

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
			node_height=self.node_height,
			font_size_c=self.font_size_c,
			icon=data.get('icon') or self.icon
		)
		n.data = data
		# n.width = self.tree.indent_start + \
		#				self.tree.indent_level * n.level \
		#				+ sum([i.width for i in n.children])
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
		data = node.data.copy()
		if self.target and data.get('target') is None:
			data['target'] = self.target
		return cmd_action(data, self)
		
Factory.register('Hierarchy', Hierarchy)
Factory.register('Menu', Menu)
