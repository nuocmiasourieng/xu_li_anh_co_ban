import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

# ---------------------- CẤU HÌNH GIAO DIỆN MÀU ĐEN - VÀNG ----------------------
st.set_page_config(page_title="Xử Lý Ảnh Pro", layout="wide", initial_sidebar_state="collapsed")

# CSS tùy chỉnh để có nền đen, chữ vàng, các nút vàng đậm
st.markdown("""
<style>
    /* Toàn bộ nền ứng dụng */
    .stApp {
        background-color: #0e1117;
    }
    /* Tiêu đề chính */
    h1, h2, h3, .stMarkdown {
        color: #FFD700 !important;
    }
    /* Các label, text */
    .stSlider label, .stSelectbox label, .stCheckbox label {
        color: #FFD700 !important;
        font-weight: bold;
    }
    /* Nút bấm chính */
    .stButton > button {
        background-color: #FFD700;
        color: #000000;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #e6c200;
        color: #000000;
        transform: scale(1.02);
    }
    /* Thanh slider */
    .stSlider div[data-baseweb="slider"] div {
        background-color: #FFD700;
    }
    /* Khung thông báo info */
    .stAlert {
        background-color: #1e1e1e;
        border-left: 5px solid #FFD700;
    }
    /* Đường kẻ phân cách */
    hr {
        border-color: #FFD700;
    }
    /* Sidebar (nếu dùng) nhưng ta ẩn đi */
    .css-1d391kg {
        background-color: #0e1117;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ Ứng dụng Xử lý Ảnh Chuyên Nghiệp")
st.caption("Giao diện Đen - Vàng | Tách kênh RGB | Độ sáng/Tương phản | Lật | Cân bằng Histogram")

# ---------------------- KHỞI TẠO SESSION STATE ----------------------
if "original_img" not in st.session_state:
    st.session_state.original_img = None      # ảnh gốc (BGR)
if "processed_img" not in st.session_state:
    st.session_state.processed_img = None     # ảnh đã qua xử lý (BGR)
if "brightness" not in st.session_state:
    st.session_state.brightness = 0
if "contrast" not in st.session_state:
    st.session_state.contrast = 1.0

# ---------------------- HÀM XỬ LÝ ----------------------
def load_image(uploaded_file):
    """Đọc ảnh từ file upload -> trả về ảnh BGR (OpenCV)"""
    pil_img = Image.open(uploaded_file).convert("RGB")
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

def apply_brightness_contrast(img, brightness, contrast):
    """
    Điều chỉnh độ sáng & tương phản theo công thức có pivot 127.5 (giống Photoshop)
    brightness: -100 -> 100
    contrast: 0.1 -> 3.0
    """
    alpha = contrast
    beta = brightness
    # Công thức với pivot
    pivot = 127.5
    img_float = img.astype(np.float32)
    adjusted = alpha * (img_float - pivot) + pivot + beta
    adjusted = np.clip(adjusted, 0, 255)
    return adjusted.astype(np.uint8)

def update_processed_from_original():
    """Cập nhật processed_img từ original_img, reset brightness/contrast"""
    if st.session_state.original_img is not None:
        st.session_state.processed_img = st.session_state.original_img.copy()
        st.session_state.brightness = 0
        st.session_state.contrast = 1.0

def update_preview():
    """Hiển thị ảnh hiện tại (processed_img sau khi áp dụng sáng/tương phản)"""
    if st.session_state.processed_img is None:
        return
    # Áp dụng sáng/tương phản lên ảnh full (nhưng để hiển thị ta vẫn dùng full, 
    # thực tế Streamlit tự scale nên không cần cache nhỏ)
    bright = st.session_state.brightness
    cont = st.session_state.contrast
    display = apply_brightness_contrast(st.session_state.processed_img, bright, cont)
    display_rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
    return display_rgb

# ---------------------- BỐ CỤC GIAO DIỆN ----------------------
col_left, col_right = st.columns([2.5, 1.2], gap="medium")

with col_left:
    st.subheader("📸 Vùng làm việc")
    if st.session_state.processed_img is not None:
        img_display = update_preview()
        st.image(img_display, use_container_width=True, caption="Ảnh đang xử lý")
    else:
        st.info("👈 Hãy tải ảnh lên từ bảng điều khiển bên phải")

with col_right:
    st.markdown("## 🛠️ Bảng điều khiển")
    
    # --------------------- NHÓM 1: QUẢN LÝ TỆP ---------------------
    with st.expander("📂 Quản lý Tệp", expanded=True):
        uploaded_file = st.file_uploader("Mở Ảnh Mới", type=["jpg", "jpeg", "png", "bmp"], key="file_uploader")
        if uploaded_file is not None:
            img_cv = load_image(uploaded_file)
            st.session_state.original_img = img_cv.copy()
            st.session_state.processed_img = img_cv.copy()
            st.session_state.brightness = 0
            st.session_state.contrast = 1.0
            st.success("✅ Đã tải ảnh thành công!")
            st.rerun()
        
        col_save, col_reset = st.columns(2)
        with col_save:
            if st.button("💾 Lưu Ảnh", use_container_width=True):
                if st.session_state.processed_img is not None:
                    bright = st.session_state.brightness
                    cont = st.session_state.contrast
                    final = apply_brightness_contrast(st.session_state.processed_img, bright, cont)
                    final_rgb = cv2.cvtColor(final, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(final_rgb)
                    buf = io.BytesIO()
                    pil_img.save(buf, format="PNG")
                    st.download_button("⬇️ Tải xuống", data=buf.getvalue(), file_name="anh_da_xu_ly.png", mime="image/png", key="download_btn")
                else:
                    st.warning("Chưa có ảnh để lưu")
        with col_reset:
            if st.button("🔄 Khôi phục gốc", use_container_width=True):
                if st.session_state.original_img is not None:
                    st.session_state.processed_img = st.session_state.original_img.copy()
                    st.session_state.brightness = 0
                    st.session_state.contrast = 1.0
                    st.rerun()
                else:
                    st.warning("Chưa có ảnh gốc")
    
    st.divider()
    
    # --------------------- NHÓM 2: ÁNH SÁNG & TƯƠNG PHẢN ---------------------
    with st.expander("☀️ Ánh sáng & Tương phản", expanded=True):
        if st.session_state.processed_img is not None:
            brightness = st.slider("Độ sáng", -100, 100, st.session_state.brightness, key="bright")
            contrast = st.slider("Độ tương phản", 10, 300, int(st.session_state.contrast*100), key="contr") / 100.0
            if brightness != st.session_state.brightness or contrast != st.session_state.contrast:
                st.session_state.brightness = brightness
                st.session_state.contrast = contrast
                st.rerun()
        else:
            st.info("Mở ảnh trước khi điều chỉnh")
    
    st.divider()
    
    # --------------------- NHÓM 3: TÁCH KÊNH MÀU ---------------------
    with st.expander("🎨 Tách kênh màu", expanded=False):
        if st.session_state.processed_img is not None:
            col_r, col_g, col_b = st.columns(3)
            with col_r:
                if st.button("🔴 Kênh R", use_container_width=True):
                    img = st.session_state.processed_img.copy()
                    img[:, :, 0] = 0  # B
                    img[:, :, 1] = 0  # G
                    st.session_state.processed_img = img
                    st.rerun()
            with col_g:
                if st.button("🟢 Kênh G", use_container_width=True):
                    img = st.session_state.processed_img.copy()
                    img[:, :, 0] = 0  # B
                    img[:, :, 2] = 0  # R
                    st.session_state.processed_img = img
                    st.rerun()
            with col_b:
                if st.button("🔵 Kênh B", use_container_width=True):
                    img = st.session_state.processed_img.copy()
                    img[:, :, 1] = 0  # G
                    img[:, :, 2] = 0  # R
                    st.session_state.processed_img = img
                    st.rerun()
        else:
            st.info("Chưa có ảnh")
    
    st.divider()
    
    # --------------------- NHÓM 4: BIẾN ĐỔI & HIỆU ỨNG ---------------------
    with st.expander("🔄 Biến đổi & Hiệu ứng", expanded=False):
        if st.session_state.processed_img is not None:
            col_fh, col_fv = st.columns(2)
            with col_fh:
                if st.button("↔️ Lật ngang", use_container_width=True):
                    st.session_state.processed_img = cv2.flip(st.session_state.processed_img, 1)
                    st.rerun()
            with col_fv:
                if st.button("↕️ Lật dọc", use_container_width=True):
                    st.session_state.processed_img = cv2.flip(st.session_state.processed_img, 0)
                    st.rerun()
            
            st.markdown("**Nhân đôi màu (x2)**")
            col_mr, col_mg, col_mb = st.columns(3)
            with col_mr:
                if st.button("Nhân R"):
                    img = st.session_state.processed_img.copy()
                    img[:, :, 2] = cv2.convertScaleAbs(img[:, :, 2], alpha=2.0)
                    st.session_state.processed_img = img
                    st.rerun()
            with col_mg:
                if st.button("Nhân G"):
                    img = st.session_state.processed_img.copy()
                    img[:, :, 1] = cv2.convertScaleAbs(img[:, :, 1], alpha=2.0)
                    st.session_state.processed_img = img
                    st.rerun()
            with col_mb:
                if st.button("Nhân B"):
                    img = st.session_state.processed_img.copy()
                    img[:, :, 0] = cv2.convertScaleAbs(img[:, :, 0], alpha=2.0)
                    st.session_state.processed_img = img
                    st.rerun()
            
            if st.button("📊 Cân bằng Histogram", use_container_width=True):
                gray = cv2.cvtColor(st.session_state.processed_img, cv2.COLOR_BGR2GRAY)
                eq = cv2.equalizeHist(gray)
                st.session_state.processed_img = cv2.cvtColor(eq, cv2.COLOR_GRAY2BGR)
                st.rerun()
        else:
            st.info("Chưa có ảnh")

# ---------------------- FOOTER ----------------------
st.markdown("---")
st.markdown("<p style='text-align: center; color: #FFD700;'>✨ Ứng dụng xử lý ảnh chuyên nghiệp - Giao diện Đen Vàng ✨</p>", unsafe_allow_html=True)
