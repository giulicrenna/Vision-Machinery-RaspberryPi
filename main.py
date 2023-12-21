from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal
from ui.test import Ui_MainWindow
from src.opencv_engine import *
from src.config import *
from sys import platform
import cv2 as cv
import sys
import qdarkstyle
import os


if platform == "linux" or platform == "linux2":
    os.environ['QT_QPA_PLATFORM'] = 'linuxfb'
elif platform == "win32":
    os.environ['QT_QPA_PLATFORM'] = 'windows'

class WorkerCam1(QThread):
    image_update = pyqtSignal(QImage)
    def run(self):
        self.ThreadActive = True
        
        while self.ThreadActive:
            try:
                reader = BarcodeReaderPyZbar(open_cams[0])
                frame, code, _ = reader.process_buffer()
                image = frame#imutils.resize(frame, width=640)
                frame = cv.cvtColor(image, cv.COLOR_BGR2RGB)
                
                imageComponent = QImage(frame,
                                        frame.shape[1],
                                        frame.shape[0],
                                        frame.strides[0],
                                        QImage.Format_RGB888)
                
                self.image_update.emit(imageComponent)
            except:
                pass
            
    def stop(self):
        self.ThreadActive = False
        self.quit()

class WorkerCam2(QThread):
    image_update = pyqtSignal(QImage)
    
    def run(self):
        self.ThreadActive = True
        
        while self.ThreadActive:
            try:
                reader = BarcodeReaderPyZbar(open_cams[1])
                frame, code, _ = reader.process_buffer()
                image = frame#imutils.resize(frame, width=640)
                frame = cv.cvtColor(image, cv.COLOR_BGR2RGB)
                
                imageComponent = QImage(frame,
                                        frame.shape[1],
                                        frame.shape[0],
                                        frame.strides[0],
                                        QImage.Format_RGB888)
                
                self.image_update.emit(imageComponent)
            except:
                pass
            
    def stop(self):
        self.ThreadActive = False
        self.quit()
        
class WorkerCam3(QThread):
    image_update = pyqtSignal(QImage)
    
    def run(self):
        self.ThreadActive = True
        
        while self.ThreadActive:
            try:
                reader = BarcodeReaderPyZbar(open_cams[2])
                frame, code, _ = reader.process_buffer()
                image = frame#imutils.resize(frame, width=640)
                frame = cv.cvtColor(image, cv.COLOR_BGR2RGB)
                
                imageComponent = QImage(frame,
                                        frame.shape[1],
                                        frame.shape[0],
                                        frame.strides[0],
                                        QImage.Format_RGB888)
                
                self.image_update.emit(imageComponent)
            except:
                pass
            
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
        
        self.update_worker_1 = WorkerCam1()
        self.update_worker_1.start()
        self.update_worker_1.image_update.connect(self.set_picture_cam_1)
        
        self.update_worker_2 = WorkerCam2()
        self.update_worker_2.start()
        self.update_worker_2.image_update.connect(self.set_picture_cam_2)
        
        self.update_worker_3 = WorkerCam3()
        self.update_worker_3.start()
        self.update_worker_3.image_update.connect(self.set_picture_cam_3)
        
        self.window_.pushButton_2.clicked.connect(self.close)   
        
        self.showMaximized()
        
    def set_picture_cam_1(self, imageComponent: QImage) -> None:
        self.window_.label.setPixmap(QPixmap.fromImage(imageComponent))
    
    def set_picture_cam_2(self, imageComponent: QImage) -> None:
        self.window_.label_2.setPixmap(QPixmap.fromImage(imageComponent))
    
    def set_picture_cam_3(self, imageComponent: QImage) -> None:
        self.window_.label_3.setPixmap(QPixmap.fromImage(imageComponent))

    def close(self) -> None:
        sys.exit(0)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
    
