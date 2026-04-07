import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io

# Cấu hình trang
st.set_page_config(page_title="Bộ lọc Ảnh Chuyên Nghiệp", layout="centered")
st.title("🎨 Chỉnh sửa ảnh cơ bản - Chèn hiệu ứng")
st.markdown("Tải ảnh lên, chọn hiệu ứng và nhấn **Xử lý**")

# --- Các hàm xử lý filter ---
def apply_gaussian_blur(img):
    """Làm mờ bằng Gaussian Blur (kernel 15x15)"""
    return cv2.GaussianBlur(img, (15, 15), 0)

def apply_sharpen(img):
    """Làm sắc nét bằng kernel sharpen"""
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    return cv2.filter2D(img, -1, kernel)

def apply_grayscale(img):
    """Chuyển sang ảnh xám (grayscale)"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)  # giữ 3 kênh để hiển thị

def apply_sepia(img):
    """Hiệu ứng Sepia (cổ điển)"""
    # Chuyển sang float để tính toán
    img_float = img.astype(np.float32)
    # Ma trận sepia
    sepia_matrix = np.array([[0.272, 0.534, 0.131],
                              [0.349, 0.686, 0.168],
                              [0.393, 0.769, 0.189]])
    sepia_img = img_float @ sepia_matrix.T
    sepia_img = np.clip(sepia_img, 0, 255).astype(np.uint8)
    return sepia_img

# --- Giao diện chính ---
uploaded_file = st.file_uploader("Chọn ảnh từ máy tính", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Đọc ảnh và chuyển sang định dạng OpenCV (BGR)
    pil_img = Image.open(uploaded_file).convert("RGB")
    original_img = np.array(pil_img)
    original_img = cv2.cvtColor(original_img, cv2.COLOR_RGB2BGR)

    # Hiển thị ảnh gốc
    st.subheader("📷 Ảnh gốc")
    st.image(pil_img, use_container_width=True)

    # Chọn filter
    filter_option = st.selectbox(
        "Chọn hiệu ứng:",
        ["Làm mờ (Gaussian Blur)", "Làm sắc nét (Sharpen)", "Ảnh xám (Grayscale)", "Sepia (cổ điển)"]
    )

    # Nút xử lý
    if st.button("✨ Xử lý ảnh", type="primary"):
        with st.spinner("Đang xử lý..."):
            if filter_option == "Làm mờ (Gaussian Blur)":
                result = apply_gaussian_blur(original_img)
            elif filter_option == "Làm sắc nét (Sharpen)":
                result = apply_sharpen(original_img)
            elif filter_option == "Ảnh xám (Grayscale)":
                result = apply_grayscale(original_img)
            elif filter_option == "Sepia (cổ điển)":
                result = apply_sepia(original_img)
            else:
                result = original_img

        # Chuyển kết quả từ BGR sang RGB để hiển thị
        result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        st.subheader("✨ Ảnh sau khi xử lý")
        st.image(result_rgb, use_container_width=True)

        # Tạo nút tải ảnh xuống
        result_pil = Image.fromarray(result_rgb)
        buf = io.BytesIO()
        result_pil.save(buf, format="PNG")
        st.download_button(
            label="📥 Tải ảnh xuống",
            data=buf.getvalue(),
            file_name="filtered_image.png",
            mime="image/png"
        )
else:
    st.info("Hãy tải ảnh lên để bắt đầu")
