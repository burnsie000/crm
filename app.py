# let's import the flask
from flask import Flask, render_template, request, redirect, url_for
import os # importing operating system module
from os import path
from flask import Flask
from os import path
from my_package.__init__ import create_app

app = Flask(__name__)

app = create_app()
# to stop caching static file

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

app.secret_key = '823r9h2983hrf23j89fj29r8329'

from my_package.auth import auth
from my_package.views import views 

@app.route('/') # this decorator create the home route
def home ():
    techs = ['HTML', 'CSS', 'Flask', 'Python']
    name = '30 Days Of Python Programming'
    return render_template('home.html', techs=techs, name = name, title = 'Home')

@app.route('/about')
def about():
    name = '30 Days Of Python Programming'
    return render_template('about.html', name = name, title = 'About Us')

@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/post', methods= ['GET','POST'])
def post():
    name = 'Text Analyzer'
    if request.method == 'GET':
         return render_template('post.html', name = name, title = name)
    if request.method =='POST':
        content = request.form['content']
        print(content)
        return redirect(url_for('result'))


if __name__ == '__main__':
    # for deployment
    # to make it work for both production and development
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='192.168.1.126', port=port)

