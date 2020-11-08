#!/usr/bin/exec python3
import sys

import requests

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtWidgets import QWidget

from PyQt5.QtCore import (Qt, QTimer, QFont)
from PyQt5.QtGui import QFont

PORTS = {}

SELECTED_BTN = """QPushButton {
  background-color: rgb(0,80,200);
  border-style: solid;
  border-color: gray;
}"""

class ASInterface(QMainWindow):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.setWindowTitle("Antenna Switch")
    layout = QGridLayout()

    msg = QLabel("W6BSD\nAntenna Switch")
    msg.setFont(QFont("Arial", 18, QFont.Black))
    msg.setStyleSheet("QLabel {background-color: #AA4400;}")
    msg.setFrameStyle(QFrame.Panel)
    msg.setAlignment(Qt.AlignCenter)
    msg.setFixedHeight(80)
    layout.addWidget(msg, 0, 0, 1, 2)

    self.buttons = {}
    for idx, name in PORTS.items():
      self.buttons[idx] = QPushButton(name)
      self.buttons[idx].port_number = idx
      self.buttons[idx].setFixedHeight(50)
      self.buttons[idx].clicked.connect(self.button_clicked)
      layout.addWidget(self.buttons[idx], idx, 0, 1, 2)

    spacer = QSpacerItem(10, 20, QSizePolicy.Minimum | QSizePolicy.MinimumExpanding)
    layout.addItem(spacer)

    qbtn = QPushButton('Quit', self)
    qbtn.clicked.connect(QApplication.instance().quit)
    qbtn.resize(100, 50)

    pos = len(PORTS)
    layout.addWidget(qbtn, pos+2, 1)

    self.statusbar = QStatusBar()
    self.setStatusBar(self.statusbar)
    self.statusbar.showMessage("Inititalization...", 2000)

    widget = QWidget()
    widget.setLayout(layout)
    self.setCentralWidget(widget)

    self.timer = QTimer()
    self.timer.setInterval(100)
    self.timer.timeout.connect(self.checkswitch)
    self.timer.start()

  def checkswitch(self):
    self.timer.setInterval(5000)
    switch = read_switch()
    for idx, port in switch.items():
      idx = int(idx)
      if port['status'] == 1:
        self.buttons[idx].setEnabled(False)
        self.buttons[idx].setStyleSheet(SELECTED_BTN)
      else:
        self.buttons[idx].setEnabled(True)
        self.buttons[idx].setStyleSheet("")

  def button_clicked(self):
    sender = self.sender()
    idx = sender.port_number

    self.statusbar.showMessage(sender.text() + ' selected', 2000)
    try:
      select_antenna(idx)
    except SystemError as err:
      self.statusbar.showMessage(err.args[0])
      return

    for btn in self.buttons:
      self.buttons[btn].setEnabled(True)
      self.buttons[btn].setStyleSheet("")

    sender.setEnabled(False)
    sender.setStyleSheet(SELECTED_BTN)


def select_antenna(idx):
  url = f'http://aswitch.home:8088/api/v1/select/{idx}'
  try:
    response = requests.get(url)
    response.raise_for_status()
  except requests.HTTPError as http_err:
    raise SystemError(f'HTTP error: {http_err}') from http_err
  except Exception as err:
    raise SystemError(f'Other error: {err}') from err

  data = response.json()
  if data['status'] == 'ERROR':
    raise SystemError(data['msg'])

  return response.json()


def read_switch():
  url = 'http://aswitch.home:8088/api/v1/ports'
  try:
    response = requests.get(url)
    response.raise_for_status()
  except requests.HTTPError as http_err:
    raise SystemError(f'HTTP error: {http_err}') from http_err
  except Exception as err:
    raise SystemError(f'Other error: {err}') from err

  return response.json()

def main():
  global PORTS
  try:
    switch = read_switch()
    for key, port in sorted(switch.items()):
      PORTS[int(key)] = port['label']
  except SystemError as err:
    print(err)
    sys.exit(1)

  app = QApplication(sys.argv)
  view = ASInterface()
  view.show()
  sys.exit(app.exec_())

if __name__ == '__main__':
  main()
