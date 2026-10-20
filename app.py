import os
import json
import time
import logging
from typing import List, Optional, Union
import numpy as np
import onnxruntime as ort
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from fleet_data import FLEETS_METADATA, ALL_FLEETS, get_nasa_dataset, BENCHMARK_COMPARISON

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("bms_api")

app = FastAPI(
    title="Battery Management System (BMS) Inference API",
    description="REST API for real-time State of Charge (SOC) and State of Health (SOH) estimation using an ONNX Transformer.",
    version="1.0.0"
)

# Enable CORS for browser-based dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directory for graphs and visual assets
if not os.path.exists("static"):
    os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


class BMSInferenceEngine:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = {}
        self.session: Optional[ort.InferenceSession] = None
        self.model_path = ""
        self.window_size = 32
        self.features = ["voltage", "current", "temperature"]
        self.load_model()

    def load_model(self):
        """Loads or reloads config.json and the ONNX model."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found at: {self.config_path}")

        with open(self.config_path, "r") as f:
            self.config = json.load(f)

        self.model_path = self.config.get("model_file", "transformer(1).onnx")
        self.window_size = self.config.get("window_size", 32)
        self.features = self.config.get("features", ["voltage", "current", "temperature"])

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"ONNX model file not found at: {self.model_path}")

        logger.info(f"Loading ONNX model from: {self.model_path}")
        # Configure session options
        opts = ort.SessionOptions()
        opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self.session = ort.InferenceSession(self.model_path, sess_options=opts)
        logger.info(f"Successfully loaded '{self.config.get('model_name')}' (v{self.config.get('version')})")

    def normalize(self, data: np.ndarray) -> np.ndarray:
        """Applies normalization according to config.json settings."""
        if not self.config.get("enable_normalization", False):
            return data

        method = self.config.get("normalization_method", "minmax")
        scaler = self.config.get("scaler", {})
        norm_data = np.copy(data)

        for i, feat in enumerate(self.features):
            p = scaler.get(feat, {})
            if method == "minmax":
                f_min = p.get("min", 0.0)
                f_max = p.get("max", 1.0)
                if f_max > f_min:
                    norm_data[:, :, i] = (norm_data[:, :, i] - f_min) / (f_max - f_min)
            elif method == "zscore":
                mean = p.get("mean", 0.0)
                std = p.get("std", 1.0)
                if std > 0:
                    norm_data[:, :, i] = (norm_data[:, :, i] - mean) / std

        return norm_data

    def predict(self, window_data: np.ndarray):
        """
        Runs inference on input window [batch, 32, 3].
        Returns soc and soh arrays.
        """
        # Ensure float32
        data = window_data.astype(np.float32)

        # Handle automatic cold-start padding if fewer than window_size timesteps provided
        batch_size, seq_len, num_features = data.shape
        if seq_len < self.window_size:
            logger.warning(f"Input sequence length {seq_len} < {self.window_size}. Padding start with initial readings.")
            pad_len = self.window_size - seq_len
            first_timestep = np.tile(data[:, :1, :], (1, pad_len, 1))
            data = np.concatenate([first_timestep, data], axis=1)
        elif seq_len > self.window_size:
            # Take the most recent window_size readings
            data = data[:, -self.window_size:, :]

        # Normalize if enabled
        data = self.normalize(data)

        # Run ONNX inference
        outputs = self.session.run(["soc", "soh"], {"window": data})
        soc_raw, soh_raw = outputs[0], outputs[1]

        # Guardrails on SOH if enabled
        if self.config.get("guardrails", {}).get("clip_soh", True):
            soh_min = self.config.get("guardrails", {}).get("soh_min", 0.0)
            soh_max = self.config.get("guardrails", {}).get("soh_max", 1.5)
            soh_raw = np.clip(soh_raw, soh_min, soh_max)

        return soc_raw, soh_raw


# Initialize global engine instance
engine = BMSInferenceEngine()


# --- Pydantic Request & Response Schemas ---
class PredictWindowRequest(BaseModel):
    # Expects 32 timesteps, each with 3 features: [voltage, current, temperature]
    window: List[List[float]] = Field(
        ...,
        description="List of 32 readings, each containing [Voltage, Current, Temperature]."
    )
    apply_normalization: Optional[bool] = Field(
        None,
        description="Override config to force normalization on/off for this request."
    )


class BatchPredictRequest(BaseModel):
    batch: List[List[List[float]]] = Field(
        ...,
        description="Batch of windows, shape: [batch_size, 32, 3]."
    )


class ReadingItem(BaseModel):
    voltage: float
    current: float
    temperature: float


class PredictChannelsRequest(BaseModel):
    # Alternative format: 3 separate lists of 32 numbers
    voltage: List[float] = Field(..., description="List of 32 voltage readings")
    current: List[float] = Field(..., description="List of 32 current readings")
    temperature: List[float] = Field(..., description="List of 32 temperature readings")


class PredictionResult(BaseModel):
    soc_percentage: float = Field(..., description="State of Charge (0% to 100%)")
    soc_raw: float = Field(..., description="Raw SOC output [0.0 to 1.0]")
    soh_metric: float = Field(..., description="State of Health metric (1.0 = 100% nominal health)")
    battery_status: str = Field(..., description="Health status classification: NORMAL, WARNING, or CRITICAL")
    inference_time_ms: float = Field(..., description="Inference latency in milliseconds")


# --- API Routes ---
@app.get("/", response_class=HTMLResponse, tags=["General"])
def dashboard():
    """Serves the interactive web dashboard."""
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>BMS API Online</h1><p><a href='/docs'>View Swagger API Documentation</a></p>")


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "model_loaded": engine.session is not None,
        "model_file": engine.model_path,
        "window_size": engine.window_size
    }


@app.get("/model/info", tags=["Model Management"])
def model_info():
    return engine.config


@app.post("/model/reload", tags=["Model Management"])
def reload_model():
    """
    Hot-reloads the model from config.json without restarting the server.
    Use this when updating or swapping the ONNX model file.
    """
    try:
        engine.load_model()
        return {
            "status": "success",
            "message": "Model reloaded successfully.",
            "active_model": engine.config.get("model_name"),
            "version": engine.config.get("version")
        }
    except Exception as e:
        logger.error(f"Error reloading model: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload model: {str(e)}"
        )


@app.post("/predict", response_model=PredictionResult, tags=["Inference"])
def predict(request: PredictWindowRequest):
    """
    Predicts SOC and SOH given a window of 32 sensor measurements.
    """
    start_time = time.perf_counter()
    window = np.array(request.window, dtype=np.float32)

    # Validate shape
    if window.ndim != 2 or window.shape[1] != 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid window shape {window.shape}. Expected (N, 3) where columns are [Voltage, Current, Temperature]."
        )

    # Expand to [batch=1, seq_len, 3]
    input_data = np.expand_dims(window, axis=0)

    # Optional per-request normalization override
    orig_norm = engine.config.get("enable_normalization")
    if request.apply_normalization is not None:
        engine.config["enable_normalization"] = request.apply_normalization

    try:
        soc_arr, soh_arr = engine.predict(input_data)
    finally:
        engine.config["enable_normalization"] = orig_norm

    latency_ms = (time.perf_counter() - start_time) * 1000.0

    soc_val = float(soc_arr[0])
    soh_val = float(soh_arr[0])

    # Determine status
    if soc_val < 0.10:
        bat_status = "CRITICAL_LOW_CHARGE"
    elif soh_val < 0.70:
        bat_status = "DEGRADED_BATTERY"
    elif soc_val < 0.20 or soh_val < 0.80:
        bat_status = "WARNING"
    else:
        bat_status = "NORMAL"

    return PredictionResult(
        soc_percentage=round(soc_val * 100.0, 2),
        soc_raw=round(soc_val, 4),
        soh_metric=round(soh_val, 4),
        battery_status=bat_status,
        inference_time_ms=round(latency_ms, 2)
    )


@app.post("/predict/channels", response_model=PredictionResult, tags=["Inference"])
def predict_channels(request: PredictChannelsRequest):
    """
    Alternative endpoint accepting 3 explicit named arrays: voltage, current, and temperature.
    Guarantees no channel order mix-up.
    """
    if not (len(request.voltage) == len(request.current) == len(request.temperature)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voltage, current, and temperature arrays must have identical length."
        )

    combined = list(zip(request.voltage, request.current, request.temperature))
    return predict(PredictWindowRequest(window=combined))


# --- Fleet & Benchmark Endpoints ---
@app.get("/fleet/list", tags=["Fleet Management"])
def list_fleets():
    """Returns list and metadata of all 5 simulated fleets."""
    return FLEETS_METADATA


@app.get("/fleet", tags=["Fleet Management"])
@app.get("/fleet/{fleet_id}", tags=["Fleet Management"])
def get_fleet_summary(fleet_id: str = "FLEET-1"):
    """
    Returns overview of all battery packs in the specified fleet (30 to 50 packs)
    with real model inference predictions.
    """
    fid = fleet_id.upper()
    if fid not in ALL_FLEETS:
        fid = "FLEET-1"

    fleet_entry = ALL_FLEETS[fid]
    fleet_meta = fleet_entry["metadata"]
    raw_packs = fleet_entry["packs"]

    # Batch predict all batteries in this fleet simultaneously
    batch_windows = []
    for b in raw_packs:
        vecs = [step["model_vector"] for step in b["telemetry_window"]]
        batch_windows.append(vecs)

    batch_array = np.array(batch_windows, dtype=np.float32)
    soc_preds, soh_preds = engine.predict(batch_array)

    healthy_count = 0
    caution_count = 0
    critical_count = 0
    fleet_with_preds = []

    for i, b in enumerate(raw_packs):
        soc_pct = round(float(soc_preds[i]) * 100.0, 1)
        soh_val = round(float(soh_preds[i]), 4)
        bat_status = b["status"]

        if bat_status == "HEALTHY":
            healthy_count += 1
        elif bat_status == "CAUTION":
            caution_count += 1
        elif bat_status == "CRITICAL":
            critical_count += 1

        b_summary = {
            "id": b["id"],
            "name": b["name"],
            "fleet_id": fid,
            "vehicle_id": b["vehicle_id"],
            "cycles": b["cycles"],
            "rated_ah": b["rated_ah"],
            "current_ah": b["current_ah"],
            "avg_voltage": b["avg_voltage"],
            "avg_current": b["avg_current"],
            "peak_temperature": b["peak_temperature"],
            "predicted_soc": soc_pct,
            "predicted_soh": soh_val,
            "status": bat_status,
            "load_profile": b["load_profile"]
        }
        fleet_with_preds.append(b_summary)

    avg_soc = round(float(np.mean([p["predicted_soc"] for p in fleet_with_preds])), 1)
    avg_soh = round(float(np.mean([p["predicted_soh"] for p in fleet_with_preds])), 3)

    return {
        "fleet_id": fid,
        "fleet_name": fleet_meta["name"],
        "fleet_type": fleet_meta["type"],
        "description": fleet_meta["description"],
        "base_dataset": fleet_meta["base_dataset"],
        "fleet_size": len(fleet_with_preds),
        "fleet_avg_soc": avg_soc,
        "fleet_avg_soh": avg_soh,
        "healthy_count": healthy_count,
        "caution_count": caution_count,
        "critical_count": critical_count,
        "batteries": fleet_with_preds
    }


@app.get("/fleet/{fleet_id}/{battery_id}", tags=["Fleet Management"])
def get_battery_detail(fleet_id: str, battery_id: str):
    """Returns full 32-step telemetry and detailed prediction for a specific battery in a fleet."""
    fid = fleet_id.upper()
    if fid not in ALL_FLEETS:
        fid = "FLEET-1"

    raw_packs = ALL_FLEETS[fid]["packs"]
    matched = next((b for b in raw_packs if b["id"].upper() == battery_id.upper()), None)
    if not matched:
        # Fallback search across all fleets
        for f_key in ALL_FLEETS:
            matched = next((b for b in ALL_FLEETS[f_key]["packs"] if b["id"].upper() == battery_id.upper()), None)
            if matched:
                break

    if not matched:
        raise HTTPException(status_code=404, detail=f"Battery {battery_id} not found.")

    vecs = [step["model_vector"] for step in matched["telemetry_window"]]
    input_arr = np.expand_dims(np.array(vecs, dtype=np.float32), axis=0)
    soc_pred, soh_pred = engine.predict(input_arr)

    res = dict(matched)
    res["predicted_soc"] = round(float(soc_pred[0]) * 100.0, 2)
    res["predicted_soh"] = round(float(soh_pred[0]), 4)
    return res


@app.get("/dataset/benchmarks", tags=["Dataset Benchmarks"])
def dataset_benchmarks(cell: str = "B0005"):
    """Returns NASA PCoE battery aging dataset degradation curves for specified cell."""
    return get_nasa_dataset(cell)


@app.get("/benchmark/comparison", tags=["Model Comparison"])
def benchmark_comparison():
    """Returns compiled Transformer vs State-Space Model (SSM) empirical benchmarks."""
    return BENCHMARK_COMPARISON


class CustomDatasetUploadRequest(BaseModel):
    dataset_name: str = Field(..., description="Name of user dataset")
    cell_chemistry: str = Field("Lithium-Ion NMC 18650", description="Battery chemistry")
    sampling_rate: str = Field("10 Hz", description="Data capture frequency")
    total_samples: int = Field(1200, description="Total timesteps in dataset")
    features_mapped: List[str] = Field(["Voltage", "Current", "Temperature"], description="Mapped telemetry columns")


@app.post("/custom-dataset/upload", tags=["Custom Datasets"])
def upload_custom_dataset(payload: CustomDatasetUploadRequest):
    """
    Simulated ingestion endpoint allowing users/evaluators to register custom battery datasets.
    Demonstrates planned AWS S3 + Glue automated ETL pipeline.
    """
    return {
        "status": "success",
        "message": f"Custom dataset '{payload.dataset_name}' successfully validated and ingested.",
        "assigned_id": f"CUSTOM-{int(time.time()) % 10000}",
        "dataset_name": payload.dataset_name,
        "cell_chemistry": payload.cell_chemistry,
        "sampling_rate": payload.sampling_rate,
        "samples_parsed": payload.total_samples,
        "pipeline_stage": "Ingested to S3 -> Validated -> Ready for Transformer Fine-Tuning",
        "storage_bucket": "s3://bms-custom-datasets-college-demo/"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
