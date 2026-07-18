(function () {
  'use strict';

  var THEMES = ['light', 'dark', 'blue', 'purple', 'emerald', 'orange', 'black'];

  function applyTheme(theme) {
    if (THEMES.indexOf(theme) === -1) theme = 'dark';
    document.documentElement.setAttribute('data-wl-theme', theme);
    localStorage.setItem('wl-theme', theme);
    document.querySelectorAll('button[data-wl-theme]').forEach(function (btn) {
      btn.classList.toggle('active', btn.getAttribute('data-wl-theme') === theme);
    });
  }

  function closeAllDropdowns() {
    document.querySelectorAll('[data-wl-dropdown].open').forEach(function (d) {
      d.classList.remove('open');
      var t = d.querySelector('.wl-saas-dropdown-trigger');
      if (t) t.setAttribute('aria-expanded', 'false');
    });
  }

  function initDropdowns() {
    document.querySelectorAll('[data-wl-dropdown]').forEach(function (wrap) {
      var trigger = wrap.querySelector('.wl-saas-dropdown-trigger');
      if (!trigger) return;

      trigger.addEventListener('click', function (e) {
        e.stopPropagation();
        var open = wrap.classList.contains('open');
        document.querySelectorAll('[data-wl-dropdown].open').forEach(function (d) {
          if (d !== wrap) {
            d.classList.remove('open');
            var t = d.querySelector('.wl-saas-dropdown-trigger');
            if (t) t.setAttribute('aria-expanded', 'false');
          }
        });
        wrap.classList.toggle('open', !open);
        trigger.setAttribute('aria-expanded', !open ? 'true' : 'false');
      });

      wrap.querySelectorAll('.wl-saas-dropdown-menu a, .wl-saas-dropdown-menu button').forEach(function (item) {
        item.addEventListener('click', function (e) {
          e.stopPropagation();
          if (item.tagName === 'BUTTON' && !item.hasAttribute('data-wl-theme') && !item.closest('.wl-saas-dropdown-menu--themes')) {
            wrap.classList.remove('open');
            trigger.setAttribute('aria-expanded', 'false');
          }
        });
      });
    });

    document.addEventListener('click', function (e) {
      if (!e.target.closest('[data-wl-dropdown]')) {
        closeAllDropdowns();
      }
    });
  }

  function initThemeEngine() {
    applyTheme(localStorage.getItem('wl-theme') || 'dark');
    document.querySelectorAll('button[data-wl-theme]').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        applyTheme(btn.getAttribute('data-wl-theme'));
        var parent = btn.closest('[data-wl-dropdown]');
        if (parent) {
          parent.classList.remove('open');
          var t = parent.querySelector('.wl-saas-dropdown-trigger');
          if (t) t.setAttribute('aria-expanded', 'false');
        }
      });
    });
  }

  function initNavDropdowns() {
    document.querySelectorAll('[data-nav-dropdown]').forEach(function (dropdown) {
      var toggle = dropdown.querySelector('.wl-saas-nav-toggle');
      if (!toggle) return;
      toggle.addEventListener('click', function () {
        if (document.body.classList.contains('wl-sidebar-collapsed')) return;
        var isOpen = dropdown.classList.contains('open');
        document.querySelectorAll('[data-nav-dropdown].open').forEach(function (d) {
          if (d !== dropdown) {
            d.classList.remove('open');
            var t = d.querySelector('.wl-saas-nav-toggle');
            if (t) t.setAttribute('aria-expanded', 'false');
          }
        });
        dropdown.classList.toggle('open', !isOpen);
        toggle.setAttribute('aria-expanded', !isOpen ? 'true' : 'false');
      });
    });
  }

  function updateCollapseIcon() {
    var btn = document.getElementById('wlSidebarCollapse');
    if (!btn) return;
    var icon = btn.querySelector('i');
    if (!icon) return;
    icon.className = document.body.classList.contains('wl-sidebar-collapsed')
      ? 'mdi mdi-menu-open'
      : 'mdi mdi-backburger';
  }

  function initSidebar() {
    var collapseBtn = document.getElementById('wlSidebarCollapse');
    var mobileBtn = document.getElementById('wlSidebarMobile');
    var sidebar = document.getElementById('wlSaasSidebar');
    var overlay = document.getElementById('wlSidebarOverlay');

    if (collapseBtn) {
      var collapsed = localStorage.getItem('wl-sidebar-collapsed') === '1';
      if (collapsed) document.body.classList.add('wl-sidebar-collapsed');
      updateCollapseIcon();
      collapseBtn.addEventListener('click', function () {
        document.body.classList.toggle('wl-sidebar-collapsed');
        localStorage.setItem('wl-sidebar-collapsed', document.body.classList.contains('wl-sidebar-collapsed') ? '1' : '0');
        updateCollapseIcon();
      });
    }

    function openMobileNav() {
      sidebar.classList.add('mobile-open');
      if (overlay) overlay.classList.add('open');
      document.body.classList.add('wl-mobile-nav-open');
    }
    function closeMobileNav() {
      sidebar.classList.remove('mobile-open');
      if (overlay) overlay.classList.remove('open');
      document.body.classList.remove('wl-mobile-nav-open');
    }

    if (mobileBtn && sidebar) {
      mobileBtn.addEventListener('click', function () {
        if (sidebar.classList.contains('mobile-open')) closeMobileNav();
        else openMobileNav();
      });
    }
    if (overlay) {
      overlay.addEventListener('click', closeMobileNav);
    }
    if (sidebar) {
      // Close the drawer after tapping a real navigation link on mobile
      sidebar.querySelectorAll('.wl-saas-nav-link[href]').forEach(function (link) {
        link.addEventListener('click', function () {
          if (window.matchMedia('(max-width: 900px)').matches) closeMobileNav();
        });
      });
    }
    // Reset the drawer state when resizing back to desktop
    window.addEventListener('resize', function () {
      if (!window.matchMedia('(max-width: 900px)').matches) closeMobileNav();
    });
  }

  function initSupportWidget() {
    var fab = document.getElementById('wlSupportFab');
    var trigger = document.getElementById('wlSupportTrigger');
    var panel = document.getElementById('wlSupportPanel');
    if (!fab || !trigger || !panel) return;

    trigger.addEventListener('click', function (e) {
      e.stopPropagation();
      var isOpen = fab.classList.toggle('open');
      panel.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
    });

    document.addEventListener('click', function (e) {
      if (!fab.contains(e.target)) {
        fab.classList.remove('open');
        panel.setAttribute('aria-hidden', 'true');
      }
    });
  }

  function initQuickFab() {
    var fab = document.getElementById('wlQuickFab');
    var trigger = document.getElementById('wlQuickFabTrigger');
    var menu = document.getElementById('wlQuickFabMenu');
    if (!fab || !trigger || !menu) return;

    trigger.addEventListener('click', function (e) {
      e.stopPropagation();
      var isOpen = fab.classList.toggle('open');
      menu.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
    });

    document.addEventListener('click', function (e) {
      if (!fab.contains(e.target)) {
        fab.classList.remove('open');
        menu.setAttribute('aria-hidden', 'true');
      }
    });
  }

  function animateCounter(el, target, duration) {
    var start = 0;
    var startTime = null;
    target = parseFloat(String(target).replace(/,/g, '')) || 0;
    if (target === 0) { el.textContent = '0'; return; }

    function step(ts) {
      if (!startTime) startTime = ts;
      var progress = Math.min((ts - startTime) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      var val = Math.floor(start + (target - start) * eased);
      el.textContent = val.toLocaleString('en-IN');
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = target.toLocaleString('en-IN');
    }
    requestAnimationFrame(step);
  }

  function initCounters() {
    document.querySelectorAll('.wl-metric-value[data-count]').forEach(function (el) {
      animateCounter(el, el.getAttribute('data-count'), 1200);
    });
    document.querySelectorAll('.wl-metric-value span[data-count]').forEach(function (span) {
      animateCounter(span, span.getAttribute('data-count'), 1400);
    });
  }

  function getGoogTransLang() {
    var m = document.cookie.match(/googtrans=\/[a-z]+\/([a-z]+)/);
    return m ? m[1] : 'en';
  }

  function setGoogTransLang(lang) {
    var host = location.hostname;
    var expired = ';expires=Thu, 01 Jan 1970 00:00:00 GMT';
    // Clear any existing cookie across possible scopes
    ['', ';domain=' + host, ';domain=.' + host].forEach(function (scope) {
      document.cookie = 'googtrans=;path=/' + scope + expired;
    });
    if (lang && lang !== 'en') {
      var val = '/en/' + lang;
      ['', ';domain=' + host, ';domain=.' + host].forEach(function (scope) {
        document.cookie = 'googtrans=' + val + ';path=/' + scope;
      });
    }
    window.location.reload();
  }

  function hideGoogleBanner() {
    // Google injects an inline top offset on <body> and a banner iframe — kill both
    if (document.body && document.body.style.top && document.body.style.top !== '0px') {
      document.body.style.top = '0px';
    }
    var frames = document.querySelectorAll(
      'iframe.goog-te-banner-frame, .goog-te-banner-frame, .skiptranslate iframe'
    );
    frames.forEach(function (f) {
      f.style.display = 'none';
      f.style.visibility = 'hidden';
    });
    var tt = document.getElementById('goog-gt-tt');
    if (tt) tt.style.display = 'none';
  }

  function initGoogleBannerGuard() {
    hideGoogleBanner();
    // Google renders asynchronously, so keep enforcing for a short window
    var tries = 0;
    var timer = setInterval(function () {
      hideGoogleBanner();
      if (++tries > 40) clearInterval(timer);
    }, 250);
    // And react to any later DOM mutations (e.g. hover tooltips)
    if (window.MutationObserver) {
      new MutationObserver(hideGoogleBanner).observe(document.documentElement, {
        childList: true,
        subtree: true,
      });
    }
  }

  function initLangSwitcher() {
    var buttons = document.querySelectorAll('button[data-wl-lang]');
    if (!buttons.length) return;
    var current = getGoogTransLang();
    var label = document.getElementById('wlLangLabel');
    if (label) label.textContent = current.toUpperCase();

    buttons.forEach(function (btn) {
      var lang = btn.getAttribute('data-wl-lang');
      btn.classList.toggle('active', lang === current);
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        if (lang === current) return;
        setGoogTransLang(lang);
      });
    });
  }

  function initKeyboardSearch() {
    document.addEventListener('keydown', function (e) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        var input = document.querySelector('.wl-saas-search input');
        if (input) input.focus();
      }
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initThemeEngine();
    initDropdowns();
    initSidebar();
    initNavDropdowns();
    initSupportWidget();
    initQuickFab();
    initCounters();
    initKeyboardSearch();
    initLangSwitcher();
    initGoogleBannerGuard();
  });
})();
