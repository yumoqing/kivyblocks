#uitype.py
"""
each ui type need to provides a view widget and a input widget
to auto construct the form widget and record show widget.

we use a register machinans to maintian the ui type information to build the view widget and input widget
"""

from kivy.factory import Factory

from appPublic.myTE import string_template_render

view_widget_builders = {
}

input_widget_builders = {}

def view_register(uitype, f):
	view_widget_builders.update({uitype:f})

def input_register(uitype, f):
	input_widget_builders.update({uitype:f})

def get_input_builder(uitype):
	return input_widget_builders.get(uitype, \
			input_widget_builders.get('str', None))

def get_view_builder(uitype):
	return view_widget_builders.get(uitype, \
			view_widget_builders.get('str', None))

def build_view_widget(desc, rec = None):
	if desc.get('viewer'):
		if isinstance(viewer,dict):
			viewer = json.dumps(viewer)
		rendered = string_template_render(viewer, rec)
		dic = json.loads(rendered)
		if dic is None:
			return None
		w = Factory.Blocks().widgetBuild(dic)
		return w
		
	f = get_view_builder(desc.get('uitype'))
	return f(desc, rec)

def build_input_widget(desc, rec=None):
	f = get_input_builder(desc.get('uitype'))
	return f(desc, rec)

def get_value(desc, rec=None):
	if rec:
		return rec.get(desc['name'])
	return desc.get('value', desc.get('defaultvalue', ''))
	
def build_view_text_widget(desc, rec=None):
	txt = get_value(desc, rec=rec)
	return Factory.Text(text=str(txt),
						font_size=CSize(1),
						wrap=True,
						halign='left',
						valign='middle')

view_register('str', build_view_text_widget)
view_register('date', build_view_text_widget)
view_register('time', build_view_text_widget)
view_register('timestamp', build_view_text_widget)

def build_view_int_widget(desc, rec=None):
	v = get_value(desc, rec=rec)
	return Text(text=str(v),
			font_size=CSize(1), 
			wrap=True,
			halign='right', 
			valign='middle'
	)

view_register('int', build_view_int_widget)
view_register('long', build_view_int_widget)
view_register('integer', build_view_int_widget)

def build_view_float_widget(desc, rec=None):
	v = get_value(desc, rec=rec)
	f = '%%.0%df' % desc.get('dec',2)
	return Text(text=f % float(v),
					font_size=CSize(1), 
					wrap=True,
					halign='right', 
					valign='middle'
			)

view_register('float', build_view_float_widget)

def build_view_code_widget(desc, rec=None):
		tf = desc.get('textField','text')
		vf = desc.get('valueField','value')
		v = rec.get(tf,rec.get(vf, ' '))
		return Text(text=v, 
					font_size = CSize(1), 
					wrap=True,
					halign='center', 
					valign='middle'
		)

view_register('code', build_view_code_widget)


