# -*- coding: utf-8 -*-
"""
AI 提示词超级工作台 - Linear/Vercel 级专业 SaaS 界面
设计系统：深色主题 + 精致玻璃拟态 + Bento Grid
配色方案：Emerald→Blue 渐变 (#10B981 → #3B82F6)
字体系统：Plus Jakarta Sans（标题）/ Inter（正文）/ JetBrains Mono（代码）
布局：顶部导航栏 + 分类 Tab 横向滚动 + Bento 卡片网格
API 接入：智谱清言 BigModel (glm-4.7-flash 30B 级 SOTA，支持思考模式)
"""

import streamlit as st
import streamlit.components.v1 as components
from prompts_data import PROMPTS_DATA
from openai import OpenAI

# ==========================================
# 页面配置
# ==========================================
st.set_page_config(
    page_title="PromptHub AI - 提示词超级工作台",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ==========================================
# LocalStorage 积分持久化（防止刷新重置）
# ==========================================
components.html(
    """
<script>
// 初始化积分：从 LocalStorage 读取，默认 10
if (window.parent.st_streamlit === undefined) {
    window.parent.st_streamlit = {};
}
var savedCredits = localStorage.getItem('promptHub_credits');
if (savedCredits === null) {
    savedCredits = 10;
    localStorage.setItem('promptHub_credits', savedCredits);
}
window.parent.st_streamlit.savedCredits = parseInt(savedCredits);

// 提供全局函数：更新积分到 LocalStorage
window.parent.st_streamlit.updateCredits = function(newCredits) {
    localStorage.setItem('promptHub_credits', newCredits);
};

// 提供全局函数：重置积分
window.parent.st_streamlit.resetCredits = function() {
    localStorage.setItem('promptHub_credits', 10);
};
</script>
""",
    height=0,
    width=0,
)

# ==========================================
# Session State 初始化
# ==========================================
if "credits" not in st.session_state:
    # 从 LocalStorage 读取，默认 10
    st.session_state.credits = 10
if "credits_loaded" not in st.session_state:
    st.session_state.credits_loaded = False
if "results" not in st.session_state:
    st.session_state.results = {}
if "selected_category" not in st.session_state:
    st.session_state.selected_category = "全部"
if "show_settings" not in st.session_state:
    st.session_state.show_settings = False
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "base_url" not in st.session_state:
    st.session_state.base_url = "https://open.bigmodel.cn/api/paas/v4"
if "model_name" not in st.session_state:
    st.session_state.model_name = "glm-4.7-flash"
if "api_provider" not in st.session_state:
    st.session_state.api_provider = "智谱清言 (BigModel)"

# ==========================================
# 设计系统 - CSS 注入（核心！）
# ==========================================
st.markdown(
    """
<style>
/* =====================
   0. CSS 变量 / 设计令牌
   ===================== */
:root {
    --bg-primary: #0F172A;
    --bg-secondary: #1E293B;
    --bg-tertiary: #334155;
    --bg-input: rgba(15, 23, 42, 0.6);
    --text-primary: #F1F5F9;
    --text-secondary: #94A3B8;
    --text-muted: #64748B;
    --accent-start: #10B981;
    --accent-end: #3B82F6;
    --accent-primary: #10B981;
    --accent-hover: #059669;
    --accent-glow: rgba(16, 185, 129, 0.15);
    --accent-secondary: #3B82F6;
    --gradient-primary: linear-gradient(135deg, #10B981 0%, #3B82F6 100%);
    --gradient-primary-hover: linear-gradient(135deg, #059669 0%, #2563EB 100%);
    --danger: #EF4444;
    --warning: #F59E0B;
    --success: #10B981;
    --glass-bg: rgba(30, 41, 59, 0.4);
    --glass-border: rgba(255, 255, 255, 0.08);
    --glass-shadow: 0 4px 24px rgba(0, 0, 0, 0.3);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 24px;
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.2);
    --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.3);
    --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.4);
    --shadow-glow: 0 0 20px var(--accent-glow);
    --transition-base: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    --section-gap: 1.5rem;
}

/* =====================
   1. 字体引入 & 全局重置
   ===================== */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, #root, .stApp, .stApp > header, .stApp > .main, .stApp > .main .block-container {
    background: var(--bg-primary) !important;
}

* {
    box-sizing: border-box;
}

body, .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
    font-weight: 400;
    line-height: 1.6;
    color: var(--text-secondary);
}

h1, h2, h3, h4, h5, h6,
.hero-title, .navbar-title, .card-title, .settings-title {
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
}

code, pre, .template-preview, .copy-btn {
    font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', monospace !important;
}

.stApp > header {
    background: transparent !important;
    border-bottom: none !important;
    padding-top: 0 !important;
}

#MainMenu, footer, header {
    visibility: hidden !important;
}
.stDeployButton { display: none !important; }

.main .block-container {
    padding-top: 1rem !important;
    padding-bottom: 4rem !important;
    max-width: 1400px !important;
}

/* 消除 Streamlit 默认的元素间距 */
[data-testid="stVerticalBlock"] > div {
    margin-bottom: 0 !important;
}

[data-testid="stHorizontalBlock"] > div {
    margin-bottom: 0 !important;
}

/* =====================
   2. 顶部导航栏（精致玻璃拟态）
   ===================== */
.navbar {
    position: sticky;
    top: 0.75rem;
    z-index: 999;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1.5rem;
    margin-bottom: var(--section-gap);
    background: var(--glass-bg);
    backdrop-filter: blur(16px) saturate(180%);
    -webkit-backdrop-filter: blur(16px) saturate(180%);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    box-shadow: var(--glass-shadow);
    transition: var(--transition-base);
}

.navbar-brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.navbar-logo {
    width: 40px;
    height: 40px;
    background: var(--gradient-primary);
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.125rem;
    font-weight: 800;
    color: white;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
    transition: var(--transition-base);
}

.navbar-logo:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(16, 185, 129, 0.35);
}

.navbar-title {
    font-size: 1.125rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    line-height: 1.3;
}

.navbar-subtitle {
    font-size: 0.75rem;
    color: var(--text-muted);
    font-weight: 400;
    line-height: 1.3;
}

.credit-badge {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: var(--gradient-primary);
    border-radius: 999px;
    color: white;
    font-weight: 600;
    font-size: 0.8125rem;
    white-space: nowrap;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.15), 0 2px 8px rgba(16, 185, 129, 0.3);
    transition: var(--transition-base);
}

.credit-badge:hover {
    transform: translateY(-1px);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.2), 0 4px 16px rgba(16, 185, 129, 0.4);
}

/* =====================
   3. Hero 区域
   ===================== */
.hero-section {
    text-align: center;
    padding: 3rem 0;
    margin-bottom: var(--section-gap);
}

.hero-title {
    font-size: 2.5rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, var(--text-primary) 0%, var(--accent-start) 50%, var(--accent-end) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 1rem 0;
    line-height: 1.2;
}

.hero-description {
    font-size: 0.875rem;
    color: var(--text-secondary);
    max-width: 560px;
    margin: 0 auto;
    line-height: 1.6;
    font-weight: 400;
}

.hero-steps {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    margin-top: 1.5rem;
    flex-wrap: wrap;
}

.hero-step {
    display: flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.375rem 0.75rem;
    background: var(--glass-bg);
    backdrop-filter: blur(8px);
    border: 1px solid var(--glass-border);
    border-radius: 999px;
    font-size: 0.75rem;
    color: var(--text-secondary);
    font-weight: 500;
    transition: var(--transition-base);
}

.hero-step:hover {
    border-color: rgba(16, 185, 129, 0.2);
    background: rgba(30, 41, 59, 0.6);
}

.hero-step-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    background: var(--gradient-primary);
    color: white;
    border-radius: 50%;
    font-size: 0.625rem;
    font-weight: 700;
    line-height: 1;
}

.hero-arrow {
    color: var(--text-muted);
    font-size: 0.75rem;
}

/* =====================
   4. 分类 Tab 栏
   ===================== */
.category-tabs {
    display: flex;
    align-items: stretch;
    gap: 0.25rem;
    padding: 0.375rem;
    margin-bottom: var(--section-gap);
    background: rgba(30, 41, 59, 0.5);
    backdrop-filter: blur(8px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
}

.category-tabs::-webkit-scrollbar { display: none; }

/* Streamlit 按钮覆盖为 Tab 样式 */
div[data-testid="stHorizontalBlock"] button[kind^="secondary"],
div[data-testid="stHorizontalBlock"] button[kind="primary"] {
    background: transparent !important;
    border: 1px solid transparent !important;
    color: var(--text-secondary) !important;
    font-size: 0.8125rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 0.75rem !important;
    border-radius: var(--radius-md) !important;
    box-shadow: none !important;
    min-height: auto !important;
    height: auto !important;
    transition: var(--transition-base) !important;
    width: 100% !important;
    letter-spacing: 0.01em !important;
}

div[data-testid="stHorizontalBlock"] button[kind^="secondary"]:hover {
    background: var(--bg-tertiary) !important;
    color: var(--text-primary) !important;
}

div[data-testid="stHorizontalBlock"] button[kind^="secondary"]:active {
    transform: scale(0.97) !important;
}

div[data-testid="stHorizontalBlock"] button[kind="primary"] {
    background: var(--gradient-primary) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.25) !important;
}

div[data-testid="stHorizontalBlock"] button[kind="primary"]:hover {
    background: var(--gradient-primary-hover) !important;
    box-shadow: 0 4px 16px rgba(16, 185, 129, 0.35) !important;
    transform: translateY(-1px) !important;
}

div[data-testid="stHorizontalBlock"] button[kind="primary"]:active {
    transform: scale(0.97) !important;
}

/* =====================
   5. 设置面板
   ===================== */
.settings-section {
    margin-bottom: var(--section-gap);
}

/* =====================
   6. 提示词卡片（精致玻璃拟态）
   ===================== */
.card-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;
    margin-bottom: var(--section-gap);
}

.prompt-card {
    background: var(--glass-bg);
    backdrop-filter: blur(16px) saturate(180%);
    -webkit-backdrop-filter: blur(16px) saturate(180%);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    transition: var(--transition-base);
    position: relative;
    overflow: hidden;
    height: 100%;
    display: flex;
    flex-direction: column;
    opacity: 0;
    animation: cardFadeIn 0.4s ease forwards;
}

@keyframes cardFadeIn {
    from {
        opacity: 0;
        transform: translateY(16px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.prompt-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--accent-start), var(--accent-end));
    opacity: 1;
    transition: opacity var(--transition-base);
}

.prompt-card:hover {
    transform: translateY(-4px);
    border-color: rgba(16, 185, 129, 0.3);
    box-shadow: 0 8px 32px rgba(16, 185, 129, 0.15), 0 4px 24px rgba(0, 0, 0, 0.3);
}

.card-category {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.625rem;
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 999px;
    color: var(--accent-secondary);
    font-size: 0.6875rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    width: fit-content;
    transition: var(--transition-base);
}

.card-category:hover {
    background: rgba(59, 130, 246, 0.15);
    border-color: rgba(59, 130, 246, 0.3);
}

.card-title {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0.75rem 0 0.5rem 0;
    letter-spacing: -0.01em;
    line-height: 1.35;
}

.card-description {
    font-size: 0.8125rem;
    color: var(--text-secondary);
    line-height: 1.6;
    margin-bottom: 1rem;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    font-weight: 400;
}

/* =====================
   7. 提示词模板区域 + 复制按钮
   ===================== */
.template-area {
    position: relative;
    margin-bottom: 1rem;
    flex: 1;
}

.template-preview {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: var(--radius-md);
    padding: 0.75rem 1rem;
    font-size: 0.75rem;
    line-height: 1.6;
    color: var(--text-secondary);
    font-family: 'JetBrains Mono', 'Fira Code', 'SF Mono', monospace !important;
    max-height: 120px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-word;
}

.copy-btn {
    position: absolute;
    top: 0.5rem;
    right: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.3rem 0.625rem;
    background: rgba(30, 41, 59, 0.8);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: var(--text-secondary);
    font-size: 0.6875rem;
    font-weight: 500;
    cursor: pointer;
    transition: var(--transition-base);
    z-index: 2;
    line-height: 1.4;
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
}

.copy-btn:hover {
    background: var(--gradient-primary);
    color: white;
    border-color: transparent;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
}

.copy-btn:active {
    transform: scale(0.96);
}

.copy-btn.copied {
    background: var(--gradient-primary);
    color: white;
    border-color: transparent;
}

/* =====================
   8. 输入框 + 按钮覆盖
   ===================== */
.action-row {
    display: flex;
    gap: 0.5rem;
    margin-top: 0.5rem;
}

/* Streamlit text_input 覆盖 */
.stTextInput > div > div > input, .stTextInput input {
    background: var(--bg-input) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-size: 0.8125rem !important;
    font-weight: 400 !important;
    padding: 0.625rem 0.875rem !important;
    height: auto !important;
    transition: var(--transition-base) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif !important;
}

.stTextInput > div > div > input:focus {
    border-color: #10B981 !important;
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1) !important;
    background: rgba(15, 23, 42, 0.8) !important;
}

.stTextInput > div > div > input::placeholder {
    color: #64748B !important;
}

/* Streamlit primary button 覆盖 — 卡片内生成按钮 */
.stButton > button[kind="primary"] {
    background: var(--gradient-primary) !important;
    border: none !important;
    color: white !important;
    border-radius: var(--radius-md) !important;
    font-weight: 600 !important;
    font-size: 0.8125rem !important;
    padding: 0.625rem 1.25rem !important;
    height: auto !important;
    letter-spacing: 0.01em !important;
    transition: var(--transition-base) !important;
    box-shadow: 0 2px 8px rgba(16, 185, 129, 0.2) !important;
}

.stButton > button[kind="primary"]:hover {
    background: var(--gradient-primary-hover) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 16px rgba(16, 185, 129, 0.3) !important;
}

.stButton > button[kind="primary"]:active {
    transform: scale(0.98) !important;
}

/* Streamlit secondary button 覆盖 */
.stButton > button[kind="secondary"] {
    background: rgba(30, 41, 59, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: var(--text-secondary) !important;
    border-radius: var(--radius-md) !important;
    font-weight: 500 !important;
    font-size: 0.8125rem !important;
    padding: 0.625rem 1.25rem !important;
    height: auto !important;
    transition: var(--transition-base) !important;
}

.stButton > button[kind="secondary"]:hover {
    background: rgba(51, 65, 85, 0.5) !important;
    color: var(--text-primary) !important;
    border-color: rgba(255, 255, 255, 0.15) !important;
}

.stButton > button[kind="secondary"]:active {
    transform: scale(0.98) !important;
}

/* 所有按钮通用 */
.stButton > button {
    border-radius: var(--radius-md) !important;
    font-weight: 600 !important;
    font-size: 0.8125rem !important;
    height: auto !important;
    transition: var(--transition-base) !important;
    letter-spacing: 0.01em !important;
}

/* =====================
   9. 生成结果区域
   ===================== */
.result-area {
    margin-top: 1rem;
    padding: 1rem;
    background: rgba(16, 185, 129, 0.04);
    border: 1px solid rgba(16, 185, 129, 0.15);
    border-radius: var(--radius-md);
    font-size: 0.8125rem;
    line-height: 1.65;
    color: var(--text-primary);
    white-space: pre-wrap;
    word-break: break-word;
    animation: resultSlideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
}

@keyframes resultSlideUp {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

/* 流式输出光标闪烁效果 */
.stream-cursor::after {
    content: '';
    animation: blink 1s step-end infinite;
    color: var(--accent-primary);
    font-weight: bold;
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
}

/* =====================
   10. Toast 通知
   ===================== */
.toast {
    position: fixed;
    bottom: 2rem;
    left: 50%;
    transform: translateX(-50%) translateY(24px);
    padding: 0.75rem 1.5rem;
    background: rgba(30, 41, 59, 0.9);
    backdrop-filter: blur(16px) saturate(180%);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    color: var(--text-primary);
    font-size: 0.8125rem;
    font-weight: 500;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    z-index: 10000;
    opacity: 0;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    pointer-events: none;
}

.toast.show {
    transform: translateX(-50%) translateY(0);
    opacity: 1;
}

.toast.success {
    border-color: rgba(16, 185, 129, 0.3);
    background: rgba(16, 185, 129, 0.1);
    backdrop-filter: blur(16px) saturate(180%);
}

.toast.error {
    border-color: rgba(239, 68, 68, 0.3);
    background: rgba(239, 68, 68, 0.1);
    backdrop-filter: blur(16px) saturate(180%);
    color: #FCA5A5;
}

.toast.warning {
    border-color: rgba(245, 158, 11, 0.3);
    background: rgba(245, 158, 11, 0.1);
    backdrop-filter: blur(16px) saturate(180%);
    color: #FCD34D;
}

/* =====================
   11. 底部
   ===================== */
.footer {
    text-align: center;
    padding: 2rem 1rem;
    color: var(--text-muted);
    font-size: 0.75rem;
    border-top: 1px solid var(--glass-border);
    margin-top: 3rem;
    line-height: 1.8;
}

.footer a {
    color: var(--accent-primary);
    text-decoration: none;
    transition: color 0.2s ease;
}

.footer a:hover {
    color: var(--accent-end);
}

/* =====================
   12. Streamlit 全局组件覆盖
   ===================== */
.stSelectbox > div > div > select {
    background: var(--bg-input) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-size: 0.8125rem !important;
    padding: 0.625rem 0.875rem !important;
    transition: var(--transition-base) !important;
}

.stSelectbox > div > div > select:focus {
    border-color: #10B981 !important;
    box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1) !important;
}

.stExpander {
    background: var(--glass-bg) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-lg) !important;
    backdrop-filter: blur(16px) saturate(180%) !important;
    margin-bottom: 0 !important;
}

.stExpander > div {
    border: none !important;
}

[data-testid="stExpander"] .element-container {
    margin-bottom: 0.25rem !important;
}

/* Expander 箭头清理 */
[data-testid="stExpander"] summary::marker {
    content: "" !important;
    display: none !important;
}

[data-testid="stExpander"] summary::-webkit-details-marker {
    display: none !important;
}

[data-testid="stExpander"] .st-emotion-cache-1ad7f0p svg,
[data-testid="stExpander"] svg[class*="arrow"],
[data-testid="stExpander"] [class*="Arrow"],
[data-testid="stExpander"] [class*="arrow"] {
    visibility: hidden !important;
    width: 0 !important;
    height: 0 !important;
}

[data-testid="stExpander"] .st-emotion-cache-1ad7f0p,
[data-testid="stExpander"] .st-emotion-cache-1e76sdc,
[data-testid="stExpander"] [class^="st-emotion"] > span:first-child,
[data-testid="stExpander"] summary > span:first-child {
    display: none !important;
}

[data-testid="stExpander"] span[data-baseweb="icon"],
[data-testid="stExpander"] span[role="img"] {
    display: none !important;
}

/* 消除 columns 的额外间距 */
[data-testid="stColumn"] {
    padding-left: 0.375rem !important;
    padding-right: 0.375rem !important;
}

[data-testid="stForm"] {
    margin-bottom: 0 !important;
}

.element-container {
    margin-bottom: 0.25rem !important;
}

/* =====================
   13. 滚动条美化
   ===================== */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
    background: #475569;
}

/* =====================
   14. 空状态
   ===================== */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: var(--text-muted);
}

.empty-state-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    opacity: 0.6;
}

.empty-state-title {
    font-size: 0.9375rem;
    font-weight: 500;
    margin-bottom: 0.5rem;
    color: var(--text-secondary);
}

.empty-state-desc {
    font-size: 0.8125rem;
    color: var(--text-muted);
}

/* =====================
   15. 分割线样式
   ===================== */
hr {
    border: none !important;
    border-top: 1px solid var(--glass-border) !important;
    margin: 1rem 0 !important;
}

/* =====================
   16. 响应式
   ===================== */
@media (max-width: 768px) {
    .hero-title { font-size: 1.75rem !important; }
    .hero-section { padding: 2rem 0 !important; }
    .navbar { padding: 0.625rem 1rem !important; }
    .navbar-title { font-size: 1rem !important; }
    .navbar-subtitle { display: none !important; }
    .navbar-logo { width: 36px !important; height: 36px !important; }
    .credit-badge { padding: 0.375rem 0.75rem !important; font-size: 0.75rem !important; }
    .prompt-card { padding: 1.25rem !important; }
    .card-grid { grid-template-columns: 1fr !important; gap: 1rem !important; }
    .hero-steps { gap: 0.375rem !important; }
    .hero-step { font-size: 0.6875rem !important; padding: 0.25rem 0.5rem !important; }
}

@media (min-width: 769px) and (max-width: 1024px) {
    .card-grid { grid-template-columns: repeat(2, 1fr) !important; }
    .hero-title { font-size: 2rem !important; }
}

@media (min-width: 1025px) {
    .card-grid { grid-template-columns: repeat(3, 1fr) !important; }
}
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# JavaScript 注入
# ==========================================
st.markdown(
    """
<script>
// =====================
// Toast 通知系统
// =====================
function showToast(message, type) {
    type = type || 'success';
    var existing = document.querySelectorAll('.toast');
    existing.forEach(function(t) { t.remove(); });

    var toast = document.createElement('div');
    toast.className = 'toast ' + type;

    var icon = '';
    if (type === 'success') icon = '<span style="margin-right:6px">✓</span>';
    else if (type === 'error') icon = '<span style="margin-right:6px">✕</span>';
    else if (type === 'warning') icon = '<span style="margin-right:6px"></span>';

    toast.innerHTML = icon + message;
    document.body.appendChild(toast);

    requestAnimationFrame(function() {
        requestAnimationFrame(function() {
            toast.classList.add('show');
        });
    });

    setTimeout(function() {
        toast.classList.remove('show');
        setTimeout(function() { toast.remove(); }, 300);
    }, 3000);
}

// =====================
// 剪贴板复制
// =====================
function copyToClipboard(text, btnElement) {
    navigator.clipboard.writeText(text).then(function() {
        btnElement.innerHTML = '<span style="margin-right:4px">✓</span>已复制';
        btnElement.classList.add('copied');
        showToast('提示词已复制到剪贴板', 'success');
        setTimeout(function() {
            btnElement.textContent = '复制';
            btnElement.classList.remove('copied');
        }, 2000);
    }).catch(function() {
        showToast('复制失败，请手动复制', 'error');
    });
}

// =====================
// 复制按钮初始化
// =====================
function initCopyButtons() {
    var copyBtns = document.querySelectorAll('.copy-btn:not([data-bound])');
    copyBtns.forEach(function(btn) {
        btn.setAttribute('data-bound', 'true');
        btn.onclick = function(e) {
            e.preventDefault();
            e.stopPropagation();
            var targetId = this.getAttribute('data-target');
            var target = document.getElementById(targetId);
            if (target) {
                copyToClipboard(target.textContent, this);
            }
        };
    });
}

// =====================
// 卡片入场动画（stagger）
// =====================
function initCardAnimations() {
    var cards = document.querySelectorAll('.prompt-card:not([data-animated])');
    cards.forEach(function(card, index) {
        card.setAttribute('data-animated', 'true');
        card.style.animationDelay = (index * 50) + 'ms';
    });
}

// =====================
// Ripple 效果
// =====================
function createRipple(event) {
    var button = event.currentTarget;
    var existing = button.querySelector('.ripple-effect');
    if (existing) existing.remove();

    var ripple = document.createElement('span');
    ripple.className = 'ripple-effect';
    var rect = button.getBoundingClientRect();
    var size = Math.max(rect.width, rect.height);
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = (event.clientX - rect.left - size / 2) + 'px';
    ripple.style.top = (event.clientY - rect.top - size / 2) + 'px';
    ripple.style.position = 'absolute';
    ripple.style.borderRadius = '50%';
    ripple.style.background = 'rgba(255, 255, 255, 0.2)';
    ripple.style.transform = 'scale(0)';
    ripple.style.animation = 'ripple 0.6s ease-out';
    ripple.style.pointerEvents = 'none';

    var style = window.getComputedStyle(button);
    if (style.position === 'static') {
        button.style.position = 'relative';
    }
    button.style.overflow = 'hidden';
    button.appendChild(ripple);

    setTimeout(function() { ripple.remove(); }, 600);
}

var rippleStyle = document.createElement('style');
rippleStyle.textContent = '@keyframes ripple { to { transform: scale(4); opacity: 0; } }';
document.head.appendChild(rippleStyle);

function initRippleEffects() {
    var buttons = document.querySelectorAll('.stButton > button:not([data-ripple])');
    buttons.forEach(function(btn) {
        btn.setAttribute('data-ripple', 'true');
        btn.addEventListener('click', createRipple);
    });
}

// =====================
// 清理 Expander 箭头
// =====================
function cleanExpanderArrows() {
    var expanders = document.querySelectorAll('[data-testid="stExpander"]');
    expanders.forEach(function(exp) {
        var walker = document.createTreeWalker(exp, NodeFilter.SHOW_TEXT, null, false);
        var node;
        while (node = walker.nextNode()) {
            if (node.textContent.trim() === '_arrow' || node.textContent.trim() === 'Arrow') {
                node.parentNode.removeChild(node);
            }
        }
    });
}

// =====================
// 初始化
// =====================
function init() {
    initCopyButtons();
    initCardAnimations();
    initRippleEffects();
    setTimeout(cleanExpanderArrows, 500);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

var observer = new MutationObserver(function() {
    init();
});
observer.observe(document.body, { childList: true, subtree: true });

setInterval(cleanExpanderArrows, 3000);
</script>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 顶部导航栏
# ==========================================
st.markdown(
    f"""
<div class="navbar">
    <div class="navbar-brand">
        <div class="navbar-logo">P</div>
        <div>
            <div class="navbar-title">PromptHub AI</div>
            <div class="navbar-subtitle">提示词超级工作台</div>
        </div>
    </div>
    <div class="credit-badge">
        <span>⚡</span>
        <span>{st.session_state.credits} 积分</span>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# Hero 区域
# ==========================================
st.markdown(
    """
<div class="hero-section">
    <h1 class="hero-title">让 AI 提示词产生复利价值</h1>
    <p class="hero-description">
        精选高质量提示词模板，一键替换变量，AI 即时生成专业内容。
        <br>覆盖写作、职场、编程、营销、小红书、学习六大场景。
    </p>
    <div class="hero-steps">
        <div class="hero-step"><span class="hero-step-num">1</span>选择分类</div>
        <span class="hero-arrow">→</span>
        <div class="hero-step"><span class="hero-step-num">2</span>复制提示词</div>
        <span class="hero-arrow">→</span>
        <div class="hero-step"><span class="hero-step-num">3</span>填入变量</div>
        <span class="hero-arrow">→</span>
        <div class="hero-step"><span class="hero-step-num">4</span>AI 生成</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 分类 Tab 栏
# ==========================================
CATEGORIES = ["全部", "写作", "职场", "编程", "营销", "小红书", "学习"]

st.markdown('<div class="category-tabs">', unsafe_allow_html=True)

cat_cols = st.columns(len(CATEGORIES))
for i, cat in enumerate(CATEGORIES):
    with cat_cols[i]:
        if st.button(
            cat,
            key=f"cat_{cat}",
            type="primary" if cat == st.session_state.selected_category else "secondary",
            use_container_width=True,
        ):
            st.session_state.selected_category = cat
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 筛选提示词
# ==========================================
selected = st.session_state.selected_category
if selected == "全部":
    filtered_prompts = PROMPTS_DATA
else:
    filtered_prompts = [p for p in PROMPTS_DATA if p["category"] == selected]

if "show_settings" not in st.session_state:
    st.session_state.show_settings = False

# ==========================================
# 设置面板
# ==========================================
st.markdown('<div class="settings-section">', unsafe_allow_html=True)

settings_toggle_label = "▼ 收起设置" if st.session_state.show_settings else "▶ API 设置 & 卡密充值"
toggle_col1, toggle_col2 = st.columns([1, 10])
with toggle_col1:
    if st.button("⚙️", key="settings_toggle_btn", use_container_width=True, type="primary" if st.session_state.show_settings else "secondary"):
        st.session_state.show_settings = not st.session_state.show_settings
        st.rerun()
with toggle_col2:
    st.markdown(
        f"""
<div style="display:flex;align-items:center;height:38px;color:var(--text-secondary);font-size:0.875rem;font-weight:500;padding-left:0.5rem;letter-spacing:0.01em;">
    {settings_toggle_label}
</div>
""",
        unsafe_allow_html=True,
    )

if st.session_state.show_settings:
    st.markdown('<div class="settings-body">', unsafe_allow_html=True)

    # ==================== API 服务商选择 ====================
    API_PROVIDERS = {
        "智谱清言 (BigModel)": {
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "models": ["glm-4.7-flash", "glm-4-flash", "glm-4", "glm-4-air", "glm-4-flashx"],
            "help_key": "🔑 获取方式：访问 https://open.bigmodel.cn → 注册登录 → API 密钥 → 创建密钥",
            "help_model": " glm-4.7-flash: 30B 级 SOTA，编码/写作/前端审美最强（推荐）",
        },
        "DeepSeek": {
            "base_url": "https://api.deepseek.com/v1",
            "models": ["deepseek-chat", "deepseek-reasoner"],
            "help_key": "🔑 获取方式：访问 https://platform.deepseek.com → 注册登录 → API 密钥",
            "help_model": " deepseek-chat: 通用对话 / deepseek-reasoner: 深度推理",
        },
        "硅基流动 (SiliconFlow)": {
            "base_url": "https://api.siliconflow.cn/v1",
            "models": ["Pro/deepseek-ai/DeepSeek-V3", "Pro/deepseek-ai/DeepSeek-R1", "Qwen/Qwen2.5-72B-Instruct"],
            "help_key": "🔑 获取方式：访问 https://cloud.siliconflow.cn → 注册登录 → API 密钥",
            "help_model": " 硅基流动提供多种开源模型，按需选择",
        },
    }

    api_provider = st.selectbox(
        "API 服务商",
        options=list(API_PROVIDERS.keys()),
        index=list(API_PROVIDERS.keys()).index(st.session_state.api_provider) if st.session_state.api_provider in API_PROVIDERS else 0,
        help="选择你要使用的 AI API 服务商",
    )

    # 当切换服务商时，自动更新 base_url 和 model 列表
    provider_config = API_PROVIDERS[api_provider]
    if api_provider != st.session_state.api_provider:
        st.session_state.api_provider = api_provider
        st.session_state.base_url = provider_config["base_url"]
        # 尝试保留之前的模型选择（如果在新列表中）
        if st.session_state.model_name not in provider_config["models"]:
            st.session_state.model_name = provider_config["models"][0]
        st.rerun()

    st.markdown('<div style="margin-top: 0.75rem; margin-bottom: 0.25rem;">', unsafe_allow_html=True)

    col_api1, col_api2 = st.columns([1, 1])
    with col_api1:
        new_api_key = st.text_input(
            "API Key",
            value=st.session_state.api_key,
            type="password",
            placeholder="请输入你的 API Key",
            help=provider_config["help_key"],
        )
    with col_api2:
        new_base_url = st.text_input(
            "Base URL",
            value=st.session_state.base_url,
            help=f"{api_provider} API 基础地址，可手动修改。",
        )

    # 找到默认模型的索引
    model_options = provider_config["models"]
    default_idx = model_options.index(st.session_state.model_name) if st.session_state.model_name in model_options else 0

    new_model_name = st.selectbox(
        "选择模型",
        options=model_options,
        index=default_idx,
        help=provider_config["help_model"],
    )

    # 保存按钮
    save_col1, save_col2, save_col3 = st.columns([1, 1, 1])
    with save_col1:
        if st.button("💾 保存配置", use_container_width=True, type="primary"):
            st.session_state.api_key = new_api_key
            st.session_state.base_url = new_base_url
            st.session_state.model_name = new_model_name
            st.success("配置已保存！")

    with save_col2:
        if st.button("🔄 重置默认", use_container_width=True, type="secondary"):
            st.session_state.api_key = ""
            st.session_state.api_provider = "智谱清言 (BigModel)"
            st.session_state.base_url = "https://open.bigmodel.cn/api/paas/v4"
            st.session_state.model_name = "glm-4.7-flash"
            st.success("已重置为默认配置！")
            st.rerun()

    with save_col3:
        if st.button(" 重置积分", use_container_width=True, type="secondary"):
            st.session_state.credits = 10
            components.html(
                """
<script>
    window.parent.st_streamlit.resetCredits();
    window.parent.location.reload();
</script>
""",
                height=0,
                width=0,
            )
            st.success("积分已重置为 10！")
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    st.markdown('<div style="font-weight:600;font-size:0.875rem;color:var(--text-secondary);margin-bottom:0.5rem;letter-spacing:0.01em;">卡密充值</div>', unsafe_allow_html=True)
    recharge_col1, recharge_col2 = st.columns([2, 1])
    with recharge_col1:
        recharge_code = st.text_input(
            "输入卡密",
            placeholder="请输入充值卡密，例如 VIP2024",
            label_visibility="collapsed",
        )
    with recharge_col2:
        if st.button("兑换积分", use_container_width=True, type="primary"):
            if recharge_code.strip() == "VIP2024":
                st.session_state.credits += 100
                components.html(
                    f"""
<script>
    window.parent.st_streamlit.updateCredits({st.session_state.credits});
</script>
""",
                    height=0,
                    width=0,
                )
                st.success("兑换成功！已增加 100 积分！")
                st.rerun()
            else:
                st.error("卡密无效，请联系客服获取正确卡密。")

    st.markdown('</div>', unsafe_allow_html=True)

# 始终从 session_state 读取 API 配置
api_key = st.session_state.api_key
base_url = st.session_state.base_url
model_name = st.session_state.model_name

# ==========================================
# Bento Grid 卡片展示
# ==========================================
if not filtered_prompts:
    st.markdown(
        """
<div class="empty-state">
    <div class="empty-state-icon">📭</div>
    <div class="empty-state-title">暂无提示词</div>
    <div class="empty-state-desc">该分类下暂无提示词，请选择其他分类。</div>
</div>
""",
        unsafe_allow_html=True,
    )
else:
    cols = st.columns(3)

    for idx, prompt in enumerate(filtered_prompts):
        col = cols[idx % 3]
        with col:
            card_html = f"""
<div class="prompt-card" style="animation-delay: {idx * 50}ms">
    <span class="card-category">{prompt['category']}</span>
    <div class="card-title">{prompt['title']}</div>
    <div class="card-description">{prompt['description']}</div>
"""
            st.markdown(card_html, unsafe_allow_html=True)

            # 提示词模板 + 复制按钮
            template_id = f"tmpl_{prompt['id']}"
            st.markdown(
                f"""
<div class="template-area">
    <button class="copy-btn" data-target="{template_id}" onclick="copyToClipboard(document.getElementById('{template_id}').textContent, this)">复制</button>
    <div class="template-preview" id="{template_id}">{prompt['template']}</div>
</div>
""",
                unsafe_allow_html=True,
            )

            # 变量输入 + 生成按钮
            user_input = st.text_input(
                "输入变量",
                key=f"input_{prompt['id']}",
                placeholder="例如：Python 入门教程",
                label_visibility="collapsed",
            )

            # 生成结果展示容器（使用 placeholder 实现流式更新）
            result_placeholder = st.empty()

            if st.button(
                "✨ AI 生成",
                key=f"btn_{prompt['id']}",
                use_container_width=True,
                type="primary",
            ):
                # 前置检查：积分
                if st.session_state.credits <= 0:
                    st.markdown(
                        """
<div style="
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(239, 68, 68, 0.08) 100%);
    border: 2px solid rgba(245, 158, 11, 0.4);
    border-radius: var(--radius-lg);
    padding: 1.25rem 1.5rem;
    margin: 0.75rem 0;
    box-shadow: 0 0 24px rgba(245, 158, 11, 0.15);
    animation: resultSlideUp 0.3s cubic-bezier(0.4, 0, 0.2, 1);
">
    <div style="
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.75rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(245, 158, 11, 0.2);
    ">
        <span style="font-size: 1.25rem;">⚠️</span>
        <span style="
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 1rem;
            font-weight: 700;
            color: #F59E0B;
            letter-spacing: -0.01em;
        ">免费体验额度（10次）已用完！</span>
    </div>

    <div style="margin-bottom: 0.75rem;">
        <div style="
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.625rem 0.875rem;
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: var(--radius-md);
            margin-bottom: 0.5rem;
        ">
            <span style="font-size: 1rem;">🎁</span>
            <span style="color: #F1F5F9; font-size: 0.875rem; font-weight: 500;">
                添加主理人 <strong style="color: #10B981; font-weight: 700;">小刚</strong> 微信：
                <span style="
                    display: inline-block;
                    padding: 0.125rem 0.5rem;
                    background: rgba(16, 185, 129, 0.2);
                    border-radius: 6px;
                    color: #10B981;
                    font-family: 'JetBrains Mono', monospace;
                    font-weight: 700;
                    font-size: 0.875rem;
                    letter-spacing: 0.05em;
                ">esadmin</span>
                <br>回复暗号 <strong style="color: #F59E0B;">【领积分】</strong>，即可免费获取 <strong style="color: #10B981;">100 积分卡密</strong>！
            </span>
        </div>
    </div>

    <div style="
        padding: 0.5rem 0.75rem;
        background: rgba(59, 130, 246, 0.08);
        border-radius: var(--radius-md);
        border-left: 3px solid #3B82F6;
    ">
        <span style="font-size: 0.8125rem; color: #94A3B8; line-height: 1.6;">
            📚 同时免费赠送 <strong style="color: #F1F5F9;">《2026国内免费大模型API羊毛指南》</strong>
            （含智谱、DeepSeek、硅基流动等白嫖教程）<br>
            🎫 及 <strong style="color: #F1F5F9;">【AI搞钱内部交流群】</strong> 入场券！
        </span>
    </div>
</div>
""",
                        unsafe_allow_html=True,
                    )

                # 前置检查：API Key
                elif not api_key.strip():
                    st.error("请先在设置面板填入 API Key！")

                # 前置检查：输入变量
                elif not user_input.strip():
                    st.warning("请先输入变量内容再生成。")

                else:
                    # 替换模板中的 [主题] 变量
                    filled_prompt = prompt["template"].replace("[主题]", user_input)

                    # 积分扣减标记（移到 try 外部，确保 except 可访问）
                    first_token_received = False

                    try:
                        # 初始化智谱清言 OpenAI 客户端
                        client = OpenAI(api_key=api_key, base_url=base_url)

                        # 构建请求参数
                        request_params = {
                            "model": model_name,
                            "messages": [
                                {"role": "user", "content": filled_prompt}
                            ],
                            "stream": True,
                        }

                        # 调用 chat.completions.create() 流式输出
                        response = client.chat.completions.create(**request_params)

                        # 实时流式展示
                        full_content = ""
                        reasoning_content = ""  # GLM-4.7 思考过程
                        first_token_received = False  # 标记：是否已收到第一个 token

                        for chunk in response:
                            if chunk.choices and len(chunk.choices) > 0:
                                delta = chunk.choices[0].delta
                                
                                # GLM-4.7 思考过程输出
                                if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                                    reasoning_content += delta.reasoning_content
                                
                                # 正式内容
                                if delta.content:
                                    # 第一个 token 到达时才扣积分
                                    if not first_token_received:
                                        first_token_received = True
                                        st.session_state.credits -= 1
                                        # 同步更新到 LocalStorage
                                        components.html(
                                            f"""
<script>
    window.parent.st_streamlit.updateCredits({st.session_state.credits});
</script>
""",
                                            height=0,
                                            width=0,
                                        )

                                    full_content += delta.content
                                    # 实时更新显示
                                    display_content = ""
                                    if reasoning_content:
                                        display_content += f'<div style="color: var(--text-muted); font-size: 0.75rem; margin-bottom: 0.5rem; padding: 0.5rem; background: rgba(59, 130, 246, 0.05); border-radius: var(--radius-sm); border-left: 2px solid var(--accent-secondary);">💭 思考过程：{reasoning_content}</div>'
                                    display_content += full_content
                                    
                                    result_placeholder.markdown(
                                        f'<div class="result-area stream-cursor">{display_content}</div>',
                                        unsafe_allow_html=True,
                                    )

                        # 流式输出完成，移除光标效果，保存结果
                        final_content = ""
                        if reasoning_content:
                            final_content += f'<div style="color: var(--text-muted); font-size: 0.75rem; margin-bottom: 0.5rem; padding: 0.5rem; background: rgba(59, 130, 246, 0.05); border-radius: var(--radius-sm); border-left: 2px solid var(--accent-secondary);">💭 思考过程：{reasoning_content}</div>'
                        final_content += full_content
                        
                        result_placeholder.markdown(
                            f'<div class="result-area">{final_content}</div>',
                            unsafe_allow_html=True,
                        )
                        st.session_state.results[f"result_{prompt['id']}"] = final_content

                        # 成功提示（显示剩余积分）
                        st.success(f"生成成功！扣除 1 积分，当前剩余 {st.session_state.credits} 积分")

                    except Exception as e:
                        # 详细异常处理
                        error_type = type(e).__name__

                        if "AuthenticationError" in error_type or "authentication" in str(e).lower():
                            error_msg = "API Key 无效或余额不足，请检查你的密钥。"
                            st.error(f"❌ {error_msg}")
                            st.caption(f"原始错误：{e}")

                        elif "APIConnectionError" in error_type or "connection" in str(e).lower() or "timeout" in str(e).lower():
                            error_msg = "网络连接失败，请检查 Base URL 是否正确。"
                            st.error(f"❌ {error_msg}")
                            st.caption(f"当前 Base URL: {base_url}")
                            st.caption(f"原始错误：{e}")

                        else:
                            # 其他异常
                            error_msg = f"请求失败：{e}"
                            st.error(f"❌ {error_msg}")

                        # API 调用失败，不扣积分
                        if not first_token_received:
                            st.warning("⚠️ 未扣除积分，请重试。")

            # 显示之前的生成结果（非流式状态下的持久化）
            # 注意：只有在没有刚生成新结果时才显示历史记录
            result_key = f"result_{prompt['id']}"
            if result_key in st.session_state.results:
                result_placeholder.markdown(
                    f'<div class="result-area">{st.session_state.results[result_key]}</div>',
                    unsafe_allow_html=True,
                )

            st.markdown("</div>", unsafe_allow_html=True)

# ==========================================
# 底部
# ==========================================
st.markdown(
    """
<div class="footer">
    PromptHub AI — AI 提示词超级工作台
</div>
""",
    unsafe_allow_html=True,
)
