---
name: test-quality
description: Evaluate generated track quality against BMAsia zone-specific genre standards
user_invocable: true
---

# /test-quality

Evaluate generated audio quality against BMAsia's zone-type requirements.

## Usage
```
/test-quality outputs/lobby-ambient-01.mp3
/test-quality outputs/hotel-lobby/ --genre lounge
/test-quality --run-matrix presets/genre-test-matrix.json
```

## Genre Matrix (BMAsia Zone Types)

| Zone Type | Genres | BPM | Duration | Key Traits |
|-----------|--------|-----|----------|------------|
| Hotel Lobby / Lounge | Ambient, Jazz, Chill, Bossa Nova | 60-100 | 180-300s | Soft, non-intrusive, elegant |
| Restaurant / Dinner | Jazz, Classical, Acoustic, Bossa | 70-110 | 180-300s | Warm, conversational-friendly |
| Fashion Retail | Pop, Indie, Electronic, Funk | 100-140 | 120-240s | Trendy, upbeat, contemporary |
| Spa / Wellness | Ambient, New Age, Nature, Meditation | 50-80 | 240-600s | Calming, spacious, meditative |
| QSR / Fast Casual | Pop, EDM, Hip-Hop, Dance | 110-150 | 120-180s | Energetic, youthful, fun |
| Bar / Nightlife | Deep House, Lounge, R&B, Jazz | 100-130 | 180-300s | Sophisticated, groove, mood |
| Elevator / On-Hold | Light Jazz, Easy Listening, Ambient | 70-100 | 120-240s | Inoffensive, background |

## Quality Dimensions

1. **Audio Fidelity** — No artifacts, clipping, distortion, or unexpected silence
2. **Genre Adherence** — Matches the requested style description
3. **Tempo Accuracy** — BPM within 10% of requested value
4. **Duration Accuracy** — Within 5% of requested duration
5. **Structural Coherence** — Has intro, body, natural ending (no abrupt cuts)
6. **Loop Compatibility** — Can transition smoothly for continuous background play
7. **Vocal Quality** — If vocals present: clear, on-pitch, intelligible lyrics
8. **Mix Balance** — No single instrument overwhelming the mix

## Evaluation Workflow

1. **File Validation**
   - Verify file exists, is not empty, correct format
   - Check sample rate (should be 48kHz) and channels (stereo)

2. **Automated Checks**
   - Duration vs target (pass if within 5%)
   - Silence detection (flag if >3s continuous silence)
   - Clipping detection (flag if samples hit max amplitude)
   - Basic spectral analysis (flag if no content above 8kHz — suggests low quality)

3. **Manual Listening Evaluation** (human reviewer)
   - Rate each quality dimension 1-5
   - Overall verdict: APPROVE / NEEDS_REVISION / REJECT
   - Notes for rejected tracks (what went wrong)

4. **Report Generation**

## Report Format

```json
{
  "track": "lobby-ambient-01.mp3",
  "zone_type": "hotel_lobby",
  "verdict": "APPROVE",
  "automated_checks": {
    "duration_target": 180,
    "duration_actual": 182.4,
    "duration_pass": true,
    "silence_detected": false,
    "clipping_detected": false,
    "sample_rate": 48000,
    "channels": 2,
    "file_size_mb": 4.3
  },
  "manual_scores": {
    "audio_fidelity": 4,
    "genre_adherence": 5,
    "tempo_accuracy": 4,
    "structural_coherence": 4,
    "loop_compatibility": 3,
    "mix_balance": 4
  },
  "overall_score": 4.0,
  "notes": ""
}
```

## A/B Comparison vs Mureka

For evaluating whether ACE-Step can replace Mureka:
1. Select 5 representative Mureka tracks per zone type
2. Generate ACE-Step equivalents with matched genre/tempo/duration
3. Blind listening test: team rates without knowing source
4. Compare scores per dimension
5. Decision threshold: ACE-Step must score within 80% of Mureka average

## GPU REQUIRED
Audio generation requires a running ACE-Step server. Automated analysis can run locally with Python audio libraries (librosa, soundfile).
