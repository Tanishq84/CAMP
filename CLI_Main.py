#!/usr/bin/env python

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
from prettytable import PrettyTable
from colorama import Fore, Style, init
init(autoreset=True)


db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="crime_management"
)
cursor = db.cursor()

def convert_image_to_binary(image_path):
    with open(image_path, "rb") as file:
        binary_data = file.read()
    return binary_data

def convert_binary_to_image(binary_data):
    image = Image.open(io.BytesIO(binary_data))
    return image

def display_images(known_image_array, unknown_image_array, known_title, unknown_title):
    plt.subplot(1, 2, 1)
    plt.imshow(known_image_array)
    plt.title(known_title)
    plt.axis('off')
    plt.subplot(1, 2, 2)
    plt.imshow(unknown_image_array)
    plt.title(unknown_title)
    plt.axis('off')
    plt.show()

def print_table(header, data):
    t = Texttable()
    t.add_row(header)
    for row in data:
        t.add_row(row)
    print(t.draw())

def add_station(name, location=None, contact=None, head_officer=None, num_prisoners=None):
    try:        
        insert_query = "INSERT INTO police_stations (StationName, Location, Contact, HeadOfficer, NumberOfPrisoners) VALUES (%s, %s, %s, %s, %s)"
        data = (name, location, contact, head_officer, num_prisoners)
        cursor.execute(insert_query, data)
        db.commit()
        print(f"{name} added to the database successfully!")
    except:  
        print("Operation Failed! Please try again later.")

def add_criminal(FirstName, LastName=None, DOB=None, DOD=None, Sex=None, CaseID=None, Keywords=None, StationID=None, InPrison=None, Address=None, Contact=None, Photo=None):
    try:
        insert_query = "INSERT INTO criminals (FirstName, LastName, DOB, DOD, Sex, CaseID, Keywords, StationID, InPrison, Address, Contact, Photo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        data = (FirstName, LastName, DOB, DOD, Sex, CaseID, Keywords, StationID, InPrison, Address, Contact, Photo)
        cursor.execute(insert_query, data)
        db.commit()
        print("Criminal added successfully!")
    except:
        print("Operation Failed! Please try again later.")

def add_case(CriminalID=None, CaseDescription=None, InvestigatingStationID=None, Keywords=None, Status="Pending", DateReported=None):
    try:
        if DateReported is None:
            DateReported = datetime.now().strftime('%Y-%m-%d')
        insert_query = "INSERT INTO criminal_cases (CriminalID, CaseDescription, InvestigatingStationID, Keywords, Status, DateReported, DateClosed, ResultOutcome) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        data = (CriminalID, CaseDescription, InvestigatingStationID, Keywords, Status, DateReported, None, None)
        cursor.execute(insert_query, data)
        db.commit()
        print("Case filed successfully!")
    except:
        print("Operation Failed! Please try again later.")

def close_case(CaseID, ResultOutcome, DateClosed=None):
    try:
        if DateClosed is None:
            DateClosed = datetime.now().strftime('%Y-%m-%d')
        update_query = "UPDATE criminal_cases SET Status = 'Closed', DateClosed = %s, ResultOutcome = %s WHERE CaseID = %s"
        update_data = (DateClosed, ResultOutcome, CaseID)
        cursor.execute(update_query, update_data)
        db.commit()
        print("Case Closed successfully!")
        query = f"SELECT * FROM criminal_cases WHERE CaseID = {CaseID}"
        cursor.execute(query)
        case = cursor.fetchall()
        t = Texttable()
        t.add_rows([["CaseID", "CriminalID", "CaseDescription", "InvestigatingStationID", "Keywords", "Status", "DateReported", "DateClosed", "ResultOutcome"], case[0]])
        print(t.draw())
    except:
        print("Operation Failed! Please try again later.")

def search_criminal_case_by_id(case_id):
    query = f"SELECT * FROM criminal_cases WHERE CaseID = {case_id}"
    cursor.execute(query)
    result = cursor.fetchall()
    if result:
        header = ["CaseID", "CriminalID", "CaseDescription", "InvestigatingStationID", "Keywords", "Status", "DateReported", "DateClosed", "ResultOutcome"]
        data = [list(map(str, result[0]))]
        print_table(header, data)
    else:
        print("No matching criminal case found.")

def search_criminal_case_by_status(status):
    query = f"SELECT * FROM criminal_cases WHERE Status = '{status}'"
    cursor.execute(query)
    result = cursor.fetchall()
    if result:
        header = ["CaseID", "CriminalID", "CaseDescription", "InvestigatingStationID", "Keywords", "Status", "DateReported", "DateClosed", "ResultOutcome"]
        data = [list(map(str, row)) for row in result]
        print_table(header, data)
    else:
        print(f"No criminal cases with status '{status}' found.")

def search_criminal_by_id(criminal_id):
    query = f"SELECT * FROM criminals WHERE CriminalID = {criminal_id}"
    cursor.execute(query)
    result = cursor.fetchall()
    if result:
        header = ["CriminalID", "FirstName", "LastName", "DOB", "DOD", "Sex", "CaseID", "Keywords", "StationID", "InPrison", "Address", "Contact"]
        data = [list(map(str, result[0][:-1]))]
        print_table(header, data)
    else:
        print("No matching criminal found.")

def search_police_station_by_id(station_id):
    query = f"SELECT * FROM police_stations WHERE StationID = {station_id}"
    cursor.execute(query)
    result = cursor.fetchall()
    if result:
        header = ["StationID", "StationName", "Location", "Contact", "HeadOfficer", "NumberOfPrisoners"]
        data = [list(map(str, result[0]))]
        print_table(header, data)
    else:
        print("No matching police station found.")

def img_search(bphoto):
    unknown_image_data = convert_binary_to_image(bphoto)
    unknown_image_array = np.array(unknown_image_data)
    unknown_encoding = face_recognition.face_encodings(unknown_image_array)[0]
    query = f"SELECT photo, CriminalID, FirstName, LastName, DOB, DOD, Sex, CaseID, Keywords, StationID, InPrison, Address, Contact FROM criminals"
    cursor.execute(query)
    result = cursor.fetchall()
    if result:
        for match in result:
            known_image_data = convert_binary_to_image(match[0])
            known_image_array = np.array(known_image_data)
            known_encoding = face_recognition.face_encodings(known_image_array)[0]
            results = face_recognition.compare_faces([known_encoding], unknown_encoding)
            if results[0]:
                print("Match Found!!")
                header = ["CriminalID", "FirstName", "LastName", "DOB", "DOD", "Sex", "CaseID", "Keywords", "StationID", "InPrison", "Address", "Contact"]
                data = [list(map(str, match[1:]))]
                print_table(header, data)
                display_images(known_image_array, unknown_image_array, str(data[0][1] + ' ' + data[0][2]), "Unknown Image")
                break
            else:
                if match == result[-1]:
                    print("No matching photo found.")
    else:
        print("No matching photo found.")

if __name__ == '__main__':
    while True:
        print("\n" + Fore.WHITE + "***************************************")
        print("*" + Fore.GREEN + "      Crime Management System        " + Fore.WHITE + "*")
        print("***************************************")
        print("1. Add Police Station")
        print("2. Add Criminal")
        print("3. Add Criminal Case")
        print("4. Close Criminal Case")
        print("5. Search Criminal Case by ID")
        print("6. Search Criminal Case by Status")
        print("7. Search Criminal by ID")
        print("8. Search Police Station by ID")
        print("9. Image Search")
        print("0. Exit")
        choice = input("Enter your choice (0-9): ")
        if choice == '1':
            # Add Police Station
            name = input("Enter Station Name: ")
            location = input("Enter Location: ")
            contact = input("Enter Contact: ")
            head_officer = input("Enter Head Officer: ")
            num_prisoners = input("Enter Number of Prisoners: ")
            add_station(name, location, contact, head_officer, num_prisoners)
        elif choice == '2':
            # Add Criminal
            FirstName = input("Enter First Name: ")
            LastName = input("Enter Last Name: ")
            DOB = input("Enter Date of Birth (YYYY-MM-DD): ")
            DOD = input("Enter Date of Death (YYYY-MM-DD): ")
            Sex = input("Enter Sex: ")
            CaseID = input("Enter Case ID: ")
            Keywords = input("Enter Keywords: ")
            StationID = input("Enter Station ID: ")
            InPrison = input("Is the criminal in prison? (Y/N): ")
            Address = input("Enter Address: ")
            Contact = input("Enter Contact: ")
            Photo = input("Enter path to Photo: ")
            add_criminal(FirstName, LastName, DOB, DOD, Sex, CaseID, Keywords, StationID, InPrison, Address, Contact, convert_image_to_binary(Photo))
        elif choice == '3':
            # Add Criminal Case
            CriminalID = input("Enter Criminal ID: ")
            CaseDescription = input("Enter Case Description: ")
            InvestigatingStationID = input("Enter Investigating Station ID: ")
            Keywords = input("Enter Keywords: ")
            add_case(CriminalID, CaseDescription, InvestigatingStationID, Keywords)
        elif choice == '4':
            # Close Criminal Case
            CaseID = input("Enter Case ID to close: ")
            ResultOutcome = input("Enter Result Outcome: ")
            close_case(CaseID, ResultOutcome)
        elif choice == '5':
            # Search Criminal Case by ID
            case_id = input("Enter Case ID: ")
            search_criminal_case_by_id(case_id)
        elif choice == '6':
            # Search Criminal Case by Status
            status = input("Enter Status: ")
            search_criminal_case_by_status(status)
        elif choice == '7':
            # Search Criminal by ID
            criminal_id = input("Enter Criminal ID: ")
            search_criminal_by_id(criminal_id)
        elif choice == '8':
            # Search Police Station by ID
            station_id = input("Enter Station ID: ")
            search_police_station_by_id(station_id)
        elif choice == '9':
            # Image Search
            photo_path = input("Enter path to the photo: ")
            img_search(convert_image_to_binary(photo_path))
        elif choice == '0':
            # Exit
            print("\n" + Fore.RED + "Exiting Crime Management System. Goodbye!")
            break
        else:
            print("\n" + Fore.RED + "Invalid choice. Please enter a number between 0 and 9.")

