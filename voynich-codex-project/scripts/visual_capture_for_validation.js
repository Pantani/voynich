/**
 * Captura screenshots de elementos específicos para análise visual posterior.
 * Playwright usa compositor Chromium — não tem CORS para screenshots.
 */
const fs = require('fs');
const path = require('path');

// Playwright: tenta instalação local primeiro, depois skill directory
let chromium;
try {
  ({ chromium } = require('playwright'));
} catch {
  try {
    ({ chromium } = require(path.join(require('os').homedir(), '.claude/skills/playwright-skill/node_modules/playwright')));
  } catch {
    console.error('Playwright não encontrado. Instale: npm install playwright && npx playwright install chromium');
    process.exit(1);
  }
}

// Caminhos relativos ao script — funciona de qualquer diretório
const SCRIPT_DIR = __dirname;
const PROJECT_DIR = path.resolve(SCRIPT_DIR, '..');
const TOOLS_DIR = 'file://' + path.join(PROJECT_DIR, 'docs/tools');
const OUT = '/tmp/visual-caps';
fs.mkdirSync(OUT, { recursive: true });

const TOOLS = [
  { id: 'R42F', file: 'rota_42f_escolha_linhas_visuais_sem_zona_r32.html' },
  { id: 'R42K', file: 'rota_42k_fila_priorizada_revisao_visual_r32.html' },
  { id: 'R42L', file: 'rota_42l_confirmacao_linhas_sugeridas_r32.html' },
  { id: 'R42M', file: 'rota_42m_captura_fina_linhas_r32.html' },
  { id: 'R42B', file: 'rota_42b_pacote_html_preenchimento_humano_r32.html' },
];

async function main() {
  const browser = await chromium.launch({ headless: true });
  const manifest = {};

  for (const tool of TOOLS) {
    const page = await browser.newPage();
    await page.setViewportSize({ width: 1600, height: 900 });
    await page.goto(`${TOOLS_DIR}/${tool.file}`, { waitUntil: 'domcontentloaded' });
    // Aguarda até primeira imagem Yale IIIF carregar (máx 8s), depois espera mais 1s para canvases
    await page.waitForFunction(() => {
      const imgs = document.querySelectorAll('img[src*="yale_iiif"], img[src*="images/raw"]');
      return imgs.length === 0 || [...imgs].some(i => i.naturalWidth > 0);
    }, { timeout: 8000 }).catch(() => {});
    await page.waitForTimeout(1000);

    const caps = [];

    // 1. Screenshot completo
    const fullPath = `${OUT}/${tool.id}_full.png`;
    await page.screenshot({ path: fullPath });
    caps.push({ type: 'full_page', path: fullPath });

    // 2. Screenshot da imagem principal do manuscrito
    const mainImgSel = '#mainImage, #sourceImage, #folioImage, .mini-stage img, img[src*="yale_iiif"]';
    const mainImg = page.locator(mainImgSel).first();
    if (await mainImg.count() > 0) {
      const imgPath = `${OUT}/${tool.id}_manuscript.png`;
      await mainImg.screenshot({ path: imgPath }).catch(() => null);
      caps.push({ type: 'manuscript_image', path: imgPath });

      // 3. Screenshot da zona de overlay (se existir) + imagem de fundo
      const zoneCount = await page.locator('.line-zone-choice, .zone-box, .zone-highlight').count();
      if (zoneCount > 0) {
        // Screenshot da image-stage inteira (inclui overlay)
        const stageSel = '.image-stage, .mini-stage, [id="imageStage"], [id="miniStage"]';
        const stage = page.locator(stageSel).first();
        if (await stage.count() > 0) {
          const stagePath = `${OUT}/${tool.id}_with_zones.png`;
          await stage.screenshot({ path: stagePath }).catch(() => null);
          caps.push({ type: 'image_with_zones', path: stagePath, zoneCount });
        }

        // Também screenshot de cada zona individualmente
        const zones = page.locator('.line-zone-choice, .zone-box, .zone-highlight');
        const n = Math.min(await zones.count(), 3);
        for (let i = 0; i < n; i++) {
          const zonePath = `${OUT}/${tool.id}_zone_${i+1}.png`;
          await zones.nth(i).screenshot({ path: zonePath }).catch(() => null);
          caps.push({ type: `zone_${i+1}`, path: zonePath });
        }
      }
    }

    // 4. Screenshot dos canvas de preview (até 3)
    const canvases = page.locator('canvas[data-crop-preview]');
    const nCanvas = Math.min(await canvases.count(), 3);
    for (let i = 0; i < nCanvas; i++) {
      const canvasPath = `${OUT}/${tool.id}_canvas_${i+1}.png`;
      await canvases.nth(i).screenshot({ path: canvasPath }).catch(() => null);
      caps.push({ type: `canvas_crop_${i+1}`, path: canvasPath });
    }

    // 5. Metadados extras: número de zonas, status
    const meta = await page.evaluate(() => ({
      zoneCount: document.querySelectorAll('.line-zone-choice, .zone-box, .zone-highlight').length,
      canvasCount: document.querySelectorAll('canvas[data-crop-preview]').length,
      bannerText: (document.querySelector('.step-banner, .simple-guide') || {}).textContent?.trim()?.slice(0, 80) || '',
      imgNaturalWidth: (() => {
        const imgs = document.querySelectorAll('#mainImage, #sourceImage, #folioImage, .mini-stage img, img[src*="yale_iiif"], img[src*="images/raw"]');
        const loaded = [...imgs].find(i => i.naturalWidth > 0);
        return loaded ? loaded.naturalWidth : 0;
      })(),
      imagesTotal: document.querySelectorAll('img[src*="yale_iiif"], img[src*="images/raw"]').length,
      imagesLoaded: [...document.querySelectorAll('img[src*="yale_iiif"], img[src*="images/raw"]')].filter(i => i.naturalWidth > 0).length,
    }));

    manifest[tool.id] = { file: tool.file, caps, meta };
    await page.close();
    console.log(`${tool.id}: ${caps.length} capturas → ${JSON.stringify(meta)}`);
  }

  // Salva manifest para o Python ler
  fs.writeFileSync(`${OUT}/manifest.json`, JSON.stringify(manifest, null, 2));
  await browser.close();
  console.log(`\nManifest: ${OUT}/manifest.json`);
}

main().catch(e => { console.error(e); process.exit(1); });
