import sys
import json
import random
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QEvent

import NewProfileWindow

# TODO: make units whose recruited unit is in "dead" or "unrecruited" automatically go to "unrecruited"

class CRManager(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Menu Bar and Actions
        self.menu_bar = self.menuBar()
        self.fileMenu = self.menu_bar.addMenu('File')
        self.new_act = QAction("New Profile")
        self.open_act = QAction("Open Profile")
        self.save_act = QAction("Save Profile")
        self.ActionsInit()
        
        # Labels
        self.current_label = QLabel("Current Units")
        self.safe_label = QLabel("Safe Units")
        self.dead_label = QLabel("Dead Units")
        self.unrecruited_label = QLabel("Unrecruited Units")
        self.chapter_label = QLabel("Current Chapter:")
        self.route_label = QLabel("Route:")
        
        # Text Boxes
        self.current_text = QListWidget()
        self.safe_text = QListWidget()
        self.dead_text = QListWidget()
        self.unrecruited_text = QListWidget()
        self.CurrentEventFilter()
        
        # Buttons
        self.roll_button = QPushButton("Roll Units")
        self.skip_button = QPushButton("Skip Chapter")
        self.option_a = QRadioButton("A")
        self.option_b = QRadioButton("B")
        self.DisableButtons()
        
        # Variables with no value yet
        self.profile_filename = None
        self.current_list = []
        self.safe_list = []
        self.dead_list = []
        self.unrecruited_list = []
        self.other_list = []
        self.current_chapter_name = None
        self.current_chapter_num = None
        self.game = None
        self.chapter_list = []
        self.temp_list = []
        
        self.FixLayout()
    
    def CurrentEventFilter(self):
        self.current_text.installEventFilter(self)
    
    # Makes context menus appear for QListWidgetItems
    def eventFilter(self, source, event):
        # Only handled event is Context Menu Event from the current_text QListWidget
        if (event.type() == QEvent.ContextMenu and source is self.current_text):
            context_menu = QMenu()
            context_menu.addAction("Move Unit to Unrecruited")
            
            unit_item = source.itemAt(event.pos())
            
            if unit_item != None:
                # Removes unit from current and adds them to unrecruited
                if context_menu.exec_(event.globalPos()):
                    
                    unit_item = source.itemAt(event.pos())
                    unit = unit_item.text()
                    
                    self.current_list, self.current_text = self.RemoveUnitFromList(
                        unit,
                        self.current_list,
                        self.current_text
                    )
                    
                    self.unrecruited_list.append(unit)
                    self.unrecruited_text.addItem(unit_item)
                
            return True
        
        return super(CRManager, self).eventFilter(source, event) # Unhandled events are passed to the base class's eventFilter
    
    # Initializes all the other stuff to get the actions working like connecting them to singals
    def ActionsInit(self):
        self.new_act.triggered.connect(self.NewFile)
        self.open_act.triggered.connect(self.OpenFile)
        self.save_act.triggered.connect(self.SaveFile)
        
        self.new_act.setShortcut("Ctrl+N")
        self.open_act.setShortcut("Ctrl+O")
        self.save_act.setShortcut("Ctrl+S")
        
        self.fileMenu.addAction(self.new_act)
        self.fileMenu.addAction(self.open_act)
        self.fileMenu.addAction(self.save_act)
    
    def DisableButtons(self):
        buttons = (self.roll_button, self.skip_button, self.option_a, self.option_b)
        
        for button in buttons:
            button.setEnabled(False)
    
    def FixLayout(self):
        self.resize(1200, 675)
        self.setWindowTitle('FE Casualty Run Manager')
        
        # Centers the window on the center of the screen
        qr = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(center)
        self.move(qr.topLeft())
        
        widget = QWidget(self)
        self.setCentralWidget(widget)
        
        labels_texts = (
            (self.current_label, self.current_text),
            (self.safe_label, self.safe_text),
            (self.dead_label, self.dead_text),
            (self.unrecruited_label, self.unrecruited_text),
            self.chapter_label
        )
        
        buttons = (self.roll_button, self.skip_button)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        
        self.show()
        
        # Adds unit labels and text boxes to the grid
        for i in range(4):
            grid.addWidget(labels_texts[i][0], 0, i) #the format is (y, x) for some reason
            grid.addWidget(labels_texts[i][1], 1, i)
        
        # Adds chapter label to the grid
        grid.addWidget(labels_texts[4], 2, 0)
        
        # Adds buttons to the grid
        for i in range(2):
            grid.addWidget(buttons[i], 2, i + 1)
            
        # Radio buttons require a different layout
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        
        hbox.addWidget(self.option_a)       # Layout:    Label
        hbox.addWidget(self.option_b)       #         . A   . B
        vbox.addWidget(self.route_label)
        vbox.addLayout(hbox)
        
        vbox.setAlignment(self.route_label, Qt.AlignHCenter)
        vbox.setAlignment(hbox, Qt.AlignHCenter)
        
        grid.addLayout(vbox, 2, 3)
            
        widget.setLayout(grid)
    
    def NewFile(self):
        self.new_profile_window = NewProfileWindow.NewProfileWindow()
        
        # If a new profile was created, instantly "open" that new profile
        self.new_profile_window.new_file_made_signal.connect(self.InitAfterOpeningFile)
    
    def OpenFile(self):
        name = QFileDialog.getOpenFileName(self, "Open File") # Returns a tuple, first element is the filename
        
        if name[0] != "":
            self.InitAfterOpeningFile(name[0])
    
    def SaveFile(self):
        try:
            with open(self.profile_filename, "r") as profile:
                profile_dict = json.load(profile)
            
            profile_dict["Current Chapter"] = [self.current_chapter_name, self.current_chapter_num]
            
            keys = ("Current Units", "Dead Units", "Unrecruited Units", "Other Units")
            lists = (self.current_list, self.dead_list, self.unrecruited_list, self.other_list)
            
            for i in range(4):
                profile_dict[keys[i]] = lists[i]
            
            with open(self.profile_filename, "w") as profile:
                json.dump(profile_dict, profile, indent = 4)
                
        except:
            print("\nCannot save file. Check to make sure that a run is currently opened.")
        
    def InitAfterOpeningFile(self, filename):
        self.profile_filename = filename
        list_widgets = (self.current_text, self.safe_text, self.dead_text, self.unrecruited_text)
        
        # Clear out all the list widgets
        for list_widget in list_widgets:
            list_widget.clear()
        
        # Enable all the buttons
        self.roll_button.setEnabled(True)
        self.skip_button.setEnabled(True)
        
        self.roll_button.clicked.connect(self.RollDeadUnit)
        self.skip_button.clicked.connect(self.SkipChapter)
        
        with open(self.profile_filename, "r") as profile:
            profile_dict = json.load(profile)
        
        self.game = profile_dict["Game"][:3]
        self.current_chapter_name = profile_dict["Current Chapter"][0]
        self.current_chapter_num = profile_dict["Current Chapter"][1]
        
        self.UpdateChapterLabel()
        
        self.current_list = profile_dict["Current Units"]
        self.safe_list = profile_dict["Safe Units"]
        self.dead_list = profile_dict["Dead Units"]
        self.unrecruited_list = profile_dict["Unrecruited Units"]
        self.other_list = profile_dict["Other Units"]
        
        lists = (self.current_list, self.safe_list, self.dead_list, self.unrecruited_list)
        
        # Adds all the units in the profile to their respective list widget
        for i in range(4):
            for unit in lists[i]:
                list_widgets[i].addItem(QListWidgetItem(unit))
        
        # Grabs the game_file dictionary for use in multiple functions
        game_filename = (
            os.path.dirname(os.path.abspath(__file__))
            + "/GameData/"
            + self.game
            + ".json"
        )
        
        with open(game_filename, "r") as game_file:
            game_dict = json.load(game_file)
            self.chapter_list = game_dict["Chapters"]
    
    def UpdateChapterLabel(self):
        self.chapter_label.setText(
            "Current Chapter: "
            + self.game
            + " "
            + self.current_chapter_name
        )
        
    def RollDeadUnit(self):
        if len(self.current_list) > 0:  # Only rolls if the list is not empty
            chosen_death = random.choice(self.current_list)
        
            self.current_list, self.current_text = self.RemoveUnitFromList(
                chosen_death,
                self.current_list,
                self.current_text
            )
        
            self.dead_list.append(chosen_death)
            self.dead_text.addItem(QListWidgetItem(chosen_death))
        
        if self.current_chapter_name == "Final":    # Disables buttons after reaching final chapter
            self.DisableButtons()
            
        self.NextChapter()
    
    # Moves on to the next chapter and moves all the units in that chapter to unrecruited
    def SkipChapter(self):
        current_chapter = self.chapter_list[self.current_chapter_num]
            
        # Loop through all units recruited in that chapter and move them to unrecruited
        for i in range(1, len(current_chapter)):
            unit = current_chapter[i]
                
            self.current_list, self.current_text = self.RemoveUnitFromList(
                unit,
                self.current_list,
                self.current_text
            )
                
            self.unrecruited_list.append(unit)
            self.unrecruited_text.addItem(QListWidgetItem(unit))
            
        self.NextChapter()
    
    # Goes to next chapter and adds all units in that chapter to the currnt_units list
    def NextChapter(self):
        if self.current_chapter_num + 1 < len(self.chapter_list): # So that it won't go past the last index of chapter_list
            self.current_chapter_num += 1
            
            current_chapter = self.chapter_list[self.current_chapter_num]
            self.current_chapter_name = current_chapter[0]
            
            self.GameHandling()
            
            current_chapter = self.chapter_list[self.current_chapter_num] # Repeat since it might be updated in the handling functions
            
            self.UpdateChapterLabel()
            
            for i in range(1, len(current_chapter)):
                unit = current_chapter[i]
                
                if unit not in self.safe_list and unit not in self.current_list and unit not in self.dead_list:
                    self.current_list.append(unit)
                    self.current_text.addItem(QListWidgetItem(unit))
    
    # Removes a unit from a certain list and the list_widget; returns the latter two 
    def RemoveUnitFromList(self, unit, unit_list, unit_text):
        unit_list.remove(unit)
        
        # First find the item, then find out the row the item is in, then use the row to take the item out
        # Needlessly complicated...
        unit_item = unit_text.findItems(unit, Qt.MatchExactly)[0]
        row = unit_text.row(unit_item)
        removed_unit_item = unit_text.takeItem(row)
        removed_unit_item = None
        
        return unit_list, unit_text
        
    def RadioButtonsSwitch(self, switch):
        self.option_a.setEnabled(switch)
        self.option_b.setEnabled(switch)
        
        if switch:
            self.option_a.setChecked(True)
    
    ##########################################################
    ### FUNCTIONS THAT HANDLE SPECIAL RECRUITMENT EVENTS   ###
    ### IN EACH GAME                                       ### 
    ##########################################################
    
    def GameHandling(self):
        if self.game == "FE8":
            self.FE8Handling()
    
    def FE8Handling(self):
        if self.current_chapter_name == "5x":
            for unit in self.current_list:
                self.temp_list.append(unit) # Can technically do temp_list = current_list[:] but they sometimes have the same list?
            
            self.current_text.clear()
            self.current_list = []
            
        elif self.current_chapter_name == "6":
            units = ("Forde", "Kyle", "Orson")
            
            for unit in units:
                if unit in self.current_list:
                    self.current_list, self.current_text = self.RemoveUnitFromList(
                        unit,
                        self.current_list,
                        self.current_text
                    )
                    
            for unit in self.temp_list:
                self.current_list.append(unit)
                self.current_text.addItem(QListWidgetItem(unit))
        
        # Reenable buttons so people can pick which route to go to before Chapter 9A
        elif self.current_chapter_name == "8":
            self.RadioButtonsSwitch(True)
        
        # Disable them when route split starts and move to 9B if option B is checked
        elif self.current_chapter_name == "9A":
            self.RadioButtonsSwitch(False)
            
            if self.option_b.isChecked():
                self.current_chapter_num = 18    # If the player goes B route, change current_chapter_num and name to 9B
                self.current_chapter_name = "9B"
        
        # Adds Amelia to current in Ch. 13A only if she hasn't been recruited and is still alive
        elif self.current_chapter_name == "13A":
            if "Amelia" in self.unrecruited_list:
                self.current_list.append("Amelia")
                self.current_text.addItem(QListWidgetItem("Amelia"))
                
                self.unrecruited_list, self.unrecruited_text = RemoveUnitFromList(
                    "Amelia",
                    self.unrecruited_list,
                    self.unrecruited_text
                )
        
        # Jumps from 15A to 16
        elif self.current_chapter_name == "Dummy":
            self.current_chapter_num = 25
            self.current_chapter_name = "16"
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CRManager()
    sys.exit(app.exec_())
