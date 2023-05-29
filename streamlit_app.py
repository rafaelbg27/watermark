import os
import PyPDF2
import streamlit as st
from reportlab.pdfgen import canvas


def create_watermark(text, pdf, file_name):
    # Create a PDF canvas with the same size as the original PDF
    page = pdf.pages[0]
    width, height = page.mediabox.width, page.mediabox.height
    c = canvas.Canvas("temp/watermark.pdf", pagesize=(width, height))
    c.translate(float(width) / 2, float(height) / 2.5)
    c.rotate(30)
    c.setFillColorRGB(0.5, 0.5, 0.5, 0.5)
    c.setFont("Helvetica", 100)
    c.drawCentredString(0, 0, text)
    c.save()

    # Merge the watermark with the original PDF
    watermark = PyPDF2.PdfReader(open("temp/watermark.pdf", "rb"))
    output = PyPDF2.PdfWriter()
    for i in range(len(pdf.pages)):
        page = pdf.pages[i]
        page.merge_page(watermark.pages[0])
        output.add_page(page)

    # Save the watermarked PDF
    with open(f"temp/{file_name[:-4]}_{text}.pdf", "wb") as f:
        output.write(f)


def main():
    st.title("PDF Watermarker")

    # Upload PDF file
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        # Create temp directory if it doesn't exist
        if not os.path.exists("temp"):
            os.makedirs("temp")

        # Save uploaded file to a temporary directory
        with open(f"temp/{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Load PDF file
        pdf = PyPDF2.PdfReader(open(f"temp/{uploaded_file.name}", "rb"))

        file_details = {
            "FileName": uploaded_file.name,
            "FileType": uploaded_file.type
        }
        st.write(file_details)

        # Input list of strings
        texts = st.text_input("Enter a list of strings separated by commas")
        texts = [text.strip() for text in texts.split(",")]

        # Watermark PDF with each string
        for text in texts:
            create_watermark(text, pdf, uploaded_file.name)

        if len(texts) > 1 or texts[0] != "":
            for text in texts:
                st.download_button(
                    label=
                    f"Download watermarked file {uploaded_file.name[:-4]}_{text}.pdf",
                    data=open(f"temp/{uploaded_file.name[:-4]}_{text}.pdf",
                              "rb").read(),
                    file_name=f"temp/{uploaded_file.name[:-4]}_{text}.pdf",
                )


if __name__ == "__main__":
    main()