# Golden Circle — 5s quiz-show reveal (KBC-style, no currency symbol)

- `Golden_Circle_5s_16x9.mp4`: 1920×1080, 30fps, 5.0s, with sound
- `Golden_Circle_5s_1x1.mp4`: 1080×1080 square for social

## Timeline
| Time | Beat |
|---|---|
| 0–1.3s | Light streaks converge on a glowing core (riser whoosh) |
| 0.5–1.9s | Gold rings draw in, spinning in alternating directions; segmented ring, tick marks, dots, spokes, diamond studs (lock-in hit) |
| 1.35–2s | Eight-point gold star pops in the blue centre disc where the ₹ would be; gold sparks burst out (bell shimmer) |
| 2.5–3.6s | Specular light sweep across the emblem + lens-flare glints (sparkle ticks) |
| 4.05s | Big flash / flare hit (impact + chord), then hold on the circle |

## Editing / re-rendering
`source/index.html` is the whole animation as a pure function `render(t)`; open it in a browser for a live looping preview.
- Stills: `node source/cap.js stills 1920 1080 1,2.9,4.05`
- Video: `FFMPEG=/path/to/ffmpeg node source/cap.js video 1920 1080 out.mp4` (needs Playwright + ffmpeg with libx264)
- Sound: `python3 source/audio.py` → `soundtrack.wav` (100% synthesized, royalty-free)
- Mux: `ffmpeg -i out.mp4 -i soundtrack.wav -c:v copy -c:a aac -shortest final.mp4`
