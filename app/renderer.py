from jinja2 import Environment, FileSystemLoader
from xhtml2pdf import pisa

def render_invoice(data, output_file):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("target_invoice.html")

    html_out = template.render(invoice=data)

    with open(output_file, "wb") as f:
        pisa_status = pisa.CreatePDF(html_out, dest=f)

    if pisa_status.err:
        print(f"Error creating PDF: {pisa_status.err}")
