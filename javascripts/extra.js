// SuperOptix Documentation Enhanced JavaScript
// Professional theme-aware UI enhancements

document.addEventListener('DOMContentLoaded', function() {
  // Initialize all UI enhancements
  initializeThemeHandling();
  initializeReadingProgress();
  initializeSearchEnhancements();
  initializeSmoothScrolling();
  initializeCodeEnhancements();
  initializeNavigationEnhancements();
  initializeAnimations();
  initializeKeyboardNavigation();
  initializePerformanceOptimizations();
});

/* =========================================
   THEME HANDLING
   ========================================= */

function initializeThemeHandling() {
  // Watch for theme changes
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.type === 'attributes' && mutation.attributeName === 'data-md-color-scheme') {
        updateThemeElements();
      }
    });
  });

  // Start observing the document body for theme changes
  observer.observe(document.body, {
    attributes: true,
    attributeFilter: ['data-md-color-scheme']
  });

  // Initial theme setup
  updateThemeElements();
}

function updateThemeElements() {
  const currentTheme = document.body.getAttribute('data-md-color-scheme');
  
  // Update any theme-specific elements
  const themeElements = document.querySelectorAll('[data-theme-element]');
  themeElements.forEach(element => {
    element.classList.toggle('theme-dark', currentTheme === 'slate');
    element.classList.toggle('theme-light', currentTheme === 'default');
  });

  // Update custom elements based on theme
  updateCodeBlocks();
  updateFeatureCards();
}

/* =========================================
   READING PROGRESS INDICATOR
   ========================================= */

function initializeReadingProgress() {
  // Create progress bar element
  const progressBar = document.createElement('div');
  progressBar.className = 'reading-progress';
  progressBar.setAttribute('role', 'progressbar');
  progressBar.setAttribute('aria-label', 'Reading progress');
  document.body.appendChild(progressBar);

  // Update progress on scroll
  function updateProgress() {
    const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = (winScroll / height) * 100;
    progressBar.style.width = scrolled + '%';
    progressBar.setAttribute('aria-valuenow', Math.round(scrolled));
  }

  // Throttled scroll handler
  const throttledUpdateProgress = throttle(updateProgress, 16);
  window.addEventListener('scroll', throttledUpdateProgress);
}

/* =========================================
   SEARCH ENHANCEMENTS
   ========================================= */

function initializeSearchEnhancements() {
  const searchInput = document.querySelector('.md-search__input');
  const searchForm = document.querySelector('.md-search__form');
  
  if (!searchInput || !searchForm) return;

  // Enhanced search with keyboard shortcuts
  document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      searchInput.focus();
      searchInput.select();
    }
    
    // Escape to close search
    if (e.key === 'Escape' && document.activeElement === searchInput) {
      searchInput.blur();
    }
  });

  // Search input animations
  searchInput.addEventListener('focus', function() {
    searchForm.classList.add('search-focused');
    this.setAttribute('aria-expanded', 'true');
  });

  searchInput.addEventListener('blur', function() {
    searchForm.classList.remove('search-focused');
    this.setAttribute('aria-expanded', 'false');
  });

  // Search suggestions enhancement
  let searchTimeout;
  searchInput.addEventListener('input', function() {
    clearTimeout(searchTimeout);
    const query = this.value.trim();
    
    if (query.length > 2) {
      searchTimeout = setTimeout(() => {
        enhanceSearchResults(query);
      }, 300);
    }
  });
}

function enhanceSearchResults(query) {
  // Add search result highlighting and sorting
  const searchResults = document.querySelectorAll('.md-search-result');
  
  searchResults.forEach(result => {
    const title = result.querySelector('.md-search-result__title');
    const content = result.querySelector('.md-search-result__teaser');
    
    if (title && content) {
      highlightSearchTerms(title, query);
      highlightSearchTerms(content, query);
    }
  });
}

function highlightSearchTerms(element, query) {
  const text = element.textContent;
  const regex = new RegExp(`(${query})`, 'gi');
  const highlighted = text.replace(regex, '<mark>$1</mark>');
  element.innerHTML = highlighted;
}

/* =========================================
   SMOOTH SCROLLING
   ========================================= */

function initializeSmoothScrolling() {
  // Enhanced smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      
      if (target) {
        const offsetTop = target.offsetTop - 80; // Account for fixed header
        
        window.scrollTo({
          top: offsetTop,
          behavior: 'smooth'
        });
        
        // Update URL without jumping
        history.pushState(null, null, this.getAttribute('href'));
        
        // Focus management for accessibility
        target.focus();
      }
    });
  });

  // Smooth scroll to top button
  createScrollToTopButton();
}

function createScrollToTopButton() {
  const scrollButton = document.createElement('button');
  scrollButton.className = 'scroll-to-top';
  scrollButton.innerHTML = '↑';
  scrollButton.setAttribute('aria-label', 'Scroll to top');
  scrollButton.setAttribute('title', 'Scroll to top');
  
  // Add styles
  scrollButton.style.cssText = `
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    width: 3rem;
    height: 3rem;
    border-radius: 50%;
    background: var(--primary-gradient);
    color: var(--text-hero);
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    z-index: 1000;
    transform: translateY(100px);
    transition: all 0.3s ease;
    box-shadow: var(--shadow-medium);
  `;

  document.body.appendChild(scrollButton);

  // Show/hide button based on scroll position
  function toggleScrollButton() {
    if (window.scrollY > 500) {
      scrollButton.style.transform = 'translateY(0)';
    } else {
      scrollButton.style.transform = 'translateY(100px)';
    }
  }

  // Scroll to top functionality
  scrollButton.addEventListener('click', function() {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  });

  // Hover effects
  scrollButton.addEventListener('mouseenter', function() {
    this.style.transform = 'translateY(0) scale(1.1)';
  });

  scrollButton.addEventListener('mouseleave', function() {
    this.style.transform = window.scrollY > 500 ? 'translateY(0) scale(1)' : 'translateY(100px) scale(1)';
  });

  window.addEventListener('scroll', throttle(toggleScrollButton, 100));
}

/* =========================================
   CODE ENHANCEMENTS
   ========================================= */

function initializeCodeEnhancements() {
  // Enhanced copy-to-clipboard functionality
  document.querySelectorAll('.md-clipboard').forEach(button => {
    button.addEventListener('click', async function(e) {
      e.preventDefault();
      
      const codeBlock = this.closest('.highlight').querySelector('code');
      if (!codeBlock) return;
      
      const text = codeBlock.textContent;
      
      try {
        await navigator.clipboard.writeText(text);
        showCopyFeedback(this, 'Copied!');
      } catch (err) {
        // Fallback for older browsers
        fallbackCopyTextToClipboard(text);
        showCopyFeedback(this, 'Copied!');
      }
    });
  });

  // Line numbers disabled - using CSS-only approach for better performance
  // document.querySelectorAll('pre code').forEach(addLineNumbers);
}

function addLineNumbers(codeBlock) {
  const lines = codeBlock.textContent.split('\n');
  if (lines.length > 3) { // Only add line numbers for longer code blocks
    const lineNumbers = lines.map((_, i) => i + 1).join('\n');
    const lineNumbersElement = document.createElement('div');
    lineNumbersElement.className = 'line-numbers';
    lineNumbersElement.style.cssText = `
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 3rem;
      background: rgba(0, 0, 0, 0.1);
      color: var(--text-muted);
      font-size: 0.8rem;
      line-height: 1.5;
      padding: 1.5rem 0.5rem;
      border-right: 1px solid var(--border-light);
      user-select: none;
    `;
    lineNumbersElement.textContent = lineNumbers;
    
    const preElement = codeBlock.parentElement;
    preElement.style.position = 'relative';
    preElement.style.paddingLeft = '4rem';
    preElement.appendChild(lineNumbersElement);
  }
}



function showCopyFeedback(button, message) {
  const originalContent = button.innerHTML;
  button.innerHTML = '✓';
  button.style.background = 'var(--secondary-gradient)';
  
  setTimeout(() => {
    button.innerHTML = originalContent;
    button.style.background = 'var(--text-accent)';
  }, 2000);
}

function fallbackCopyTextToClipboard(text) {
  const textArea = document.createElement('textarea');
  textArea.value = text;
  textArea.style.position = 'fixed';
  textArea.style.left = '-999999px';
  textArea.style.top = '-999999px';
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();
  
  try {
    document.execCommand('copy');
  } catch (err) {
    console.error('Fallback: Oops, unable to copy', err);
  }
  
  document.body.removeChild(textArea);
}

/* =========================================
   NAVIGATION ENHANCEMENTS
   ========================================= */

function initializeNavigationEnhancements() {
  // Enhanced navigation with keyboard support
  const navLinks = document.querySelectorAll('.md-nav__link');
  
  navLinks.forEach(link => {
    // Add ripple effect on click
    link.addEventListener('click', function(e) {
      createRippleEffect(this, e);
    });
    
    // Enhanced focus management
    link.addEventListener('focus', function() {
      this.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    });
  });

  // Auto-collapse navigation on mobile after selection
  if (window.innerWidth < 768) {
    navLinks.forEach(link => {
      link.addEventListener('click', function() {
        setTimeout(() => {
          const sidebar = document.querySelector('.md-sidebar--primary');
          if (sidebar) {
            sidebar.classList.remove('md-sidebar--primary');
          }
        }, 300);
      });
    });
  }
}

function createRippleEffect(element, event) {
  const circle = document.createElement('span');
  const diameter = Math.max(element.clientWidth, element.clientHeight);
  const radius = diameter / 2;
  
  circle.style.width = circle.style.height = `${diameter}px`;
  circle.style.left = `${event.clientX - element.offsetLeft - radius}px`;
  circle.style.top = `${event.clientY - element.offsetTop - radius}px`;
  circle.classList.add('ripple');
  
  // Add ripple styles
  circle.style.cssText += `
    position: absolute;
    border-radius: 50%;
    transform: scale(0);
    animation: ripple 600ms linear;
    background-color: rgba(255, 255, 255, 0.6);
    pointer-events: none;
  `;
  
  // Add ripple animation
  const style = document.createElement('style');
  style.textContent = `
    @keyframes ripple {
      to {
        transform: scale(4);
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(style);
  
  const ripple = element.querySelector('.ripple');
  if (ripple) {
    ripple.remove();
  }
  
  element.appendChild(circle);
}

/* =========================================
   ANIMATIONS
   ========================================= */

function initializeAnimations() {
  // Intersection Observer for scroll animations
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');
      }
    });
  }, observerOptions);

  // Observe elements for animation (tables excluded to prevent layout issues)
  document.querySelectorAll('.hero-section, .feature-card, .md-typeset h2, .admonition').forEach(el => {
    observer.observe(el);
  });

  // Add animation classes
  const animationStyles = document.createElement('style');
  animationStyles.textContent = `
    .animate-in {
      animation: slideInUp 0.6s ease-out forwards;
    }
    
    @keyframes slideInUp {
      from {
        opacity: 0;
        transform: translateY(30px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
  `;
  document.head.appendChild(animationStyles);

  // Hero image scroll animation
  const heroImage = document.querySelector('.hero-image-container img');
  if (heroImage) {
    window.addEventListener('scroll', () => {
      const scrollPosition = window.scrollY;
      const scale = Math.max(0.8, 1 - scrollPosition / 1000);
      heroImage.style.transform = `scale(${scale})`;
    });
  }
}

/* =========================================
   KEYBOARD NAVIGATION
   ========================================= */

function initializeKeyboardNavigation() {
  // Enhanced keyboard navigation
  document.addEventListener('keydown', function(e) {
    // Tab navigation enhancement
    if (e.key === 'Tab') {
      document.body.classList.add('using-keyboard');
    }
    
    // Navigation shortcuts
    if (e.altKey) {
      switch(e.key) {
        case 'h':
          e.preventDefault();
          document.querySelector('.md-header__title')?.focus();
          break;
        case 'n':
          e.preventDefault();
          document.querySelector('.md-nav__link')?.focus();
          break;
        case 'm':
          e.preventDefault();
          document.querySelector('.md-content')?.focus();
          break;
      }
    }
  });

  // Remove keyboard class on mouse use
  document.addEventListener('mousedown', function() {
    document.body.classList.remove('using-keyboard');
  });

  // Add keyboard navigation styles
  const keyboardStyles = document.createElement('style');
  keyboardStyles.textContent = `
    .using-keyboard *:focus {
      outline: 3px solid var(--text-accent);
      outline-offset: 2px;
    }
    
    .using-keyboard .md-nav__link:focus {
      background: var(--nav-active);
      color: var(--text-hero);
    }
  `;
  document.head.appendChild(keyboardStyles);
}

/* =========================================
   PERFORMANCE OPTIMIZATIONS
   ========================================= */

function initializePerformanceOptimizations() {
  // Lazy loading for images
  const images = document.querySelectorAll('img[data-src]');
  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.classList.remove('lazy');
        imageObserver.unobserve(img);
      }
    });
  });

  images.forEach(img => imageObserver.observe(img));

  // Preload critical resources
  const criticalResources = [
    '/stylesheets/extra.css',
    '/javascripts/extra.js'
  ];

  criticalResources.forEach(resource => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = resource;
    link.as = resource.endsWith('.css') ? 'style' : 'script';
    document.head.appendChild(link);
  });
}

/* =========================================
   UTILITY FUNCTIONS
   ========================================= */

function throttle(func, limit) {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

function debounce(func, wait, immediate) {
  let timeout;
  return function() {
    const context = this;
    const args = arguments;
    const later = function() {
      timeout = null;
      if (!immediate) func.apply(context, args);
    };
    const callNow = immediate && !timeout;
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
    if (callNow) func.apply(context, args);
  };
}

function updateCodeBlocks() {
  // Update code blocks for current theme
  document.querySelectorAll('pre code').forEach(block => {
    const theme = document.body.getAttribute('data-md-color-scheme');
    block.classList.toggle('theme-dark', theme === 'slate');
    block.classList.toggle('theme-light', theme === 'default');
  });
}

function updateFeatureCards() {
  // Update feature cards for current theme
  document.querySelectorAll('.feature-card').forEach(card => {
    const theme = document.body.getAttribute('data-md-color-scheme');
    card.classList.toggle('theme-dark', theme === 'slate');
    card.classList.toggle('theme-light', theme === 'default');
  });
}

/* =========================================
   ACCESSIBILITY ENHANCEMENTS
   ========================================= */

// Skip link for keyboard navigation
function addSkipLink() {
  const skipLink = document.createElement('a');
  skipLink.href = '#main-content';
  skipLink.textContent = 'Skip to main content';
  skipLink.className = 'skip-link';
  skipLink.style.cssText = `
    position: absolute;
    top: -40px;
    left: 6px;
    background: var(--text-accent);
    color: var(--text-hero);
    padding: 8px;
    text-decoration: none;
    border-radius: 4px;
    z-index: 1001;
    transition: top 0.3s;
  `;
  
  skipLink.addEventListener('focus', function() {
    this.style.top = '6px';
  });
  
  skipLink.addEventListener('blur', function() {
    this.style.top = '-40px';
  });
  
  document.body.insertBefore(skipLink, document.body.firstChild);
}

// Initialize accessibility features
document.addEventListener('DOMContentLoaded', function() {
  addSkipLink();
  
  // Add main content ID for skip link
  const mainContent = document.querySelector('.md-content');
  if (mainContent) {
    mainContent.id = 'main-content';
    mainContent.setAttribute('tabindex', '-1');
  }
});

/* =========================================
   ENHANCED FEATURES
   ========================================= */

// Add enhanced table of contents
function enhanceTableOfContents() {
  const toc = document.querySelector('.md-nav--secondary');
  if (!toc) return;
  
  // Add smooth scrolling to TOC links
  toc.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
}

// Initialize enhanced features
document.addEventListener('DOMContentLoaded', function() {
  enhanceTableOfContents();
});

// Export functions for external use
window.SuperOptixDocs = {
  throttle,
  debounce,
  updateThemeElements,
  enhanceSearchResults,
  createRippleEffect
}; 