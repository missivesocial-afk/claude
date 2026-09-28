# HoduSoft · "The Hold" (full suite): After Effects package

The whole 39.9 s ad as an editable After Effects project: 9:16 and 16:9 comps, native text, shape layers, music, SFX and voice-over.

> After Effects `.aep` files are a closed binary format that can only be written by After Effects itself.
> This package uses the standard alternative, a **build script**. You run it once and AE assembles the full project, then you save it as `.aep`.

## Setup (about 2 minutes)
1. **Install the fonts** in `fonts/` (Anton, Inter, JetBrains Mono), then restart After Effects.
2. Keep the folder structure as-is: the script looks for `footage/` and `audio/` next to itself.
3. In After Effects: **File → Scripts → Run Script File…** and choose `HoduSoft_TheHold_BUILD.jsx`.
4. When the "built" message appears: **File → Save As…** and save your `.aep`.

## What you get
```
HoduSoft - The Hold (full suite)/
├── HoduSoft_TheHold_9x16    1080×1920 · 30 fps · 39.9 s
├── HoduSoft_TheHold_16x9    1920×1080 · 30 fps · 39.9 s
├── Precomps 9x16 / 16x9     one precomp per headline line and per product-slate name
├── Footage                  plate_9x16.mp4, plate_16x9.mp4
└── Audio                    music, SFX, hold music, IVR voice, full-mix reference
    └── Voice-over clips     VO_01 … VO_14
```
Layer stack in each comp, top to bottom:

| Layers | What they are | Editable |
|---|---|---|
| Text layers | Product tags, feature chips (01 — SKILL-BASED ROUTING …), slate labels and taglines, "MEET / HoduSoft / HODUCC · HODUPBX · HODUBLAST", end logo, products line, URL, CTA text | Native AE text: change copy, font, color. Position, scale and opacity are keyframed |
| `HLxx line n` precomps | Every headline line (e.g. "EVERY MINUTE", "HANGS UP."). Inside, each word is its own text layer that slides up through the line's mask, timed to the voice-over | Double-click to edit words |
| `Slate n product name` precomps | HoduCC, HoduPBX, HoduBlast name wipes | Yes |
| Shape layers | Feature-chip outlines, CTA pill, CTA arrow circle | Native shapes (Fill / Stroke colors) |
| `PLATE - graphics without copy` | Everything else: hold timer, waveforms, caller grid, app windows, wallboards, IVR tree, dialer, omnichannel desktop, AI score wall, PBX tenant map, SIP / provisioning / REC panels, HoduBlast shockwave, film grain | Rendered footage |
| Audio | `MUSIC (ducked under VO)`, `SFX`, `HOLD MUSIC`, `IVR VOICE`, 14 × `VO n - <line>`, `REFERENCE FULL MIX (muted)` | Separate levels. VO clips can be slid individually |

Timeline markers name every scene (HOOK, PROBLEM 1–3, BRAND, SLATE 01–03, each feature, END CARD).

## Common edits
- **Change copy or CTA:** edit the text layer. Headlines: open the `HLxx line n` precomp.
- **Brand color:** all orange is `#F26422`. Change text Fill Colors and shape Fills. The plate's orange is baked, so for a new accent color on the plate, add a *Change to Color* effect on the plate layer (From `#F26422`).
- **Swap in your real logo:** hide `End logo Hodu` and `End logo Soft`, then drop your logo file in at the same spot.
- **Re-time the voice-over:** slide the `VO n` layers. Music ducking is baked into the music stem at the original timing, so for big re-times, use the un-ducked approach: lower `MUSIC` and keyframe its levels yourself.
- **Render:** Composition → Add to Adobe Media Encoder Queue → H.264, "Match Source – High bitrate".

## Audio stems (44.1 kHz, 24-bit WAV)
`01_music_ducked` · `02_sfx` · `03_hold_music` · `04_ivr_phone_voice` · `05_voiceover_full` (all lines on one track, not placed by the script) · `vo/VO_01…14` · `00_full_mix_reference` (the exact mix of the delivered MP4, muted in the comp).
At 0 dB the stems sum to the delivered mix, minus the final soft-clip.

## Credits
Voice-over: Kokoro-82M `af_heart` (Apache-2.0). IVR line: ElevenLabs premade voice "Bella". Music + SFX: synthesized originals, royalty-free. Fonts: Anton, Inter, JetBrains Mono (SIL Open Font License).

`_generator/` holds the tools that produced this package (sampler, capture, JSX generator, mock-AE test, preview verifier). You don't need them to use the project.
