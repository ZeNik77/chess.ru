from app import app, render_template


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')
