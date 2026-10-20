import os
import sys
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def create_publication_paper(filename="BMS_Transformer_Conference_Paper.docx"):
    doc = Document()
    
    # Page setup - Standard Letter / A4 with clean 0.8" margins
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11.0)
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)
    
    # Configure Normal Style (Times New Roman, 10.5 pt, 1.15 line spacing)
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(10.5)
    font.color.rgb = RGBColor(30, 41, 59) # Professional dark slate
    
    # ------------------ HELPER FUNCTIONS ------------------
    def add_title(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(8)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(18)
        run.font.bold = True
        run.font.color.rgb = RGBColor(15, 23, 42) # Deep Navy / Slate
        return p

    def add_authors():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(16)
        
        # Author names
        r_names = p.add_run("Sudipto Nandi, Adinath, Darshan K, Piyush\n")
        r_names.font.name = 'Times New Roman'
        r_names.font.size = Pt(11)
        r_names.font.bold = True
        r_names.font.color.rgb = RGBColor(30, 41, 59)
        
        # Guide & Affiliation
        r_aff = p.add_run("Faculty Supervisor: Dr. Sangeetha N\nVIT Vellore, India")
        r_aff.font.name = 'Times New Roman'
        r_aff.font.size = Pt(9.5)
        r_aff.font.italic = True
        r_aff.font.color.rgb = RGBColor(71, 85, 105)
        return p

    def add_abstract_callout(abstract_text, keywords_text):
        # Create a stylized single-cell callout box with a soft blue/gray background and left blue border
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.9)
        
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(r'<w:shd {} w:fill="F8FAFC"/>'.format(nsdecls('w')))
        borders = parse_xml(r'<w:tcBorders {}><w:top w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/><w:bottom w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/><w:left w:val="single" w:sz="24" w:space="0" w:color="2563EB"/><w:right w:val="single" w:sz="6" w:space="0" w:color="CBD5E1"/></w:tcBorders>'.format(nsdecls('w')))
        tcPr.append(shd)
        tcPr.append(borders)
        
        # Cell margin padding
        mar = parse_xml(r'<w:tcMar {}><w:top w:w="160" w:type="dxa"/><w:bottom w:w="160" w:type="dxa"/><w:left w:w="220" w:type="dxa"/><w:right w:w="220" w:type="dxa"/></w:tcMar>'.format(nsdecls('w')))
        tcPr.append(mar)
        
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        
        r_head = p.add_run("Abstract—")
        r_head.font.bold = True
        r_head.font.size = Pt(9.5)
        r_head.font.color.rgb = RGBColor(15, 23, 42)
        
        r_body = p.add_run(abstract_text)
        r_body.font.size = Pt(9.5)
        r_body.font.color.rgb = RGBColor(51, 65, 85)
        
        p_kw = cell.add_paragraph()
        p_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_kw.paragraph_format.space_before = Pt(4)
        p_kw.paragraph_format.space_after = Pt(2)
        
        r_kwh = p_kw.add_run("Index Terms—")
        r_kwh.font.bold = True
        r_kwh.font.size = Pt(9)
        r_kwh.font.color.rgb = RGBColor(15, 23, 42)
        
        r_kwb = p_kw.add_run(keywords_text)
        r_kwb.font.italic = True
        r_kwb.font.size = Pt(9)
        r_kwb.font.color.rgb = RGBColor(71, 85, 105)
        
        # Spacing after abstract
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    def add_sec_heading(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(15, 23, 42)
        return p

    def add_subsec_heading(title):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(title)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = RGBColor(37, 99, 235) # Accent Blue
        return p

    def add_p(text, space_after=6):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10.5)
        r.font.color.rgb = RGBColor(30, 41, 59)
        return p

    def add_bullet(text):
        p = doc.add_paragraph(style='List Bullet')
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10.5)
        r.font.color.rgb = RGBColor(30, 41, 59)
        return p

    def add_equation(eq_str, num_str):
        tbl = doc.add_table(rows=1, cols=2)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell_eq = tbl.cell(0, 0)
        cell_eq.width = Inches(6.0)
        cell_num = tbl.cell(0, 1)
        cell_num.width = Inches(0.9)
        
        # Borderless
        for cell in (cell_eq, cell_num):
            tcPr = cell._tc.get_or_add_tcPr()
            b = parse_xml(r'<w:tcBorders {}><w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/></w:tcBorders>'.format(nsdecls('w')))
            tcPr.append(b)
            
        p1 = cell_eq.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p1.paragraph_format.space_before = Pt(2)
        p1.paragraph_format.space_after = Pt(2)
        r1 = p1.add_run(eq_str)
        r1.font.italic = True
        r1.font.size = Pt(10)
        r1.font.color.rgb = RGBColor(15, 23, 42)
        
        p2 = cell_num.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p2.paragraph_format.space_before = Pt(2)
        p2.paragraph_format.space_after = Pt(2)
        r2 = p2.add_run(f"({num_str})")
        r2.font.bold = True
        r2.font.size = Pt(10)
        r2.font.color.rgb = RGBColor(100, 116, 139)

    def add_image_figure(image_path, caption_text, width_inches=6.2):
        if not os.path.exists(image_path):
            print(f"Warning: Image not found at {image_path}")
            return
            
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(10)
        p_img.paragraph_format.space_after = Pt(4)
        p_img.paragraph_format.keep_with_next = True
        run = p_img.add_run()
        run.add_picture(image_path, width=Inches(width_inches))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(12)
        r_cap = p_cap.add_run(caption_text)
        r_cap.font.name = 'Times New Roman'
        r_cap.font.size = Pt(9.5)
        r_cap.font.bold = True
        r_cap.font.color.rgb = RGBColor(71, 85, 105)

    # =========================================================================
    # DOCUMENT HEADER
    # =========================================================================
    add_title("A Cloud-Native, Transformer-Based Battery Management System for Real-Time State of Charge and State of Health Prediction with Digital Twin Monitoring")
    add_authors()

    # =========================================================================
    # ABSTRACT & INDEX TERMS
    # =========================================================================
    abs_text = (
        "Accurate, real-time prediction of State of Charge (SOC) and State of Health (SOH) in lithium-ion batteries is essential "
        "for operational safety, performance optimization, and lifespan management across electric vehicles, grid-scale energy storage, "
        "and industrial equipment. This paper presents a cloud-native battery management system (BMS) powered by a dual-head, two-layer "
        "Transformer encoder architecture exported to the Open Neural Network Exchange (ONNX) format and deployed as a high-throughput, "
        "containerized asynchronous API. The model ingests a 32-step sliding window of voltage, current, and temperature telemetry to "
        "simultaneously estimate SOC and SOH retention. In reported benchmark evaluations, the Transformer model achieved an R² determination "
        "coefficient of 0.985 and a central processing unit (CPU) inference latency ranging between 0.62 and 0.68 ms per window. The production "
        "service was integrated with a web-based digital twin monitoring dashboard tracking 200 simulated battery packs across five distinct "
        "operational fleets, benchmarked against experimental degradation trajectories from the NASA Ames Prognostics Center of Excellence "
        "lithium-ion dataset. The reported benchmarks indicate that the Transformer architecture achieved higher prediction accuracy and lower "
        "inference latency than a comparative State-Space Model (SSM/Mamba) baseline on the evaluated platform, demonstrating a viable architectural "
        "pathway toward scalable, cloud-connected industrial battery intelligence."
    )
    kw_text = "Battery management systems, state of charge, state of health, transformer neural networks, ONNX Runtime, digital twin, cloud-native inference."
    add_abstract_callout(abs_text, kw_text)

    # =========================================================================
    # SECTION I: INTRODUCTION
    # =========================================================================
    add_sec_heading("I. INTRODUCTION")
    add_p(
        "Lithium-ion batteries (LIBs) serve as the cornerstone of the global transition toward decarbonized transportation, renewable energy grid integration, "
        "aerospace electrification, and automated robotics [1], [2]. To ensure safe operation, maximize usable energy extraction, and mitigate catastrophic "
        "thermal runaway risks, LIB systems rely comprehensively on Battery Management Systems (BMSs) [1]. Within modern BMS operations, the twin estimation "
        "tasks of State of Charge (SOC) and State of Health (SOH) are paramount. While SOC represents the instantaneous remaining electrochemical energy "
        "analogous to a dynamic fuel gauge, SOH quantifies irreversible capacity fade and internal impedance rise accumulated through cyclic degradation, "
        "solid electrolyte interphase (SEI) layer growth, and active material loss [3], [4]."
    )
    add_p(
        "Accurately determining SOC and SOH under volatile operational conditions is challenging. Traditional electrochemical models (such as the "
        "pseudo-two-dimensional Doyle–Fuller–Newman formulation) and Equivalent Circuit Models (ECMs) coupled with Extended Kalman Filters (EKF) "
        "suffer from severe computational overhead, non-trivial parameter identification under variable c-rates, and calibration drift across thermal ranges [3], [5]. "
        "Consequently, data-driven deep learning architectures have gained widespread acclaim for their ability to learn complex nonlinear degradation mappings "
        "directly from observable terminal telemetry (voltage, current, and temperature) [6], [7]. However, practical field adoption requires reconciling "
        "high predictive accuracy with low computational latency, while transitioning offline experimental prototypes into reliable, containerized cloud services [8]."
    )
    add_p(
        "A critical research gap persists between algorithmic laboratory models and robust, operational cloud deployments. While extensive literature examines "
        "deep neural networks on static offline datasets, practical systems must integrate time-series inference runtimes, sub-millisecond API endpoints, "
        "dynamic zero-downtime model hot-swapping, and multi-fleet digital twin telemetry visualization in a unified cloud infrastructure. To address this challenge, "
        "this work presents an end-to-end cloud-native BMS architecture that integrates deep sequence modeling with a resilient, cloud-hosted serving pipeline."
    )
    add_p("The primary contributions of this paper are summarized as follows:")
    add_bullet("Containerized Dual-Head Transformer Model: Development and validation of a compact, two-layer Transformer encoder exported to the Open Neural Network Exchange (ONNX) format, optimized for sub-millisecond CPU inference execution.")
    add_bullet("Production-Grade Asynchronous API: Implementation of a FastAPI backend service featuring a dedicated model-reload endpoint designed to support model replacement in memory without intentionally terminating the service process.")
    add_bullet("Multi-Fleet Digital Twin Dashboard: A live, web-based monitoring platform tracking 200 simulated battery packs across five operational environments, providing real-time telemetry inspection and automated health classification.")
    add_bullet("Empirical Validation on NASA PCoE Benchmarks: Comprehensive grounding using the NASA Ames Prognostics Center of Excellence lithium-ion dataset, incorporating degradation trajectories across reference cells B0005, B0006, B0007, and B0018.")
    add_bullet("Comparative Architectural Benchmarking: A quantitative evaluation comparing the Transformer against a State-Space Model (SSM/Mamba) baseline across inference latency, parameter count, and determination accuracy.")

    add_p(
        "The remainder of this paper is organized as follows: Section II surveys related work across battery state estimation, deep sequence modeling, and digital twins. "
        "Section III details the system architecture, model topology, and cloud infrastructure. Section IV outlines the dataset, feature engineering, and fleet simulation. "
        "Section V presents the experimental results, comparative benchmarks, and dashboard performance. Section VI concludes the paper and outlines future directions."
    )

    # =========================================================================
    # SECTION II: RELATED WORK
    # =========================================================================
    add_sec_heading("II. RELATED WORK")
    add_p(
        "Battery state estimation has evolved through multiple paradigms over the past two decades. Early industrial deployments relied predominantly on "
        "coulomb counting and Equivalent Circuit Models (ECMs) optimized via adaptive observers, most notably the Extended Kalman Filter (EKF) and Unscented Kalman Filter (UKF) [3], [5]. "
        "While Kalman filters provide closed-loop error-correcting dynamics, their estimation fidelity is intrinsically bounded by the order of the underlying circuit approximation "
        "(typically 1-RC or 2-RC networks) and frequently diverges during aggressive dynamic current pulses or pronounced temperature shifts [5]."
    )
    add_p(
        "To capture unmodeled electrochemical dynamics, data-driven machine learning has gained significant prominence. Chemali et al. demonstrated that "
        "Long Short-Term Memory (LSTM) recurrent networks achieve high SOC tracking precision across diverse driving cycles by exploiting internal memory gating [6]. "
        "Similarly, Recurrent Neural Networks (RNNs) and Gated Recurrent Units (GRUs) have been extensively deployed for battery degradation tracking and Remaining Useful Life (RUL) "
        "prognosis [9]. However, recurrent architectures process sequence tokens sequentially, creating sequential execution bottlenecks and hindering efficient vectorization on commodity CPUs."
    )
    add_p(
        "The Transformer architecture, pioneered by Vaswani et al. [10], revolutionized sequential modeling through multi-head self-attention mechanisms that compute "
        "global temporal correlations across an entire receptive window simultaneously. Shen et al. [7] successfully applied self-attention to battery state estimation, "
        "observing enhanced capacity to track nonlinear capacity recovery phenomena. Concurrently, structured State-Space Models (SSMs), notably the selective scan Mamba architecture "
        "introduced by Gu and Dao [11], have emerged as linear-time sequence alternatives, achieving competitive accuracy with dramatically reduced parameter footprints."
    )
    add_p(
        "In parallel with modeling advancements, the integration of digital twins for energy storage systems has emerged as an active research frontier [8], [12], [13]. "
        "A digital twin establishes a synchronized virtual representation of a physical asset, ingesting continuous telemetry to mirror degradation states, detect thermal anomalies, "
        "and execute predictive maintenance [13]. Crucially, operationalizing digital twins in production requires hardware-accelerated inference runtimes. Frameworks such as the "
        "Open Neural Network Exchange (ONNX) Runtime provide graph-level kernel fusion and hardware-optimized BLAS operations, bridging the gap between research models and production serving [14]. "
        "Modern asynchronous web frameworks like FastAPI provide high-throughput, non-blocking I/O execution with native OpenAPI compliance [15]. This work synthesizes these "
        "technologies into a unified, deployable platform addressing the end-to-end continuum from sensor to cloud inference."
    )

    # =========================================================================
    # SECTION III: SYSTEM ARCHITECTURE
    # =========================================================================
    add_sec_heading("III. SYSTEM ARCHITECTURE")
    add_p(
        "The system architecture integrates an optimized neural network model, a containerized asynchronous backend microservice, and a secured cloud infrastructure. "
        "Fig. 1 depicts the complete neural processing and inference pipeline."
    )
    
    # FIGURE 1: Transformer Architecture
    add_image_figure(os.path.join("figures", "fig1_transformer_architecture.png"), 
                     "Fig. 1. End-to-end data flow and dual-head Transformer model architecture for simultaneous SOC and SOH prediction.", width_inches=6.2)

    add_subsec_heading("A. Model Architecture & Dual Prediction Heads")
    add_p(
        "The predictive engine is built upon a custom dual-head, two-layer Transformer encoder. The model processes a sliding temporal window of battery telemetry:"
    )
    add_equation("X in R^(B x L x D)", "1")
    add_p(
        "where B denotes the batch dimension, L = 32 represents sequential time steps, and D = 3 corresponds to the physical feature channels: "
        "cell terminal voltage (V, in volts), load current (I, in amperes), and surface temperature (T, in degrees Celsius). Telemetry arrays are formatted as 32-bit floating-point tensors (Float32)."
    )
    add_p(
        "The input sequence is mapped into the encoder via a linear projection layer combined with a positional embedding tensor. In the project specification, "
        "the positional embedding is designated with dimensions [1, 512, 32] and characterized as a fixed or learned positional embedding. We preserve this supplied "
        "specification verbatim, noting that in standard sequence implementations, 512 denotes maximum allocated sequence length and 32 denotes the hidden embedding dimension, "
        "matching the sequence window length."
    )
    add_p(
        "The encoder comprises two stacked Transformer layers executing scaled dot-product multi-head self-attention followed by a position-wise feed-forward network with residual connections and layer normalization:"
    )
    add_equation("Attention(Q, K, V) = softmax( (Q K^T) / sqrt(d_k) ) V", "2")
    add_equation("Z^(l) = LayerNorm( X^(l-1) + MultiHead(X^(l-1)) )", "3")
    add_equation("X^(l) = LayerNorm( Z^(l) + FFN(Z^(l)) )", "4")
    add_p(
        "where Q, K, and V represent query, key, and value matrices, and d_k is the projection dimension. The complete neural topology encompasses approximately 25,600 trainable parameters."
    )
    add_p(
        "The latent representation from the final encoder layer is pooled and directed into two specialized, task-specific output heads:\n"
        "1) SOC Output Head (soc_output): Produces a tensor of shape [B, 1] mapped through a nonlinear Sigmoid activation function sigma(z) = (1 + e^(-z))^(-1), "
        "constraining the raw output to [0.0, 1.0]. The percentage SOC is computed directly via:"
    )
    add_equation("SOC_% = soc_raw * 100", "5")
    add_p(
        "2) SOH Output Head (soh_output): Produces a tensor of shape [B, 1] via a linear regression layer without activation, outputting a continuous scalar representing "
        "capacity retention relative to nominal capacity (1.0 = 100% nominal capacity)."
    )
    add_p(
        "To safeguard downstream operations against numerical drift, the backend applies a software clamping guardrail constraining SOH to [0.0, 1.5]. "
        "An automatic heuristic status classifier evaluates operational safety:"
    )
    add_equation("Status = NORMAL if SOH >= 0.85; DEGRADED if 0.70 <= SOH < 0.85; CRITICAL if SOH < 0.70 or Abnormal Temp", "6")
    add_p(
        "These decision boundaries represent project-defined software heuristics rather than internationally certified battery safety standards. "
        "The precise mathematical definition of 'Abnormal Temp' was not specified in the project documentation and must be determined via domain-specific thermal protocols."
    )
    add_p(
        "The neural network was exported to the Open Neural Network Exchange (ONNX) format. The compiled binary (transformer(1).onnx) occupies exactly 221,528 bytes (~216 KB) "
        "with cryptographic integrity validated via SHA-256 hash: 00c1c87675150f615d0ab5fbfa30577dd5099133ad422778c4a30aeb01c6a519."
    )

    add_subsec_heading("B. Backend Inference Service")
    add_p(
        "The inference engine is embedded within an asynchronous web microservice developed using FastAPI and Python. Model graph execution is delegated to the "
        "Microsoft ONNX Runtime utilizing the CPU execution provider. In local and cloud execution tests, the CPU inference latency was measured between 0.62 and 0.68 ms per 32-step window."
    )
    add_p(
        "The service architecture decouples model configuration from application code via a centralized configuration file (config.json). This file defines the active model filename, "
        "sliding window length (32), feature names, cold-start telemetry buffering, and scaler parameters for normalization. The API exposes six primary REST endpoints:"
    )
    add_bullet("POST /predict: Accepts a JSON payload containing a 32-step telemetry array ([32 x 3]), executing normalization, ONNX inference, clamping, and status categorization.")
    add_bullet("POST /predict/channels: Ingests three independent arrays representing voltage, current, and temperature vectors.")
    add_bullet("GET /fleet/{fleet_id}/{pack_id}: Retrieves historical telemetry, simulated sensor traces, and current operational states for a designated pack.")
    add_bullet("GET /health: Reports process health, loaded model status, active binary name, and window size.")
    add_bullet("GET /model/info: Returns active scaler boundaries, feature mappings, and guardrail limits.")
    add_bullet("GET /benchmark/comparison: Serves comparative empirical metrics between Transformer and alternative sequence models.")

    add_p(
        "A critical operational feature is the dynamic model management endpoint (POST /model/reload). This endpoint reloads config.json and instantiates a new ONNX Runtime "
        "InferenceSession in memory, overwriting the session reference without terminating the parent process or restarting the background daemon. While designed to facilitate "
        "hot-swapping during model updates, production zero-downtime performance under high concurrent query loads requires rigorous queue draining and validation."
    )

    add_subsec_heading("C. Cloud Infrastructure & Security")
    add_p(
        "The microservice was deployed onto an Amazon Web Services (AWS) Elastic Compute Cloud (EC2) virtual instance located in the Asia Pacific (Mumbai) region (ap-south-1). "
        "The instance configuration utilizes a t2.micro tier equipped with 1 virtual CPU (vCPU), 1 GB of random-access memory (RAM), and an 8 GB general-purpose solid-state drive (gp3 SSD) running Ubuntu Linux. "
        "Fig. 2 illustrates the cloud deployment architecture."
    )

    # FIGURE 3: Cloud Deployment Topology
    add_image_figure(os.path.join("figures", "fig3_cloud_infrastructure.png"), 
                     "Fig. 2. Cloud deployment topology on AWS EC2 showing Nginx reverse proxy, TLS termination, and FastAPI background service.", width_inches=6.2)

    add_p(
        "The application process is managed as a continuous background daemon via a systemd unit (bms-api.service). Inbound HTTP traffic is managed by an Nginx 1.24.0 reverse proxy "
        "configured with gzip compression, routing external requests on ports 80 and 443 to the internal ASGI upstream bound to 127.0.0.1:8000. Public access is routed via Dynamic DNS "
        "under the custom domain battery-bms.duckdns.org. Transport Layer Security (TLS) is terminated at Nginx using a 2048-bit RSA certificate issued by Let's Encrypt, with automated "
        "certificate renewal managed by the systemd certbot.timer. Under the standard AWS Free Tier policy providing 750 monthly instance hours for t2.micro, the project documentation "
        "reported an operational infrastructure expenditure of $0.00/month. We present this figure strictly as project-supplied operational telemetry; actual cloud billing remains subject "
        "to individual account status, network data egress, snapshot storage, and regional AWS pricing policies."
    )

    # =========================================================================
    # SECTION IV: DATASET AND EXPERIMENTAL SETUP
    # =========================================================================
    add_sec_heading("IV. DATASET AND EXPERIMENTAL SETUP")
    add_subsec_heading("A. NASA Ames PCoE Battery Dataset")
    add_p(
        "The empirical grounding of this study relies on the publicly available lithium-ion battery degradation repository published by the NASA Ames Prognostics Center of Excellence (PCoE) [4]. "
        "The project documentation identifies four commercially available 18650-size lithium-ion cells: B0005, B0006, B0007, and B0018. These cells were subjected to repeated charge-discharge "
        "cycling under controlled laboratory conditions to characterize accelerated capacity degradation and thermal response:"
    )
    add_bullet("Cell B0005: Cycled at room temperature (24°C) under a constant 2.0A direct-current discharge regime down to a cutoff threshold of 2.7V.")
    add_bullet("Cell B0006: Subjected to accelerated aging at 24°C under 2.0A discharge with a deep-discharge cutoff threshold of 2.5V, inducing accelerated capacity loss.")
    add_bullet("Cell B0007: Operated at 24°C under 2.0A discharge to an extended cutoff of 2.2V, serving as an extended-life reference trajectory.")
    add_bullet("Cell B0018: Cycled under severe thermal and deep-discharge stress down to 2.5V cutoff conditions.")

    add_p(
        "The project documentation references capacity fade and SOH degradation monitored over 168 discharge cycles. Verification of original NASA PCoE records indicates that "
        "168 discharge cycles characterizes the specific test regime of cells B0005, B0006, and B0007, whereas cell B0018 underwent a shortened cycling profile of 132 discharge cycles. "
        "Fig. 3 presents the multi-panel scientific degradation analysis extracted from these four benchmark cells."
    )

    # FIGURE 2: NASA Degradation Curves
    add_image_figure(os.path.join("figures", "fig2_nasa_degradation.png"), 
                     "Fig. 3. Scientific degradation analysis across NASA reference cells: (a) capacity fade, (b) SOH retention, (c) dynamic voltage collapse, and (d) thermal rise.", width_inches=6.2)

    add_subsec_heading("B. Input Feature Engineering")
    add_p(
        "The neural model ingests three raw telemetry channels: voltage (V), current (I), and temperature (T). Continuous time-series measurements are structured into uniform "
        "sliding windows containing 32 sequential samples, yielding an input tensor shape of [B, 32, 3]. Telemetry normalization is defined in config.json via linear min-max scaling:"
    )
    add_equation("x_tilde_i = (x_i - x_min_i) / (x_max_i - x_min_i)", "7")
    add_p(
        "where x_min and x_max represent pre-configured channel boundaries (e.g., V in [2.5, 4.2] V, I in [-20, 20] A, and T in [0, 60]°C). In the reported production deployment configuration, "
        "the software toggle enable_normalization was set to false, indicating that model weights operated directly on calibrated engineering units or pre-scaled upstream signals."
    )

    add_subsec_heading("C. Multi-Fleet Digital Twin Simulator")
    add_p(
        "To validate digital twin monitoring capabilities across varied duty cycles, the cloud platform integrates a multi-fleet data generator simulating 200 distinct battery packs "
        "distributed across five industrial sectors (Fig. 4):"
    )
    add_bullet("Fleet 1 - Urban EV Taxi Fleet: 35 packs, characterized by frequent stop-and-go regeneration cycles and benchmarked against NASA cell B0005.")
    add_bullet("Fleet 2 - Heavy Logistics Highway Fleet: 40 packs, characterized by sustained high-rate discharge profiles benchmarked against cell B0006.")
    add_bullet("Fleet 3 - Grid Energy Storage Substation: 45 packs, operating under shallow diurnal cycling benchmarked against cell B0007.")
    add_bullet("Fleet 4 - Airport Ground Support Equipment: 30 packs, characterized by intermittent heavy draw cycles benchmarked against cell B0018.")
    add_bullet("Fleet 5 - Commercial Last-Mile Delivery Vans: 50 packs, operating under heterogeneous urban routes governed by a composite NASA benchmark.")

    # FIGURE 4: Fleet Distribution
    add_image_figure(os.path.join("figures", "fig4_fleet_distribution.png"), 
                     "Fig. 4. Distribution of 200 simulated battery packs across five operational fleet environments in the digital twin platform.", width_inches=5.8)

    add_p(
        "We explicitly emphasize that these 200 operational battery packs represent synthetic, mathematically simulated digital twin profiles grounded in empirical NASA degradation curves; "
        "they do not represent 200 instrumented physical battery hardware systems."
    )

    add_subsec_heading("D. Evaluation Metrics")
    add_p(
        "The quantitative performance of the state estimation framework is evaluated using three primary criteria:\n"
        "1) Coefficient of Determination (R²): Measures the proportion of variance in the ground-truth battery state (y) explained by model predictions (y_hat):"
    )
    add_equation("R^2 = 1 - ( sum( (y_i - y_hat_i)^2 ) / sum( (y_i - y_bar)^2 ) )", "8")
    add_p(
        "where y_bar denotes the empirical mean of the ground truth. An R² value approaching 1.0 indicates close predictive correlation.\n"
        "2) Inference Latency (tau): The execution wall-clock time in milliseconds (ms) required for the ONNX Runtime session to process a single [1, 32, 3] input tensor on CPU.\n"
        "3) Parameter Footprint (P): The total number of trainable weights and biases, governing computational complexity and memory utilization."
    )

    # =========================================================================
    # SECTION V: RESULTS AND DISCUSSION
    # =========================================================================
    add_sec_heading("V. RESULTS AND DISCUSSION")
    add_subsec_heading("A. Prediction Accuracy")
    add_p(
        "In project-reported benchmark evaluations, the dual-head Transformer model achieved a determination coefficient of R² = 0.985. "
        "This reported metric indicates strong agreement between model predictions and reference test observations across the evaluated dataset. "
        "However, academic rigor requires clarifying that this figure was supplied as an aggregate metric; the project documentation does not separate "
        "R² values independently for the SOC head versus the SOH head, nor does it detail the exact train/test cycle split, cross-validation partitioning, "
        "or temporal leakage prevention protocols."
    )
    add_p(
        "The software guardrail clamping SOH in [0.0, 1.5] serves as a practical software safeguard to eliminate catastrophic floating-point excursions "
        "in unconstrained linear regression heads. However, clamping represents an external boundary filter and does not inherently reflect higher intrinsic "
        "predictive fidelity within the normal operating range. Comprehensive academic validation would require publishing mean absolute error (MAE), "
        "root mean square error (RMSE), and cell-level cross-validation distributions across unseen battery chemistries."
    )

    add_subsec_heading("B. Inference Latency & System Responsiveness")
    add_p(
        "On the evaluated AWS EC2 t2.micro virtual machine (1 vCPU, Intel Xeon Family architecture), the ONNX-optimized Transformer achieved a reported execution latency of "
        "0.62 to 0.68 ms per 32-step window. This sub-millisecond execution demonstrates that compact self-attention networks can be efficiently executed on standard x86 CPU architectures "
        "without requiring dedicated graphics processing units (GPUs) or neural accelerators."
    )
    add_p(
        "Nevertheless, this measurement reflects isolated neural execution time within the ONNX C++ runtime. It should not be conflated with end-to-end network latency, "
        "which encompasses client-side serialization, TCP transport over the public Internet, TLS handshake negotiation, Nginx proxy forwarding, and JSON schema validation within FastAPI. "
        "In local network client testing (test_client.py), complete HTTP round-trip times averaged between 12 and 18 ms, illustrating that network transport dominates computational inference time."
    )

    add_subsec_heading("C. Architecture Comparison: Transformer vs. SSM/Mamba")
    add_p(
        "To contextualize the performance of the Transformer architecture, the project documentation includes comparative benchmark measurements against a State-Space Model (SSM/Mamba) sequence baseline. "
        "The exact comparative results are reported in Table I."
    )

    # TABLE I: ARCHITECTURE PERFORMANCE COMPARISON
    p_tcap = doc.add_paragraph()
    p_tcap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tcap.paragraph_format.space_before = Pt(8)
    p_tcap.paragraph_format.space_after = Pt(2)
    p_tcap.paragraph_format.keep_with_next = True
    rt1 = p_tcap.add_run("TABLE I\nARCHITECTURE PERFORMANCE COMPARISON")
    rt1.font.bold = True
    rt1.font.size = Pt(9.5)
    rt1.font.color.rgb = RGBColor(15, 23, 42)

    tab1 = doc.add_table(rows=5, cols=3)
    tab1.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_data = [
        ["Metric", "Transformer", "SSM (Mamba)"],
        ["Inference Latency", "0.68 ms", "5.60 ms"],
        ["Speedup Factor", "1× (baseline)", "Approximately 8.2× slower"],
        ["Parameter Count", "25,600", "7,800"],
        ["R² Accuracy", "0.985", "0.962"]
    ]
    for r_idx, row in enumerate(table_data):
        for c_idx, val in enumerate(row):
            cell = tab1.cell(r_idx, c_idx)
            cell.width = Inches(2.1)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            r = p.add_run(val)
            r.font.name = 'Times New Roman'
            r.font.size = Pt(9.5)
            
            tcPr = cell._tc.get_or_add_tcPr()
            if r_idx == 0:
                r.font.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
                shd = parse_xml(r'<w:shd {} w:fill="1E293B"/>'.format(nsdecls('w'))) # Dark Navy header
                tcPr.append(shd)
            elif r_idx % 2 == 1:
                shd = parse_xml(r'<w:shd {} w:fill="F8FAFC"/>'.format(nsdecls('w'))) # Subtle light stripe
                tcPr.append(shd)

    # Set table borders
    tblPr = tab1._tbl.tblPr
    borders = parse_xml(r'<w:tblBorders {}><w:top w:val="single" w:sz="8" w:space="0" w:color="0F172A"/><w:bottom w:val="single" w:sz="8" w:space="0" w:color="0F172A"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/><w:insideV w:val="none"/><w:left w:val="none"/><w:right w:val="none"/></w:tblBorders>'.format(nsdecls('w')))
    tblPr.append(borders)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # FIGURE 5: Slide 8 Empirical Graphic
    if os.path.exists("slide8_graph.jpg"):
        add_image_figure("slide8_graph.jpg", 
                         "Fig. 5. Empirical architecture benchmark: tracking accuracy, CPU inference latency (0.68 ms vs 5.60 ms), and parameter footprint (25.6k vs 7.8k).", width_inches=6.2)

    add_p(
        "As summarized in Table I and Fig. 5, the Transformer model possesses a larger parameter footprint (25,600 parameters) than the compact Mamba model (7,800 parameters). "
        "Despite having approximately 3.3 times more parameters, the Transformer achieved an inference latency of 0.68 ms, which is approximately 8.2 times faster than the reported Mamba latency of 5.60 ms. "
        "Furthermore, the Transformer achieved a higher reported coefficient of determination (R² = 0.985) compared to the SSM baseline (R² = 0.962)."
    )
    add_p(
        "These values represent project-reported benchmark observations and must be interpreted within proper computational context. We do not claim that Transformer architectures are "
        "fundamentally faster than State-Space Models across all sequence lengths. In general algorithmic theory, SSMs scale with linear complexity O(L), whereas standard self-attention "
        "exhibits quadratic complexity O(L²). However, for very short sequence lengths (L = 32), the quadratic overhead of attention is negligible. Moreover, the ONNX Runtime provides mature, "
        "highly vectorized Basic Linear Algebra Subprograms (BLAS) CPU kernels for dense matrix multiplications used in self-attention. In contrast, SSM architectures rely on sequential recurrent "
        "scans or parallel associative scans that frequently require specialized GPU CUDA/Triton kernels to achieve peak throughput; when executed on standard CPU runtimes in general-purpose "
        "frameworks, sequential scan operations can experience substantial loop overhead. A definitive hardware-agnostic comparison requires uniform profiling under identical runtime kernels, "
        "batch sizes, and hardware architectures."
    )

    add_subsec_heading("D. Digital Twin Dashboard Performance")
    add_p(
        "The live digital twin dashboard was verified across 200 simulated packs. Dashboard telemetry streams operate with sub-second interface refreshes, rendering interactive sparklines "
        "for voltage, current, and temperature alongside real-time SOC gauges and SOH indicators. Dynamic inspection modals trigger model inference on demand, generating instant diagnostic assessments."
    )
    add_p(
        "The dynamic model hot-swapping capability was validated via the POST /model/reload endpoint. During diagnostic testing, an updated configuration and model binary were loaded into the "
        "running Python process without terminating the systemd service. However, this capability constitutes a functional software mechanism; verifying true zero-downtime performance with "
        "zero dropped packets under saturated concurrent load requires formal distributed load testing and blue-green deployment infrastructure."
    )

    # =========================================================================
    # SECTION VI: CONCLUSION & FUTURE WORK
    # =========================================================================
    add_sec_heading("VI. CONCLUSION")
    add_p(
        "This paper presented the design, implementation, and deployment of a cloud-native battery management system integrating a dual-head, two-layer Transformer encoder with an asynchronous "
        "inference microservice and an interactive digital twin monitoring platform. Exported to the ONNX format and executed via ONNX Runtime on an AWS EC2 micro-instance, the model achieved a "
        "reported R² determination coefficient of 0.985 and a CPU inference latency of 0.62–0.68 ms for 32-step telemetry windows. In the reported empirical comparison, the Transformer demonstrated "
        "faster CPU inference execution and higher predictive correlation than an SSM/Mamba baseline. The integrated platform demonstrated continuous monitoring capabilities across 200 simulated "
        "battery packs grounded in NASA PCoE degradation curves."
    )
    add_p(
        "These findings highlight the engineering feasibility of deploying deep sequence models for microsecond-scale battery state inference within cost-effective cloud architectures. "
        "However, broader industrial applicability requires addressing clear limitations: the evaluation relied on laboratory datasets and synthetic fleet profiles rather than physically "
        "instrumented operational vehicles, and the system does not possess industrial safety certifications."
    )
    add_p("Future research will focus on the following directions:")
    add_bullet("Joint RUL Prediction: Extending the multi-task heads to predict Remaining Useful Life (RUL) and knee-point degradation onset directly alongside SOC and SOH.")
    add_bullet("Embedded Edge Acceleration: Porting the containerized ONNX runtime to embedded edge hardware platforms (e.g., NVIDIA Jetson, Raspberry Pi) to benchmark localized inference against cloud execution.")
    add_bullet("Heterogeneous Fleet Telemetry: Validating model generalization using heterogeneous field telemetry from operational electric vehicle fleets under sub-zero and dynamic charging conditions.")
    add_bullet("Concurrency and Stress Testing: Conducting formal stress testing under concurrent user loads to quantify API throughput, queuing delays, and reload reliability under heavy saturation.")

    # =========================================================================
    # ACKNOWLEDGMENT
    # =========================================================================
    add_sec_heading("ACKNOWLEDGMENT")
    add_p(
        "The authors acknowledge the NASA Ames Prognostics Center of Excellence for providing access to the publicly available lithium-ion battery dataset used in this study."
    )

    # =========================================================================
    # REFERENCES
    # =========================================================================
    add_sec_heading("REFERENCES")
    refs = [
        "[1] M. A. Hannan, M. S. H. Lipu, A. Hussain, and A. Mohamed, \"A review of lithium-ion battery state of charge estimation and management system in electric vehicle applications: Challenges and recommendations,\" Renewable and Sustainable Energy Reviews, vol. 78, pp. 834–854, Oct. 2017, doi: 10.1016/j.rser.2017.05.001.",
        "[2] K. A. Severson et al., \"Data-driven prediction of battery cycle life before capacity degradation,\" Nature Energy, vol. 4, no. 5, pp. 383–391, May 2019, doi: 10.1038/s41560-019-0356-8.",
        "[3] G. L. Plett, \"Extended Kalman filtering for battery management systems of LiPB-based HEV battery packs: Part 3. State and parameter estimation,\" Journal of Power Sources, vol. 134, no. 2, pp. 277–292, Aug. 2004, doi: 10.1016/j.jpowsour.2004.02.033.",
        "[4] B. Saha and K. Goebel, \"Battery Data Set,\" NASA Ames Prognostics Data Repository, NASA Ames Research Center, Moffett Field, CA, USA, 2007.",
        "[5] H. He, R. Xiong, and J. Fan, \"Evaluation of lithium-ion battery equivalent circuit models for state of charge estimation by an experimental approach,\" Energies, vol. 4, no. 4, pp. 582–598, Apr. 2011, doi: 10.3390/en4040582.",
        "[6] E. Chemali, P. J. Kollmeyer, M. Preindl, R. Ahmed, and A. Emadi, \"Long short-term memory networks for accurate state-of-charge estimation of Li-ion batteries,\" IEEE Transactions on Industrial Electronics, vol. 65, no. 8, pp. 6730–6739, Aug. 2018, doi: 10.1109/TIE.2017.2787758.",
        "[7] H. Shen, X. Zhou, Z. Wang, and J. Wang, \"State of charge estimation for lithium-ion battery using Transformer with immersion and invariance adaptive observer,\" Journal of Energy Storage, vol. 45, p. 103768, Jan. 2022, doi: 10.1016/j.est.2021.103768.",
        "[8] D. Karnehm, L. Anekal, A. Samanta, A. Neve, and S. S. Williamson, \"Towards digital twining of lithium-ion battery management systems: An extended Kalman filter for state-of-charge estimation in cloud-platform,\" in Proc. 2023 IEEE Energy Conversion Congress and Exposition (ECCE), 2023, pp. 1109–1114, doi: 10.1109/ECCE53617.2023.10362099.",
        "[9] W. Li, M. Sengupta, P. Dechent, D. Howey, A. Annaswamy, and D. U. Sauer, \"One-shot battery degradation trajectory prediction with deep learning,\" Journal of Power Sources, vol. 506, p. 230024, Sep. 2021, doi: 10.1016/j.jpowsour.2021.230024.",
        "[10] A. Vaswani et al., \"Attention is all you need,\" in Advances in Neural Information Processing Systems (NeurIPS), vol. 30, 2017, pp. 5998–6008.",
        "[11] A. Gu and T. Dao, \"Mamba: Linear-time sequence modeling with selective state spaces,\" arXiv preprint arXiv:2312.00752, 2023.",
        "[12] A. Dharani, S. S. Patange, et al., \"A digital twin framework for dual-path estimation of battery state of charge and state of health using hybrid physics-informed machine learning,\" IEEE Access, vol. 14, 2026, doi: 10.1109/ACCESS.2026.3652279.",
        "[13] N. Ghosh, A. Garg, A. J. Warnecke, D. Kumar, and L. Gao, \"Transfer adaptive digital twin for cross-domain state-of-health estimation of Li-ion batteries,\" IEEE Transactions on Transportation Electrification, 2025, doi: 10.1109/TTE.2025.3538624.",
        "[14] ONNX Runtime Developers, \"ONNX Runtime: Cross-platform, high performance ML inferencing and training accelerator,\" Microsoft, 2021. [Online]. Available: https://onnxruntime.ai",
        "[15] S. Ramirez, \"FastAPI: High performance, easy to learn, fast to code, ready for production,\" 2018. [Online]. Available: https://fastapi.tiangolo.com"
    ]
    for r_str in refs:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        r = p.add_run(r_str)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(51, 65, 85)

    doc.save(filename)
    print(f"Successfully generated Word document: {filename}")

if __name__ == "__main__":
    create_publication_paper()
