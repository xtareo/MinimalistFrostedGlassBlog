# Copyright (c) <2026> <Xtareo>
# Licensed under the MIT License. See LICENSE file for details.

import os
import json
import io
import random
import string
from flask import (
    Flask, render_template, request, redirect, url_for, flash,
    jsonify, session, make_response
)
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# ---------- 配置 ----------
ARTICLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'articles')
IMAGES_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'images')
USERNAME = "admin"
PASSWORD_HASH = "" #请填写你的登入密码哈希

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}

app = Flask(__name__)
app.url_map.strict_slashes = False
app.secret_key = os.urandom(24).hex()   # 生产环境请改用固定强随机值
app.config['WTF_CSRF_ENABLED'] = True
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
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
    safe_name = secure_filename(filename)
    if not safe_name:
        return None
    _, ext = os.path.splitext(safe_name)
    if ext not in ('.md', '.json'):
        return None
    if ext == '.json' and safe_name != 'list.json':
        return None
    full_path = os.path.normpath(os.path.join(ARTICLES_DIR, safe_name))
    if not full_path.startswith(os.path.normpath(ARTICLES_DIR)):
        return None
    return full_path

def get_editable_files():
    try:
        files = [f for f in os.listdir(ARTICLES_DIR) if f.endswith('.md')]
        if os.path.exists(os.path.join(ARTICLES_DIR, 'list.json')):
            files.append('list.json')
        return sorted(files)
    except FileNotFoundError:
        return []

def safe_image_path(relative_path):
    clean = relative_path.strip('/')
    if '..' in clean:
        return None
    full = os.path.normpath(os.path.join(IMAGES_DIR, clean))
    if not full.startswith(os.path.normpath(IMAGES_DIR)):
        return None
    return full

def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

def generate_captcha_svg():
    chars = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
    code = ''.join(random.choices(chars, k=4))
    width, height = 120, 50
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
      <rect width="100%" height="100%" fill="#f9fafb" rx="8"/>
      <text x="50%" y="55%" dominant-baseline="middle" text-anchor="middle"
            font-family="monospace" font-size="28" font-weight="bold"
            fill="#1e293b" transform="rotate({random.randint(-4,4)}, {width/2}, {height/2})"
            letter-spacing="8">{code}</text>
      {''.join(f'<line x1="{random.randint(0,width)}" y1="{random.randint(0,height)}" x2="{random.randint(0,width)}" y2="{random.randint(0,height)}" stroke="#cbd5e1" stroke-width="1"/>' for _ in range(3))}
      {''.join(f'<circle cx="{random.randint(0,width)}" cy="{random.randint(0,height)}" r="{random.randint(1,2)}" fill="#94a3b8"/>' for _ in range(20))}
    </svg>'''
    return svg, code

# ---------- 验证码路由 ----------
@app.route('/manage/captcha')
def captcha():
    svg_data, answer = generate_captcha_svg()
    session['captcha_answer'] = answer
    response = make_response(svg_data)
    response.headers['Content-Type'] = 'image/svg+xml'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return response

# ---------- 登录 ----------
@app.route('/manage/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('manage_page'))
    error = None
    if request.method == 'POST':
        user_captcha = request.form.get('captcha', '').strip().upper()
        server_captcha = session.get('captcha_answer', '').upper()
        if not user_captcha or user_captcha != server_captcha:
            error = '验证码错误'
        else:
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            if username == USERNAME and check_password_hash(PASSWORD_HASH, password):
                user = User(username)
                login_user(user)
                flash('登录成功', 'success')
                return redirect(url_for('manage_page'))
            else:
                error = '用户名或密码错误'
        session.pop('captcha_answer', None)
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
    files = get_editable_files()
    return render_template('manage.html', files=files)

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

# ---------- 图片管理 API ----------
@app.route('/manage/api/images')
@login_required
def api_list_images():
    folder = request.args.get('path', '').strip('/')
    target_dir = safe_image_path(folder)
    if target_dir is None or not os.path.isdir(target_dir):
        return jsonify({'error': '无效目录'}), 400

    folders = []
    images = []
    try:
        for entry in sorted(os.listdir(target_dir)):
            if entry.startswith('.'):
                continue
            full_entry = os.path.join(target_dir, entry)
            if os.path.isdir(full_entry):
                folders.append({
                    'name': entry,
                    'path': os.path.join(folder, entry).replace('\\', '/')
                })
            else:
                if allowed_image(entry):
                    images.append({
                        'name': entry,
                        'path': os.path.join(folder, entry).replace('\\', '/')
                    })
    except OSError:
        return jsonify({'error': '无法读取目录'}), 500

    return jsonify({'folders': folders, 'images': images, 'current': folder})

@app.route('/manage/api/images/upload', methods=['POST'])
@login_required
def api_upload_image():
    folder = request.form.get('folder', '').strip('/')
    target_dir = safe_image_path(folder)
    if target_dir is None or not os.path.isdir(target_dir):
        return jsonify({'error': '无效目录'}), 400

    if 'file' not in request.files:
        return jsonify({'error': '未选择文件'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400
    if not allowed_image(file.filename):
        return jsonify({'error': '不支持的文件类型'}), 400

    filename = secure_filename(file.filename)
    # 如果文件已存在，自动重命名（加时间戳）
    base, ext = os.path.splitext(filename)
    dest_path = os.path.join(target_dir, filename)
    counter = 0
    while os.path.exists(dest_path):
        counter += 1
        filename = f"{base}_{counter}{ext}"
        dest_path = os.path.join(target_dir, filename)
    try:
        file.save(dest_path)
        relative = os.path.join(folder, filename).replace('\\', '/')
        return jsonify({'success': True, 'filename': filename, 'path': relative})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/manage/api/images/mkdir', methods=['POST'])
@login_required
def api_create_image_folder():
    data = request.get_json()
    if not data:
        return jsonify({'error': '请求数据无效'}), 400
    parent = data.get('folder', '').strip('/')
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': '文件夹名称不能为空'}), 400
    safe_name = secure_filename(name)
    if safe_name != name:  # 如果被修改，说明包含非法字符
        return jsonify({'error': '文件夹名称包含非法字符'}), 400

    parent_dir = safe_image_path(parent)
    if parent_dir is None or not os.path.isdir(parent_dir):
        return jsonify({'error': '无效父目录'}), 400

    new_dir = os.path.join(parent_dir, safe_name)
    if os.path.exists(new_dir):
        return jsonify({'error': '文件夹已存在'}), 409
    try:
        os.makedirs(new_dir, exist_ok=False)
        return jsonify({'success': True, 'name': safe_name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/manage/api/images/delete', methods=['POST'])
@login_required
def api_delete_image():
    data = request.get_json()
    if not data or 'paths' not in data:
        return jsonify({'error': '缺少路径参数'}), 400
    paths = data['paths']  # 期望为数组
    if not isinstance(paths, list):
        paths = [paths]

    errors = []
    for p in paths:
        clean = p.strip('/')
        target = safe_image_path(clean)
        if target is None:
            errors.append(f'{p}: 非法路径')
            continue
        if not os.path.exists(target):
            errors.append(f'{p}: 不存在')
            continue
        try:
            if os.path.isfile(target):
                os.remove(target)
            elif os.path.isdir(target):
                # 只允许删除空文件夹
                if len(os.listdir(target)) == 0:
                    os.rmdir(target)
                else:
                    errors.append(f'{p}: 文件夹不为空，无法删除')
            else:
                errors.append(f'{p}: 未知类型')
        except Exception as e:
            errors.append(f'{p}: {str(e)}')

    if errors:
        return jsonify({'error': '部分操作失败', 'details': errors}), 400
    return jsonify({'success': True})

if __name__ == '__main__':
    os.makedirs(ARTICLES_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    app.run(host='127.0.0.1', port=5000, debug=False)