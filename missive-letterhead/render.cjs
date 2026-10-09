// Renders print-ready PDFs + PNG previews for each letterhead design.
// Usage: node render.cjs [design ...]   (needs Playwright + Chromium)
const fs = require("fs"), path = require("path");
const { chromium } = require(process.env.PLAYWRIGHT_PATH || "playwright");
const dir = __dirname, out = path.join(dir, "output");
const all = fs.readdirSync(dir).filter(f => /^[a-z]-.*\.html$/.test(f)).map(f => f.slice(0, -5));
const designs = process.argv.length > 2 ? process.argv.slice(2) : all;
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 794, height: 1123 }, deviceScaleFactor: 2.5 });
  for (const d of designs) {
    await page.goto("file://" + path.join(dir, d + ".html"));
    await page.evaluate(() => document.fonts.ready);
    // Blank print master: every sheet in the file
    await page.pdf({ path: path.join(out, `${d}-letterhead.pdf`), preferCSSPageSize: true, printBackground: true });
    // Sample letter on page 1
    await page.evaluate(() => document.body.classList.add("sample"));
    await page.pdf({ path: path.join(out, `${d}-sample-letter.pdf`), preferCSSPageSize: true, printBackground: true, pageRanges: "1" });
    const names = await page.$$eval(".page", ps => ps.map((p, i) => p.dataset.name || ["first", "continuation"][i]));
    const shot = async (i, name) => {
      // Show one sheet at a time so neighbouring pages never bleed into the PNG
      await page.evaluate(i => document.querySelectorAll(".page").forEach((p, j) => p.style.display = i === j ? "" : "none"), i);
      await page.locator(".page").nth(i).screenshot({ path: path.join(out, `${d}-${name}.png`) });
    };
    await shot(0, "preview");
    await page.evaluate(() => document.body.classList.remove("sample"));
    await shot(0, "blank");
    for (let i = 1; i < names.length; i++) await shot(i, names[i]);
  }
  await browser.close();
})();
