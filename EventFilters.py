# Modified based on the forum post by Erwan Leroy with a solution by Mitchel Woodin
# https://community.foundry.com/discuss/topic/145197/contextual-right-click-menu-in-dag

from PySide2 import QtCore, QtGui, QtWidgets, QtOpenGL
import KnobHijacker
import nuke

class CustomEventFilter(QtCore.QObject):
    def __init__(self):
        super(CustomEventFilter, self).__init__()

        # Keep reference to the parent widget otherwise garbage collection deletes the dag reference
        self.dag_parent = next((widget for widget in QtWidgets.QApplication.instance().allWidgets() if isinstance(widget, QtWidgets.QWidget) and 'DAG' in widget.objectName()), None)
        if self.dag_parent:
            self.dag = self.dag_parent.findChild(QtOpenGL.QGLWidget)
            self.dag.installEventFilter(self)

    def eventFilter(self, widget, event):
        if event.type() == QtCore.QEvent.MouseButtonPress and event.button() == QtCore.Qt.MouseButton.RightButton:
            
            # Send left click event to select the node
            if self.dag_parent:
                QtWidgets.QApplication.sendEvent(self.dag, 
                                                 QtGui.QMouseEvent(QtCore.QEvent.MouseButtonPress, 
                                                                   self.dag.mapFromGlobal(QtGui.QCursor.pos()), 
                                                                   QtCore.Qt.LeftButton, QtCore.Qt.LeftButton,
                                                                     QtCore.Qt.NoModifier))

            # Check if a node is selected else propagate as default
            selected_node = self.check_selected()
            
            if selected_node:
                # Delay the hijack to allow button release to process, 
                # else the buton release event will act on our widget, effectively spawning a menu
                hijacker = KnobHijacker.Hijack()
                QtCore.QTimer.singleShot(125, lambda:hijacker.run(selected_node))
                return True

        # Allow other events to be processed normally
        return False
    
    def check_selected(self):
        # Make sure the fake left-click has propagated
        QtCore.QCoreApplication.processEvents()

        try:
            node = nuke.selectedNode()
            return node
        except ValueError:
            return None
