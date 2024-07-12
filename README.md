## Mocap Controller

### Overview

Mocap Controller is a simple application designed to facilitate the simultaneous recording of motion capture data using Rokoko Studio and video recording using OBS Studio. The application allows users to set the OBS Studio save path, create a new folder based on the provided name, and ensure synchronized start and stop recording for both Rokoko Studio and OBS Studio.

### Features

- **Set OBS Save Path**: Choose the directory where OBS Studio will save recordings.
- **Create Folder with Custom Name**: Create a new folder with a user-defined name to store OBS recordings.
- **Simultaneous Recording**: Start and stop recordings in `Rokoko Studio` and `OBS Studio` with a single click.
- **User-friendly Interface**: Simple and intuitive GUI for easy operation.

### Interface

- **Text Editor**: Enter the desired name for the new folder where OBS recordings will be saved.
- **OBS Save Path Button**: Opens a dialog to set the save path for OBS Studio recordings.
- **Start Recording Button (Circle)**: Starts recording in both Rokoko Studio and OBS Studio simultaneously.
- **Stop Recording Button (Square)**: Stops recording in both Rokoko Studio and OBS Studio simultaneously.

### How to Use

1. **Set the Save Path**:
   - Click the `OBS save path` button to open a file dialog.
   - Select the directory where you want OBS Studio to save recordings.
   - The selected path will be displayed below the button.

2. **Create New Folder**:
   - Enter the desired name for the new folder in the text editor (e.g., `Take_1`).
   - When you start recording, a new folder with this name will be created in the selected save path.

3. **Start Recording**:
   - Click the circle button to start recording in both Rokoko Studio and OBS Studio simultaneously.
   - Ensure both programs are set up and ready to record before clicking the button.

4. **Stop Recording**:
   - Click the square button to stop recording in both Rokoko Studio and OBS Studio simultaneously.

### Requirements

- **OBS Studio**: Must be installed and set up with OBS WebSocket plugin.
- **Rokoko Studio**: Must be installed and configured for motion capture.
- **obsws_python**: Python library for interacting with OBS WebSocket API.
- **PyQt5**: Python library for creating the graphical user interface.

### Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the Application**:
    ```bash
    python main.py
    ```

### Notes
- Ensure OBS Studio is running and the WebSocket server is enabled before starting the application.
- Set the OBS WebSocket port as **4455** and password is **123456** or **disable** in `Tools > WebSocket Server Settings`