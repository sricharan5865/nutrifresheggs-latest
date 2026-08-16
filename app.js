/**
 * Nutrifresh Eggs - Interactive App Logic (Happy Egg Replica)
 * Drawer menu, Video Sound Toggle, Product Carousel, Yolk Slider, Stats Counter, Store Locator
 */

document.addEventListener('DOMContentLoaded', () => {
  initHeader();
  initDrawer();
  initVideoHero();
  initProductCarousel();
  initYolkSlider();
  initStatsCounter();
  initStoreLocator();
  initRecipes();
  initLegalModals();
  initNewsletter();
});

/* --------------------------------------------------------------------------
   1. Sticky Header & Scroll Effects
   -------------------------------------------------------------------------- */
function initHeader() {
  const header = document.querySelector('.site-header');
  if (!header) return;

  const handleScroll = () => {
    if (window.scrollY > 50) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  };

  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll();
}

/* --------------------------------------------------------------------------
   2. Slideout Drawer Menu
   -------------------------------------------------------------------------- */
function initDrawer() {
  const drawerTriggers = document.querySelectorAll('.drawer-trigger, .drawer-toggle, #menuToggle');
  const drawerOverlay = document.querySelector('.drawer-overlay, #drawerOverlay');
  const drawerCloseBtns = document.querySelectorAll('.drawer-close, #drawerClose');
  const drawerLinks = document.querySelectorAll('.drawer-nav-list a, .drawer-carton-item');

  if (!drawerOverlay) return;

  const openDrawer = () => {
    drawerOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
    drawerTriggers.forEach(btn => btn.setAttribute('aria-expanded', 'true'));
  };

  const closeDrawer = () => {
    drawerOverlay.classList.remove('active');
    document.body.style.overflow = '';
    drawerTriggers.forEach(btn => btn.setAttribute('aria-expanded', 'false'));
  };

  drawerTriggers.forEach(btn => btn.addEventListener('click', openDrawer));
  drawerCloseBtns.forEach(btn => btn.addEventListener('click', closeDrawer));

  drawerLinks.forEach(link => {
    link.addEventListener('click', () => {
      closeDrawer();
    });
  });

  drawerOverlay.addEventListener('click', (e) => {
    if (e.target === drawerOverlay) {
      closeDrawer();
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && drawerOverlay.classList.contains('active')) {
      closeDrawer();
    }
  });
}

/* --------------------------------------------------------------------------
   3. Video Hero & Sound Toggle
   -------------------------------------------------------------------------- */
function initVideoHero() {
  const heroVideo = document.querySelector('.hero-video');
  const soundToggleBtn = document.querySelector('.hero-sound-toggle');

  if (!heroVideo) return;

  // Guarantee seamless background video autoplay
  const playPromise = heroVideo.play();
  if (playPromise !== undefined) {
    playPromise.catch(() => {
      heroVideo.muted = true;
      heroVideo.play();
    });
  }

  if (!soundToggleBtn) return;

  soundToggleBtn.addEventListener('click', () => {
    if (heroVideo.muted) {
      heroVideo.muted = false;
      heroVideo.volume = 0.6;
      soundToggleBtn.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77zm-2.5-2.23L6.5 6H2v12h4.5l5 5V1z"/></svg>
        <span>Sound On</span>
      `;
    } else {
      heroVideo.muted = true;
      soundToggleBtn.innerHTML = `
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63zm2.5 0c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71zM4.27 3L3 4.27 7.73 9H3v6h4l5 5v-6.73l4.25 4.25c-.67.52-1.42.93-2.25 1.18v2.06c1.38-.31 2.63-.95 3.69-1.81L19.73 21 21 19.73 4.27 3zM12 4L9.91 6.09 12 8.18V4z"/></svg>
        <span>Sound Muted</span>
      `;
    }
  });
}

/* --------------------------------------------------------------------------
   4. Product Carousel with Navigation & Swipe
   -------------------------------------------------------------------------- */
function initProductCarousel() {
  const track = document.querySelector('.carousel-track');
  const prevBtn = document.querySelector('.carousel-prev');
  const nextBtn = document.querySelector('.carousel-next');

  if (!track || !prevBtn || !nextBtn) return;

  let currentIndex = 0;
  const cards = track.querySelectorAll('.product-card');
  const totalCards = cards.length;
  const isFullWidthSlider = track.classList.contains('happy-slider-track');

  const getVisibleCards = () => {
    if (isFullWidthSlider) return 1;
    if (window.innerWidth <= 768) return 1;
    if (window.innerWidth <= 1024) return 2;
    return 3;
  };

  const updateCarousel = () => {
    const visibleCards = getVisibleCards();
    const maxIndex = Math.max(0, totalCards - visibleCards);
    if (currentIndex > maxIndex) currentIndex = maxIndex;
    if (currentIndex < 0) currentIndex = 0;

    const cardWidth = cards[0].offsetWidth;
    const gap = isFullWidthSlider ? 0 : (window.innerWidth <= 768 ? 16 : 30);
    const moveAmount = (cardWidth + gap) * currentIndex;
    track.style.transform = `translateX(-${moveAmount}px)`;
  };

  prevBtn.addEventListener('click', () => {
    if (currentIndex > 0) {
      currentIndex--;
      updateCarousel();
    }
  });

  nextBtn.addEventListener('click', () => {
    const visibleCards = getVisibleCards();
    const maxIndex = Math.max(0, totalCards - visibleCards);
    if (currentIndex < maxIndex) {
      currentIndex++;
      updateCarousel();
    } else {
      currentIndex = 0; // wrap around
      updateCarousel();
    }
  });

  // Touch Swipe Support for mobile phones
  let touchStartX = 0;
  let touchEndX = 0;

  track.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
  }, { passive: true });

  track.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    const swipeDistance = touchEndX - touchStartX;
    if (Math.abs(swipeDistance) > 40) {
      if (swipeDistance < 0) {
        // Swipe left -> next
        const visibleCards = getVisibleCards();
        const maxIndex = Math.max(0, totalCards - visibleCards);
        if (currentIndex < maxIndex) {
          currentIndex++;
        } else {
          currentIndex = 0;
        }
        updateCarousel();
      } else {
        // Swipe right -> prev
        if (currentIndex > 0) {
          currentIndex--;
          updateCarousel();
        }
      }
    }
  }, { passive: true });

  window.addEventListener('resize', updateCarousel);
}

/* --------------------------------------------------------------------------
   5. Interactive Yolk Grade Slider (Grades 1 to 15)
   -------------------------------------------------------------------------- */
function initYolkSlider() {
  const slider = document.getElementById('yolkGradeSlider');
  const yolkDome = document.querySelector('.dynamic-yolk-dome');
  const gradeNum = document.getElementById('yolkGradeValue');
  const gradeTitle = document.getElementById('yolkGradeTitle');
  const gradeDesc = document.getElementById('yolkGradeDescription');

  if (!slider || !yolkDome || !gradeNum) return;

  const yolkData = {
    1: {
      title: 'Grade 1: Conventional Caged',
      color: 'radial-gradient(circle at 35% 35%, #FFF9C4 0%, #FFF59D 70%, #FFEE58 100%)',
      shadow: '0 8px 18px rgba(255, 238, 88, 0.25)',
      desc: 'Pale yellow, flat yolk from caged environments. Low in natural carotenoids, lutein, and omega-3 nutrients.'
    },
    5: {
      title: 'Grade 5: Standard Cage-Free',
      color: 'radial-gradient(circle at 35% 35%, #FFF176 0%, #FFD54F 70%, #FFCA28 100%)',
      shadow: '0 8px 20px rgba(255, 202, 40, 0.3)',
      desc: 'Moderate yellow with basic roundness. Lacks rich natural outdoor foraging benefits and daily sunshine.'
    },
    10: {
      title: 'Grade 10: Standard Free-Range',
      color: 'radial-gradient(circle at 35% 35%, #FFA726 0%, #FF9800 70%, #FB8C00 100%)',
      shadow: '0 10px 22px rgba(251, 140, 0, 0.35)',
      desc: 'Warm golden yellow with improved dome plumpness from outdoor access and balanced grains.'
    },
    15: {
      title: 'Grade 15: Nutrifresh Heritage Sunset Amber',
      color: 'radial-gradient(circle at 35% 35%, #FF7043 0%, #FF5700 70%, #BF360C 100%)',
      shadow: '0 12px 28px rgba(255, 87, 0, 0.5)',
      desc: 'Deep glowing sunset amber with a plump, creamy, rich dome. Packed with 6x Vitamin D, Xanthophylls, and rich velvety taste!'
    }
  };

  const updateYolk = (val) => {
    gradeNum.textContent = val;

    let nearest = 1;
    if (val >= 13) nearest = 15;
    else if (val >= 8) nearest = 10;
    else if (val >= 4) nearest = 5;
    else nearest = 1;

    // Calculate interpolated colors
    const r = Math.min(255, Math.round(255));
    const g = Math.max(70, Math.round(245 - (val / 15) * 160));
    const b = Math.max(10, Math.round(180 - (val / 15) * 170));
    
    yolkDome.style.background = `radial-gradient(circle at 35% 35%, rgb(${r}, ${g + 30}, ${b + 30}) 0%, rgb(${r}, ${g}, ${b}) 75%, rgb(${Math.max(160, r - 40)}, ${Math.max(30, g - 40)}, 0) 100%)`;
    yolkDome.style.boxShadow = `0 10px 25px rgba(${r}, ${g}, ${b}, 0.45)`;

    if (gradeTitle) gradeTitle.textContent = yolkData[nearest].title;
    if (gradeDesc) gradeDesc.textContent = yolkData[nearest].desc;
  };

  slider.addEventListener('input', (e) => updateYolk(parseInt(e.target.value, 10)));
  updateYolk(parseInt(slider.value, 10));
}

/* --------------------------------------------------------------------------
   6. Live Animated Stats Counter
   -------------------------------------------------------------------------- */
function initStatsCounter() {
  const counterElements = document.querySelectorAll('.stat-counter-num');
  if (!counterElements.length) return;

  const animateCounter = (el) => {
    const target = parseFloat(el.getAttribute('data-target'));
    const isDecimal = target % 1 !== 0;
    const duration = 2000;
    const stepTime = 20;
    const steps = duration / stepTime;
    const increment = target / steps;
    let current = 0;

    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      el.textContent = isDecimal ? current.toFixed(1) : Math.floor(current);
    }, stepTime);
  };

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        animateCounter(entry.target);
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  counterElements.forEach(el => observer.observe(el));
}

/* --------------------------------------------------------------------------
   7. Store Locator Search & Map Preview
   -------------------------------------------------------------------------- */
function initStoreLocator() {
  const searchInput = document.getElementById('storeSearchInput');
  const searchBtn = document.getElementById('storeSearchBtn');
  const storeList = document.getElementById('storeResultsList');

  if (!searchInput || !searchBtn || !storeList) return;

  const sampleStores = [
    { name: 'Whole Foods Market', address: '450 Natural Grove Way', city: 'Austin, TX 78701', dist: '0.8 miles', stock: 'In Stock (All Cartons)' },
    { name: 'Sprouts Farmers Market', address: '1280 Green Valley Rd', city: 'Austin, TX 78704', dist: '1.4 miles', stock: 'In Stock (Heritage & Pasture)' },
    { name: 'Kroger Fresh Market', address: '2100 Farmcrest Blvd', city: 'Austin, TX 78745', dist: '2.1 miles', stock: 'In Stock (Organic Free Range)' },
    { name: 'Target Supercenter', address: '500 E Stassney Ln', city: 'Austin, TX 78745', dist: '3.5 miles', stock: 'In Stock (Pasture Raised)' },
    { name: 'Trader Joe’s Market', address: '2805 Bee Caves Rd', city: 'Austin, TX 78746', dist: '4.2 miles', stock: 'In Stock (Heritage Amber)' }
  ];

  const renderStores = (query = '') => {
    const filtered = sampleStores.filter(s => 
      s.name.toLowerCase().includes(query.toLowerCase()) || 
      s.city.toLowerCase().includes(query.toLowerCase()) ||
      s.address.toLowerCase().includes(query.toLowerCase()) ||
      query.trim() === ''
    );

    if (filtered.length === 0) {
      storeList.innerHTML = `
        <div style="padding: 24px; text-align: center; color: #64748B;">
          <p style="font-weight: 700;">No stores found near "${query}".</p>
          <p style="font-size: 0.9rem;">Try searching another zip code or city!</p>
        </div>
      `;
      return;
    }

    storeList.innerHTML = filtered.map(store => `
      <div class="store-result-item">
        <span class="store-badge-open">✓ ${store.stock}</span>
        <h4>${store.name}</h4>
        <p>${store.address}, ${store.city}</p>
        <div class="store-actions">
          <span>📍 ${store.dist}</span>
          <a href="https://maps.google.com" target="_blank" rel="noopener">Get Directions →</a>
        </div>
      </div>
    `).join('');
  };

  searchBtn.addEventListener('click', () => {
    renderStores(searchInput.value);
  });

  searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      renderStores(searchInput.value);
    }
  });

  renderStores();
}

/* --------------------------------------------------------------------------
   8. Recipes Filtering & Recipe Modals
   -------------------------------------------------------------------------- */
function initRecipes() {
  const filterBtns = document.querySelectorAll('.recipe-filter-btn');
  const cards = document.querySelectorAll('#recipeCardsGrid .recipe-card');
  const modalOverlay = document.getElementById('recipeModalOverlay');
  const modalContent = document.getElementById('recipeModalContent');
  const closeBtn = document.getElementById('closeRecipeModal');

  const recipeDatabase = {
    benedict: {
      title: "Sunset Amber Eggs Benedict",
      category: "Weekend Brunch",
      time: "25 Mins",
      servings: "2 Servings",
      image: "assets/images/nutrifresh_breakfast_dish.jpg",
      description: "A showstopping brunch masterpiece featuring velvety Grade 15 sunset amber yolks that create an ultra-rich hollandaise sauce.",
      ingredients: [
        "4 Nutrifresh Heritage Breed eggs (for poaching)",
        "3 Nutrifresh Heritage egg yolks (for hollandaise)",
        "1 stick (1/2 cup) unsalted grass-fed butter, melted",
        "1 tbsp fresh lemon juice",
        "2 English muffins, split and toasted",
        "4 slices Canadian bacon or thick-cut ham",
        "1 tbsp white vinegar (for poaching water)",
        "Fresh chopped chives, sea salt & cayenne pepper"
      ],
      steps: [
        "In a blender or heatproof bowl over simmering water, whisk 3 Nutrifresh egg yolks with lemon juice. Slowly stream in warm melted butter until thick and emulsified. Season with pinch of cayenne and sea salt.",
        "Bring a saucepan of water with 1 tbsp vinegar to a gentle simmer. Swirl water to create a whirlpool, then gently drop in cracked Nutrifresh eggs one at a time. Poach for 3 minutes for glorious runny yolks.",
        "In a skillet, warm the Canadian bacon slices until edges are lightly browned.",
        "Assemble by topping each toasted English muffin half with bacon, a poached Nutrifresh egg, and a generous ladle of golden hollandaise. Garnish with fresh chives."
      ]
    },
    tacos: {
      title: "Pasture Breakfast Tacos",
      category: "Quick Breakfast",
      time: "15 Mins",
      servings: "4 Tacos",
      image: "assets/images/nutrifresh_egg_tacos.jpg",
      description: "Velvety soft-scrambled pasture eggs on warm blistered tortillas with cotija cheese, roasted salsa verde, and fresh cilantro.",
      ingredients: [
        "6 Nutrifresh Pasture-Raised eggs",
        "2 tbsp grass-fed butter",
        "4 yellow corn tortillas",
        "1 ripe avocado, sliced",
        "1/4 cup crumbled cotija cheese",
        "3 tbsp roasted tomatillo salsa verde",
        "Pickled red onions and chopped fresh cilantro"
      ],
      steps: [
        "Whisk 6 Nutrifresh pasture eggs with a pinch of sea salt and black pepper until completely smooth.",
        "Melt butter in a non-stick skillet over medium-low heat. Pour in whisked eggs and gently push with a spatula from edges to center to create pillowy soft curds.",
        "Warm corn tortillas over an open flame or in a dry pan until charred and pliable.",
        "Spoon soft scramble into tortillas, top with sliced avocado, salsa verde, cotija cheese, pickled onions, and cilantro."
      ]
    },
    shakshuka: {
      title: "Cast-Iron Farm Shakshuka",
      category: "Weekend Feast",
      time: "30 Mins",
      servings: "3-4 Servings",
      image: "assets/images/breakfast-plate.jpg",
      description: "Eggs gently poached directly inside a smoky, spiced heirloom tomato sauce with bell peppers, garlic, cumin, and crumbled feta.",
      ingredients: [
        "5 Nutrifresh Pasture-Raised or Organic eggs",
        "2 tbsp extra virgin olive oil",
        "1 medium yellow onion, diced",
        "1 red bell pepper, diced",
        "3 cloves garlic, minced",
        "1 tsp ground cumin, 1 tsp smoked paprika",
        "1 can (28 oz) whole peeled San Marzano tomatoes, crushed",
        "1/2 cup crumbled feta cheese & fresh parsley"
      ],
      steps: [
        "Heat olive oil in a 12-inch cast iron skillet over medium heat. Sauté onion and bell pepper until tender (approx 6 mins).",
        "Add minced garlic, cumin, smoked paprika, and red pepper flakes; cook for 1 minute until fragrant.",
        "Pour in crushed tomatoes, season with salt and pepper, and simmer gently for 12-15 minutes until sauce thickens.",
        "Use a wooden spoon to create 5 small wells in the sauce. Crack one Nutrifresh egg directly into each well. Cover and simmer on low for 6-8 minutes until whites are set but yolks remain runny and jammy.",
        "Remove from heat, crumble feta cheese over top, sprinkle fresh parsley, and serve immediately with crusty sourdough bread."
      ]
    },
    curd: {
      title: "Heritage Amber Lemon Curd",
      category: "Baking & Gourmet",
      time: "45 Mins",
      servings: "2 Jars",
      image: "assets/images/nutrifresh_yolk_comparison.jpg",
      description: "An extraordinarily rich, jewel-toned curd taking advantage of the high carotenoid content in Heritage eggs.",
      ingredients: [
        "6 Nutrifresh Heritage Breed egg yolks",
        "3/4 cup granulated sugar",
        "1/2 cup fresh Meyer lemon juice",
        "1 tbsp finely grated lemon zest",
        "6 tbsp cold unsalted butter, cubed"
      ],
      steps: [
        "Whisk Heritage egg yolks and sugar together in a heatproof glass bowl until pale and slightly thickened.",
        "Whisk in fresh lemon juice and zest. Place bowl over a saucepan of gently simmering water.",
        "Cook stirring continuously with a silicone spatula for 10-12 minutes until mixture coats the back of a spoon (170°F / 77°C).",
        "Remove from heat and whisk in cold cubed butter one piece at a time until silky and glossy.",
        "Strain through a fine-mesh sieve into clean glass jars. Chill in refrigerator for at least 2 hours."
      ]
    },
    tartine: {
      title: "Jammy Yolk Avocado Toast",
      category: "Quick Breakfast",
      time: "10 Mins",
      servings: "2 Servings",
      image: "assets/images/nutrifresh_farmer_pasture.jpg",
      description: "6.5-minute jammy boiled egg atop toasted country levain with whipped ripe avocado, crunchy seeds, and spicy chili crunch.",
      ingredients: [
        "2 Nutrifresh Pasture-Raised eggs",
        "2 thick slices country sourdough bread",
        "1 ripe Hass avocado, pitted and mashed",
        "1 tsp fresh lime juice",
        "1 tbsp crispy chili oil / chili crunch",
        "Toasted sesame seeds & flaky Maldon sea salt"
      ],
      steps: [
        "Bring a small pot of water to a rolling boil. Carefully lower 2 Nutrifresh eggs using a slotted spoon. Boil for exactly 6 minutes and 30 seconds.",
        "Transfer eggs immediately to an ice bath for 3 minutes, then peel under cold water and slice in half to reveal the jammy amber center.",
        "Toast sourdough slices until deeply golden and crisp. Mash avocado with lime juice and sea salt, then spread generously on toast.",
        "Top each toast with jammy egg halves, drizzle with chili crunch oil, and sprinkle with sesame seeds and flaky salt."
      ]
    },
    omelette: {
      title: "Classic French Rolled Omelette",
      category: "Culinary Masterclass",
      time: "8 Mins",
      servings: "1 Serving",
      image: "assets/images/nutrifresh_hens_pasture.jpg",
      description: "The ultimate test of egg craft: a blemish-free golden roll with a custardy, delicate soft curd interior.",
      ingredients: [
        "3 Nutrifresh Heritage Breed eggs",
        "1.5 tbsp unsalted butter",
        "1 tbsp finely minced fresh chives",
        "Pinch of fine sea salt and white pepper"
      ],
      steps: [
        "Whisk eggs vigorously with salt and white pepper with a fork until whites and yolks are completely homogenized.",
        "Melt butter in an 8-inch nonstick pan over medium-low heat without letting it brown.",
        "Pour in eggs and immediately shake pan back and forth while rapidly stirring eggs with chopsticks or a rubber spatula to create micro-curds.",
        "When top is still glossy and slightly runny, smooth the surface, tap pan on counter, and gently roll the omelette into a cylinder toward the far edge of the pan.",
        "Invert onto a warm plate, brush with melted butter for a glossy shine, and garnish with fresh chives."
      ]
    }
  };

  // Filter tabs logic
  if (filterBtns.length && cards.length) {
    filterBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        filterBtns.forEach(b => {
          b.classList.remove('active', 'btn-navy');
          b.classList.add('btn-outline');
        });
        btn.classList.add('active', 'btn-navy');
        btn.classList.remove('btn-outline');

        const filter = btn.getAttribute('data-filter');
        cards.forEach(card => {
          const category = card.getAttribute('data-category');
          if (filter === 'all' || category === filter) {
            card.style.display = 'flex';
          } else {
            card.style.display = 'none';
          }
        });
      });
    });
  }

  // Modal logic
  const openButtons = document.querySelectorAll('.open-recipe-modal');
  openButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const id = btn.getAttribute('data-recipe');
      const recipe = recipeDatabase[id];
      if (!recipe || !modalContent || !modalOverlay) return;

      modalContent.innerHTML = `
        <div style="margin-bottom: 20px;">
          <span style="background: rgba(255,183,27,0.2); color: var(--yolk-orange-dark); font-size: 0.8rem; font-weight: 800; text-transform: uppercase; padding: 4px 12px; border-radius: 999px;">${recipe.category}</span>
          <h2 style="font-size: 2rem; margin: 12px 0 6px; color: var(--deep-navy);">${recipe.title}</h2>
          <div style="display: flex; gap: 16px; font-size: 0.9rem; color: #64748B; font-weight: 600;">
            <span>⏱ Prep Time: ${recipe.time}</span>
            <span>🍽 ${recipe.servings}</span>
          </div>
        </div>
        <img src="${recipe.image}" alt="${recipe.title}" style="width: 100%; height: 260px; object-fit: cover; border-radius: 12px; margin-bottom: 20px;">
        <p style="font-size: 1.05rem; color: #475569; line-height: 1.6; margin-bottom: 24px;">${recipe.description}</p>
        
        <h4 style="font-size: 1.2rem; margin-bottom: 12px; color: var(--deep-navy);">Ingredients:</h4>
        <ul style="list-style: disc; padding-left: 24px; margin-bottom: 24px; color: #334155; line-height: 1.8;">
          ${recipe.ingredients.map(ing => `<li>${ing}</li>`).join('')}
        </ul>

        <h4 style="font-size: 1.2rem; margin-bottom: 12px; color: var(--deep-navy);">Step-by-Step Instructions:</h4>
        <ol style="list-style: decimal; padding-left: 24px; color: #334155; line-height: 1.8;">
          ${recipe.steps.map(step => `<li style="margin-bottom: 10px;">${step}</li>`).join('')}
        </ol>
      `;

      modalOverlay.classList.add('active');
      document.body.style.overflow = 'hidden';
    });
  });

  if (closeBtn && modalOverlay) {
    closeBtn.addEventListener('click', () => {
      modalOverlay.classList.remove('active');
      document.body.style.overflow = '';
    });

    modalOverlay.addEventListener('click', (e) => {
      if (e.target === modalOverlay) {
        modalOverlay.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  }
}

/* --------------------------------------------------------------------------
   8. Interactive Legal & Compliance Modal
   -------------------------------------------------------------------------- */
function initLegalModals() {
  const modal = document.getElementById('legalModal');
  const openButtons = document.querySelectorAll('.legal-link-btn, [data-legal-tab]');
  const closeBtn = document.getElementById('closeLegalModal') || document.querySelector('.legal-modal-close');
  const dismissBtn = document.getElementById('dismissLegalModalBtn');
  const tabButtons = document.querySelectorAll('.legal-tab-btn');
  const tabPanels = document.querySelectorAll('.legal-tab-panel');

  if (!modal) return;

  const switchTab = (tabId) => {
    tabButtons.forEach(btn => {
      const match = btn.getAttribute('data-tab') === tabId;
      btn.classList.toggle('active', match);
      btn.setAttribute('aria-selected', match ? 'true' : 'false');
    });

    tabPanels.forEach(panel => {
      const match = panel.id.toLowerCase() === `tabpanel${tabId.toLowerCase()}`;
      if (match) {
        panel.classList.add('active');
        panel.removeAttribute('hidden');
      } else {
        panel.classList.remove('active');
        panel.setAttribute('hidden', 'true');
      }
    });
  };

  const openModal = (tabId = 'privacy') => {
    switchTab(tabId);
    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
    if (closeBtn) closeBtn.focus();
  };

  const closeModal = () => {
    modal.classList.remove('active');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  };

  openButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const tab = btn.getAttribute('data-legal-tab') || 'privacy';
      openModal(tab);
    });
  });

  tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.getAttribute('data-tab');
      if (tab) switchTab(tab);
    });
  });

  if (closeBtn) closeBtn.addEventListener('click', closeModal);
  if (dismissBtn) dismissBtn.addEventListener('click', closeModal);

  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('active')) {
      closeModal();
    }
  });

  // Load existing cookie preferences
  const savedCookiePrefs = localStorage.getItem('nutrifresh_cookies');
  if (savedCookiePrefs) {
    try {
      const parsed = JSON.parse(savedCookiePrefs);
      const anInput = document.getElementById('cookieAnalyticsToggle');
      const mkInput = document.getElementById('cookieMarketingToggle');
      if (anInput && typeof parsed.analytics === 'boolean') anInput.checked = parsed.analytics;
      if (mkInput && typeof parsed.marketing === 'boolean') mkInput.checked = parsed.marketing;
    } catch (e) {
      // Ignore parse error
    }
  }

  // Cookie Settings Preferences Handling
  const saveCookieBtn = document.getElementById('saveCookiePreferencesBtn');
  const acceptAllBtn = document.getElementById('acceptAllCookiesBtn');
  const feedbackMsg = document.getElementById('cookieFeedbackMsg');

  const saveCookies = (analytics, marketing, msg) => {
    localStorage.setItem('nutrifresh_cookies', JSON.stringify({
      essential: true,
      analytics,
      marketing,
      savedAt: new Date().toISOString()
    }));
    if (feedbackMsg) {
      feedbackMsg.innerHTML = `<div style="background: #DCFCE7; color: #166534; padding: 10px 16px; border-radius: 8px; font-weight: 700; margin-top: 14px;">✓ ${msg}</div>`;
      setTimeout(() => { feedbackMsg.innerHTML = ''; }, 4000);
    }
  };

  if (saveCookieBtn) {
    saveCookieBtn.addEventListener('click', () => {
      const an = document.getElementById('cookieAnalyticsToggle')?.checked ?? true;
      const mk = document.getElementById('cookieMarketingToggle')?.checked ?? true;
      saveCookies(an, mk, 'Your cookie preferences have been saved.');
    });
  }

  if (acceptAllBtn) {
    acceptAllBtn.addEventListener('click', () => {
      const anInput = document.getElementById('cookieAnalyticsToggle');
      const mkInput = document.getElementById('cookieMarketingToggle');
      if (anInput) anInput.checked = true;
      if (mkInput) mkInput.checked = true;
      saveCookies(true, true, 'All cookies accepted. Thank you!');
    });
  }
}

/* --------------------------------------------------------------------------
   9. Newsletter Form UX & Validation
   -------------------------------------------------------------------------- */
function initNewsletter() {
  const form = document.getElementById('footerNewsletter');
  if (!form) return;

  const emailInput = form.querySelector('#newsletterEmail') || form.querySelector('input[type="email"]');
  const feedback = document.getElementById('newsletterFeedback');
  const submitBtn = form.querySelector('button[type="submit"]');

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const email = emailInput ? emailInput.value.trim() : '';

    if (!email) {
      if (feedback) {
        feedback.innerHTML = `<span style="color: #F87171; font-size: 0.85rem; font-weight: 700; margin-top: 6px; display: block;">⚠️ Please enter an email address.</span>`;
      }
      if (emailInput) emailInput.focus();
      return;
    }

    if (!emailRegex.test(email)) {
      if (feedback) {
        feedback.innerHTML = `<span style="color: #F87171; font-size: 0.85rem; font-weight: 700; margin-top: 6px; display: block;">⚠️ Please enter a valid email address (e.g. name@domain.com).</span>`;
      }
      if (emailInput) emailInput.focus();
      return;
    }

    // Success State
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span>Joining...</span>`;
    }

    setTimeout(() => {
      localStorage.setItem('nutrifresh_newsletter_subscribed', email);
      if (feedback) {
        feedback.innerHTML = `
          <div style="background: rgba(27, 122, 67, 0.3); border: 1px solid #2E9E5B; color: #86EFAC; padding: 12px 16px; border-radius: 8px; font-weight: 700; font-size: 0.9rem; margin-top: 10px;">
            🎉 Welcome to the flock! Check your inbox for sunrise recipes and coupons.
          </div>
        `;
      }
      if (emailInput) emailInput.value = '';
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `<span>Subscribed!</span>`;
        setTimeout(() => {
          submitBtn.innerHTML = `<span>Subscribe</span>`;
        }, 3000);
      }
    }, 400);
  });
}


