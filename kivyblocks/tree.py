import traceback

from kivy.app import App
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.graphics import Color, Rectangle, Triangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import ButtonBehavior
from kivyblocks.widgetExt import ScrollWidget
from kivyblocks.utils import CSize
from appPublic.dictObject import DictObject
from appPublic.jsonConfig import getConfig
from .baseWidget import PressableLabel
from .color_definitions import getColors
from .bgcolorbehavior import BGColorBehavior
from .utils import alert,absurl

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
	def __init__(self, size_cnt=1,open_status=False,color=[1,0,0,1]):
		super().__init__(size_cnt=size_cnt)
		self.open_status = open_status
		self.line_color = color
		self.countPoints()
		self.showOpenStatus()
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
	
	def on_press(self):
		self.open_status = False if self.open_status else True
		self.showOpenStatus()

	def showOpenStatus(self):
		points = self.close_points
		if self.open_status:
			points = self.open_points
		self.canvas.clear()
		points = self.pointsShift(points)
		with self.canvas:
			Color(*self.line_color)
			Triangle(points=points)
		# print('pos=',self.pos,'size=',self.size)

class TreeNode(BoxLayout):
	def __init__(self,data,tree=None,
						parentNode=None,
						):
		"""
		base TreeNode
		data:{
			if children miss, it is a leaf node,if children is a empty array, is mean need load at it is first expanded.
			}
		"""
		BoxLayout.__init__(self,orientation='vertical',size_hint=(None,None))
		self.treeObj = tree
		self.parentNode = parentNode
		self.data = data
		self.content = None
		self.children_open = False
		self.nodes = []
		self.initChildren = False
		self.node_box = BoxLayout(orientation='horizontal',
							spacing=CSize(0.5),
							size_hint_y=None)
		self.node_box1 = BoxLayout(orientation='horizontal')
		n = data.get('children')
		self.hasChildren_nodes = True if not n is None else False
		self.children_nodes = n
		self.children_loaded = False
		self.hasChildren_nodes = data.get('children')
		if self.hasChildren_nodes:
			self.trigger = NodeTrigger()
			self.trigger.bind(on_press=self.toggleChildren)
			self.buildChildrenContainer()
		else:
			self.trigger = EmptyBox()
		self.node_box.add_widget(self.trigger)
		self.add_widget(self.node_box)
		self.addContent()
		self.setSize()

	def setSize(self):
		if self.children_open:
			self.height = self.node_box.height + self.node_box1.height
		else:
			self.height = self.node_box.height
		self.width = self.node_box.width
		self._trigger_layout()
		if self.parentNode:
			self.parentNode._trigger_layout()
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
		self.node_box.height = self.content.height
		self.node_box.width = self.trigger.width + \
						self.content.width
		Logger.info('Tree : content=(%d,%d),box=(%d,%d)', \
						self.content.width,self.content.height,
						self.node_box.width,self.node_box.height)

	def buildChildren(self):
		if self.initChildren == True:
			return

		if self.data.children is None:
			Logger.info('Tree : is a leaf node')
			return

		if self.data.children == []:
			self.treeObj.getUrlData(self.addChildren,self.data)
			return
		if len(self.nodes) == 0:
			Logger.info('Tree : add subnodes')
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
		self.treeObj.unselect_row()
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
	"color_level",
	"checkbox",
	"multplecheck",
	"idField",
	"textFiled",
	"data" # array of {children:{},...}
}
"""
class Tree(BGColorBehavior, ScrollWidget):
	def __init__(self,**options):
		self.color_level = options.get('color_level',0)
		ScrollWidget.__init__(self)
		BGColorBehavior.__init__(self,color_level=self.color_level)
		self.options = DictObject(**options)
		self.nodes = []
		self.initflag = False
		self.selected_node = None
		self.bind(size=self.onSize,pos=self.onSize)

	def select_row(self, node):
		self.unselect_row()
		self.selected_node = node
		node.selected()

	def unselect_row(self):
		if self.selected_node:
			Logger.info('selected node unselected')
			self.selected_node.unselected()
			self.selected_node = None
		
	def onSize(self,o,v=None):
		if not self.initflag:
			self.initflag = True
			self.buildTree()
		for n in self.nodes:
			n.setMinWidth(self.width)

	def setNodeKlass(self,klass):
		self.NodeKlass = klass

	def getUrlData(self,callback,kv=None):
		hc = App.get_running_app().hc
		params = self.options.get('params',{}).copy()
		if not kv is None:
			for k,v in kv.items():
				if k in params.keys():	
					params[k] = v
			params['id'] = kv[self.options.idField]
		config = getConfig()
		url = absurl(self.options.url,None)
		Logger.info('Tree: getUrlData(),url=%s',url)
		hc.get(url,params=params,
					callback=callback,
					errback=self.showError)

	def showError(self,o,e):
		traceback.print_exc()
		Logger.info('Tree: showError() o=%s,e=%s',o,e)
		alert(e,title='error')

	def buildTree(self,kv=None):
		if not hasattr(self,'NodeKlass'):
			self.NodeKlass = TreeNode

		if self.options.url:
			return self.getUrlData(self.dataLoaded,kv)
		data = self.options.data or []
		Logger.info("Tree : buildTree,data=%s",data)
		self.dataLoaded(None,data)
		self.color, self.bgcolor = getColors(self.color_level)

	def dataLoaded(self,o,d):
		Logger.info("Tree: dataLoaded,d=%s",d)
		self.data = d
		self.addNodes()

	def addNodes(self):
		Logger.info("Tree: addNodes()")
		for c in self.data:
			options = {}
			options['tree'] = self
			options['parentNode'] = None
			options['data'] = DictObject(**c)
			w = self.NodeKlass(**options)
			self.nodes.append(w)
			self.add_widget(w)
			Logger.info('Tree : node=%s',type(w))

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

class TextContent(PressableLabel):
	def __init__(self,color_level=0,**options):
		PressableLabel.__init__(self,color_level=color_level,**options)
		

class TextTreeNode(TreeNode):
	def buildContent(self):
		txt = self.data.get(self.treeObj.options.textField,
				self.data.get(self.treeObj.options.idField,'defaulttext'))
		self.content = TextContent(color_level=self.treeObj.color_level,
							text=txt,
							size_hint=(None,None),
							font_size=CSize(1),
							text_size=CSize(len(txt)-1,1),
							halign='left',
							height=CSize(2),
							width=CSize(len(txt)))
		self.content.color, self.content.bgcolor = getColors(self.treeObj.color_level,
					selected=False)
		self.content.bind(on_press=self.onPress)
		return 
	
	def onPress(self,o,v=None):
		if self.hasChildren_nodes:
			self.toggleChildren(self)
			self.trigger.on_press()
			return
		Logger.info('select the leaf node')
		self.treeObj.select_row(self)

	def selected(self):
		if hasattr(self.content,'selected'):
			self.content.selected()

	def unselected(self):
		if hasattr(self.content,'unselected'):
			self.content.unselected()

class TextTree(Tree):
	def __init__(self,**options):
		self.NodeKlass = TextTreeNode
		super().__init__(**options)
		self.register_event_type('on_press')

	def select_row(self, node):
		super().select_row(node)
		self.dispatch('on_press',node.data)

	def on_press(self,o,v=None):
		print('TextTree():on_press(),o=',o,'v=',v)

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
		Logger.info('PopupMenu: on_press fired')

	def onMenuItemTouch(self,o,d=None,v=None):
		Logger.info('MenuTree: on_press fired,o=%s,d=%s,v=%s',o,d,v)
		data = {
			'target':self.target,
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
