// Render a deck spec (JSON) to PPTX. Assertion-evidence layout:
// the headline is the claim, the lines are the evidence.
//
//   node render/deck_from_spec.mjs examples/sharp_deck.json
//   NO_NOTES=1 node render/deck_from_spec.mjs deck.json   # share-safe build
import fs from "node:fs";
import path from "node:path";
import pptxgen from "pptxgenjs";

const specPath = process.argv[2];
if (!specPath) {
  console.error("usage: node render/deck_from_spec.mjs <deck.json>");
  process.exit(2);
}
const deck = JSON.parse(fs.readFileSync(specPath, "utf-8"));

const DARK = "1F1E1D", BODY = "33302C", MUTED = "6E6862", ACCENT = "CC785C";
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = deck.company || "Pitch";

(deck.slides || []).forEach((sl, i) => {
  const s = pres.addSlide();
  s.background = { color: i === 0 ? DARK : "FFFFFF" };
  const onDark = i === 0;
  s.addText((sl.arc || "").toUpperCase(), {
    x: 0.6, y: 0.35, w: 8.8, h: 0.3, fontSize: 11, bold: true, charSpacing: 3,
    color: ACCENT, fontFace: "Calibri", margin: 0,
  });
  s.addText(sl.headline || "", {
    x: 0.6, y: 0.75, w: 8.8, h: 1.2, fontSize: 30, bold: true,
    color: onDark ? "FFFFFF" : DARK, fontFace: "Cambria", margin: 0,
  });
  (sl.lines || []).forEach((ln, j) => {
    s.addText(ln, {
      x: 0.6, y: 2.2 + j * 0.55, w: 8.8, h: 0.5, fontSize: 16,
      color: onDark ? "EDE8E1" : BODY, fontFace: "Calibri", margin: 0,
    });
  });
  if (sl.notes && !process.env.NO_NOTES) s.addNotes(sl.notes);
  s.addText(`${deck.company || ""} · ${i + 1}`, {
    x: 7.6, y: 5.25, w: 2.0, h: 0.3, fontSize: 9, align: "right",
    color: MUTED, fontFace: "Calibri", margin: 0,
  });
});

const base = path.basename(specPath, ".json");
const out = process.env.NO_NOTES ? `${base}_SHARE.pptx` : `${base}.pptx`;
await pres.writeFile({ fileName: out });
console.log(`wrote ${out}: ${deck.slides.length} slides${process.env.NO_NOTES ? " (notes stripped)" : ""}`);
