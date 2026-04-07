import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

# ---------- CẤU HÌNH TRANG ----------
st.set_page_config(page_title="Bộ lọc Ảnh Pro", layout="wide", initial_sidebar_state="collapsed")

# CSS tùy chỉnh (nền đen, chữ vàng, nút vàng)
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    h1, h2, h3, .stMarkdown, label {
        color: #FFD700 !important;
    }
    .stButton > button {
        background-color: #FFD700;
        color: #000000;
        font-weight: bold;
        border-radius: 8px;
        border: none;
    }
    .stButton > button:hover {
        background-color: #e6c200;
        transform: scale(1.02);
    }
    .stSlider div[data-baseweb="slider"] div {
        background-color: #FFD700;
    }
    hr {
        border-color: #FFD700;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎨 Ứng dụng xử lý ảnh chuyên nghiệp")
st.caption("Giao diện Đen - Vàng | Tùy chỉnh độ sáng, tương phản, lọc màu, hiệu ứng")

# ---------- KHỞI TẠO SESSION STATE ----------
if "original" not in st.session_state:
    st.session_state.original = None   # ảnh gốc BGR
if "processed" not in st.session_state:
    st.session_state.processed = None  # ảnh đang chỉnh sửa BGR
if "brightness" not in st.session_state:
    st.session_state.brightness = 0
if "contrast" not in st.session_state:
    st.session_state.contrast = 1.0

# ---------- HÀM XỬ LÝ ----------
def load_image(uploaded):
    pil = Image.open(uploaded).convert("RGB")
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

def apply_brightness_contrast(img, brightness, contrast):
    pivot = 127.5
    img_float = img.astype(np.float32)
    adjusted = contrast * (img_float - pivot) + pivot + brightness
    return np.clip(adjusted, 0, 255).astype(np.uint8)

def apply_sepia(img):
    sepia = np.array([[0.272, 0.534, 0.131],
                      [0.349, 0.686, 0.168],
                      [0.393, 0.769, 0.189]])
    result = img.astype(np.float32) @ sepia.T
    return np.clip(result, 0, 255).astype(np.uint8)

def extract_channel(img, channel):
    out = img.copy()
    if channel == 'R':
        out[:, :, 0] = 0
        out[:, :, 1] = 0
    elif channel == 'G':
        out[:, :, 0] = 0
        out[:, :, 2] = 0
    else:  # B
        out[:, :, 1] = 0
        out[:, :, 2] = 0
    return out

# ---------- GIAO DIỆN 2 CỘT ----------
col_left, col_right = st.columns([2.2, 1], gap="medium")

with col_left:
    st.subheader("📷 Ảnh hiện tại")
    if st.session_state.processed is not None:
        # Hiển thị ảnh đã qua sáng/tương phản (nhưng chưa lưu vào processed)
        display = apply_brightness_contrast(st.session_state.processed,
                                             st.session_state.brightness,
                                             st.session_state.contrast)
        display_rgb = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
        st.image(display_rgb, use_container_width=True)
    else:
        st.info("👈 Tải ảnh lên từ bảng điều khiển bên phải")

with col_right:
    st.markdown("## 🛠️ Bảng điều khiển")
    
    # ----- TẢI ẢNH -----
    uploaded = st.file_uploader("Mở ảnh mới", type=["jpg","jpeg","png"])
    if uploaded is not None:
        img = load_image(uploaded)
        st.session_state.original = img.copy()
        st.session_state.processed = img.copy()
        st.session_state.brightness = 0
        st.session_state.contrast = 1.0
        st.success("✅ Đã tải ảnh")
        st.rerun()
    
    # ----- ĐỘ SÁNG / TƯƠNG PHẢN -----
    if st.session_state.processed is not None:
        bright = st.slider("Độ sáng", -100, 100, st.session_state.brightness, key="bri")
        cont = st.slider("Tương phản", 10, 300, int(st.session_state.contrast*100), key="con") / 100.0
        if bright != st.session_state.brightness or cont != st.session_state.contrast:
            st.session_state.brightness = bright
            st.session_state.contrast = cont
            st.rerun()
    else:
        st.info("Chưa có ảnh")
    
    st.divider()
    
    # ----- BỘ LỌC NHANH -----
    st.markdown("### 🎨 Bộ lọc đặc biệt")
    if st.session_state.processed is not None:
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            if st.button("✨ Sepia", use_container_width=True):
                st.session_state.processed = apply_sepia(st.session_state.processed)
                st.rerun()
        with col_f2:
            if st.button("⚫ Xám", use_container_width=True):
                gray = cv2.cvtColor(st.session_state.processed, cv2.COLOR_BGR2GRAY)
                st.session_state.processed = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                st.rerun()
        with col_f3:
            if st.button("🔄 Khôi phục", use_container_width=True):
                if st.session_state.original is not None:
                    st.session_state.processed = st.session_state.original.copy()
                    st.rerun()
    else:
        st.info("Chưa có ảnh")
    
    st.markdown("#### 🧩 Tách kênh màu")
    if st.session_state.processed is not None:
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🔴 Kênh R"):
                st.session_state.processed = extract_channel(st.session_state.processed, 'R')
                st.rerun()
        with c2:
            if st.button("🟢 Kênh G"):
                st.session_state.processed = extract_channel(st.session_state.processed, 'G')
                st.rerun()
        with c3:
            if st.button("🔵 Kênh B"):
                st.session_state.processed = extract_channel(st.session_state.processed, 'B')
                st.rerun()
    else:
        st.info("Chưa có ảnh")
    
    st.markdown("#### 🔄 Lật ảnh")
    if st.session_state.processed is not None:
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            if st.button("↔️ Lật ngang"):
                st.session_state.processed = cv2.flip(st.session_state.processed, 1)
                st.rerun()
        with col_l2:
            if st.button("↕️ Lật dọc"):
                st.session_state.processed = cv2.flip(st.session_state.processed, 0)
                st.rerun()
    
    # ----- LƯU ẢNH -----
    if st.session_state.processed is not None:
        st.divider()
        # Ảnh để lưu là processed đã qua sáng/tương phản
        final = apply_brightness_contrast(st.session_state.processed,
                                           st.session_state.brightness,
                                           st.session_state.contrast)
        final_rgb = cv2.cvtColor(final, cv2.COLOR_BGR2RGB)
        pil_final = Image.fromarray(final_rgb)
        buf = io.BytesIO()
        pil_final.save(buf, format="PNG")
        st.download_button("💾 Lưu ảnh kết quả", data=buf.getvalue(),
                           file_name="filtered_image.png", mime="image/png")
