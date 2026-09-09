(() => {
  const replaceBrandText = (root) => {
    const scope = root && root.nodeType === 1 ? root : document;
    const screens = scope.matches?.('.screen') ? [scope] : [...scope.querySelectorAll?.('.screen') || []];
    const targets = screens.length ? screens : [document.body];

    for (const target of targets) {
      if (!target) continue;
      const id = String(target.id || '');
      if (id.startsWith('admin')) continue;

      const walker = document.createTreeWalker(target, NodeFilter.SHOW_TEXT);
      const nodes = [];
      while (walker.nextNode()) nodes.push(walker.currentNode);

      for (const node of nodes) {
        const parent = node.parentElement;
        if (!parent) continue;
        if (parent.closest('[id^="admin"], .admin, script, style, textarea, input, option')) continue;
        if (node.nodeValue && node.nodeValue.includes('PAIRA')) {
          node.nodeValue = node.nodeValue.replace(/PAIRA/g, 'ALA');
        }
      }
    }
  };

  const apply = () => {
    document.title = 'ALA';
    replaceBrandText(document);
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
        if (parent && !parent.closest('[id^="admin"], .admin, script, style, textarea, input, option') && mutation.target.nodeValue?.includes('PAIRA')) {
          mutation.target.nodeValue = mutation.target.nodeValue.replace(/PAIRA/g, 'ALA');
        }
        continue;
      }
      for (const node of mutation.addedNodes) {
        if (node.nodeType === 1) replaceBrandText(node);
        if (node.nodeType === 3 && node.nodeValue?.includes('PAIRA')) {
          const parent = node.parentElement;
          if (parent && !parent.closest('[id^="admin"], .admin, script, style, textarea, input, option')) {
            node.nodeValue = node.nodeValue.replace(/PAIRA/g, 'ALA');
          }
        }
      }
    }
  });

  const startObserver = () => document.body && observer.observe(document.body, { childList: true, subtree: true, characterData: true });
  if (document.body) startObserver();
  else document.addEventListener('DOMContentLoaded', startObserver, { once: true });
})();
