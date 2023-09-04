from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QObject
import sip

import itertools

from gefplus.components.dragbutton import DragButton



class DragManager:

    """ Abstract class for all the widgets that support 
    drag n' drop operations """

    def __init__(self, *, parent, home_layout=None, home_widget=None, home_area=None,
                single_choice_layouts=None, multi_choice_layouts=None, 
                drop_action=None):
        """
        :param home_layout: The layout containing the draggable buttons 
        :param home_widget: The widget into the home_layout 
        :param home_area: The QScrollArea containing the draggable buttons
        :param single_choice_layouts: The layout that can contain a single draggable button at a time
        :param multi_choice_layouts: The layout that can contain more draggable button at a time
        :param drop_action: The method executed every time a drop takes place
        :param parent: The parent widget
        """
        self.parent = parent 
        self.parent.setAcceptDrops(True)
        self.parent.dragEnterEvent = self.dragEnterEvent
        self.parent.dropEvent = self.dropEvent
        self.home_layout = home_layout
        self.home_widget = home_widget
        self.home_area = home_area
        self.single_choice_layouts = tuple() if single_choice_layouts is None else single_choice_layouts
        self.multi_choice_layouts = tuple() if multi_choice_layouts is None else multi_choice_layouts
        self.drop_action = drop_action

    def get_content (self, layout):
        """ Get names of buttons in a layout """
        count = len([i for i in range(layout.count()) if isinstance(layout.itemAt(i).widget(), DragButton)])
        if count == 0: 
            return
        fields = tuple(layout.itemAt(i).widget().text() 
            for i in range(layout.count()) if isinstance(layout.itemAt(i).widget(), DragButton))
        return fields[0] if len(fields) == 1 and layout in self.single_choice_layouts else fields
    
    @property 
    def all_layouts(self):
        return itertools.chain((self.home_layout, ), self.single_choice_layouts, self.multi_choice_layouts)

    def reset(self):
        """ Reset all the draggable buttons """
        for layout in self.all_layouts:
            for i in range(layout.count()):  
                widget = layout.itemAt(i).widget()
                if isinstance(widget, DragButton):
                    widget.deleteLater()
                if (layout in self.single_choice_layouts or layout in self.multi_choice_layouts) and \
                   (layout.count() == 0 or layout.count() == 1 and isinstance(layout.itemAt(0).widget(), DragButton)):
                    widget = QWidget()
                    widget.setStyleSheet("margin:5px; border:1px solid rgb(180, 180, 180);")
                    widget.setMinimumSize(100, 40)
                    widget.setMaximumSize(16777215, 40)
                    layout.addWidget(widget)
        
    def populate_buttons(self, fields, clear=False):
        """ Populate the home_layout with the draggable buttons """
        if clear: 
            self.reset()
        for header in fields:
            btn = DragButton(header, self.parent)
            self.home_layout.addWidget(btn)
        

    def add_dummy_widgets(self):
        """ Add a dummy widget to the layouts to ensure 
        the drag n' drop functioning """
        #print([layout.count() for layout in self.all_layouts])
        for layout in itertools.chain(self.single_choice_layouts, self.multi_choice_layouts):
            if layout.count() == 0:
                widget = QWidget()
                widget.setStyleSheet("margin:5px; border:1px solid rgb(180, 180, 180);")
                widget.setMinimumSize(100, 40)
                widget.setMaximumSize(16777215, 40)
                layout.addWidget(widget)
    
    def dragEnterEvent(self, event):
        """ Method to accept dragging """
        event.accept()    

    def dropEvent(self, event):
        """ Method to accept dropping """
        pos = event.pos()
        button = event.source()
        text = button.text()

        # Verify first a reinsertion in the home_area
        widget = self.home_widget
        if widget.x() < pos.x() < widget.x() + widget.size().width() \
            and widget.y() < pos.y() < widget.y() + widget.size().height():
                self.home_layout.addWidget(button)
                event.accept()
                self.add_dummy_widgets()
                self.drop_action()
                return
        
        for layout in self.single_choice_layouts:
            for i in range(layout.count()):  
                widget = layout.itemAt(i).widget()
                if widget.x() < pos.x() < widget.x() + widget.size().width() \
                    and widget.y() < pos.y() < widget.y() + widget.size().height():
                    layout.removeWidget(widget) 
                    layout.addWidget(button)
                    if isinstance(widget, DragButton):
                        self.home_layout.addWidget(widget)  
                    else:
                        widget.deleteLater()
                    event.accept()
                    self.add_dummy_widgets()
                    self.drop_action()
                    return

        for layout in self.multi_choice_layouts:
            for i in range(layout.count()):  
                widget = layout.itemAt(i).widget()
                if widget.x() < pos.x() < widget.x() + widget.size().width() \
                    and widget.y() < pos.y() < widget.y() + widget.size().height():
                    if not isinstance(widget, DragButton):
                        layout.removeWidget(widget)
                        widget.deleteLater()
                    layout.insertWidget(i - 1, button)
                    event.accept()
                    self.add_dummy_widgets()
                    self.drop_action()
                    return
        event.ignore()   