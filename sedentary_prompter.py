import cv2
import threading
import time
import tkinter as tk
from tkinter import messagebox
from PyQt5.QtWidgets import QApplication, QMessageBox
import sys

# 人脸识别的级联分类器，OpenCV已提供了许多预训练好的XML文件
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# 标记是否检测到人脸
face_detected = False

# 检测到人脸后开始计时的时间戳
start_time = None

# 最后一次检测到人脸的时间戳
last_face_time = None

# 人脸不可见的时间阈值，设置为10秒
face_not_seen_threshold = 10

# 提醒的时间间隔，这里是40分钟转换为秒
reminder_interval = 40 * 60 

remind = False # 初始化是否提醒
app = QApplication(sys.argv)  # 初始化QApplication对象  

# 用于检查是否需要提醒的函数
def check_reminder():
    global face_detected, start_time, remind
    while True:
        if face_detected:
            # 检查是否已经过了提醒的时间间隔
            elapsed_time = time.time() - start_time
            print(f"检测到人脸，已过时间: {elapsed_time}秒")
            if elapsed_time >= reminder_interval:
                # 提醒后重置计时器
                face_detected = False
                remind = True
                print('满足条件，触发提醒')
            else:
                remind  = False
        else:
            remind = False
        time.sleep(60)

# 启动提醒检查线程
reminder_thread = threading.Thread(target=check_reminder)
reminder_thread.daemon = True
reminder_thread.start()

# 使用OpenCV捕获视频
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    if remind:
        # 计算坐了多久（分钟）
        minutes_sitting = round(reminder_interval / 60)
        msgBox = QMessageBox()  # 创建QMessageBox对象
        msgBox.setIcon(QMessageBox.Warning)  # 设置图标类型为警告
        msgBox.setWindowTitle("久坐提醒")  # 设置窗口标题
        msgBox.setText(f"你已经坐了超过{minutes_sitting}分钟，请起身休息一下！")  # 设置显示的文本
        msgBox.show()  # 显示消息框
        remind = False
    
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    if len(faces) > 0:
        # 更新最后一次检测到人脸的时间
        last_face_time = time.time()
        
        if not face_detected:
            print("检测到人脸，开始计时。")
            face_detected = True
            start_time = time.time()
    else:
        # 检查自从最后一次看到人脸以来是否已经过了10秒
        if last_face_time and (time.time() - last_face_time > face_not_seen_threshold):
            if face_detected:
                print(f"人脸不再可见超过{face_not_seen_threshold}秒。")
                face_detected = False

    # 在检测到的每张脸周围画一个矩形（可选）
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

    # 显示结果
    # cv2.imshow('Face Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放摄像头资源并关闭窗口
cap.release()
cv2.destroyAllWindows()
