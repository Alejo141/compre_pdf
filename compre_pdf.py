import streamlit as st
import fitz  # PyMuPDF
import io
import zipfile
import os
import logging
logging.basicConfig(level=logging.DEBUG)

st.set_page_config(page_title="Compresor PDF en ZIP", layout="centered")
st.title("📚 Compresor de PDFs en ZIP")
st.write("Sube múltiples archivos PDF, ajusta el nivel de compresión y descarga un ZIP con los archivos comprimidos.")

# Nivel de compresión
compression_level = st.slider("🔧 Nivel de compresión (resolución)", 0.3, 2.0, 1.0, 0.1)

# Nombre del archivo ZIP
zip_name = st.text_input("📦 Nombre del archivo ZIP", value="PDFs_Comprimidos")

# Carga de archivos
uploaded_files = st.file_uploader("Selecciona uno o más archivos PDF", type=["pdf"], accept_multiple_files=True)

def compress_pdf(file, scale=1.0):
    original_size = len(file.getvalue()) / 1024  # KB

    input_doc = fitz.open(stream=file.read(), filetype="pdf")
    output_buffer = io.BytesIO()
    output_doc = fitz.open()

    for page_num in range(len(input_doc)):
        page = input_doc.load_page(page_num)
        matrix = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        img_pdf = fitz.open()
        rect = fitz.Rect(0, 0, pix.width, pix.height)
        page_img = img_pdf.new_page(width=pix.width, height=pix.height)
        page_img.insert_image(rect, pixmap=pix)
        output_doc.insert_pdf(img_pdf)

    output_doc.save(output_buffer)
    output_doc.close()
    compressed_size = len(output_buffer.getvalue()) / 1024  # KB
    output_buffer.seek(0)

    return output_buffer, original_size, compressed_size

if uploaded_files:
    with st.spinner("📉 Comprimiendo PDFs..."):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for i, file in enumerate(uploaded_files):
                st.write(f"🔄 Procesando: **{file.name}**")
                progress = st.progress(i / len(uploaded_files))

                compressed_pdf, original_kb, compressed_kb = compress_pdf(file, scale=compression_level)
                filename = file.name.replace(".pdf", "_comprimido.pdf")

                zipf.writestr(filename, compressed_pdf.read())
                st.write(f"📄 `{file.name}`: {original_kb:.1f} KB → {compressed_kb:.1f} KB")

        zip_buffer.seek(0)
        st.success("✅ Todos los archivos fueron comprimidos y empaquetados.")

        st.download_button(
            label="📥 Descargar ZIP",
            data=zip_buffer,
            file_name=f"{zip_name}.zip",
            mime="application/zip"
        )
