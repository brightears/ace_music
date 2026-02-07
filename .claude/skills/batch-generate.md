---
name: batch-generate
description: Batch generate multiple tracks from a JSON/YAML preset configuration file
user_invocable: true
---

# /batch-generate

Generate multiple tracks from a preset file. Designed for producing zone-specific background music at scale.

## Usage
```
/batch-generate presets/hotel-lobby.json
/batch-generate presets/retail.json --limit 10 --dry-run
/batch-generate presets/full-catalog.json --concurrency 4
```

## Preset File Format

```json
{
  "name": "Hotel Lobby Background Music",
  "description": "Ambient, non-intrusive tracks for hotel lobby zones",
  "default_params": {
    "duration": 180,
    "model": "turbo",
    "format": "mp3",
    "instrumental": true,
    "language": "en"
  },
  "tracks": [
    {
      "id": "lobby-ambient-01",
      "caption": "smooth ambient lounge, soft piano, gentle strings, warm pads",
      "bpm": 75,
      "key": "C major"
    },
    {
      "id": "lobby-jazz-01",
      "caption": "laid-back jazz lounge, saxophone, upright bass, brushed drums",
      "bpm": 95,
      "duration": 240
    },
    {
      "id": "lobby-classical-01",
      "caption": "light classical, string quartet, elegant, refined",
      "bpm": 80
    }
  ]
}
```

Track-level values override `default_params`.

## Options

| Option | Default | Description |
|--------|---------|-------------|
| preset | required | Path to preset JSON file |
| --limit | all | Max tracks to generate |
| --concurrency | 4 | Simultaneous API submissions |
| --output-dir | outputs/ | Output directory |
| --dry-run | false | Validate preset without generating |
| --retry | 2 | Retry count for failed tracks |
| --resume | false | Skip tracks that already exist in output-dir |

## Workflow

1. Parse and validate preset file
2. Merge each track's params with default_params
3. If `--dry-run`: report track count, estimated time, estimated cost, then exit
4. Submit tracks via `/release_task` (respecting --concurrency limit)
5. Poll all task IDs via `/query_result` (batch query supported)
6. Download completed audio files
7. Name files: `{output-dir}/{preset-name}/{track-id}.{format}`
8. Generate batch report: `{output-dir}/{preset-name}/batch-report.json`

## Batch Report Format

```json
{
  "preset": "Hotel Lobby Background Music",
  "generated_at": "2026-02-07T15:30:00Z",
  "total_tracks": 25,
  "succeeded": 23,
  "failed": 2,
  "total_duration_seconds": 4320,
  "total_file_size_mb": 98.5,
  "total_generation_time_seconds": 145,
  "avg_time_per_track_seconds": 5.8,
  "failed_tracks": ["lobby-world-04", "lobby-ambient-12"],
  "tracks": [...]
}
```

## GPU REQUIRED
Requires a running ACE-Step API server. Use `/setup-cloud` first.

## Cost Estimation
- RTX 3090: ~6s/track → 600 tracks/hour → ~$0.50/hour = ~$0.001/track
- A100: ~2s/track → 1800 tracks/hour → ~$2.00/hour = ~$0.001/track
- Compare: Mureka = ~$0.057/track (57x more expensive)
