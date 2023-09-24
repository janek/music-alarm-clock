from flask import Flask, render_template
import datetime

# set up initial alarm time
alarm_time = datetime.time(hour=8, minute=0)
alarm_active = False

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', alarm_time=alarm_time, alarm_active=alarm_active)


if __name__ == '__main__':
    app.run(debug=True, port=3142, host='0.0.0.0')