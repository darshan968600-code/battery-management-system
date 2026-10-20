import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

os.makedirs('figures', exist_ok=True)

# ----------------------------------------------------------------------
# FIGURE 1: Transformer Model Architecture & Data Flow Diagram
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.0, 5.0), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

def draw_box(x, y, w, h, title, subtitle="", color="#f0f4f8", border="#1f77b4", radius=2):
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.5,rounding_size={radius}",
                                  facecolor=color, edgecolor=border, linewidth=1.5)
    ax.add_patch(rect)
    if subtitle:
        ax.text(x + w/2, y + h*0.62, title, ha='center', va='center', fontsize=9.5, fontweight='bold', color='#111827')
        ax.text(x + w/2, y + h*0.28, subtitle, ha='center', va='center', fontsize=8, color='#4b5563')
    else:
        ax.text(x + w/2, y + h/2, title, ha='center', va='center', fontsize=9, fontweight='bold', color='#111827')

def draw_arrow(x1, y1, x2, y2, label=""):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(facecolor='#374151', edgecolor='#374151', arrowstyle='->', lw=1.5))
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2 + 1.8, label, ha='center', va='bottom', fontsize=7.5, color='#1f2937')

# Input Layer
draw_box(4, 38, 16, 24, "Raw Telemetry", "V(t), I(t), T(t)\nWindow L=32", color="#e0f2fe", border="#0284c7")
draw_arrow(20, 50, 26, 50, "Sliding Window")

# Preprocessing & Scaler
draw_box(26, 38, 15, 24, "Input Layer", "Shape: [B, 32, 3]\nMinMax Scaler", color="#f1f5f9", border="#64748b")
draw_arrow(41, 50, 47, 50, "Float32 Tensor")

# Transformer Encoder
draw_box(47, 30, 24, 40, "2-Layer Transformer", "Multi-Head Self-Attention\nPos. Embed [1, 512, 32]\nLayerNorm & Res. Adds\n~25,600 Parameters", color="#fef3c7", border="#d97706")

# Branches to dual heads
draw_arrow(71, 58, 77, 72)
draw_arrow(71, 42, 77, 28)

# SOC Head
draw_box(77, 63, 20, 18, "SOC Output Head", "Sigmoid Activation\nSOC = raw * 100\n[Batch, 1]", color="#dcfce7", border="#16a34a")

# SOH Head
draw_box(77, 19, 20, 18, "SOH Output Head", "Linear Regression\nCapacity Retention\n[Batch, 1]", color="#fee2e2", border="#dc2626")

# Convergence to Guardrails
ax.annotate('', xy=(77, 4), xytext=(87, 19), arrowprops=dict(facecolor='#374151', edgecolor='#374151', arrowstyle='->', lw=1.2))
draw_box(52, 2, 44, 11, "Software Guardrail & Status Classifier", "Clamping [0.0, 1.5] -> NORMAL / DEGRADED / CRITICAL", color="#ede9fe", border="#7c3aed")

plt.tight_layout()
fig_arch = os.path.join('figures', 'fig1_transformer_architecture.png')
plt.savefig(fig_arch, dpi=300)
plt.close()
print(f"Generated: {fig_arch}")

# ----------------------------------------------------------------------
# FIGURE 3: Cloud Deployment & Service Infrastructure Topology
# ----------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.0, 4.8), dpi=300)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# External Traffic
draw_box(2, 60, 22, 26, "Client & Telemetry", "ESP32 Edge MCU\nBrowser Dashboard\nDynamic REST / JSON", color="#f0fdf4", border="#16a34a")
draw_arrow(24, 73, 32, 73, "HTTPS (443)")

# AWS EC2 Instance Perimeter
rect_ec2 = patches.FancyBboxPatch((30, 10), 68, 85, boxstyle="round,pad=1.0,rounding_size=3",
                                  facecolor="#fafafa", edgecolor="#f97316", linewidth=2, linestyle='--')
ax.add_patch(rect_ec2)
ax.text(32, 91, "AWS EC2 Ubuntu (ap-south-1, t2.micro: 1 vCPU, 1 GB RAM, 8 GB SSD) - $0.00/Mo Free Tier", 
        fontsize=8.5, fontweight='bold', color="#c2410c")

# Nginx Reverse Proxy
draw_box(33, 56, 18, 30, "Nginx 1.24.0", "Reverse Proxy\nLet's Encrypt TLS\nCertbot Timer\nGzip Engine", color="#ecfdf5", border="#059669")
draw_arrow(51, 71, 57, 71, "Upstream:8000")

# FastAPI App
draw_box(57, 45, 20, 42, "FastAPI Service", "Asynchronous Python\nbms-api.service\n/predict & /health\nPOST /model/reload", color="#f0f9ff", border="#0284c7")
draw_arrow(77, 66, 82, 66)

# ONNX Runtime
draw_box(82, 45, 14, 42, "ONNX\nRuntime", "CPU Provider\nLatency:\n0.62-0.68ms\nBinary: 216KB", color="#fef9c3", border="#ca8a04")

# Hot reload feedback loop
ax.annotate('Dynamic Reload\nWithout Restart', xy=(67, 45), xytext=(67, 24),
            arrowprops=dict(facecolor='#7c3aed', edgecolor='#7c3aed', arrowstyle='<->', lw=1.5),
            ha='center', va='top', fontsize=7.5, fontweight='bold', color='#6d28d9')

# Config.json
draw_box(54, 14, 26, 10, "Pluggable config.json", "Scalers, weights & thresholds", color="#f3f4f6", border="#4b5563")

plt.tight_layout()
fig_cloud = os.path.join('figures', 'fig3_cloud_infrastructure.png')
plt.savefig(fig_cloud, dpi=300)
plt.close()
print(f"Generated: {fig_cloud}")
