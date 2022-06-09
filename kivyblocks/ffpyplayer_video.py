
import time
import numpy as np
from ffpyplayer.player import MediaPlayer
from ffpyplayer.tools import set_log_callback

from kivy.factory import Factory
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, \
			OptionProperty, NumericProperty
from kivy.graphics.texture import Texture


class FFVideo(Image):
	v_src = StringProperty(None)
	status = OptionProperty('stop', \
			options=['stop', 'play', 'pause'])
	play_mode = OptionProperty('normal', \
			options=['normal', 'preview', 'audioonly'])
	header_callback = StringProperty(None)
	audio_id = NumericProperty(None)
	duration = NumericProperty(-1)
	position = NumericProperty(-1)
	volume = NumericProperty(-1)
	framerate = NumericProperty(180)
	in_center_focus = BooleanProperty(Fasle)

	def __init__(self, **kwargs):
		self._player = None
		self._update_task = None
		self._texture = None
		self.is_black = False
		self.videosize = None
		self.timeperiod = 1.0 / self.framerate
		self.ff_opts = {}
		self.lib_opts = {}
		self.headers_pattern = {}
		self.playing_task = None
		self.playing_tasks = []
		super(FFVideo, self).__init__(**kwargs)
		self.register_event_type('on_frame')
		self.register_event_type('on_open_failed')
		self.register_event_type('on_leave_focus')
		self.register_event_type('on_enter_focus')
		self.register_event_type('on_load_success')

	def add_playing_task(self, f):
		if f in self.playing_tasks:
			return
		self.playing_tasks.append(f)

	def del_playing_task(self, f):
		self.playing_tasks = [ i for i in self.playing_tasks if i != f ]

	def do_playing_tasks(self, *args):
		for f in self.playing_tasks:
			try:
				f()
			except Exception as e:
				print('error:', e)
				print_exc()

	def on_open_failed(self, *args):
		pass

	def on_load_syccess(self, *args):
		pass

	def on_enter_focus(self, *args):
		pass

	def on_leave_focus(self, *args):
		pass

	def check_focus(self,*args):
		if not self.parent:
			self.in_center_screen = False
			return
		if not self.get_root_window():
			self.in_center_screen = False

		w = self.parent
		pos = w.to_widget(*Window.center)
		if self.collide_point(*pos):
			self.in_center_screen = True
		else:
			self.in_center_screen = False

	def set_ff_opt(self, k,v):
		self.ff_opts.update({k:v})

	def set_lib_opt(self, k, v):
		self.lib_opts.update({k:v})

	def set_pattern_header(self, pattern, k,v):
		dic = self.headers_pattern.get(pattern,{})
		dic.update({k:v})
		self.headers_pattern[pattern] = dic

	def _get_spec_headers(self, filename):
		for p in self.headers_pattern.keys():
			if filename.startswith(p):
				headers = self.headers_pattern[p]
				headers_str = ''.join([f'{k}:{v}\r\n' for k,v in headers.items()])
				return headers_str
		return None

	def on_volume(self, *args):
		if self._player is None:
			return

		self._player.set_volume(self.volume)
		
	def on_status(self, *args):
		print('on_status called, ', self.status)
		if self._player is None:
			return

		if self.status == 'play':
			self._player.set_pause(False)
		elif self.status == 'pause':
			self._player.set_pause(True)
		elif self.status == 'stop':
			self._play_stop()
		else:
			pass

	def on_frame(self, *args):
		if self._player is None:
			return
		if self.audio_id is None:
			return
		self._player.request_channel(self, 'audio', 'open', self.audio_id)

	def __del__(self):
		if self._update_task:
			self._update_task.cancel()
			self._update_task = None
		if self._player:
			self._player.close_player()
			self._player = None

	def set_volume(self, v):
		if self.play_mode == 'preview':
			return
		if self._player is None:
			return
		if self.status != 'play':
			return
		if v > 1.0:
			v = 1.0
		if v < 0.0:
			v = 0.0
		self.volume = v

	def seek(self, pts):
		if self.play_mode == 'preview':
			return
		if self._player is None:
			return
		if self.status != 'play':
			return
		self._player.seek(pts)
		self.position = self._player.get_pts()

	def mute(self, flag):
		if self.play_mode == 'preview':
			return
		if self._player is None:
			return
		if self.status != 'play':
			return
		self._player.set_mute(flag)
		
	def switch_audio(self):
		if self.play_mode == 'preview':
			return
		if self._player is None:
			return
		if self.status != 'play':
			return
		self._player.request_channel('audio', action='cycle')

	def on_v_src(self, o, src):
		self._play_stop()
		ff_opts = {
			'pause':False
		}

		if self.play_mode == 'preview':
			ff_opts['lowres'] = 2 # 1/4 size
			ff_opts['an'] = True
		elif self.play_mode == 'audioonly':
			ff_opts['vn'] = True
		ff_opts.update(self.ff_opts)

		lib_opts = {
		}
		lib_opts.update(self.lib_opts)
		heads = self._get_spec_headers(self.v_src)
		if heads:
			lib_opts.update({'headers':heads})
			ff_opts.update({'headers':heads})

		print('ff_opts=', ff_opts)
		print('lib_opts=', lib_opts)
		# self._player = MediaPlayer(self.v_src) 
		self._player = MediaPlayer(self.v_src, ff_opts=ff_opts, \
						lib_opts=lib_opts) 
		self._play_start()

	def play(self):
		if self._player is None:
			return
		# self._player.set_pause(False)
		self.status = 'play'

	def pause(self):
		if self._player is None:
			return
		# self._player.set_pause(True)
		self.status = 'pause'

	def _play_start(self):
		self.timepass = 0.0
		self.last_frame = None
		self.is_black = False
		self.first_play = True
		self._update_task = Clock.schedule_interval(self._update, self.timeperiod)

	def _get_video_info(self):
		if self.first_play:
			meta = self._player.get_metadata()
			self.duration = meta['duration']
			self.position = 0
			self._out_fmt = meta['src_pix_fmt']
			self.frame_rate = meta['frame_rate']
			self.videosize = meta['src_vid_size']
			if self.playing_task:
				self.playing_task.cancel()
				self.playing_taks = None
			self.playing_task = self.

	def _play_stop(self):
		if self._player is None:
			return
		self._update_task.cancel()
		self._update_task = None
		self._player.close_player()
		self._player = None
		self.timepass = 0
		self.next_frame = None
		self.duration = -1
		self.position = -1
		self.frame_rate = None
		self.videosize = None
		
	def on_size(self, *args):
		if self._player is None:
			return
		if self.videosize == None:
			return
		w, h = self.videosize
		r = w / h
		r1 = self.width / self.height
		if r1 >= r:
			self._player.set_size(-1, self.height)
		else:
			self._player.set_size(self.width, -1)

	def set_black(self):
		if self.is_black:
			return
		image_texture = Texture.create(
            size=self.size, colorfmt='rgb')
		buf = b'\x00' * self.width * self.height * 3
		image_texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
		self.texture = image_texture
		self.is_black = True

	def show_yuv420(self, img):
		w, h = img.get_size()
		w2 = int(w / 2)
		h2 = int(h / 2)
		self._tex_y = Texture.create(
			size=(w, h), colorfmt='luminance')
		self._tex_u = Texture.create(
			size=(w2, h2), colorfmt='luminance')
		self._tex_v = Texture.create(
			size=(w2, h2), colorfmt='luminance')
		self._fbo = fbo = Fbo(size=(w, h))
		with fbo:
			BindTexture(texture=self._tex_u, index=1)
			BindTexture(texture=self._tex_v, index=2)
			Rectangle(size=fbo.size, texture=self._tex_y)
		fbo.shader.fs = VideoFFPy.YUV_RGB_FS
		fbo['tex_y'] = 0
		fbo['tex_u'] = 1
		fbo['tex_v'] = 2
		self._texture = fbo.texture
		dy, du, dv, _ = img.to_memoryview()
		if dy and du and dv:
			self._tex_y.blit_buffer(dy, colorfmt='luminance')
			self._tex_u.blit_buffer(du, colorfmt='luminance')
			self._tex_v.blit_buffer(dv, colorfmt='luminance')
			self._fbo.ask_update()
			self._fbo.draw()
		texture.flip_vertical()
		self.texture = texture

	def show_others(self, img):
		w, h = img.get_size()
		texture = Texture.create(size=(w, h), colorfmt='rgb')
		texture.blit_buffer(
				img.to_memoryview()[0], colorfmt='rgb',
				bufferfmt='ubyte')
		texture.flip_vertical()
		self.texture = texture
		# print('img_size=', w, h, 'window size=', self.size)

	def _update(self, dt):
		if self.last_frame is None:
			frame, val = self._player.get_frame()
			if val == 'eof':
				print('*****EOF******')
				self.status = 'stop'
				self.set_black()
				return
			if val == 'pause':
				self.status = 'pause'
				return
			if frame is None:
				# print('video null', time.time())
				self.set_black()
				return
			self.last_frame = frame
			self.video_ts = val
			self._get_video_info()
			
		self.timepass += self.timeperiod
		self.position = self._player.get_pts()
		if self.timepass < self.video_ts:
			return

		if self.timepass > self.video_ts +0.2:
			self.last_frame = None
			return

		self.status = 'play'
		img, t = self.last_frame
		if self._out_fmt == 'yuv420p':
			self.show_yuv420(img)
		else:
			self.show_others(img)
		self.dispatch('on_frame', self.last_frame)
		self.last_frame = None

Factory.register('FFVideo', FFVideo)
