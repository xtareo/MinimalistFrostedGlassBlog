# Copyright (c) <2026> <Xtareo>
# Licensed under the MIT License. See LICENSE file for details.

import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# ---------- 配置 ----------
ARTICLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'articles')
USERNAME = "admin"
PASSWORD_HASH = ""   # 务必修改为密码哈希 在python控制台里运行generate_password_hash("填你的密码")来获取哈希

app = Flask(__name__)
app.url_map.strict_slashes = False          # 允许 /manage/ 和 /manage 均可访问
app.secret_key = os.urandom(24).hex()
app.config['WTF_CSRF_ENABLED'] = True
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '请先登录'

# ---------- 用户类 ----------
class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    if username == USERNAME:
        return User(username)
    return None

# ---------- 辅助函数 ----------
def safe_article_path(filename):
    """允许 .md 和 list.json，严格防路径遍历"""
    safe_name = secure_filename(filename)
    if not safe_name:
        return None
    # 检查扩展名
    _, ext = os.path.splitext(safe_name)
    if ext not in ('.md', '.json'):
        return None
    # 只允许特定的 .json 文件
    if ext == '.json' and safe_name != 'list.json':
        return None
    full_path = os.path.normpath(os.path.join(ARTICLES_DIR, safe_name))
    if not full_path.startswith(os.path.normpath(ARTICLES_DIR)):
        return None
    return full_path

def get_editable_files():
    """返回可编辑的文件列表：所有 .md + list.json（如果存在）"""
    try:
        files = [f for f in os.listdir(ARTICLES_DIR) if f.endswith('.md')]
        if os.path.exists(os.path.join(ARTICLES_DIR, 'list.json')):
            files.append('list.json')
        return sorted(files)
    except FileNotFoundError:
        return []

# ---------- 路由 ----------
@app.route('/manage/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('manage_page'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if username == USERNAME and check_password_hash(PASSWORD_HASH, password):
            user = User(username)
            login_user(user)
            flash('登录成功', 'success')
            return redirect(url_for('manage_page'))
        else:
            error = 'Username or password incorrect'
    return render_template('login.html', error=error)

@app.route('/manage/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('login'))

@app.route('/manage')
@login_required
def manage_page():
    files = get_editable_files()    # 现在使用新函数
    return render_template('manage.html', files=files)

# ---------- API ----------
@app.route('/manage/api/files')
@login_required
def api_files():
    return jsonify(get_editable_files())

@app.route('/manage/api/file/<filename>', methods=['GET'])
@login_required
def api_read_file(filename):
    path = safe_article_path(filename)
    if not path or not os.path.exists(path):
        return jsonify({'error': '文件不存在'}), 404
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    return jsonify({'content': content})

@app.route('/manage/api/file/<filename>', methods=['POST'])
@login_required
def api_write_file(filename):
    path = safe_article_path(filename)
    if not path:
        return jsonify({'error': '非法文件名'}), 400
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': '缺少内容'}), 400
    content = data['content']
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/manage/api/file/<filename>/delete', methods=['POST'])
@login_required
def api_delete_file(filename):
    if filename == 'list.json':
        return jsonify({'error': '不能删除 list.json'}), 403
    path = safe_article_path(filename)
    if not path or not os.path.exists(path):
        return jsonify({'error': '文件不存在'}), 404
    try:
        os.remove(path)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/manage/api/file/create', methods=['POST'])
@login_required
def api_create_file():
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({'error': '请提供文件名'}), 400
    raw_name = data['filename'].strip()
    if not raw_name:
        return jsonify({'error': '文件名不能为空'}), 400
    # 只允许创建 .md 文件
    if not raw_name.endswith('.md'):
        raw_name += '.md'
    safe_name = secure_filename(raw_name)
    if not safe_name or safe_name == '.md':
        return jsonify({'error': '无效的文件名'}), 400
    path = os.path.normpath(os.path.join(ARTICLES_DIR, safe_name))
    if not path.startswith(os.path.normpath(ARTICLES_DIR)):
        return jsonify({'error': '非法文件名'}), 400
    if os.path.exists(path):
        return jsonify({'error': '文件已存在'}), 409
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write('')
        return jsonify({'success': True, 'filename': safe_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    os.makedirs(ARTICLES_DIR, exist_ok=True)
    app.run(host='127.0.0.1', port=5000, debug=False)