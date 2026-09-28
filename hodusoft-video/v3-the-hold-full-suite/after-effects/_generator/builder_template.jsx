/*
  HoduSoft - "The Hold" (full suite) - After Effects project builder
  -------------------------------------------------------------------
  1. Install the fonts in /fonts (Anton, Inter, JetBrains Mono) and restart After Effects.
  2. Keep this script next to the /footage and /audio folders.
  3. In After Effects: File > Scripts > Run Script File... and pick this file.
  4. When it finishes: File > Save As... to get your .aep.

  Builds two comps (9x16 and 16x9, 30 fps, 39.9 s):
    - every piece of copy as a native, editable text layer (keyframed)
    - headline lines as precomps so the word-by-word mask reveal is preserved
    - feature chip outline, CTA pill + arrow as native shape layers
    - background graphics as a plate (footage/plate_*.mp4)
    - music, SFX, hold music, IVR voice and 14 separate voice-over clips
    - scene markers on the timeline
  Tested against the After Effects ExtendScript DOM (CC 2019 and later).
*/
(function () {
    var DATA = __DATA__;
    var ROOT = File($.fileName).parent;

    function fileAt(rel) {
        var f = new File(ROOT.fsName + "/" + rel);
        if (!f.exists) { throw new Error("Missing file next to the script: " + rel); }
        return f;
    }
    function importItem(rel, folder) {
        var it = app.project.importFile(new ImportOptions(fileAt(rel)));
        if (folder) { it.parentFolder = folder; }
        return it;
    }
    function folder(name, parent) {
        var f = app.project.items.addFolder(name);
        if (parent) { f.parentFolder = parent; }
        return f;
    }
    function setKeys(prop, keys) {
        if (!keys || !keys.length) { return; }
        if (keys.length === 1) { prop.setValue(keys[0][1]); return; }
        var t = [], v = [], i;
        for (i = 0; i < keys.length; i++) { t.push(keys[i][0]); v.push(keys[i][1]); }
        prop.setValuesAtTimes(t, v);
    }
    function setScaleKeys(prop, keys) {
        if (!keys || !keys.length) { return; }
        if (keys.length === 1) { prop.setValue([keys[0][1], keys[0][1]]); return; }
        var t = [], v = [], i;
        for (i = 0; i < keys.length; i++) { t.push(keys[i][0]); v.push([keys[i][1], keys[i][1]]); }
        prop.setValuesAtTimes(t, v);
    }
    function applyTransform(layer, k) {
        var tr = layer.property("ADBE Transform Group");
        var pos = tr.property("ADBE Position");
        pos.dimensionsSeparated = true;
        setKeys(tr.property("ADBE Position_0"), k.x);
        setKeys(tr.property("ADBE Position_1"), k.y);
        setScaleKeys(tr.property("ADBE Scale"), k.s);
        setKeys(tr.property("ADBE Opacity"), k.o);
    }
    function trimLayer(layer, inT, outT) {
        layer.inPoint = Math.max(0, inT);
        layer.outPoint = outT;
    }

    var fontWarnings = {};
    function addTextLayer(comp, u) {
        var layer = comp.layers.addText(u.text);
        layer.name = u.name;
        var srcProp = layer.property("ADBE Text Properties").property("ADBE Text Document");
        var td = srcProp.value;
        td.resetCharStyle();
        td.resetParagraphStyle();
        td.fontSize = u.fs;
        try { td.font = u.font; } catch (e) { fontWarnings[u.font] = true; }
        td.applyFill = true;
        td.fillColor = u.col;
        td.applyStroke = false;
        td.tracking = u.tr;
        td.justification = ParagraphJustification.LEFT_JUSTIFY;
        srcProp.setValue(td);
        try { if (srcProp.value.font !== u.font) { fontWarnings[u.font] = true; } } catch (e2) {}
        // text anchor (0,0) = start of baseline, which is what the keyframes describe
        applyTransform(layer, u.k);
        trimLayer(layer, u["in"], u.out);
        return layer;
    }

    function addShape(comp, sh) {
        var layer = comp.layers.addShape();
        layer.name = sh.name;
        var contents = layer.property("ADBE Root Vectors Group");
        if (sh.arrow) {   // arrow glyph (drawn on top of the circle)
            var ag = contents.addProperty("ADBE Vector Group");
            ag.name = "Arrow";
            var ac = ag.property("ADBE Vectors Group");
            var p = ac.addProperty("ADBE Vector Shape - Group");
            var pts = [[12, 4], [10.6, 5.4], [16.2, 11], [4, 11], [4, 13], [16.2, 13], [10.6, 18.6], [12, 20], [20, 12]];
            var sc = (36 / 24) * (sh.w / 62), verts = [], i;
            for (i = 0; i < pts.length; i++) { verts.push([(pts[i][0] - 12) * sc, (pts[i][1] - 12) * sc]); }
            var shape = new Shape(); shape.vertices = verts; shape.closed = true;
            p.property("ADBE Vector Shape").setValue(shape);
            var af = ac.addProperty("ADBE Vector Graphic - Fill");
            af.property("ADBE Vector Fill Color").setValue([242 / 255, 100 / 255, 34 / 255]);
        }
        var g = contents.addProperty("ADBE Vector Group");
        g.name = sh.kind === "ellipse" ? "Circle" : "Pill";
        var c = g.property("ADBE Vectors Group");
        if (sh.kind === "ellipse") {
            c.addProperty("ADBE Vector Shape - Ellipse").property("ADBE Vector Ellipse Size").setValue([sh.w, sh.h]);
        } else {
            var r = c.addProperty("ADBE Vector Shape - Rect");
            r.property("ADBE Vector Rect Size").setValue([sh.w, sh.h]);
            r.property("ADBE Vector Rect Roundness").setValue(sh.h / 2);
        }
        if (sh.fill) {
            c.addProperty("ADBE Vector Graphic - Fill").property("ADBE Vector Fill Color").setValue(sh.fill);
        }
        if (sh.stroke) {
            var st = c.addProperty("ADBE Vector Graphic - Stroke");
            st.property("ADBE Vector Stroke Color").setValue(sh.stroke);
            st.property("ADBE Vector Stroke Width").setValue(sh.sw);
        }
        applyTransform(layer, sh.k);
        trimLayer(layer, sh["in"], sh.out);
        return layer;
    }

    function build(fm, bins, audio, voItems) {
        var comp = app.project.items.addComp("HoduSoft_TheHold_" + fm.label, fm.W, fm.H, 1, fm.dur, fm.fps);
        comp.parentFolder = bins.root;
        comp.bgColor = [10 / 255, 10 / 255, 11 / 255];
        var pre = folder("Precomps " + fm.label, bins.root);

        // audio (bottom of the stack)
        function addAudio(item, name, start) {
            var l = comp.layers.add(item);
            l.name = name; l.startTime = start || 0;
            return l;
        }
        var i, audioLayers = [];
        audioLayers.push(addAudio(audio.music, "MUSIC (ducked under VO)"));
        audioLayers.push(addAudio(audio.sfx, "SFX"));
        audioLayers.push(addAudio(audio.hold, "HOLD MUSIC"));
        audioLayers.push(addAudio(audio.ivr, "IVR VOICE (phone filtered)"));
        for (i = 0; i < voItems.length; i++) {
            audioLayers.push(addAudio(voItems[i], "VO " + (i + 1) + " - " + DATA.vo[i].text, DATA.vo[i].start));
        }
        var ref = addAudio(audio.mix, "REFERENCE FULL MIX (muted)");
        ref.audioEnabled = false;
        audioLayers.push(ref);

        // background plate
        var plateItem = importItem(fm.plate, bins.footage);
        var plate = comp.layers.add(plateItem);
        plate.name = "PLATE - graphics without copy";
        plate.moveToEnd();
        for (i = 0; i < audioLayers.length; i++) { audioLayers[i].moveToEnd(); }

        // shapes
        for (i = 0; i < fm.shapes.length; i++) { addShape(comp, fm.shapes[i]); }

        // headline lines / slate names as precomps (their bounds do the masking)
        for (i = 0; i < fm.clips.length; i++) {
            var c = fm.clips[i];
            var pc = app.project.items.addComp(fm.label + " - " + c.name, c.w, c.h, 1, fm.dur, fm.fps);
            pc.parentFolder = pre;
            var w;
            for (w = c.words.length - 1; w >= 0; w--) { addTextLayer(pc, c.words[w]); }
            var pl = comp.layers.add(pc);
            pl.name = c.name;
            applyTransform(pl, c.k);
            trimLayer(pl, c["in"], c.out);
        }
        // free text layers
        for (i = 0; i < fm.texts.length; i++) { addTextLayer(comp, fm.texts[i]); }

        // markers
        for (i = 0; i < DATA.markers.length; i++) {
            comp.markerProperty.setValueAtTime(DATA.markers[i][0], new MarkerValue(DATA.markers[i][1]));
        }
        return comp;
    }

    app.beginUndoGroup("Build HoduSoft - The Hold");
    try {
        if (!app.project) { app.newProject(); }
        var bins = {};
        bins.root = folder("HoduSoft - The Hold (full suite)");
        bins.footage = folder("Footage", bins.root);
        bins.audio = folder("Audio", bins.root);
        var voBin = folder("Voice-over clips", bins.audio);
        var audio = {
            music: importItem("audio/01_music_ducked.wav", bins.audio),
            sfx: importItem("audio/02_sfx.wav", bins.audio),
            hold: importItem("audio/03_hold_music.wav", bins.audio),
            ivr: importItem("audio/04_ivr_phone_voice.wav", bins.audio),
            mix: importItem("audio/00_full_mix_reference.wav", bins.audio)
        };
        var voItems = [], i;
        for (i = 0; i < DATA.vo.length; i++) { voItems.push(importItem(DATA.vo[i].file, voBin)); }
        var comps = [];
        for (i = 0; i < DATA.formats.length; i++) { comps.push(build(DATA.formats[i], bins, audio, voItems)); }
        comps[0].openInViewer();
        var missing = [], f;
        for (f in fontWarnings) { if (fontWarnings.hasOwnProperty(f)) { missing.push(f); } }
        alert("HoduSoft - The Hold is built: 2 comps (9x16, 16x9).\n\n" +
              (missing.length ? "Fonts not found (install from /fonts, restart AE, run again):\n" + missing.join(", ") + "\n\n" : "") +
              "Now use File > Save As... to save your .aep.");
    } catch (err) {
        alert("Build stopped: " + err.toString() + (err.line ? " (line " + err.line + ")" : ""));
    } finally {
        app.endUndoGroup();
    }
})();
