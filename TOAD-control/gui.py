from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import (QWidget, QPushButton, QApplication,
                             QHBoxLayout, QVBoxLayout, QGridLayout)
 
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import json
import time

parameters = {
        'power': 'off', 
        'mode': 'Ackermann',
        'forward speed': 0,
        'steering angle': 0,
        'turn speed': 50,
        'turning': False
        }

with open('output.txt', 'w') as json_file:
    json.dump(parameters, json_file, indent = len(parameters))

class Joystick(QWidget):
    value = pyqtSignal(QPointF)
    def __init__(self, parent=None):
        super(Joystick, self).__init__(parent)
        self.setMinimumSize(200, 200)
        self.movingOffset = QPointF(0, 0)
        self.coords = QPointF(0, 0)
        self.grabCenter = False
        self.__maxDistance = 50

    def paintEvent(self, event):
        painter = QPainter(self)
        bounds = QRectF(-self.__maxDistance, -self.__maxDistance, self.__maxDistance * 2, self.__maxDistance * 2).translated(self._center())
        painter.drawEllipse(bounds)
        painter.setBrush(Qt.black)
        painter.drawEllipse(self._centerEllipse())

    def _centerEllipse(self):
        if self.grabCenter:
            return QRectF(-20, -20, 40, 40).translated(self.movingOffset)
        return QRectF(-20, -20, 40, 40).translated(self._center())

    def _center(self):
        return QPointF(self.width()/2, self.height()/2)


    def _boundJoystick(self, point):
        limitLine = QLineF(self._center(), point)
        if (limitLine.length() > self.__maxDistance):
            limitLine.setLength(self.__maxDistance)
        return limitLine.p2()

    def mousePressEvent(self, ev):
        self.grabCenter = self._centerEllipse().contains(ev.pos())
        return super().mousePressEvent(ev)

    def mouseReleaseEvent(self, event):
        self.grabCenter = False
        self.movingOffset = QPointF(0, 0)
        self.coords = QPointF(0, 0)
        self.value.emit(self.coords)
        self.update()

    def mouseMoveEvent(self, event):
        time.sleep(.1)
        if self.grabCenter:
            #print("Moving")
            self.movingOffset = self._boundJoystick(event.pos())
            self.update()
        self.coords = self.movingOffset - self._center()
        #print(self.coords)
        self.value.emit(self.coords)

class PyQtLayout(QWidget):
 
    def __init__(self):
        super().__init__()
        self.UI()

 
    def UI(self):

        def switchMode():
            if combo.currentText() == 'Ackermann':
                joystick.setVisible(True)
                slider_label.setVisible(False)
                slider.setVisible(False)
                turnButton.setVisible(False)
            elif combo.currentText() == 'Turn in Place':
                joystick.setVisible(False)
                slider.setVisible(True)
                slider_label.setVisible(True)
                slider.setValue(50)
                turnButton.setVisible(True)
        

        def json_output():
            parameters['mode'] = combo.currentText()

            if combo.currentText() == 'Ackermann':
                parameters['forward speed'] = int(round(joystick.coords.y() * -2))
                parameters['steering angle'] = int(round(joystick.coords.x() * 0.6))
            elif combo.currentText() == 'Turn in Place':
                parameters['turn speed'] = slider.value()

            if turnButton.isDown():
                parameters['turning'] = True
            else:
                parameters['turning'] = False

            if button.isChecked():
                parameters['power'] = 'on'
                button.setStyleSheet("background-color : green")
            else:
                parameters['power'] = 'off'
                button.setStyleSheet("background-color : red")

            with open('output.txt', 'w') as json_file:
                json.dump(parameters, json_file, indent = len(parameters))
        


        # Turn in Place Button
        turnButton = QPushButton('Hold to Turn')
        turnButton.setVisible(False)
        turnButton.pressed.connect(json_output)
        turnButton.released.connect(json_output)

        # Power Button
        button = QPushButton('Power')
        button.setCheckable(True)
        button.clicked.connect(json_output)
        button.setMaximumWidth(50)
        button.setStyleSheet("background-color : red") 
        
        # Driving Mode Combo Box 
        combo = QtWidgets.QComboBox(self)
        combo.addItems(["Ackermann", "Turn in Place"])
        combo.currentIndexChanged.connect(switchMode)
        combo.currentIndexChanged.connect(json_output)
        
        # Speed Slider
        slider = QtWidgets.QSlider(Qt.Vertical, self)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        slider.setTickInterval(10)
        slider.valueChanged.connect(json_output)
        slider.setVisible(False)

        # Slider label    
        slider_label = QtWidgets.QLabel(self)
        slider_label.setText("Turn\nspeed")
        slider_label.setVisible(False)

        # Joystick
        joystick = Joystick()
        joystick.value.connect(json_output)
        
        # Grid Layout Management 
        vbox = QGridLayout()
        vbox.addWidget(combo, 0, 1)
        vbox.addWidget(slider, 1, 0)
        vbox.addWidget(slider_label, 2, 0)
        vbox.addWidget(button, 2, 2)
        vbox.addWidget(turnButton, 1, 1, 1, 2)
        vbox.addWidget(joystick, 1, 1)

        self.setLayout(vbox)
        self.setGeometry(300, 300, 350, 250)
        self.setWindowTitle('TOAD Controller')

        self.show()

def main():
    app = QApplication(sys.argv)
    ex = PyQtLayout()
    sys.exit(app.exec_())
 
if __name__ == '__main__':
    main()
