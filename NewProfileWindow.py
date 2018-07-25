import json
import os
import random
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal


class NewProfileWindow(QWidget):
    new_file_made_signal = pyqtSignal(str) # Has to be initialized outside of constructor or else it bugs out
                                           # Will pass a str argument to the function it's connected to
    
    def __init__(self):
        super().__init__()
        
        # Initializes profile name part
        self.name_label = QLabel("Profile Name:", self)
        self.name_text = QLineEdit(self)
        
        # Initializes game choice part
        self.game_label = QLabel("Game:", self)
        self.game_combo_box = QComboBox(self)
        self.AddComboBoxOptions()
        
        # Initializes safe unit choice part
        self.safe_label = QLabel("Safe Unit Choice: ", self)
        self.option_1 = QRadioButton("None", self)
        self.option_2 = QRadioButton("Up to midgame", self)
        self.option_3 = QRadioButton("Any", self)
        self.option_1.setChecked(True)
        
        # Initializes buttons
        self.ok_button = QPushButton("Create Profile", self)
        self.cancel_button = QPushButton("Cancel", self)
        self.ConnectButtons()
        
        # Initializes other initially unused variables
        self.profile_dict = {}
        self.possible_safe_units = []
        
        self.FixLayout()
        
        self.show()
    
    def AddComboBoxOptions(self):
        games = (
            #"FE6 (Fire Emblem: The Binding Blade)",
            #"FE7 (Fire Emblem: The Blazing Sword)",
            "FE8 (Fire Emblem: The Sacred Stones)",
        )
        
        for game in games:
            self.game_combo_box.addItem(game)
            
    def ConnectButtons(self):
        self.ok_button.clicked.connect(self.MakeNewProfile)
        self.cancel_button.clicked.connect(self.close)
        
    def FixLayout(self):
        self.setGeometry(600, 400, 400, 200)
        self.setWindowTitle("New Profile")
        
        hbox_1 = QHBoxLayout()
        hbox_2 = QHBoxLayout()
        hbox_3 = QHBoxLayout()
        hbox_4 = QHBoxLayout()
        vbox = QVBoxLayout()
        
        #Put in a tuple so I can easily loop through the widgets when putting them in the hboxes
        elements = (
            (self.name_label, self.name_text), 
            (self.game_label, self.game_combo_box), 
            (self.safe_label, self.option_1, self.option_2, self.option_3),
            (self.ok_button, self.cancel_button)
        )
        
        hboxes = (hbox_1, hbox_2, hbox_3, hbox_4)
        
        #Adds name label and text to 1st hbox, game label and combo box to 2nd hbox, and so on)
        for i in range(4):
            for element in elements[i]:
                hboxes[i].addWidget(element)
            
            vbox.addLayout(hboxes[i])
        
        vbox.addStretch() # Pushes everything to the top
        vbox.setSpacing(20) # Put some spacing between so it's not too squished together
        self.setLayout(vbox)
    
    ### Makes a new profile and closes the window
    def MakeNewProfile(self):
        profile_name = str(self.name_text.text()) + ".json"  # Makes the file name
        directory = os.path.dirname(os.path.abspath(__file__))
        
        if profile_name != "":
            # Saves file in the "Profiles" directory
            filepath = (
                directory
                + "/Profiles/"
                + profile_name
            )
            new_file = open(filepath, "w")
            
            # Creates the dictionary to be added to the profile json file
            self.profile_dict = {
                "Game": self.game_combo_box.currentText(), # Grabs game from the combo box and adds it to the dict
                "Current Chapter": None,
                "Current Units": [],
                "Safe Units": [],
                "Dead Units": [],
                "Unrecruited Units": [],
                "Other Units": []
            }
            
            # Gets the "FE#" and adds it to ".json" to get the game json filename
            game_filename = (
                directory
                + "/GameData/"
                + self.profile_dict["Game"][:3]
                + ".json"
            )
            
            # Loads the game json file
            with open(game_filename, "r") as game_file:
                game_dict = json.load(game_file)
                self.chapter_list = game_dict["Chapters"]
                cutoff_point = game_dict["Cutoff Point"]
                starting_chapter = self.chapter_list[0]   # Gets first chapter data
                
                self.profile_dict["Current Chapter"] = (starting_chapter[0], 0)
                
                # Adds all the units you get in the first chapter to the "Current Units" list
                for current_unit in range(1, len(starting_chapter)):
                    self.profile_dict["Current Units"].append(starting_chapter[current_unit])
                    self.possible_safe_units.append(starting_chapter[current_unit])
                
                # Adds all the units from first chapter to the end to the "Unrecruited Units" list
                # Only if safe unit option "up to midgame" is not checked
                if not self.option_2.isChecked():
                    self.AddUnitsToUnrecruited(1, len(self.chapter_list))
                    
                    # If safe unit option "any" is checked, pick a safe unit
                    if self.option_3.isChecked():
                        self.PickSafeUnit()
                            
                # Otherwise, add all the units before the cutoff point first and add the rest later
                else:
                    self.AddUnitsToUnrecruited(1, cutoff_point)
                    self.PickSafeUnit()
                    self.AddUnitsToUnrecruited(cutoff_point, len(self.chapter_list))
                        
                for safe_unit in game_dict["Safe Units"]:
                    self.profile_dict["Safe Units"].append(safe_unit)
            
            json.dump(self.profile_dict, new_file, indent = 4)
            
            new_file.close()
            
        self.new_file_made_signal.emit(filepath)
        self.close()
    
    # Iterates through units in certain chapters and adds them to the "Other units" list
    def AddUnitsToUnrecruited(self, start_chapter, end_chapter):
        for chapter in range(start_chapter, end_chapter):
            for unit in range(1, len(self.chapter_list[chapter])):
                self.profile_dict["Other Units"].append(self.chapter_list[chapter][unit])
                self.possible_safe_units.append(self.chapter_list[chapter][unit])

    def PickSafeUnit(self):
        chosen_safe = random.choice(self.possible_safe_units)
        
        # Put this check since possible_safe_units includes units in "Other" AND "Current"
        if chosen_safe in self.profile_dict["Other Units"]:
            self.profile_dict["Other Units"].remove(chosen_safe)
        else:
            self.profile_dict["Current Units"].remove(chosen_safe)
            
        self.profile_dict["Safe Units"].append(chosen_safe)
        
        print(chosen_safe)
