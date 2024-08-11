# Modified based on the forum post by Erwan Leroy with a solution by Mitchel Woodin
# https://community.foundry.com/discuss/topic/145197/contextual-right-click-menu-in-dag

from PySide2 import QtCore, QtGui, QtWidgets, QtOpenGL
import KnobHijacker
import nuke
import threading
import time

class CustomEventFilter(QtCore.QObject):
    def __init__(self):
        super(CustomEventFilter, self).__init__()

        self.install_dag_event_filter()

    def eventFilter(self, widget, event):
        
        if isinstance(widget, QtWidgets.QWidget):
            if event.type() == QtCore.QEvent.MouseButtonPress and event.button() == QtCore.Qt.MouseButton.RightButton:
                
                # Retrieve DAG widget again, otherwise you get Internal C++ object (PySide2.QtOpenGL.QGLWidget) already deleted.
                for widget in QtWidgets.QApplication.allWidgets():
                    if widget.windowTitle() == 'Node Graph':
                        dag = widget.findChild(QtOpenGL.QGLWidget)
                        break

                # Send left click event to select the node
                QtWidgets.QApplication.sendEvent(dag, QtGui.QMouseEvent(QtCore.QEvent.MouseButtonPress,  dag.mapFromGlobal(QtGui.QCursor.pos()), QtCore.Qt.LeftButton, QtCore.Qt.LeftButton, QtCore.Qt.NoModifier))
                QtWidgets.QApplication.sendEvent(dag, QtGui.QMouseEvent(QtCore.QEvent.MouseButtonRelease,  dag.mapFromGlobal(QtGui.QCursor.pos()), QtCore.Qt.LeftButton, QtCore.Qt.LeftButton, QtCore.Qt.NoModifier))

                # Check if a node is selected and trigger hijack
                try:
                    node_context = nuke.selectedNode()
                except ValueError:
                    node_context = None

                if node_context:
                    widget = KnobHijacker.Hijack().run(node_context)
                    widget.show()
                    # Postponing until the RightButtonRelease propagates
                    threading.Thread(target=self.apply_rules, args=(widget,)).start()
                    return True

            # Allow other events to be processed normally
            return False
        
    def apply_rules(self, widget):
        time.sleep(0.05)
        nuke.executeInMainThread(widget.apply_knob_rules, (widget.knob_widget))

    def install_dag_event_filter(self):
        dags = [widget for widget in QtWidgets.QApplication.instance().allWidgets() if widget.windowTitle() == 'Node Graph']
        
        if dags:
            dag = dags[0].findChild(QtOpenGL.QGLWidget)
            if dag:
                dag.installEventFilter(self)
        if not dags or not dag:
            print("Couldn't install Event Filter, DAG not found")

