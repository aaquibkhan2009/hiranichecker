import fitz  # PyMuPDF
import math
import streamlit as st

def extract_highlight_details(pdf_path):
    # Define the mapping of colors to their purpose
    color_map = {
        "Technical Highlight (Yellow)": (1, 1, 0),  # Hirani Group scope
        "Payment/Invoice (Green)": (0, 1, 0),  # Payment/Invoice requirements
        "Exclusion (Red)": (1, 0, 0),  # Exclusion
        "Client Deliverables (Blue)": (0, 0, 1),  # Client deliverables
        "Schedules (Brown)": (0.6, 0.4, 0.2),  # Schedules
    }

    def closest_color(color):
        """Find the closest known color using Euclidean distance."""
        min_distance = float("inf")
        closest_name = "Unknown Highlight"
        for name, rgb in color_map.items():
            distance = math.sqrt(sum((color[i] - rgb[i]) ** 2 for i in range(3)))
            if distance < min_distance:
                min_distance = distance
                closest_name = name
        return closest_name

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        st.error(f"Could not open PDF: {str(e)}")
        return []

    results = []

    for page_number in range(len(doc)):
        page = doc[page_number]
        for annot in page.annots() or []:
            try:
                if annot.type[0] in [8, 1, 21]:  # Include highlight and free text annotations
                    color = annot.colors.get("stroke") or annot.colors.get("fill")
                    if color:
                        # Normalize color and check transparency
                        normalized_color = tuple(round(c, 1) for c in color)
                        category = closest_color(normalized_color)  # Match with closest known color
                        rect = annot.rect  # Get annotation rectangle
                        highlighted_text = page.get_text("words", clip=rect)
                        results.append(f"{category} found on page {page_number + 1}: {highlighted_text}")
                    else:
                        results.append(f"Uncolored annotation found on page {page_number + 1}")
            except Exception as e:
                results.append(f"Error processing annotation on page {page_number + 1}: {str(e)}")

    return results

def main():
    st.title("PDF Highlight Extractor")

    # File uploader
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

    if uploaded_file is not None:
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.read())

        # Extract highlights
        st.info("Processing the PDF... This might take a moment.")
        results = extract_highlight_details("temp.pdf")

        if results:
            st.success("Highlights found:")
            for result in results:
                st.write(result)

            # Option to copy to clipboard
            if st.button("Copy to Clipboard"):
                st.experimental_set_query_params(highlights="\n".join(results))
                st.success("Highlights copied to clipboard! Use browser functionality to paste.")
        else:
            st.warning("No highlights detected in the selected PDF.")

if __name__ == "__main__":
    main()