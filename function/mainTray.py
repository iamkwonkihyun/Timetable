import sys, logging
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon
from function.mainFunctions import todayVariable, isMWF, isShortened, assets_dir_func, getAllTimetable
from function.trayFunctions import makeTrayMenu
class mainTray:
    """Windows System Tray Function"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        menuIconPath = assets_dir_func("hanseiLogo.ico")
        self.menuIcon = QSystemTrayIcon(QIcon(menuIconPath), self.app)

        self.menu = QMenu()

        makeTrayMenu(
            self=self,
            icon="time.ico",
            title="Shortened_Timetable",
            function=self.show_shortended_timetable,
            action="shortenedTimetable"
        )

        makeTrayMenu(
            self=self,
            icon="settings.ico",
            title="Settings",
            function=self.show_settings,
            action="settings"
        )
        
        makeTrayMenu(
            self=self,
            icon="exit.ico",
            title="Exit",
            function=self.app.exit,
            action="exit"
        )

        self.menuIcon.setContextMenu(self.menu)
        self.update_tooltip()
        self.menuIcon.show()

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

        self.menuIcon.setToolTip(timetable_message)

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
