from docxtpl import DocxTemplate, InlineImage
import datetime
import json
import os


def report_generation(company_name="Insert Company name here"):
    """
    Creates a network topologi report.
    company_name: str = "Insert company name here"
    scan_options: list = ["thing","thing2"]
    """
    with open(f"final/scan-results/{company_name}_local_scan.json") as f:
        local_data = json.load(f)
    try:
        with open(f"final/scan-results/{company_name}_cloud_scan.json") as f:
            cloud_data = json.load(f)
    except:
        cloud_data = ""

    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    doc = DocxTemplate(f"final/docxtemplate/rapport_template.docx")
    local_image = InlineImage(doc, f"final/network_diagrams/{company_name}_local_diagram.png")

    cloud_exist = os.path.exists(f"final/network_diagrams/{company_name}_cloud_diagram.png")
    if cloud_exist is True:
        cloud_image = InlineImage(doc, f"final/network_diagrams/{company_name}_cloud_diagram.png")
    else:
        cloud_image = ""
    context = {
        'company_name': company_name,
        "date": current_date,
        "image1": local_image,
        "image2": cloud_image,
        "local_devices": local_data,
        "cloud_devices": cloud_data,
        }
    doc.render(context)
    doc.save(f"final/generated_report/{company_name}_network_scan.docx")
