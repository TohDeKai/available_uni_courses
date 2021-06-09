from flask import Flask, render_template, request
import csv

app = Flask(__name__, template_folder='templates')

all_courses = []




@app.route("/calculate",methods=['GET','POST'])

def calculate():
    with open('output.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            all_courses.append(row)
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
    if rankpoints != 'uncalculated':
        for courses in all_courses:
            if float(rankpoints) >= float(courses[3]):
                avail_courses.append(courses)
            else:
                continue
    return render_template('calculate.html',rankpoints = rankpoints,avail_courses = avail_courses)

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/")
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
