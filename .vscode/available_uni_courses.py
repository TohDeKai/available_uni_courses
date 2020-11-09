# Importing essential modules
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileReader
from pathlib import Path
import pdfplumber
import pprint
from selenium import webdriver
import re


# A-Level Grades Conversion to UAS
grade_to_uas = {"A": 20, "B": 17.5, "C": 15, "D": 12.5, "E": 10, "S": 5, "U": 0}

def convert_igp_to_uas(igp):
    uas = 0
    for i in igp[:3]:
        uas += grade_to_uas[i]
    uas += grade_to_uas[igp[4]]/2
    uas += 15
    return uas


# Ask user to enter their A - Levels Score
print ("Please enter your A Level Score")
h2_1 = input('What is the grade of your first H2?').upper()
h2_2 = input('What is the grade of your second H2?').upper()
h2_3 = input('What is the grade of your third H2?').upper()
h1 = input('What is the grade of your H1?').upper()
gp = input('What is the grade of your General Paper?').upper()
pw = input('What is the grade of your Project Work?').upper()


# Calculating to UAS
try:
    h2_total = grade_to_uas[h2_1] + grade_to_uas[h2_2] + grade_to_uas[h2_3]
    h1_total = (grade_to_uas[gp] + grade_to_uas[pw] + grade_to_uas[h1])/2
    total_uas = h2_total + h1_total
    print (f'Your UAS is {total_uas}')
    print ('\n')
except KeyError:
    print ("Only letter grades are accepted. For example, \"A\" or \"B\"")

# Web - Scraping

#NUS

URL_NUS = 'http://www.nus.edu.sg/oam/undergraduate-programmes/indicative-grade-profile-(igp)'
nus_page = requests.get(URL_NUS)
nus_soup = BeautifulSoup(nus_page.content, 'html.parser')
nus_results = nus_soup.find(id='ContentPlaceHolder_contentPlaceholder_TC88F994D007_Col00')

nus_igp_elems = nus_results.find_all("tr", class_=False, id=False)

#Data starts from Index 3 : Faculty of Law, ends at Index 47

for i in nus_igp_elems[3:48]:
    course_elem = i.find('td',  class_=False, id=False)
    igp_grades = i.find('div', class_=False, id=False)
    if igp_grades == None:
        continue
    uas_for_course = 0
    for i in igp_grades.text[:4]:
        if i == '/':
            continue
        uas_for_course += grade_to_uas[i]
    uas_for_course += grade_to_uas[igp_grades.text[4]]/2
    # Since GP and PW assumed to be C
    uas_for_course += 15
    if uas_for_course <= total_uas:
        print ('NUS',",",course_elem.text,",",uas_for_course) 
        print ('\n')



#NTU
# URL_NTU = 'https://www3.ntu.edu.sg/oad2/website_files/IGP/NTU_IGP.pdf'


filename = Path('NTU_IGP.pdf')
url = 'https://www3.ntu.edu.sg/oad2/website_files/IGP/NTU_IGP.pdf'
response = requests.get(url)
filename.write_bytes(response.content)

pdf_path='NTU_IGP.pdf'
pdf = PdfFileReader(str(pdf_path))

with pdfplumber.open('NTU_IGP.pdf') as pdf:
    second_page = pdf.pages[1]
    third_page = pdf.pages[2]
    ntu_course_list = []
    for i in second_page.extract_table():
        if i[0] == None or i[0] == "":
            continue
        course_and_igp = []
        course_and_igp.append(i[0])
        course_and_igp.append(i[2])
        ntu_course_list.append(course_and_igp)
    for i in third_page.extract_table():
        if i[0] == None or i[0] == "":
            continue
        course_and_igp = []
        course_and_igp.append(i[0])
        course_and_igp.append(i[2])
        ntu_course_list.append(course_and_igp)

for i in ntu_course_list:
    coursename = i[0]
    uas_for_course = 0
    if i[1] == "":
        continue
    for char in i[1][:4]:
        if char == '/':
            continue
        uas_for_course += grade_to_uas[char]
    uas_for_course += grade_to_uas[i[1][4]]/2
    # Since GP and PW assumed to be C
    uas_for_course += 15
    if uas_for_course <= total_uas:
        print ('NTU',",",coursename,",",uas_for_course)
        print ('\n')


#SMU
#Cannot scrape:"Request unsuccessful. Incapsula incident"
#So I inspected page source, copied and pasted it into a text file instead
URL_SMU = 'https://admissions.smu.edu.sg/admissions/indicative-grade-profiles-igp'
smu = open("SMU_IGP.txt", encoding="utf8")
smufile = smu.read()
smu_soup = BeautifulSoup(smufile, 'html.parser')
smu_results = smu_soup.find(id="content IndicativeGradeProfiles(IGP)")
smu_igp_elems = smu_results.find_all("td", class_=False, id=False)

def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

#Data starts from Index 4, ends at Index 25

for i in range(len(smu_igp_elems[4:25])):
    html_tags_removed = (remove_html_tags(str(smu_igp_elems[i+4])))
    course_name_regex =  re.search("Bachelor", html_tags_removed)
    uas_for_course = 0
    if course_name_regex:
        course_name = (html_tags_removed)
        igp_grades = (remove_html_tags(str(smu_igp_elems[i+5])))
        uas_for_course = convert_igp_to_uas(igp_grades)
        if uas_for_course <= total_uas:
            print ('SMU ,',course_name, uas_for_course)
            print ('\n')
