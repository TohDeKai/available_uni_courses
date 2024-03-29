from bs4 import BeautifulSoup
import requests
import re
from PyPDF2 import PdfFileReader
from pathlib import Path
import pdfplumber
import csv


def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def convert_igp_to_uas(igp):
    grade_to_uas = {"A": 20, "B": 17.5, "C": 15, "D": 12.5, "E": 10, "S": 5, "U": 0}
    uas = 0
    for i in igp[:3]:
        uas += grade_to_uas[i]
    uas += grade_to_uas[igp[4]]/2
    uas += 15
    return uas

#NUS

#Scraping NUS data
URL_NUS = 'https://www.nus.edu.sg/oam/undergraduate-programmes/indicative-grade-profile-(igp)'
nus_page = requests.get(URL_NUS)
nus_soup = BeautifulSoup(nus_page.content, 'html.parser')
nus_results = nus_soup.find(id='ContentPlaceHolder_contentPlaceholder_TC88F994D007_Col00')
nus_igp_elems = nus_results.find_all("tr", class_=False, id=False)

#Cleaning up NUS data
#I want data to be an array. [[course1],[course2]...]
#Inside each course should be [school][name][IGP][UAS]

nus_courses = []
for i in nus_igp_elems[3:49]:
    course = []
    course_elem = i.find('td',  class_=False, id=False)
    igp_grades = i.find('div', class_=False, id=False)
    if course_elem == None or igp_grades == None:
        continue
    else:
        if bool(re.match(r'\w{3}/\w{1}', igp_grades.text)) == False:
            continue   
    uas = convert_igp_to_uas(igp_grades.text)
    course.append('NUS')
    course.append(course_elem.text)
    course.append(igp_grades.text)
    course.append(uas)

    nus_courses.append(course)


#SMU

#Scraping SMU Data

#Cannot scrape:"Request unsuccessful. Incapsula incident"
#So I inspected page source, copied and pasted it into a text file instead
smu = open("SMU_IGP.txt", encoding="utf8")
smufile = smu.read()
smu_soup = BeautifulSoup(smufile, 'html.parser')
smu_results = smu_soup.find(id="content IndicativeGradeProfiles(IGP)")
smu_igp_elems = smu_results.find_all("td", class_=False, id=False)

#Data Cleanup
smu_courses = []
for i in range(len(smu_igp_elems[4:25])):
    course = []
    html_tags_removed = (remove_html_tags(str(smu_igp_elems[i+4])))
    course_name_regex =  re.search("Bachelor", html_tags_removed)
    if course_name_regex:
        course_name = (html_tags_removed)
        igp_grades = (remove_html_tags(str(smu_igp_elems[i+5])))
        uas_for_course = convert_igp_to_uas(igp_grades)
        course.append('SMU')
        course.append(course_name)
        course.append(igp_grades)
        course.append(uas_for_course)
        smu_courses.append(course)



#NTU
#I downloaded the PDF and used a PDF scraper to extract the IGP
URL_NTU = 'https://www3.ntu.edu.sg/oad2/website_files/IGP/NTU_IGP.pdf'
filename = Path('NTU_IGP.pdf')
response = requests.get(URL_NTU)
filename.write_bytes(response.content)

pdf_path='NTU_IGP.pdf'
pdf = PdfFileReader(str(pdf_path))

#Cleaning data up
with pdfplumber.open('NTU_IGP.pdf') as pdf:
    second_page = pdf.pages[1]
    third_page = pdf.pages[2]
    second_page_cropped = second_page.crop((0,0.37*float(second_page.height),\
        second_page.width,second_page.height))
    ntu_courses = []
    second_page_table = second_page_cropped.extract_table(
        table_settings={
            'vertical_strategy':'text',
            'horizontal_strategy':'text',
            'keep_blank_chars':True
        }
    )
    third_page_table = third_page.extract_table(
        table_settings={
            'vertical_strategy':'text',
            'horizontal_strategy':'text',
            'keep_blank_chars':True
        }
    )
def ntu_table_cleanup(table: list):
    for i in table:
        if i[0] == '' or i[1] == '' or i[2] == '' :
            table.remove(i)
    return table
for i in ntu_table_cleanup(second_page_table):
    course = []
    course.append('NTU')
    course.append(i[0])
    course.append(i[1])
    uas_for_course = convert_igp_to_uas(i[1])
    course.append(uas_for_course)
    ntu_courses.append(course)

for i in (ntu_table_cleanup(third_page_table))[1:]: #Cannot remove 1st row despite filtering
    course = []
    course.append('NTU')
    course.append(i[0])
    course.append(i[1])
    uas_for_course = convert_igp_to_uas(i[1])
    course.append(uas_for_course)
    ntu_courses.append(course)

#Combine 3 school data together
all_course_list  = []

#Combining items in the different arrays together
def combine(array1,array2):
    for item in array1:
        array2.append(item)


combine(nus_courses,all_course_list)
combine(ntu_courses,all_course_list)
combine(smu_courses,all_course_list)

with open('output.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(all_course_list)
