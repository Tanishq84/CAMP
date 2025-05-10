import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGraphicsBlurEffect, QLabel, QVBoxLayout, QGridLayout, \
    QHBoxLayout, QStackedWidget, QLineEdit, QTextEdit, QMessageBox, QComboBox, QFileDialog, QDateEdit, QScrollArea, QTableWidgetItem, QTableWidget, QHeaderView, QInputDialog
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor, QIcon
from PyQt5.QtCore import Qt
import mysql.connector
import io
import base64
from PIL import Image, ImageTk
import cv2
import numpy as np
from datetime import datetime
from texttable import Texttable
import face_recognition
import matplotlib.pyplot as plt

class CrimeAnalysisApp(QWidget):
    def __init__(self):
        super().__init__()
        self.db = self.connect_to_database()
        self.init_ui()
        
    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #111;
                color: #fff;
            }
            QPushButton {
                background: qradialgradient(
                    cx: 0.5, cy: 0.5, radius: 0.5,
                    fx: 0.5, fy: 0.5,
                    stop: 0.7 #444444, stop: 1 #111
                );
                color: #fff;
                border: 1px solid #0077cc; /* Darker Blue */
                padding: 10px;  /* Reduced padding for smaller buttons */
                border-radius: 5px;
            }
            QPushButton:hover {
                background: qradialgradient(
                    cx: 0.5, cy: 0.5, radius: 0.5,
                    fx: 0.5, fy: 0.5,
                    stop: 0.7 #888888, stop: 1 #111
                );
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #555555;
                border-radius: 3px;
                background-color: #333333;
                color: #fff;
            }
        """)

   
        self.setWindowTitle('Crime Analysis and Monitoring Portal (CAMP)')
        self.showMaximized()  
        self.setWindowIcon(QIcon('camp.png'))

        blur_container = QWidget(self)
        blur_container.setGeometry(0, 0, self.width(), self.height())

        self.blur_background(blur_container)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True) 
        scroll_area.setGeometry(0, 0, self.width(), self.height())

        scroll_content = QWidget(scroll_area)
        scroll_area.setWidget(scroll_content)

        main_layout = QVBoxLayout(scroll_content)
        header_layout = QHBoxLayout()

        title_label = QLabel('Welcome to CAMP!', self)
        title_label.setStyleSheet("QLabel { color: #00ffcc; font-size: 36px; font-weight: bold; }")
        title_label.setAlignment(Qt.AlignCenter)  

        left_logo_label = QLabel(self)
        left_logo_pixmap = QPixmap("permutes.png").scaledToWidth(130) 
        left_logo_label.setPixmap(left_logo_pixmap)
        left_logo_label.setAlignment(Qt.AlignCenter)

        right_logo_label = QLabel(self)
        right_logo_pixmap = QPixmap("camp.png").scaledToWidth(180)
        right_logo_label.setPixmap(right_logo_pixmap)
        right_logo_label.setAlignment(Qt.AlignCenter)

        header_layout.addWidget(left_logo_label)
        header_layout.addWidget(title_label)
        header_layout.addWidget(right_logo_label)

        main_layout.addLayout(header_layout)

        full_form_label = QLabel('(Crime Analysis and Monitoring Portal)', self)
        full_form_label.setStyleSheet("QLabel { color: #00ffcc; font-size: 24px; }")
        full_form_label.setAlignment(Qt.AlignCenter) 

        main_layout.addWidget(full_form_label, alignment=Qt.AlignCenter)
        self.stacked_widget = QStackedWidget(self)
        main_page = QWidget()
        main_page_layout = QVBoxLayout(main_page)
        top_button_layout = QHBoxLayout()

        fnt = QFont()
        fnt.setPointSize(16)
        police_stations_button = QPushButton('Police Stations', self)
        police_stations_button.clicked.connect(self.show_police_stations_page)
        police_stations_button.setFont(fnt)
        police_stations_button.setFixedSize(400, 100)
        criminal_cases_button = QPushButton('Criminal Cases', self)
        criminal_cases_button.clicked.connect(self.show_criminal_cases_page)
        criminal_cases_button.setFont(fnt)
        criminal_cases_button.setFixedSize(400, 100)
        criminal_database_button = QPushButton('Criminal Database', self)
        criminal_database_button.clicked.connect(self.show_criminals_page)
        criminal_database_button.setFont(fnt)
        criminal_database_button.setFixedSize(400, 100)

        top_button_layout.addWidget(police_stations_button)
        top_button_layout.addWidget(criminal_cases_button)
        top_button_layout.addWidget(criminal_database_button)

        main_page_layout.addLayout(top_button_layout)
        grid_layout = QGridLayout()
        button_labels = [
            'Add Station', 'Add Criminal', 'New Case', 'Close a Case',
            'Image Search', 'EXIT'
        ]
        row = 1 
        col = 0
        for label in button_labels:
            button = QPushButton(label, self)
            font = QFont()
            font.setPointSize(12) 
            button.setFont(font)
            button.setFixedSize(275, 70) 

            if label == 'EXIT':
                button.clicked.connect(self.close_application)
            elif label == 'Add Station':
                button.clicked.connect(self.show_add_station_page)
            elif label == 'Add Criminal':
                button.clicked.connect(self.show_add_criminal_page)
            elif label == 'New Case':
                button.clicked.connect(self.show_add_case_page)
            elif label == 'Close a Case':
                button.clicked.connect(self.show_close_case_page)

            grid_layout.addWidget(button, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        self.apply_shine_effect(grid_layout)
        main_page_layout.addLayout(grid_layout)
        self.stacked_widget.addWidget(main_page)
        add_station_page = QWidget()
        add_station_layout = QVBoxLayout(add_station_page)

        name_label = QLabel('Station Name:', add_station_page)
        name_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")
        self.name_input = QLineEdit(add_station_page)
        self.name_input.setStyleSheet("QLineEdit { font-size: 16px; }")

        location_label = QLabel('Location:', add_station_page)
        location_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")
        self.location_input = QLineEdit(add_station_page)
        self.location_input.setStyleSheet("QLineEdit { font-size: 16px; }")

        contact_label = QLabel('Contact:', add_station_page)
        contact_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")
        self.contact_input = QLineEdit(add_station_page)
        self.contact_input.setStyleSheet("QLineEdit { font-size: 16px; }")

        head_officer_label = QLabel('Head Officer:', add_station_page)
        head_officer_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")
        self.head_officer_input = QLineEdit(add_station_page)
        self.head_officer_input.setStyleSheet("QLineEdit { font-size: 16px; }")

        num_prisoners_label = QLabel('Number of Prisoners:', add_station_page)
        num_prisoners_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")
        self.num_prisoners_input = QLineEdit(add_station_page)
        self.num_prisoners_input.setStyleSheet("QLineEdit { font-size: 16px; }")

        add_station_button = QPushButton('Add Station', add_station_page)
        add_station_button.clicked.connect(self.add_station)
        add_station_button.setStyleSheet("QPushButton { font-size: 16px; }")

        back_button = QPushButton('Back', add_station_page)
        back_button.clicked.connect(self.show_main_page)
        back_button.setStyleSheet("QPushButton { font-size: 16px; }")

        add_station_layout.addWidget(name_label)
        add_station_layout.addWidget(self.name_input)
        add_station_layout.addWidget(location_label)
        add_station_layout.addWidget(self.location_input)
        add_station_layout.addWidget(contact_label)
        add_station_layout.addWidget(self.contact_input)
        add_station_layout.addWidget(head_officer_label)
        add_station_layout.addWidget(self.head_officer_input)
        add_station_layout.addWidget(num_prisoners_label)
        add_station_layout.addWidget(self.num_prisoners_input)
        add_station_layout.addWidget(add_station_button)
        add_station_layout.addWidget(back_button)

        self.stacked_widget.addWidget(add_station_page)


        # Create the "Add Criminal" page
        add_criminal_page = QWidget()
        add_criminal_layout = QVBoxLayout(add_criminal_page)

        first_name_label = QLabel('Frist Name:', add_criminal_page)
        first_name_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")
        self.first_name_input = QLineEdit(add_criminal_page)
        self.first_name_input.setStyleSheet("QLineEdit { font-size: 16px; }")

        last_name_label = QLabel('Last Name:', add_criminal_page)
        last_name_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")
        self.last_name_input = QLineEdit(add_criminal_page)
        self.last_name_input.setStyleSheet("QLineEdit { font-size: 16px; }")

        dob_label = QLabel('Date of Birth:', add_criminal_page)
        dob_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")

        self.dob_input = QDateEdit(add_criminal_page)
        self.dob_input.setStyleSheet("QDateEdit { font-size: 16px; }")

        dod_label = QLabel('Date of Death:', add_criminal_page)
        dod_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")
        self.dod_input = QLineEdit(add_criminal_page)
        self.dod_input.setStyleSheet("QLineEdit { font-size: 16px; }")

        sex_label = QLabel('Sex:', add_criminal_page)
        sex_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")

        self.gender_combo = QComboBox(add_criminal_page)
        self.gender_combo.addItem("Male")
        self.gender_combo.addItem("Female")
        self.gender_combo.setStyleSheet("QComboBox { font-size: 16px; }")

        caseid_label = QLabel('Associated Case ID:', add_criminal_page)
        caseid_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")
        self.caseid_input = QLineEdit(add_criminal_page)
        self.caseid_input.setStyleSheet("QLineEdit { font-size: 16px; }")

        keywords_label = QLabel('Keywords:', add_criminal_page)
        keywords_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")
        self.keywords_input = QLineEdit(add_criminal_page)
        self.keywords_input.setStyleSheet("QLineEdit { font-size: 16px; }")

        stationid_label = QLabel('Associated Station ID:', add_criminal_page)
        stationid_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")
        self.stationid_input = QLineEdit(add_criminal_page)
        self.stationid_input.setStyleSheet("QLineEdit { font-size: 16px; }")

        inprison_label = QLabel('In Prison?', add_criminal_page)
        inprison_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")

        self.inprison_combo = QComboBox(add_criminal_page)
        self.inprison_combo.addItems(["Y", "N"])
        self.inprison_combo.setStyleSheet("QComboBox { font-size: 16px; }")

        address_label = QLabel('Residential Address:', add_criminal_page)
        address_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")
        self.address_input = QLineEdit(add_criminal_page)
        self.address_input.setStyleSheet("QLineEdit { font-size: 16px; }")

        contact_label = QLabel('Contact Number:', add_criminal_page)
        contact_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")
        self.contact_input = QLineEdit(add_criminal_page)
        self.contact_input.setStyleSheet("QLineEdit { font-size: 16px; }")

        photo_label = QLabel('Photo:', add_criminal_page)
        photo_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")

        self.photo_input = QLineEdit(add_criminal_page)
        self.photo_input.setReadOnly(True)
        self.photo_input.setStyleSheet("QLineEdit { font-size: 16px; }")

        browse_button = QPushButton('Browse Photo', add_criminal_page)
        browse_button.clicked.connect(self.browse_photo)
        browse_button.setStyleSheet("QPushButton { font-size: 16px; }")

        add_criminal_button = QPushButton('Add Criminal', add_criminal_page)
        add_criminal_button.clicked.connect(self.add_criminal)
        add_criminal_button.setStyleSheet("QPushButton { font-size: 16px; }")

        back_button = QPushButton('Back', add_criminal_page)
        back_button.clicked.connect(self.show_main_page)
        back_button.setStyleSheet("QPushButton { font-size: 16px; }")

        add_criminal_layout.addWidget(first_name_label)
        add_criminal_layout.addWidget(self.first_name_input)
        add_criminal_layout.addWidget(last_name_label)
        add_criminal_layout.addWidget(self.last_name_input)
        add_criminal_layout.addWidget(dob_label)
        add_criminal_layout.addWidget(self.dob_input)
        add_criminal_layout.addWidget(dod_label)
        add_criminal_layout.addWidget(self.dod_input)
        add_criminal_layout.addWidget(sex_label)
        add_criminal_layout.addWidget(self.gender_combo)
        add_criminal_layout.addWidget(caseid_label)
        add_criminal_layout.addWidget(self.caseid_input)
        add_criminal_layout.addWidget(keywords_label)
        add_criminal_layout.addWidget(self.keywords_input)
        add_criminal_layout.addWidget(stationid_label)
        add_criminal_layout.addWidget(self.stationid_input)
        add_criminal_layout.addWidget(inprison_label)
        add_criminal_layout.addWidget(self.inprison_combo)
        add_criminal_layout.addWidget(address_label)
        add_criminal_layout.addWidget(self.address_input)
        add_criminal_layout.addWidget(contact_label)
        add_criminal_layout.addWidget(self.contact_input)
        add_criminal_layout.addWidget(photo_label)
        add_criminal_layout.addWidget(self.photo_input)
        add_criminal_layout.addWidget(browse_button)
        add_criminal_layout.addWidget(add_criminal_button)
        add_criminal_layout.addWidget(back_button)


        self.stacked_widget.addWidget(add_criminal_page)


        police_stations_page = QWidget()
        police_stations_layout = QVBoxLayout(police_stations_page)

        self.police_stations_table = QTableWidget(self)
        self.police_stations_table.setColumnCount(6)
        self.police_stations_table.setHorizontalHeaderLabels(["Station ID", "Name", "Location", "Contact", "Head Officer", "No. of Prisoners"])
        self.police_stations_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        header = self.police_stations_table.horizontalHeader()
        header.setStyleSheet("QHeaderView::section { color: black; font-size: 18px; font-weight: bold;}")

        police_stations_layout.addWidget(self.police_stations_table)
        update_station_button = QPushButton('Update Station Data', police_stations_page)
        update_station_button.clicked.connect(self.update_station)
        update_station_button.setStyleSheet("QPushButton { font-size: 16px; }")
        police_stations_layout.addWidget(update_station_button)

        
        delete_criminal_button = QPushButton('Delete Station Data!', police_stations_page)
        delete_criminal_button.clicked.connect(self.delete_station)
        delete_criminal_button.setStyleSheet("QPushButton { font-size: 16px; }")
        police_stations_layout.addWidget(delete_criminal_button)

        back_button = QPushButton('Back', police_stations_page)
        back_button.clicked.connect(self.show_main_page)
        back_button.setStyleSheet("QPushButton { font-size: 16px; }")

        police_stations_layout.addWidget(back_button)
        self.stacked_widget.addWidget(police_stations_page)


        # Create the "Criminal Cases" page
        criminal_cases_page = QWidget()
        criminal_cases_layout = QVBoxLayout(criminal_cases_page)

        self.criminal_cases_table = QTableWidget(self)
        self.criminal_cases_table.setColumnCount(9)
        self.criminal_cases_table.setHorizontalHeaderLabels(["Case ID", "CriminalID", "Description", "Invgt. Station", "Keywords", "Status", "Date Reported", "Date Closed", "Result"])
        self.criminal_cases_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        header = self.criminal_cases_table.horizontalHeader()
        header.setStyleSheet("QHeaderView::section { color: black; font-size: 18px; font-weight: bold;}")

        criminal_cases_layout.addWidget(self.criminal_cases_table)

        update_case_button = QPushButton('Update Case Data', criminal_cases_page)
        update_case_button.clicked.connect(self.update_case)
        update_case_button.setStyleSheet("QPushButton { font-size: 16px; }")
        criminal_cases_layout.addWidget(update_case_button)

        
        delete_case_button = QPushButton('Delete Case Data!', criminal_cases_page)
        delete_case_button.clicked.connect(self.delete_case)
        delete_case_button.setStyleSheet("QPushButton { font-size: 16px; }")
        criminal_cases_layout.addWidget(delete_case_button)

        back_button = QPushButton('Back', criminal_cases_page)
        back_button.clicked.connect(self.show_main_page)
        back_button.setStyleSheet("QPushButton { font-size: 16px; }")

        criminal_cases_layout.addWidget(back_button)
        self.stacked_widget.addWidget(criminal_cases_page)



        # Create the "Criminals" page
        criminal_page = QWidget()
        criminal_layout = QVBoxLayout(criminal_page)

        self.criminal_table = QTableWidget(self)
        self.criminal_table.setColumnCount(12)
        self.criminal_table.setHorizontalHeaderLabels(["Criminal ID", "First Name", "Last Name", "DOB", "DOD", "Sex", "Case ID", "Keywords", "Station ID", "In Prison", "Res. Address", "Contact No."])
        self.criminal_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        header = self.criminal_table.horizontalHeader()
        header.setStyleSheet("QHeaderView::section { color: black; font-size: 18px; font-weight: bold;}")

        criminal_layout.addWidget(self.criminal_table)
        update_criminal_button = QPushButton('Update Criminal Data', criminal_page)
        update_criminal_button.clicked.connect(self.update_criminal_data)
        update_criminal_button.setStyleSheet("QPushButton { font-size: 16px; }")
        criminal_layout.addWidget(update_criminal_button)

        
        delete_criminal_button = QPushButton('Delete Criminal Data!', criminal_page)
        delete_criminal_button.clicked.connect(self.delete_criminal)
        delete_criminal_button.setStyleSheet("QPushButton { font-size: 16px; }")
        criminal_layout.addWidget(delete_criminal_button)

        back_button = QPushButton('Back', criminal_page)
        back_button.clicked.connect(self.show_main_page)
        back_button.setStyleSheet("QPushButton { font-size: 16px; }")



        criminal_layout.addWidget(back_button)
        self.stacked_widget.addWidget(criminal_page)
        add_case_page = QWidget()
        add_case_layout = QVBoxLayout(add_case_page)

        criminalid_label = QLabel('Criminal ID (if applicable):', add_case_page)
        criminalid_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")
        self.criminalid_input = QLineEdit(add_case_page)
        self.criminalid_input.setStyleSheet("QLineEdit { font-size: 16px; }")

        case_description_label = QLabel('Case Description:', add_case_page)
        case_description_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")
        self.case_description_input = QTextEdit(add_case_page)
        self.case_description_input.setStyleSheet("QTextEdit { font-size: 16px; }")

        invid_label = QLabel('Investigating Station ID:', add_case_page)
        invid_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")
        self.invid_officer_input = QLineEdit(add_case_page)
        self.invid_officer_input.setStyleSheet("QLineEdit { font-size: 16px; }")

        keyword_label = QLabel('Keywords:', add_case_page)
        keyword_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")
        self.keyword_input = QLineEdit(add_case_page)
        self.keyword_input.setStyleSheet("QLineEdit { font-size: 16px; }")

        status_label = QLabel('Status:', add_criminal_page)
        status_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")

        self.status_combo = QComboBox(add_criminal_page)
        self.status_combo.addItems(["Pending", "Closed"])
        self.status_combo.setStyleSheet("QComboBox { font-size: 20px; }")

        dater_label = QLabel('Date Reported (YYYY-MM-DD):', add_case_page)
        dater_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")
        self.dater_input = QLineEdit(add_case_page)
        self.dater_input.setStyleSheet("QLineEdit { font-size: 16px; }")

        datec_label = QLabel('Date Closed (YYYY-MM-DD):', add_case_page)
        datec_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")
        self.datec_input = QLineEdit(add_case_page)
        self.datec_input.setStyleSheet("QLineEdit { font-size: 16px; }")

        result_label = QLabel('Result Outcome:', add_case_page)
        result_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")
        self.result_input = QLineEdit(add_case_page)
        self.result_input.setStyleSheet("QLineEdit { font-size: 16px; }")

        add_case_button = QPushButton('Add Case', add_case_page)
        add_case_button.clicked.connect(self.add_case)
        add_case_button.setStyleSheet("QPushButton { font-size: 16px; }")

        back_button = QPushButton('Back', add_case_page)
        back_button.clicked.connect(self.show_main_page)
        back_button.setStyleSheet("QPushButton { font-size: 16px; }")


        add_case_layout.addWidget(criminalid_label)
        add_case_layout.addWidget(self.criminalid_input)
        add_case_layout.addWidget(case_description_label)
        add_case_layout.addWidget(self.case_description_input)
        add_case_layout.addWidget(invid_label)
        add_case_layout.addWidget(self.invid_officer_input)
        add_case_layout.addWidget(keyword_label)
        add_case_layout.addWidget(self.keyword_input)
        add_case_layout.addWidget(status_label)
        add_case_layout.addWidget(self.status_combo)
        add_case_layout.addWidget(dater_label)
        add_case_layout.addWidget(self.dater_input)
        add_case_layout.addWidget(datec_label)
        add_case_layout.addWidget(self.datec_input)
        add_case_layout.addWidget(result_label)
        add_case_layout.addWidget(self.result_input)
        add_case_layout.addWidget(add_case_button)
        add_case_layout.addWidget(back_button)




        self.stacked_widget.addWidget(add_case_page)


        # Create the "Close Case" page
        close_case_page = QWidget()
        close_case_layout = QVBoxLayout(close_case_page)

        case_id_label = QLabel('Case ID:', close_case_page)
        case_id_label.setStyleSheet("QLabel { color: #fff; font-size: 16px; }")
        self.case_id_input = QLineEdit(close_case_page)
        self.case_id_input.setStyleSheet("QLineEdit { font-size: 16px; }")
        fetch_case_button = QPushButton('Fetch Case Details', close_case_page)
        fetch_case_button.clicked.connect(self.fetch_and_display_case_details)
        fetch_case_button.setStyleSheet("QPushButton { font-size: 16px; }")

        close_button = QPushButton('Close Case', close_case_page)
        close_button.clicked.connect(self.close_case)
        close_button.setStyleSheet("QPushButton { font-size: 16px; }")

        back_button = QPushButton('Back', criminal_page)
        back_button.clicked.connect(self.show_main_page)
        back_button.setStyleSheet("QPushButton { font-size: 16px; }")

        self.criminals_table = QTableWidget(self)
        self.criminals_table.setColumnCount(12)
        self.criminals_table.setHorizontalHeaderLabels(["Criminal ID", "First Name", "Last Name", "DOB", "DOD", "Sex", "Case ID", "Keywords", "Station ID", "In Prison", "Res. Address", "Contact No."])
        self.criminals_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        header = self.criminals_table.horizontalHeader()
        header.setStyleSheet("QHeaderView::section { color: black; font-size: 18px; font-weight: bold;}")

        self.criminals_cases_table = QTableWidget(self)
        self.criminals_cases_table.setColumnCount(9)
        self.criminals_cases_table.setHorizontalHeaderLabels(["Case ID", "CriminalID", "Description", "Invgt. Station", "Keywords", "Status", "Date Reported", "Date Closed", "Result"])
        self.criminals_cases_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        header = self.criminals_cases_table.horizontalHeader()
        header.setStyleSheet("QHeaderView::section { color: black; font-size: 18px; font-weight: bold;}")

        self.police_station_table = QTableWidget(self)
        self.police_station_table.setColumnCount(6)
        self.police_station_table.setHorizontalHeaderLabels(["Station ID", "Name", "Location", "Contact", "Head Officer", "No. of Prisoners"])
        self.police_station_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        header = self.police_station_table.horizontalHeader()
        header.setStyleSheet("QHeaderView::section { color: black; font-size: 18px; font-weight: bold;}")

        close_case_layout.addWidget(case_id_label)
        close_case_layout.addWidget(self.case_id_input)
        close_case_layout.addWidget(fetch_case_button)
        close_case_layout.addWidget(self.criminals_cases_table)
        close_case_layout.addWidget(self.criminals_table)
        close_case_layout.addWidget(self.police_station_table)
        close_case_layout.addWidget(close_button)
        close_case_layout.addWidget(back_button)

        self.stacked_widget.addWidget(close_case_page)
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(QVBoxLayout(self))
        self.layout().addWidget(scroll_area)


    def fetch_and_display_case_details(self):
        case_id = int(self.case_id_input.text())
        cursor = self.db.cursor()
        select_query = f"SELECT * FROM criminal_cases WHERE CaseID = {case_id}"
        cursor.execute(select_query)
        criminal_cases = cursor.fetchall()
        if criminal_cases:
            self.criminals_cases_table.setRowCount(len(criminal_cases))
            for row, case_data in enumerate(criminal_cases):
                for col in range(len(case_data)):
                    item = QTableWidgetItem(str(case_data[col]))
                    self.criminals_cases_table.setItem(row, col, item)
        else:
            self.criminals_cases_table.setRowCount(0)
        select_query = f"SELECT CriminalID, FirstName, LastName, DOB, DOD, Sex, CaseID, Keywords, StationID, InPrison, Address, Contact FROM criminals WHERE CaseID = {case_id}"
        cursor.execute(select_query)
        criminal = cursor.fetchall()
        if criminal:
            self.criminals_table.setRowCount(len(criminal))
            for row, criminal_data in enumerate(criminal):
                for col in range(len(criminal_data)):
                    item = QTableWidgetItem(str(criminal_data[col]))
                    self.criminals_table.setItem(row, col, item)
        else:
            self.criminals_table.setRowCount(0)

        q = f"SELECT InvestigatingStationID FROM criminal_cases WHERE CaseID = {case_id}"
        cursor.execute(q)
        sid = cursor.fetchall()
        if len(sid) > 0:
            select_query = f"SELECT * FROM police_stations WHERE StationID = {int(sid[0][0])}"
            cursor.execute(select_query)
            police_stations = cursor.fetchall()
            if police_stations:
                self.police_station_table.setRowCount(len(police_stations))
                for row, station in enumerate(police_stations):
                    for col in range(len(station)):
                        item = QTableWidgetItem(str(station[col]))
                        self.police_station_table.setItem(row, col, item)
            else:
                self.police_station_table.setRowCount(0)
        
        

    def close_case(self):
        updated_status, ok = QInputDialog.getText(self, 'Update Status', 'Enter Updated Status (Closed/Pending):')
        if ok:
            case_id = self.case_id_input.text()
            update_query = "UPDATE criminal_cases SET Status = %s WHERE CaseID = %s"
            data = (updated_status, case_id)
            cursor = self.db.cursor()
            cursor.execute(update_query, data)
            self.db.commit()
            self.show_notification("Case Updated", f"Status of Case {case_id} updated to {updated_status}")





    def blur_background(self, widget):
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(10)  
        widget.setGraphicsEffect(blur)

    def apply_shine_effect(self, layout):
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item.widget():
                pal = item.widget().palette()
                pal.setColor(QPalette.Highlight, QColor("#888888")) 
                item.widget().setPalette(pal)

    def close_application(self):
        sys.exit()

    def show_police_stations_page(self):
        self.stacked_widget.setCurrentIndex(3)
        police_stations = self.get_police_stations()
        if police_stations:
            self.police_stations_table.setRowCount(len(police_stations))
            for row, station in enumerate(police_stations):
                for col in range(len(station)):
                    item = QTableWidgetItem(str(station[col]))
                    self.police_stations_table.setItem(row, col, item)
        else:
            self.police_stations_table.setRowCount(0)

    def show_close_case_page(self):
        self.stacked_widget.setCurrentIndex(7)

    def show_criminal_cases_page(self):
        self.stacked_widget.setCurrentIndex(4) 
        criminal_cases = self.get_criminal_cases()
        if criminal_cases:
            self.criminal_cases_table.setRowCount(len(criminal_cases))
            for row, case_data in enumerate(criminal_cases):
                for col in range(len(case_data)):
                    item = QTableWidgetItem(str(case_data[col]))
                    self.criminal_cases_table.setItem(row, col, item)
        else:
            self.criminal_cases_table.setRowCount(0)

    def show_add_case_page(self):
        self.stacked_widget.setCurrentIndex(6)

    def show_criminals_page(self):
        self.stacked_widget.setCurrentIndex(5) 
        criminals = self.get_criminals()
        if criminals:
            self.criminal_table.setRowCount(len(criminals))
            for row, criminal_data in enumerate(criminals):
                for col in range(len(criminal_data)):
                    item = QTableWidgetItem(str(criminal_data[col]))
                    self.criminal_table.setItem(row, col, item)
        else:
            self.criminal_table.setRowCount(0)

    def show_add_station_page(self):
        self.stacked_widget.setCurrentIndex(1)

    def show_add_criminal_page(self):
        self.stacked_widget.setCurrentIndex(2)

    def show_main_page(self):
        self.stacked_widget.setCurrentIndex(0)

    def add_station(self):
        name = self.name_input.text() 
        location = self.location_input.text()
        contact = self.contact_input.text()
        head_officer = self.head_officer_input.text()
        num_prisoners = self.num_prisoners_input.text()
        try:
            self.add_station_to_database(name, location, contact, head_officer, num_prisoners)
            self.name_input.clear()
            self.location_input.clear()
            self.contact_input.clear()
            self.head_officer_input.clear()
            self.num_prisoners_input.clear()
            self.show_notification("Station Added", f"{name} added to the database successfully!")
            self.show_main_page()

        except Exception as e:
            error_message = f"Operation Failed! Error: {e}"
            self.show_notification("Error", error_message)

    def add_station_to_database(self, name, location, contact, head_officer, num_prisoners):
        try:
            cursor = self.db.cursor()
            insert_query = "INSERT INTO police_stations (StationName, Location, Contact, HeadOfficer, NumberOfPrisoners) " \
                        "VALUES (%s, %s, %s, %s, %s)"
            data = (name, location, contact, head_officer, num_prisoners)
            cursor.execute(insert_query, data)
            self.db.commit()
        except Exception as e:
            raise e
        
    def add_case(self):
        criminalid = self.criminalid_input.text() if len(str(self.criminalid_input.text())) > 2 else None
        case_description = self.case_description_input.toPlainText()
        invid = self.invid_officer_input.text() if len(str(self.invid_officer_input.text())) > 2 else None
        keyword = self.keyword_input.text()
        status = self.status_combo.currentText()
        dateR = self.dater_input.text() if len(str(self.dater_input.text())) > 2 else None
        datec = self.datec_input.text() if len(str(self.datec_input.text())) > 2 else None
        result = self.result_input.text() if len(str(self.result_input.text())) > 2 else None
        try:
            self.add_case_to_database(criminalid, case_description, invid, keyword, status, dateR, datec, result)
            self.criminalid_input.clear()
            self.case_description_input.clear()
            self.invid_officer_input.clear()
            self.keyword_input.clear()
            self.dater_input.clear()
            self.datec_input.clear()
            self.result_input.clear()
            self.show_notification("Case Added", f"{dateR} added to the database successfully!")
            self.show_main_page()
        except Exception as e:
            error_message = f"Operation Failed! Error: {e}"
            self.show_notification("Error", error_message)

    def add_case_to_database(self, criminalid, case_description, invid, keyword, status, dateR, datec, result):
        try:
            cursor = self.db.cursor()
            insert_query = "INSERT INTO criminal_cases (CriminalID, CaseDescription, InvestigatingStationID, Keywords, Status, DateReported, DateClosed, ResultOutcome) " \
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            data = (criminalid, case_description, invid, keyword, status, dateR, datec, result)
            cursor.execute(insert_query, data)
            self.db.commit()
        except Exception as e:
            raise e
        
    def add_criminal(self):
        first_name = self.first_name_input.text()
        last_name = self.last_name_input.text() if len(str(self.last_name_input.text())) > 2 else None
        dob_date = self.dob_input.date()
        dod = self.dod_input.text() if len(str(self.dod_input.text())) > 2 else None
        sex = self.gender_combo.currentText()
        caseid = self.caseid_input.text() if len(str(self.caseid_input.text())) > 2 else None
        keywords = self.keywords_input.text() if len(str(self.keywords_input.text())) > 2 else None
        stationid = self.stationid_input.text() if len(str(self.stationid_input.text())) > 2 else None
        inprison = self.inprison_combo.currentText()
        address = self.address_input.text() if len(str(self.address_input.text())) > 2 else None
        contact = self.contact_input.text() if len(str(self.contact_input.text())) > 2 else None
        photo = self.convert_image_to_binary(self.photo_input.text()) if (len(str(self.photo_input.text())) > 2) else None
        dob = dob_date.toString(Qt.ISODate) if dob_date.isValid() else None
        try:
            self.add_criminal_to_database(first_name,
                                          last_name,
                                          dob,
                                          dod,
                                          sex,
                                          caseid,
                                          keywords,
                                          stationid,
                                          inprison,
                                          address,
                                          contact,
                                          photo)
            self.first_name_input.clear()
            self.last_name_input.clear()
            self.caseid_input.clear()
            self.keywords_input.clear()
            self.stationid_input.clear()
            self.address_input.clear()
            self.contact_input.clear()
            self.show_notification("Criminal Added", f"{first_name} added to the database successfully!")
            self.show_main_page()
        except Exception as e:
            error_message = f"Operation Failed! Error: {e}"
            self.show_notification("Error", error_message)

    def add_criminal_to_database(self, FirstName, LastName=None, DOB=None, DOD=None, Sex=None, CaseID=None, Keywords=None, StationID=None, InPrison=None, Address=None, Contact=None, Photo=None):
        try:
            cursor = self.db.cursor()
            insert_query = "INSERT INTO criminals (FirstName, LastName, DOB, DOD, Sex, CaseID, Keywords, StationID, InPrison, Address, Contact, Photo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            data = (FirstName, LastName, DOB, DOD, Sex, CaseID, Keywords, StationID, InPrison, Address, Contact, Photo)
            cursor.execute(insert_query, data)
            self.db.commit()
        except Exception as e:
            raise e

    def browse_photo(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Image Files (*.png *.jpg *.bmp)")
        file_dialog.setViewMode(QFileDialog.Detail)
        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            self.photo_input.setText(file_path)

    def convert_image_to_binary(self, image_path):
        with open(image_path, "rb") as file:
            binary_data = file.read()
        return binary_data


    def get_police_stations(self):
        try:
            cursor = self.db.cursor()
            select_query = "SELECT * FROM police_stations"
            cursor.execute(select_query)
            police_stations = cursor.fetchall()
            return police_stations
        except Exception as e:
            print(f"Error fetching police stations: {e}")
            return None
        
    def get_criminal_cases(self):
        try:
            cursor = self.db.cursor()
            select_query = "SELECT * FROM criminal_cases"
            cursor.execute(select_query)
            criminal_cases = cursor.fetchall()
            return criminal_cases
        except Exception as e:
            print(f"Error fetching criminal cases: {e}")
            return None

    def get_criminals(self):
        try:
            cursor = self.db.cursor()
            select_query = "SELECT CriminalID, FirstName, LastName, DOB, DOD, Sex, CaseID, Keywords, StationID, InPrison, Address, Contact FROM criminals"
            cursor.execute(select_query)
            criminals = cursor.fetchall()
            return criminals
        except Exception as e:
            print(f"Error fetching criminals: {e}")
            return None
        

    def delete_criminal(self):
        selected_row = self.criminal_table.currentRow()
        if selected_row == -1:
            self.show_notification("Error", "Please select a criminal to delete.")
            return
        criminal_id_item = self.criminal_table.item(selected_row, 0)
        criminal_id = criminal_id_item.text()
        confirm_dialog = QMessageBox.question(
            self,
            "Confirmation",
            f"Are you sure you want to remove Criminal ID {criminal_id} from the database?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm_dialog == QMessageBox.Yes:
            try:
                cursor = self.db.cursor()
                delete_query = "DELETE FROM criminals WHERE CriminalID = %s"
                data = (criminal_id,)
                cursor.execute(delete_query, data)
                self.db.commit()

                self.show_notification("Success", "Criminal data deleted successfully!")
                self.criminal_table.removeRow(selected_row)

            except Exception as e:
                print(f"Error deleting criminal data: {e}")
                self.show_notification("Error", f"Deletion Failed! Error: {e}")
        else:
            self.show_notification("Deletion Cancelled", "Criminal data deletion cancelled.")

    def delete_case(self):
        selected_row = self.criminal_cases_table.currentRow()
        if selected_row == -1:
            self.show_notification("Error", "Please select a case to delete.")
            return
        case_id_item = self.criminal_cases_table.item(selected_row, 0)
        case_id = case_id_item.text()
        confirm_dialog = QMessageBox.question(
            self,
            "Confirmation",
            f"Are you sure you want to remove Case ID {case_id} from the database?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm_dialog == QMessageBox.Yes:
            try:
                cursor = self.db.cursor()
                delete_query = "DELETE FROM criminal_cases WHERE CaseID = %s"
                data = (case_id,)
                cursor.execute(delete_query, data)
                self.db.commit()
                self.show_notification("Success", "Case data deleted successfully!")
                self.criminal_cases_table.removeRow(selected_row)
            except Exception as e:
                print(f"Error deleting case data: {e}")
                self.show_notification("Error", f"Deletion Failed! Error: {e}")
        else:
            self.show_notification("Deletion Cancelled", "Case data deletion cancelled.")

    def update_case(self):
        try:
            cursor = self.db.cursor()
            # self.criminal_cases_table.setHorizontalHeaderLabels(["Case ID", "CriminalID", "Description", "Invgt. Station", "Keywords", "Status", "Date Reported", "Date Closed", "Result"])
            for row in range(self.criminal_cases_table.rowCount()):
                case_id = self.criminal_cases_table.item(row, 0).text() if ((len(str(self.criminal_cases_table.item(row, 0).text())) >= 1) and str(self.criminal_cases_table.item(row, 0).text()) != 'None') else None
                criminal_id = self.criminal_cases_table.item(row, 1).text() if ((len(str(self.criminal_cases_table.item(row, 1).text())) >= 1) and str(self.criminal_cases_table.item(row, 1).text()) != 'None') else None
                Description = self.criminal_cases_table.item(row, 2).text() 
                stationid = self.criminal_cases_table.item(row, 3).text() if ((len(str(self.criminal_cases_table.item(row, 3).text())) >= 1) and str(self.criminal_cases_table.item(row, 3).text()) != 'None') else None
                keywords = self.criminal_cases_table.item(row, 4).text() if ((len(str(self.criminal_cases_table.item(row, 4).text())) > 1) and str(self.criminal_cases_table.item(row, 4).text()) != 'None') else None
                status = self.criminal_cases_table.item(row, 5).text() if ((len(str(self.criminal_cases_table.item(row, 5).text())) > 1) and str(self.criminal_cases_table.item(row, 5).text()) != 'None') else None
                date_open = self.criminal_cases_table.item(row, 6).text() if ((len(str(self.criminal_cases_table.item(row, 6).text())) > 1) and str(self.criminal_cases_table.item(row, 6).text()) != 'None') else None
                date_close = self.criminal_cases_table.item(row, 7).text() if ((len(str(self.criminal_cases_table.item(row, 7).text())) > 1) and str(self.criminal_cases_table.item(row, 7).text()) != 'None') else None
                result = self.criminal_cases_table.item(row, 8).text() if ((len(str(self.criminal_cases_table.item(row, 8).text())) > 1) and str(self.criminal_cases_table.item(row, 8).text()) != 'None') else None
                update_query = "UPDATE criminal_cases SET CriminalID = %s, CaseDescription = %s, InvestigatingStationID = %s, Keywords = %s, Status = %s, DateReported = %s, DateClosed = %s, ResultOutcome = %s WHERE CaseID = %s"
                data = (criminal_id, Description, stationid, keywords, status, date_open, date_close, result, case_id)
                cursor.execute(update_query, data)
            self.db.commit()
            self.show_notification("Update Successful", "Case data updated successfully!")
        except Exception as e:
            error_message = f"Update Failed! Error: {e}"
            self.show_notification("Error", error_message)

    def update_criminal_data(self):
        try:
            cursor = self.db.cursor()
            for row in range(self.criminal_table.rowCount()):
                criminal_id = self.criminal_table.item(row, 0).text() if ((len(str(self.criminal_table.item(row, 0).text())) >= 1) and str(self.criminal_table.item(row, 0).text()) != 'None') else None
                first_name = self.criminal_table.item(row, 1).text() 
                last_name = self.criminal_table.item(row, 2).text() if ((len(str(self.criminal_table.item(row, 2).text())) >= 1) and str(self.criminal_table.item(row, 2).text()) != 'None') else None
                dob = self.criminal_table.item(row, 3).text() if ((len(str(self.criminal_table.item(row, 3).text())) > 1) and str(self.criminal_table.item(row, 3).text()) != 'None') else None
                dod = self.criminal_table.item(row, 4).text() if ((len(str(self.criminal_table.item(row, 4).text())) > 1) and str(self.criminal_table.item(row, 4).text()) != 'None') else None
                sex = self.criminal_table.item(row, 5).text() if ((len(str(self.criminal_table.item(row, 5).text())) >= 1) and str(self.criminal_table.item(row, 5).text()) != 'None') else None
                caseid = self.criminal_table.item(row, 6).text() if ((len(str(self.criminal_table.item(row, 6).text())) >= 1) and str(self.criminal_table.item(row, 6).text()) != 'None') else None
                keywords = self.criminal_table.item(row, 7).text() if ((len(str(self.criminal_table.item(row, 7).text())) > 1) and str(self.criminal_table.item(row, 7).text()) != 'None') else None
                stationid = self.criminal_table.item(row, 8).text() if ((len(str(self.criminal_table.item(row, 8).text())) >= 1) and str(self.criminal_table.item(row, 8).text()) != 'None') else None
                inprison = self.criminal_table.item(row, 9).text() if ((len(str(self.criminal_table.item(row, 9).text())) >= 1) and str(self.criminal_table.item(row, 9).text()) != 'None') else None
                address = self.criminal_table.item(row, 10).text() if ((len(str(self.criminal_table.item(row, 10).text())) > 1) and str(self.criminal_table.item(row, 10).text()) != 'None') else None
                contact = self.criminal_table.item(row, 11).text() if ((len(str(self.criminal_table.item(row, 11).text())) > 1) and str(self.criminal_table.item(row, 11).text()) != 'None') else None
                update_query = "UPDATE criminals SET FirstName = %s, LastName = %s, DOB = %s, DOD = %s, Sex = %s, CaseID = %s, Keywords = %s, StationID = %s, InPrison = %s, Address = %s, Contact = %s WHERE CriminalID = %s"
                data = (first_name, last_name, dob, dod, sex, caseid, keywords, stationid, inprison, address, contact, criminal_id)
                cursor.execute(update_query, data)
            self.db.commit()
            self.show_notification("Update Successful", "Criminal data updated successfully!")
        except Exception as e:
            error_message = f"Update Failed! Error: {e}"
            self.show_notification("Error", error_message)

    def update_station(self):
        try:
            cursor = self.db.cursor()
            for row in range(self.police_stations_table.rowCount()):
                station_id = self.police_stations_table.item(row, 0).text() if ((len(str(self.police_stations_table.item(row, 0).text())) >= 1) and str(self.police_stations_table.item(row, 0).text()) != 'None') else None
                name = self.police_stations_table.item(row, 1).text() 
                location = self.police_stations_table.item(row, 2).text() if ((len(str(self.police_stations_table.item(row, 2).text())) >= 1) and str(self.police_stations_table.item(row, 2).text()) != 'None') else None
                contact = self.police_stations_table.item(row, 3).text() if ((len(str(self.police_stations_table.item(row, 3).text())) > 1) and str(self.police_stations_table.item(row, 3).text()) != 'None') else None
                head_officer = self.police_stations_table.item(row, 4).text() if ((len(str(self.police_stations_table.item(row, 4).text())) > 1) and str(self.police_stations_table.item(row, 4).text()) != 'None') else None
                num_prisoners = int(self.police_stations_table.item(row, 5).text()) if ((len(str(self.police_stations_table.item(row, 5).text())) >= 1) and str(self.police_stations_table.item(row, 5).text()) != 'None') else None
                update_query = "UPDATE police_stations SET StationName = %s, Location = %s, Contact = %s, HeadOfficer = %s, NumberOfPrisoners = %s WHERE StationID = %s"
                data = (name, location, contact, head_officer, num_prisoners, station_id)
                cursor.execute(update_query, data)
            self.db.commit()
            self.show_notification("Update Successful", "Station data updated successfully!")
        except Exception as e:
            error_message = f"Update Failed! Error: {e}"
            self.show_notification("Error", error_message)

    def delete_station(self):
        selected_row = self.police_stations_table.currentRow()
        if selected_row == -1:
            self.show_notification("Error", "Please select a station to delete.")
            return
        station_id_item = self.police_stations_table.item(selected_row, 0)
        station_id = station_id_item.text()
        confirm_dialog = QMessageBox.question(
            self,
            "Confirmation",
            f"Are you sure you want to remove Station ID {station_id} from the database?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm_dialog == QMessageBox.Yes:
            try:
                cursor = self.db.cursor()
                delete_query = "DELETE FROM police_stations WHERE StationID = %s"
                data = (station_id,)
                cursor.execute(delete_query, data)
                self.db.commit()
                self.show_notification("Success", "Station data deleted successfully!")
                self.police_stations_table.removeRow(selected_row)
            except Exception as e:
                print(f"Error deleting station data: {e}")
                self.show_notification("Error", f"Deletion Failed! Error: {e}")
        else:
            self.show_notification("Deletion Cancelled", "Station data deletion cancelled.")

    def convert_binary_to_image(self, binary_data):
        image = Image.open(io.BytesIO(binary_data))
        return image

    def display_images(self, known_image_array, unknown_image_array, known_title, unknown_title):
        plt.subplot(1, 2, 1)
        plt.imshow(known_image_array)
        plt.title(known_title)
        plt.axis('off')
        plt.subplot(1, 2, 2)
        plt.imshow(unknown_image_array)
        plt.title(unknown_title)
        plt.axis('off')
        plt.show()

    def show_notification(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()

    def connect_to_database(self):
        try:
            db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="iamts@84",
                database="crime_management"
            )
            return db
        except mysql.connector.Error as e:
            print(f"Error: {e}")
            sys.exit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CrimeAnalysisApp()
    window.show()
    sys.exit(app.exec_())
