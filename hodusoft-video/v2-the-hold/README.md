# HoduSoft: "The Hold" (29.4s, with voice-over)

Built from the business pain point, not from the reference video.

**Insight:** every contact center's worst number is the one customers feel, which is time on hold.
Behind it: agents switching between tools, and supervisors with no live view.
**Device:** a hold timer that races up in the opening, drops the call, and at the end rewinds to `00:00 · CONNECTED`.

| Time | Voice-over | On screen |
|---|---|---|
| 0–3.5 | (IVR, phone-filtered) "Your call is important to us. Please stay on the line." | Hold timer races 00:00 → 14:52, hold-music waveform |
| 3.5–4.2 | busy tone | CALL DROPPED, red glitch |
| 4.3–6.9 | "Every minute on hold, another customer hangs up." | 100-caller grid, dots turn red and fall, abandoned-calls counter |
| 7.0–9.0 | "Your agents? Juggling six screens." | 6 app windows, alt-tab chaos |
| 9.1–11.1 | "Your supervisors? Flying blind." | Wallboard of static, NO SIGNAL |
| 11.3–13.5 | "Meet HoduCC, by HoduSoft." | Lime flash, the flatline comes back as a heartbeat |
| 13.6–16.5 | "Smart IVR sends every call to the right agent." | 01 Smart IVR + routing: call pulse travels the IVR tree to an agent |
| 16.6–19.4 | "Predictive dialing keeps your team talking, not waiting." | 02 Predictive dialer: agents flip from IDLE to TALKING |
| 19.6–22.0 | "Voice, WhatsApp, email and chat. One screen." | 03 Omnichannel: the 6 windows merge into one agent desktop |
| 22.1–25.3 | "Supervisors can listen, whisper, or barge in. Live." | 04 Live monitoring: wallboard comes alive; listen, whisper, barge in |
| 25.6–29.4 | "Nobody likes waiting. Now, nobody has to." | Timer rewinds to 00:00 CONNECTED, then logo + BOOK A FREE DEMO |

## Audio credits
- Narration: Kokoro-82M `af_heart` (open source, Apache-2.0), `source/vo/tts.py`
- IVR line: ElevenLabs "Bella" (premade voice), phone-band filtered
- Music + all SFX: synthesized in `source/audio.py`, royalty-free

## Rebuild
1. `python3 -c "s=open('index.html').read();open('page.html','w').write(s.replace('__TIMING__',open('timing.json').read()))"`
2. `node cap.js video 1080 1920 v.mp4` (or `1920 1080`)
3. `python3 audio.py` → `soundtrack.wav`, then `ffmpeg -i v.mp4 -i soundtrack.wav -c:v copy -c:a aac -shortest out.mp4`

Colors live in `:root` at the top of `index.html` (`--lime`, `--red`, `--bg`), so brand colors are a one-line swap.
