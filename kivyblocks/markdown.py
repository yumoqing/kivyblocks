from kivy.properties import StringProperty
from kivy.factory import Factory
from kivy.clock import Clock

from .baseWidget import ScrollWidget,  getDataHandler
from .utils import CSize
import re

class Markdown(ScrollWidget):
	"""
# Markdown
MArkdown widget using to render a markdown file and show it
description file format
{
	"widgettype":"Markdown",
	"options":{
		"source": the markdown file
		other options
	}
}
	"""
	source = StringProperty(None)
	def __init__(self, **kw):
		ScrollWidget.__init__(self, **kw)
		self.bind(source=self.load_text)
		if self.source:
			Clock.schedule_once(self.load_text, 0.3)
		self.bind(size=self.setChildMinWidth)

	def setChildMinWidth(self, *args):
		print('size changed')
		for i,c in enumerate(self._inner.children):
			c.width = self.width

	def load_text(self, *args):
		print('source fired, hahaha', *args)
		self.clear_widgets()
		h =  getDataHandler(self.source)
		h.bind(on_success=self.update)
		h.bind(on_error=self.show_error)
		h.handle()

	def show_error(self, o, e):
		print('load_text(), error=',e)

	def update(self, o, text):
		print('text=',text, type(text))
		text = ''.join(text.split('\r'))
		"""
		org_boxs = re.findall(r"\n```\n(.*)\n```\n", text)
		org_boxs_widget = [ \
				Factory.Blocks().widgetBuild({ \
						"widgettype":f"Title{level}", \
						"options":{ \
							"text":txt, \
							"size_hint_x":None, \
							"width":self.width, \
							"size_hint_y":None, \
							"markup":True, \
							"bgcolor":self.options.source_bgcolor, \
							"wrap":True, \
							"halign":"left", \
							"valign":"middle" \
						} \
					}) for t in org_boxs ]
		other_texts = re.split(r"\n```\n(.*)\n```\n", text)
		"""
		if not text:
			return
		for l in text.split('\n'):
			self.parse_line(l)

	def parse_title(self, txt, level):
		w = Factory.Blocks().widgetBuild({
			"widgettype":f"Title{level}",
			"options":{
				"text":txt,
				"size_hint_x":None,
				"width":self.width,
				"size_hint_y":None,
				"markup":True,
				"wrap":True,
				"halign":"left",
				"valign":"middle"
			}
		})
		if not w:
			return
		w1,h1 = w.get_wraped_size()
		clen = CSize(1)
		if h1 is None or h1 < clen:
			h1 = clen
		w.height = h1
		print(w, w1, h1, w.height)
		w.bind(on_ref_press=self.open_new_md)
		self.add_widget(w)
		
	def parse_line(self, l):
		if l.startswith('###### '):
			t = self.mktext_bbtext(l[7:])
			return self.parse_title(t,6)
		if l.startswith('##### '):
			t = self.mktext2bbtext(l[6:])
			return self.parse_title(t,5)
		if l.startswith('#### '):
			t = self.mktext2bbtext(l[5:])
			return self.parse_title(t,4)
		if l.startswith('### '):
			t = self.mktext2bbtext(l[4:])
			return self.parse_title(t,3)
		if l.startswith('## '):
			t = self.mktext2bbtext(l[3:])
			return self.parse_title(t,2)
		if l.startswith('# '):
			t = self.mktext2bbtext(l[2:])
			return self.parse_title(t,1)
		t = self.mktext2bbtext(l)
		w = Factory.Blocks().widgetBuild({
			"widgettype":"Text",
			"options":{
				"text":t,
				"wrap":True,
				"size_hint_x":None,
				"width":self.width,
				"markup":True,
				"valign":"middle",
				"halign":"left"
			}
		})
		if not w:
			return
		_,h = w.get_wraped_size()
		clen = CSize(1)
		if h is None or h < clen:
			h = clen
		w.height = h
		w.bind(on_ref_press=self.open_new_md)
		self.add_widget(w)

	def open_new_md(self, o, value):
		print(value,'is it a link')
		self.source = value

	def mktext2bbtext(self,mdtext):
		"""
		convert markdown text to bbtag text kivy Label Widget recognized

		markdown syntax
		*XXX*		Italic
		**XXX**		Bold
		***XXX***	Bold + Italic
		> XXXX		reference
		>> XXXX		reference inside reference
		[-*] XXX	list
		[0-9]*[.] XXX	list
		***			split line
		---			split line
		___			split line
		[.*](url)	link
		![.*](url)	image
		[![.*](url)](url)		image link
		!v[.*](url)	video*		plan to extend
		!a[.*](url) audio*		plan to extend

		bb tag syntax
		[b]XXX[/b]	Bold
		[i]XXX[/i]	Italic
		[sub]XXX[/sub]
		"""
		mdtext = re.sub('\*\*\*(.*)\*\*\*', \
					lambda x: '[b][i]'+x.group(1)+'[/i][/b]', \
					mdtext)

		mdtext = re.sub('\*\*(.*)\*\*', \
					lambda x: '[b]'+x.group(1)+'[/b]', \
					mdtext)

		mdtext = re.sub('\*(.*)\*', \
					lambda x: '[i]'+x.group(1)+'[/i]', \
					mdtext)

		mdtext = re.sub('([^!]?)\[(.*)\]\((.*)\)', \
					lambda x:x.group(1) + '[ref='+x.group(3)+'][color=00ff00]'+ x.group(2)+'[/color][/ref]', \
					mdtext)

		return mdtext
