/**
 * Inyecta el nav desde partials/nav-en.html o nav-es.html en cada página
 * que contiene <!-- landing:inject-nav --> y escribe dist/*.html.
 * El resto de HTML en src/ se copia tal cual a dist/.
 */
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SRC = path.join(__dirname, "src");
const DIST = path.join(__dirname, "dist");
const PARTIALS = path.join(SRC, "partials");

const MARKER = "<!-- landing:inject-nav -->";

/** @type {Record<string, { lang: 'en' | 'es'; NAV_CTA_HREF: string; LANG_ES_HREF?: string; LANG_EN_HREF?: string; indent: string }>} */
const NAV_BY_FILE = {
  "index.html": {
    lang: "en",
    NAV_CTA_HREF: "contact-en.html#landing-contact-form",
    LANG_ES_HREF: "index-es.html",
    indent: "    ",
  },
  "contact-en.html": {
    lang: "en",
    NAV_CTA_HREF: "#landing-contact-form",
    LANG_ES_HREF: "contact.html#landing-contact-form",
    indent: "  ",
  },
  "pricing-en.html": {
    lang: "en",
    NAV_CTA_HREF: "contact-en.html#landing-contact-form",
    LANG_ES_HREF: "pricing.html",
    indent: "    ",
  },
  "index-es.html": {
    lang: "es",
    NAV_CTA_HREF: "contact.html#landing-contact-form",
    LANG_EN_HREF: "index.html",
    indent: "    ",
  },
  "contact.html": {
    lang: "es",
    NAV_CTA_HREF: "#landing-contact-form",
    LANG_EN_HREF: "contact-en.html#landing-contact-form",
    indent: "  ",
  },
  "pricing.html": {
    lang: "es",
    NAV_CTA_HREF: "contact.html#landing-contact-form",
    LANG_EN_HREF: "pricing-en.html",
    indent: "    ",
  },
};

function loadTemplate(lang) {
  const name = lang === "en" ? "nav-en.html" : "nav-es.html";
  return fs.readFileSync(path.join(PARTIALS, name), "utf8");
}

function applyTokens(template, cfg) {
  let out = template.replace(/\{\{NAV_CTA_HREF\}\}/g, cfg.NAV_CTA_HREF);
  if (cfg.lang === "en") {
    out = out.replace(/\{\{LANG_ES_HREF\}\}/g, cfg.LANG_ES_HREF);
  } else {
    out = out.replace(/\{\{LANG_EN_HREF\}\}/g, cfg.LANG_EN_HREF);
  }
  return out;
}

function indentNav(navHtml, indent) {
  return navHtml
    .split("\n")
    .map((line) => (line.length ? indent + line : line))
    .join("\n");
}

function buildNavHtml(filename) {
  const cfg = NAV_BY_FILE[filename];
  const raw = loadTemplate(cfg.lang);
  const withTokens = applyTokens(raw, cfg);
  return indentNav(withTokens, cfg.indent);
}

function listHtmlFiles() {
  return fs
    .readdirSync(SRC)
    .filter((f) => f.endsWith(".html"));
}

function main() {
  fs.mkdirSync(DIST, { recursive: true });
  const htmlFiles = listHtmlFiles();

  for (const file of htmlFiles) {
    const srcPath = path.join(SRC, file);
    let body = fs.readFileSync(srcPath, "utf8");

    if (!body.includes(MARKER)) {
      fs.writeFileSync(path.join(DIST, file), body);
      continue;
    }

    const cfg = NAV_BY_FILE[file];
    if (!cfg) {
      throw new Error(
        `[build-nav] ${file} tiene ${MARKER} pero no hay entrada en NAV_BY_FILE`
      );
    }

    const navInner = buildNavHtml(file);
    const navBlock = `${cfg.indent}<!-- Nav -->\n${navInner}`;
    const markerPattern = /\n\s*<!-- landing:inject-nav -->\s*\n/;
    if (!markerPattern.test(body)) {
      throw new Error(`[build-nav] ${file}: falta el marcador ${MARKER}`);
    }
    body = body.replace(markerPattern, `\n${navBlock}\n`);
    fs.writeFileSync(path.join(DIST, file), body);
  }
}

main();
