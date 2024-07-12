import os
import sys
import json
import requests
import obsws_python as obs
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt, QTimer
# API 설정
OBS_WEBSOCKET_PORT = 4455  # 웹소켓 서버 URL
OBS_WEBSOCKET_PASSWORD = "123456"  # 설정한 웹소켓 비밀번호
IP_ADDRESS = '127.0.0.1'
PORT = '14053'
API_KEY = '1234'
CLIP_DIR = 'tmp'
BACK_TO_LIVE = False
# QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
class CWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.is_recording = False
        # 타이머 설정
        self.timer = QTimer(self)
        self.timer.setInterval(500)  # 500 밀리초마다 타이머 실행
        self.timer.timeout.connect(self.toggle_button_color)
        # OBS Studio 연결
    def initUI(self):
        self.setWindowTitle('Mocap Controller')
        self.setGeometry(100, 100, 200, 100)
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        # QLineEdit 위젯 추가
        self.line_edit = QLineEdit()
        self.line_edit.setText('Take_1')  # 처음에 'Take 1' 설정
        self.line_edit.setPlaceholderText('여기에 경로를 입력해주세요.')
        main_layout.addWidget(self.line_edit)
        # 버튼 레이아웃 설정
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)
        # 동그라미 버튼 추가
        self.circle_button = QPushButton('●')
        self.circle_button.setFixedSize(50, 50)  # 버튼 크기 조정
        self.circle_button.setStyleSheet("color: black;")  # 처음에는 검정색
        button_layout.addWidget(self.circle_button)
        self.circle_button.clicked.connect(self.start_recording)
        # 네모 버튼 추가
        self.square_button = QPushButton('■')
        self.square_button.setFixedSize(50, 50)  # 버튼 크기 조정
        self.square_button.clicked.connect(self.stop_recording)
        button_layout.addWidget(self.square_button)
        # 버튼을 양쪽 끝으로 배치하기 위해 공간 추가
        button_layout.addStretch(1)
        button_layout.addWidget(self.circle_button)
        button_layout.addStretch(1)
        button_layout.addWidget(self.square_button)
        button_layout.addStretch(1)
        self.show()
    # 타이머를 시작 및 중지하는 함수
    def start_blinking(self):
        self.timer.start()
    def stop_blinking(self):
        self.timer.stop()
        self.circle_button.setStyleSheet("color: black;")  # 깜빡임 멈추고 검정색으로 설정
    # 타이머가 만료될 때 호출되는 함수
    def toggle_button_color(self):
        current_color = self.circle_button.styleSheet()
        if "color: red" in current_color:
            self.circle_button.setStyleSheet("color: black;")
        else:
            self.circle_button.setStyleSheet("color: red;")
    # 네모 버튼 클릭 시 텍스트 박스의 숫자를 증가 및 업데이트
    def increment_take(self):
        text = self.line_edit.text()
        # 마지막 숫자를 추출하고 1 증가
        text_split = text.split('_')
        current_number = int(text_split[-1])
        text_split[-1] = str(current_number + 1)
        text_increment = '_'.join(text_split)
        self.line_edit.setText(text_increment)
        self.stop_blinking()  # 네모 버튼 클릭 시 깜빡임 멈추기
    def start_recording_rokoko(self):
        clip_name = os.path.join(CLIP_DIR, self.line_edit.text())
        url = f"http://{IP_ADDRESS}:{PORT}/v1/{API_KEY}/recording/start"
        data = {
            'filename': clip_name,
            'time': '',  # 필요 시 여기에 타임코드 추가
        }
        response = requests.post(url, json=data)
    def stop_recording_rokoko(self):
        clip_name = os.path.join(CLIP_DIR, self.line_edit.text())
        url = f"http://{IP_ADDRESS}:{PORT}/v1/{API_KEY}/recording/stop"
        data = {
            'filename': clip_name,
            'time': '',  # 필요 시 여기에 타임코드 추가
            'back_to_live': BACK_TO_LIVE,
        }
        response = requests.post(url, json=data)
    def start_recording_obs(self):
        cl = obs.ReqClient(host='localhost', port=OBS_WEBSOCKET_PORT, password=OBS_WEBSOCKET_PASSWORD, timeout=3)
        cl.start_record()
        cl.disconnect()
    def stop_recording_obs(self):
        cl = obs.ReqClient(host='localhost', port=OBS_WEBSOCKET_PORT, password=OBS_WEBSOCKET_PASSWORD, timeout=3)
        cl.stop_record()
        cl.disconnect()
    def start_recording(self):
        if self.is_recording:
            return
        try:
            current_number = int(self.line_edit.text().split('_')[-1])
        except (ValueError, IndexError):
            self.display_error_dialog(QMessageBox.Warning, "파일명의 형식이 잘못되었습니다. '_숫자' 형식으로 입력해주세요.")
            return
        # Rokoko Studio 녹화 시작
        try:
            self.start_recording_rokoko()
        except requests.exceptions.ConnectionError:
            self.display_error_dialog(QMessageBox.Icon.Critical, "Rokoko Studio와 연결할 수 없습니다. Rokoko Studio가 실행 중인지 확인해주세요.")
            return
        # OBS Studio 녹화 시작
        try:
            self.start_recording_obs()
        except ConnectionRefusedError:
            self.display_error_dialog(QMessageBox.Icon.Critical, "OBS Studio와 연결할 수 없습니다. OBS Studio가 실행 중인지 확인해주세요.")
            self.stop_recording_rokoko()
            return
        self.is_recording = True
        self.start_blinking()
        self.line_edit.setEnabled(False)
    def stop_recording(self):
        if not self.is_recording:
            return
        # Rokoko Studio 녹화 중지
        try:
            self.stop_recording_rokoko()
        except requests.exceptions.ConnectionError:
            self.display_error_dialog(QMessageBox.Icon.Critical, "Rokoko Studio와 연결할 수 없습니다. Rokoko Studio가 실행 중인지 확인해주세요.")
        # OBS Studio 녹화 중지
        try:
            self.stop_recording_obs()
        except ConnectionRefusedError:
            self.display_error_dialog(QMessageBox.Icon.Critical, "OBS Studio와 연결할 수 없습니다. OBS Studio가 실행 중인지 확인해주세요.")
        self.is_recording = False
        self.increment_take()
        self.line_edit.setEnabled(True)
    def display_error_dialog(self, type, message):
        error_dialog = QMessageBox(self)
        error_dialog.setMaximumSize(200, 100)
        error_dialog.setIcon(type)
        error_dialog.setWindowTitle("Error")
        error_dialog.setText(message)
        error_dialog.exec_()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = CWidget()
    sys.exit(app.exec_())