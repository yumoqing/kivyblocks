
from functools import partial
from kivy.logger import Logger
from kivy.factory import Factory

def get_cmd_desc(cmd_desc):
	desc = {
	}
	v = cmd_desc
	desc['conform'] = v.get('conform')
	desc['target'] = v.get('target')
	if v.get('datawidget'):
		desc['datawidget'] = v.get('datawidget')
		if v.get('datamethod'):
			desc['datamethod'] = v['datamethod']
	keys = v.keys()
	if 'url' in keys:
		Logger.info('get_cmd_desc():cmd_desc=%s', cmd_desc)
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
		Logger.error('CommandAction: desc is None cmd_desc=%s error', \
						cmd_desc)
		return
	blocks = Factory.Blocks()
	conform_desc = desc.get('conform')
	if conform_desc is None:
		Logger.info('cmd_action():desc=%s', desc)
		blocks.uniaction(widget, desc)
		return

	w = blocks.widgetBuild({
			"widgettype":"Conform",
			"options":conform_desc
	})
	w.bind(on_conform=partial(blocks.uniaction, widget, desc))
	w.open()
	Logger.info('cmd_action():desc=%s, conform and action', desc)


