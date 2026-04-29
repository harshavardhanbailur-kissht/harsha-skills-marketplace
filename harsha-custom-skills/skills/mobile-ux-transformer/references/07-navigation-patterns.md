# Mobile Navigation Patterns

> Comprehensive guide to mobile navigation implementation

## Navigation Pattern Selection

### Decision Matrix

| Pattern | Best For | Item Count | Thumb Access |
|---------|----------|------------|--------------|
| Bottom Tab Bar | Primary navigation | 3-5 items | ✅ Excellent |
| Top Tab Bar | Content categories | 2-7 items | ⚠️ Requires reach |
| Hamburger/Drawer | Secondary navigation | 5+ items | ⚠️ Two taps |
| Floating Action Button | Primary action | 1 action | ✅ Good |
| Bottom Sheet | Contextual options | Variable | ✅ Excellent |
| Search | Content discovery | N/A | Varies |

---

## Bottom Tab Bar

### Usage Guidelines

- **3-5 destinations maximum** (5 is absolute max)
- **Always show labels** with icons
- **Persistent across screens** (except fullscreen experiences)
- **Current location indicated** clearly
- **Badge for notifications** (unread count, alerts)

### Implementation

```html
<nav class="bottom-tab-bar" role="navigation" aria-label="Main navigation">
  <a href="/" class="tab-item active" aria-current="page">
    <span class="tab-icon">
      <svg aria-hidden="true"><!-- Home icon --></svg>
    </span>
    <span class="tab-label">Home</span>
  </a>
  
  <a href="/search" class="tab-item">
    <span class="tab-icon">
      <svg aria-hidden="true"><!-- Search icon --></svg>
    </span>
    <span class="tab-label">Search</span>
  </a>
  
  <a href="/notifications" class="tab-item">
    <span class="tab-icon">
      <svg aria-hidden="true"><!-- Bell icon --></svg>
      <span class="badge" aria-label="3 unread notifications">3</span>
    </span>
    <span class="tab-label">Alerts</span>
  </a>
  
  <a href="/profile" class="tab-item">
    <span class="tab-icon">
      <svg aria-hidden="true"><!-- Profile icon --></svg>
    </span>
    <span class="tab-label">Profile</span>
  </a>
</nav>
```

```css
.bottom-tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 56px;
  padding-bottom: env(safe-area-inset-bottom);
  display: flex;
  justify-content: space-around;
  align-items: center;
  background: var(--surface);
  border-top: 1px solid var(--border);
  z-index: 1000;
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex: 1;
  min-width: 64px;
  max-width: 96px;
  min-height: 48px;
  padding: 6px 0;
  text-decoration: none;
  color: var(--text-secondary);
  transition: color 0.2s;
  position: relative;
}

.tab-item.active {
  color: var(--primary);
}

.tab-icon {
  position: relative;
  width: 24px;
  height: 24px;
  margin-bottom: 4px;
}

.tab-label {
  font-size: 12px;
  font-weight: 500;
  line-height: 1;
}

.badge {
  position: absolute;
  top: -4px;
  right: -8px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  background: var(--error);
  color: white;
  font-size: 10px;
  font-weight: 600;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Content padding for bottom nav */
.page-content {
  padding-bottom: calc(56px + env(safe-area-inset-bottom) + 16px);
}
```

### Animation on Tab Change

```javascript
class TabBar {
  constructor(element) {
    this.element = element;
    this.tabs = element.querySelectorAll('.tab-item');
    this.indicator = this.createIndicator();
    
    this.tabs.forEach(tab => {
      tab.addEventListener('click', (e) => this.onTabClick(e, tab));
    });
    
    this.updateIndicator(element.querySelector('.tab-item.active'));
  }
  
  createIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'tab-indicator';
    this.element.appendChild(indicator);
    return indicator;
  }
  
  onTabClick(e, tab) {
    // Update active state
    this.tabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    
    // Animate indicator
    this.updateIndicator(tab);
    
    // Haptic feedback
    if (navigator.vibrate) {
      navigator.vibrate(10);
    }
  }
  
  updateIndicator(tab) {
    const rect = tab.getBoundingClientRect();
    const barRect = this.element.getBoundingClientRect();
    
    this.indicator.style.width = `${rect.width}px`;
    this.indicator.style.transform = `translateX(${rect.left - barRect.left}px)`;
  }
}
```

---

## Top Tab Bar (Segmented Navigation)

### Usage Guidelines

- **2-7 tabs maximum**
- **Scrollable if more than fits**
- **Use for content filtering/categories**
- **Keep labels short** (1-2 words)

### Implementation

```html
<div class="top-tabs-container">
  <nav class="top-tabs" role="tablist">
    <button class="tab active" role="tab" aria-selected="true" id="tab-all">
      All
    </button>
    <button class="tab" role="tab" aria-selected="false" id="tab-photos">
      Photos
    </button>
    <button class="tab" role="tab" aria-selected="false" id="tab-videos">
      Videos
    </button>
    <button class="tab" role="tab" aria-selected="false" id="tab-albums">
      Albums
    </button>
  </nav>
</div>
```

```css
.top-tabs-container {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.top-tabs-container::-webkit-scrollbar {
  display: none;
}

.top-tabs {
  display: flex;
  border-bottom: 1px solid var(--border);
  position: relative;
}

.top-tabs .tab {
  flex: 1;
  min-width: max-content;
  padding: 12px 16px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  background: none;
  border: none;
  cursor: pointer;
  white-space: nowrap;
}

.top-tabs .tab.active {
  color: var(--primary);
}

/* Underline indicator */
.top-tabs::after {
  content: '';
  position: absolute;
  bottom: 0;
  height: 2px;
  background: var(--primary);
  transition: transform 0.2s, width 0.2s;
}
```

---

## Navigation Drawer (Hamburger Menu)

### Usage Guidelines

- **Use for many destinations** (5+)
- **Group related items**
- **Show current location**
- **Include user profile/settings**
- **Avoid for primary navigation** (adds extra tap)

### Implementation

```html
<!-- Hamburger trigger -->
<button class="menu-trigger" aria-label="Open menu" aria-expanded="false">
  <svg aria-hidden="true"><!-- Hamburger icon --></svg>
</button>

<!-- Drawer -->
<aside class="nav-drawer" aria-label="Main menu" hidden>
  <div class="drawer-backdrop"></div>
  <nav class="drawer-content">
    <header class="drawer-header">
      <img src="avatar.jpg" alt="" class="user-avatar">
      <div class="user-info">
        <p class="user-name">John Doe</p>
        <p class="user-email">john@example.com</p>
      </div>
    </header>
    
    <ul class="drawer-menu">
      <li class="menu-section">
        <span class="section-label">Main</span>
        <ul>
          <li><a href="/" class="active">Home</a></li>
          <li><a href="/explore">Explore</a></li>
          <li><a href="/saved">Saved</a></li>
        </ul>
      </li>
      <li class="menu-section">
        <span class="section-label">Account</span>
        <ul>
          <li><a href="/settings">Settings</a></li>
          <li><a href="/help">Help</a></li>
          <li><a href="/logout">Log out</a></li>
        </ul>
      </li>
    </ul>
  </nav>
</aside>
```

```css
.nav-drawer {
  position: fixed;
  inset: 0;
  z-index: 2000;
}

.drawer-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  animation: fadeIn 0.2s;
}

.drawer-content {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 280px;
  max-width: 80vw;
  background: var(--surface);
  animation: slideInLeft 0.3s ease-out;
  overflow-y: auto;
}

@keyframes slideInLeft {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.drawer-header {
  display: flex;
  align-items: center;
  padding: 16px;
  padding-top: calc(16px + env(safe-area-inset-top));
  background: var(--primary);
  color: white;
}

.drawer-menu {
  list-style: none;
  padding: 8px 0;
}

.drawer-menu a {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  color: var(--text-primary);
  text-decoration: none;
}

.drawer-menu a.active {
  background: var(--primary-light);
  color: var(--primary);
}
```

---

## Floating Action Button (FAB)

### Usage Guidelines

- **One primary action only**
- **Position bottom-right** (or bottom-center)
- **Use recognizable icon** (+ for create)
- **Can expand to speed dial**
- **Hide on scroll (optional)**

### Implementation

```html
<!-- Simple FAB -->
<button class="fab" aria-label="Create new item">
  <svg aria-hidden="true"><!-- Plus icon --></svg>
</button>

<!-- Extended FAB -->
<button class="fab fab-extended">
  <svg aria-hidden="true"><!-- Plus icon --></svg>
  <span>Create</span>
</button>

<!-- Speed Dial FAB -->
<div class="fab-container">
  <div class="fab-actions" hidden>
    <button class="fab-action" aria-label="Take photo">
      <svg><!-- Camera icon --></svg>
    </button>
    <button class="fab-action" aria-label="Upload file">
      <svg><!-- Upload icon --></svg>
    </button>
    <button class="fab-action" aria-label="Write note">
      <svg><!-- Note icon --></svg>
    </button>
  </div>
  <button class="fab fab-main" aria-label="Create" aria-expanded="false">
    <svg aria-hidden="true"><!-- Plus icon --></svg>
  </button>
</div>
```

```css
.fab {
  position: fixed;
  bottom: calc(16px + env(safe-area-inset-bottom) + 56px); /* Above tab bar */
  right: 16px;
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: var(--primary);
  color: white;
  border: none;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 100;
  transition: transform 0.2s, box-shadow 0.2s;
}

.fab:active {
  transform: scale(0.95);
}

.fab-extended {
  width: auto;
  padding: 0 20px;
  gap: 8px;
}

/* Speed dial */
.fab-container {
  position: fixed;
  bottom: calc(16px + env(safe-area-inset-bottom) + 56px);
  right: 16px;
  display: flex;
  flex-direction: column-reverse;
  align-items: center;
  gap: 16px;
}

.fab-actions {
  display: flex;
  flex-direction: column-reverse;
  gap: 12px;
}

.fab-action {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--surface);
  color: var(--text-primary);
  border: none;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  opacity: 0;
  transform: scale(0.8) translateY(20px);
  animation: fabActionIn 0.2s forwards;
}

@keyframes fabActionIn {
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}
```

---

## Back Navigation

### Platform Differences

| Platform | Primary Method | Fallback |
|----------|---------------|----------|
| iOS | Edge swipe (left to right) | Top-left back button |
| Android | System back (button/gesture) | Toolbar up arrow |
| Web | Browser back | In-app back button |

### Implementation

```html
<!-- iOS-style back button -->
<button class="ios-back" onclick="history.back()">
  <svg aria-hidden="true"><!-- Chevron left --></svg>
  <span>Back</span>
</button>

<!-- Android-style up button -->
<button class="android-up" onclick="goToParent()">
  <svg aria-hidden="true"><!-- Arrow left --></svg>
</button>
```

```javascript
// Handle browser back button
window.addEventListener('popstate', (event) => {
  // Handle state change
  if (event.state) {
    navigateTo(event.state.page);
  }
});

// Push state when navigating
function navigate(page) {
  history.pushState({ page }, '', `/${page}`);
  renderPage(page);
}
```

### Swipe Back Gesture (iOS Web)

```javascript
let startX = 0;
let startY = 0;

document.addEventListener('touchstart', (e) => {
  startX = e.touches[0].clientX;
  startY = e.touches[0].clientY;
});

document.addEventListener('touchend', (e) => {
  const endX = e.changedTouches[0].clientX;
  const endY = e.changedTouches[0].clientY;
  const deltaX = endX - startX;
  const deltaY = Math.abs(endY - startY);
  
  // Check for edge swipe (started within 20px of left edge)
  if (startX < 20 && deltaX > 100 && deltaY < 50) {
    history.back();
  }
});
```

---

## Search Navigation

### Search Bar Patterns

```html
<!-- Expandable search -->
<div class="search-container">
  <button class="search-trigger" aria-label="Search">
    <svg><!-- Search icon --></svg>
  </button>
  
  <div class="search-expanded" hidden>
    <input type="search" placeholder="Search..." autofocus>
    <button class="search-cancel">Cancel</button>
  </div>
</div>

<!-- Persistent search -->
<div class="search-bar">
  <svg class="search-icon" aria-hidden="true"><!-- Search icon --></svg>
  <input type="search" placeholder="Search products...">
  <button class="search-clear" hidden aria-label="Clear search">
    <svg><!-- X icon --></svg>
  </button>
</div>
```

```css
.search-bar {
  display: flex;
  align-items: center;
  height: 48px;
  padding: 0 12px;
  background: var(--surface-variant);
  border-radius: 24px;
  margin: 8px 16px;
}

.search-bar input {
  flex: 1;
  border: none;
  background: none;
  font-size: 16px;
  padding: 8px;
}

.search-bar input:focus {
  outline: none;
}

.search-icon {
  width: 20px;
  height: 20px;
  color: var(--text-secondary);
}
```

---

## Breadcrumbs (Mobile Adaptation)

On mobile, show only current and parent level:

```html
<!-- Desktop: Full breadcrumb -->
<nav aria-label="Breadcrumb">
  <ol class="breadcrumb">
    <li><a href="/">Home</a></li>
    <li><a href="/electronics">Electronics</a></li>
    <li><a href="/electronics/phones">Phones</a></li>
    <li aria-current="page">iPhone 15</li>
  </ol>
</nav>

<!-- Mobile: Simplified -->
<nav aria-label="Breadcrumb" class="breadcrumb-mobile">
  <a href="/electronics/phones" class="parent-link">
    <svg aria-hidden="true"><!-- Chevron left --></svg>
    Phones
  </a>
</nav>
```

---

## Key Takeaways

1. **Bottom tab bar for primary navigation** — 3-5 items max
2. **Always include labels** — Icons alone are ambiguous
3. **Respect platform back patterns** — iOS edge swipe, Android system back
4. **One FAB maximum** — For the single most important action
5. **Hamburger adds friction** — Reserve for secondary navigation
6. **Fixed bottom elements need safe area** — Account for notches
7. **Test with one hand** — Primary nav must be thumb-accessible
