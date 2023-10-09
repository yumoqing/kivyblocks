import traceback

from kivy.app import App
from kivy.factory import Factory
from kivy.properties import ListProperty, BooleanProperty
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.graphics import Color, Rectangle, Triangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.uix.widget import Widget
from kivy.uix.button import ButtonBehavior
from kivyblocks.widgetExt import ScrollWidget
from kivyblocks.utils import CSize
from appPublic.dictObject import DictObject
from appPublic.jsonConfig import getConfig
from appPublic.registerfunction import getRegisterFunctionByName
from .baseWidget import PressableLabel, Text, HBox, VBox
from .color_definitions import getColors
from .widget_css import WidgetCSS
from .utils import alert,absurl, SUPER
from .toggleitems import PressableBox
from .threadcall import HttpClient

class EmptyBox(Label):
	def __init__(self,size_cnt=1):
		self.size_cnt = size_cnt
		siz=CSize(self.size_cnt)
		super().__init__(text='  ',font_size=siz,
				text_size=(siz,siz),
				halign='center',
				size_hint=[None,None],size=[siz,siz])

	def onSize(self,o=None,v=None):
		return

class NodeTrigger(ButtonBehavior, EmptyBox):
	open_status = BooleanProperty(False)
	color = ListProperty([1,0,0,1])
	def __init__(self, **kw):
		self.open_points = None
		self.close_points = None
		SUPER(NodeTrigger, self, kw)
		self.countPoints()
		self.bind(size=self.onSize,pos=self.onSize)

	def countPoints(self):
		self.open_points = [0,self.height, 
				self.width,self.height,
				self.width/2,0]
		self.close_points = [0,self.height, 
				0,0, self.width,

				self.height/2]
	def pointsShift(self,points):
		x = [ p + self.pos[0] if i % 2 == 0 else p + self.pos[1] \
				for i,p in enumerate(points) ]
		return x

	def onSize(self,o=None,v=None):
		self.countPoints()
		self.showOpenStatus()
	
	def on_press(self, *args):
		self.open_status = False if self.open_status else True

	def on_open_status(self, *largs):
		self.showOpenStatus()

	def on_color(self, *largs):
		self.showOpenStatus()

	def showOpenStatus(self):
		if self.close_points is None:
			return
		points = self.close_points
		if self.open_status:
			points = self.open_points
		self.canvas.clear()
		points = self.pointsShift(points)
		with self.canvas:
			Color(*self.color)
			Triangle(points=points)

class TreeNode(BoxLayout):
	def __init__(self,data,tree=None,
						parentNode=None
						):
		"""
		base TreeNode
		data:{
			if children miss, it is a leaf node,if children is a empty array, is mean need load at it is first expanded.
			}
		"""
		super(TreeNode, self).__init__(orientation='vertical',size_hint_y=None)
		self.treeObj = tree
		self.parentNode = parentNode
		self.node_level = 0
		if self.parentNode:
			self.node_level = self.parentNode.node_level + 1
		self.data = data
		self.content = None
		self.children_open = False
		self.nodes = []
		self.initChildren = False
		self.node_box = HBox(spacing=CSize(0.5),
							csscls=self.treeObj.normal_css,
							size_hint_y=None)
		self.node_box1 = BoxLayout(orientation='horizontal')
		n = data.get('children')
		self.hasChildren_nodes = True if not n is None else False
		self.children_nodes = n
		self.children_loaded = False
		self.hasChildren_nodes = data.get('children')
		if self.hasChildren_nodes:
			self.trigger = NodeTrigger(color=self.node_box.fgcolor)
			self.trigger.bind(on_press=self.toggleChildren)
			self.buildChildrenContainer()
		else:
			self.trigger = EmptyBox()
		self.node_box.add_widget(self.trigger)
		self.add_widget(self.node_box)
		self.addContent()
		self.setSize()

	def sibling(self):
		if self.parentNode is None:
			return [ i for i in self.treeObj.nodes if i != self ]
		return [ i for i in self.parentNode.nodes if i != self ]

	def selected(self):
		self.content.selected()

	def unselected(self):
		self.content.unselected()

	def setSize(self):
		if self.children_open:
			self.height = self.node_box.height + self.node_box1.height
		else:
			self.height = self.node_box.height
		self._trigger_layout()
		if self.parentNode:
			self.parentNode._trigger_layout()
		else:
			self.treeObj._inner._trigger_layout()
		
	def buildChildrenContainer(self):
		self.node_box1.add_widget(EmptyBox())
		self.children_box = BoxLayout(orientation='vertical')
		self.node_box1.add_widget(self.children_box)
		
	def setMinWidth(self,width):
		if self.node_box.width < width:
			self.node_box.width = width
		if self.node_box1.width < width:
			self.node_box1.width = width
		for n in self.nodes:
			n.setMinWidth(width)

	def buildContent(self):
		pass

	def addContent(self):
		self.buildContent()
		self.node_box.add_widget(self.content)
		self.node_box.height = self.treeObj.rowheight
		self.node_box.width = self.trigger.width + \
						self.content.width

	def buildChildren(self):
		if self.initChildren == True:
			return

		if self.data.children is None:
			return

		if self.data.children == []:
			self.treeObj.getUrlData(self.addChildren,self.data)
			return
		if len(self.nodes) == 0:
			self.addChildren(self.data.children)
		else:
			Logger.info('Tree : not need add subnodes')
		self.initChildren = True

	def childrenSizeChange(self,tn,v):
		h = 0
		w = 0
		for n in self.nodes:
			h += n.height
			w = max(w,n.width)

		self.children_box.height = h
		self.children_box.width = w
		self.node_box1.height = self.children_box.height
		self.node_box1.width = self.trigger.width + self.children_box.width
		self.setSize()

	def addChildren(self,children):
		self.data.children = children
		self.children_box.height = 0
		self.children_box.width = 0
		for c in children:
			options = {}
			options['tree'] = self.treeObj
			options['parentNode'] = self
			options['data'] = c
			tn = self.treeObj.NodeKlass(**options)
			tn.bind(size=self.childrenSizeChange)
			self.nodes.append(tn)
			self.children_box.add_widget(tn)
			self.children_box.height += tn.height
			self.children_box.width = max(self.children_box.width,tn.width)
			self.node_box1.height = self.children_box.height
			self.node_box1.width = self.trigger.width + self.children_box.width

	def addNodeByData(self,data):
		options = {}
		options['tree'] = self.treeObj
		options['parentNode'] = self
		if isinstance(data,dict):
			options['data'] = DictObject(**data)
		else:
			options['data'] = data
		w = self.treeObj.NodeKlass(**options)
		self.nodes.append(w)
		self.children_box.add_widget(w)
		self.childrenSizeChange(None,None)
		
	def addNode(self,node):
		node.parentNode = self
		self.nodes.append(node)
		self.children_box.add_widget(node)
		self.childrenSizeChange(None,None)

	def deleteNode(self,node):
		self.children_box.remove_widget(node)
		self.nodes = [ i for i in self.nodes if i != node ]
		self.childrenSizeChange(None,None)

	def delete(self):
		parentNode = self.parentNode if self.parentNode else self.treeObj
		parentNode.deleteNode(self)

	def expand(self):
		if self.treeObj.single_expand:
			if self.parentNode:
				self.parentNode.collapseall()
			else:
				self.treeObj.collapseall()
		if self.children_open:
			return
		self.toggleChildren(None)

	def collapse(self):
		if not self.children_open:
			return
		self.toggleChildren(None)

	def expandall(self):
		if not self.children_open:
			self.toggleChildren(None)
		for n in self.nodes:
			n.expandall()

	def collapseall(self):
		if self.children_open:
			self.toggleChildren(None)
		for n in self.nodes:
			n.collapseall(None)

	def moveNode(self,node,newParent=None):
		old_parent = node.parent
		if old_parent == None:
			old_parent = node.treeObj
		old_parent.deleteNode(node)
		if newParent == None:
			newParent = node.treeObj
		newParent.addNode(node)

	def toggleChildren(self,o):
		# self.treeObj.unselect_row()
		self.children_open = True if not self.children_open else False
		if self.children_open:
			self.buildChildren()
			self.add_widget(self.node_box1)
		else:
			self.remove_widget(self.node_box1)
		self.setSize()
		# when a widget remove from its parent, the get_parent_window()
		# will return a None
		# w1 = self.children_box.get_parent_window()
		# Logger.info('Tree :get_parent_window() return=%s',str(type(w1)))
	
"""
tree options
{
	"url":
	"params",
	"normal_css",
	"selected_css",
	"single_expand",
	"select_leaf_only",
	"bgcolor",
	"checkbox",
	"multplecheck",
	"idField",
	"textFiled",
	"data" # array of {children:{},...}
}
"""
class Tree(WidgetCSS, ScrollWidget):
	data = ListProperty([])
	def __init__(self,
			url=None,
			params={},
			single_expand=False,
			select_leaf_only=True,
			bgcolor=[0.2,0.2,0.2,1],
			normal_css="default",
			row_height=2,
			selected_css="selected",
			checkbox=False,
			multiplecheck=False,
			idField='id',
			textField='text',
			data=None,
			**options):
		self.url = url
		self.params = params
		self.data = data
		self.single_expand=single_expand
		self.select_leaf_only=select_leaf_only
		self.row_height=row_height
		self.rowheight = CSize(self.row_height)
		self.bgcolor = bgcolor
		self.normal_css = normal_css
		self.selected_css = selected_css
		self.checkbox = checkbox
		self.multiplecheck = multiplecheck
		self.idField = idField
		self.textField = textField
		print('options=',options)
		super(Tree, self).__init__(**options)
		self.options = DictObject(**options)
		self.nodes = []
		self.initflag = False
		self.selected_node = None
		self.buildTree()
		self.bind(size=self.onSize,pos=self.onSize)
		self.register_event_type('on_press')

	def on_press(self,*larg):
		pass

	def select_row(self, node):
		if node.hasChildren_nodes and self.select_leaf_only:
			node.toggleChildren(node)
			node.trigger.on_press()
			if node.children_open and self.single_expand:
				for n in node.sibling():
					if n.hasChildren_nodes and n.children_open:
						n.collapse()
			return
		self.unselect_row()
		self.selected_node = node
		node.selected()
		self.dispatch('on_press', node)

	def unselect_row(self):
		if self.selected_node:
			self.selected_node.unselected()
			self.selected_node = None
		
	def onSize(self,o,v=None):
		for n in self.nodes:
			n.setMinWidth(self.width)

	def setNodeKlass(self,klass):
		self.NodeKlass = klass

	def getUrlData(self,kv=None):
		hc = HttpClient()
		params = self.params.copy()
		if kv:
			for k,v in kv.items():
				if k in params.keys():	
					params[k] = v
			params['id'] = kv[self.idField]
		config = getConfig()
		app = App.get_running_app()
		url = app.absurl(self.url)
		hc.get(url,params=params,
					callback=self.dataLoaded,
					errback=self.showError)

	def showError(self,o,e):
		traceback.print_exc()
		alert(e,title='error')

	def on_data(self, *largs):
		self.addNodes()

	def buildTree(self,kv=None):
		if not hasattr(self,'NodeKlass'):
			self.NodeKlass = TreeNode

		if self.url:
			return self.getUrlData(kv)
		if len(self.data) > 0:
			self.addNodes()

	def dataLoaded(self, o, d):
		self.data = d

	def addNodes(self):
		for c in self.data:
			self.addNode(c)

	def addNode(self,data,parentNode=None):
		options = {}
		options['tree'] = self
		options['parentNode'] = None
		options['data'] = DictObject(**data)
		w = self.NodeKlass(**options)
		self.nodes.append(w)
		self.add_widget(w)
		
	def deleteNode(self,node):
		if self.selected_node == node:
			self.selected_node = None
		self.remove_widget(node)
		self.nodes = [ i for i in self.nodes if i != node ]

	def collapseall(self):
		for n in self.nodes:
			n.collapse()

	def expandall(self):
		for n in self.nodes:
			n.expand()

class TextContent(PressableLabel):
	def __init__(self,**options):
		PressableLabel.__init__(self,**options)

class TextTreeNode(TreeNode):
	def buildContent(self):
		txt = self.data.get(self.treeObj.textField,
				self.data.get(self.treeObj.idField,'defaulttext'))
		self.content = TextContent(csscls=self.treeObj.normal_css,
							text=txt,
							size_hint_y=None,
							font_size=CSize(1),
							text_size=CSize(len(txt)-1,1),
							halign='left',
							height=CSize(2))
		self.content.bind(on_press=self.onPress)
		return 
	
	def onPress(self,o,v=None):
		self.treeObj.select_row(self)

	def selected(self):
		if hasattr(self.content,'selected'):
			self.content.selected()

	def unselected(self):
		if hasattr(self.content,'unselected'):
			self.content.unselected()

class TextTree(Tree):
	def __init__(self,nodeklass=TextTreeNode,**options):
		self.NodeKlass = nodeklass
		super().__init__(**options)

class MenuTreeNode(TextTreeNode):
	def on_size(self, *args):
		self.node_box.width = self.width
		self.content.width = self.node_box.width - self.trigger.width
		self.text_widget.width = self.content.width - CSize(1)

	def selected(self):
		self.content.active(True)

	def unselected(self):
		self.content.active(False)

	def buildContent(self):
		txt = self.data.get(self.treeObj.textField,
				self.data.get(self.treeObj.idField,'defaulttext'))
		icon = self.data.get('icon')
		self.content = PressableBox(normal_css=self.treeObj.normal_css,
				actived_css=self.treeObj.selected_css,
				size_hint_y=None,
				height=self.treeObj.rowheight
		)
		self.content.orientation = 'horizontal'
		if icon:
			img = AsyncImage(source=icon,
							size_hint=(None,None),
							height=CSize(1),
							width=CSize(1))
		else:
			img = EmptyBox()
		
		self.content.add_widget(img)
		textw = Text( text=txt,
							size_hint=(None,None),
							font_size=CSize(1),
							text_size=CSize(len(txt)-1,1),
							halign='left',
							wrap=True,
							height=CSize(2),
							width=self.width)
		self.content.add_widget(textw)
		self.text_widget = textw
		self.content.bind(on_press=self.onPress)
		return 
	

"""
{
	...
	target:kkk,
	data:[
		{
			id:
			text:
			icon:
			url:
			rfname
			children
		}
	]
}
"""
class MenuTree(TextTree):
	def __init__(self, target=None, **kw):
		self.target = target
		super().__init__(nodeklass=MenuTreeNode, **kw)

	def select_row(self, node):
		super().select_row(node)
		if not node.hasChildren_nodes:
			self.menucall(node)
		
	def menucall(self, node):
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
			print('menucall(), params=', params)
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
		


class PopupMenu(BoxLayout):
	def __init__(self,target,menudesc,**opts):
		self.target = target
		self.menudesc = menudesc
		BoxLayout.__init__(self, size_hint=(0.5,0.5), **opts)
		self.menu_tree = TextTree(**menudesc)
		self.add_widget(self.menu_tree)
		self.menu_tree.bind(on_press=self.onMenuItemTouch)
		self.register_event_type('on_press')

	def on_press(self,o,v=None):
		pass

	def onMenuItemTouch(self,o,d=None,v=None):
		data = {
			'target':self.treeObj.target,
			'menudata':d
		}
		self.dispatch('on_press',data)
		self.dismiss()

	def open(self):
		Window.add_widget(self)
		self.center = Window.center

	def dismiss(self):
		Window.remove_widget(self)

	def on_touch_down(self,touch):
		if not self.collide_point(*touch.pos):
			self.dismiss()
			return False
		super().on_touch_down(touch)
		return True
