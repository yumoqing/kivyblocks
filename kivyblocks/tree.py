from kivy.app import App
from kivy.logger import logging
from kivy.graphics import Color, Rectangle, Triangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import ButtonBehavior
from kivyblocks.widgetExt import ScrollWidget
from kivyblocks.utils import CSize
from appPublic.dictObject import DictObject
from .baseWidget import PressableLabel
from .stylebehavior import StyleBehavior

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
		super().__init__(orientation='vertical',size_hint=(None,None))
		self.treeObj = tree
		self.data = data
		self.parentNonde = parentNode
		self.content = None
		self.children_open = False
		self.subNodes = []
		self.node_box = BoxLayout(orientation='horizontal',size_hint_y=None)
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
		self.width = self.trigger.width + \
					max(self.node_box.width,self.node_box1.width)
		
	def buildChildrenContainer(self):
		self.node_box1.add_widget(EmptyBox())
		self.children_box = BoxLayout(orientation='vertical')
		self.node_box1.add_widget(self.children_box)
		
	def setMinWidth(self,width):
		if self.node_box.width < width:
			self.node_box.width = width
		if self.node_box1.width < width:
			self.node_box1.width = width
		for n in self.subNodes:
			n.setMinWidth(width)

	def buildContent(self):
		pass

	def addContent(self):
		self.buildContent()
		self.node_box.add_widget(self.content)
		self.node_box.height = self.content.height + CSize(1)
		self.node_box.width = self.trigger.width + \
						self.content.width + CSize(1)
		logging.info('Tree : content=(%d,%d),box=(%d,%d)', \
						self.content.width,self.content.height,
						self.node_box.width,self.node_box.height)

	def buildChildren(self):
		if self.data.children is None:
			logging.info('Tree : is a leaf node')
			return

		if self.data.children == []:
			self.treeObj.getUrlData(self.addChildren,self.data)
			return
		if len(self.subNodes) == 0:
			logging.info('Tree : add subnodes')
			self.addChildren(self.data.children)
		else:
			logging.info('Tree : not need add subnodes')

	def childrenSizeChange(self,tn,v):
		h = 0
		w = 0
		for n in self.subNodes:
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
			self.subNodes.append(tn)
			self.children_box.add_widget(tn)
			self.children_box.height += tn.height
			self.children_box.width = max(self.children_box.width,tn.width)
			self.node_box1.height = self.children_box.height
			self.node_box1.width = self.trigger.width + self.children_box.width

	def toggleChildren(self,o):
		self.treeObj.unselected()
		self.children_open = True if not self.children_open else False
		if self.children_open:
			self.buildChildren()
			self.add_widget(self.node_box1)
		else:
			self.remove_widget(self.node_box1)
		self.setSize()
	
"""
tree options
{
	"url":
	"params",
	"bg_color",
	"color",
	"checkbox",
	"multplecheck",
	"idField",
	"textFiled",
	"data" # array of {children:{},...}
}
"""
class Tree(StyleBehavior,ScrollWidget):
	def __init__(self,**options):
		ScrollWidget.__init__(self)
		level = options.get('level',0)
		StyleBehavior.__init__(self,level=level)
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
			logging.info('selected node unselected')
			self.selected_node.unselected()
			self.selected_node = None
		
	def onSize(self,o,v=None):
		if not self.initflag:
			self.initflag = True
			self.buildTree(self)
		for n in self.nodes:
			n.setMinWidth(self.width)

	def setNodeKlass(self,klass):
		self.NodeKlass = klass

	def getUrlData(self,callback,kv=None):
		hc = App.get_running_app().hc
		params = self.options.get(params,{}).copy()
		if not data is None:
			for k,v in kv:
				if k in params.keys():	
					params[k] = v
			params['id'] = kv[self.options.idField]
		hc.get(self.url,params=params,callback=callback)

	def buildTree(self,kv=None):
		if not hasattr(self,'NodeKlass'):
			self.NodeKlass = TreeNode

		if self.options.url:
			return self.getUrlData(self.dataLoaded,kv)
		data = self.options.data
		logging.info("Tree : buildTree,data=%s",data)
		self.dataLoaded(data)


	def dataLoaded(self,d):
		self.data = d
		self.addNodes()

	def addNodes(self):
		for c in self.data:
			options = {}
			options['tree'] = self
			options['parentNode'] = None
			options['data'] = DictObject(**c)
			w = self.NodeKlass(**options)
			self.nodes.append(w)
			self.add_widget(w)
			logging.info('Tree : node=%s',type(w))

class TextContent(StyleBehavior, PressableLabel):
	def __init__(self,level=0,**options):
		PressableLabel.__init__(self,**options)
		StyleBehavior.__init__(self,level=level)
		
class TextTreeNode(TreeNode):
	def buildContent(self):
		txt = self.data.get(self.treeObj.options.textField,
				self.data.get(self.treeObj.options.idField,'defaulttext'))
		self.content = TextContent(level=self.treeObj.style_level,
							text=txt,
							size_hint=(None,None),
							font_size=CSize(1),
							text_size=CSize(len(txt)-1,1),
							halign='left',
							height=CSize(2),
							width=CSize(len(txt)))
		self.content.text_color = [0,0,0,1] #self.treeObj.text_color
		self.content.bind(on_press=self.onPress)
		return 
	
	def onPress(self,o,v=None):
		if self.hasChildren_nodes:
			v = True if not self.children_open else False
			self.toggleChildren(self)
			self.trigger.on_press()
			return
		logging.info('select the leaf node')
		self.treeObj.select_row(self)

	def selected(self):
		logging.info('content selected ........')
		self.content.selected()

	def unselected(self):
		logging.info('content unselected ........')
		self.content.unselected()

class TextTree(Tree):
	def __init__(self,**options):
		self.NodeKlass = TextTreeNode
		super().__init__(**options)
		self.register_event_type('on_press')

		
	def onPress(self,o,v=None):
		if self.selectNode:
			self.selectNode.unselected()
		self.selectNode = o
		o.selected()
		self.dispatch(on_press,o,o.data)

	def on_press(self,o,v):
		print('TextTree():on_press(),o=',o,'v=',v)
