
from functools import partial
from ffpyplayer.player import MediaPlayer as OldMediaPlayer
from threading import Thread
from kivy.core.video.video_ffpyplayer import VideoFFPy
from kivy.core.video import video_ffpyplayer

external_ff_opts = {}
external_lib_opts = {}

def set_external_ff_opts(dic):
	external_ff_opts = dic

def set_external_lib_opts(dic):
	external_lib_opts = dic

def MediaPlayer(filename, *args, ff_opts={}, lib_opts={}, **kw):
	ff_opts.update(external_ff_opts)
	lib_opts.update(external_lib_opts)
	if filename.startswith('http://') or \
			filename.startswith('https://'):
		headers = get_spec_headers(filename)
		if headers is not None:
			lib_opts['headers'] = "$'%s'" % headers

	return OldMediaPlayer(filename, *args, ff_opts=ff_opts,
						lib_opts=lib_opts, **kw)

def hack_mediaplayer():
	video_ffpyplayer.MediaPlayer = MediaPlayer

headers_pattern = {
}

def set_headers_pattern(pattern, headers_str):
	headers_pattern[pattern] = headers_str

def get_spec_headers(filename):
	for p in headers_pattern.keys():
		if p in filename:
			return headers_pattern[p]
	return None
