# ⚡ AI-Driven Battery Management System (BMS) Digital Twin

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![ONNX Runtime](https://img.shields.io/badge/Inference-ONNX%20Runtime%20CPU-005CED?logo=onnx&logoColor=white)](https://onnxruntime.ai/)
[![Deployment](https://img.shields.io/badge/Cloud-AWS%20EC2%20%2B%20Nginx%20%2B%20HTTPS-FF9900?logo=amazon-aws&logoColor=white)](https://battery-bms.duckdns.org)
[![Conference Paper](https://img.shields.io/badge/IEEE-Conference%20Paper%20Included-00629B?logo=ieee&logoColor=white)](paper/IEEE_TwoColumn_BMS_Conference_Paper.pdf)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **A production-grade cyber-physical Digital Twin and high-performance inference platform for Electric Vehicle (EV) and Grid Battery Management Systems (BMS), powered by a dual-head Transformer neural network.**

---

## 🌐 Live Production Demo & API Docs

- **Interactive Web Dashboard**: [https://battery-bms.duckdns.org](https://battery-bms.duckdns.org)
- **Interactive Swagger OpenAPI**: [https://battery-bms.duckdns.org/docs](https://battery-bms.duckdns.org/docs)
- **Alternative ReDoc UI**: [https://battery-bms.duckdns.org/redoc](https://battery-bms.duckdns.org/redoc)

---

## 🚀 Key Highlights & Capabilities

- **Ultra-Low Latency Edge Inference**: Runs an optimized 2-layer self-attention Transformer via Microsoft ONNX Runtime on CPU with **~0.65 ms latency** per 32-step telemetry window.
- **Dual-Head Prediction**: Simultaneously infers:
  - **State of Charge (SOC %)**: Bounded nonlinear battery charge level.
  - **State of Health (SOH)**: Battery capacity retention & degradation progression.
- **Pluggable & Zero-Downtime Hot-Swapping**: Update model weights and scalers on the fly (`POST /model/reload`) without restarting the server.
- **Fleet-Scale Digital Twin**: Simulates and monitors **200 battery packs** across 5 distinct operational operating environments (Urban EV, Highway Haulage, Tropical Grid, Cold Arctic, Extreme Heavy Duty).
- **Empirical Grounding**: Grounded in real-world **NASA Ames Prognostics Center of Excellence (PCoE)** Lithium-ion aging curves (Cells B0005, B0006, B0007, B0018) and empirical State-Space Model (SSM / Mamba) benchmarks.
- **Academic Research Included**: Includes full IEEE 2-column format conference paper (`paper/IEEE_TwoColumn_BMS_Conference_Paper.pdf`) and LaTeX source files (`paper/paper.tex`).

---

## 📐 System Architecture

```
                       +---------------------------------------+
                       |   Battery Telemetry (32 Timesteps)    |
                       |   Voltage (V), Current (A), Temp (°C) |
                       +---------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        FASTAPI CORE & INFERENCE ENGINE                            |
|                                                                                   |
|   +-----------------------+     Config & Scalers      +-----------------------+   |
|   |   Input Validation    | <-----------------------> |      config.json      |   |
|   |  (Pydantic Schemas)   |                           +-----------------------+   |
|   +-----------------------+                                                       |
|               |                                                                   |
|               v                                                                   |
|   +---------------------------------------------------------------------------+   |
|   |                   ONNX Runtime Engine (CPU Provider)                      |   |
|   |      Model Artifact: transformer(1).onnx (~216 KB, ~25,600 params)        |   |
|   |      Latencies: 0.62 ms - 0.68 ms                                         |   |
|   +---------------------------------------------------------------------------+   |
|               |                                       |                           |
|               v                                       v                           |
|       Head 1: SOC [0.0 - 1.0]                 Head 2: SOH Metric                  |
+-----------------------------------------------------------------------------------+
        |                                                       |
        v                                                       v
+----------------------------------+        +---------------------------------------+
|    Interactive Web Dashboard     |        |          External Consumers           |
| (Multi-Fleet Digital Twin & Lab) |        |   (CAN Bus / IoT Telemetry / Cloud)   |
+----------------------------------+        +---------------------------------------+
```

---

## 📁 Repository Structure

```
Battery-Management-System-BMS/
│
├── app.py                     # High-performance FastAPI server & inference engine
├── fleet_data.py              # 200-pack fleet telemetry simulation & NASA datasets
├── config.json                # Runtime configuration, scalers & guardrails
├── transformer(1).onnx        # Trained dual-head Transformer ONNX model artifact
├── index.html                 # Adaptive interactive dashboard (Localhost & Cloud auto-detect)
├── requirements.txt           # Python package dependencies
├── verify_model.py            # Local ONNX model integrity & benchmark verification script
├── test_client.py             # Client test suite for testing endpoints & latency
│
├── deployment/                # Production cloud deployment templates
│   ├── bms-api.service        # Systemd daemon configuration
│   └── bms_nginx.conf         # Nginx reverse-proxy & SSL/TLS configuration
│
├── docs/                      # Technical roadmaps and architecture specs
│   ├── PROJECT_HANDOVER.txt   # Complete operational handover document
│   ├── AWS_BMS_ROADMAP.md     # AWS IoT Core, DynamoDB, S3 ETL architecture plan
│   └── FUTURE_IMPROVEMENTS.md # Embedded C/C++ target, Kalman filter, edge roadmaps
│
└── paper/                     # Academic publication materials
    ├── IEEE_TwoColumn_BMS_Conference_Paper.pdf  # Full IEEE 2-column paper (Ready to Read)
    ├── paper.tex              # Complete IEEE conference LaTeX source
    ├── figures/               # High-resolution architectural & benchmark figures
    └── scripts/               # Figure generation & compilation scripts
```

---

## 💻 Quickstart: Running Locally

You can run the entire system locally in under 2 minutes:

### 1. Clone the Repository
```bash
git clone https://github.com/darshan968600-code/battery-management-system.git
cd battery-management-system
```

### 2. Create and Activate Virtual Environment
```bash
# On Linux / macOS
python3 -m venv venv
source venv/bin/activate

# On Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify the ONNX Model
Run the standalone model diagnostic script to verify your CPU execution environment:
```bash
python verify_model.py
```

### 5. Launch the Local BMS Service
```bash
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
# Or directly:
python app.py
```

### 6. Open the Dashboard
Open your browser and visit:
👉 **[http://localhost:8000](http://localhost:8000)**

The dashboard automatically senses it is running locally, displaying **`Localhost (127.0.0.1:8000)`** and executing all neural predictions against your local machine.

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the interactive Digital Twin web dashboard |
| `GET` | `/health` | Healthcheck verifying model state and input dimension |
| `GET` | `/model/info` | Inspect active model metadata, window size, and normalization scalers |
| `POST` | `/model/reload` | Zero-downtime hot-reload of model from `config.json` |
| `POST` | `/predict` | Ingests a 32-step `[V, I, T]` window; returns SOC %, SOH, and latency |
| `GET` | `/fleet/list` | Returns summary list of all 5 simulated fleets (200 packs) |
| `GET` | `/fleet/{fleet_id}` | Detailed telemetry and predictions for all packs in a fleet |
| `GET` | `/fleet/{fleet_id}/{battery_id}` | Full 32-timestep waveform and single-pack diagnostic detail |
| `GET` | `/dataset/benchmarks` | NASA Ames PCoE capacity degradation curves (B0005, B0006, etc.) |
| `GET` | `/benchmark/comparison` | Empirical benchmarks: Transformer vs. SSM (Mamba) |
| `POST` | `/custom-dataset/upload` | Validates and ingests user-uploaded battery test datasets |

### Example Prediction Request (`curl`):
```bash
curl -X POST "http://127.0.0.1:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "window": [
         [3.82, -2.1, 28.5],
         [3.81, -2.1, 28.6],
         [3.80, -2.2, 28.7]
       ]
     }'
```
*Note: Any window shorter than 32 timesteps is automatically front-padded with initial readings.*

---

## 📄 Academic Research Paper

The complete academic paper documenting the model architecture, NASA PCoE battery aging experiments, and cloud cyber-physical integration is included in this repository:

- 📄 **PDF**: [`paper/IEEE_TwoColumn_BMS_Conference_Paper.pdf`](paper/IEEE_TwoColumn_BMS_Conference_Paper.pdf)
- 📝 **LaTeX**: [`paper/paper.tex`](paper/paper.tex)

### Citation (BibTeX)
```bibtex
@inproceedings{bms_transformer_2026,
  title={Cyber-Physical Battery Management System with Dual-Head Transformer Neural Inference and Cloud Digital Twin},
  author={Kodali, D. R.},
  booktitle={IEEE International Conference on Industrial Cyber-Physical Systems (ICPS)},
  year={2026}
}
```

---

## 🔒 Security Notice

This repository strictly excludes all private access keys (`*.pem`, `*.key`) and environment credentials via `.gitignore`. When deploying to AWS or any cloud infrastructure, always manage certificates via Let's Encrypt / Certbot and manage access keys through IAM roles or local credential managers.

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
