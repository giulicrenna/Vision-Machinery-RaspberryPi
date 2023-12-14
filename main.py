from PyQt5.QtWidgets import QApplication, QDialog, QTableWidgetItem, QMessageBox, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import QtGui
from ui.test import Ui_MainWindow
from src.opencv_engine import *
import cv2 as cv
import imutils
import sys
import qdarkstyle
import os

os.environ['QT_QPA_PLATFORM'] = 'windows'
#'linuxfb' 'windows'

reader = BarcodeReaderPyZbar()

class Worker(QThread):
    image_update = pyqtSignal(QImage)
    
    def run(self):
        self.ThreadActive = True
        
        while self.ThreadActive:
            frame, code, _ = reader.process_buffer()
            image = frame#imutils.resize(frame, width=640)
            frame = cv.cvtColor(image, cv.COLOR_BGR2RGB)
            
            imageComponent = QImage(frame,
                                    frame.shape[1],
                                    frame.shape[0],
                                    frame.strides[0],
                                    QImage.Format_RGB888)
            
            self.image_update.emit(imageComponent)
            
    def stop(self):
        self.ThreadActive = False
        self.quit()
        
class Window(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.window_ = Ui_MainWindow()
        self.window_.setupUi(self)
        
        self.setWindowTitle("Test")
        #self.setWindowIcon(QtGui.QIcon('static/icon.png'))
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        
        self.update_worker = Worker()
        self.update_worker.start()
        self.update_worker.image_update.connect(self.set_picture)
        
        self.window_.pushButton_2.clicked.connect(self.close)   
                
    def set_picture(self, imageComponent: QImage) -> None:
        self.window_.label.setPixmap(QPixmap.fromImage(imageComponent))

    def close(self) -> None:
        ...
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
    
