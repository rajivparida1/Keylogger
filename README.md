# Keylogger Project

This is a Python-based keylogger application that captures keyboard inputs. The project includes a basic graphical interface with images and a password-protected mechanism.

**Important Note:** This project is for educational purposes only. Using this software in any malicious or unauthorized manner is strictly prohibited.

## Features:
- Keylogging functionality
- Simple graphical interface
- Background images and audio

## Prerequisites

Before running the project, make sure you have Python installed. You also need to install the required libraries:

1. **Install Python**: [Download Python](https://www.python.org/downloads/)

2. **Install Required Libraries**:

   Run the following command to install dependencies:

   ```bash
   pip install -r requirements.txt

How to Build the Executable
If you want to build the .exe yourself using PyInstaller:

1) Install PyInstaller:
     pip install pyinstaller
2) In the terminal, navigate to the folder where your keylogger.py is located and run:
     python -m PyInstaller --onefile --noconsole ^
    --upx-dir C:\upx ^
    --add-data "background.jpg;." ^
    --add-data "anatomy.png;." ^
    --add-data "nail-pin.png;." ^
    --add-data "skull.png;." ^
    --add-data "loader.gif;." ^
    --add-data "loading.wav;." ^
    --add-data "password.txt;." ^
    --icon=icon.ico ^
    keylogger.py
  This will generate the keylogger.exe file in the dist folder.

Running the Executable
Once the .exe is built, you can run the keylogger.exe directly. The password is stored in the password.txt file.

                                    OR 

## 🔗 Download Executable

You can download the file directly from Google Drive:

[📥 Download keylogger.exe]
([https://drive.google.com/your-shared-link-here](https://drive.google.com/drive/folders/1eUFX-OiuKtKUhrbVuqXkfcKWO5CHfSJi?usp=sharing))


Important Warning: Use this application responsibly. It is crucial to obtain proper consent before monitoring or recording someone's activity.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Disclaimer
This is an educational project. Do not use this software for malicious purposes. Always respect privacy and ethical guidelines.



