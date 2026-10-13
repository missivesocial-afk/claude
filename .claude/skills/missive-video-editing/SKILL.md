---
name: missive-video-editing
description: Edit, re-cut, re-brand and re-render the HTML/Playwright motion-graphics ads in this repo (and new ones for Missive Digital or its clients). Use when the user asks to change copy, timing, colours, voice-over, music, aspect ratio or the CTA of a video, render stills or a final MP4, or make a new ad in the Missive brand. Read brand-colours.md before touching any colour, font or gradient.
---

# Missive video editing

Every ad here is a single HTML page that draws one frame for any time `t`. Playwright screenshots it frame by frame, ffmpeg encodes it, and a Python script synthesises the soundtrack. Edit the source, render, mux. Never edit the MP4s directly.

## Project layout

```
<project>/
├── README.md              storyboard table: time · scene · sound. Keep it in sync with edits.
├── <Name>_16x9.mp4        1920×1080 (website hero, YouTube, LinkedIn)
├── <Name>_9x16.mp4        1080×1920 (Reels, TikTok, Shorts, Stories)
└── source/
    ├── index.html | film.html | ride.html   the animation; exposes window.render(t) and window.ready
    ├── timeline.json / timing.json / durs.json   scene and VO cue times (shared by HTML and audio)
    ├── cap.js             renderer: stills or full video
    ├── audio.py           music + SFX + VO mix → soundtrack.wav
    ├── vo/*.wav, tts.py   voice-over clips and the script that made them
    └── fonts/*.woff2      fonts are embedded locally, never loaded from a CDN at render time
```

`cap.js` loads `page.html` from the current directory. Copy or symlink the project's HTML to `page.html` before running it if the names differ.

## Workflow

1. **Read first.** Open the project README (storyboard) and the top of the HTML: colours are CSS variables in `:root`, timings come from the JSON file. Find the scene by its time in the storyboard.
2. **Make the edit** in the smallest place that owns it:
   | Change | Where |
   |---|---|
   | Copy / headline / CTA / URL | text in the HTML scene function |
   | Colour, gradient, font | `:root` CSS variables (see brand-colours.md) |
   | Scene timing, VO cue | the timeline/timing JSON. Both `render(t)` and `audio.py` read it, so picture and sound stay in sync |
   | VO line | regenerate the clip with `vo/tts.py`, then update its duration in `durs.json` |
   | Music / SFX | `audio.py` |
   | Total length | `dur` in `cap.js` and the end time in the JSON |
3. **Check stills before a full render** (fast, catches 90% of problems):
   ```
   node cap.js stills 1080 1920 0.5,4,12.5,27   # writes st/1080x1920_<t>.jpg
   node cap.js stills 1920 1080 0.5,4,12.5,27
   ```
   Look at the stills (Read the JPGs). Check both aspect ratios: text must clear the 9:16 safe area (top 250 px and bottom 350 px are covered by platform UI) and never clip at 16:9.
4. **Render** each aspect ratio:
   ```
   node cap.js video 1080 1920 out_9x16.mp4
   node cap.js video 1920 1080 out_16x9.mp4
   ```
   30 fps, libx264 CRF 17, yuv420p. Needs Playwright (preinstalled Chromium) and ffmpeg. Do not run `playwright install`.
5. **Sound:** `python3 audio.py` → `soundtrack.wav`. VO is ducked under the music automatically. Keep peaks below −1 dBFS.
6. **Mux:**
   ```
   ffmpeg -i out_9x16.mp4 -i soundtrack.wav -c:v copy -c:a aac -b:a 192k -shortest <Name>_9x16.mp4
   ```
7. **Verify** with `ffprobe` (resolution, duration, audio stream present) and pull 3–4 frames from the final file with `ffmpeg -ss <t> -frames:v 1` to confirm nothing changed unexpectedly.
8. **Update the README** storyboard if timing or copy changed, then commit source and MP4s together.

## Editing rules

- One idea per beat; a cut lands on the beat (120 BPM = 0.5 s grid in most projects).
- Hold every on-screen line long enough to read twice: about 0.3 s per word, 1.2 s minimum.
- Burned-in captions for every VO line; most social video plays muted.
- Hook in the first 1.5 s, logo and CTA on screen for the final 3 s minimum, URL readable at phone size.
- Only real product names, features and numbers the client gave you. Never invent statistics, reviews or customer logos.
- No em-dashes in on-screen copy.
- Audio is synthesised or from `vo/`. Do not pull music or SFX from the internet (licensing).
- Client brands keep their own colours (HoduSoft orange `#F26422`). Use the Missive palette only for Missive's own videos, or for the "Made by Missive" end tag.

## After Effects hand-off

`v3-the-hold-full-suite/after-effects/` shows the pattern: a `.jsx` build script that assembles native text layers, shape layers, a rendered plate and separate audio stems. Use the same approach when a client asks for an editable AE project; `.aep` cannot be written outside After Effects.

## New Missive-branded video checklist

- [ ] `:root` uses the tokens from brand-colours.md, nothing off-palette
- [ ] Instrument Sans 600 headings, Rubik body, both embedded as woff2
- [ ] Brand gradient on at most one highlighted word per headline, the CTA pill and eyebrow badges
- [ ] End card: Missive logo, one CTA ("Book a consultation" or the brief's exact label), missivedigital.com
- [ ] Stills checked at 9:16 and 16:9, final MP4s probed, README storyboard written
