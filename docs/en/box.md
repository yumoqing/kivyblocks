# Box
Box is a BoxLayout widget with a BGColorBehavior class, when add a Text, or widget contains Text, it will set the Text color as Box's fgcolor. 

It use normal_bgcolor as the background color, and normal_fgcolor as the text color if the Box is not selected, when the Box is selected, it show selected_bgcolor background color, and reset the Text's color inside the Box with selected_fgcolor

## options

### color_level
default is 0, the main color seials, color level for this widget, please reference to block color for further information
### radius: default is [], means not Box corner without radius. if present, it must be a list of 4 float value, indicate radius for the four corners[ top=left, top-right, bottom-right, bottom-left] 

### others options
each options accepte by BoxLayout is also accepted by Box

## Method

### selected
selected draws Box's background with selected_bgcolor, set all the Text widgets's color with selected_fgcolor

### unselected
this method draws Box's background with normal_bgcolor, set all Text widgets's color with normal_fgcolor

## event
no new events

## refence
Horizonal Box[HBox](./hbox.md)
Vertical Box[VBox](./vbox.md)
Text [Text](./text.md)


