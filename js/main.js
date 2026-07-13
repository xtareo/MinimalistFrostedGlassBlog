// Copyright (c) <2026> <Xtareo>
// Licensed under the MIT License. See LICENSE file for details
// ==================== 主逻辑 ====================
(function () {
    // ============ DOM 引用 ============
    const bgLayer = document.getElementById('bgLayer');
    const sidebar = document.getElementById('sidebar');
    const sidebarAvatar = document.getElementById('sidebarAvatar');
    const sidebarName = document.getElementById('sidebarName');
    const sidebarBio = document.getElementById('sidebarBio');
    const sidebarLinks = document.getElementById('sidebarLinks');
    const sidebarRuntime = document.getElementById('sidebarRuntime');
    const sidebarCopyright = document.getElementById('sidebarCopyright');

    const mobileHeader = document.getElementById('mobileHeader');
    const mobileAvatar = document.getElementById('mobileAvatar');
    const mobileName = document.getElementById('mobileName');
    const mobileFooter = document.getElementById('mobileFooter');
    const mobileRuntime = document.getElementById('mobileRuntime');
    const mobileCopyright = document.getElementById('mobileCopyright');

    const toolbar = document.getElementById('toolbar');
    const btnBack = document.getElementById('btnBack');
    const toolbarTitle = document.getElementById('toolbarTitle');
    const layoutToggle = document.getElementById('layoutToggle');
    const layoutBtns = layoutToggle.querySelectorAll('.layout-btn');

    const contentArea = document.getElementById('contentArea');
    const articleList = document.getElementById('articleList');
    const articleDetail = document.getElementById('articleDetail');
    const emptyState = document.getElementById('emptyState');
    const loadingState = document.getElementById('loadingState');

    // ============ 状态 ============
    let articles = [];
    let currentView = 'list'; // 'list' | 'article'
    let currentArticleId = null;
    let layoutMode = CONFIG.defaultLayout || 'list';

    // 从 localStorage 恢复布局偏好
    const savedLayout = localStorage.getItem('blog_layout_mode');
    if (savedLayout === 'grid' || savedLayout === 'list') {
        layoutMode = savedLayout;
    }

    // ============ 图标映射 ============
    const iconSVGs = {
        github: '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/></svg>',
        twitter: '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>',
        email: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><polyline points="2 6 12 13 22 6"/></svg>',
        rss: '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><circle cx="6.18" cy="17.82" r="2.18"/><path d="M4 4.44v2.83c7.03 0 12.73 5.7 12.73 12.73h2.83c0-8.59-6.97-15.56-15.56-15.56z"/><path d="M4 10.1v2.83c3.9 0 7.07 3.17 7.07 7.07h2.83c0-5.47-4.43-9.9-9.9-9.9z"/></svg>',
        website: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><ellipse cx="12" cy="12" rx="4" ry="10"/><line x1="2" y1="12" x2="22" y2="12"/></svg>',
        link: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>',
        bilibili:'<svg fill="currentColor" fill-rule="evenodd" height="1em" style="flex:none;line-height:1" viewBox="0 0 24 24" width="1em" xmlns="http://www.w3.org/2000/svg"><title>bilibili</title><path clip-rule="evenodd" d="M4.977 3.561a1.31 1.31 0 111.818-1.884l2.828 2.728c.08.078.149.163.205.254h4.277a1.32 1.32 0 01.205-.254l2.828-2.728a1.31 1.31 0 011.818 1.884L17.82 4.66h.848A5.333 5.333 0 0124 9.992v7.34a5.333 5.333 0 01-5.333 5.334H5.333A5.333 5.333 0 010 17.333V9.992a5.333 5.333 0 015.333-5.333h.781L4.977 3.56zm.356 3.67a2.667 2.667 0 00-2.666 2.667v7.529a2.667 2.667 0 002.666 2.666h13.334a2.667 2.667 0 002.666-2.666v-7.53a2.667 2.667 0 00-2.666-2.666H5.333zm1.334 5.192a1.333 1.333 0 112.666 0v1.192a1.333 1.333 0 11-2.666 0v-1.192zM16 11.09c-.736 0-1.333.597-1.333 1.333v1.192a1.333 1.333 0 102.666 0v-1.192c0-.736-.597-1.333-1.333-1.333z"></path></svg>'
    };

    function getIconSVG(iconType) {
        return iconSVGs[iconType] || iconSVGs['link'];
    }

    // ============ 初始化 UI ============
    function initUI() {
        // 背景图
        if (CONFIG.backgroundImage) {
            bgLayer.style.backgroundImage = `url(${CONFIG.backgroundImage})`;
        }

        // 头像
        sidebarAvatar.src = CONFIG.avatar;
        mobileAvatar.src = CONFIG.avatar;

        // 名称
        sidebarName.textContent = CONFIG.name;
        mobileName.textContent = CONFIG.name;

        // 个人介绍
        sidebarBio.textContent = CONFIG.bio;

        // 社交链接
        sidebarLinks.innerHTML = '';
        CONFIG.links.forEach((link) => {
            const a = document.createElement('a');
            a.href = link.url;
            a.target = '_blank';
            a.rel = 'noopener noreferrer';
            a.title = link.name;
            a.innerHTML = getIconSVG(link.icon);
            sidebarLinks.appendChild(a);
        });

        // 运行时间 & 版权
        updateFooterInfo();
        // 每分钟更新一次运行时间
        setInterval(updateFooterInfo, 60000);

        // 布局按钮状态
        updateLayoutButtons();

        // 布局切换事件
        layoutBtns.forEach((btn) => {
            btn.addEventListener('click', function () {
                const newLayout = this.dataset.layout;
                if (newLayout && newLayout !== layoutMode) {
                    layoutMode = newLayout;
                    localStorage.setItem('blog_layout_mode', layoutMode);
                    updateLayoutButtons();
                    renderArticleList();
                }
            });
        });

        // 返回按钮
        btnBack.addEventListener('click', goBackToList);
    }

    function updateFooterInfo() {
        const now = new Date();
        const start = new Date(CONFIG.startDate);
        const runtimeStr = calcRuntime(start, now);

        const startYear = start.getFullYear();
        const currentYear = now.getFullYear();
        let copyright = CONFIG.copyright
            .replace(/\{startYear\}/g, startYear)
            .replace(/\{year\}/g, currentYear);
        // 如果起始年份等于当前年份，简化显示
        if (startYear === currentYear) {
            copyright = copyright.replace(startYear + '-', '');
        }

        sidebarRuntime.textContent = runtimeStr;
        sidebarCopyright.textContent = copyright;
        mobileRuntime.textContent = runtimeStr;
        mobileCopyright.textContent = copyright;
    }

    function calcRuntime(start, now) {
        let years = now.getFullYear() - start.getFullYear();
        let months = now.getMonth() - start.getMonth();
        let days = now.getDate() - start.getDate();

        if (days < 0) {
            months--;
            const prevMonth = new Date(now.getFullYear(), now.getMonth(), 0);
            days += prevMonth.getDate();
        }
        if (months < 0) {
            years--;
            months += 12;
        }

        const parts = [];
        if (years > 0) parts.push(`${years} 年`);
        if (months > 0) parts.push(`${months} 个月`);
        parts.push(`${Math.max(0, days)} 天`);

        return `本站已运行 ${parts.join(' ')}`;
    }

    function updateLayoutButtons() {
        layoutBtns.forEach((btn) => {
            if (btn.dataset.layout === layoutMode) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    }

    // ============ 加载文章索引 ============
    async function loadArticles() {
        try {
            const resp = await fetch(CONFIG.articlesIndex);
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            const data = await resp.json();
            articles = Array.isArray(data) ? data : [];
            // 按日期降序排列
            articles.sort((a, b) => new Date(b.date) - new Date(a.date));
        } catch (err) {
            console.error('加载文章列表失败:', err);
            articles = [];
        }
    }

    // ============ 渲染文章列表 ============
    function renderArticleList() {
        articleList.innerHTML = '';
        articleList.className = 'article-list';

        if (articles.length === 0) {
            articleList.style.display = 'none';
            emptyState.style.display = 'flex';
            loadingState.style.display = 'none';
            return;
        }

        emptyState.style.display = 'none';
        loadingState.style.display = 'none';
        articleList.style.display = '';

        // 应用布局模式
        articleList.classList.add(layoutMode === 'grid' ? 'grid-mode' : 'list-mode');

        articles.forEach((article) => {
            const card = document.createElement('div');
            card.className = 'article-card';
            card.addEventListener('click', () => openArticle(article));

            // 封面
            let coverHTML = '';
            if (article.cover) {
                coverHTML = `<img class="card-cover" src="${escapeHTML(article.cover)}" alt="" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='flex';" />`;
                coverHTML += `<div class="card-cover-placeholder" style="display:none;"><svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg></div>`;
            } else {
                coverHTML = `<div class="card-cover-placeholder"><svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg></div>`;
            }

            // 标签
            let tagsHTML = '';
            if (article.tags && article.tags.length > 0) {
                tagsHTML = article.tags
                    .map((t) => `<span class="tag">${escapeHTML(t)}</span>`)
                    .join('');
            }

            // 格式化日期
            const dateStr = formatDate(article.date);

            card.innerHTML = `
                        ${coverHTML}
                        <div class="card-info">
                            <div class="card-title">${escapeHTML(article.title)}</div>
                            <div class="card-meta">
                                <span>${dateStr}</span>
                            </div>
                            ${article.summary ? `<div class="card-summary">${escapeHTML(article.summary)}</div>` : ''}
                            ${tagsHTML ? `<div class="card-tags">${tagsHTML}</div>` : ''}
                        </div>
                    `;

            articleList.appendChild(card);
        });
    }

    function formatDate(dateStr) {
        if (!dateStr) return '';
        try {
            const d = new Date(dateStr);
            const y = d.getFullYear();
            const m = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');
            return `${y}-${m}-${day}`;
        } catch {
            return dateStr;
        }
    }

    // ============ 打开文章 ============
    async function openArticle(article) {
        currentView = 'article';
        currentArticleId = article.id;

        // 更新工具栏
        btnBack.style.display = 'flex';
        toolbarTitle.textContent = article.title;
        layoutToggle.style.display = 'none';

        // 隐藏列表
        articleList.style.display = 'none';
        emptyState.style.display = 'none';
        loadingState.style.display = 'flex';
        articleDetail.style.display = 'none';

        try {
            const resp = await fetch(article.file);
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            const mdText = await resp.text();
            const htmlContent = marked.parse(mdText);

            const dateStr = formatDate(article.date);
            let tagsHTML = '';
            if (article.tags && article.tags.length > 0) {
                tagsHTML = article.tags
                    .map((t) => `<span class="tag">${escapeHTML(t)}</span>`)
                    .join('');
            }

            articleDetail.innerHTML = `
                        <div class="article-detail-header">
                            <h1 class="article-detail-title">${escapeHTML(article.title)}</h1>
                            <div class="article-detail-meta">
                                <span>📅 ${dateStr}</span>
                            </div>
                            ${tagsHTML ? `<div class="article-detail-tags">${tagsHTML}</div>` : ''}
                        </div>
                        <div class="markdown-body">${htmlContent}</div>
                    `;

            loadingState.style.display = 'none';
            articleDetail.style.display = 'block';
            contentArea.scrollTop = 0;
        } catch (err) {
            console.error('加载文章失败:', err);
            loadingState.style.display = 'none';
            articleDetail.style.display = 'block';
            articleDetail.innerHTML = `
                        <div class="empty-state">
                            <p>😢 文章加载失败，请检查文件路径是否正确。</p>
                            <p style="font-size:0.8rem;color:var(--text-muted);">${escapeHTML(err.message)}</p>
                        </div>
                    `;
        }
    }

    function goBackToList() {
        currentView = 'list';
        currentArticleId = null;
        btnBack.style.display = 'none';
        toolbarTitle.textContent = '文章列表';
        layoutToggle.style.display = 'flex';
        articleDetail.style.display = 'none';
        loadingState.style.display = 'none';
        renderArticleList();
        contentArea.scrollTop = 0;
    }

    // ============ 工具函数 ============
    function escapeHTML(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    // ============ 响应式处理 ============
    function handleResize() {
        const isMobile = window.innerWidth <= 768;
        if (isMobile && layoutMode === 'grid') {
            // 移动端虽然强制列表显示，但保持 grid 状态以便恢复
            // 实际上通过 CSS 已经处理了移动端的显示
        }
        // 移动端隐藏布局切换按钮
        if (isMobile) {
            layoutToggle.style.display = 'none';
        } else if (currentView === 'list') {
            layoutToggle.style.display = 'flex';
        }
    }

    window.addEventListener('resize', handleResize);

    // ============ 键盘导航 ============
    window.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && currentView === 'article') {
            goBackToList();
        }
    });

    // ============ 启动 ============
    async function init() {
        initUI();
        handleResize();
        loadingState.style.display = 'flex';
        emptyState.style.display = 'none';
        articleList.style.display = 'none';

        await loadArticles();
        renderArticleList();

        if (articles.length === 0) {
            loadingState.style.display = 'none';
            emptyState.style.display = 'flex';
        } else {
            loadingState.style.display = 'none';
        }
    }

    // DOM 加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();