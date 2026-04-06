import streamlit as st
from PIL import Image, ImageOps, ImageEnhance
import io

# ==================== HÀM XỬ LÝ SEPia ====================
def apply_sepia(img):
    """Hàm chuyển ảnh sang tông màu Sepia (màu cổ điển)"""
    img = img.convert('RGB')
    width, height = img.size
    pixels = img.load()
    
    for y in range(height):
        for x in range(width):
            r, g, b = pixels[x, y]
            # Công thức Sepia chuẩn
            tr = int(r * 0.393 + g * 0.769 + b * 0.189)
            tg = int(r * 0.349 + g * 0.686 + b * 0.168)
            tb = int(r * 0.272 + g * 0.534 + b * 0.131)
            pixels[x, y] = (min(tr, 255), min(tg, 255), min(tb, 255))
    return img

# ==================== GIAO DIỆN WEB ====================
st.set_page_config(page_title="Xử Lý Ảnh", page_icon="🖼️", layout="wide")
st.title("🖼️ Xử Lý Ảnh Cơ Bản Bằng Python")
st.write("Upload ảnh và áp dụng các bộ lọc đơn giản (đổi màu, grayscale, sepia...)")

# Upload ảnh
uploaded_file = st.file_uploader(
    "📤 Chọn ảnh để upload (JPG, PNG, JPEG)", 
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    # Mở ảnh
    image = Image.open(uploaded_file)
    
    # Chia 2 cột: ảnh gốc | ảnh đã xử lý
    col1, col2 = st.columns(2)
    
    with col1:
        st.image(image, caption="📸 Ảnh gốc", use_column_width=True)
    
    # Sidebar - chọn bộ lọc
    st.sidebar.header("🎛️ Cài đặt bộ lọc")
    filter_type = st.sidebar.selectbox(
        "Chọn loại bộ lọc",
        [
            "Không thay đổi (Original)",
            "Grayscale (Đen trắng)",
            "Negative (Đảo màu)",
            "Sepia (Màu cổ điển)",
            "Tăng độ sáng (Brightness +)",
            "Tăng tương phản (Contrast +)",
            "Tint màu (Đổi màu theo lựa chọn)"
        ]
    )

    # Xử lý ảnh theo lựa chọn
    processed_image = image  # mặc định là ảnh gốc

    if filter_type == "Grayscale (Đen trắng)":
        processed_image = ImageOps.grayscale(image).convert('RGB')
    elif filter_type == "Negative (Đảo màu)":
        processed_image = ImageOps.invert(image)
    elif filter_type == "Sepia (Màu cổ điển)":
        processed_image = apply_sepia(image)
    elif filter_type == "Tăng độ sáng (Brightness +)":
        enhancer = ImageEnhance.Brightness(image)
        processed_image = enhancer.enhance(1.5)
    elif filter_type == "Tăng tương phản (Contrast +)":
        enhancer = ImageEnhance.Contrast(image)
        processed_image = enhancer.enhance(1.5)
    elif filter_type == "Tint màu (Đổi màu theo lựa chọn)":
        tint_color_hex = st.sidebar.color_picker("🎨 Chọn màu tint", value="#FF5733")
        # Chuyển hex sang RGB
        r = int(tint_color_hex[1:3], 16)
        g = int(tint_color_hex[3:5], 16)
        b = int(tint_color_hex[5:7], 16)
        # Tạo lớp overlay màu
        tint_overlay = Image.new('RGB', image.size, (r, g, b))
        processed_image = Image.blend(image, tint_overlay, alpha=0.4)  # 0.4 = độ đậm của màu

    # Hiển thị ảnh sau xử lý
    with col2:
        st.image(processed_image, caption=f"✅ {filter_type}", use_column_width=True)

    # Nút tải ảnh
    buf = io.BytesIO()
    processed_image.save(buf, format="PNG")
    byte_data = buf.getvalue()
    
    st.download_button(
        label="📥 Tải ảnh đã xử lý về máy",
        data=byte_data,
        file_name="anh_da_xu_ly.png",
        mime="image/png",
        use_container_width=True
    )

else:
    st.info("👆 Hãy upload một ảnh để bắt đầu xử lý nhé!")

st.caption("🚀 Được tạo bằng Streamlit + Pillow | Code trên GitHub")
