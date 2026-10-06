// Dependency-free checks for persistence, accessibility preferences and animation recovery.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = name => fs.readFileSync(path.join(__dirname, '../js', name), 'utf8');
let checks = 0;

function fixture({saved = null, systemDark = false, reduced = false, storageBlocked = false, transition = 'supported'} = {}) {
  const attributes = {};
  const listeners = {};
  const classes = new Set();
  const status = {textContent: ''};
  const meta = {setAttribute(name, value) { this[name] = value; }};
  const storage = new Map(saved === null ? [] : [['anekdote-theme', saved]]);
  const animations = [];
  const button = {
    title: '',
    setAttribute(name, value) { attributes[name] = value; },
    addEventListener(name, callback) { listeners[name] = callback; },
    getBoundingClientRect: () => ({left: 900, top: 20, width: 64, height: 44})
  };
  const root = {
    dataset: {},
    classList: {add: name => classes.add(name), remove: name => classes.delete(name)},
    animate(keyframes, options) { animations.push({keyframes, options}); return {finished: Promise.resolve()}; }
  };
  const system = {matches: systemDark, addEventListener(name, callback) { this.change = callback; }};
  const motion = {matches: reduced};
  const document = {
    documentElement: root,
    querySelectorAll: () => [button],
    querySelector: selector => selector.includes('theme-color') ? meta : status
  };
  let snapshots = 0;
  let skipped = false;
  if (transition !== 'unsupported') document.startViewTransition = update => {
    snapshots++;
    update();
    return {
      ready: transition === 'skipped' ? Promise.reject(new Error('Snapshot unavailable')) : Promise.resolve(),
      finished: Promise.resolve(),
      skipTransition() { skipped = true; }
    };
  };
  const windowEvents = {};
  const context = vm.createContext({
    document, innerWidth: 1280, innerHeight: 800,
    matchMedia: query => query.includes('reduced-motion') ? motion : system,
    localStorage: {
      getItem(key) { if (storageBlocked) throw new Error('Storage denied'); return storage.get(key) ?? null; },
      setItem(key, value) { if (storageBlocked) throw new Error('Storage denied'); storage.set(key, value); }
    },
    window: {addEventListener(name, callback) { windowEvents[name] = callback; }},
    setTimeout: () => 1, clearTimeout: () => {}
  });
  vm.runInContext(source('theme-init.js'), context);
  vm.runInContext(source('theme.js'), context);
  return {buttonTitle: () => button.title, root, attributes, status, meta, storage, system, listeners, classes, animations, windowEvents, get snapshots() { return snapshots; }, get skipped() { return skipped; }};
}

(async () => {
  let f = fixture({saved: 'dark'});
  assert.equal(f.root.dataset.theme, 'dark');
  assert.equal(f.buttonTitle(), 'Passer au thème clair');
  assert.equal(f.attributes['aria-checked'], 'true');
  assert.equal(f.meta.content, '#191918');
  checks++;

  f = fixture({systemDark: true});
  assert.equal(f.root.dataset.theme, 'dark');
  f.system.change({matches: false});
  assert.equal(f.root.dataset.theme, 'light');
  checks++;

  f = fixture({saved: 'light', systemDark: true});
  f.system.change({matches: true});
  assert.equal(f.root.dataset.theme, 'light');
  checks++;

  f = fixture({reduced: true});
  await f.listeners.click();
  assert.equal(f.root.dataset.theme, 'dark');
  assert.equal(f.storage.get('anekdote-theme'), 'dark');
  assert.equal(f.buttonTitle(), 'Passer au thème clair');
  assert.equal(f.status.textContent, 'Thème sombre activé.');
  assert.equal(f.snapshots, 0);
  assert.equal(f.animations.length, 0);
  assert.equal(f.classes.size, 0);
  checks++;

  f = fixture({storageBlocked: true, reduced: true});
  await f.listeners.click();
  assert.equal(f.root.dataset.theme, 'dark');
  assert.equal(f.attributes['aria-checked'], 'true');
  checks++;

  f = fixture({transition: 'unsupported'});
  await f.listeners.click();
  assert.equal(f.root.dataset.theme, 'dark');
  assert.equal(f.classes.has('theme-fading'), true);
  assert.equal(f.animations.length, 0);
  checks++;

  f = fixture();
  const first = f.listeners.click();
  const repeated = f.listeners.click();
  await Promise.all([first, repeated]);
  assert.equal(f.snapshots, 1);
  assert.equal(f.animations[0].options.duration, 620);
  assert.equal(f.animations[0].options.pseudoElement, '::view-transition-new(root)');
  assert.equal(f.classes.has('theme-reveal'), false);
  assert.equal(f.root.dataset.theme, 'dark');
  await f.listeners.click();
  assert.equal(f.root.dataset.theme, 'light');
  assert.equal(f.storage.get('anekdote-theme'), 'light');
  checks++;

  f = fixture({transition: 'skipped'});
  await f.listeners.click();
  assert.equal(f.root.dataset.theme, 'dark');
  assert.equal(f.skipped, true);
  assert.equal(f.classes.has('theme-reveal'), false);
  await f.listeners.click();
  assert.equal(f.root.dataset.theme, 'light');
  checks++;

  f = fixture();
  f.windowEvents.storage({key: 'anekdote-theme', newValue: 'dark'});
  assert.equal(f.root.dataset.theme, 'dark');
  assert.equal(f.attributes['aria-checked'], 'true');
  f.windowEvents.storage({key: 'anekdote-theme', newValue: null});
  assert.equal(f.root.dataset.theme, 'light');
  checks++;

  console.log(`${checks} theme checks passed.`);
})().catch(error => { console.error(error); process.exitCode = 1; });
