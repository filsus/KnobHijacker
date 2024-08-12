from PySide2 import QtWidgets, QtGui, QtCore
import threading
import nuke
import os
import json

class Hijack(QtWidgets.QWidget):
    def __init__(self):
        super(Hijack, self).__init__()
        self.node = None
        self.knob_widget = None

        self.setMinimumWidth(400)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Popup | QtCore.Qt.NoDropShadowWindowHint)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.keyPressEvent = self.keyPressEvent
    
    # Make QButton widgets executable by pressing Enter
    def keyPressEvent(self,event):
        if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
            widget = self.layout.itemAt(0).widget()
            try:
                widget.click()
            except:
                pass
    
    def find_properties_widget_recursive(self, screen_points):
        properties_panels = []

        def resursive(widget):
            # Check if the current widget's name contains "Properties"
            if widget.objectName() and "Properties" in widget.objectName():
                return widget

            # Recursively search in the parent widget
            parent_widget = widget.parentWidget()
            if parent_widget:
                return resursive(parent_widget)
            
        for p in screen_points:
            widget = QtWidgets.QApplication.instance().widgetAt(p)
            if widget != None:
                panel = resursive(widget)
                properties_panels.append(panel)

        return properties_panels
    
   
    def get_open_properties_panels(self):
        # Get information about all screens
        screens = QtWidgets.QApplication.screens()
        # Create a list to store the screen points
        screen_points = []

        for screen in screens:
            screen_geometry = screen.geometry()

            screen_width, screen_height = screen_geometry.width(), screen_geometry.height()

            # Set up the 16x16 grid
            rows, cols = 16, 16

            # Calculate the grid points for the current screen
            for row in range(rows):
                for col in range(cols):
                    # Calculate the corresponding points based on simple math
                    x = col * (screen_width // cols) + 20 + screen_geometry.left()
                    y = row * (screen_height // rows) + screen_geometry.top()

                    # Append QPoint to the list
                    screen_points.append(QtCore.QPoint(x, y))

        # Pass the screen_points list to your function
        return nuke.executeInMainThreadWithResult(self.find_properties_widget_recursive, (screen_points))

    def apply_knob_rules(self, knob_widget):
        if isinstance(knob_widget, QtWidgets.QComboBox):
                knob_widget.currentTextChanged.connect(self.close)
                knob_widget.showPopup()

        elif isinstance(knob_widget, QtWidgets.QToolButton):
            knob_widget.triggered.connect(self.close)
            knob_widget.showMenu()
            
        elif len(knob_widget.children()) > 0:
            knob = self.knob_widget.children()[1].children()[2]
            if isinstance(knob, QtWidgets.QLineEdit):
                knob.setFocus()
                knob.selectAll()
                knob.returnPressed.connect(self.close)

    def refresh_control_panel_hijacked(self):
        def _showPanel():
            nuke.executeInMainThread(self.node.showControlPanel, ())

        self.node.hideControlPanel()
        threading.Thread(target=_showPanel).start()
    
    def closeEvent(self, event):
        self.refresh_control_panel_hijacked()
        self.layout.removeWidget(self.knob_widget)
        self.knob_widget.deleteLater()
        event.accept()
        
    def get_widget_tooltip(self,knob_name):
        knob_tooltip = self.node[knob_name].tooltip()
        if knob_tooltip == "":
            widget_tooltip = f"<b>{knob_name}</b>"
        else:
            html_tooltip = knob_tooltip.replace('>', '&gt;').replace('<', "&lt;").replace('\n', '<br>').replace('\t', '	').replace('<br><br>', '<p>')
            widget_tooltip = f"<b>{knob_name}</b><br>{html_tooltip}"

        return widget_tooltip
        
    def find_child_with_tooltip(self, parent_widget, tooltip):
        # For color knob only like in Grade or ColorCorrection
        color_child = parent_widget.findChild(QtWidgets.QLineEdit, "ColorKnobDoubleSpinBox")
        color_panel = None
        if color_child:
            color_panel = color_child.parent().parent().parent()

        if color_panel:
            children = color_panel.children()
            for child in children:
                try:
                    child_tooltip = child.toolTip()
                    if child_tooltip == tooltip:
                        return child
                except:
                    pass

        # For generic knobs
        for child in parent_widget.children():
            if "toolTip" in dir(child):
                if child.toolTip() == tooltip:
                    
                    return child
                
                found_child = self.find_child_with_tooltip(child, tooltip)
                if found_child:
                    return found_child
        return None 
    
    def get_nodes_property_panel(self, panels):
        filtered_list = [value for value in panels if value is not None]
        node_properties = filtered_list[0]
        return node_properties
    
    def show_knob_selection_dialog(self):

        # Create a dialog
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("Choose a knob to hijack.")
        dialog.setMinimumWidth(400)
        # Create a layout
        layout = QtWidgets.QVBoxLayout()

        # Create a combo box and populate it with knob names
        knob_combo_box = QtWidgets.QComboBox()
        knob_combo_box.addItems([knob for knob in self.node.knobs()])
        layout.addWidget(knob_combo_box)

        # Create OK and Cancel buttons
        ok_button = QtWidgets.QPushButton("OK")
        cancel_button = QtWidgets.QPushButton("Cancel")
        layout.addWidget(ok_button)
        layout.addWidget(cancel_button)

        # Connect button actions
        def ok_clicked():
            selected_knob_name = knob_combo_box.currentText()
            dialog.accept()

        def cancel_clicked():
            dialog.reject()
        
        ok_button.clicked.connect(ok_clicked)
        cancel_button.clicked.connect(cancel_clicked)

        # Set the layout for the dialog
        dialog.setLayout(layout)
        
        # Show the dialog and wait for user input
        result = dialog.exec_()

        # Return the selected knob name if OK was clicked, otherwise return None
        if result == QtWidgets.QDialog.Accepted:
            return knob_combo_box.currentText()
        else:
            return None
        
    def load_knob_to_hijack(self):
        user_nuke_dir = os.path.join(os.path.expanduser("~"), ".nuke")
        file_path = os.path.join(user_nuke_dir, "Hijacker_settings.json")

        try:
            # Try to open the file in read mode
            with open(file_path, 'r') as file:
                # If the file exists, read and return its content
                settings_data = json.load(file)

            if self.node.Class() in settings_data.keys():
                knob_name = settings_data[self.node.Class()]
                return knob_name
            
            else:
                knob_name = self.show_knob_selection_dialog()
                if knob_name != None:
                    settings_data[self.node.Class()] = knob_name
                    with open(file_path, 'w') as file:
                        json.dump(settings_data, file, indent=2)

                return knob_name

        except FileNotFoundError:
            # If the file doesn't exist, create it with default settings
            settings_data = {}
            knob_name = self.show_knob_selection_dialog()
            if knob_name != None:
                settings_data[self.node.Class()] = knob_name

                with open(file_path, 'w') as file:
                    json.dump(settings_data, file, indent=2)

            return settings_data[self.node.Class()]

    def run(self, node):
        self.node = node
        # Load knob name from json file, if it does not exist ask user to select one
        knob_name = self.load_knob_to_hijack()
        if knob_name != None:
            tooltip = self.get_widget_tooltip(knob_name) 

            # Force open properties panel for selected node and retrieve the widget that holds it
            self.node.showControlPanel()
            properties_panels = self.get_open_properties_panels()
            properties_panel = self.get_nodes_property_panel(properties_panels)
            
            if properties_panel != None:
                # Use the nuke.Knob tooltip to find the child widget bearing the same tooltip                                
                self.knob_widget = self.find_child_with_tooltip(properties_panel, tooltip) 
                
                if self.knob_widget != None:
                    self.layout.addWidget(self.knob_widget)

                    # Move the widget to cursor location
                    cursor = QtGui.QCursor.pos() 
                    self.move(QtCore.QPoint(cursor.x()-60, cursor.y()+20))

                else:
                    nuke.message("Could not find the widget for selected Node. Please report the the developers.")
                
        return self