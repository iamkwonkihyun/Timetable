import sys, os, logging
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
# 경로 추가 (가능하면 상대경로를 권장)
sys.path.append(os.path.abspath("c:/HANSEI/TimeTable/data"))  
sys.path.append(os.path.abspath("c:/HANSEI/TimeTable/function"))  

from all_data import TIMETABLE
from todayVariable import todayVariable

class systemTray:
    def __init__(self):
        self.app = QApplication(sys.argv)

        tray_icon_path = "C:/HANSEI/TimeTable/assets/hansei.ico"
        self.tray_icon = QSystemTrayIcon(QIcon(tray_icon_path), self.app)

        self.menu = QMenu()
        
        settings_icon_path = "C:/HANSEI/TimeTable/assets/settings.ico"
        self.show_action = QAction(QIcon(settings_icon_path), "Settings", self.menu)
        self.show_action.triggered.connect(self.show_settings)
        self.menu.addAction(self.show_action)

        exit_icon_patt = "C:/HANSEI/TimeTable/assets/exit.ico"
        self.quit_action = QAction(QIcon(exit_icon_patt), "Exit", self.menu)
        self.quit_action.triggered.connect(self.app.quit)
        self.menu.addAction(self.quit_action)

        self.tray_icon.setContextMenu(self.menu)

        self.update_tooltip()
        
        self.tray_icon.show()

    def update_tooltip(self):
        _, txt_today, _, _ = todayVariable(isTest=False)
        today_schedule = TIMETABLE.get(txt_today, {})

        # 시간표를 문자열로 변환
        timetable_message = "\n".join([f"{time}: {task}" for time, task in today_schedule.items()])
        
        if not timetable_message:
            timetable_message = "No schedule available"  # 시간표가 없을 경우 기본 메시지

        self.tray_icon.setToolTip(timetable_message)  # 📌 마우스를 올렸을 때 툴팁으로 표시됨

    def show_settings(self):
        self.tray_icon.showMessage(
            "Timetable",
            self.tray_icon.toolTip(),  # 기존 툴팁 내용 사용
            QSystemTrayIcon.Information,
            2000
        )

    def run(self):
        if self.app.exec_() == 0:
            logging.info("PROGRAM OFF")
            sys.exit()