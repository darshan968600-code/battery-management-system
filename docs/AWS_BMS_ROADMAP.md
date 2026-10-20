# AWS Hosting & Deployment Roadmap: Battery Management System (BMS)

> **Project Goal**: Host the pre-trained BMS Transformer model (`transformer(1).onnx`) on AWS EC2 as a REST API under the **AWS Free Tier ($0.00 cost)**, designed with a **pluggable architecture** so that future improved models can be swapped in with zero downtime and zero code changes.

---

## 📊 Live Progress Tracker

| Phase | Description | Status | Completion Date |
| :---: | :--- | :---: | :---: |
| **Phase 1** | Local API & Pluggable Architecture Preparation | 🟢 **Completed** | 20-10-2026 |
| **Phase 2** | AWS Account Setup, $0.01 Budget Alarm & EC2 Launch | 🟢 **Completed** | 20-10-2026 |
| **Phase 3** | EC2 Configuration, Dependency Setup & System Service | 🟢 **Completed** | 20-10-2026 |
| **Phase 4** | Live Public API & 5-Fleet Interactive Dashboard | 🟢 **Completed** | 20-10-2026 |
| **Phase 5** | NASA Benchmark Curves & Slide 8 SSM Comparison | 🟢 **Completed** | 20-10-2026 |
| **Phase 6** | Custom Domain & Let's Encrypt HTTPS Security | 🟢 **Completed** | 20-10-2026 |
*Legend: ⚪ Pending | 🟡 In Progress | 🟢 Completed*

---

## 🛡️ Critical AWS Free-Tier Guardrails (Keep Cost at $0.00)

1. **Always select `t2.micro` or `t3.micro`**:
   - Only these instance types are covered under the 750 free hours/month.
2. **Never change storage above 30 GB**:
   - The Free Tier provides up to 30 GB of General Purpose SSD (gp2/gp3) EBS storage. We will use the default 8 GB (plenty for Linux + Python).
3. **Never allocate Elastic IPs without attaching them**:
   - Unattached Elastic IPs incur small hourly fees. We will use the standard public IP provided automatically by AWS.
4. **Set Up a $0.01 Budget Alarm**:
   - In Phase 2, the very first thing we do in the console is set up an email notification if spending exceeds $0.01.

---

## 🏗️ Architecture Design (Model-Agnostic & Pluggable)

```
[ Client: Postman / Browser / ESP32 ]
                 │
                 │ HTTP POST /predict (JSON: Voltage, Current, Temperature)
                 ▼
[ AWS EC2 Instance: Ubuntu 24.04 LTS (t2.micro / Free Tier) ]
  ├── FastAPI Web Server (Uvicorn)
  ├── Input Validator & Cold-Start Buffer (auto-pads to 32 timesteps)
  ├── Normalization Layer (driven by config.json)
  ├── ONNX Runtime Inference Engine
  └── Model Artifact: transformer(1).onnx
                 │
                 ▼
[ Response JSON: { "soc_percent": 84.5, "soh_metric": 0.982, "status": "NORMAL" } ]
```

### Why This Architecture is Pluggable:
- The server does **not** hardcode any model layers or weights.
- Everything is managed via `config.json`:
  - Input names, dimensions, window size (32), feature names, and scaler parameters.
- When an updated model is created (e.g. `transformer_v2.onnx`):
  1. Drop the new file onto the server.
  2. Update the filename in `config.json`.
  3. Call `POST /reload` $\rightarrow$ The server loads the new model instantly without restarting!

---

## 📋 Detailed Phased Breakdown

### 🔹 Phase 1: Local API & Pluggable Architecture Preparation
- [x] Create `config.json` with model parameters and configurable scaler settings.
- [x] Build `app.py` using FastAPI and ONNX Runtime:
  - `GET /health`: Checks server and model health.
  - `GET /model/info`: Returns active model name, version, and input specs.
  - `POST /predict`: Handles 32-step window or single-reading streams with auto-buffering.
  - `POST /reload`: Hot-reloads updated model files dynamically.
- [x] Create `test_client.py` to simulate realistic battery data locally.
- [x] Verify local execution and ensure clean error handling.

### 🔹 Phase 2: AWS Console Onboarding & EC2 Instance Setup
- [x] Log in to AWS Management Console.
- [x] Configure AWS Free-Tier Zero-Spend Budget Alert ($0.01 threshold).
- [x] Select optimal AWS Region (e.g., `ap-south-1` Mumbai or `us-east-1` N. Virginia).
- [x] Create and download EC2 Key Pair (`bms-key.pem`).
- [x] Configure Security Group firewall rules:
  - Port 22 (SSH) - for remote terminal access.
  - Port 8000 (Custom TCP) - for public API access.
- [x] Launch `t2.micro` Ubuntu 24.04 LTS instance.

### 🔹 Phase 3: Server Configuration & Background Service
- [x] Connect to EC2 instance via SSH.
- [x] Install Python 3, pip, and required lightweight libraries (`fastapi`, `uvicorn`, `onnxruntime`, `numpy`, `pydantic`).
- [x] Transfer `transformer(1).onnx`, `config.json`, and `app.py` to EC2.
- [x] Configure Linux `systemd` background service (`bms-api.service`):
  - Ensures the API runs 24/7.
  - Automatically restarts if the server reboots.

### 🔹 Phase 4: Verification & Live Demo Testing
- [x] Test public EC2 API endpoint using Postman or Python test client:
  - `http://<EC2-PUBLIC-IP>:8000/docs` (Interactive Swagger UI).
  - `http://<EC2-PUBLIC-IP>:8000/predict` (Prediction test).
- [x] Verify inference latency (typically < 5ms).
- [x] Test cold-start buffering and anomaly error handling.

### 🔹 Phase 5: Future Model Swapping & College Presentation Guide
- [ ] Document the step-by-step procedure to swap the model when an updated version is trained.
- [ ] Prepare sample API test payloads and expected outputs for college submission.
- [ ] Document project architecture diagrams and cost-free maintenance guidelines.

---

## 🔬 NASA PCoE Dataset & 20-Battery Fleet Integration (Completed)
- **Dataset Ground Truth**: Integrated NASA Ames PCoE Lithium-ion battery dataset (B0005, B0006, B0007, B0018).
- **20-Battery Fleet Simulator**: Real-time fleet of 20 packs across 3 lifecycle stages (12 Healthy, 5 Caution, 3 Critical EOL).
- **Drill-Down Inspection**: Interactive modal displaying detailed 32-timestep sensor telemetry for any individual battery.
- **Scientific Benchmark Curves**:
  1. Capacity Fade & SOH Degradation vs Cycle Number (168 cycles).
  2. Dynamic Discharge Voltage profiles (Cycle 1 vs 50 vs 100 vs 160).
  3. Cell Surface Temperature Elevation curves under discharge.

---

## 🌟 Major Demonstration Update: 5 Fleets, Benchmarks & Dataset Ingestion
- **5 Complete Fleets (200 Total Packs)**:
  1. Fleet 1: Urban EV Taxis (35 packs &bull; NASA B0005)
  2. Fleet 2: Heavy Logistics Trucks (40 packs &bull; NASA B0006)
  3. Fleet 3: Grid Energy Storage Substation (45 packs &bull; NASA B0007)
  4. Fleet 4: Airport Ground Shuttles (30 packs &bull; NASA B0018)
  5. Fleet 5: Last-Mile Delivery Vans (50 packs &bull; Mixed NASA Benchmark)
- **Cell-Specific Scientific Analysis**: Interactive selector for NASA B0005, B0006, B0007, and B0018.
- **Slide 8 Empirical Benchmark**: Integrated Transformer vs. State-Space Model (SSM / Mamba) 4-panel comparison graphic and cross-dataset accuracy/latency matrix.
- **Custom Dataset Ingestion (Planned Feature Demo)**: UI Modal allowing drag & drop dataset registration into an automated AWS S3 telemetry pipeline.
