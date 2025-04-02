import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from function.mainFunctions import assets_dir_func, exitProgramFunc
from function.trayFunctions import (
    setRefresh, updateTooltip, setShortenedTimetableMode, makeTrayMenu, showProfile, showSettingsWindow
)

class systemTray:
    """Windows System Tray Function"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        menuIconPath = assets_dir_func("remy.ico")
        self.menuIcon = QSystemTrayIcon(QIcon(menuIconPath), self.app)
        self.menu = QMenu()

        # 프로필 트레이
        makeTrayMenu(self, "profile.ico", "profile", showProfile, "profile")
        
        # 한세사이버보안고등학교 트레이
        makeTrayMenu(self, "refresh.ico", "refresh", lambda: setRefresh(self), "refresh")
        
        # 단축 수업 트레이
        makeTrayMenu(self, "time.ico", "Shortened_Timetable", lambda: setShortenedTimetableMode(self), "shortenedTimetable")
        
        # 세팅 트레이
        makeTrayMenu(self, "settings.ico", "Settings", lambda: showSettingsWindow(self), "settings")
        
        # 프로그램 종료 트레이
        makeTrayMenu(self, "exit.ico", "Exit", exitProgramFunc, "exit")

        self.menuIcon.setContextMenu(self.menu)
        updateTooltip(self)
        self.menuIcon.show()

    def run(self):
        if self.app.exec_() == 0:
            exitProgramFunc()
