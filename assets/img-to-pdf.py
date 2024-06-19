# main code
import streamlit as st
from streamlit_sortables import sort_items
from PIL import Image, ExifTags
import os, shutil
import atexit
import pyheif
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import pillow_heif

def cleanup():
    shutil.rmtree("uploads", ignore_errors=True)

def correct_orientation(image):
    try:
        exif = image._getexif()
        if exif is not None:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break

            if orientation in exif:
                orientation_value = exif[orientation]
                rotate_values = {
                    3: 180,
                    6: 270,
                    8: 90
                }

                if orientation_value in rotate_values:
                    image = image.rotate(rotate_values[orientation_value], expand=True)
    except (AttributeError, KeyError, IndexError):
        pass

    return image

def save_uploaded_images(uploaded_images):
    uploaded_paths = []
    uploaded_image_names = set()

    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    for uploaded_image in uploaded_images:
        original_filename, ext = os.path.splitext(uploaded_image.name)

        if ext.lower() in ['.heic', '.heif']:
            try:
                heif_file = pyheif.read_heif(uploaded_image)
                image = Image.frombytes(
                    heif_file.mode,
                    heif_file.size,
                    heif_file.data,
                    "raw",
                    heif_file.mode,
                    heif_file.stride,
                )
                image = correct_orientation(image)
                ext = '.jpg'

                new_filename = f"{original_filename}.jpg"
                counter = 1
                while new_filename in uploaded_image_names:
                    new_filename = f"{original_filename}({counter}).jpg"
                    counter += 1

                uploaded_image_names.add(new_filename)
                image_path = os.path.join("uploads", new_filename)
                image.save(image_path, "JPEG")
            except Exception as e:
                st.error(f"Error processing HEIF image: {e}")
                continue
        else:
            try:
                new_filename = f"{original_filename}{ext}"
                counter = 1

                while new_filename in uploaded_image_names:
                    new_filename = f"{original_filename}({counter}){ext}"
                    counter += 1

                uploaded_image_names.add(new_filename)
                image_path = os.path.join("uploads", new_filename)

                bytes_buffer = io.BytesIO(uploaded_image.read())
                bytes_buffer.seek(0)

                with open(image_path, "wb") as f:
                    f.write(bytes_buffer.read())

                image = Image.open(image_path)
                image = correct_orientation(image)
                image.save(image_path)
            except Exception as e:
                st.error(f"Error processing image {original_filename}{ext}: {e}")
                continue

        uploaded_paths.append(image_path)

    return uploaded_paths

def display_images(uploaded_paths, reordered_paths):
    images_per_row = 3
    num_images = len(reordered_paths)
    num_rows = num_images // images_per_row + (num_images % images_per_row > 0)

    for i in range(num_rows):
        row_images = reordered_paths[i * images_per_row: (i + 1) * images_per_row]
        st.write("\n")

        row_images_display = []
        captions = []
        for filename in row_images:
            try:
                image_path = os.path.join("uploads", filename)
                image = Image.open(image_path)
                image = correct_orientation(image)
                image = image.resize((200, 200))
                row_images_display.append(image)
                captions.append(f"Page {i * images_per_row + len(row_images_display)}: {os.path.basename(filename)}")
            
            except OSError:
                pass

        if row_images_display:
            st.image(row_images_display, caption=captions, width=200, use_column_width=False)
        st.write("\n")

def convert_images_to_pdf(image_paths, output_pdf_path):
    pdf_canvas = canvas.Canvas(output_pdf_path, pagesize=letter)
    page_width, page_height = letter

    for image_path in image_paths:
        img = Image.open(image_path)
        img = correct_orientation(img)
        img_width, img_height = img.size
        scale = min(page_width / img_width, page_height / img_height)
        new_width, new_height = int(img_width * scale), int(img_height * scale)

        x_offset = (page_width - new_width) // 2
        y_offset = (page_height - new_height) // 2

        pdf_canvas.setPageSize((page_width, page_height))
        pdf_canvas.drawImage(image_path, x_offset, y_offset, width=new_width, height=new_height)
        pdf_canvas.showPage()

    pdf_canvas.save()

def main():
    st.title("Images to PDF")
    uploaded_images = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png", "heic", "heif"], accept_multiple_files=True)

    if uploaded_images:
        uploaded_paths = save_uploaded_images(uploaded_images)
        st.write("Arrange the order of the images")
        reordered_paths = sort_items([os.path.basename(path) for path in uploaded_paths])
        st.write("Order for the uploaded images:")
        display_images(uploaded_paths, reordered_paths)
        output_pdf_name = st.text_input("Enter the name of the output PDF file (without extension):", "merged_images_pdf")

        if st.button("Convert to PDF"):
            output_pdf_path = os.path.join("uploads", f"{output_pdf_name}.pdf" if not output_pdf_name.endswith(".pdf") else output_pdf_name)
            convert_images_to_pdf([os.path.join("uploads", filename) for filename in reordered_paths], output_pdf_path)

            st.success("The images have been converted to PDF, and it is ready for download.")
            output_pdf_name = output_pdf_name.split('.')[0]
            st.download_button(
                label="Download PDF",
                data=open(output_pdf_path, "rb").read(),
                file_name=f"{output_pdf_name}.pdf",
                key="merged_images_pdf_button"
            )

if __name__ == "__main__":
    atexit.register(cleanup)
    main()
