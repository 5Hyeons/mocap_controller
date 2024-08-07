import os
import sys
import json
import requests
import obsws_python as obs

from PyQt5.QtWidgets import QApplication, QFileDialog, QLineEdit, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QLabel
from PyQt5.QtCore import Qt, QTimer
from pythonosc import udp_client


# API 설정
OBS_WEBSOCKET_PORT = 4455  # 웹소켓 서버 URL
OBS_WEBSOCKET_PASSWORD = "123456"  # 설정한 웹소켓 비밀번호 (사용 안 할 수도 있음)
IP_ADDRESS = '127.0.0.1'
PORT = '14053'
API_KEY = '1234'
# CLIP_DIR = 'tmp'
BACK_TO_LIVE = False

# QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

class CWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.is_recording = False
        self.obs_save_dir_path = None
        # 타이머 설정
        self.timer = QTimer(self)
        self.timer.setInterval(500)  # 500 밀리초마다 타이머 실행
        self.timer.timeout.connect(self.toggle_button_color)
    def initUI(self):
        self.setWindowTitle('Mocap Controller')
        self.setGeometry(100, 100, 400, 100)
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        # QLineEdit 위젯 추가
        self.line_edit = QLineEdit()
        self.line_edit.setText('Take_1')  # 처음에 'Take 1' 설정
        self.line_edit.setPlaceholderText('여기에 경로를 입력해주세요.')
        main_layout.addWidget(self.line_edit)
        
        self.text_button = QPushButton('OBS save path: None')
        self.text_button.clicked.connect(self.set_obs_save_path)
        main_layout.addWidget(self.text_button)

        hbox = QHBoxLayout()
        label = QLabel('Live Link Face IP: ')
        label.setFixedWidth(130)
        hbox.addWidget(label)
        self.osc_ip_line_edit = QLineEdit()
        self.osc_ip_line_edit.setPlaceholderText('여기에 아이폰 IP를 입력해주세요')
        hbox.addWidget(self.osc_ip_line_edit)
        main_layout.addLayout(hbox)

        hbox = QHBoxLayout()
        label = QLabel('Live Link Face PORT: ')
        label.setFixedWidth(130)
        hbox.addWidget(label)
        self.osc_port_line_edit = QLineEdit()
        self.osc_port_line_edit.setPlaceholderText('여기에 PORT를 입력해주세요')
        hbox.addWidget(self.osc_port_line_edit)
        main_layout.addLayout(hbox)

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

    def set_obs_save_path(self):
        self.obs_save_dir_path = QFileDialog.getExistingDirectory(self, 'Select OBS save path')
        if os.name == 'nt':
            self.obs_save_dir_path = self.obs_save_dir_path.replace('/', '\\')
        self.text_button.setText(f'OBS save path: {self.obs_save_dir_path}')

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
        # clip_name = os.path.join(CLIP_DIR, self.line_edit.text())
        clip_name = self.line_edit.text()
        url = f"http://{IP_ADDRESS}:{PORT}/v1/{API_KEY}/recording/start"
        data = {
            'filename': clip_name,
            'time': '',  # 필요 시 여기에 타임코드 추가
        }
        response = requests.post(url, json=data)

    def stop_recording_rokoko(self):
        # clip_name = os.path.join(CLIP_DIR, self.line_edit.text())
        clip_name = self.line_edit.text()
        url = f"http://{IP_ADDRESS}:{PORT}/v1/{API_KEY}/recording/stop"
        data = {
            'filename': clip_name,
            'time': '',  # 필요 시 여기에 타임코드 추가
            'back_to_live': BACK_TO_LIVE,
        }
        response = requests.post(url, json=data)

    def start_recording_obs(self):
        cl = obs.ReqClient(host='localhost', port=OBS_WEBSOCKET_PORT, password=OBS_WEBSOCKET_PASSWORD, timeout=3)
        new_record_dir = os.path.join(self.obs_save_dir_path, self.line_edit.text())
        os.makedirs(new_record_dir, exist_ok=True)
        cl.set_record_directory(new_record_dir)
        print(f'New record directory: {new_record_dir}')
        cl.start_record()
        cl.disconnect()

    def stop_recording_obs(self):
        cl = obs.ReqClient(host='localhost', port=OBS_WEBSOCKET_PORT, password=OBS_WEBSOCKET_PASSWORD, timeout=3)
        cl.stop_record()
        cl.disconnect()

    # 녹화를 시작하는 함수
    def start_recording_livelinkface(self, slate="default_slate", take=1):
        # OSC 클라이언트를 생성합니다.
        osc_ip = self.osc_ip_line_edit.text()
        osc_port = int(self.osc_port_line_edit.text())
        osc_client = udp_client.SimpleUDPClient(osc_ip, osc_port)
        osc_client.send_message("/RecordStart", [slate, take])
        print(f"라이브 링크 페이스 녹화 시작 명령을 보냈습니다. 슬레이트: {slate}, 테이크: {take}")

    # 녹화를 중지하는 함수
    def stop_recording_livelinkface(self):
        # OSC 클라이언트를 생성
        osc_ip = self.osc_ip_line_edit.text()
        osc_port = int(self.osc_port_line_edit.text())
        osc_client = udp_client.SimpleUDPClient(osc_ip, osc_port)
        osc_client.send_message("/RecordStop", 1)
        print("라이브 링크 페이스 녹화 중지 명령을 보냈습니다.")

    def start_recording(self):
        if self.is_recording:
            return
        if self.obs_save_dir_path is None:
            self.display_error_dialog(QMessageBox.Icon.Critical, "OBS Studio 녹화 경로를 설정해주세요.")
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
        # Live Link Face 녹화 시작
        try:
            slate = '_'.join(self.line_edit.text().split('_')[:-1])
            self.start_recording_livelinkface(slate=slate, take=current_number)
        except:
            print("Live Link Face와 연결할 수 없습니다.")

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
        # Live Link Face 녹화 중지
        try:
            self.stop_recording_livelinkface()
        except:
            print("Live Link Face와 연결할 수 없습니다.")
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