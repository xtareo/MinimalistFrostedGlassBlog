// Copyright (c) <2026> <Xtareo>
// Licensed under the MIT License. See LICENSE file for details
// ==================== 配置文件 ====================
// 在这里修改你的个人信息、背景图、链接等
const CONFIG = {
    // 头像图片路径（放在 images/ 文件夹或使用在线URL）
    avatar: 'images/avatar.jpg',

    // 博主名称
    name: '博主名称',

    // 个人介绍
    bio: '这里是个人介绍，简短描述自己。喜欢计算机。',

    // 背景图片路径（放在 images/ 文件夹或使用在线URL）
    // 留空则使用默认渐变背景
    backgroundImage: '',

    // 社交链接（小图标横向排列）
    // icon 可选值: 'github', 'twitter', 'email', 'link', 'rss', 'website'
    links: [
        { name: 'GitHub', url: 'https://github.com/', icon: 'github' },
        { name: 'Link', url: '#', icon: 'link' },
        { name: 'Bilibili', url: 'https://space.bilibili.com/', icon: 'bilibili' },
    ],

    // 网站起始运行日期（格式：YYYY-MM-DD）
    startDate: '2026-07-11',

    // 版权信息（{year} 会被替换为当前年份，{startYear} 为起始年份）
    copyright: '© {startYear}-{year} 博主名称. All rights reserved.',

    // 文章列表文件路径
    articlesIndex: 'articles/list.json',

    // 默认布局模式: 'list' | 'grid'
    defaultLayout: 'list',
};