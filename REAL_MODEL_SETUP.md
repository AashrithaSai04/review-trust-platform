# Loading the Real Trained Model

Your API is currently running with **mock predictions** because Torch and Transformers are not installed in the `ml-service` environment. Follow these steps to load the real trained DistilBERT classifier.

## What Changed

✅ **New API Response Field**: All predictions now include `is_mock_prediction` (boolean)
  - `true` = using fallback mock model  
  - `false` = using real trained classifier

✅ **Updated Swagger Docs**: Example now shows realistic prediction (low fake_probability → high trust_score)

✅ **Improved Trust Score Calculation**: Formula is `trust_score = round((1 - fake_probability) * 100)`
  - Example: `fake_probability: 0.18` → `trust_score: 82` ✓

## Step 1: Install Torch and Transformers

Open a PowerShell terminal in your `ml-service` folder and run:

```powershell
cd "c:\Users\aashr\OneDrive\Desktop\Mini Project\review-trust-platform\ml-service"
.\venv\Scripts\python.exe -m pip install torch==2.1.1 transformers==4.38.0
```

**Expected time**: 5-15 minutes (large downloads: PyTorch ~800MB, Transformers ~200MB)

**Note**: If you get an error about older numpy, run:
```powershell
.\venv\Scripts\python.exe -m pip install --upgrade numpy
```

## Step 2: Verify Installation

```powershell
.\venv\Scripts\python.exe -c "import torch, transformers; print(f'Torch {torch.__version__}, Transformers {transformers.__version__}')"
```

Expected output: `Torch 2.1.1, Transformers 4.38.0`

## Step 3: Model Detection (Automatic)

The model service automatically looks for the trained model at:
1. `ml-pipeline/my_model/` (checked first)
2. `ml-pipeline/models/distilbert-review-classifier/` (fallback)

**Check what's available**:
```powershell
Get-ChildItem -Path "c:\Users\aashr\OneDrive\Desktop\Mini Project\review-trust-platform\ml-pipeline\models" -Recurse -Include config.json
```

If you see `config.json` files, models are ready.

## Step 4: Restart the API Server

Power cycle your Uvicorn server to reload:

```powershell
cd "c:\Users\aashr\OneDrive\Desktop\Mini Project\review-trust-platform\ml-service"
.\venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Watch the logs** for this confirmation:
```
INFO:     Loading tokenizer from c:\Users\aashr\OneDrive\Desktop\Mini Project\review-trust-platform\ml-pipeline\my_model
INFO:     Loading model from c:\Users\aashr\OneDrive\Desktop\Mini Project\review-trust-platform\ml-pipeline\my_model
INFO:     Model loaded on cpu
```

If you still see `Using mock predictions`, check that the model path exists and contains `config.json`.

## Step 5: Test the Real Model

Make a prediction request:

```powershell
$headers = @{ "Content-Type" = "application/json" }
$body = @{ "text" = "This product is absolutely amazing and works perfectly!" } | ConvertTo-Json
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/predict" -Method POST -Headers $headers -Body $body | Select-Object -ExpandProperty Content | ConvertFrom-Json
```

**Compare with and without the real model**:
- **With mock**: `is_mock_prediction: true`
- **With real model**: `is_mock_prediction: false`

## Troubleshooting

### Model not loading?
1. Check model files exist: `ls ml-pipeline/my_model/config.json`
2. Verify Torch/Transformers are installed in the correct venv
3. Check server logs for specific error messages

### "Cannot allocate memory for GPU"?
The model defaults to CPU, which is slower but works on any machine. GPU is optional.

### Want to use GPU instead?
Set the `DEVICE` environment variable before starting the server:
```powershell
$env:DEVICE = "cuda"
.\venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Configuration

You can override the model path using the `MODEL_DIR` environment variable:

```powershell
$env:MODEL_DIR = "c:\path\to\custom\model"
.\venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Response Comparison

### Mock Mode (current)
```json
{
  "text": "Great product!",
  "fake_probability": 0.45,
  "trust_score": 55,
  "risk_level": "Medium Risk",
  "is_mock_prediction": true,  // ← FLAG: using fallback
  "important_words": [...],
  "prediction_id": "..."
}
```

### Real Model Mode (after installing Torch)
```json
{
  "text": "Great product!",
  "fake_probability": 0.12,
  "trust_score": 88,
  "risk_level": "Low Risk",
  "is_mock_prediction": false,  // ← FLAG: using trained classifier
  "important_words": [...],
  "prediction_id": "..."
}
```

The `is_mock_prediction` flag makes it obvious in Swagger docs (`/docs`) and in your frontend UI which predictions are real vs. fallback.
