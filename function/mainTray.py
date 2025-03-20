import sys
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon
from function.trayFunctions import makeTrayMenu
from function.mainFunctions import (todayVariable, isMWF, isShortened, assets_dir_func, getAllTimetable, loggingFunc,
                                    convert_timetable, exitProgramFunc)

class mainTray:
    """Windows System Tray Function"""
    
    def __init__(self):
        
        loggingFunc(title="MT_init", comment="MAKING ···")
        
        self.app = QApplication(sys.argv)
        
        menuIconPath = assets_dir_func("hanseiLogo.ico")
        self.menuIcon = QSystemTrayIcon(QIcon(menuIconPath), self.app)

        self.menu = QMenu()

        makeTrayMenu(
            self=self,
            icon="time.ico",
            title="Shortened_Timetable",
            function=self.showShortenedTimetable,
            action="shortenedTimetable"
        )

        makeTrayMenu(
            self=self,
            icon="settings.ico",
            title="Settings",
            function=self.showSettings,
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
        self.updateTooltip()
        self.menuIcon.show()

    def updateTooltip(self, isShortened:bool=False):
        
        loggingFunc(title="MT_updateTooltip", comment="MAKING ···")
        
        _, allTimetable = getAllTimetable()
        
        basicTimetable = allTimetable["BASIC_TIMETABLE"]
        shortenedTimetable = allTimetable["SHORTENED_TIMETABLE"]
        basicTimetable = convert_timetable(timetable=basicTimetable)
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
    
    def showShortenedTimetable(self):
        
        loggingFunc(title="MT_showShortenedTimetable", comment="MAKING ···")
        
        isActivated = isShortened()
        comment = "Activated" if isActivated else "Deactivated"
        self.updateTooltip(isShortened=isActivated)
        self.tray_icon.showMessage(
            "Shortened Timetable Mode",
            f"{comment}",
            QSystemTrayIcon.Information,
            2000
        )

    def showSettings(self):
        
        loggingFunc(title="MT_showSettings", comment="MAKING ···")
        
        from function.settingsTray import settingsTray
        settingsTray(self)

    def run(self):
        loggingFunc(title="MT_run", comment="MAKING ···")
        if self.app.exec_() == 0:
            loggingFunc("{:<15}: OFF".format("PROGRAM"))
            exitProgramFunc()