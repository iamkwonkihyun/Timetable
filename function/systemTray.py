import sys, os, logging
from data.filePath import assets_dir_func
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from data.all_data import TIMETABLE, SHORTENED_TIMETABLE
from function.todayVariable import todayVariable
from function.isMWF import isMWF
from function.isShortened import isShortened

isActivated = True

class systemTray:
    """Windows System Tray Function
    """
    def __init__(self):
        self.app = QApplication(sys.argv)

        tray_icon_path = assets_dir_func("hansei.ico")
        self.tray_icon = QSystemTrayIcon(QIcon(tray_icon_path), self.app)

        self.menu = QMenu()
        
        settings_icon_path = assets_dir_func(("time.ico"))
        self.show_action = QAction(QIcon(settings_icon_path), "Shortened_Mode", self.menu)
        self.show_action.triggered.connect(self.show_shortended_timetable)
        self.menu.addAction(self.show_action)
        
        settings_icon_path = assets_dir_func(("settings.ico"))
        self.show_action = QAction(QIcon(settings_icon_path), "Settings", self.menu)
        self.show_action.triggered.connect(self.show_settings)
        self.menu.addAction(self.show_action)

        exit_icon_patt = assets_dir_func(("exit.ico"))
        self.quit_action = QAction(QIcon(exit_icon_patt), "Exit", self.menu)
        self.quit_action.triggered.connect(self.app.quit)
        self.menu.addAction(self.quit_action)

        self.tray_icon.setContextMenu(self.menu)

        self.update_tooltip()
        
        self.tray_icon.show()

    def update_tooltip(self):
        global isActivated
        
        _, txt_today, _, _ = todayVariable(isTest=False)
        if isShortened():
            key = "MWF" if isMWF(txt_today) else "TT"
            today_schedule = SHORTENED_TIMETABLE.get(key, {})
            isActivated = True
        else:
            today_schedule = TIMETABLE.get(txt_today, {})
            isActivated = False

            
        # 시간표를 문자열로 변환
        timetable_message = "\n".join([f"{time}: {task}" for time, task in today_schedule.items()])

        if not timetable_message:
            timetable_message = "No schedule available"  # 시간표가 없을 경우 기본 메시지

        self.tray_icon.setToolTip(timetable_message)  # 📌 마우스를 올렸을 때 툴팁으로 표시됨

    def show_shortended_timetable(self):
        comment = "Deactivated" if isActivated else "Activated"
        self.update_tooltip()
        self.tray_icon.showMessage(
            "Shortened Timetable Mode",
            f"{comment}",  # 기존 툴팁 내용 사용
            QSystemTrayIcon.Information,
            2000
        )

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