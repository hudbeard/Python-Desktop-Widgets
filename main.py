import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, QVBoxLayout, QSlider, QStackedLayout, QFrame
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer
import pyautogui
import winreg
from get_volume import GetVolume
from get_weather import Weather


def is_dark_mode_enabled():
    registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
    reg_keypath = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize'
    reg_key = winreg.OpenKey(registry, reg_keypath)

    for i in range(1024):
        value_name, value, _ = winreg.EnumValue(reg_key, i)
        if value_name == 'AppsUseLightTheme':
            return value == 0
    return False


class Layout(QWidget):
    def __init__(self, widgets):
        super().__init__()

        self.BLANK = 0
        self.labels = {}
        self.layouts = []
        self.dark_mode = is_dark_mode_enabled()

        self.screen_width, self.screen_height = pyautogui.size()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnBottomHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet("color: white;" if self.dark_mode else "color: black;")

        self.setGeometry(self.screen_width - 460, 0, 460, self.screen_height)
        self.general_layout = QVBoxLayout()
        self.general_layout.setSpacing(15)
        self.general_layout.setContentsMargins(15, 15, 15, 15)

        self.setLayout(self.general_layout)
        self.weather = Weather()
        self.volume = GetVolume()
        self.make_widgets(widgets)
        self.general_layout.addStretch()

        self.show()

    def make_widgets(self, widgets_layout):
        widget_functions = {
            0: (self.weather_widget, self.update_weather_widget),
            1: (self.volume_widget, self.update_default_widget),
            2: (self.blank_widget, self.BLANK)
        }
        widget_alignment = {
            0: Qt.AlignmentFlag.AlignTop,
            1: Qt.AlignmentFlag.AlignCenter,
            2: Qt.AlignmentFlag.AlignCenter,
        }
        for index, widgets in enumerate(widgets_layout):
            row_layout = QHBoxLayout()
            row_layout.setSpacing(0)
            row_layout.setContentsMargins(0, 0, 0, 0)
            self.layouts.append(row_layout)
            for i, widget in widgets.items():
                label = QLabel(self)
                label.setFixedSize(widget[0], widget[1])
                label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
                if bool(widget_functions[i][1]):
                    label.setStyleSheet('QWidget{background-color: '
                                        f"{'rgba(100,100,100, .3);' if self.dark_mode else 'rgba(255,255,255, .3);'}"
                                        ' padding: 30px; border-radius: 30px; backdrop-filter: blur(5px);}')
                label.setAlignment(widget_alignment[i])
                label.setOpenExternalLinks(True)
                self.labels[i] = label
                widget_functions[i][0](i, index)
                if bool(widget_functions[i][1]):
                    timer = QTimer(self)
                    timer.timeout.connect(widget_functions[i][1])
                    timer.start(5000)
            self.general_layout.addLayout(row_layout)

    def default_widget(self, i, index):
        self.labels[i].setText("This is a widget")
        self.layouts[index].addWidget(self.labels[i])

    def update_default_widget(self):
        pass

    def blank_widget(self, i, index):
        self.layouts[index].addWidget(self.labels[i])

    def weather_widget(self, i, index):
        data = self.weather.get_data()
        formatted_data = self.weather.format_data(data)
        self.labels[i].setText(formatted_data)
        self.layouts[index].addWidget(self.labels[i])

    def volume_widget(self, i, index):
        s_layout = QStackedLayout()
        s_layout.setSpacing(0)
        s_layout.setContentsMargins(0, 0, 0, 0)
        s_layout.setStackingMode(QStackedLayout.StackingMode.StackAll)

        slider = QSlider(self)
        centered_frame = QFrame()
        centered_frame.setLayout(QVBoxLayout())
        centered_frame.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)

        centered_frame.layout().addWidget(slider)

        slider.setOrientation(Qt.Orientation.Horizontal)
        slider.setMinimum(int(self.volume.audio_range[0] * 100))
        slider.setMaximum(int(self.volume.audio_range[1] * 100))
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval(100)
        slider.setValue(int(self.volume.current_volume * 100))

        slider.setFixedSize(250, 40)
        slider.valueChanged.connect(self.update_volume_on_slider_change)

        centered_frame.layout().addWidget(slider)

        self.labels[i].setText(f"""
        <html>
            <p style="font-size: 30px; white-space: pre;">🔇{"&#9;" * 4}🔊</p>
        </html>
        """)

        s_layout.addWidget(self.labels[i])
        s_layout.addWidget(centered_frame)
        s_layout.setCurrentIndex(1)

        self.layouts[index].addLayout(s_layout)

    def update_volume(self):
        pass

    def update_volume_on_slider_change(self, value):
        self.volume.set_volume(value / 100)

    def update_weather_widget(self):
        data = self.weather.get_data()
        formatted_data = self.weather.format_data(data)
        self.labels[0].setText(formatted_data)


if __name__ == '__main__':
    screen_width, screen_height = pyautogui.size()
    widgets_to_make = [
        {0: (430, 460)},
        {1: (430, 110)},
        {2: (430, screen_height-600)}
    ]
    app = QApplication(sys.argv)
    widgets = Layout(widgets_to_make)
    sys.exit(app.exec())
