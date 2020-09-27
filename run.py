import sys
import os
import threading
import time
import logging
from flask import Flask, request, redirect, url_for, render_template, flash
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from router.models import User, query_user
from flask_script import Manager, Server
from router.module import module_bp

# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)

app.config['JSON_SORT_KEYS'] = False
app.secret_key = '1234567'

# manager = Manager(app)
# manager.add_command('runserver', Server(host='0.0.0.0', port=5000, use_debugger=False))
# # manager.option('-r', '-d')

app.register_blueprint(module_bp)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = ''
login_manager.init_app(app)

#################################################
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('userid')
        user = query_user(user_id)
        if user is not None and request.form['password'] == user['password']:

            curr_user = User()
            curr_user.id = user_id

            # 通过Flask-Login的login_user方法登录用户
            login_user(curr_user)

            return redirect(url_for('module.dashboard'))

        flash('无效的用户名或密码！')
    # GET 请求
    return render_template('login.html', title="登录系统")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    # return 'Logged out successfully!'
    return render_template('login.html' , title="登录系统")


@login_manager.user_loader
def load_user(user_id):
    if query_user(user_id) is not None:
        curr_user = User()
        curr_user.id = user_id
        return curr_user
        
# def start_browser(tname, delay):
#     # print('start: ' + tname)
#     time.sleep(delay)
#     # os.system('start_gui.bat')
#     os.system("..\\GoogleChromePortable\\App\\Chrome-bin\\chrome.exe --disable-extensions --app=http://127.0.0.1:5000")

def start_server(tname, delay):
    # print('start: ' + tname)
    time.sleep(delay)
    # sys.argv.append('runserver')
    # manager.run()
    # app.run(host='127.0.0.1', port=5000, debug=False)
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    try:
        # t1 = threading.Thread(target=start_browser, args=('t1_browser', 3,))
        t2 = threading.Thread(target=start_server, args=('t2_server', 1,))
        # t1.start()
        t2.start()
    except:
        print("Error: unable to start thread")
