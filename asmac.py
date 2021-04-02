#!/usr/bin/env python3.7
import argparse
import logging
import sys
import time

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

from PyQt5.QtCore import (Qt, QTimer)
from PyQt5.QtGui import QFont

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%c',
                    level=logging.INFO)

PORTS = {}

URL = "http://192.168.10.180:8088"
URL = "http://aswitch.home:8088"

SELECTED_BTN = """QPushButton {
  background-color: rgb(0,80,200);
  border-style: solid;
  border-color: gray;
}"""

TITLE_STYLE = """QLabel {
  background-color: #262626;
  border-width: 2px;
  border-color: darkgray;
  border-style: solid; /* just a single line */
  border-radius: 3px; /* same radius as the QComboBox */
}"""


class ASInterface(QMainWindow):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.setWindowTitle("MacSwitch")
    layout = QGridLayout()

    title = QLabel("W6BSD\nAntenna Switch")
    title.setFont(QFont("Arial", 18, QFont.Black))
    title.setStyleSheet(TITLE_STYLE)
    title.setFrameStyle(QFrame.Panel)
    title.setAlignment(Qt.AlignCenter)
    title.setFixedHeight(60)
    layout.addWidget(title, 0, 0, 1, 2)

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
    qbtn.clicked.connect(self.quit)
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

  def quit(self):
    logging.info('bye bye')
    QApplication.quit()

  def checkswitch(self):
    self.timer.setInterval(5000)
    try:
      switch = read_switch()
    except IOError as err:
      self.statusbar.showMessage("Connection Error", 2000)
      return
    except SystemError as err:
      self.statusbar.showMessage("HTTP Error", 2000)
      logging.error(err)
      return

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

    try:
      reply = select_antenna(idx)
      if reply['status'] != 'OK':
        raise SystemError(reply['msg'])
    except SystemError as err:
      logging.warning(err.args[0])
      self.statusbar.showMessage(err.args[0])
      return

    for btn in self.buttons:
      self.buttons[btn].setEnabled(True)
      self.buttons[btn].setStyleSheet("")

    sender.setEnabled(False)
    sender.setStyleSheet(SELECTED_BTN)
    self.statusbar.showMessage(reply['msg'], 5000)


def select_antenna(idx):
  url = '{}/api/v1/select/{}'.format(URL, idx)
  try:
    response = requests.get(url)
    response.raise_for_status()
  except requests.HTTPError as http_err:
    raise SystemError(f'HTTP error: {http_err}') from http_err
  except Exception as err:
    raise SystemError(f'Other error: {err}') from err

  data = response.json()
  if data['status'] == 'ERROR':
    logging.error(data['msg'])
    raise SystemError(data['msg'])

  return response.json()


def read_switch(timeout=2):
  url = '{}/api/v1/ports'.format(URL)
  try:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
  except requests.ConnectionError as err:
    raise IOError('Connection Error')
  except requests.HTTPError as err:
    raise SystemError(f'HTTP error: {http_err}')
  except Exception as err:
    raise SystemError(f'Other error: {err}')

  return response.json()

def main():
  global PORTS
  global URL

  parser = argparse.ArgumentParser(
    description="Remote control for the Wireless Antenna Switch",
  )
  parser.add_argument("--url", type=str, default=URL,
                      help="Switch's URL [default: %(default)s]")
  opts = parser.parse_args()
  if opts.url:
    URL = opts.url

  while True:
    try:
      switch = read_switch()
    except IOError as err:
      logging.error(err)
      logging.info('Waiting for the switch to be turned on')
      time.sleep(10)
    except SystemError as err:
      logging.error(err)
      sys.exit()
    else:
      logging.info('Connected...')
      break

  logging.info('Inititalizing...')
  logging.info('Reading swtich configuration...')
  for key, port in sorted(switch.items()):
    PORTS[int(key)] = port['label']
    status = 'Selected' if port['status'] else 'Ready'
    logging.info('Port: "{}" {}'.format(port['label'], status))
  logging.info('{:d} Ports found'.format(len(PORTS)))

  app = QApplication(sys.argv)
  view = ASInterface()
  view.show()
  sys.exit(app.exec_())

if __name__ == '__main__':
  main()
