import json
from scripts.summary import get_summary
from flask import Flask, request, render_template, send_from_directory
app = Flask(__name__)

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/summary/')
def summary():
    data = get_summary("/data/result.json")
    return render_template('partials/summary.html', data=data)

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('resources/js', path)
    
@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('resources/css', path)

@app.route('/imgs/<path:path>')
def send_imgs(path):
    return send_from_directory('resources/imgs', path)

@app.errorhandler(404)
def page_not_found(e):
    return "404. Oh noes nothing here!"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9898, debug=False)