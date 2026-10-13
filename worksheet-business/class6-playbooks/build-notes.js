// Builds the Class 6 subject playbooks: notes/<subject>.md -> pdf/<subject>.pdf
// Usage: node build-notes.js            (all subjects)
//        node build-notes.js maths      (one subject)
//
// Notes format = Markdown plus:
//   a header block between --- lines (title, subtitle, color, lang)
//   boxes:   :::trick Title   ...   :::     (trick, play, mumbai, fact, exam, check, key)
//   ## Heading  starts a new chapter on a new page
const fs = require('fs');
const path = require('path');
const { marked } = require('marked');
const { chromium } = require('playwright');

const BOXES = {
  trick: ['🧠', 'Memory Trick'],
  play: ['🎲', 'Play It in Class'],
  mumbai: ['📍', 'Mumbai Connection'],
  fact: ['💡', 'Did You Know?'],
  exam: ['⭐', 'Exam Tip'],
  check: ['✏️', 'Quick Check'],
  key: ['📌', 'Must Remember'],
};

function parse(src) {
  const meta = {};
  const m = src.match(/^---\n([\s\S]*?)\n---\n/);
  if (m) {
    for (const line of m[1].split('\n')) {
      const i = line.indexOf(':');
      if (i > 0) meta[line.slice(0, i).trim()] = line.slice(i + 1).trim();
    }
    src = src.slice(m[0].length);
  }
  // Replace :::box blocks with HTML (inner Markdown rendered separately).
  const body = src.replace(/^:::(\w+)(.*)\n([\s\S]*?)^:::\s*$/gm, (_, type, title, inner) => {
    const [icon, label] = BOXES[type] || ['', type];
    const head = title.trim() ? `${label}: ${title.trim()}` : label;
    return `<div class="box ${type}"><div class="box-h">${icon} ${head}</div>${marked.parse(inner)}</div>\n`;
  });
  return { meta, html: marked.parse(body) };
}

function page({ meta, html }) {
  const color = meta.color || '#2f6fb3';
  return `<!doctype html><html lang="${meta.lang || 'en'}"><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;800&family=Noto+Sans:wght@400;600;700&family=Noto+Sans+Devanagari:wght@400;600;700&family=Noto+Sans+Mono&display=swap" rel="stylesheet">
<style>
  @page { size: A4; margin: 13mm 13mm 15mm; }
  * { box-sizing: border-box; }
  :root { --c: ${color}; }
  body { font-family: 'Noto Sans', 'Noto Sans Devanagari', 'Noto Color Emoji', sans-serif; color: #1f2430; font-size: 11.5pt; line-height: 1.5; margin: 0; }
  .cover { height: 268mm; display: flex; flex-direction: column; justify-content: center; text-align: center; page-break-after: always;
           border: 6px solid var(--c); border-radius: 18px; padding: 20mm 14mm; }
  .cover .big { font-size: 64pt; line-height: 1; }
  .cover h1 { font-family: 'Baloo 2', 'Noto Sans Devanagari', sans-serif; font-size: 36pt; color: var(--c); margin: 10px 0 0; line-height: 1.1; }
  .cover .sub { font-size: 14pt; color: #444; margin-top: 8px; }
  .cover .tag { display: inline-block; margin: 18px auto 0; background: var(--c); color: #fff; border-radius: 30px; padding: 6px 18px; font-weight: 700; }
  .cover .small { margin-top: 30px; font-size: 9.5pt; color: #777; }
  h1, h2, h3 { font-family: 'Baloo 2', 'Noto Sans Devanagari', sans-serif; line-height: 1.2; }
  h1 { color: var(--c); font-size: 22pt; margin: 0 0 6px; }
  h2 { break-before: page; color: #fff; background: var(--c); font-size: 17pt; padding: 6px 14px; border-radius: 10px; margin: 0 0 10px; }
  h3 { color: var(--c); font-size: 13.5pt; margin: 14px 0 4px; border-bottom: 2px solid var(--c); padding-bottom: 2px; }
  p { margin: 5px 0; }
  ul, ol { margin: 4px 0; padding-left: 22px; }
  li { margin: 2px 0; }
  table { border-collapse: collapse; width: 100%; margin: 6px 0; font-size: 10.5pt; break-inside: avoid; }
  th { background: var(--c); color: #fff; text-align: left; }
  th, td { border: 1px solid #c9ced8; padding: 4px 7px; vertical-align: top; }
  tr:nth-child(even) td { background: #f5f7fb; }
  code { font-family: inherit; background: #eef1f6; padding: 0 4px; border-radius: 4px; }
  .box { border-radius: 10px; padding: 7px 12px; margin: 9px 0; break-inside: avoid; border-left: 6px solid; }
  .box-h { font-weight: 700; margin-bottom: 2px; }
  .box p:first-of-type { margin-top: 0; }
  .trick  { background: #fff8db; border-color: #f2b705; }
  .play   { background: #e7f8ec; border-color: #2b9348; }
  .mumbai { background: #e6f1fb; border-color: #2f6fb3; }
  .fact   { background: #f2ecfb; border-color: #7b4bc4; }
  .exam   { background: #fdecec; border-color: #d64545; }
  .check  { background: #fff1e6; border-color: #e8590c; }
  .key    { background: #eef1f6; border-color: #4a5568; }
  pre { background: #f7f6f0; border: 1px solid #ddd8c4; border-radius: 8px; padding: 8px 10px; font-family: 'Noto Sans Mono', 'Noto Sans Devanagari', monospace; font-size: 9.5pt; line-height: 1.45; white-space: pre-wrap; break-inside: avoid; }
  pre code { background: none; padding: 0; }
  blockquote { margin: 6px 0; padding: 6px 12px; background: #faf7f0; border-left: 4px solid var(--c); border-radius: 6px; }
  hr { border: none; border-top: 1px dashed #bbb; margin: 10px 0; }
  .footer-note { font-size: 9pt; color: #777; }
</style></head><body>
<div class="cover">
  <div class="big">${meta.icon || '📘'}</div>
  <h1>${meta.title || ''}</h1>
  <div class="sub">${meta.subtitle || ''}</div>
  <div><span class="tag">ICSE Class 6 · Full Book · Final Exam Ready</span></div>
  <div class="small">Play &amp; Learn Notes · Independent study material, not affiliated with CISCE.<br>
  Chapter names and order can differ slightly between schools and publishers. Follow your school's exam syllabus.</div>
</div>
${html}
</body></html>`;
}

(async () => {
  const only = process.argv.slice(2);
  const dir = path.join(__dirname, 'notes');
  const files = fs.readdirSync(dir).filter((f) => f.endsWith('.md'))
    .filter((f) => !only.length || only.includes(path.basename(f, '.md')));
  const browser = await chromium.launch();
  const pg = await browser.newPage();
  for (const f of files) {
    const doc = parse(fs.readFileSync(path.join(dir, f), 'utf8'));
    await pg.setContent(page(doc), { waitUntil: 'networkidle' });
    await pg.evaluate(() => document.fonts.ready);
    const out = path.join(__dirname, 'pdf', path.basename(f, '.md') + '.pdf');
    await pg.pdf({
      path: out, format: 'A4', printBackground: true, preferCSSPageSize: true,
      displayHeaderFooter: true, headerTemplate: '<span></span>',
      footerTemplate: `<div style="font-size:8px;color:#888;width:100%;padding:0 13mm;display:flex;justify-content:space-between;font-family:sans-serif">
        <span>${doc.meta.footer || 'ICSE Class 6 · Play & Learn Notes'}</span><span>Page <span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`,
    });
    console.log('wrote', out);
  }
  await browser.close();
})();
