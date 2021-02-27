from kivy.properties import StringProperty
from kivy.factory import Factory
from kivy.clock import Clock

from .baseWidget import ScrollWidget,  getDataHandler
from .utils import CSize
import re

SOURCE_DELIMITER = "\n```\n"
VIDEO_LEAD = "![@"
AUDIO_LEAD = "![#"
IMAGE_LEAD = "!["
LINK_LEAD = "["
REFER_SPLIT = "]("
REFER_END = ")"

class MarkDownParser(object):
	mdkeys = [
		SOURCE_DELIMITER,
		VIDEO_LEAD,
		AUDIO_LEAD,
		IMAGE_LEAD
	]
	def __init__(self, mdtext):
		self.mdtext = mdtext
		self.result = []
		self.text = ""
		self.mdkey_handler = {
			SOURCE_DELIMITER:self.handle_source_delimiter,
			VIDEO_LEAD:self.lead_video,
			AUDIO_LEAD:self.lead_audio,
			IMAGE_LEAD:self.lead_image,
		}

	def handle_source_delimiter(self,mdtext):
		x = self.mdtext.split(SOURCE_DELIMITER,1)
		mk_p = MarkDownParser(x[0])
		self.result += mk_p.parse()
		if len(x) > 1:
			self.mdtext = x[1]

	def lead_video(self):
		print('lead_video() ..., mdtext=', self.mdtext)
		x = self.mdtext.split(REFER_SPLIT,1)
		if len(x)<2:
			print('lead_video() return here', REFER_SPLIT, '---', self.mdtext)
			self.text = f'{VIDEO_LEAD}'
			return
		title = x[0]
		y = x[1].split(REFER_END,1)
		if len(y) < 2:
			print('lead_video() return here', REFER_END)
			self.text = f'{VIDEO_LEAD}'
			return
		url = y[0]
		self.mdtext = y[1]
		d = {
			"video":{
				"title":title,
				"url":url
			}
		}
		self.result.append(d)

	def lead_audio(self):
		x = self.mdtext.split(REFER_SPLIT,1)
		if len(x)<2:
			self.text = f'{VIDEO_LEAD}'
			return
		title = x[0]
		y = x[0].split(REFER_END,1)
		if len(y) < 2:
			self.text = f'{VIDEO_LEAD}'
			return
		url = y[0]
		d = {
			"audio":{
				"title":"title",
				"url":url
			}
		}
		self.result.append(d)
		l = len(title) + 2 + len(url)
		self.mdtext = self.mdtext[l:]

	def lead_image(self):
		x = self.mdtext.split(REFER_SPLIT,1)
		if len(x)<2:
			self.text = f'{VIDEO_LEAD}'
			return
		title = x[0]
		y = x[0].split(REFER_END,1)
		if len(y) < 2:
			self.text = f'{VIDEO_LEAD}'
			return
		url = y[0]
		d = {
			"image":{
				"title":"title",
				"url":url
			}
		}
		self.result.append(d)
		l = len(title) + 2 + len(url)
		self.mdtext = self.mdtext[l:]

	def check_key(self,t):
		for k in self.mdkeys:
			if t.startswith(k):
				return k
		return None

	def parse(self):
		"""
		parser parse mdtext, recognize bbtext, source, img, audio, video
		part text
		"""
		while len(self.mdtext) > 0:
			k = self.check_key(self.mdtext)
			if k is None:
				self.text = f'{self.text}{self.mdtext[0]}'
				self.mdtext = self.mdtext[1:]
			else:
				if len(self.text) > 0:
					self.result.append({'pure_md':self.text})
					self.text = ""
				self.mdtext = self.mdtext[len(k):]
				self.mdkey_handler[k]()
		if len(self.text) > 0:
			self.result.append({'pure_md':self.text})
			self.text = ''
		return self.result	

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
		self.part_handlers = {
			"pure_md":self.build_pure_md,
			"source":self.build_source,
			"image":self.build_image,
			"video":self.build_video,
			"audio":self.build_audio
		}
		ScrollWidget.__init__(self, **kw)
		self.bind(source=self.load_text)
		if self.source:
			Clock.schedule_once(self.load_text, 0.3)
		self.bind(size=self.setChildMinWidth)

	def build_source(self,source_desc):
		pass

	def build_pure_md(self, mdtext):
		for l in mdtext.split('\n'):
			self.parse_line(l)

	def build_image(self,img_desc):
		w = Factory.AsyncImage(soure=img_desc['url'],
					keep_ratio=True,
					size_hint_y=None
			)
		w.bind(minimum_height=w.setter('height'))
		self.add_widget(w)

	def build_video(self, video_desc):
		w = Factory.NewVideo(source=video_desc['url'],
				keep_ratio=True,
				play=True,
				allow_stretch = True,
				size_hint_y=None
		)
		w.height=self.width * 10 / 16
		self.add_widget(w)
		
	def build_audio(self, audio_desc):
		w = Factory.APlayer(source=audio_desc.url)
		w.bind(minimum_height=w.setter('height'))
		self.add_widget(w)

	def setChildMinWidth(self, *args):
		print('size changed')
		for i,c in enumerate(self._inner.children):
			c.width = self.width
			if hasattr(c, 'resize'):
				c.resize(self.size)

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
		if not text:
			return
		text = ''.join(text.split('\r'))
		mdp = MarkDownParser(text)
		parts = mdp.parse()
		for p in parts:
			for k,v in p.items():
				print('part=', k, v)
				f = self.part_handlers.get(k)
				f(v)


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
		w.bind(on_ref_press=self.open_new_md)
		# w.bind(minimum_height=w.setter('height'))
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
		# w.bind(minimum_height=w.setter('height'))
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
