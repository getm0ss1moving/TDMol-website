# frame.py
from flask import Flask, render_template
# create an app
app = Flask(__name__)

# define a route
# @app.route('/') run the function home() when the root URL is accessed
@app.route('/')
def home():
    
    # create an HTML page in the "templates" folder
    return render_template('index.html')

# run web app
if __name__ == '__main__':
    app.run(debug=True)