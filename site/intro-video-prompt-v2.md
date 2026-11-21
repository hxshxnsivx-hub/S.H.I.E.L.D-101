# Kavach Intro — v2: ONE continuous sequence (first 3 beats)

Rewritten after reviewing your Flow output. The style was right; it failed on
two things: **garbled text** and **scene-cut churn**. This version fixes both —
one unbroken self-drawing take, and no real words for the AI to misspell.

---

## The two rules this prompt is built on

1. **No real words in the generation.** Veo cannot spell — your clip produced
   "Whta leals?", "data leals?", "Padhaar", "7FB8EF". So the boxes and clouds are
   generated as **illegible scribble**, and you type the **real words as a crisp
   overlay afterwards** (CapCut / DaVinci / Premiere, handwriting "write-on" font).
2. **One continuous shot.** No "scenes", no page turns. The ink **draws itself and
   stays** while the camera slowly pulls back — that removes the jumpy redrawing.

**Use your own clip as the style reference:** in Flow, add a clean frame from this
video (the opening frame works) as the **reference image / first frame**, so the new
render keeps this exact blue-ink / cork-board / hand look.

---

## ⭐ MASTER PROMPT — paste this as a single generation (16:9, 1080p, 8s)

```
One continuous unbroken shot, no cuts, no page turns. Top-down view of a spiral-bound
sketchbook lying open flat on a warm brown cork board. Both ivory pages are ruled with
soft sky-blue horizontal lines, a faint red margin down the left. A hand holding a navy
ballpoint pen draws fast, and the ENTIRE scene appears as self-drawing blue ink —
line by line, ink accumulating and never erased.

The drawing builds in one flow: first a small worried stick figure sits hunched at a
desktop computer on the left page, typing. Small 3D-looking boxes sketch themselves
beside him and glide along curved arrows toward a hand-drawn monitor on the right page.
As the boxes reach the screen, the camera starts a slow smooth pull-back, and the empty
space around the drawing blooms with hand-sketched thought-clouds — rough scribbled
cloud shapes with little tails — puffing outward one after another across both pages,
surrounding the figure with worry. Tiny crosses, question marks and spark lines scribble
between the clouds. The hand keeps drawing throughout.

Style: hand-drawn navy ballpoint ink and graphite on warm ivory ruled paper, spiral
binding, on textured brown cork board, warm soft overhead light, gentle paper grain,
faint wet-ink sheen, shallow depth of field, subtle camera breathing, drifting dust
motes, light vignette, 35mm film grain, 24fps, photoreal paper and hand.

Text: every word inside the boxes and clouds is LOOSE ILLEGIBLE SCRIBBLE, not real
letters — placeholder squiggles only. Do not render readable words.

Audio: continuous fast pen-on-paper scratching, soft paper rustle, a quiet ticking
tension that rises as the clouds appear, faint worried whispers underneath, calm room
tone. No music swell yet.

16:9, 1920x1080.
```

---

## Internal pacing (so one 8s take reads as a sequence, not a jump)

- **0–3 s** — figure + computer draw themselves on the left page.
- **3–5 s** — data boxes slide along arrows into the monitor; camera begins pulling back.
- **5–8 s** — worry thought-clouds bloom outward around everything; hold wide.

If you want it longer / calmer, use **Extend** in Flow to continue the *same* drawing
(same style reference), rather than generating a second clip.

---

## Richer options (the "more things" you asked for)

Add any of these lines into the Style block to deepen it:
- "a chipped coffee mug and scattered eraser shavings rest on the cork board edge"
- "the pen leaves a glistening wet-ink trail that dries a shade darker"
- "soft warm key light from the upper left, cool fill, gentle falloff into the corners"
- "the thought-clouds cast faint soft pencil shadows on the page"
- "a barely-there paper curl lifts at the page corners"
- "the camera drifts with a slow, handheld-organic micro-float"

Keep **one** idea per added line; piling on too many makes Veo average them out.

---

## After you generate (the part that makes it look pro)

1. Pick the best of 3–4 takes (AI video is a slot machine).
2. In your editor, **overlay the real words** on the boxes and clouds with a handwriting
   "write-on" reveal: e.g. `Aadhaar`, `card`, `OTP` on the boxes; `What if it leaks?`,
   `Who sees my data?` in the clouds. Times New Roman italic or a neat marker font.
3. Grade slightly warmer, add a soft vignette, mix the audio.
4. This sequence ends wide on the worry-clouds — the next beat (the handwritten question
   + shield, then morph into the product) continues from here with Extend or a new take.

---

## If you insist on AI-rendered text (not recommended)

Use at most **one** short word, big and alone, e.g. only the monitor says `ENTER`.
Everything else stays scribble. More than one word and it degrades again.
