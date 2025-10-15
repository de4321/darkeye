from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel
import cv2
import numpy as np
from pathlib import Path

def detect_and_mark_faces(image_path: str | Path, min_size: tuple = (30, 30)) -> QPixmap:
    """
    检测图片中的人脸并在人脸位置绘制矩形框，返回适合QLabel显示的QPixmap
    
    参数:
        image_path: 图片路径(str或Path对象)
        min_size: 最小人脸检测尺寸(宽,高)，单位像素
        
    返回:
        QPixmap: 带人脸框的图像，可直接用QLabel.setPixmap()显示
    """
    # 加载预训练模型
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    #face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
    
    # 读取图片
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"无法读取图片: {image_path}")
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 检测人脸
    faces = face_cascade.detectMultiScale(
        gray, 
        scaleFactor=1.1,
        minNeighbors=6,
        minSize=min_size,
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    # 绘制最大的人脸框
    if len(faces) > 0:
        faces = sorted(faces, key=lambda x: x[2]*x[3], reverse=True)
        x, y, w, h = faces[0]
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    # 将OpenCV图像转换为QPixmap
    height, width, channel = img.shape
    bytes_per_line = 3 * width
    q_img = QImage(img.data, width, height, bytes_per_line, QImage.Format_BGR888)
    pixmap = QPixmap.fromImage(q_img)
    
    return pixmap


