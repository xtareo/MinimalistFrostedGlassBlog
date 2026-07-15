# 简单的毛玻璃博客（含管理后台）

一个兼具 **极简毛玻璃风格** 与 **轻量在线编辑** 的静态博客系统。  
前端采用纯静态 HTML/CSS/JS，支持 Markdown 文章渲染、列表/网格切换、自适应移动端；后端基于 Flask 提供安全的文章管理界面，与 Nginx 静态站点无缝共存，通过 `/manage` 路径即可在线增删改文章。

---

## ✨ 特性一览

### 前端（静态博客）
- **毛玻璃设计** – 大量 `backdrop-filter` 半透明模糊，现代美观  
- **自定义背景** – 支持任意图片或默认渐变背景  
- **Markdown 写作** – 将 `.md` 文件放入 `articles/` 目录，自动解析为文章  
- **列表 / 网格双视图** – 右侧文章区可在列表与卡片网格间自由切换，并记住用户偏好  
- **左侧个人信息** – 头像、昵称、简介、社交图标链接；底部显示运行时长与版权信息  
- **移动端适配** – 手机自动隐藏侧边栏，顶部显示头像与名称，仅保留列表模式  
- **独立滚动区域** – 文章列表与内容区拥有独立半透明滚动条，长内容不影响整体布局  

### 后台（管理编辑器）
- **安全登录** – 单用户认证，密码使用 Werkzeug 哈希存储，登入验证码，CSRF 防护，会话管理  
- **文件管理** – 左侧列出所有 `.md` 文件和 `list.json`，支持新建、编辑、保存、删除（`list.json` 禁止删除）
- **图片管理** - 通过这个轻松管理博客图片，来方便文章插入图片，支持上传、删除、新建图片文件夹、复制图片所在根目录路径
- **实时预览** – 编辑 Markdown 时使用 `marked` + `highlight.js` 渲染，支持 GFM 表格和代码高亮；编辑 `list.json` 时预览格式化 JSON  
- **路径安全** – 严格的路径规范化与 `secure_filename` 过滤，防止目录遍历攻击，仅允许操作 `articles` 目录  
- **无缝集成** – 与 Nginx 静态博客共用同一域名，仅需增加一个 `location /manage/` 反向代理

---

## 📁 项目结构

```
your-blog/
├── index.html                    # 静态博客主页
├── style.css                     # 毛玻璃样式 + 响应式
├── js/
│   ├── config.js                 # 个人配置（头像、昵称、社交链接等）
│   └── main.js                   # 文章加载、视图切换逻辑
├── articles/                     # 文章目录（前后端共享）
│   ├── list.json                 # 文章索引（标题、日期、路径等）
│   ├── hello-world.md
│   └── ...
├── images/
│   ├── avatar.jpg                #头像 背景 网站图标等图片
│   └── bg.jpg
├── manage_app/                   # Flask 管理应用（独立子目录）
│   ├── app.py                    # 主程序
│   ├── templates/
│   │   ├── login.html            #登入页面
│   │   └── manage.html           #管理页面
│   ├── requirements.txt
│   └── venv/                     # Python 虚拟环境（可选）
```

---

## 🚀 快速开始（开发环境）

### 前置条件
- 现代浏览器（支持 `backdrop-filter`）
- 本地静态服务器（用于预览前端） – 可选 Python / Node / VS Code Live Server
- Python 3.8+（用于管理后台）

---

### 第一步：运行静态博客（无需后台）

1. **克隆或下载项目**，确保目录结构如上。

2. **修改个人信息** – 编辑 `js/config.js`：
   ```javascript
   const CONFIG = {
       avatar: 'images/avatar.jpg',
       name: '你的昵称',
       bio: '个人简介',
       backgroundImage: '', // 留空使用渐变，或填写图片路径
       links: [
            //name填跳转链接名称，url填跳转链接网址，icon：填跳转链接网址的按钮的图标
            //按钮的图标，请打开main.js查看图标映射处，有可以使用的图标名称
           { name: 'GitHub', url: 'https://github.com/yourname', icon: 'github' }, 
           { name: '邮箱', url: 'mailto:you@example.com', icon: 'email' },
       ],
       startDate: '2024-01-01',
       copyright: '© {startYear}-{year} 你的昵称',
   };
   ```

3. **添加文章** – 将 `.md` 文件放入 `articles/`，并在 `list.json` 中注册（格式见下方说明）。

4. **启动本地预览**（必须通过服务器，否则因 CORS 无法加载本地文件）：
   ```bash
   # Python 3
   python -m http.server 8000
   # 或使用 VS Code Live Server 插件
   ```
   访问 `http://localhost:8000` 即可看到博客。

---

### 第二步：启用管理后台（可选）

若你需要在线编辑文章，请继续以下步骤：

1. **进入管理应用目录**：
   ```bash
   cd manage_app
   ```

2. **创建虚拟环境并安装依赖**：
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **设置管理员密码** – 生成密码哈希：
   ```bash
   python3 -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('你的强密码'))"
   ```
   将输出的哈希字符串替换 `app.py` 中的 `PASSWORD_HASH` 变量值。

4. **测试运行**（开发模式）：
   ```bash
   python app.py
   ```
   访问 `http://127.0.0.1:5000/manage/`，用户名固定为 `admin`，密码即你设定的强密码。

5. **确保 `articles` 目录和`images`目录可读写**（若与前端目录一致，权限需放开）。

---

## 🖊️ 文章管理和图片管理后台使用指南

登录后，界面分为左侧文件列表和右侧编辑区域：

- **编辑已有文章** – 点击左侧任一 `.md` 文件，右侧加载内容，可编辑并实时预览（Markdown 渲染效果）。  
- **新建文章** – 在底部输入框中填写文件名（不带后缀），点击“新建”，文件即创建并出现在列表中。  
- **保存更改** – 编辑完成后点击“💾 保存文件”。  
- **删除文章** – 点击文件名旁的 🗑️ 图标，确认后删除（物理删除 `.md` 文件）。  
- **编辑 `list.json`** – 点击左侧 `list.json`，可在右侧直接编辑 JSON 内容，保存时自动校验格式合法性。  
- **退出登录** – 点击侧边栏底部的“退出登录”。
- **切换按钮(图片管理/文章列表)** - 点击按钮可以切换图片管理与文章列表界面。
- **图片的上传** - 点击即可选择图片文件上传，默认支持png, jpg, jpeg, gif, webp, svg这几种图片类型。
- **图片的新建文件夹** - 点击后输入文件夹名，文件夹命名默认只支持英文且不能有特殊符号与空格，通过这个可以对图片分类。
- **图片的搜索框** - 点击输入图片名称即可对当前所在文件夹进行搜索展示。
- **图片的删除与路径获取** - 点击图片左上方的🗑️图标即可删除该图片，点击右下方`复制路径`即可获取并复制该图片所在路径，方便文章插入图片时不用手输入路径。
> **注意**：所有操作均同步到磁盘，修改后静态博客页面会自动刷新（需手动刷新浏览器查看新内容）。

---

## 🔧 生产环境部署（Nginx + Systemd）

### 1. 部署静态博客
将整个项目（除 `manage_app` 外）上传到服务器，例如 `/var/www/blog/`，配置 Nginx 根目录指向该文件夹：

```nginx
server {
    listen 80;
    server_name 填你的域名或服务器IP地址;
    root /var/www/blog;
    index index.html;

    # 后续添加 /manage/ 反向代理...
}
```

### 2. 部署管理后台（Flask）

- **将 `manage_app` 目录放在服务器合适位置**（例如 `/var/www/blog/manage_app`）。
- 设置虚拟环境、安装依赖、配置 `PASSWORD_HASH`（同上）。
- **设置文件权限**，确保 Flask 进程（通常 `www-data` 用户）可读写 `articles` 目录和`images`目录：
  ```bash
  sudo chown -R www-data:www-data /var/www/blog/articles
  sudo chmod -R 755 /var/www/blog/articles
  sudo chown -R www-data:www-data /var/www/blog/images
  ```

- **创建 Systemd 服务**（`/etc/systemd/system/blog-manage.service`）：
  ```ini
  [Unit]
  Description=Blog Manage Flask App
  After=network.target

  [Service]
  User=www-data
  Group=www-data
  WorkingDirectory=/var/www/blog/manage_app
  ExecStart=/var/www/blog/manage_app/venv/bin/python /var/www/blog/manage_app/app.py
  Restart=always
  Environment="PATH=/var/www/blog/manage_app/venv/bin"

  [Install]
  WantedBy=multi-user.target
  ```
  启动并设置开机自启：
  ```bash
  sudo systemctl daemon-reload
  sudo systemctl enable --now blog-manage.service
  ```

  > 若需更高性能，可将 `ExecStart` 替换为 Gunicorn（需安装）：
  > `ExecStart=/path/to/gunicorn -w 2 -b 127.0.0.1:5000 app:app`

### 3. Nginx 配置反向代理

在站点 `server` 块中添加 `/manage/` 路径，**必须放在 `location /` 之前**：

```nginx
location /manage/ {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

location / {
    try_files $uri $uri/ =404;
}
```

确保 Nginx 允许访问 /images/ 路径（在静态博客的 server 块中添加）:
```nginx
location /images/ {
    alias /var/www/blog/images/;
    expires 30d;
}
```

重载 Nginx：
```bash
sudo nginx -t && sudo systemctl reload nginx
```

现在访问 `http://你的域名或服务器IP地址/manage/` 即可使用管理后台。

---

## 🎨 自定义样式与配置

### 前端视觉调整
所有毛玻璃效果、主色调、圆角等均在 `css/style.css` 的 `:root` 中定义，可自由修改：
```css
:root {
    --glass-bg: rgba(255, 255, 255, 0.18);
    --glass-blur: blur(18px);
    --accent: #5b7fff;
    --radius: 16px;
    /* ... */
}
```

### 文章索引格式（`list.json`）
每篇文章需注册为如下对象（按 `date` 降序排列）：
```json
{
    "id": "my-first-post",
    "title": "我的第一篇文章",
    "date": "2024-09-01",
    "summary": "简短摘要",
    "file": "articles/my-first-post.md",
    "tags": ["生活", "技术"],
    "cover": ""
}
```
- `cover` 为封面图路径，留空显示占位图标。

---

## 🛠 技术栈

| 部分     | 技术 |
| -------- | ---- |
| 前端     | HTML5, CSS3 (Flexbox/Grid, `backdrop-filter`), 原生 JavaScript, [marked.js](https://marked.js.org/) |
| 后端管理 | Python 3, Flask, Flask-Login, Flask-WTF, Werkzeug |
| 部署     | Nginx, Systemd (可选 Gunicorn) |
| 预览渲染 | Highlight.js (代码高亮) |

---

## 🔒 安全说明
- 密码使用 `pbkdf2:sha256` 哈希存储，无明文。
- 所有管理接口强制登录，CSRF 令牌验证。
- 文件名经过 `secure_filename` 过滤，路径拼接严格限制在 `articles` 目录内。
- 仅允许操作 `.md` 和 `list.json`，避免任意文件读写。
- Flask 监听 `127.0.0.1`，通过 Nginx 反向代理对外暴露，减少攻击面。

---

## ❓ 常见问题

**Q：静态博客无法加载文章？**  
A：请确保通过 HTTP 服务器访问（非 `file://` 协议），并检查 `articles/list.json` 格式是否正确，文件路径是否有效。

**Q：管理后台登录后 404？**  
A：确认 Flask 服务运行中 (`systemctl status blog-manage`)，且 Nginx 的 `location /manage/` 配置正确，`proxy_pass` 不带尾部斜杠（或按示例配置）。

**Q：修改密码后如何生效？**  
A：更新 `app.py` 中的 `PASSWORD_HASH`，重启服务：`sudo systemctl restart blog-manage`。

**Q：文章修改后静态页面未更新？**  
A：前端完全静态，需手动刷新浏览器；也可设置 Nginx 缓存策略，但建议开发时禁用缓存。

**Q：1MB以上大小的图片上传失败？**
A：由于Flask 默认限制为 16MB（app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024），
同时，Nginx 也有默认 1MB 的上传限制，即使 Flask 放宽了限制，Nginx 也会拦截大文件。
增加 Flask 限制（例如改为 50MB）：
```python
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
```
修改 Nginx 配置，在 server 块或 location /manage/ 中添加：
```python
client_max_body_size 50m;
```
然后重载 Nginx和重启 Flask

---

## 📄 许可

MIT License © Xtareo

---

**Enjoy!** 如果你喜欢这个项目，欢迎 Star ⭐ 或提交 Issue/PR 改进。
