import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from function.mainFunctions import assets_dir_func
from function.trayFunctions import (showHansei, updateTooltip, showShortenedTimetable, showSettings, exitApp, makeTrayMenu,
showProfile)

class mainTray:
    """Windows System Tray Function"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        menuIconPath = assets_dir_func("remy.ico")
        self.menuIcon = QSystemTrayIcon(QIcon(menuIconPath), self.app)
        self.menu = QMenu()

        makeTrayMenu(self, "profile.ico", "profile", showProfile, "profile")
        makeTrayMenu(self, "hanseiLogo.ico", "HanseiCyberHighSchool", showHansei, "hansei")
        makeTrayMenu(self, "time.ico", "Shortened_Timetable", lambda: showShortenedTimetable(self), "shortenedTimetable")
        makeTrayMenu(self, "settings.ico", "Settings", lambda: showSettings(self), "settings")
        makeTrayMenu(self, "exit.ico", "Exit", exitApp, "exit")

        self.menuIcon.setContextMenu(self.menu)
        updateTooltip(self)
        self.menuIcon.show()

    def run(self):
        if self.app.exec_() == 0:
            exitApp()
