#Importing Required Packages.
import cv2
import pytesseract
import re
import mysql.connector as mc
import cv2
import numpy as np
from PIL import Image
from datetime import datetime

pytesseract.pytesseract.tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class PAN_OCR:
    def __init__(self, img_path):
        self.user_pan_no = str()
        self.user_name = str()
        self.user_dob = str()
        self.img_name = img_path
    
    def extract_data(self):
        # Reading the image, extracting text from it, and storing the text into a list.
        img = cv2.imread(self.img_name)
        text = pytesseract.image_to_string(img)
        all_text_list = re.split(r'[\n]', text)
        
        # Process the text list to remove all whitespace elements in the list.
        text_list = list()

        for i in all_text_list:
            if re.match(r'^(\s)+$', i) or i=='':
                continue
            else:
                text_list.append(i)

        # Extracting all the necessary details from the pruned text list.
        # 1) PAN Card No.
        lineno = 0
        pan_no_pat = r'Permanent Account Number Card|Permanent Account Number|Permanent Account|Permanent'
        pan_no = str()
        for i, text in enumerate(text_list):
            if re.match(pan_no_pat, text):
                lineno = i+1
                pan_no = text_list[i+1]
            else:
                continue

        for i in pan_no:
            if i.isalnum() and len(pan_no) == 10 and pan_no[0:5].isalpha() and pan_no[5:9].isdigit() and pan_no[-1:].isalpha():
                self.user_pan_no = self.user_pan_no + i
            else:
                continue
    
        name = None
        dob = None
        name = str()
        # pan_name = r'(NAME|name|Name)$'
        # for i, text in enumerate(text_list):
        #     if re.match(pan_name, text):
        #         name = text_list[i+1]
        #     else:
        #         continue
        name = text_list[lineno+2]
        # name = text_list[lineno+2]

        dob = str()
        dob_check = r'DOB|Date of Birth|DATE OF BIRTH|DATE|BIRTH|IRTH|date|dob'
        for i, text in enumerate(text_list):
            if re.match(dob_check, text):
                dob = text_list[i+1]
                # dob = text_list[i+3]
            else:
                continue

        try:
            # Cleaning first names
            name = name.rstrip()
            name = name.lstrip()
            name = name.replace("8", "B")
            name = name.replace("0", "D")
            name = name.replace("6", "G")
            name = name.replace("1", "I")
            name = re.sub('[^a-zA-Z] +', ' ', name)
            # Cleaning DOB
            dob = dob.rstrip()
            dob = dob.lstrip()
            dob = dob.replace('l', '/')
            dob = dob.replace('L', '/')
            dob = dob.replace('I', '/')
            dob = dob.replace('i', '/')
            dob = dob.replace('|', '/')
            dob = dob.replace('\"', '/1')
            dob = dob.replace(" ", "")
            dob = datetime.strptime(dob, '%d/%m/%Y').date()

        except:
            pass
        self.user_name = name
        self.user_dob = dob

        return [self.user_pan_no, self.user_name, self.user_dob]

    def findword(textlist, wordstring):
        lineno = -1
        for wordline in textlist:
            xx = wordline.split( )
            if ([w for w in xx if re.search(wordstring, w)]):
                lineno = textlist.index(wordline)
                textlist = textlist[lineno+1:]
                return textlist
    
    def commit_changes(self, pan_no, name, dob):
        # Commit details to a mysql database
        # Change the 'database' attribute in the line below to match your database and make sure that the server is running before executing this code.
        # mydb = mc.connect(host='localhost', user='root', passwd='root', database='fyp_pan')
        mydb = mc.connect(host='localhost', user='root', database='fyp_pan')
        mycursor = mydb.cursor()

        # Make sure that the table, attribute names match the ones in your database.
        insert_query = "Insert into card_details(pan_no, name, dob) values(%s, %s, %s)"
        card_details = (pan_no, name, dob)

        mycursor.execute(insert_query, card_details)

        mydb.commit()
