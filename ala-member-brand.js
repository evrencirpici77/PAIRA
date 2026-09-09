(() => {
  const BRAND = 'ÂLÂ';

  const replaceBrandText = (root) => {
    const scope = root && root.nodeType === 1 ? root : document;
    const walker = document.createTreeWalker(scope, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);

    for (const node of nodes) {
      const parent = node.parentElement;
      if (!parent) continue;
      if (parent.closest('script, style, textarea, input, option')) continue;
      if (node.nodeValue && node.nodeValue.includes('PAIRA')) {
        node.nodeValue = node.nodeValue.replace(/PAIRA/g, BRAND);
      }
      if (node.nodeValue && node.nodeValue.includes('ALA')) {
        node.nodeValue = node.nodeValue.replace(/\bALA\b/g, BRAND);
      }
    }
  };

  const apply = () => {
    document.title = BRAND;
    const appleTitle = document.querySelector('meta[name="apple-mobile-web-app-title"]');
    if (appleTitle) appleTitle.setAttribute('content', BRAND);
    replaceBrandText(document.body || document.documentElement);
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', apply, { once: true });
  } else {
    apply();
  }

  const observer = new MutationObserver((mutations) => {
    for (const mutation of mutations) {
      if (mutation.type === 'characterData') {
        const parent = mutation.target.parentElement;
        if (!parent || parent.closest('script, style, textarea, input, option')) continue;
        const value = mutation.target.nodeValue || '';
        const next = value.replace(/PAIRA/g, BRAND).replace(/\bALA\b/g, BRAND);
        if (next !== value) mutation.target.nodeValue = next;
        continue;
      }
      for (const node of mutation.addedNodes) {
        if (node.nodeType === 1) replaceBrandText(node);
        if (node.nodeType === 3 && node.parentElement && !node.parentElement.closest('script, style, textarea, input, option')) {
          const value = node.nodeValue || '';
          const next = value.replace(/PAIRA/g, BRAND).replace(/\bALA\b/g, BRAND);
          if (next !== value) node.nodeValue = next;
        }
      }
    }
  });

  const startObserver = () => document.body && observer.observe(document.body, { childList: true, subtree: true, characterData: true });
  if (document.body) startObserver();
  else document.addEventListener('DOMContentLoaded', startObserver, { once: true });
})();
