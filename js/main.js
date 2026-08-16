/**
 * Nutrifresh Eggs - Interactive Controllers & UI Dynamics
 * Inspired by HappyEgg.com
 */

document.addEventListener('DOMContentLoaded', () => {

  /* ==========================================================================
     1. Header Scroll Dynamics
     ========================================================================== */
  const header = document.getElementById('header');
  if (header) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 40) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
    });
  }

  /* ==========================================================================
     2. Full-Screen Navigation Drawer
     ========================================================================== */
  const menuToggle = document.getElementById('menuToggle');
  const navDrawer = document.getElementById('navDrawer');
  const drawerLinks = document.querySelectorAll('.drawer-nav-link');

  function toggleDrawer() {
    if (!menuToggle || !navDrawer) return;
    menuToggle.classList.toggle('active');
    navDrawer.classList.toggle('active');
    
    if (navDrawer.classList.contains('active')) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
  }

  if (menuToggle) {
    menuToggle.addEventListener('click', toggleDrawer);
  }

  drawerLinks.forEach(link => {
    link.addEventListener('click', () => {
      if (navDrawer && navDrawer.classList.contains('active')) {
        toggleDrawer();
      }
    });
  });

  // Close drawer on ESC key
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && navDrawer && navDrawer.classList.contains('active')) {
      toggleDrawer();
    }
  });

  /* ==========================================================================
     3. Splide.js Product Carousel
     ========================================================================== */
  const productCarouselEl = document.getElementById('productCarousel');
  if (productCarouselEl && typeof Splide !== 'undefined') {
    const splide = new Splide('#productCarousel', {
      type: 'slide',
      perPage: 3,
      perMove: 1,
      gap: '30px',
      arrows: true,
      pagination: true,
      drag: true,
      breakpoints: {
        1024: {
          perPage: 2,
          gap: '24px'
        },
        768: {
          perPage: 1,
          gap: '16px'
        }
      }
    });
    splide.mount();
  }

  /* ==========================================================================
     4. Carousel Drag Cursor
     ========================================================================== */
  const carousel = document.getElementById('productCarousel');
  const customCursor = document.getElementById('carouselCursor');

  if (carousel && customCursor) {
    carousel.addEventListener('mouseenter', () => {
      customCursor.classList.add('active');
    });

    carousel.addEventListener('mouseleave', () => {
      customCursor.classList.remove('active');
    });

    carousel.addEventListener('mousemove', (e) => {
      customCursor.style.left = `${e.clientX - 40}px`;
      customCursor.style.top = `${e.clientY - 40}px`;
    });
  }

  /* ==========================================================================
     5. Interactive Yolk Scale Slider (1:1 with HappyEgg)
     ========================================================================== */
  const yolkSlider = document.getElementById('yolkSlider');
  const yolkCurrentScore = document.getElementById('yolkCurrentScore');
  const yolkLevelTitle = document.getElementById('yolkLevelTitle');
  const yolkLevelDesc = document.getElementById('yolkLevelDesc');
  const vitDStat = document.getElementById('vitDStat');
  const omegaStat = document.getElementById('omegaStat');

  const yolkData = {
    standard: {
      title: "Standard Supermarket Egg (Scale 1–6)",
      desc: "Pale, flat, watery yellow yolk. Typically from caged hens with no outdoor access and grain-only diets. Lower micronutrient density.",
      vitD: "1x Baseline",
      omega: "1x Baseline"
    },
    cageFree: {
      title: "Conventional Cage-Free (Scale 7–9)",
      desc: "Mild yellow-golden yolk. Hens live inside open barn floors without outdoor sunlight or foraging. Modest improvements in natural nutrients.",
      vitD: "1.5x Baseline",
      omega: "1.4x Baseline"
    },
    freeRange: {
      title: "Nutrifresh Free Range (Scale 10–12)",
      desc: "Vibrant golden-orange yolk with plump dome firmness. Hens roam outdoors with fresh air and green grass daily.",
      vitD: "2.5x Higher",
      omega: "2x Higher"
    },
    pastureHeritage: {
      title: "Nutrifresh Pasture Raised & Heritage (Scale 13–15)",
      desc: "EXTRAORDINARY SUNSET AMBER YOLK! Plump, tall, velvety, and bursting with rich culinary flavor. Hens roam freely on 8–50 acres of lush pasture under natural sunlight.",
      vitD: "4x Higher",
      omega: "3x Higher"
    }
  };

  if (yolkSlider) {
    function updateYolkScale(val) {
      if (yolkCurrentScore) yolkCurrentScore.textContent = `Score: ${val}/15`;
      
      let selected;
      if (val <= 6) {
        selected = yolkData.standard;
      } else if (val <= 9) {
        selected = yolkData.cageFree;
      } else if (val <= 12) {
        selected = yolkData.freeRange;
      } else {
        selected = yolkData.pastureHeritage;
      }

      if (yolkLevelTitle) yolkLevelTitle.textContent = selected.title;
      if (yolkLevelDesc) yolkLevelDesc.textContent = selected.desc;
      if (vitDStat) vitDStat.textContent = selected.vitD;
      if (omegaStat) omegaStat.textContent = selected.omega;
    }

    yolkSlider.addEventListener('input', (e) => {
      updateYolkScale(parseInt(e.target.value));
    });

    // Initialize with default max score
    updateYolkScale(parseInt(yolkSlider.value || 14));
  }

  /* ==========================================================================
     6. Animated Count-Up Numbers for Stats Section
     ========================================================================== */
  const statNumbers = document.querySelectorAll('.stat-number');
  let statsCounted = false;

  function countUp(el, target, suffix = '') {
    const isFloat = target.toString().includes('.');
    const duration = 2000;
    const steps = 60;
    const increment = target / steps;
    let current = 0;
    let stepCount = 0;

    const timer = setInterval(() => {
      stepCount++;
      current += increment;
      if (stepCount >= steps) {
        current = target;
        clearInterval(timer);
      }
      el.textContent = (isFloat ? current.toFixed(1) : Math.floor(current)) + suffix;
    }, duration / steps);
  }

  if (statNumbers.length > 0) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting && !statsCounted) {
          statsCounted = true;
          statNumbers.forEach(stat => {
            const rawVal = stat.getAttribute('data-target') || '0';
            const suffix = stat.getAttribute('data-suffix') || '';
            const num = parseFloat(rawVal);
            countUp(stat, num, suffix);
          });
        }
      });
    }, { threshold: 0.4 });

    const statsSection = document.querySelector('.stats-section');
    if (statsSection) {
      observer.observe(statsSection);
    }
  }

  /* ==========================================================================
     7. Store Locator Modal & Interactive Search
     ========================================================================== */
  const openLocatorBtns = document.querySelectorAll('.openLocatorBtn');
  const locatorModalOverlay = document.getElementById('locatorModalOverlay');
  const closeLocatorBtn = document.getElementById('closeLocatorBtn');
  const locatorZipInput = document.getElementById('locatorZipInput');
  const locatorSearchBtn = document.getElementById('locatorSearchBtn');
  const locatorResultsList = document.getElementById('locatorResultsList');

  // Open Locator Modal
  openLocatorBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      if (locatorModalOverlay) {
        locatorModalOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        setTimeout(() => {
          if (locatorZipInput) locatorZipInput.focus();
        }, 200);
      }
    });
  });

  // Close Locator Modal
  function closeLocatorModal() {
    if (locatorModalOverlay) {
      locatorModalOverlay.classList.remove('active');
    }
    if (!navDrawer || !navDrawer.classList.contains('active')) {
      document.body.style.overflow = '';
    }
  }

  if (closeLocatorBtn) {
    closeLocatorBtn.addEventListener('click', closeLocatorModal);
  }

  if (locatorModalOverlay) {
    locatorModalOverlay.addEventListener('click', (e) => {
      if (e.target === locatorModalOverlay) {
        closeLocatorModal();
      }
    });
  }

  // Perform Store Search
  function performStoreSearch() {
    if (!locatorZipInput || !locatorResultsList) return;
    const zipCode = locatorZipInput.value.trim();
    
    const zipRegex = /^\d{5}$/;
    if (!zipRegex.test(zipCode)) {
      locatorResultsList.innerHTML = `
        <p style="text-align: center; color: var(--color-primary); font-weight: 700; padding: 15px;">
          Please enter a valid 5-digit US ZIP code (e.g., 90210, 10001, 75001, 60601).
        </p>
      `;
      return;
    }

    // Loading State
    locatorResultsList.innerHTML = `
      <div style="text-align: center; padding: 30px 10px;">
        <div style="
          display: inline-block; 
          width: 44px; 
          height: 44px; 
          border: 4px solid rgba(27,28,71,0.1); 
          border-left-color: var(--color-sunny); 
          border-radius: 50%; 
          animation: spinLoader 0.9s linear infinite;
        "></div>
        <p style="margin-top: 14px; color: var(--color-text-muted); font-weight: 600;">Finding local grocery stores with fresh Nutrifresh Eggs...</p>
      </div>
      <style>
        @keyframes spinLoader {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      </style>
    `;

    setTimeout(() => {
      const mockStores = [
        {
          name: "Whole Foods Market",
          address: `${120 + parseInt(zipCode[0]) * 15} Organic Harvest Ave`,
          city: "Metro Center",
          distance: `${(0.8 + parseInt(zipCode[4]) * 0.3).toFixed(1)} mi`,
          stock: "Heritage Breed, Pasture Raised, Organic Free Range"
        },
        {
          name: "Sprouts Farmers Market",
          address: `${2400 + parseInt(zipCode[1]) * 20} Golden Pasture Blvd`,
          city: "Westridge Commons",
          distance: `${(1.9 + parseInt(zipCode[3]) * 0.4).toFixed(1)} mi`,
          stock: "Pasture Raised, Organic Free Range, Free Range"
        },
        {
          name: "Kroger Fresh Superstore",
          address: `${580 + parseInt(zipCode[2]) * 35} Country Fair Way`,
          city: "Eastside Plaza",
          distance: `${(3.4 + parseInt(zipCode[2]) * 0.5).toFixed(1)} mi`,
          stock: "Pasture Raised, Free Range Dozen"
        },
        {
          name: "Target Supercenter",
          address: `${1020 + parseInt(zipCode[3]) * 40} Commerce Parkway`,
          city: "North Park",
          distance: `${(4.8 + parseInt(zipCode[1]) * 0.6).toFixed(1)} mi`,
          stock: "Pasture Raised 12ct & 18ct"
        }
      ];

      let resultsHtml = `<div style="margin-bottom: 12px; font-weight: 700; color: var(--color-secondary); font-size: 0.95rem;">${mockStores.length} stores found near ${zipCode}:</div>`;
      
      mockStores.forEach(store => {
        resultsHtml += `
          <div class="store-card">
            <div class="store-card-info">
              <h4>${store.name}</h4>
              <p>${store.address}, ${store.city}</p>
              <p style="color: var(--color-primary); font-size: 0.85rem; margin-top: 6px; font-weight: 600;">✓ In Stock: ${store.stock}</p>
            </div>
            <div class="store-card-distance">
              <span>${store.distance}</span>
              <a href="https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(store.name + ' ' + store.address)}" target="_blank" rel="noopener noreferrer">Get Directions &rarr;</a>
            </div>
          </div>
        `;
      });

      locatorResultsList.innerHTML = resultsHtml;
    }, 600);
  }

  if (locatorSearchBtn) {
    locatorSearchBtn.addEventListener('click', performStoreSearch);
  }

  if (locatorZipInput) {
    locatorZipInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        performStoreSearch();
      }
    });
  }

  /* ==========================================================================
     8. Interactive Recipe Modal System
     ========================================================================== */
  const recipeModalOverlay = document.getElementById('recipeModalOverlay');
  const closeRecipeBtn = document.getElementById('closeRecipeBtn');
  const recipeModalBody = document.getElementById('recipeModalBody');
  const recipeViewBtns = document.querySelectorAll('.btn-recipe-view');

  const recipeDatabase = {
    benedict: {
      title: "Golden Amber Eggs Benedict",
      prep: "15 mins",
      cook: "10 mins",
      servings: "4 servings",
      image: "./assets/images/nutrifresh_breakfast_dish.jpg",
      ingredients: [
        "4 Nutrifresh Heritage or Pasture-Raised Eggs",
        "2 English muffins, split and toasted",
        "4 slices Canadian bacon or thick-cut smoked ham",
        "3 Nutrifresh egg yolks (for hollandaise)",
        "1/2 cup unsalted butter, melted and warm",
        "1 tbsp fresh lemon juice",
        "1 pinch cayenne pepper & sea salt",
        "Fresh chopped chives for garnish"
      ],
      steps: [
        "Fill a deep skillet with 3 inches of water, add 1 tbsp white vinegar, and bring to a gentle simmer.",
        "To make hollandaise: whisk 3 Nutrifresh yolks and lemon juice vigorously in a heatproof bowl over simmering water until doubled in volume.",
        "Slowly drizzle in warm melted butter while continuously whisking until thick and velvety. Season with salt and cayenne.",
        "Crack cold Nutrifresh eggs into ramekins, swirl the simmering water into a gentle whirlpool, and slip each egg in. Poach for 3 to 4 minutes until whites are set and yolks remain luscious and runny.",
        "Assemble: place toasted muffin halves, top with warm Canadian bacon, a poached Nutrifresh egg, and generously spoon over the warm golden hollandaise. Sprinkle with fresh chives and serve immediately!"
      ]
    },
    tacos: {
      title: "Loaded Pasture Breakfast Tacos",
      prep: "10 mins",
      cook: "10 mins",
      servings: "3 servings (6 tacos)",
      image: "./assets/images/nutrifresh_egg_tacos.jpg",
      ingredients: [
        "6 Nutrifresh Pasture-Raised Eggs",
        "6 warm small corn or flour tortillas",
        "1 ripe Hass avocado, sliced",
        "1/3 cup crumbled Cotija cheese or queso fresco",
        "1/4 cup roasted salsa verde",
        "2 tbsp fresh cilantro, chopped",
        "1 tbsp unsalted butter",
        "Lime wedges & hot sauce to taste"
      ],
      steps: [
        "Whisk 6 Nutrifresh eggs with a pinch of sea salt and freshly cracked black pepper.",
        "Melt butter in a nonstick skillet over medium-low heat. Pour in the eggs and gently sweep across the pan with a silicone spatula for soft, ultra-creamy curds (about 3 minutes).",
        "Warm tortillas on a dry cast iron skillet until soft and lightly charred.",
        "Divide soft scrambled eggs among warm tortillas. Top with fresh avocado slices, crumbled Cotija cheese, spoonfuls of vibrant salsa verde, and fresh cilantro.",
        "Squeeze fresh lime juice over the top and enjoy the most satisfying morning breakfast tacos!"
      ]
    },
    tartine: {
      title: "Rustic Sourdough Avocado & Poached Egg Tartine",
      prep: "10 mins",
      cook: "5 mins",
      servings: "2 servings",
      image: "./assets/images/nutrifresh_breakfast_dish.jpg",
      ingredients: [
        "2 Nutrifresh Organic Free Range or Heritage Eggs",
        "2 thick slices artisan sourdough bread",
        "1 ripe avocado, mashed with lime juice and flake salt",
        "1 cup microgreens or baby arugula",
        "1 tbsp extra virgin olive oil",
        "Red pepper chili flakes and everything bagel seasoning"
      ],
      steps: [
        "Toast sourdough slices until deep golden and crisp. Rub lightly with a raw garlic clove if desired.",
        "Poach or soft-boil 2 Nutrifresh eggs for exactly 6 minutes for gooey amber yolk perfection.",
        "Generously spread mashed avocado over the warm toasted sourdough.",
        "Place warm eggs on top, slit slightly to let the vibrant sunset amber yolk spill over the avocado.",
        "Garnish with microgreens, a drizzle of olive oil, flaky sea salt, and chili flakes."
      ]
    }
  };

  recipeViewBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const recipeKey = btn.getAttribute('data-recipe');
      const recipe = recipeDatabase[recipeKey];
      if (!recipe || !recipeModalOverlay || !recipeModalBody) return;

      let ingredientsList = '';
      recipe.ingredients.forEach(item => {
        ingredientsList += `<li style="margin-bottom: 8px;"><label style="display:flex; align-items:center; gap:8px; cursor:pointer;"><input type="checkbox" style="accent-color: var(--color-primary); width:18px; height:18px;"> <span>${item}</span></label></li>`;
      });

      let stepsList = '';
      recipe.steps.forEach((step, idx) => {
        stepsList += `
          <div style="display:flex; gap:16px; margin-bottom: 16px;">
            <div style="width:30px; height:30px; border-radius:50%; background:var(--color-sunny); color:var(--color-secondary); font-weight:800; display:flex; align-items:center; justify-content:center; flex-shrink:0;">${idx + 1}</div>
            <p style="font-size:0.95rem; color:var(--color-text-dark); line-height:1.5;">${step}</p>
          </div>
        `;
      });

      recipeModalBody.innerHTML = `
        <img src="${recipe.image}" alt="${recipe.title}" style="width:100%; height:260px; object-fit:cover; border-radius:var(--radius-md); margin-bottom:20px;">
        <div style="display:flex; gap:16px; margin-bottom:14px; color:var(--color-text-muted); font-size:0.9rem; font-weight:600;">
          <span>⏱ Prep: ${recipe.prep}</span>
          <span>🔥 Cook: ${recipe.cook}</span>
          <span>🍽 ${recipe.servings}</span>
        </div>
        <h2 style="font-size:2rem; margin-bottom:18px; color:var(--color-secondary);">${recipe.title}</h2>
        
        <h4 style="font-size:1.2rem; margin:20px 0 12px; color:var(--color-secondary);">Ingredients:</h4>
        <ul style="list-style:none; margin-bottom:24px; padding:0;">
          ${ingredientsList}
        </ul>

        <h4 style="font-size:1.2rem; margin:20px 0 14px; color:var(--color-secondary);">Instructions:</h4>
        <div style="display:flex; flex-direction:column;">
          ${stepsList}
        </div>
      `;

      recipeModalOverlay.classList.add('active');
      document.body.style.overflow = 'hidden';
    });
  });

  if (closeRecipeBtn && recipeModalOverlay) {
    closeRecipeBtn.addEventListener('click', () => {
      recipeModalOverlay.classList.remove('active');
      document.body.style.overflow = '';
    });

    recipeModalOverlay.addEventListener('click', (e) => {
      if (e.target === recipeModalOverlay) {
        recipeModalOverlay.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  }

  /* ==========================================================================
     9. Newsletter Form Interaction
     ========================================================================== */
  const newsletterForm = document.getElementById('newsletterForm');
  if (newsletterForm) {
    newsletterForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const input = newsletterForm.querySelector('input[type="email"]');
      if (input && input.value) {
        newsletterForm.innerHTML = `
          <div style="background: rgba(255,255,255,0.15); padding: 16px 24px; border-radius: var(--radius-pill); color: var(--color-sunny); font-weight: 700;">
            🎉 You're in! Welcome to the Nutrifresh family for farm recipes and coupons.
          </div>
        `;
      }
    });
  }

});
