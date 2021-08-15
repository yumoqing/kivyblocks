from kivy.properties import StringProperty, NumericProperty, ListProperty
from kivy.factory import Factory
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage

from .baseWidget import ScrollWidget,  getDataHandler, VBox

from .utils import CSize
import re

SOURCE_DELIMITER = "\n```\n"
VIDEO_LEAD = "![@"
AUDIO_LEAD = "![#"
IMAGE_LEAD = "!["
LINK_LEAD = "["
REFER_SPLIT = "]("
REFER_END = ")"

class MarkdownParser(object):
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

	def handle_source_delimiter(self):
		x = self.mdtext.split(SOURCE_DELIMITER,1)
		mk_p = MarkdownParser(x[0])
		d = {
			'source':x[0]
		}
		self.result.append(d) 
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
			self.text = f'{AUDIO_LEAD}'
			return
		title = x[0]
		y = x[1].split(REFER_END,1)
		if len(y) < 2:
			self.text = f'{AUDIO_LEAD}'
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
			self.text = f'{IMAGE_LEAD}'
			return
		title = x[0]
		y = x[1].split(REFER_END,1)
		if len(y) < 2:
			self.text = f'{IMAGE_LEAD}'
			return
		url = y[0]
		d = {
			"image":{
				"title":"title",
				"url":url
			}
		}
		self.result.append(d)
		self.mdtext = y[1]

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

class MDImage(AsyncImage):
	parent_width=NumericProperty(None)
	image_size = ListProperty(None)	
	def __init__(self, **kw):
		super().__init__(**kw)
		self.image_size = None
		self.parent_width = None
		self.bind(texture=self.image_loaded)

	def image_loaded(self,o, *args):
		self.image_size = self.texture.size

	def resize(self, *args):
		ps = [0,0,0,0]
		if hasattr(self.parent, 'padding'):
			ps = self.parent.padding
		self.parent_width = self.parent.width - ps[0] - ps[2]
		if self.texture:
			if self.texture.size:
				self.image_size = self.texture.size
		Logger.info('MDImage:resize called, %d', self.parent_width)

	def on_image_size(self, *args):
		if self.parent_width:
			Logger.info('MDImage:on_iage_size %d, %s', self.parent_width,
						self.image_size)
			self.set_image_size()

	def on_parent_width(self, *args):
		if self.image_size:
			Logger.info('MDImage:on_oarent_width %d, %s', self.parent_width,
						self.image_size)
			self.set_image_size()

	def set_image_size(self):
		self.width = self.parent_width
		self.height = self.parent_width * self.image_size[1] \
							/ self.image_size[0]
		Logger.info('MDImage:set_image_size %d, %d', self.width,
					self.height)
	
class MarkdownBody(VBox):
	def __init__(self, md_obj=None, padding=[10,10,10,10], **kw):
		self.part_handlers = {
			"pure_md":self.build_pure_md,
			"source":self.build_source,
			"image":self.build_image,
			"video":self.build_video,
			"audio":self.build_audio
		}
		self.md_obj = md_obj
		super().__init__(**kw)
		self.padding=padding
		self.size_hint = None,None
		self.bind(parent=self.resize)
		self.resize()
	
	def show_mdtext(self, mdtext):
		mdp = MarkdownParser(mdtext)
		parts = mdp.parse()
		self.clear_widgets()
		for p in parts:
			for k,v in p.items():
				f = self.part_handlers.get(k)
				f(v)

	def resize(self, *args):
		Logger.info('MDBody:resize called')
		if self.parent:
			ps = [0,0,0,0]
			if hasattr(self.parent, 'padding'):
				ps = self.parent.padding
			h = 0
			for c in self.children:
				if hasattr(c, 'resize'):
					c.resize()
				h += c.height
			self.width = self.parent.width - ps[0] - ps[2]
			self.height = h
		else:
			Logger.info('resize:parent is null')

	def build_source(self,source_desc):
		w = MarkdownBody(md_obj=self.md_obj,
				csscls=self.md_obj.second_css, size_hint_y=None)
		w.show_mdtext(source_desc)
		self.add_widget(w)
		w.resize()

	def build_pure_md(self, mdtext):
		for l in mdtext.split('\n'):
			self.parse_line(l)

	def build_image(self,img_desc):
		w = MDImage(source=img_desc['url'],
					allow_stretch=True,
					size_hint_y=None,
					height=CSize(10),
					keep_ratio=True
			)
		
		self.add_widget(w)
		w.resize()

	def build_video(self, video_desc):
		w = Factory.NewVideo(source=video_desc['url'],
				keep_ratio=True,
				play=False,
				allow_stretch = True,
				size_hint_y=None
		)
		w.height=self.width * 10 / 16
		w.state = 'pause'
		def f1(x):
			x.state = 'play'
		def f2(x):
			x.state = 'stop'

		w.bind(on_enter_focus=f1)
		w.bind(on_leave_focus=f2)
		self.add_widget(w)
		w.resize()
		
	def build_audio(self, audio_desc):
		w = Factory.APlayer(source=audio_desc.url)
		w.bind(minimum_height=w.setter('height'))
		self.add_widget(w)

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
		w.bind(on_ref_press=self.md_obj.open_new_md)
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
		print('markdown.py, t=', t, 'len(t)=', len(t), 'type(t)=', type(t))
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
		w.bind(on_ref_press=self.md_obj.open_new_md)
		self.add_widget(w)

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


class Markdown(ScrollView):
	"""
# Markdown
MArkdown widget using to render a markdown file and show it
description file format
{
	"widgettype":"Markdown",
	"options":{
		"source": the markdown file
		"first_css":,
		"second_css":
		other options
	}
}
	"""
	source = StringProperty(None)
	first_css = StringProperty("default")
	second_css = StringProperty("default")
	def __init__(self, **kw):
		super(Markdown, self).__init__(**kw)
		self.root_body = MarkdownBody(md_obj=self,
					csscls=self.first_css,
					size_hint_y=None
		)
		self.root_body.bind(minimum_height=self.root_body.setter('height'))
		self.add_widget(self.root_body)
		self.source = kw.get('source')
		if self.source:
			self.load_text()
		self.bind(size=self.root_body.resize)
		self.bind(source=self.load_text)

	def check_parent_window(self, *args):
		pw = self.get_parent_window()
		rw = self.get_root_window()
		print('MD: pw=%s,rw=%s', pw,rw)

	def stop_media(self, *args):
		self.root_body.stp_video()

	def load_text(self, *args):
		h = getDataHandler(self.source)
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
		self.root_body.show_mdtext(text)
		self.scroll_y = 1

	def open_new_md(self, o, value):
		print(value,'is it a link')
		self.source = value
