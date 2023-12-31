from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from ui.window import Ui_MainWindow
from src.opencv_engine import *
from src.config import *
from sys import platform
import cv2 as cv
import sys
import qdarkstyle
import os
import time

if platform == "linux" or platform == "linux2":
    os.environ['QT_QPA_PLATFORM'] = 'linuxfb'
elif platform == "win32":
    os.environ['QT_QPA_PLATFORM'] = 'windows'


CAMERA_1: int | str = 0
CAMERA_2: int | str = open_cams[0]

ARUCO_ID_1: int = -1
ARUCO_ID_2: int = -1

class WorkerCam1(QThread):
    image_update = pyqtSignal(QImage)
    def run(self):
        self.ThreadActive = True
        global ARUCO_ID_1
        reader = ArucoReader(CAMERA_1)
        
        while self.ThreadActive:
            try:
                image, code = reader.aruco_proccesor()
                image = imutils.resize(image, width=640)
                frame = cv.cvtColor(image, cv.COLOR_BGR2RGB)
                
                try: ARUCO_ID_1 = code[0][0]
                except: pass
                
                imageComponent = QImage(frame,
                                        frame.shape[1],
                                        frame.shape[0],
                                        frame.strides[0],
                                        QImage.Format_RGB888)
                
                self.image_update.emit(imageComponent)
            except:
                pass
            time.sleep(0.1)
            
    def stop(self):
        self.ThreadActive = False
        self.quit()

class WorkerCam2(QThread):
    image_update = pyqtSignal(QImage)
    
    def run(self):
        self.ThreadActive = True
        global ARUCO_ID_2
        reader = ArucoReader(CAMERA_2)
        
        while self.ThreadActive:
            try:
                image, code = reader.aruco_proccesor()
                image = imutils.resize(image, width=640)
                frame = cv.cvtColor(image, cv.COLOR_BGR2RGB)
                
                try: ARUCO_ID_2 = code[0][0] 
                except: pass
                
                imageComponent = QImage(frame,
                                        frame.shape[1],
                                        frame.shape[0],
                                        frame.strides[0],
                                        QImage.Format_RGB888)
                
                self.image_update.emit(imageComponent)
            except:
                pass
            time.sleep(0.1)
            
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
        
        self.window_.salir.clicked.connect(self.close)   
        
        timer = QTimer(self)
        timer.timeout.connect(self.update_ids)
        timer.start(100)
        
        self.showMaximized()
        
    def set_picture_cam_1(self, imageComponent: QImage) -> None:
        self.window_.cam_1.setPixmap(QPixmap.fromImage(imageComponent))
    
    def set_picture_cam_2(self, imageComponent: QImage) -> None:
        self.window_.cam_2.setPixmap(QPixmap.fromImage(imageComponent))

    def update_ids(self) -> None:
        self.window_.id_0.setText(f'<html><head/><body><p align="center"><span style=" font-weight:600;">ID: {ARUCO_ID_1}</span></p></body></html>')
        self.window_.id_1.setText(f'<html><head/><body><p align="center"><span style=" font-weight:600;">ID: {ARUCO_ID_2}</span></p></body></html>')
    
    def close(self) -> None:
        sys.exit(0)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
    
