
from functools import partial
from ffpyplayer.player import MediaPlayer
from threading import Thread
from kivy.core.video.video_ffpyplayer import VideoFFPy

headers_pattern = {
}

def set_headers_pattern(pattern, headers_str):
	headers_pattern[pattern] = headers_str

def get_spec_headers(filename):
	for p in headers_pattern.keys():
		if p in filename:
			return headers_pattern[p]
	return None

old_init = getattr(MediaPlayer, '__init__')

def mediaplayer_init(self, filename, *args, lib_opts={}, **kw):
	print('******************** MediaPlayer __init__ hacked *****')
	if self._filename.startswith('http://') or \
			self._filename.startswith('https://'):
		headers = get_spec_headers(self._filename)
		if headers is not None:
			lib_opts['headers'] = "$'%s'" % headers
	old_init(self, file, *args, lib_opts=lib_opts, **kw)

# setattr(MediaPlayer, '__init__', mediaplayer_init)
