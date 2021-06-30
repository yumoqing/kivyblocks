from kivy.utils import platform
try:
	from plyer.platforms.android import activity
except:
	activity = None

def get_rotation():
	try:
		r = activity.getWindowManager().getDefaultDisplay().getRotation()
		print('get_rotation(): rotation=', r, type(r))
		return r
	except Exception as e:
		print('get_rotation() failed',e)
		return None
