import cv2 as cv
import numpy as np
import imutils
import warnings 
from pyzbar import pyzbar
from src.config import *

warnings.filterwarnings('ignore') 

"""
ABSTRACTO:
El cálculo del gradiente de Scharr es un método utilizado 
en el procesamiento de imágenes para calcular la magnitud 
del gradiente de una imagen. El gradiente es una medida de 
cómo cambian los niveles de intensidad de píxeles adyacentes 
en una imagen. El operador de Scharr es una variante del 
operador de Sobel, utilizado para calcular derivadas de 
primer orden en direcciones horizontal y vertical.

En resumen, al computar el gradiente de Scharr de una imagen, 
se busca determinar la magnitud de cambio de intensidad en diferentes 
direcciones dentro de la imagen, lo que puede ser útil en tareas 
como la detección de bordes o el realce de ciertas características en la imagen.
"""


def detect_barcode(image) -> list:
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

    ddepth: int = cv.cv.CV_32F if imutils.is_cv2() else cv.CV_32F
    gradX = cv.Sobel(gray, ddepth=ddepth, dx=1, dy=0, ksize=-1)
    gradY = cv.Sobel(gray, ddepth=ddepth, dx=0, dy=1, ksize=-1)
    
    # Se subtrae el gradiente Y del gradiente X
    gradient = cv.subtract(gradX, gradY)
    gradient = cv.convertScaleAbs(gradient)

    # Se hace un blur y se hace un treshold de color
    blurred = cv.blur(gradient, (9, 9))
    (_, thresh) = cv.threshold(blurred, 225, 255, cv.THRESH_BINARY)
    
    # Se contruye un kernel cerrado y se aplica a la imagen con el threshold
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (21, 7))
    closed = cv.morphologyEx(thresh, cv.MORPH_CLOSE, kernel)
    
    # Erosiones y dilataciones
    closed = cv.erode(closed, None, iterations=4)
    closed = cv.dilate(closed, None, iterations=4)
    
    # find the contours in the thresholded image
    cnts = cv.findContours(closed.copy(), cv.RETR_EXTERNAL,
       cv.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    
    # if no contours were found, return None
    if len(cnts) == 0:
       return None
   
    # otherwise, sort the contours by area and compute the rotated
    # bounding box of the largest contour
    c = sorted(cnts, key=cv.contourArea, reverse=True)[0]
    rect = cv.minAreaRect(c)
    box = cv.cv.BoxPoints(rect) if imutils.is_cv2() else cv.boxPoints(rect)
    box = np.int0(box)
    # return the bounding box of the barcode
    return box


class BarcodeReader:
    def __init__(self) -> None:
        camera_port: int | str = CAMERA_CONFIG[0]
        if CAMERA_CONFIG[1] in ["LOCAL_CAMERA_PORT","WLAN_CAMERA_IP", "LOCAL_VIDEO"]:
            self.image_buffer = cv.VideoCapture(camera_port)
        if CAMERA_CONFIG[1] in ["LOCAL_IMAGE"]:            
            self.image_buffer = cv.VideoCapture(camera_port)
            
    def process_buffer(self, run_on_loop: bool = False) -> None:
        while True:
            _, frame = self.image_buffer.read()
    
            # video
            if frame is None:
                break
            
            # detect the barcode in the image
            box = detect_barcode(frame)
            
            # if a barcode was found, draw a bounding box on the frame
            if box is not None:
                cv.drawContours(frame, [box], -1, (0, 255, 0), 2)
                
            # show the frame and record if the user presses a key
            cv.imshow("Frame", frame)
            key = cv.waitKey(1) & 0xFF
            
            # if the 'q' key is pressed, stop the loop
            if key == ord("q"):
                break
            if not run_on_loop: break
            
class BarcodeReaderPyZbar:
    def __init__(self) -> None:
        camera_port: int | str = CAMERA_CONFIG[0]
        if CAMERA_CONFIG[1] in ["LOCAL_CAMERA_PORT","WLAN_CAMERA_IP", "LOCAL_VIDEO"]:
            self.image_buffer = cv.VideoCapture(camera_port)
        if CAMERA_CONFIG[1] in ["LOCAL_IMAGE"]:            
            self.image_buffer = cv.VideoCapture(camera_port)

        self.last_type_detected: str = ""
        self.last_code_detected: str = ""
        
        self.num_frames: int = 60
        
    def process_buffer(self) -> tuple[np.ndarray, str, str]:
        _, frame = self.image_buffer.read()

        barcodes = pyzbar.decode(frame)
        
        for barcode in barcodes:
            # extract the bounding box location of the barcode and draw the
            # bounding box surrounding the barcode on the image
            (x, y, w, h) = barcode.rect
            cv.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            
            # the barcode data is a bytes object so if we want to draw it on
            # our output image we need to convert it to a string first
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type
            
            # draw the barcode data and barcode type on the image
            text = "{} ({})".format(barcodeData, barcodeType)
            cv.putText(frame, text, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 0, 255), 2)
            
            print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))
            if barcodeData != self.last_code_detected:
                self.last_code_detected = barcodeData
        
        cv.putText(frame, str(cv.CAP_PROP_FPS), (30, 30), cv.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 0, 255), 2)
        
        # show the frame and record if the user presses a key
        
        return frame, self.last_code_detected, self.last_type_detected
    
    def run_on_loop(self) -> None:
        while True:
            _, frame = self.image_buffer.read()

            barcodes = pyzbar.decode(frame)
            
            for barcode in barcodes:
                # extract the bounding box location of the barcode and draw the
                # bounding box surrounding the barcode on the image
                (x, y, w, h) = barcode.rect
                cv.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                
                # the barcode data is a bytes object so if we want to draw it on
                # our output image we need to convert it to a string first
                barcodeData = barcode.data.decode("utf-8")
                barcodeType = barcode.type
                
                # draw the barcode data and barcode type on the image
                text = "{} ({})".format(barcodeData, barcodeType)
                cv.putText(frame, text, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 255), 2)
                
                if barcodeData != self.last_code_detected:
                    print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))
                    self.last_code_detected = barcodeData
            
            cv.putText(frame, str(cv.CAP_PROP_FPS), (30, 30), cv.FONT_HERSHEY_SIMPLEX,
                    0.5, (0, 0, 255), 2)
            
            # show the frame and record if the user presses a key
            cv.imshow("Frame", frame)
            key = cv.waitKey(1) & 0xFF
            # if the 'q' key is pressed, stop the loop
            if key == ord("q"):
                break
        cv.destroyAllWindows()
        
    
if __name__ == '__main__':
    reader = BarcodeReaderPyZbar()
    f, _, _ = reader.run_on_loop()
         
    
    
