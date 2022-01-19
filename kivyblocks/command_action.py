
from functools import partial
from kivy.logger import Logger
from kivy.factory import Factory

def get_cmd_desc(cmd_desc):
	desc = {
	}
	v = cmd_desc
	desc['target'] = v.get('target')
	if v.get('datawidget'):
		desc['datawidget'] = v.get('datawidget')
		if v.get('datamethod'):
			desc['datamethod'] = v['datamethod']
	keys = v.keys()
	if 'url' in keys:
		desc['actiontype'] = 'urlwidget'
		desc['mode'] = 'replace'
		options = {
			'params':v.get('params',{}),
			'url':v.get('url')
		}
		desc['options'] = options
		return desc
	if 'rfname' in keys:
		desc['actiontype'] = 'registedfunction'
		desc['params'] = v.get('params',{})
		return desc
	if 'script' in keys:
		desc['actiontype'] = 'script'
		desc['script'] = v.get('script')
		return desc
	if 'method' in keys:
		desc['actiontype'] = 'method'
		desc['method'] = v.get('method')
		return desc
	if 'actions' in keys:
		desc['actiontype'] = 'multiple'
		desc['actions'] = v.get('actions')
		return desc
	return None

def cmd_action(cmd_desc, widget):
	desc = get_cmd_desc(cmd_desc)
	if desc is None:
		Logger.error('CommandAction: cmd_desc=%s error')
		return
	blocks = Factory.Blocks()
	if 'conform' in cmd_desc:
		options = cmd_desc['conform']
		w = Factory.Conform(**options)
		f = partial(blocks.uniaction, widget, desc)
		w.bind(on_conform=f)
		return
	blocks.uniaction(widget, desc)

