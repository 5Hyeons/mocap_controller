import os
import sys
import asyncio
import json
import requests
import websockets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer

# API 설정
OBS_WEBSOCKET_URL = "ws://localhost:4455"  # 웹소켓 서버 URL
OBS_PASSWORD = "your_password"  # 설정한 웹소켓 비밀번호
IP_ADDRESS = '127.0.0.1'
PORT = '14053'
API_KEY = '1234'
CLIP_DIR = 'tmp'
BACK_TO_LIVE = False

async def obs_send_command(command, **kwargs):
    async with websockets.connect(OBS_WEBSOCKET_URL) as websocket:
        await websocket.send(json.dumps({
            "op": 6,  # Request type
            "d": {
                "requestType": command,
                "requestData": kwargs
            }
        }))
        response = await websocket.recv()
        return json.loads(response)

def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle('PyQt5 위젯 예제')
    window.setGeometry(100, 100, 200, 100)  # 윈도우 크기 조정

    central_widget = QWidget(window)
    window.setCentralWidget(central_widget)
    
    # 레이아웃 설정
    main_layout = QVBoxLayout()
    central_widget.setLayout(main_layout)
    
    # QLineEdit 위젯 추가
    line_edit = QLineEdit()
    line_edit.setText('Take_1')  # 처음에 'Take 1' 설정
    line_edit.setPlaceholderText('여기에 경로를 입력해주세요.')
    main_layout.addWidget(line_edit)
    
    # 버튼 레이아웃 설정
    button_layout = QHBoxLayout()
    main_layout.addLayout(button_layout)
    
    # 동그라미 버튼 추가
    circle_button = QPushButton('●')
    circle_button.setFixedSize(50, 50)  # 버튼 크기 조정
    circle_button.setStyleSheet("color: black;")  # 처음에는 검정색
    button_layout.addWidget(circle_button)
    
    # 네모 버튼 추가
    square_button = QPushButton('■')
    square_button.setFixedSize(50, 50)  # 버튼 크기 조정
    button_layout.addWidget(square_button)
    
    # 버튼을 양쪽 끝으로 배치하기 위해 공간 추가
    button_layout.addStretch(1)
    button_layout.addWidget(circle_button)
    button_layout.addStretch(1)
    button_layout.addWidget(square_button)
    button_layout.addStretch(1)

    # 타이머 설정
    timer = QTimer(window)
    timer.setInterval(500)  # 500 밀리초마다 타이머 실행

    # 타이머를 시작 및 중지하는 함수
    def start_blinking():
        timer.start()

    def stop_blinking():
        timer.stop()
        circle_button.setStyleSheet("color: black;")  # 깜빡임 멈추고 검정색으로 설정

    # 타이머가 만료될 때 호출되는 함수
    def toggle_button_color():
        current_color = circle_button.styleSheet()
        if "color: red" in current_color:
            circle_button.setStyleSheet("color: black;")
        else:
            circle_button.setStyleSheet("color: red;")

    timer.timeout.connect(toggle_button_color)

    # 네모 버튼 클릭 시 텍스트 박스의 숫자를 증가 및 업데이트
    def increment_take():
        text = line_edit.text()
        try:
            # 마지막 숫자를 추출하고 1 증가
            current_number = int(text.split()[-1])
            new_number = current_number + 1
            line_edit.setText(f'Take_{new_number}')
        except (ValueError, IndexError):
            # 숫자를 찾을 수 없으면 'Take 1'로 초기화
            line_edit.setText('Take_1')
        stop_blinking()  # 네모 버튼 클릭 시 깜빡임 멈추기


    def start_recording():
        start_blinking()
        clip_name = os.path.join(CLIP_DIR, line_edit.text())
        asyncio.run(obs_send_command("StartRecord"))
        url = f"http://{IP_ADDRESS}:{PORT}/v1/{API_KEY}/recording/start"
        data = {
            'filename': clip_name,
            'time': '',  # 필요 시 여기에 타임코드 추가
        }
        response = requests.post(url, json=data)
        print(f"Start recording: {response.status_code}")

    def stop_recording():
        increment_take()
        clip_name = os.path.join(CLIP_DIR, line_edit.text())
        asyncio.run(obs_send_command("StopRecord"))
        url = f"http://{IP_ADDRESS}:{PORT}/v1/{API_KEY}/recording/stop"
        data = {
            'filename': clip_name,
            'time': '',  # 필요 시 여기에 타임코드 추가
            'back_to_live': BACK_TO_LIVE,
        }
        response = requests.post(url, json=data)
        print(f"Stop recording: {response.status_code}")


    # 버튼 클릭 시 타이머 제어 및 녹화 시작/중지
    circle_button.clicked.connect(start_recording)
    square_button.clicked.connect(stop_recording)
    
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()