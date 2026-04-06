import streamlit as st
import cv2
import numpy as np
from PIL import Image

# Cấu hình trang
st.set_page_config(page_title="Filter Ảnh Đơn Giản", layout="centered")
st.title("🖼️ Chèn Filter vào Ảnh có sẵn")
st.markdown("Tải ảnh lên, chọn bộ lọc và nhấn **Áp dụng**")

# Tải ảnh lên
uploaded_file = st.file_uploader("Chọn ảnh từ máy tính", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Đọc ảnh và chuyển sang định dạng OpenCV (BGR)
    pil_image = Image.open(uploaded_file).convert("RGB")
    img = np.array(pil_image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Hiển thị ảnh gốc
    st.subheader("Ảnh gốc")
    st.image(pil_image, use_container_width=True)

    # Chọn filter
    filter_choice = st.selectbox(
        "Chọn bộ lọc:",
        ["Ảnh gốc", "Đen trắng", "Sepia (cổ điển)", "Làm mờ (Gaussian)", "Tăng độ sắc nét", "Chuyển sang Xám"]
    )

    # Nút áp dụng
    if st.button("✨ Áp dụng filter", type="primary"):
        result = img.copy()

        if filter_choice == "Đen trắng":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        elif filter_choice == "Sepia (cổ điển)":
            kernel = np.array([[0.272, 0.534, 0.131],
                               [0.349, 0.686, 0.168],
                               [0.393, 0.769, 0.189]])
            result = cv2.transform(img, kernel)
            result = np.clip(result, 0, 255).astype(np.uint8)
        elif filter_choice == "Làm mờ (Gaussian)":
            result = cv2.GaussianBlur(img, (15, 15), 0)
        elif filter_choice == "Tăng độ sắc nét":
            kernel = np.array([[0, -1, 0],
                               [-1, 5, -1],
                               [0, -1, 0]])
            result = cv2.filter2D(img, -1, kernel)
        elif filter_choice == "Chuyển sang Xám":
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        # Nếu chọn "Ảnh gốc" thì giữ nguyên

        # Chuyển kết quả từ BGR sang RGB để hiển thị
        result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        st.subheader("Ảnh sau khi áp dụng filter")
        st.image(result_rgb, use_container_width=True)

        # Tạo nút tải ảnh xuống
        from io import BytesIO
        result_pil = Image.fromarray(result_rgb)
        buf = BytesIO()
        result_pil.save(buf, format="PNG")
        st.download_button("📥 Tải ảnh xuống", data=buf.getvalue(), file_name="filtered_image.png", mime="image/png")

else:
    st.info("👈 Hãy tải ảnh lên để bắt đầu")
