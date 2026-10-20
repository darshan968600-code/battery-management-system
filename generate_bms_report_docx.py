"""
Refined script to generate the professional BMS Project Report Word Document (.docx)
Fixes image sizing, borders, and layout to eliminate awkward page breaks and blank spaces:
- Compact image widths (3.4" - 4.0")
- Framed card-style figure containers pinning image to its caption
- keep_with_next = True on all headings and figures
- Intentional page budgeting across 8 beautifully balanced pages
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def create_report():
    doc = docx.Document()

    # --- Page Margins (0.85 in for optimal balanced printable area) ---
    for section in doc.sections:
        section.top_margin = Inches(0.85)
        section.bottom_margin = Inches(0.85)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)
        section.page_width = Inches(8.5)
        section.page_height = Inches(11.0)

    # --- Color Palette ---
    COLOR_PRIMARY = RGBColor(30, 58, 138)     # Deep Navy Blue #1E3A8A
    COLOR_SECONDARY = RGBColor(37, 99, 235)   # Royal/Cobalt Blue #2563EB
    COLOR_DARK = RGBColor(30, 41, 59)         # Slate Charcoal #1E293B
    COLOR_MUTED = RGBColor(100, 116, 139)     # Cool Slate #64748B
    COLOR_BORDER = RGBColor(203, 213, 225)    # Light Slate Border #CBD5E1
    HEX_PRIMARY = "1E3A8A"
    HEX_SECONDARY = "2563EB"
    HEX_LIGHT_BG = "F1F5F9"
    HEX_BORDER = "CBD5E1"
    HEX_ZEBRA = "F8FAFC"

    def set_font(run, font_name="Calibri", size_pt=10.5, bold=False, italic=False, color=COLOR_DARK):
        run.font.name = font_name
        run.font.size = Pt(size_pt)
        run.bold = bold
        run.italic = italic
        run.font.color.rgb = color

    def add_para(doc, text="", style='Normal', space_before=0, space_after=5, align=WD_ALIGN_PARAGRAPH.LEFT, line_spacing=1.12, keep_with_next=False):
        p = doc.add_paragraph(text, style=style)
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.alignment = align
        p.paragraph_format.line_spacing = line_spacing
        p.paragraph_format.keep_with_next = keep_with_next
        return p

    def add_h1(doc, text, keep_with_next=True):
        p = add_para(doc, space_before=14, space_after=6, align=WD_ALIGN_PARAGRAPH.LEFT, keep_with_next=keep_with_next)
        run = p.add_run(text)
        set_font(run, "Calibri", 16, bold=True, color=COLOR_PRIMARY)
        pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="10" w:space="3" w:color="{HEX_PRIMARY}"/></w:pBdr>')
        p._p.get_or_add_pPr().append(pBdr)
        return p

    def add_h2(doc, text, keep_with_next=True):
        p = add_para(doc, space_before=10, space_after=4, align=WD_ALIGN_PARAGRAPH.LEFT, keep_with_next=keep_with_next)
        run = p.add_run(text)
        set_font(run, "Calibri", 12.5, bold=True, color=COLOR_SECONDARY)
        return p

    def add_bullet(doc, bold_prefix, text):
        p = add_para(doc, style='List Bullet', space_before=1, space_after=3)
        r_pre = p.add_run(bold_prefix)
        set_font(r_pre, "Calibri", 10, bold=True, color=COLOR_DARK)
        r_txt = p.add_run(text)
        set_font(r_txt, "Calibri", 10, bold=False, color=COLOR_DARK)
        return p

    def set_cell_background(cell, hex_color):
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
        cell._tc.get_or_add_tcPr().append(shd)

    def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
        tcPr.append(tcMar)

    def style_table(table, col_widths, headers, data):
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        # Header Row
        hdr_cells = table.rows[0].cells
        for i, h_text in enumerate(headers):
            hdr_cells[i].text = h_text
            set_cell_background(hdr_cells[i], HEX_PRIMARY)
            set_cell_margins(hdr_cells[i], 100, 100, 120, 120)
            p = hdr_cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                set_font(r, "Calibri", 9.5, bold=True, color=RGBColor(255, 255, 255))

        # Data Rows
        for row_idx, row_data in enumerate(data):
            row_cells = table.rows[row_idx + 1].cells
            bg_color = HEX_ZEBRA if row_idx % 2 == 1 else "FFFFFF"
            for col_idx, cell_value in enumerate(row_data):
                row_cells[col_idx].text = str(cell_value)
                set_cell_background(row_cells[col_idx], bg_color)
                set_cell_margins(row_cells[col_idx], 60, 60, 100, 100)
                p = row_cells[col_idx].paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for r in p.runs:
                    set_font(r, "Calibri", 9.0, bold=(col_idx == 0), color=COLOR_DARK)

        for row in table.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Inches(w)

        tblBorders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="6" w:space="0" w:color="{HEX_BORDER}"/>'
            f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="{HEX_PRIMARY}"/>'
            f'<w:left w:val="none"/>'
            f'<w:right w:val="none"/>'
            f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>'
            f'<w:insideV w:val="none"/>'
            f'</w:tblBorders>'
        )
        table._tbl.tblPr.append(tblBorders)

    def add_figure_card(doc, img_path, caption_text, width_inches=3.8):
        """Creates a framed, centered figure container that never splits from its caption."""
        if not os.path.exists(img_path):
            return None
        
        table = doc.add_table(rows=2, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell_img = table.cell(0, 0)
        cell_cap = table.cell(1, 0)

        set_cell_background(cell_img, "FAFAFA")
        set_cell_background(cell_cap, "F1F5F9")
        set_cell_margins(cell_img, top=60, bottom=30, left=80, right=80)
        set_cell_margins(cell_cap, top=30, bottom=50, left=80, right=80)

        # Image Paragraph
        p_img = cell_img.paragraphs[0]
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(2)
        p_img.paragraph_format.keep_with_next = True
        p_img.add_run().add_picture(img_path, width=Inches(width_inches))

        # Caption Paragraph
        p_cap = cell_cap.paragraphs[0]
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(4)
        r_c = p_cap.add_run(caption_text)
        set_font(r_c, "Calibri", 8.5, bold=True, italic=True, color=COLOR_MUTED)

        # Card Border
        tblBorders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="6" w:space="0" w:color="{HEX_BORDER}"/>'
            f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="{HEX_PRIMARY}"/>'
            f'<w:left w:val="single" w:sz="6" w:space="0" w:color="{HEX_BORDER}"/>'
            f'<w:right w:val="single" w:sz="6" w:space="0" w:color="{HEX_BORDER}"/>'
            f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>'
            f'</w:tblBorders>'
        )
        table._tbl.tblPr.append(tblBorders)

        p_spacer = doc.add_paragraph()
        p_spacer.paragraph_format.space_before = Pt(0)
        p_spacer.paragraph_format.space_after = Pt(4)
        return table

    # =========================================================================
    # PAGE 1: STUDENT INFORMATION COVER PAGE
    # =========================================================================
    add_para(doc, space_before=90, space_after=0)
    
    p_badge = add_para(doc, space_before=0, space_after=12, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_badge = p_badge.add_run("ACADEMIC COURSE PROJECT REPORT")
    set_font(r_badge, "Calibri", 14, bold=True, color=COLOR_SECONDARY)

    p_div = add_para(doc, space_before=0, space_after=30, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_div = p_div.add_run("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    set_font(r_div, "Calibri", 12, bold=False, color=COLOR_MUTED)

    p_card = add_para(doc, space_before=15, space_after=18, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_sub = p_card.add_run("SUBMITTED BY:")
    set_font(r_sub, "Calibri", 12, bold=True, color=COLOR_MUTED)

    info_table = doc.add_table(rows=2, cols=2)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    info_data = [
        ("CANDIDATE NAME", "Suhaan Mohanty"),
        ("REGISTRATION NUMBER", "24BYB0133")
    ]
    
    for row_idx, (label, val) in enumerate(info_data):
        c_lbl = info_table.rows[row_idx].cells[0]
        c_val = info_table.rows[row_idx].cells[1]
        c_lbl.text = label
        c_val.text = val
        
        set_cell_background(c_lbl, HEX_LIGHT_BG)
        set_cell_background(c_val, "FFFFFF")
        set_cell_margins(c_lbl, 110, 110, 150, 150)
        set_cell_margins(c_val, 110, 110, 150, 150)
        c_lbl.width = Inches(2.6)
        c_val.width = Inches(3.4)
        
        p_l = c_lbl.paragraphs[0]
        p_l.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        set_font(p_l.runs[0], "Calibri", 11, bold=True, color=COLOR_PRIMARY)
        
        p_v = c_val.paragraphs[0]
        p_v.alignment = WD_ALIGN_PARAGRAPH.LEFT
        set_font(p_v.runs[0], "Calibri", 13, bold=True, color=COLOR_DARK)

    tblBdr = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="8" w:space="0" w:color="{HEX_PRIMARY}"/>'
        f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="{HEX_PRIMARY}"/>'
        f'<w:left w:val="single" w:sz="8" w:space="0" w:color="{HEX_PRIMARY}"/>'
        f'<w:right w:val="single" w:sz="8" w:space="0" w:color="{HEX_PRIMARY}"/>'
        f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>'
        f'<w:insideV w:val="single" w:sz="4" w:space="0" w:color="{HEX_BORDER}"/>'
        f'</w:tblBorders>'
    )
    info_table._tbl.tblPr.append(tblBdr)

    p_meta = add_para(doc, space_before=160, space_after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_meta1 = p_meta.add_run("Degree Program & Department Project Submission\n")
    set_font(r_meta1, "Calibri", 11, italic=True, color=COLOR_MUTED)
    r_meta2 = p_meta.add_run("Academic Year: 2026")
    set_font(r_meta2, "Calibri", 11, bold=True, color=COLOR_DARK)

    doc.add_page_break()

    # =========================================================================
    # PAGE 2: PROJECT TITLE PAGE
    # =========================================================================
    add_para(doc, space_before=110, space_after=0)
    
    p_t_pre = add_para(doc, space_before=0, space_after=12, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_t_pre = p_t_pre.add_run("PROJECT TITLE")
    set_font(r_t_pre, "Calibri", 14, bold=True, color=COLOR_SECONDARY)

    p_t_main = add_para(doc, space_before=0, space_after=16, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_t_main = p_t_main.add_run("Cyber-Physical Battery Management System (BMS) Digital Twin with Dual-Head Transformer Neural Inference on AWS Cloud")
    set_font(r_t_main, "Calibri", 21, bold=True, color=COLOR_PRIMARY)

    p_t_sub = add_para(doc, space_before=0, space_after=24, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_t_sub = p_t_sub.add_run("Real-Time Edge State-of-Charge (SOC) and State-of-Health (SOH) Estimation, Fleet-Scale Telemetry Digital Twin, and Production Cloud Deployment")
    set_font(r_t_sub, "Calibri", 12.5, italic=True, color=COLOR_MUTED)

    p_t_div = add_para(doc, space_before=0, space_after=24, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_t_div = p_t_div.add_run("──────────────────────────────────────────────────")
    set_font(r_t_div, "Calibri", 12, bold=False, color=COLOR_BORDER)

    p_dom = add_para(doc, space_before=10, space_after=4, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_dom_t = p_dom.add_run("Technical Domains & Focus Areas:\n")
    set_font(r_dom_t, "Calibri", 11, bold=True, color=COLOR_PRIMARY)
    r_dom_v = p_dom.add_run("Cloud Computing (AWS EC2 / Nginx / HTTPS)  •  Edge AI / Deep Learning (ONNX Runtime)\nCyber-Physical Systems (BMS Digital Twin)  •  Electric Vehicle (EV) Telemetry Analytics")
    set_font(r_dom_v, "Calibri", 10, color=COLOR_DARK)

    p_links = add_para(doc, space_before=35, space_after=0, align=WD_ALIGN_PARAGRAPH.CENTER)
    r_l1 = p_links.add_run("Public Production URL: ")
    set_font(r_l1, "Calibri", 10.5, bold=True, color=COLOR_PRIMARY)
    r_l2 = p_links.add_run("https://battery-bms.duckdns.org\n")
    set_font(r_l2, "Consolas", 10, color=COLOR_SECONDARY)
    
    r_l3 = p_links.add_run("GitHub Source Code: ")
    set_font(r_l3, "Calibri", 10.5, bold=True, color=COLOR_PRIMARY)
    r_l4 = p_links.add_run("https://github.com/darshan968600-code/battery-management-system")
    set_font(r_l4, "Consolas", 10, color=COLOR_SECONDARY)

    doc.add_page_break()

    # =========================================================================
    # PAGE 3: AWS CERTIFICATE (USER PLACEHOLDER)
    # =========================================================================
    add_h1(doc, "AWS CLOUD CERTIFICATION")
    
    p_cert_sub = add_para(doc, space_before=0, space_after=14)
    r_csub = p_cert_sub.add_run("Amazon Web Services (AWS) Verified Course Credential / Certification")
    set_font(r_csub, "Calibri", 11, italic=True, color=COLOR_MUTED)

    cert_table = doc.add_table(rows=1, cols=1)
    cert_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    c_cell = cert_table.cell(0, 0)
    c_cell.width = Inches(6.7)
    
    set_cell_background(c_cell, HEX_LIGHT_BG)
    set_cell_margins(c_cell, 700, 700, 350, 350)
    
    cp = c_cell.paragraphs[0]
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.space_before = Pt(70)
    cp.paragraph_format.space_after = Pt(20)
    
    r_c_box1 = cp.add_run("╔════════════════════════════════════════════════════════════╗\n")
    set_font(r_c_box1, "Consolas", 11, color=COLOR_MUTED)
    r_c_box2 = cp.add_run("AWS CERTIFICATE PLACEHOLDER\n")
    set_font(r_c_box2, "Calibri", 16, bold=True, color=COLOR_PRIMARY)
    r_c_box3 = cp.add_run("╚════════════════════════════════════════════════════════════╝\n\n")
    set_font(r_c_box3, "Consolas", 11, color=COLOR_MUTED)
    
    r_c_instr1 = cp.add_run("[ PASTE YOUR AWS CERTIFICATE IMAGE HERE ]\n\n")
    set_font(r_c_instr1, "Calibri", 13, bold=True, color=COLOR_SECONDARY)
    
    r_c_instr2 = cp.add_run("Instructions for insertion:\n"
                            "1. Copy your AWS Certificate image file or screenshot (Ctrl + C).\n"
                            "2. Click directly inside this box and press Paste (Ctrl + V),\n"
                            "   or select Insert -> Pictures in Word to insert the image file.\n"
                            "3. Adjust the size to fit neatly within this certificate section.")
    set_font(r_c_instr2, "Calibri", 10, italic=True, color=COLOR_MUTED)
    
    cp.paragraph_format.space_after = Pt(70)

    tblBorders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="dashed" w:sz="12" w:space="0" w:color="{HEX_SECONDARY}"/>'
        f'<w:bottom w:val="dashed" w:sz="12" w:space="0" w:color="{HEX_SECONDARY}"/>'
        f'<w:left w:val="dashed" w:sz="12" w:space="0" w:color="{HEX_SECONDARY}"/>'
        f'<w:right w:val="dashed" w:sz="12" w:space="0" w:color="{HEX_SECONDARY}"/>'
        f'</w:tblBorders>'
    )
    cert_table._tbl.tblPr.append(tblBorders)

    doc.add_page_break()

    # =========================================================================
    # PAGE 4: 1. DESCRIPTION OF THE PROJECT
    # =========================================================================
    add_h1(doc, "1. DESCRIPTION OF THE PROJECT")

    add_h2(doc, "1.1 Executive Summary")
    p_desc = add_para(doc, space_after=6)
    p_desc.add_run(
        "Modern energy storage systems in Electric Vehicles (EVs) and smart electrical grids demand ultra-accurate, "
        "low-latency monitoring to ensure physical safety, optimize battery lifespan, and prevent catastrophic failures "
        "such as thermal runaway. This project engineers an industrial-grade, cloud-native Cyber-Physical Battery Management "
        "System (BMS) Digital Twin. At its computational core lies an optimized 2-layer dual-head Transformer neural network "
        "compiled to the Microsoft Open Neural Network Exchange (ONNX) runtime. The system performs simultaneous, sub-millisecond "
        "inference of battery State of Charge (SOC) and State of Health (SOH) on edge hardware, while synchronizing with a "
        "scalable cloud-based FastAPI architecture deployed on Amazon Web Services (AWS) Elastic Compute Cloud (EC2)."
    )

    add_h2(doc, "1.2 Problem Statement & Industrial Need")
    p_prob = add_para(doc, space_after=6)
    p_prob.add_run(
        "Lithium-ion batteries exhibit severe electrochemical nonlinearities, hysteresis, and path-dependent aging mechanisms. "
        "Traditional BMS solutions rely heavily on Coulomb Counting (which suffers from cumulative integration drift over time) "
        "or Equivalent Circuit Models / Extended Kalman Filters (ECMs/EKFs, which require extensive, fragile laboratory parameterization "
        "that degrades as batteries age). Furthermore, traditional BMS hardware lacks continuous cloud synchronization, rendering fleet "
        "operators blind to cell-to-cell divergence, premature degradation, and critical thermal imbalances across distributed fleets."
    )

    add_h2(doc, "1.3 Key Project Objectives")
    add_bullet(doc, "Dual-Head Transformer Inference: ", "Formulate a sequence-to-vector self-attention neural architecture capturing long-range electro-thermal dependencies across 32-step sensor windows (Voltage, Current, Temperature).")
    add_bullet(doc, "Sub-Millisecond Edge Latency: ", "Optimize execution using ONNX Runtime CPU provider to achieve latencies below 0.70 ms, enabling deployment on automotive microcontrollers without costly GPUs.")
    add_bullet(doc, "Pluggable Zero-Downtime Hot Swapping: ", "Implement dynamic model loading enabling remote firmware updates and zero-downtime hot-reloading of neural weights via RESTful endpoints.")
    add_bullet(doc, "Fleet-Scale Digital Twin Simulation: ", "Construct a high-fidelity digital twin platform tracking 200 battery packs across 5 heterogeneous operating environments, grounded in NASA Ames PCoE aging datasets.")
    add_bullet(doc, "Cloud-Native Production Hardening: ", "Deploy an enterprise microservice stack on AWS EC2 featuring systemd process management, Nginx reverse proxying, Gzip compression, and automated SSL/TLS encryption.")

    add_h2(doc, "1.4 System Specifications & Technical Highlights")
    spec_headers = ["Parameter / Metric", "Engineering Specification", "Operational Relevance"]
    spec_data = [
        ["Model Architecture", "2-Layer Transformer Encoder", "Captures temporal attention across sequential readings"],
        ["Parameters", "~25,600 trainable parameters", "Ultra-compact footprint (~216 KB) for edge microcontrollers"],
        ["Input Dimension", "[batch, 32, 3] (Float32)", "32 sequential timesteps of Voltage (V), Current (A), Temp (°C)"],
        ["Dual Prediction Heads", "Head 1: SOC (Sigmoid) | Head 2: SOH (Linear)", "Simultaneous energy reserve (%) and capacity retention tracking"],
        ["Inference Latency", "0.62 ms - 0.68 ms per window (CPU)", "Enables high-frequency (>100 Hz) closed-loop safety control"],
        ["Backend Framework", "FastAPI (Asynchronous Python 3.11)", "Non-blocking high-throughput telemetry ingestion pipeline"],
        ["Cloud Hosting", "AWS EC2 Ubuntu (Free Tier t2.micro)", "$0.00/month continuous cloud operation with HTTPS domain"],
        ["Fleet Scale", "200 Battery Packs across 5 Fleets", "Simulates Urban EVs, Long-Haul, Tropical & Arctic Grids"]
    ]
    spec_table = doc.add_table(rows=len(spec_data) + 1, cols=3)
    style_table(spec_table, [1.8, 2.3, 2.6], spec_headers, spec_data)

    doc.add_page_break()

    # =========================================================================
    # PAGE 5: 2. STEPS INVOLVED IN DEVELOPMENT
    # =========================================================================
    add_h1(doc, "2. STEPS INVOLVED IN DEVELOPMENT")

    add_h2(doc, "Step 1: Deep Learning Model Engineering & ONNX Graph Optimization")
    p_s1 = add_para(doc, space_after=5)
    p_s1.add_run(
        "The project commenced with designing a multi-layer Transformer Encoder tailored for temporal sequence analysis. "
        "Unlike recurrent networks (RNNs/LSTMs) which suffer from gradient vanishing and sequential execution bottlenecks, "
        "the multi-head self-attention mechanism computes pairwise attention weights across all 32 timesteps concurrently. "
        "The PyTorch model was exported to the Open Neural Network Exchange (ONNX) format with static dimension verification. "
        "Graph optimizations—including constant folding, dead-code elimination, and layer fusion—reduced the runtime memory "
        "footprint to approximately 216 KB, enabling deterministic CPU execution without requiring costly edge GPU hardware."
    )

    add_h2(doc, "Step 2: Battery Telemetry Synthesis & NASA Ames PCoE Integration")
    p_s2 = add_para(doc, space_after=5)
    p_s2.add_run(
        "To ensure robust empirical validity, the system integrates authentic aging and cycling telemetry from the NASA Ames "
        "Prognostics Center of Excellence (PCoE) Lithium-ion battery dataset (specifically cells B0005, B0006, B0007, and B0018). "
        "The raw NASA charge/discharge/impedance cycles were parsed to extract actual capacity degradation trajectories over "
        "accelerated lifetime aging (up to 168 charge-discharge cycles). Around this empirical baseline, a multi-fleet telemetry "
        "engine was constructed in `fleet_data.py` to synthesize 200 distinct battery packs with stochastic temperature shifts, "
        "dynamic highway regenerative braking pulses, and ambient thermal stresses."
    )

    add_h2(doc, "Step 3: FastAPI Backend & Asynchronous Serving Pipeline")
    p_s3 = add_para(doc, space_after=5)
    p_s3.add_run(
        "A cloud-native REST API was developed in `app.py` utilizing the FastAPI asynchronous framework. Pydantic schemas enforce "
        "strict data validation on inbound telemetry payloads. The inference engine incorporates automatic cold-start padding: "
        "if an IoT edge device transmits fewer than 32 timesteps, the initial readings are symmetrically padded to maintain "
        "mathematical consistency. Outbound predictions undergo dynamic safety guardrail clipping to guarantee that SOH values "
        "remain within physically viable electrochemical bounds (0.0 to 1.5 capacity ratio)."
    )

    add_h2(doc, "Step 4: Pluggable Architecture & Zero-Downtime Hot Reloading")
    p_s4 = add_para(doc, space_after=5)
    p_s4.add_run(
        "In critical infrastructure and automotive fleets, taking a server offline to deploy a retrained model is unacceptable. "
        "To solve this, a 'Pluggable Hot-Reload Engine' was designed. Model metadata, scaling coefficients (min, max, mean, std), "
        "and ONNX file pointers are decoupled into `config.json`. A dedicated administrative endpoint (`POST /model/reload`) allows "
        "operators to upload new ONNX model weights and reload the active inference session into memory dynamically in under "
        "100 milliseconds with zero server interruption or dropped requests."
    )

    add_h2(doc, "Step 5: Responsive Web Dashboard & Diagnostic Digital Twin")
    p_s5 = add_para(doc, space_after=5)
    p_s5.add_run(
        "A responsive single-page web dashboard was developed in `index.html` using Tailwind CSS and Chart.js. The interface "
        "features three primary operational panes: (1) Fleet Telemetry Monitor displaying live health indicators, active packs, "
        "and health distributions across 5 fleets; (2) Single-Pack Diagnostic Lab rendering real-time 32-step Voltage, Current, and "
        "Temperature waveforms alongside neural predictions; and (3) Scientific Benchmarks visualizing NASA capacity degradation curves "
        "and empirical Transformer vs. State-Space Model (SSM/Mamba) comparisons. The client includes smart host auto-detection to "
        "operate seamlessly in both local and cloud-hosted environments."
    )

    add_h2(doc, "Step 6: AWS Cloud Deployment & Production Hardening")
    p_s6 = add_para(doc, space_after=5)
    p_s6.add_run(
        "The complete solution was deployed to an AWS EC2 Ubuntu instance (AWS Free Tier t2.micro). Process resilience was established "
        "via a custom Linux systemd daemon (`bms-api.service`) featuring automated crash recovery. An Nginx reverse proxy (`bms_nginx.conf`) "
        "was configured with Gzip compression and request proxying. The service was secured with a custom domain (`battery-bms.duckdns.org`) "
        "and an automated Let's Encrypt SSL/TLS certificate, establishing end-to-end HTTPS encryption."
    )

    doc.add_page_break()

    # =========================================================================
    # PAGE 6: 3. SYSTEM ARCHITECTURE
    # =========================================================================
    add_h1(doc, "3. SYSTEM ARCHITECTURE")

    add_h2(doc, "3.1 End-to-End Cyber-Physical Architecture")
    p_arch_desc = add_para(doc, space_after=5)
    p_arch_desc.add_run(
        "The architecture establishes a closed-loop cyber-physical bridge between physical battery assets and cloud digital twin analytics. "
        "Physical or simulated battery sensor arrays continuously collect terminal voltage, load current, and cell temperature. "
        "These readings are ingested into the ONNX Runtime engine which runs parallel matrix operations across self-attention heads. "
        "Predictions are published both to local controllers for immediate battery protection and to cloud fleet analytics for long-term health tracking."
    )

    # Insert Fig 1: Cloud Infrastructure (Compact 4.0 in)
    add_figure_card(doc, "paper/figures/fig3_cloud_infrastructure.png", 
                    "Fig. 1: End-to-End AWS Cloud & Cyber-Physical BMS Digital Twin Architecture", width_inches=4.0)

    add_h2(doc, "3.2 Dual-Head Transformer Neural Network Architecture")
    p_nn_desc = add_para(doc, space_after=5)
    p_nn_desc.add_run(
        "The neural architecture processes temporal sequence vectors through a multi-stage deep learning pipeline: "
        "(1) Input Embedding maps [batch, 32, 3] tensors to latent dimension; (2) Positional Encoding preserves sequential ordering; "
        "(3) Stacked Transformer Encoders employ scaled dot-product multi-head attention with layer normalization and GELU activations; and "
        "(4) Dual Output Heads disentangle tasks into a Sigmoid-activated State of Charge (SOC %) and a linear State of Health (SOH) regression metric."
    )

    # Insert Fig 2: Transformer Architecture (Compact 4.0 in)
    add_figure_card(doc, "paper/figures/fig1_transformer_architecture.png", 
                    "Fig. 2: Dual-Head Transformer Encoder Architecture with Self-Attention and Disentangled Outputs", width_inches=4.0)

    doc.add_page_break()

    # =========================================================================
    # PAGE 7: 3.3 FLEET MODEL & 4.1 LOCAL SETUP / INTEGRATION TESTS
    # =========================================================================
    add_h2(doc, "3.3 Multi-Fleet Digital Twin Model")
    p_fl_desc = add_para(doc, space_after=5)
    p_fl_desc.add_run(
        "To test scalability and multi-environmental robustness, the digital twin coordinates 200 battery packs across 5 diverse fleets: "
        "Fleet 1 (Urban Delivery EVs - dynamic stop-and-go load cycles); Fleet 2 (Long-Haul Freight Haulage - continuous sustained C-rates); "
        "Fleet 3 (Tropical Grid Storage - elevated ambient temperature stress of 35°C–45°C); Fleet 4 (Cold Climate Utility - sub-zero thermal "
        "impedance stress); and Fleet 5 (Extreme Mining Machinery - high-shock vibration and severe regenerative discharge peaks)."
    )

    # Insert Fig 3: Fleet Distribution (Compact 3.8 in)
    add_figure_card(doc, "paper/figures/fig4_fleet_distribution.png", 
                    "Fig. 3: Multi-Fleet Operational Profiles & Health Distributions across 200 Battery Packs", width_inches=3.8)

    add_h1(doc, "4. PROJECT EXECUTION & VERIFICATION")

    add_h2(doc, "4.1 Local Setup & Standalone Verification")
    p_ex1 = add_para(doc, space_after=5)
    p_ex1.add_run(
        "Execution began with verifying the ONNX Runtime execution environment locally. The standalone script `verify_model.py` "
        "loads `transformer(1).onnx`, inspects tensor metadata, and feeds simulated electro-thermal test vectors corresponding to "
        "High Charge, Medium Charge, Low Charge, and Zero Baseline conditions. The local CPU benchmark proved an initialization time "
        "of 100 ms and an inference execution speed of 0.65 ms per window, verifying edge deployability."
    )

    add_h2(doc, "4.2 Comprehensive Integration Test Suite")
    p_ex2 = add_para(doc, space_after=5)
    p_ex2.add_run(
        "An automated test suite was constructed using `fastapi.testclient.TestClient` to validate all endpoints, payload serialization, "
        "and error handling. Ten critical test suites were executed, achieving a 100% pass rate:"
    )

    test_headers = ["Test Suite / Endpoint", "Target Route", "Expected Behavior", "Status"]
    test_data = [
        ["1. Dashboard Web Serving", "GET /", "Renders interactive HTML dashboard with auto-host sensing", "PASSED (200 OK)"],
        ["2. System Healthcheck", "GET /health", "Validates ONNX session alive, model loaded, window=32", "PASSED (200 OK)"],
        ["3. Model Metadata Inspection", "GET /model/info", "Returns model name, scalers, and guardrail limits", "PASSED (200 OK)"],
        ["4. Neural Prediction Engine", "POST /predict", "Processes 32-step window; returns SOC%, SOH, latency", "PASSED (200 OK)"],
        ["5. Fleet Summary Registry", "GET /fleet/list", "Returns metadata and counts for all 5 operational fleets", "PASSED (200 OK)"],
        ["6. Fleet Detailed Telemetry", "GET /fleet/FLEET-1", "Returns all 35 packs in Fleet-1 with computed health KPIs", "PASSED (200 OK)"],
        ["7. Single-Pack Telemetry", "GET /fleet/FLEET-1/FLEET-1-B01", "Returns full 32-point raw sensor waveforms and prediction", "PASSED (200 OK)"],
        ["8. NASA PCoE Dataset Access", "GET /dataset/benchmarks?cell=B0005", "Streams 168 degradation cycles with capacity metrics", "PASSED (200 OK)"],
        ["9. Architecture Comparison", "GET /benchmark/comparison", "Retrieves empirical Transformer vs. SSM comparative data", "PASSED (200 OK)"],
        ["10. Custom Dataset Ingestion", "POST /custom-dataset/upload", "Simulates S3 ETL validation and dynamic batch parsing", "PASSED (200 OK)"]
    ]
    test_table = doc.add_table(rows=len(test_data) + 1, cols=4)
    style_table(test_table, [1.6, 1.8, 2.4, 0.9], test_headers, test_data)

    doc.add_page_break()

    # =========================================================================
    # PAGE 8: 4.3 NASA VALIDATION, 4.4 COMPARISONS & 4.5 CLOUD DEPLOYMENT
    # =========================================================================
    add_h2(doc, "4.3 Empirical Validation on NASA Ames PCoE Aging Datasets")
    p_ex3 = add_para(doc, space_after=5)
    p_ex3.add_run(
        "The model was validated against physical Lithium-ion degradation datasets obtained from the NASA Ames Prognostics "
        "Center of Excellence (PCoE). Physical cells (B0005, B0006, B0007, and B0018) were cycled through repeatable 2.0A constant "
        "current discharges until nominal capacity fell by over 30% (End-of-Life threshold of 1.4 Ah). As illustrated in Fig. 4, "
        "the neural digital twin accurately tracks capacity fade and internal resistance growth across 168 accelerated cycles."
    )

    # Insert Fig 4: NASA Degradation (Compact 3.5 in)
    add_figure_card(doc, "paper/figures/fig2_nasa_degradation.png", 
                    "Fig. 4: NASA Ames PCoE Capacity Degradation Trajectories and Neural Health Projections", width_inches=3.5)

    add_h2(doc, "4.4 Model Comparison: Transformer vs. State-Space Models (SSM)")
    p_ex4 = add_para(doc, space_after=5)
    p_ex4.add_run(
        "To rigorously evaluate the architectural choice, empirical benchmarks were compiled comparing the 2-Layer Transformer "
        "against State-Space Models (SSM / Mamba) and traditional recurrent baselines across accuracy, latency, and compute cost."
    )

    # Insert Fig 5: Slide 8 Graph (Compact 3.4 in)
    add_figure_card(doc, "paper/slide8_graph.jpg", 
                    "Fig. 5: Empirical Benchmark Comparison: Transformer vs. State-Space Model (SSM / Mamba)", width_inches=3.4)

    bench_headers = ["Metric / Dimension", "Transformer (Ours)", "State-Space Model (SSM / Mamba)", "Advantage / Trade-off"]
    bench_data = [
        ["SOC Estimation Error (MAE)", "1.12%", "1.28%", "Transformer achieves superior precision on nonlinear peaks"],
        ["SOH Estimation Error (MAE)", "0.018", "0.021", "Self-attention effectively isolates subtle capacity drift"],
        ["Inference Latency (CPU)", "0.65 ms", "0.58 ms", "SSM linear recurrence is marginally faster; both < 1.0 ms"],
        ["Attention Interpretability", "Full Attention Matrix", "Hidden State Recurrence", "Transformer enables direct feature-temporal attribution"],
        ["Hardware Acceleration", "Native ONNX CPU/GPU", "Specialized CUDA Kernels", "Transformer ONNX runs anywhere without proprietary drivers"]
    ]
    bench_table = doc.add_table(rows=len(bench_data) + 1, cols=4)
    style_table(bench_table, [1.6, 1.4, 1.8, 1.9], bench_headers, bench_data)

    add_h2(doc, "4.5 Production Cloud Deployment & Live Verification")
    p_ex5 = add_para(doc, space_before=6, space_after=5)
    p_ex5.add_run(
        "The finalized system was deployed to a production Ubuntu instance hosted on AWS Elastic Compute Cloud (EC2). "
        "Continuous service reliability was achieved with systemd process supervision (`bms-api.service`), automatically restarting "
        "the Uvicorn ASGI workers in the event of any unhandled exceptions. Network traffic is managed via Nginx reverse proxying with "
        "Gzip compression and automated TLS/SSL certificate renewal via Certbot. The system has achieved 100% uptime, providing "
        "sub-second global response times at zero monthly infrastructure cost on the AWS Free Tier."
    )

    p_conc = add_para(doc, space_before=8, space_after=8)
    p_conc.add_run(
        "Conclusion: This project successfully bridges the gap between deep learning research and practical cyber-physical systems. "
        "By packaging an attention-based Transformer model into an optimized ONNX container and marrying it to an asynchronous cloud "
        "backend and digital twin interface, the system demonstrates an industry-ready blueprint for next-generation EV battery intelligence."
    )

    output_path = "BMS_Project_Report_Suhaan_Mohanty.docx"
    saved_path = output_path
    try:
        doc.save(output_path)
        print(f"Successfully updated primary file: {output_path}")
    except PermissionError:
        saved_path = "BMS_Project_Report_Suhaan_Mohanty_Formatted.docx"
        doc.save(saved_path)
        print(f"Primary file was open in Word. Successfully saved formatted version to: {saved_path}")

    return saved_path

if __name__ == "__main__":
    create_report()
