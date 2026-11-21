# Kavach — Intro Film · Master Prompt for Google Flow (Veo 3)

A hand-drawn sketchbook opens, a worker is about to send private data, the page
swarms with "what if it leaks?" worries, a single italic line asks *"what if
something guarded it?"*, a shield is sketched — and the paper morphs into the
real Kavach product. Analog → AI.

---

## 1. Creative direction (the spine)

| | |
|---|---|
| **Format** | 16:9 landscape, **1920×1080**, 24 fps, filmic. (9:16 variant notes in §5.) |
| **Length** | ~40 s total = **5 shots × ~8 s** (Veo 3 generates ~8 s per clip; you stitch them). |
| **Arc** | open book → worker + private data → worry-clouds → the handwritten question + shield → morph into the product hero. |
| **Look** | warm ivory ruled paper, blue-ink + graphite sketches, soft window light, 35 mm grain, shallow depth of field. |
| **Mood** | calm-curious → anxious → hopeful → confident. |

### Palette (sampled from your reference paper)
- Page / ivory: `#FCFBEF`
- Ruled lines (sky blue): `#7FB5DD`
- Ink (handwriting & sketches): `#16304F` (deep blue-black)
- Pencil / graphite: `#4A4A4A`
- Final product reveal (your live hero): near-black `#010102`, lavender `#5E6AD2`

### Typography for the handwritten lines
- **Times New Roman, *italic*, regular weight** — slight slant, fully legible (not loopy cursive).
- Revealed **letter by letter**, left→right, as if being written (~2–3 chars/sec).
- Keep each line **≤ 6 words** (AI video renders short text far more legibly).

> **Read this before you generate:** Veo garbles exact words and real logos. Treat
> any on-screen wording and the "Kavach" wordmark as **placeholder** — generate the
> handwriting loosely for the *feel*, then overlay the **real, crisp text** in a
> video editor (CapCut / DaVinci / Premiere) using a Times New Roman italic font
> with a "write-on" reveal. Do the same for the final product UI and logo.

---

## 2. Global style block — paste at the top of EVERY scene prompt

```
Style: cinematic macro / top-down flat-lay of a horizontal hardback sketchbook on a
warm oak desk. Warm natural window light from the left, soft shadows, shallow depth
of field, 35mm film look with gentle grain, 24fps, photoreal textures. The page is
warm ivory paper (#FCFBEF) with evenly spaced horizontal ruled lines in soft sky-blue
(#7FB5DD), visible paper grain, fiber and a subtle page curl with soft contact shadow.
Everything drawn is deep blue-black ink (#16304F) and graphite pencil, with natural
ink bleed and pencil grain. Analog-meets-AI, thoughtful mood. No real company logos,
no watermarks. Aspect ratio 16:9, 1920x1080.
```

---

## 3. Scene prompts (generate each as its own 8 s clip)

### SCENE 1 — The book opens (0–8 s)
```
[STYLE BLOCK] A closed horizontal hardback sketchbook rests on a warm oak desk beside
a softly glowing laptop. Two hands gently open the cover; the pages fan and settle on
a fresh ivory page ruled with soft sky-blue horizontal lines. A hand lays a fountain
pen on the page and lifts away. Camera: slow top-down push-in (about 10%). Dust motes
drift in the window light.
Audio: soft paper rustle, the quiet creak of the spine, a single pen tap, calm room
tone, one soft piano note.
```
- **Transition out:** hold on the clean ruled page.

### SCENE 2 — The worker sends private data (8–16 s)
```
[STYLE BLOCK] On the ruled ivory page, quick ink-and-pencil sketches draw themselves:
a small figure sits at a computer, typing. Beside it, little hand-labelled boxes appear
one by one — "Aadhaar", "card", "OTP" — and arrows push them from the figure into the
machine. The figure's hand reaches toward a sketched key labelled "Enter". Camera: slow
push toward the Enter key.
Audio: brisk pencil scratches, soft keyboard taps, a low tension tone slowly rising.
```
- **Transition out:** freeze the instant before the finger presses Enter.

### SCENE 3 — The cloud of "what ifs" (16–24 s)
```
[STYLE BLOCK] Before the key is pressed, the page blooms with worry: hand-drawn
thought-clouds puff outward across the ivory paper in ink, each holding a scribbled
question — "What if the data leaks?", "Who sees my Aadhaar?". Around them, small
sketched newspaper clippings and headlines drift like clouds — "AI agent leaked user
data", "PII exposed" — with tiny worried doodle faces. Camera: slow pull-back revealing
the whole page swarmed with anxious sketches.
Audio: overlapping whispered murmurs, rustling paper, an uneasy ambient drone.
```
- **Transition out:** the worried clouds dim; a hand turns the page (motion-blur wipe).

### SCENE 4 — The question, handwritten (24–32 s)
```
[STYLE BLOCK] A fresh ivory ruled page. A single hand writes slowly, letter by letter,
in elegant Times New Roman italic ink: "What if something guarded every tool call?".
The ink looks freshly laid with a faint wet sheen. Beneath the line, the hand sketches
a small, clean shield. Camera: intimate top-down macro, static, shallow focus on the
nib.
Audio: the fine scratch of a nib on paper, a soft hopeful piano motif beginning.
```
- **Transition out:** the sketched shield starts to glow.

### SCENE 5 — Paper becomes product (32–40 s)
```
[STYLE BLOCK] The hand-drawn shield glows; its ink lines brighten into light. The ivory
paper and blue rules dissolve and morph into a sleek modern dark interface — a deep
near-black screen (#010102) where a glowing lavender shield (#5E6AD2) sits at center
and small data tags stream toward it and transform into secure tokens. The analog
sketch becomes a polished product UI. Camera: settle into a steady, confident frame.
Audio: a soft rising synth pad, one clean UI chime, a confident low hum.
```
- **Transition out:** hold on the dark hero for your end-card / logo overlay.
- **Tip:** set this clip's **last frame** (Frames-to-Video) to a real screenshot of
  your live hero so the morph lands exactly on-brand.

---

## 4. Flow production workflow

1. **Project settings:** aspect **16:9**, resolution **1080p**.
2. **Lock the paper look:** add your reference paper image as an **Ingredient**, or use
   it as Scene 1's **first frame** (Frames-to-Video). Reuse the same **seed** where Flow
   lets you, so texture/colour stay consistent across shots.
3. **Generate each scene** from its prompt; render **3–4 takes** and keep the best (AI
   video is a slot machine).
4. **Seamless joins:** use **Frames-to-Video** — take the **last frame** of a shot and
   set it as the **first frame** of the next (page-turns in 3→4, and the morph in 5).
   For Scene 5, set the **last frame = a screenshot of your real hero**.
5. **Longer beats:** use **Extend** if the writing reveal needs more than 8 s.
6. **Assemble** in **Scene Builder** in order; add short cross-dissolves on the turns.
7. **Finish in an editor:** overlay the **real, legible text** (Times New Roman italic,
   write-on reveal), drop in the **Kavach wordmark**, colour-grade, and mix the music.

---

## 5. Two ways to use it on the site

**A. Intro that resolves into your current hero (recommended).** The film ends by
morphing into the dark `#010102` + lavender hero you already have — zero rework, and
Scene 5 lands on it. Play it once on load, then reveal the live page.

**B. Restyle the whole site to the sketchbook theme.** If you want the paper look to
carry through, swap the design tokens to:
- background ivory `#FCFBEF`, ruled sky-blue `#7FB5DD` as the grid/hairlines,
- ink navy `#16304F` text, graphite `#4A4A4A` secondary, blue-ink accent `#2D6CDF`,
- a refined serif for display in italic (e.g. *Fraunces* / *Spectral* / Times-like) +
  a clean sans for body.
This is more work and flips the mood from "software-craft dark" to "editorial light."

**9:16 social cut:** re-generate Scenes 1, 4, 5 in 9:16, tighter framing, same prompts.

---

## 6. Pitfalls (so you don't waste credits)

- **Text & logos:** don't trust Veo for exact words or the wordmark — overlay in post.
- **Hands:** detailed drawing hands can look uncanny. Prefer "sketches draw themselves"
  (self-drawing ink); keep any hand brief and in soft focus.
- **Background text** (newspapers, doodle faces) will be gibberish up close — keep them
  as texture, never the focal point.
- **8 s cap:** plan every cut around it; don't ask one clip to do two beats.
- **Consistency:** same seed + the paper Ingredient on every shot, or the texture drifts.
