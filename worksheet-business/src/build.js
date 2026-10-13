// Turns a worksheet JSON file into a print-ready A4 PDF:
// page 1 = worksheet for the child, page 2 = answer key for the parent.
// Name, tagline and phone number come from brand.json.
// Usage: node build.js class3-day1.json [more.json ...]
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

function render(d) {
  let n = 0;
  const sections = d.sections.map((s) => `
    <section class="${s.hindi ? 'hi' : ''}">
      <h2><span>${esc(s.title)}</span> <small>${esc(s.titleHi)}</small></h2>
      <ol>${s.questions.map((q) => `
        <li value="${++n}">${esc(q.q)}${'<div class="line"></div>'.repeat(q.lines || 0)}</li>`).join('')}
      </ol>
    </section>`).join('');

  let m = 0;
  const answers = d.sections.map((s) => `
    <section class="${s.hindi ? 'hi' : ''}">
      <h2><span>${esc(s.title)}</span></h2>
      <ol>${s.questions.map((q) => `<li value="${++m}">${esc(q.a)}</li>`).join('')}</ol>
    </section>`).join('');

  return `<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;800&family=Noto+Sans:wght@400;600&family=Noto+Sans+Devanagari:wght@400;600&display=swap" rel="stylesheet">
<style>
  @page { size: A4; margin: 12mm 14mm; }
  * { box-sizing: border-box; }
  body { font-family: 'Noto Sans', 'Noto Sans Devanagari', sans-serif; color: #1f2430; font-size: 12.5pt; margin: 0; }
  .page { page-break-after: always; }
  .page:last-child { page-break-after: auto; }
  header { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #f2994a; padding-bottom: 6px; }
  .brand { font-family: 'Baloo 2', sans-serif; font-weight: 800; font-size: 22pt; color: #e8590c; line-height: 1; }
  .brand small { font-family: 'Noto Sans Devanagari'; font-size: 12pt; color: #8a5a2b; font-weight: 600; margin-left: 6px; }
  .meta { text-align: right; font-size: 10.5pt; color: #555; }
  .meta b { font-size: 13pt; color: #1f2430; }
  .student { display: flex; gap: 24px; margin: 10px 0 4px; font-size: 11pt; }
  .student div { flex: 1; border-bottom: 1px solid #999; padding-bottom: 2px; }
  section { margin-top: 9px; break-inside: avoid; }
  h2 { font-family: 'Baloo 2', sans-serif; font-size: 15pt; margin: 0 0 4px; color: #fff; background: #2f6fb3; display: inline-block; padding: 1px 12px; border-radius: 6px; }
  section:nth-of-type(2) h2 { background: #2b9348; }
  section:nth-of-type(3) h2 { background: #c2410c; }
  h2 small { font-family: 'Noto Sans Devanagari'; font-size: 10.5pt; font-weight: 400; opacity: .9; }
  ol { margin: 4px 0 0; padding-left: 24px; }
  li { margin: 5px 0; line-height: 1.5; white-space: pre-wrap; }
  .hi li { font-family: 'Noto Sans Devanagari', sans-serif; }
  .line { border-bottom: 1px dashed #aaa; height: 24px; }
  .fun { margin-top: 14px; border: 2px dashed #f2994a; border-radius: 10px; padding: 8px 12px; background: #fff7ef; }
  .fun b { color: #e8590c; }
  footer { margin-top: 12px; font-size: 9.5pt; color: #777; display: flex; justify-content: space-between; }
  .key h1 { font-family: 'Baloo 2', sans-serif; font-size: 18pt; margin: 10px 0 0; }
  .key p.note { font-size: 10pt; color: #666; margin: 2px 0 0; }
</style></head><body>
<div class="page">
  <header>
    <div class="brand">${esc(d.brand)}<small>${esc(d.tagline)}</small></div>
    <div class="meta"><b>${esc(d.className)} · ${esc(d.day)}</b><br>Maths · English · Hindi</div>
  </header>
  <div class="student"><div>Name:</div><div>Date:</div><div>Score: ____ / ${n + 1}</div></div>
  ${sections}
  <div class="fun"><b>★ ${esc(d.fun.q)}</b></div>
  <footer><span>Time: about 20 minutes · ${esc(d.disclaimer)}</span><span>${esc(d.contact)}</span></footer>
</div>
<div class="page key">
  <header>
    <div class="brand">${esc(d.brand)}<small>${esc(d.tagline)}</small></div>
    <div class="meta"><b>${esc(d.className)} · ${esc(d.day)}</b><br>Answer key — for parents</div>
  </header>
  <h1>Answer Key</h1>
  <p class="note">Check together with your child. Praise effort, then redo any wrong answer.</p>
  ${answers}
  <div class="fun"><b>★ ${esc(d.fun.a)}</b></div>
</div>
</body></html>`;
}

(async () => {
  const files = process.argv.slice(2);
  if (!files.length) { console.error('Usage: node build.js <worksheet.json> ...'); process.exit(1); }
  const outDir = path.join(__dirname, '..', 'samples');
  fs.mkdirSync(outDir, { recursive: true });
  const brand = JSON.parse(fs.readFileSync(path.join(__dirname, 'brand.json'), 'utf8'));
  const browser = await chromium.launch();
  const page = await browser.newPage();
  for (const f of files) {
    const data = { ...brand, ...JSON.parse(fs.readFileSync(f, 'utf8')) };
    await page.setContent(render(data), { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    const out = path.join(outDir, path.basename(f, '.json') + '.pdf');
    await page.pdf({ path: out, format: 'A4', printBackground: true, preferCSSPageSize: true });
    console.log('wrote', out);
  }
  await browser.close();
})();
