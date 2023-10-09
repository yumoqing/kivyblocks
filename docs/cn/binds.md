# 事件绑定
在构件数据格式文件中可以用”binds“属性来为构件定义一到多个事件绑定。

事件绑定是一个数组结构的数据，每个事件绑定为当前构件（及其下属命名子构件）的任何一个事件定义处理实体

一个处理实体可以是
1. 一个构件的方法
2. 一个”urlwidget“类型的构件
3. 一个描述一个构件的构件数据
4. 一个注册函数
5. 一个python脚本
6. 某个构件的事件
7. 一个组合处理（可以是上述处理实体的组合数组）

## 名称约定

* self 当前构件

* root App.root构件

* “-”（减号）开始的名称，从当前位置查找命名的祖先构件，如果到app.root还没有找到，则返回空

* app App.get_running_app

## 事件绑定数据格式说明

### wid
	事件发生所在构件，如果wid所代表的构件不存在指定的事件，此事件绑定将作废，
	必选项，self为当前构件

### event
	事件名称，wid和event组合就可以唯一确定一个事件

### actiontype
	行动类型，分别是“blocks”、”urlwidget“、“registerfunction”，“script”、“method“、”event“和”multiple“之一。

* ”blocks“：值必须是一个符合构件数据格式要求的字典数据，用来创建一个构件。

* ”urlwidget“；值必须是一个url，从服务器下载一个构件数据格式的文件来创建构件

* ”Registerfunction“：注册函数，注册函数必须是def f(*args, **kwargs)参数格式，args[0] 为wid所代表的构件对象，如果事件带数据，则从args[1]开始。

* ”script“：python 脚本。在脚本中有两个内定变量可用： self为“target”指定的构件，args=[事件对象,s事件数据]

* ”method“：构件的方法，构件由此事件绑定的”target“属性指定，此方法必须具有*args, **kwargs格式的参数定义方式

* ”event“：构件的事件，构件由此事件绑定的”target“属性指定，事件绑定的参数将传递给此事件

* “multiple”：组合绑定，参看例子

### datatarget
	指定数据获取的构件，此构件需有“getValue”方法，用来获取数据，数据需是字典类型

### target
	指定处理事件的构件，对于actiontype in ["blocks", "urlwidget"]的事件绑定， target为其父构件，缺省的插入方式为替代，即用事件构造的构件，替换所有target构件中的其他子构件，成为target构件的唯一子构件，可以在事件绑定定义了不等于”replace“的“mode“属性，使得新创建的构件添加在其他构件的后面。

### mode
	可选属性，只有在actiontype in ["blocks", "urlwidget"]情况下有效，指定事件创建的构件在target构件中的插入方式，mode==”replace“时，清空target的所有子构件后插入，否则添加到最后。

### params
	事件处理指定的静态参数，其值在构件创建时确定，不会改变，实际传递给事件处理的参数为params.update(d)， 其中d为datatarget构件的getValue方法返回的结果。如果未定义datatarget，则d={}, 

### options
	可选项，只有在actiontype in ["blocks", "urlwidget"]情况下有效，指定创建构件的构件数据格式options的值需是一个数据字典，且需满足构件数据格式要求。参看[构件数据格式](./cdf.md)

### conform
	可选项，如果存在，此事件处理前需要客户点击弹出窗体中的确认键，否则将不会处理
	conform的数据格式如下：
```
"conform":{
	"size_hint":[0.6,0.6],
	"title":"Conform for delete playlist",
	"message":"Please conform to delete this play list"
}

```
其中
	* size_hint定义弹出窗体占屏幕宽，高的占比

	* title是团出窗体的标题
	
	* message是显示的内容

### rfname
	当actiontype==‘registedfunction’时有效，指定注册函数，在前端应用中需先注册, 使用以下代码注册一个registedfunction
```
from appPublic.registerfunction import RegisterFunction

def HelloRF(*args, **kwargs):
	print('Hello ...')

rf = RegisterFunciton()
rf.register('testrf', HelloRF)
```
'testrf'即可用于rfname

### script
	当actiontype=='script'时有效，其值是一行可执行的python代码

### dispatch_event
	当actiontype=='event'时有效，指定需要触发target构件上的事件名称


## 例子

### urlwidget
```
        {
            "actiontype":"urlwidget",
            "wid":"delete",
            "datawidget":"delete",
            "target":"root.public_popup",
            "event":"on_press",
            "conform":{
                "size_hint":[0.6,0.6],
                "title":"Conform for delete playlist",
                "message":"Please conform to delete this play list"
            },
            "options":{
                "method":"GET",
                "mode":"replace",
                "params":{{json.dumps(params_kw)}},
                "url":"{{entire_url('delete_pldetail_song.dspy')}}"
            }
        },
```
命名构件”delete“按钮的”on_press"事件被绑定到了一个“urlwidget”事件处理上，数据来源为“delete”构件， 目标窗体为app.root构件下面的一个”public_popup"的构件。此事件的处理需要用户在弹出窗体中点击确认键后才能处理。

### method
```
        {
            "event":"on_press",
            "actiontype":"method",
            "wid":"delete",
            "target":"root.public_popup",
            "method":"open"
        }
```
命名构件“delete”的“on_press"事件调用app.root的public_popup构件的open函数来处理。

### registedfunction
```
        {
            "actiontype":"registedfunction",
            "wid":"playlist_add",
            "event":"on_submit",
            "datawidget":"playlist_add",
            "target":"self",
            "rfname":"playlist_add"
        }
```
"playlist_add"构件的"on_submit"事件绑定在一个registedfunction的处理函数上
事件的数据来源与“playlist_add"构件。

### script
```
        {
            "actiontype":"script",
            "wid":"playlist_add",
            "event":"on_submit",
            "datawidget":"playlist_add",
            "target":"self",
            "script":"print(self, args)"
        }
```
"playlist_add"构件的"on_submit"事件绑定了一个script的处理，即打印出target和参数


