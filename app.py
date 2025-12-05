import streamlit as st
import requests
from PIL import Image
import io
from anilist_client import get_anime_info

# 设置页面配置
st.set_page_config(
    page_title="AnimeHunter - 动漫场景搜寻",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS - 增强美观度
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #ff4b4b;
    }
    .css-1y4p8pa {
        padding-top: 1rem;
    }
    h1 {
        color: #2c3e50;
    }
    h3 {
        color: #34495e;
    }
    </style>
""", unsafe_allow_html=True)

def format_time(seconds):
    """将秒转换为 mm:ss 格式"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def search_anime(image_bytes):
    """调用 trace.moe API 搜索"""
    api_url = "https://api.trace.moe/search"
    try:
        files = {"image": image_bytes}
        # 添加 cutBorders 参数，有时能提高准确率
        params = {"cutBorders": ""}
        response = requests.post(api_url, files=files, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API 请求失败: {e}")
        return None

# --- 侧边栏配置 ---
with st.sidebar:
    st.title("⚙️ 设置")
    
    st.markdown("### 偏好选项")
    show_r18 = st.checkbox("显示 R-18 内容", value=False, help="勾选后将显示成人向动漫的搜索结果")
    
    st.divider()
    
    st.header("关于 AnimeHunter")
    st.info("""
    **怎么用？**
    1. 截图你看过的动漫画面。
    2. 拖拽上传到右侧区域。
    3. 点击搜索，我们将帮你找到它的出处！
    """)
    
    st.markdown("---")
    st.caption("数据来源: trace.moe & Anilist")
    st.caption("Designed by Gemini")

# --- 主界面 ---
st.title("🌸 AnimeHunter")
st.markdown("#### 🔍 发现动漫的每一个精彩瞬间")

uploaded_file = st.file_uploader("请上传一张动漫截图 (JPG/PNG)", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:
    st.divider()
    col1, col2 = st.columns([1, 1.5])
    
    with col1:
        st.markdown("##### 📸 你的截图")
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True, caption="预览")
        
        # 准备 API 数据
        uploaded_file.seek(0)
        image_bytes = uploaded_file.read()
        
        if st.button("🚀 开始识别", type="primary"):
            with st.spinner("✨ 正在搜索二次元宇宙..."):
                result = search_anime(image_bytes)
                
            if result and not result.get("error"):
                st.session_state['results'] = result.get("result", [])
                st.toast("搜索完成！", icon="🎉")
            elif result and result.get("error"):
                st.error(f"API 错误: {result['error']}")

    # --- 结果显示区域 ---
    with col2:
        if 'results' in st.session_state and st.session_state['results']:
            st.markdown("##### 🎯 最佳匹配结果")
            
            display_count = 0
            
            for item in st.session_state['results']:
                # 最多显示 3 个有效结果
                if display_count >= 3:
                    break
                
                similarity = item.get('similarity', 0)
                if similarity < 0.50:  # 忽略相似度过低的结果
                    continue

                # 获取元数据
                anilist_id = item.get('anilist')
                metadata = get_anime_info(anilist_id)
                
                # --- R-18 过滤逻辑 ---
                is_adult = False
                if metadata:
                    is_adult = metadata.get('isAdult', False)
                
                if is_adult and not show_r18:
                    continue # 跳过该结果
                
                display_count += 1
                
                # 准备展示数据
                title_native = "未知标题"
                title_english = ""
                cover_image = None
                
                if metadata:
                    title = metadata.get('title', {})
                    title_native = title.get('native') or title.get('romaji')
                    title_english = title.get('english')
                    cover_image = metadata.get('coverImage', {}).get('large')
                
                if not metadata:
                    title_native = item.get('filename', '未知文件')

                # --- 卡片式布局 ---
                with st.container():
                    # 使用 columns 在卡片内部布局
                    c_img, c_info = st.columns([1, 3])
                    
                    with c_img:
                        if cover_image:
                            st.image(cover_image, use_container_width=True)
                        else:
                            st.image("https://placehold.co/200x300?text=No+Cover", use_container_width=True)
                    
                    with c_info:
                        st.subheader(title_native)
                        if title_english:
                            st.caption(f"🇬🇧 {title_english}")
                        
                        if is_adult:
                            st.warning("🔞 R-18 内容")

                        # 信息行 (移除嵌套 columns)
                        st.info(f"🎬 **集数:** {item.get('episode', '?')}  |  ⏱ **时间:** {format_time(item.get('from', 0))}")
                        
                        # 相似度进度条
                        st.progress(similarity, text=f"匹配度: {similarity*100:.2f}%")

                        # 视频预览
                        with st.expander("🎥 点击预览片段"):
                            video_url = item.get('video')
                            if video_url:
                                st.video(video_url)
                            else:
                                st.write("暂无预览")
                        
                        # 原始文件名（调试用，默认折叠）
                        with st.expander("📄 原始文件名"):
                            st.code(item.get('filename', ''))
                    
                    st.divider()

            if display_count == 0:
                st.warning("没有找到匹配结果 (或者结果被过滤)。")
        
        else:
            # 占位符，引导用户操作
            st.info("👈 在左侧上传图片并点击“开始识别”来查看结果")


