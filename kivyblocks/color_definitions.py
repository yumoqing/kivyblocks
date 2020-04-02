from kivy.logger import Logger
from .colorcalc import *
from appPublic.jsonConfig import getConfig

colors = {
    'Red': {
        '200': 'ef9a9a',
        '900': 'b71c1c',
        '600': 'e53935',
        'A100': 'ff8a80',
        '300': 'e57373',
        'A400': 'ff1744',
        '700': 'd32f2f',
        '50': 'ffebee',
        'A700': 'd50000',
        '400': 'ef5350',
        '100': 'ffcdd2',
        '800': 'c62828',
        'A200': 'ff5252',
        '500': 'f44336'
    },
    'Pink': {
        '50': 'fce4ec',
        '100': 'f8bbd0',
        '200': 'f48fb1',
        '300': 'f06292',
        '400': 'ec407a',
        '500': 'e91e63',
        '600': 'd81b60',
        '700': 'C2185B',
        '800': 'ad1457',
        '900': '88e4ff',
        'A100': 'ff80ab',
        'A400': 'F50057',
        'A700': 'c51162',
        'A200': 'ff4081'
    },
    'Purple': {
        '200': 'ce93d8',
        '900': '4a148c',
        '600': '8e24aa',
        'A100': 'ea80fc',
        '300': 'ba68c8',
        'A400': 'D500F9',
        '700': '7b1fa2',
        '50': 'f3e5f5',
        'A700': 'AA00FF',
        '400': 'ab47bc',
        '100': 'e1bee7',
        '800': '6a1b9a',
        'A200': 'e040fb',
        '500': '9c27b0'
    },
    'DeepPurple': {
        '200': 'b39ddb',
        '900': '311b92',
        '600': '5e35b1',
        'A100': 'b388ff',
        '300': '9575cd',
        'A400': '651fff',
        '700': '512da8',
        '50': 'ede7f6',
        'A700': '6200EA',
        '400': '7e57c2',
        '100': 'd1c4e9',
        '800': '4527a0',
        'A200': '7c4dff',
        '500': '673ab7'
    },
    'Indigo': {
        '200': '9fa8da',
        '900': '1a237e',
        '600': '3949ab',
        'A100': '8c9eff',
        '300': '7986cb',
        'A400': '3d5afe',
        '700': '303f9f',
        '50': 'e8eaf6',
        'A700': '304ffe',
        '400': '5c6bc0',
        '100': 'c5cae9',
        '800': '283593',
        'A200': '536dfe',
        '500': '3f51b5'
    },
    'Blue': {
        '200': '90caf9',
        '900': '0D47A1',
        '600': '1e88e5',
        'A100': '82b1ff',
        '300': '64b5f6',
        'A400': '2979ff',
        '700': '1976d2',
        '50': 'e3f2fd',
        'A700': '2962ff',
        '400': '42a5f5',
        '100': 'bbdefb',
        '800': '1565c0',
        'A200': '448aff',
        '500': '2196f3'
    },
    'LightBlue': {
        '200': '81d4fa',
        '900': '01579B',
        '600': '039BE5',
        'A100': '80d8ff',
        '300': '4fc3f7',
        'A400': '00B0FF',
        '700': '0288D1',
        '50': 'e1f5fe',
        'A700': '0091EA',
        '400': '29b6f6',
        '100': 'b3e5fc',
        '800': '0277BD',
        'A200': '40c4ff',
        '500': '03A9F4'
    },
    'Cyan': {
        '200': '80deea',
        '900': '006064',
        '600': '00ACC1',
        'A100': '84ffff',
        '300': '4dd0e1',
        'A400': '00E5FF',
        '700': '0097A7',
        '50': 'e0f7fa',
        'A700': '00B8D4',
        '400': '26c6da',
        '100': 'b2ebf2',
        '800': '00838F',
        'A200': '18ffff',
        '500': '00BCD4'
    },
    'Teal': {
        '200': '80cbc4',
        '900': '004D40',
        '600': '00897B',
        'A100': 'a7ffeb',
        '300': '4db6ac',
        'A400': '1de9b6',
        '700': '00796B',
        '50': 'e0f2f1',
        'A700': '00BFA5',
        '400': '26a69a',
        '100': 'b2dfdb',
        '800': '00695C',
        'A200': '64ffda',
        '500': '009688'
    },
    'Green': {
        '200': 'a5d6a7',
        '900': '1b5e20',
        '600': '43a047',
        'A100': 'b9f6ca',
        '300': '81c784',
        'A400': '00E676',
        '700': '388e3c',
        '50': 'e8f5e9',
        'A700': '00C853',
        '400': '66bb6a',
        '100': 'c8e6c9',
        '800': '2e7d32',
        'A200': '69f0ae',
        '500': '4caf50'
    },
    'LightGreen': {
        '200': 'c5e1a5',
        '900': '33691e',
        '600': '7cb342',
        'A100': 'ccff90',
        '300': 'aed581',
        'A400': '76FF03',
        '700': '689f38',
        '50': 'f1f8e9',
        'A700': '64dd17',
        '400': '9ccc65',
        '100': 'dcedc8',
        '800': '558b2f',
        'A200': 'b2ff59',
        '500': '8bc34a'
    },
    'Lime': {
        '200': 'e6ee9c',
        '900': '827717',
        '600': 'c0ca33',
        'A100': 'f4ff81',
        '300': 'dce775',
        'A400': 'C6FF00',
        '700': 'afb42b',
        '50': 'f9fbe7',
        'A700': 'AEEA00',
        '400': 'd4e157',
        '100': 'f0f4c3',
        '800': '9e9d24',
        'A200': 'eeff41',
        '500': 'cddc39'
    },
    'Yellow': {
        '200': 'fff59d',
        '900': 'f57f17',
        '600': 'fdd835',
        'A100': 'ffff8d',
        '300': 'fff176',
        'A400': 'FFEA00',
        '700': 'fbc02d',
        '50': 'fffde7',
        'A700': 'FFD600',
        '400': 'ffee58',
        '100': 'fff9c4',
        '800': 'f9a825',
        'A200': 'FFFF00',
        '500': 'ffeb3b'
    },
    'Amber': {
        '200': 'ffe082',
        '900': 'FF6F00',
        '600': 'FFB300',
        'A100': 'ffe57f',
        '300': 'ffd54f',
        'A400': 'FFC400',
        '700': 'FFA000',
        '50': 'fff8e1',
        'A700': 'FFAB00',
        '400': 'ffca28',
        '100': 'ffecb3',
        '800': 'FF8F00',
        'A200': 'ffd740',
        '500': 'FFC107'
    },
    'Orange': {
        '200': 'ffcc80',
        '900': 'E65100',
        '600': 'FB8C00',
        'A100': 'ffd180',
        '300': 'ffb74d',
        'A400': 'FF9100',
        '700': 'F57C00',
        '50': 'fff3e0',
        'A700': 'FF6D00',
        '400': 'ffa726',
        '100': 'ffe0b2',
        '800': 'EF6C00',
        'A200': 'ffab40',
        '500': 'FF9800'
    },
    'DeepOrange': {
        '200': 'ffab91',
        '900': 'bf36c',
        '600': 'f4511e',
        'A100': 'ff9e80',
        '300': 'ff8a65',
        'A400': 'FF3D00',
        '700': 'e64a19',
        '50': 'fbe9e7',
        'A700': 'DD2C00',
        '400': 'ff7043',
        '100': 'ffccbc',
        '800': 'd84315',
        'A200': 'ff6e40',
        '500': 'ff5722'
    },
    'Brown': {
        '200': 'bcaaa4',
        '900': '3e2723',
        '600': '6d4c41',
        '300': 'a1887f',
        '700': '5d4037',
        '50': 'efebe9',
        '400': '8d6e63',
        '100': 'd7ccc8',
        '800': '4e342e',
        '500': '795548'
    },
    'Grey': {
        '200': 'eeeeee',
        '900': '212121',
        '600': '757575',
        '300': 'e0e0e0',
        '700': '616161',
        '50': 'fafafa',
        '400': 'bdbdbd',
        '100': 'f5f5f5',
        '800': '424242',
        '500': '9e9e9e'
    },
    'BlueGrey': {
        '200': 'b0bec5',
        '900': '263238',
        '600': '546e7a',
        '300': '90a4ae',
        '700': '455a64',
        '50': 'eceff1',
        '400': '78909c',
        '100': 'cfd8dc',
        '800': '37474f',
        '500': '607d8b'
    },

    'Light': {
        'StatusBar': 'E0E0E0',
        'AppBar': 'F5F5F5',
        'Background': 'FAFAFA',
        'CardsDialogs': 'FFFFFF',
        'FlatButtonDown': 'cccccc'
    },

    'Dark': {
        'StatusBar': '000000',
        'AppBar': '212121',
        'Background': '303030',
        'CardsDialogs': '424242',
        'FlatButtonDown': '999999'
    }
}

light_colors = {
    'Red': ['50', '100', '200', '300', 'A100'],
    'Pink': ['50', '100', '200', 'A100'],
    'Purple': ['50', '100', '200', 'A100'],
    'DeepPurple': ['50', '100', '200', 'A100'],
    'Indigo': ['50', '100', '200', 'A100'],
    'Blue': ['50','100', '200', '300', '400', 'A100'],
    'LightBlue': ['50', '100', '200', '300', '400', '500', 'A100', 'A200',
                  'A400'],
    'Cyan': ['50', '100', '200', '300', '400', '500', '600', 'A100', 'A200',
             'A400', 'A700'],
    'Teal': ['50', '100', '200', '300', '400', 'A100', 'A200', 'A400', 'A700'],
    'Green': ['50', '100', '200', '300', '400', '500', 'A100', 'A200', 'A400',
              'A700'],
    'LightGreen': ['50', '100', '200', '300', '400', '500', '600', 'A100',
                   'A200', 'A400', 'A700'],
    'Lime': ['50', '100', '200', '300', '400', '500', '600', '700', '800',
             'A100', 'A200', 'A400', 'A700'],
    'Yellow': ['50', '100', '200', '300', '400', '500', '600', '700', '800',
               '900', 'A100', 'A200', 'A400', 'A700'],
    'Amber': ['50', '100', '200', '300', '400', '500', '600', '700', '800',
              '900', 'A100', 'A200', 'A400', 'A700'],
    'Orange': ['50', '100', '200', '300', '400', '500', '600', '700', 'A100',
               'A200', 'A400', 'A700'],
    'DeepOrange': ['50', '100', '200', '300', '400', 'A100', 'A200'],
    'Brown': ['50', '100', '200'],
    'Grey': ['51', '100', '200', '300', '400', '500'],
    'BlueGrey': ['50', '100', '200', '300'],
    'Dark': [],
    'Light': ['White', 'MainBackground', 'DialogBackground']
}

level_bg_colors = [
	'900',
	'800',
	'700',
	'600',
	'500',
	'400',
	'300',
	'200',
	'100',
	'50'
]

text_colors = {
	'normal':['eeeeee','111111'], 
	'highlight':['ffffff','000000']
}

def getConfigStyle():
	config = getConfig()
	stype = config.color_style or 'Blue'
	return stype

def getTextColor(bgcolor,type='normal'):
	colors = text_colors.get(type,text_colors.get('normal'))
	d = 0
	tcolor = None
	for c in colors:
		d1 = distance(bgcolor,c)
		if d1>d:
			d = d1
			tcolor = c
	return tcolor

def getColors(level=0,selected=False):
	style = getConfigStyle()
	i = level % 8
	Logger.info('TEST : style=%s,level=%d', style, level)
	bg_color = colors[style][ level_bg_colors[i]]
	if selected:
		k = level_bg_colors[i]
		k1 = level_bg_colors[i+1]
		colors1 = divideColor(colors[style][k],colors[style][k1],2)
		bg_color = colors1[1]
	text_color = getTextColor(bg_color)
	return toArrayColor(text_color),toArrayColor(bg_color)

error_color_id = '100',
info_color_id = '50'
def getErrorColors():
	style = getConfigStyle()
	bg_color = colors[style][ error_color_id ]
	text_color = getTextColor(bg_color,type='highlight')
	return toArrayColor(text_color),toArrayColor(bg_color)
	
def getInfoColors():
	style = getConfigStyle()
	bg_color = colors[style][ info_color_id ]
	text_color = getTextColor(bg_color)
	return toArrayColor(text_color),toArrayColor(bg_color)
