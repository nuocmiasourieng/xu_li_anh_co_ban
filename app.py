import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

# ---------------------- CẤU HÌNH TRANG ----------------------
st.set_page_config(page_title="Xử lý Ảnh Chuyên Nghiệp", layout="wide")
st.title("🎨 Ứng dụng Xử Lý Ảnh - Tách kênh màu, Độ sáng, Tương phản, Lật, Cân bằng Histogram")

# Khởi tạo session_state để lưu ảnh gốc và ảnh đang xử lý
if "original_img" not in st.session_state:
    st.session_state.original_img = None
if "processed_img" not in st.session_state:
    st.session_state.processed_img = None
if "brightness" not in st.session_state:
    st.session_state.brightness = 0
if "contrast" not in st.session_state:
    st.session_state.contrast = 1.0

# ---------------------- HÀM TIỆN ÍCH ----------------------
def load_image(image_file):
    """Đọc ảnh từ file upload (PIL -> OpenCV BGR)"""
    pil_img = Image.open(image_file)
    # Chuyển PIL (RGB) sang OpenCV (BGR)
    cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    return cv_img

def apply_brightness_contrast(img, brightness=0, contrast=1.0):
    """
    Điều chỉnh độ sáng và tương phản theo công thức:
    G(x,y) = α * F(x,y) + β
    Với pivot = 127.5 để tránh cháy sáng/tối.
    brightness: giá trị từ -100 đến 100 (sẽ chuyển thành β)
    contrast: giá trị từ 0.1 đến 3.0 (α)
    """
    # Chuyển đổi brightness (thanh trượt -100..100) sang beta thực tế
    beta = brightness  # Thực chất brightness từ slider là beta trực tiếp? 
    # Nhưng công thức chuẩn: beta = brightness * 127.5 / 100? 
    # Trong tài liệu dùng pivot: adjusted_beta = 127.5*(1-α) + β
    # Tôi sẽ làm đơn giản: dùng cv2.convertScaleAbs với alpha=contrast, beta=brightness
    # Tuy nhiên để giống Photoshop pivot, ta làm thủ công:
    # Lưu ý: img là uint8, cần chuyển sang float để tính
    img_float = img.astype(np.float32)
    # Công thức với pivot
    alpha = contrast
    pivot = 127.5
    adjusted = alpha * (img_float - pivot) + pivot + brightness
    # Giới hạn giá trị về [0,255]
    adjusted = np.clip(adjusted, 0, 255)
    return adjusted.astype(np.uint8)

def adjust_brightness_contrast_wrapper():
    """Hàm bọc để cập nhật ảnh từ các thanh trượt"""
    if st.session_state.original_img is not None:
        img = st.session_state.original_img.copy()
        bright = st.session_state.brightness
        cont = st.session_state.contrast
        st.session_state.processed_img = apply_brightness_contrast(img, bright, cont)

def update_processed_img(new_img):
    """Cập nhật ảnh đã xử lý và reset brightness/contrast về mặc định"""
    st.session_state.processed_img = new_img.copy()
    st.session_state.brightness = 0
    st.session_state.contrast = 1.0

# ---------------------- GIAO DIỆN CHÍNH ----------------------
# Chia 2 cột: bên trái hiển thị ảnh, bên phải bảng điều khiển
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("📸 Ảnh hiện tại")
    # Nếu chưa có ảnh thì hiển thị placeholder
    if st.session_state.processed_img is not None:
        # Chuyển OpenCV BGR sang RGB để hiển thị với st.image
        display_img = cv2.cvtColor(st.session_state.processed_img, cv2.COLOR_BGR2RGB)
        st.image(display_img, use_container_width=True)
    else:
        st.info("👈 Hãy tải ảnh lên từ bảng điều khiển bên phải")

with col_right:
    st.subheader("🛠️ Bảng điều khiển")
    
    # ---------- NHÓM QUẢN LÝ TỆP ----------
    st.markdown("### 📂 Quản lý Tệp")
    uploaded_file = st.file_uploader("Mở Ảnh Mới", type=["jpg", "jpeg", "png", "bmp"])
    if uploaded_file is not None:
        img_cv = load_image(uploaded_file)
        st.session_state.original_img = img_cv.copy()
        st.session_state.processed_img = img_cv.copy()
        st.session_state.brightness = 0
        st.session_state.contrast = 1.0
        st.success("Đã tải ảnh thành công!")
        st.rerun()  # Làm mới để hiển thị ảnh ngay
    
    col_save, col_reset = st.columns(2)
    with col_save:
        if st.button("💾 Lưu Ảnh", use_container_width=True):
            if st.session_state.processed_img is not None:
                # Chuyển ảnh đang xử lý sang RGB để lưu
                save_img_rgb = cv2.cvtColor(st.session_state.processed_img, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(save_img_rgb)
                buf = io.BytesIO()
                pil_img.save(buf, format="PNG")
                byte_im = buf.getvalue()
                st.download_button(
                    label="📥 Tải xuống",
                    data=byte_im,
                    file_name="anh_da_xu_ly.png",
                    mime="image/png",
                    key="download_btn"
                )
            else:
                st.warning("Chưa có ảnh để lưu")
    with col_reset:
        if st.button("🔄 Khôi phục Ảnh Gốc", use_container_width=True):
            if st.session_state.original_img is not None:
                st.session_state.processed_img = st.session_state.original_img.copy()
                st.session_state.brightness = 0
                st.session_state.contrast = 1.0
                st.rerun()
            else:
                st.warning("Chưa có ảnh gốc")

    st.divider()
    
    # ---------- NHÓM ÁNH SÁNG & TƯƠNG PHẢN ----------
    st.markdown("### ☀️ Ánh sáng & Tương phản")
    if st.session_state.original_img is not None:
        bright_val = st.slider("Độ sáng", -100, 100, st.session_state.brightness, key="bright_slider")
        cont_val = st.slider("Độ tương phản", 10, 300, int(st.session_state.contrast*100), key="cont_slider") / 100.0
        if bright_val != st.session_state.brightness or cont_val != st.session_state.contrast:
            st.session_state.brightness = bright_val
            st.session_state.contrast = cont_val
            adjust_brightness_contrast_wrapper()
            st.rerun()
    else:
        st.info("Hãy mở ảnh trước")
    
    st.divider()
    
    # ---------- NHÓM TÁCH KÊNH MÀU ----------
    st.markdown("### 🎨 Tách kênh màu (R, G, B)")
    col_r, col_g, col_b = st.columns(3)
    if st.session_state.processed_img is not None:
        img_temp = st.session_state.processed_img.copy()
        with col_r:
            if st.button("🔴 Kênh R", use_container_width=True):
                # Giữ kênh đỏ (OpenCV: kênh 2 là R), set 2 kênh kia về 0
                tach = img_temp.copy()
                tach[:, :, 0] = 0  # B
                tach[:, :, 1] = 0  # G
                update_processed_img(tach)
                st.rerun()
        with col_g:
            if st.button("🟢 Kênh G", use_container_width=True):
                tach = img_temp.copy()
                tach[:, :, 0] = 0  # B
                tach[:, :, 2] = 0  # R
                update_processed_img(tach)
                st.rerun()
        with col_b:
            if st.button("🔵 Kênh B", use_container_width=True):
                tach = img_temp.copy()
                tach[:, :, 1] = 0  # G
                tach[:, :, 2] = 0  # R
                update_processed_img(tach)
                st.rerun()
    else:
        st.info("Chưa có ảnh")
    
    st.divider()
    
    # ---------- NHÓM BIẾN ĐỔI & HIỆU ỨNG ----------
    st.markdown("### 🔄 Biến đổi & Hiệu ứng")
    col_flip_h, col_flip_v = st.columns(2)
    if st.session_state.processed_img is not None:
        with col_flip_h:
            if st.button("🔄 Lật ngang", use_container_width=True):
                flipped = cv2.flip(st.session_state.processed_img, 1)
                update_processed_img(flipped)
                st.rerun()
        with col_flip_v:
            if st.button("↕️ Lật dọc", use_container_width=True):
                flipped = cv2.flip(st.session_state.processed_img, 0)
                update_processed_img(flipped)
                st.rerun()
        
        st.markdown("#### 🧪 Nhân màu (tăng cường 1 kênh)")
        col_mul_r, col_mul_g, col_mul_b = st.columns(3)
        with col_mul_r:
            if st.button("Nhân đôi kênh R"):
                img_mul = st.session_state.processed_img.copy()
                img_mul[:, :, 2] = cv2.convertScaleAbs(img_mul[:, :, 2], alpha=2.0)
                update_processed_img(img_mul)
                st.rerun()
        with col_mul_g:
            if st.button("Nhân đôi kênh G"):
                img_mul = st.session_state.processed_img.copy()
                img_mul[:, :, 1] = cv2.convertScaleAbs(img_mul[:, :, 1], alpha=2.0)
                update_processed_img(img_mul)
                st.rerun()
        with col_mul_b:
            if st.button("Nhân đôi kênh B"):
                img_mul = st.session_state.processed_img.copy()
                img_mul[:, :, 0] = cv2.convertScaleAbs(img_mul[:, :, 0], alpha=2.0)
                update_processed_img(img_mul)
                st.rerun()
        
        if st.button("📊 Cân bằng Histogram", use_container_width=True):
            # Chuyển sang grayscale, equalize, rồi chuyển lại BGR
            gray = cv2.cvtColor(st.session_state.processed_img, cv2.COLOR_BGR2GRAY)
            eq_gray = cv2.equalizeHist(gray)
            eq_bgr = cv2.cvtColor(eq_gray, cv2.COLOR_GRAY2BGR)
            update_processed_img(eq_bgr)
            st.rerun()
    else:
        st.info("Chưa có ảnh để thực hiện")
