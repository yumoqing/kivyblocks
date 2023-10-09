try:
	import ujson as json
except:
	import json
from kivy.factory import Factory
from .factory import UiFactory
from appPublic.myTE import MyTemplateEngine

def view_build_viewer(desc, rec=None):
	viewer_desc = desc.get('viewer')
	if not viewer_desc:
		return None
	if isinstance(viewer_desc, dict):
		viewer_desc = json.dumps(viewer_desc)

	mytmpl = MyTemplateEngine(['.'])
	v_desc = mytmpl.renders(viewer_desc, rec)
	vdesc = json.loads(v_desc)
	return Factory.Blocks().widgetBuild(vdesc)

UiFactory.register('viewer', None, view_build_viewer)
