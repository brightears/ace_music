---
name: generate-track
description: Generate a single music track using ACE-Step v1.5 API with all available parameters
user_invocable: true
---

# /generate-track

Generate a single music track via the ACE-Step REST API.

## Usage
```
/generate-track "ambient lounge jazz, soft piano, gentle strings" --duration 120
/generate-track "upbeat pop" --lyrics "[verse]\nHello world..." --duration 90 --bpm 120
/generate-track "spa wellness, nature sounds, meditation" --duration 300 --instrumental
```

## Parameters

| Parameter | Required | Default | Range/Options | Description |
|-----------|----------|---------|---------------|-------------|
| caption | Yes | -- | free text | Style/genre description |
| --lyrics | No | "" | text with tags | Lyrics with [verse]/[chorus]/[bridge] tags |
| --duration | No | 120 | 10-600 seconds | Track duration |
| --bpm | No | auto | 30-280 | Tempo (60-180 most stable) |
| --key | No | auto | e.g. "C major" | Musical key (C,G,D,Am,Em most reliable) |
| --time-sig | No | "4/4" | e.g. "3/4","6/8" | Time signature |
| --model | No | turbo | turbo/sft/base | DiT model variant |
| --instrumental | No | false | flag | Instrumental only, no vocals |
| --language | No | "en" | ISO code | Vocal language |
| --format | No | "mp3" | mp3/wav/flac | Output format |
| --seed | No | random | integer | Reproducibility seed |
| --batch | No | 1 | 1-8 | Number of variations to generate |
| --guidance | No | 7.0 | 1.0-15.0 | Guidance scale (sft/base only) |
| --thinking | No | false | flag | Enable LM chain-of-thought |

## Workflow

1. Load `ACESTEP_API_URL` and `ACESTEP_API_KEY` from `.env`
2. Validate parameters against allowed ranges
3. Build request payload:
   ```json
   {
     "prompt": "<caption>",
     "lyrics": "<lyrics>",
     "audio_duration": <duration>,
     "bpm": <bpm>,
     "seed": <seed>,
     "batch_size": <batch>,
     "audio_format": "<format>",
     "thinking": <thinking>
   }
   ```
4. POST to `{API_URL}/release_task`
5. Poll `{API_URL}/query_result` every 2s until status=1 or status=2
6. On success: GET `{API_URL}/v1/audio?path=<result_path>`
7. Save to `outputs/<timestamp>-<caption-slug>.<format>`
8. Report: filename, duration, file size, generation time, seed used

## GPU REQUIRED
This skill requires a running ACE-Step API server on a GPU machine. Use `/setup-cloud` first if no server is available.

## Error Handling
- Connection refused → Check ACESTEP_API_URL, is the server running?
- 401 Unauthorized → Check ACESTEP_API_KEY
- Queue full (HTTP 429) → Wait and retry, or reduce batch size
- Generation failed (status=2) → Log error, suggest shorter duration or different seed
- Timeout (>5 min) → Likely OOM, suggest reducing duration or batch size
