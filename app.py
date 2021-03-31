from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import re
from PyPDF2 import PdfFileReader
from pathlib import Path
import pdfplumber

app = Flask(__name__, template_folder='templates')
count = 0
grade_to_uas = {"A": 20, "B": 17.5, "C": 15, "D": 12.5, "E": 10, "S": 5, "U": 0}

def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def convert_igp_to_uas(igp):
    uas = 0
    for i in igp[:3]:
        uas += grade_to_uas[i]
    uas += grade_to_uas[igp[4]]/2
    uas += 15
    return uas

#NUS
URL_NUS = 'https://www.nus.edu.sg/oam/undergraduate-programmes/indicative-grade-profile-(igp)'
nus_page = requests.get(URL_NUS)
nus_soup = BeautifulSoup(nus_page.content, 'html.parser')
nus_results = nus_soup.find(id='ContentPlaceHolder_contentPlaceholder_TC88F994D007_Col00')
nus_igp_elems = nus_results.find_all("tr", class_=False, id=False)

#SMU
#Cannot scrape:"Request unsuccessful. Incapsula incident"
#So I inspected page source, copied and pasted it into a text file instead
smu = open("SMU_IGP.txt", encoding="utf8")
smufile = smu.read()
smu_soup = BeautifulSoup(smufile, 'html.parser')
smu_results = smu_soup.find(id="content IndicativeGradeProfiles(IGP)")
smu_igp_elems = smu_results.find_all("td", class_=False, id=False)

#NTU
#I downloaded the PDF and used a PDF scraper to extract the IGP
URL_NTU = 'https://www3.ntu.edu.sg/oad2/website_files/IGP/NTU_IGP.pdf'
filename = Path('NTU_IGP.pdf')
response = requests.get(URL_NTU)
filename.write_bytes(response.content)

pdf_path='NTU_IGP.pdf'
pdf = PdfFileReader(str(pdf_path))

@app.route("/",methods=['GET','POST'])
def home():
    avail_courses = []
    rankpoints = 'uncalculated'
    if request.method == 'POST':
        h21 = request.form.get('h21')
        h22 = request.form.get('h22')
        h23 = request.form.get('h23')
        h1 = request.form.get('h1')
        gp = request.form.get('gp')
        pw = request.form.get('pw')
        rankpoints = float(h21) + float(h22) + float(h23) + float(h1) + float(gp) + float(pw)
    
    #Comparing NUS courses
    for i in nus_igp_elems[3:49]:
        course = []
        course_elem = i.find('td',  class_=False, id=False)
        igp_grades = i.find('div', class_=False, id=False)
        if course_elem == None or igp_grades == None:
            continue
        else:
            if bool(re.match(r'\w{3}/\w{1}', igp_grades.text)) == False:
                continue      
            else:
                uas_for_course = convert_igp_to_uas(igp_grades.text)
                if rankpoints != 'uncalculated':
                    if float(uas_for_course) <= float(rankpoints):
                        #avail_courses.append('NUS',",",course_elem.text,",",uas_for_course) 
                        course.append('NUS')
                        course.append(course_elem.text)
                        course.append(igp_grades.text)
                        course.append(uas_for_course)
                        avail_courses.append(course)
    
    #Comparing SMU courses 
    for i in range(len(smu_igp_elems[4:25])):
        course = []
        html_tags_removed = (remove_html_tags(str(smu_igp_elems[i+4])))
        course_name_regex =  re.search("Bachelor", html_tags_removed)
        if course_name_regex:
            course_name = (html_tags_removed)
            igp_grades = (remove_html_tags(str(smu_igp_elems[i+5])))
            uas_for_course = convert_igp_to_uas(igp_grades)
            if rankpoints != 'uncalculated':
                if float(uas_for_course) <= float(rankpoints):
                    course.append('SMU')
                    course.append(course_name)
                    course.append(igp_grades)
                    course.append(uas_for_course)
                    avail_courses.append(course)
    
    #Comparing NTU courses 
    with pdfplumber.open('NTU_IGP.pdf') as pdf:
        second_page = pdf.pages[1]
        third_page = pdf.pages[2]
        second_page_cropped = second_page.crop((0,0.37*float(second_page.height),\
            second_page.width,second_page.height))
        ntu_course_list = []
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
        ntu_course_list.append(i)
    for i in (ntu_table_cleanup(third_page_table))[1:]: #Cannot remove 1st row despite filtering
        ntu_course_list.append(i)
                
    for i in ntu_course_list:
        uas_for_course = 0
        uas_for_course = convert_igp_to_uas(i[1])
        course = []
        if rankpoints != 'uncalculated':
            if float(uas_for_course) <= float(rankpoints):
                course.append('NTU')
                course.append(i[0])
                course.append(i[1])        
                course.append(uas_for_course)
                avail_courses.append(course)

    return render_template('home.html',rankpoints = rankpoints,avail_courses = avail_courses)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/calculate")
def calculate():
    return render_template('calculate.html')

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
