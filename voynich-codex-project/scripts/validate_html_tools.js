#!/usr/bin/env node
/**
 * Validador automático das ferramentas HTML de anotação visual.
 * Uso: node scripts/validate_html_tools.js
 * Não requer interação humana — usa Playwright headless.
 */

const { chromium } = require('/Users/pantani/.claude/skills/playwright-skill/node_modules/playwright');
const path = require('path');

const TOOLS_DIR = path.resolve(__dirname, '../docs/tools');
const TOOLS = [
  { file: 'rota_42b_pacote_html_preenchimento_humano_r32.html', id: 'R42B', dataVar: 'ITEMS' },
  { file: 'rota_42c_calibrador_linhas_baseline_r32.html',        id: 'R42C', dataVar: 'ITEMS' },
  { file: 'rota_42d_sugestoes_opencv_linhas_r32.html',           id: 'R42D', dataVar: 'ITEMS' },
  { file: 'rota_42e_mapa_opencv_linhas_visuais_r32.html',        id: 'R42E', dataVar: 'ITEMS' },
  { file: 'rota_42f_escolha_linhas_visuais_sem_zona_r32.html',   id: 'R42F', dataVar: 'ITEMS' },
  { file: 'rota_42j_fragmentos_visuais_opencv_r32.html',         id: 'R42J', dataVar: 'ITEMS' },
  { file: 'rota_42k_fila_priorizada_revisao_visual_r32.html',    id: 'R42K', dataVar: 'QUEUE_ROWS' },
  { file: 'rota_42l_confirmacao_linhas_sugeridas_r32.html',      id: 'R42L', dataVar: 'ITEMS' },
  { file: 'rota_42m_captura_fina_linhas_r32.html',               id: 'R42M', dataVar: 'ROWS' },
];

const PASS = '✅';
const FAIL = '❌';
const WARN = '⚠️ ';

async function checkTool(browser, tool) {
  const results = [];
  const url = `file://${TOOLS_DIR}/${tool.file}`;
  const page = await browser.newPage();
  await page.setViewportSize({ width: 1600, height: 900 });

  const jsErrors = [];
  const failedImages = [];
  page.on('pageerror', e => jsErrors.push(e.message));
  page.on('response', r => {
    if (!r.ok() && /\.(jpg|jpeg|png|gif|webp)$/i.test(r.url())) {
      failedImages.push(r.url().split('/').slice(-1)[0]);
    }
  });

  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 10000 });
    await page.waitForTimeout(2000);

    // 1. Sem erros de JS
    if (jsErrors.length === 0) {
      results.push({ ok: true, label: 'Sem erros JS' });
    } else {
      results.push({ ok: false, label: `Erros JS: ${jsErrors.slice(0,2).join(' | ')}` });
    }

    // 2. Imagens principais carregadas (naturalWidth > 0)
    const imgCheck = await page.evaluate(() => {
      const imgs = [...document.querySelectorAll('img[src]')].filter(i => i.src && !i.src.includes('data:'));
      if (!imgs.length) return { count: 0, broken: 0 };
      const broken = imgs.filter(i => i.naturalWidth === 0).length;
      return { count: imgs.length, broken };
    });
    if (imgCheck.count === 0) {
      results.push({ ok: null, label: 'Nenhuma <img> encontrada' });
    } else if (imgCheck.broken === 0) {
      results.push({ ok: true, label: `${imgCheck.count} imagem(ns) carregada(s)` });
    } else {
      results.push({ ok: false, label: `${imgCheck.broken}/${imgCheck.count} imagem(ns) com falha` });
    }

    // 3. Canvas de preview renderizados
    const canvasCheck = await page.evaluate(() => {
      const canvases = [...document.querySelectorAll('canvas[data-crop-preview]')];
      if (!canvases.length) return { count: 0, drawn: 0, errors: 0 };
      const drawn = canvases.filter(c => c.width > 0 && c.height > 0).length;
      const errors = canvases.filter(c => c.closest('[data-crop-status="erro"]')).length;
      return { count: canvases.length, drawn, errors };
    });
    if (canvasCheck.count > 0) {
      if (canvasCheck.errors > 0) {
        results.push({ ok: false, label: `Canvas: ${canvasCheck.errors}/${canvasCheck.count} com erro de imagem` });
      } else if (canvasCheck.drawn === canvasCheck.count) {
        results.push({ ok: true, label: `${canvasCheck.count} canvas renderizado(s)` });
      } else {
        results.push({ ok: false, label: `Canvas: ${canvasCheck.drawn}/${canvasCheck.count} desenhados` });
      }
    }

    // 4. Zonas de overlay presentes
    const zoneCheck = await page.evaluate(() => {
      const zones = document.querySelectorAll('.line-zone-choice, .zone-box, .zone-highlight, .zone-fragment');
      const clickable = [...zones].filter(z => window.getComputedStyle(z).pointerEvents === 'auto').length;
      return { total: zones.length, clickable };
    });
    if (zoneCheck.total > 0) {
      // R42K/R42M usam zonas apenas visuais — não é falha se não forem clicáveis
      const isVisualOnly = ['R42K','R42M','R42E','R42D','R42J'].includes(tool.id);
      const ok = zoneCheck.clickable > 0 || isVisualOnly;
      const clickMsg = zoneCheck.clickable > 0 ? `, ${zoneCheck.clickable} clicáveis` : isVisualOnly ? ' (visual, ok)' : ' (não clicáveis)';
      results.push({ ok, label: `${zoneCheck.total} zona(s) overlay${clickMsg}` });
    }

    // 5. Banner de instrução presente (qualquer variante conhecida)
    const hasBanner = await page.$('.step-banner, .simple-guide, .instruction-banner, [class*="banner"], [class*="guide"]')
      .then(el => !!el).catch(() => false);
    results.push({ ok: hasBanner, label: hasBanner ? 'Banner de instrução presente' : 'Banner de instrução ausente' });

    // 6. Contador de progresso (qualquer variante)
    const hasCounter = await page.$('#stepCount, #progressText, #currentCounter, .progress-block, [class*="progress"]')
      .then(el => !!el).catch(() => false);
    results.push({ ok: hasCounter, label: hasCounter ? 'Contador de progresso presente' : 'Contador de progresso ausente' });

    // 7. Clique na primeira zona clicável (se existir)
    const zoneExists = await page.$('.line-zone-choice[style], .zone-box').then(el => !!el).catch(() => false);
    if (zoneExists) {
      // Após selectLine() o renderOverlay() reconstrói o DOM — verificar no DOM novo
      await page.evaluate(() => {
        const zone = document.querySelector('.line-zone-choice[style], .zone-box');
        if (zone) zone.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true }));
      });
      await page.waitForTimeout(500);
      const hasSelected = await page.$('.line-zone-choice.selected, .zone-box.selected, .choice-card.selected')
        .then(el => !!el).catch(() => false);
      results.push({ ok: hasSelected, label: hasSelected ? 'Clique na zona funciona (→ selected)' : 'Clique na zona NÃO selecionou' });
    }

    // 8. Navegação funciona (Próximo) — lê estado ANTES e DEPOIS via evaluate
    const navResult = await page.evaluate(async () => {
      // Captura título/counter dinâmico antes de clicar
      const dynamicEl = document.querySelector(
        '#itemTitle, #targetTitle, #currentCounter, [id$="Title"], [id$="title"]'
      );
      const before = dynamicEl ? dynamicEl.textContent.trim() : null;
      if (!before) return null; // não há elemento dinâmico detectável
      const btn = document.querySelector('#nextItem') || document.querySelector('#nextPending') ||
        [...document.querySelectorAll('button')].find(b => b.textContent.includes('ximo'));
      if (!btn) return null;
      btn.click();
      // Aguarda próximo tick
      await new Promise(r => setTimeout(r, 500));
      const after = dynamicEl.textContent.trim();
      return { before, after };
    });
    if (navResult) {
      const ok = navResult.before !== navResult.after;
      results.push({ ok, label: ok ? 'Navegação próximo funciona' : `Navegação não avançou (${navResult.before.slice(0,20)})` });
    }

  } catch (e) {
    results.push({ ok: false, label: `Erro ao abrir: ${e.message.slice(0, 80)}` });
  } finally {
    await page.close();
  }

  return results;
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const allResults = {};
  let totalPass = 0, totalFail = 0, totalWarn = 0;

  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('  Validador Automático — Ferramentas HTML R42*');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

  for (const tool of TOOLS) {
    process.stdout.write(`${tool.id}  `);
    const results = await checkTool(browser, tool);
    allResults[tool.id] = results;

    const pass = results.filter(r => r.ok === true).length;
    const fail = results.filter(r => r.ok === false).length;
    const warn = results.filter(r => r.ok === null).length;
    totalPass += pass; totalFail += fail; totalWarn += warn;

    const icon = fail > 0 ? FAIL : (warn > 0 ? WARN : PASS);
    console.log(`${icon} ${pass}/${results.length} verificações`);

    results.forEach(r => {
      const icon = r.ok === true ? '  ✓' : r.ok === false ? '  ✗' : '  ~';
      console.log(`${icon} ${r.label}`);
    });
    console.log();
  }

  await browser.close();

  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log(`TOTAL: ${totalPass} ✓  ${totalFail} ✗  ${totalWarn} ~`);
  const score = Math.round((totalPass / (totalPass + totalFail + totalWarn)) * 100);
  console.log(`Score: ${score}%`);
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

  process.exit(totalFail > 0 ? 1 : 0);
}

main().catch(e => { console.error(e); process.exit(1); });
