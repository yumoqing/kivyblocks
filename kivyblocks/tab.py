"""
{
	"widgettype":"BLKTabbedPanel",
	"tab_pos":"top_left",
	"color_level":0,
	"width",
	"height",
	"size_hint",
	"tabs":[
		{
			"text":"tab1",
			"content":{
				"widgettype":"urlwidegt",
				"url":"reggtY",
			}
		},
		{
		}
	]
}
"""

class BLKTabItem(BGColorBehavior, TabbedPanelItem):
	def __init__(self,parent,color_level=0,text="",content={}):
		self.parent=parent
		self.color_level = color_level

class BLKTabedPanel(BGColorBehavior, TabbedPanel):
	def __init__(self,color_level=0, tabs=[], **kwargs):
		self.tabs_desc = tabs
		self.color_level = color_level
		TabbedPanel.__init__(**kwargs)
		BGColorBehavior.__init__(self)

class 
