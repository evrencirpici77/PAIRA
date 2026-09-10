(() => {
  const BRAND = 'ÂLÂ';

  const replaceBrandText = (root) => {
    const scope = root && root.nodeType === 1 ? root : document;
    const walker = document.createTreeWalker(scope, NodeFilter.SHOW_TEXT);
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    for (const node of nodes) {
      const parent = node.parentElement;
      if (!parent || parent.closest('script, style, textarea, input, option')) continue;
      if (node.nodeValue && node.nodeValue.includes('PAIRA')) node.nodeValue = node.nodeValue.replace(/PAIRA/g, BRAND);
      if (node.nodeValue && node.nodeValue.includes('ALA')) node.nodeValue = node.nodeValue.replace(/\bALA\b/g, BRAND);
    }
  };

  const apply = () => {
    document.title = BRAND;
    const appleTitle = document.querySelector('meta[name="apple-mobile-web-app-title"]');
    if (appleTitle) appleTitle.setAttribute('content', BRAND);
    replaceBrandText(document.body || document.documentElement);
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', apply, { once: true });
  else apply();

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

  // ÂLÂ member directory: coupleProfiles is the live directory source.
  // Explicitly removed invitations stay hidden; a missing/legacy invitation no longer hides a valid profile.
  let alaDirectory = [];
  let alaDirectoryStarted = false;

  const installMemberFix = async () => {
    if (alaDirectoryStarted) return true;
    if (typeof window.waitForPairaFirebaseApi !== 'function' || typeof window.memberCardFromProfile !== 'function' || typeof window.currentCoupleMember !== 'function') return false;
    alaDirectoryStarted = true;

    const originalRealMembersData = window.realMembersData;
    window.realMembersData = function() {
      const self = window.currentCoupleMember();
      const byId = new Map();
      alaDirectory.forEach(m => { if (m && m.id) byId.set(String(m.id), m); });
      byId.set(String(self.id), self);
      return [...byId.values()].sort((a,b) => {
        if (a.isSelf && !b.isSelf) return -1;
        if (b.isSelf && !a.isSelf) return 1;
        return String(a.name || '').localeCompare(String(b.name || ''), 'tr');
      });
    };

    try {
      const api = await window.waitForPairaFirebaseApi();
      api.subscribeCoupleProfiles(async rows => {
        const checked = await Promise.all((rows || []).map(async profile => {
          const id = String(profile?._firebaseId || '').trim();
          if (!id) return null;
          try {
            const inv = await api.getInvitation(id);
            if (inv && inv.status === 'removed') return null;
          } catch (_) {}
          return window.memberCardFromProfile(profile);
        }));
        alaDirectory = checked.filter(Boolean);
        if (typeof window.renderMembersView === 'function') window.renderMembersView();
        const active = document.querySelector('.screen.active');
        if (active && active.id === 'member' && typeof window.renderSelectedMemberView === 'function') window.renderSelectedMemberView();
      }, err => console.warn('ALA member directory sync', err));
    } catch (err) {
      alaDirectoryStarted = false;
      window.realMembersData = originalRealMembersData;
      console.warn('ALA member directory start', err);
    }
    return true;
  };

  let tries = 0;
  const timer = setInterval(async () => {
    tries += 1;
    if (await installMemberFix() || tries > 40) clearInterval(timer);
  }, 250);
})();
