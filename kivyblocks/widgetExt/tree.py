"""
tree description json format:
{
	"url":a http(s) url for get data,
	"checkbox":boolean, show a checkbox before text
	"data":if undefined url,use data to construct the tree
	"params":parameters attached to the http(s) request  via url
	"headers":headers need to set for the http request via url
	"height":widget 's height
	"width":widget's width
}

data structure :
{
	"id":identified field,
	"widgettype":widget type,
	...other data...
	"__children__":[
	]
}
"""
from .scrollwidget import ScrollWidget
from kivy.uix.treeview import TreeView

