# main code
import streamlit as st
from streamlit_sortables import sort_items
from PIL import Image
import os, shutil
import atexit
from reportlab.pdfgen import canvas

def cleanup():
    shutil.rmtree("uploads", ignore_errors=True)

def save_uploaded_images(uploaded_images):
    uploaded_paths = []
    uploaded_image_names = set()

    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    for i, uploaded_image in enumerate(uploaded_images, start=1):
        original_filename, ext = os.path.splitext(uploaded_image.name)
        new_filename = f"{original_filename}.png"
        counter = 1

        while new_filename in uploaded_image_names:
            new_filename = f"{original_filename}({counter}).png"
            counter += 1

        uploaded_image_names.add(new_filename)
        image_path = os.path.join("uploads", new_filename)

        with open(image_path, "wb") as f:
            f.write(uploaded_image.read())
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
        for filename in row_images:
            index = uploaded_paths.index(os.path.join("uploads", filename))
            image_path = uploaded_paths[index]

            try:
                image = Image.open(image_path)
                image = image.resize((200, 200))
                row_images_display.append(image)
            
            except OSError:
                pass

        st.image(row_images_display, caption=[f"Page {i * images_per_row + j + 1}: {os.path.basename(filename)}" for j, filename in enumerate(row_images)], width=200, use_column_width=False)
        st.write("\n")

def convert_images_to_pdf(image_paths, output_pdf_path, page_size=(800, 600)):
    pdf_canvas = canvas.Canvas(output_pdf_path)
    for image_path in image_paths:
        img = Image.open(image_path)
        img.thumbnail(page_size)
        position = ((page_size[0] - img.width) // 2, (page_size[1] - img.height) // 2)
        white_background = Image.new('RGB', page_size, 'white')
        white_background.paste(img, position)
        pdf_canvas.setPageSize(page_size)
        pdf_canvas.drawInlineImage(white_background, 0, 0, width=page_size[0], height=page_size[1])
        pdf_canvas.showPage()
    pdf_canvas.save()

def main():
    st.title("Images to PDF")
    uploaded_images = st.file_uploader("Upload Images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

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
            output_pdf_name=output_pdf_name.split('.')[0]
            st.download_button(
                label="Download PDF",
                data=open(output_pdf_path, "rb").read(),
                file_name=f"{output_pdf_name}.pdf",
                key="merged_images_pdf_button"
            )

if __name__ == "__main__":
    atexit.register(cleanup)
    main()
