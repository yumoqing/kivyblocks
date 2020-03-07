from kivy.app import App
from kivy.graphics import Color, Triangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.button import ButtonBehavior

from kivyblocks.widgetExt import ScrollWidget
from kivyblocks.blocksapp import BlocksApp
from kivyblocks.utils import CSize
from baseWidget import PressableLabel

from appPublic.dictObject import DictObject

class NodeTrigger(ButtonBehavior, Widget):
	def __init__(self, open_status=False,color=[1,0,0,1]):
		siz = CSize(1)
		super().__init__(size_hint=(None,None),size=[siz,siz]) #CSize(1))
		self.open_status = open_status
		self.line_color = color
		self.register_event_type('on_change')
		self.open_points = [0,self.height, self.width,self.height,self.width/2,0]
		self.close_points = [0,self.height, 0,0, self.width,self.height/2]
		self.showOpenStatus()
		self.bind(size=self.on_size)

	def on_change(self,status):
		print('new_status=',status)

	def on_size(self,o,v):
		self.open_points = [0,self.height, self.width,self.height,self.width/2,0]
		self.close_points = [0,self.height, 0,0, self.width,self.height/2]
	
	def on_press(self):
		self.open_status = False if self.open_status else True
		self.showOpenStatus()
		self.dispatch('on_change',self.open_status)

	def showOpenStatus(self):
		points = self.close_points
		if self.open_status:
			points = self.open_points
		self.canvas.clear()
		with self.canvas:
			Color(*self.line_color)
			Triangle(points=points)

class EmptyBox(Widget):
	def __init__(self):
		siz=CSize(1)
		super().__init__(size_hint=[None,None],size=[siz,siz])


class TreeNode(BoxLayout):
	def __init__(self,tree:Tree=None,
						parentNode:TreeNode=None,
						data:dict):
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
		self.hasChildren = data.get('hasChildren')
		if hasChildren_nodes:
			self.trigger = NodeTrigger()
			self.trigger.bind(on_change=self.toggleChildren)
			self.buildChildrenContainer()
		else:
			self.trigger = EmptyBox()
		self.add_widget(self.node_box)
		self.node_box.add_widget(self.trigger)
		self.buildContent()

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
		self.node_box.width = self.trigger.width + self.content.width

	def buildChildren(self):
		if self.data.children is None:
			return

		if self.data.children == []:
			self.treeObj.getUrlData(self.addChildren,self.data)
			return
		if len(self.subNodes) == 0:
			self.addChildren(self.data.children)

	def addChildren(self,children):
		self.data.children = children
		for c in children:
			options['tree'] = self.treeObj
			options['parentNode'] = self
			options['data'] = c
			tn = self.teeeObj.NodeKlass(**options)
			self.subNodes.append(tn)
			self.children_box.add_widget(tn)

	def toggleChildren(self,o,v):
		if v:
			self.buildChildren()
			self.add_widget(self.node_box1)
			self.children_open = True
			self.height = self.node_box.height + self.node_box1.height
		else:
			self.remove_widget(self.node_box1)
			self.height = self.node_box.height
			self.children_open = False
	
	def on_size(self,o,v):
		print('************treenode on_size', o, v)
		self.node_box1.height = self.children_box.height

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
class Tree(ScrollWidget):
	def __init__(self,**options):
		super().__init__()		#orientation="vertical")
		self.options = DictObject(**options)
		self.nodes = []
		self.initflag = False
		self.bind(size=self.onSize,pos=self.onSize)

	def onSize(self,o,v=None):
		if not self.initflag:
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
		self.dataLoaded(data)

	def dataLoaded(self,d):
		self.data = d
		self.addNodes()

	def addNodes(self):
		for c in self.data:
			options = {}
			options['tree'] = self
			options['parentNode'] = None
			options['data'] = DictObject(c)
			self.nodes.append(self.NodeKlass(**options))
		for w in self.nodes:
			self.add_widget(w)

class TextTreeNode(TreeNode):
	def buildContent(self):
		txt = self.data.get(self.treeObj.options.textField,
				self.data.get(self.treeObj.options.idField,'defaulttext'))
		self.content = PressableLabel(text=txt,
							size_hint=(None,None),
							font_size=CSize(1),
							text_size=CSize(len(txt),1),
							halign='left',
							height=CSize(2),width=CSize(len(txt)))
		self.content.bind(on_press=self.onPress)
		return 
	
	def onPress(self,o,v=None):
		self.treeObj.select_row(self)

	def selected(self):
		pass

	def unselected(self):
		pass

class TextTree(Tree):
	def __init__(self,**options):
		self.NodeKlass = TextTReeNode
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
