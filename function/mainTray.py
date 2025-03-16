import sys, logging
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from function.mainFunctions import todayVariable, isMWF, isShortened, assets_dir_func, getAllTimetable

class mainTray:
    """Windows System Tray Function"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        tray_icon_path = assets_dir_func("hansei.ico")
        self.tray_icon = QSystemTrayIcon(QIcon(tray_icon_path), self.app)

        self.menu = QMenu()

        time_icon_path = assets_dir_func(("time.ico"))
        self.time_action = QAction(QIcon(time_icon_path), "Shortened_Mode", self.menu)
        self.time_action.triggered.connect(self.show_shortended_timetable)
        self.menu.addAction(self.time_action)

        settings_icon_path = assets_dir_func(("settings.ico"))
        self.settings_action = QAction(QIcon(settings_icon_path), "Settings", self.menu)
        self.settings_action.triggered.connect(self.show_settings)
        self.menu.addAction(self.settings_action)

        exit_icon_patt = assets_dir_func(("exit.ico"))
        self.exit_action = QAction(QIcon(exit_icon_patt), "Exit", self.menu)
        self.exit_action.triggered.connect(self.app.quit)
        self.menu.addAction(self.exit_action)

        self.tray_icon.setContextMenu(self.menu)
        self.update_tooltip()
        self.tray_icon.show()

    def update_tooltip(self, isShortened:bool=False):
        
        _, allTimetable = getAllTimetable()
        
        basicTimetable = allTimetable["BASIC_TIMETABLE"]
        shortenedTimetable = allTimetable["SHORTENED_TIMETABLE"]
        
        _, txt_today, _, _ = todayVariable()
        
        if isShortened:
            key = "MWF" if isMWF(txt_today) else "TT"
            today_schedule = shortenedTimetable.get(key, {})
        else:
            today_schedule = basicTimetable.get(txt_today, {})
            
        timetable_message = "\n".join([f"{time}: {task}" for time, task in today_schedule.items()])

        if not timetable_message:
            timetable_message = "No schedule available"

        self.tray_icon.setToolTip(timetable_message)

    def show_shortended_timetable(self):
        isActivated = isShortened()
        comment = "Activated" if isActivated else "Deactivated"
        self.update_tooltip(isShortened=isActivated)
        self.tray_icon.showMessage(
            "Shortened Timetable Mode",
            f"{comment}",
            QSystemTrayIcon.Information,
            2000
        )

    def show_settings(self):
        from function.settingsTray import settingsTray
        settingsTray(self)

    def run(self):
        if self.app.exec_() == 0:
            logging.info("{:<15}: OFF".format("PROGRAM"))
            sys.exit()
