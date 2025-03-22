import sys
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon
from function.trayFunctions import makeTrayMenu
from function.mainFunctions import (todayVariable, isMWF, isShortened, assets_dir_func, getJsonData,
                                    convert_timetable, exitProgramFunc)

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
        
        allTimetable = getJsonData(jsonFileName="allTimetable.json")
        
        basicTimetable = allTimetable["BASIC_TIMETABLE"]
        shortenedTimetable = allTimetable["SHORTENED_TIMETABLE"]
        basicTimetable = convert_timetable(timetable=basicTimetable)
        _, txt_today, _ = todayVariable()
        
        if isShortened:
            key = "MWF" if isMWF(today=txt_today) else "TT"
            today_schedule = shortenedTimetable.get(key, {})
        else:
            today_schedule = basicTimetable.get(txt_today, {})
            
        timetable_message = "\n".join([f"{time}: {task}" for time, task in today_schedule.items()])

        if not timetable_message:
            timetable_message = "No schedule available"

        self.menuIcon.setToolTip(timetable_message)
    
    def showShortenedTimetable(self):        
        isActivated = isShortened()
        comment = "Activated" if isActivated else "Deactivated"
        self.updateTooltip(isShortened=isActivated)
        self.menuIcon.showMessage(
            "Shortened Timetable Mode",
            f"{comment}",
            QSystemTrayIcon.Information,
            2000
        )

    def showSettings(self):
        from function.settingsTray import settingsTray
        settingsTray(self)

    def run(self):
        if self.app.exec_() == 0:
            exitProgramFunc()
