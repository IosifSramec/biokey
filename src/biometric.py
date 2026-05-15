import numpy as np
import neurokit2 as nk
import wfdb
from scipy.signal import butter, filtfilt, resample


STRESS_LEVELS = ['rest', 'light', 'moderate', 'heavy', 'cognitive']

HR_THRESHOLDS = {
    'rest':     (0,   90),
    'light':    (90,  110),
    'moderate': (110, 130),
    'heavy':    (130, 160),
    'cognitive':(160, 220),
}


def load_subject(record_path):
    record = wfdb.rdrecord(record_path)
    names = [s.strip().rstrip(',') for s in record.sig_name]
    idx = {name: i for i, name in enumerate(names)}
    ecg = record.p_signal[:, idx.get('II', idx.get('ECG', 0))]
    resp = record.p_signal[:, idx['RESP']] if 'RESP' in idx else None
    return ecg, resp, record.fs


def extract_ecg_features(ecg, fs, window_sec=60):
    samples = min(window_sec * fs, len(ecg))
    ecg_segment = ecg[:samples]

    ecg_clean = nk.ecg_clean(ecg_segment, sampling_rate=fs)
    _, info = nk.ecg_peaks(ecg_clean, sampling_rate=fs)
    r_peaks = info['ECG_R_Peaks']

    if len(r_peaks) < 5:
        raise ValueError("Not enough R-peaks detected")

    rr = np.diff(r_peaks) / fs * 1000

    features = np.array([
        np.mean(rr),
        np.std(rr),
        np.min(rr),
        np.max(rr),
        np.median(rr),
        np.sqrt(np.mean(np.diff(rr) ** 2)),        # RMSSD
        np.sum(np.abs(np.diff(rr)) > 50) / len(rr), # pNN50
    ])
    return features


def extract_resp_features(resp, fs, window_sec=60):
    samples = min(window_sec * fs, len(resp))
    resp_segment = resp[:samples]

    b, a = butter(3, [0.1, 0.5], btype='band', fs=fs)
    resp_clean = filtfilt(b, a, resp_segment)

    peaks = nk.signal_findpeaks(resp_clean, relative_height_min=0.3)['Peaks']

    if len(peaks) < 3:
        raise ValueError("Not enough breath cycles detected")

    breath_intervals = np.diff(peaks) / fs * 1000

    features = np.array([
        np.mean(breath_intervals),
        np.std(breath_intervals),
        np.min(breath_intervals),
        np.max(breath_intervals),
        np.mean(resp_clean),
        np.std(resp_clean),
        np.max(resp_clean) - np.min(resp_clean),
    ])
    return features


def extract_biometric_vector(record_path, window_sec=60):
    ecg, resp, fs = load_subject(record_path)
    ecg_feat = extract_ecg_features(ecg, fs, window_sec)

    if resp is not None:
        resp_feat = extract_resp_features(resp, fs, window_sec)
    else:
        # Derive pseudo-respiration features from ECG HRV (RSA)
        resp_feat = _derive_resp_from_ecg(ecg_feat)

    return np.concatenate([ecg_feat, resp_feat])


def _derive_resp_from_ecg(ecg_features):
    """Estimate respiration features from ECG features using RSA relationship."""
    rr_mean = ecg_features[0]
    rr_std = ecg_features[1]
    resp_rate_ms = rr_mean * 4.5  # typical RSA ratio
    return np.array([
        resp_rate_ms,
        rr_std * 3.2,
        resp_rate_ms * 0.7,
        resp_rate_ms * 1.4,
        0.0,
        rr_std * 0.08,
        rr_std * 0.15,
    ])


PHASE_POSITIONS = {
    'rest':      0.0,
    'light':     0.15,
    'moderate':  0.35,
    'heavy':     0.55,
    'cognitive': 0.75,
}


def get_ecg_segment_for_level(level, bidmc_path, stdb_path, seconds=15):
    """Return raw ECG segment and fs for a given stress level — used for preview."""
    if level == 'rest':
        ecg, _, fs = load_subject(bidmc_path)
        segment = ecg[:seconds * fs]
    else:
        ecg, _, fs = load_subject(stdb_path)
        total = len(ecg)
        start = int(total * PHASE_POSITIONS[level])
        segment = ecg[start:start + seconds * fs]

    # Remove DC offset so baseline sits at 0
    segment = segment - np.mean(segment)
    return segment, fs


def extract_stress_templates(stdb_record_path, bidmc_record_path):
    """
    Extract 5 biometric templates at different stress levels.
    Uses stdb for stress phases and bidmc for rest+respiration baseline.
    """
    # Load stress ECG (no respiration)
    ecg_stress, _, fs_stress = load_subject(stdb_record_path)

    # Load rest ECG + respiration
    ecg_rest, resp_rest, fs_rest = load_subject(bidmc_record_path)

    templates = {}
    window = 60  # seconds per template

    # REST — from bidmc (calm, has respiration)
    ecg_feat = extract_ecg_features(ecg_rest, fs_rest, window)
    resp_feat = extract_resp_features(resp_rest, fs_rest, window)
    templates['rest'] = np.concatenate([ecg_feat, resp_feat])

    # Segment stdb into stress phases based on position in recording
    # Treadmill test: ramps up over ~20 min then recovery
    total_samples = len(ecg_stress)
    phase_starts = {
        'light':    int(total_samples * 0.15),
        'moderate': int(total_samples * 0.35),
        'heavy':    int(total_samples * 0.55),
        'cognitive': int(total_samples * 0.75),
    }

    for level, start in phase_starts.items():
        end = start + window * fs_stress
        ecg_window = ecg_stress[start:end]
        ecg_feat = extract_ecg_features(ecg_window, fs_stress, window)
        resp_feat = _derive_resp_from_ecg(ecg_feat)
        templates[level] = np.concatenate([ecg_feat, resp_feat])

    return templates


def get_current_hr(ecg, fs, window_sec=10):
    """Estimate current heart rate from short ECG window."""
    samples = min(window_sec * fs, len(ecg))
    ecg_clean = nk.ecg_clean(ecg[:samples], sampling_rate=fs)
    _, info = nk.ecg_peaks(ecg_clean, sampling_rate=fs)
    r_peaks = info['ECG_R_Peaks']
    if len(r_peaks) < 2:
        return 70
    rr_mean = np.mean(np.diff(r_peaks)) / fs
    return int(60 / rr_mean)
