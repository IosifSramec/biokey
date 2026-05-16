# BioKey — Biometric Cryptographic Authentication for Drone Operators

> **Your heartbeat is the only key that can unlock the drone.**

Built at HackTM 2026 — Defence track.

## What it does

BioKey derives an AES-256-GCM encryption key directly from an operator's ECG and respiration biometrics, combined with a PIN as a mandatory second factor. The encrypted payload (terrain navigation database) can only be decrypted by the enrolled operator — at any physiological state.

### The problem

Authentication systems fail precisely when the stakes are highest. Passwords are coerced or forgotten under stress. Smart cards are lost or stolen. Biometric systems enrolled at rest collapse the moment the operator's physiology changes. And if the device is captured, all onboard data is immediately accessible.

### The solution

**Multi-template stress enrollment** — the operator undergoes a treadmill-style stress test before deployment. BioKey captures ECG + respiration templates at 5 physiological states:

| Level | HR range | Source |
|-------|----------|--------|
| Rest | 60–90 bpm | BIDMC dataset |
| Light | 90–110 bpm | STDB treadmill |
| Moderate | 110–130 bpm | STDB treadmill |
| Heavy | 130–160 bpm | STDB treadmill |
| Cognitive | 80–100 bpm | STDB treadmill |

Each template independently wraps the same AES-256 key via HKDF. At authentication, the system finds the nearest matching template and unwraps the key — transparent to the operator regardless of current stress level.

## Architecture

```
[Operator ECG + Resp] → [17 biometric features]
                                ↓
                    [HKDF(seed, salt=SHA256(PIN)) × 5 levels]
                                ↓
                    [AES-256-GCM key wrapping]
                                ↓
                    [Terrain DB encrypted at rest]

Authentication:
[Live ECG + PIN] → [feature extraction] → [cosine + proximity similarity]
                                                    ↓
                                       [best template match > 0.90]
                                                    ↓
                                       [key unwrap → DB decrypt]
```

## Biometric features (17 total)

**ECG — time domain (7):** RR mean, std, min, max, median, RMSSD, pNN50

**ECG — nonlinear + frequency (3):** SD1, SD2 (Poincaré), LF/HF ratio

**Respiration (7):** breath interval mean, std, min, max, signal mean, std, range

## Security properties

- **Captured hardware**: terrain DB is ciphertext without the operator's biometric signature
- **Wrong operator**: similarity < 0.90 → key unwrap fails → DB stays encrypted
- **Correct biometrics, wrong PIN**: HKDF salt mismatch → cryptographic failure
- **Stress invariance**: 5 templates cover the full physiological range of field operations
- **Key never stored**: derived fresh from biometrics + PIN on every authentication

## Stack

- `neurokit2` — ECG signal processing, R-peak detection
- `wfdb` — PhysioNet record loading
- `cryptography` — AES-256-GCM, HKDF (SHA-256)
- `scipy` — respiration signal filtering
- `streamlit` + `plotly` — UI

## Data

ECG recordings from [PhysioNet](https://physionet.org/):
- **BIDMC PPG and Respiration Dataset** — resting ECG + respiration (125 Hz)
- **MIT-BIH Stress Test Database** — treadmill stress ECG (360 Hz)

## Run

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Terminal demo (no UI):
```bash
python -m src.demo
```
