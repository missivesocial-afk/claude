# HoduSoft — 28s social / web / ad video

- `HoduSoft_Ad_9x16_Vertical.mp4`: 1080×1920 for Reels, TikTok, Shorts, Stories and vertical ads
- `HoduSoft_Ad_16x9_Landscape.mp4`: 1920×1080 for the website hero, YouTube and LinkedIn

## Storyboard (120 BPM, cuts land on the beat)
| Time | Scene | Sound |
|---|---|---|
| 0–4s | "RING! RING! RING!!", mascot panics, missed-call counter, "Sound familiar?" | phone rings, slams, notification ticks, slide whistle, riser |
| 4–6s | "Your customers are *everywhere.*": 10 channel chips burst out | beat drops, pops |
| 6–9s | Chips get sucked into a vortex and morph into the HoduCC **Unified Inbox** | vortex sweep, bloop, chime |
| 9–12s | **Smart IVR**: caller presses 2 and is routed to an agent | real DTMF tone, connect chime |
| 12–15s | **Predictive dialer** campaign running itself | dial tones, status pops |
| 15–18s | **AI chatbot** at 3:07 AM ("AI that never clocks out") | typing clicks, bubble pops |
| 18–21s | **Real-time analytics** dashboard | ascending blips |
| 21–23.5s | "Trusted by 2,000+ businesses" · Cloud / On-premise / Hybrid | impact, counter ticks, riser |
| 23.5–28s | Logo resolve, tagline, **Book a free demo** CTA, hodusoft.com | big impact, chord, final hit |

## Editing / re-rendering
`source/index.html` is the whole animation, driven by time (`render(t)`). Colors are CSS variables at the top of the file.
- Preview a frame: open `index.html?w=1080&h=1920` and run `render(12.5)` in the console
- Render: `node cap.js video 1080 1920 out.mp4` (needs Playwright and ffmpeg)
- Music and SFX: `python3 audio.py` → `soundtrack.wav` (100% synthesized, royalty-free)
- Mux: `ffmpeg -i out.mp4 -i soundtrack.wav -c:v copy -c:a aac -shortest final.mp4`
