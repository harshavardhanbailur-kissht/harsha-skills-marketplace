# Design Extraction Techniques

## Overview

This reference provides JavaScript code snippets for extracting design tokens from any website. These can be run in browser DevTools console or adapted for automated extraction.

---

## Color Extraction

### Get All CSS Custom Properties

```javascript
const getAllCustomProperties = () => {
  const props = new Map();
  
  // Get root computed styles
  const rootStyles = getComputedStyle(document.documentElement);
  
  // Extract from computed styles
  for (const prop of rootStyles) {
    if (prop.startsWith('--')) {
      props.set(prop, rootStyles.getPropertyValue(prop).trim());
    }
  }
  
  // Extract from all stylesheets
  for (const sheet of document.styleSheets) {
    try {
      for (const rule of sheet.cssRules) {
        if (rule.style) {
          for (let i = 0; i < rule.style.length; i++) {
            const prop = rule.style[i];
            if (prop.startsWith('--')) {
              props.set(prop, rule.style.getPropertyValue(prop).trim());
            }
          }
        }
      }
    } catch (e) {
      // Cross-origin stylesheets will throw
      console.log('Skipped cross-origin stylesheet');
    }
  }
  
  return Object.fromEntries(props);
};

// Usage
const customProps = getAllCustomProperties();
console.log(customProps);
```

### Get All Colors from Computed Styles

```javascript
const getAllColors = () => {
  const colors = new Map();
  
  document.querySelectorAll('*').forEach(el => {
    const style = getComputedStyle(el);
    const colorProps = [
      'color',
      'backgroundColor', 
      'borderColor',
      'borderTopColor',
      'borderRightColor',
      'borderBottomColor',
      'borderLeftColor',
      'outlineColor',
      'fill',
      'stroke'
    ];
    
    colorProps.forEach(prop => {
      const value = style[prop];
      if (value && 
          value !== 'rgba(0, 0, 0, 0)' && 
          value !== 'transparent' &&
          value !== 'inherit' &&
          value !== 'currentcolor') {
        // Track frequency
        colors.set(value, (colors.get(value) || 0) + 1);
      }
    });
  });
  
  // Sort by frequency
  return [...colors.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([color, count]) => ({ color, count }));
};

// Usage
const colors = getAllColors();
console.table(colors.slice(0, 20)); // Top 20 colors
```

### Convert Colors to Hex

```javascript
const rgbToHex = (rgb) => {
  const match = rgb.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  if (!match) return rgb;
  
  const r = parseInt(match[1]).toString(16).padStart(2, '0');
  const g = parseInt(match[2]).toString(16).padStart(2, '0');
  const b = parseInt(match[3]).toString(16).padStart(2, '0');
  
  return `#${r}${g}${b}`;
};

// Get unique colors as hex
const getUniqueHexColors = () => {
  const colors = getAllColors();
  const hexColors = new Set();
  
  colors.forEach(({ color }) => {
    hexColors.add(rgbToHex(color));
  });
  
  return [...hexColors];
};
```

### Categorize Colors

```javascript
const categorizeColors = (colors) => {
  const categories = {
    brand: [],      // Saturated, distinctive colors
    neutral: [],    // Grays, blacks, whites
    semantic: {
      success: [],
      error: [],
      warning: [],
      info: []
    }
  };
  
  colors.forEach(({ color, count }) => {
    const hex = rgbToHex(color);
    const rgb = hexToRgb(hex);
    
    // Calculate saturation and lightness
    const { s, l } = rgbToHsl(rgb.r, rgb.g, rgb.b);
    
    if (s < 10) {
      categories.neutral.push({ color: hex, count });
    } else {
      // Detect semantic colors by hue
      const { h } = rgbToHsl(rgb.r, rgb.g, rgb.b);
      
      if (h >= 100 && h <= 140) categories.semantic.success.push(hex);
      else if (h >= 0 && h <= 20 || h >= 340) categories.semantic.error.push(hex);
      else if (h >= 40 && h <= 60) categories.semantic.warning.push(hex);
      else if (h >= 200 && h <= 240) categories.semantic.info.push(hex);
      else categories.brand.push({ color: hex, count });
    }
  });
  
  return categories;
};
```

---

## Typography Extraction

### Get All Font Families

```javascript
const getFontFamilies = () => {
  const fonts = new Map();
  
  document.querySelectorAll('*').forEach(el => {
    const fontFamily = getComputedStyle(el).fontFamily;
    fonts.set(fontFamily, (fonts.get(fontFamily) || 0) + 1);
  });
  
  return [...fonts.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([font, count]) => ({ font, count }));
};
```

### Get Font Size Scale

```javascript
const getFontSizes = () => {
  const sizes = new Map();
  
  document.querySelectorAll('*').forEach(el => {
    const fontSize = getComputedStyle(el).fontSize;
    const px = parseFloat(fontSize);
    if (!isNaN(px)) {
      sizes.set(px, (sizes.get(px) || 0) + 1);
    }
  });
  
  return [...sizes.entries()]
    .sort((a, b) => a[0] - b[0])
    .map(([size, count]) => ({ size: `${size}px`, count }));
};

// Detect scale ratio
const detectTypeScale = (sizes) => {
  const sizeValues = sizes.map(s => parseFloat(s.size));
  const ratios = [];
  
  for (let i = 1; i < sizeValues.length; i++) {
    ratios.push(sizeValues[i] / sizeValues[i-1]);
  }
  
  const avgRatio = ratios.reduce((a, b) => a + b, 0) / ratios.length;
  
  // Match to common scales
  const scales = {
    'Minor Second': 1.067,
    'Major Second': 1.125,
    'Minor Third': 1.2,
    'Major Third': 1.25,
    'Perfect Fourth': 1.333,
    'Augmented Fourth': 1.414,
    'Perfect Fifth': 1.5,
    'Golden Ratio': 1.618
  };
  
  let closestScale = 'Custom';
  let minDiff = Infinity;
  
  for (const [name, ratio] of Object.entries(scales)) {
    const diff = Math.abs(avgRatio - ratio);
    if (diff < minDiff) {
      minDiff = diff;
      closestScale = name;
    }
  }
  
  return { avgRatio, closestScale, sizes: sizeValues };
};
```

### Get Font Weights

```javascript
const getFontWeights = () => {
  const weights = new Map();
  
  document.querySelectorAll('*').forEach(el => {
    const weight = getComputedStyle(el).fontWeight;
    weights.set(weight, (weights.get(weight) || 0) + 1);
  });
  
  return [...weights.entries()]
    .sort((a, b) => parseInt(a[0]) - parseInt(b[0]))
    .map(([weight, count]) => ({ weight, count }));
};
```

### Get Line Heights

```javascript
const getLineHeights = () => {
  const lineHeights = new Map();
  
  document.querySelectorAll('*').forEach(el => {
    const style = getComputedStyle(el);
    const lineHeight = style.lineHeight;
    const fontSize = parseFloat(style.fontSize);
    
    if (lineHeight !== 'normal') {
      const lhPx = parseFloat(lineHeight);
      const ratio = (lhPx / fontSize).toFixed(2);
      lineHeights.set(ratio, (lineHeights.get(ratio) || 0) + 1);
    }
  });
  
  return [...lineHeights.entries()]
    .sort((a, b) => parseFloat(a[0]) - parseFloat(b[0]))
    .map(([ratio, count]) => ({ ratio, count }));
};
```

---

## Spacing Extraction

### Get All Spacing Values

```javascript
const getSpacingValues = () => {
  const spacing = new Map();
  
  document.querySelectorAll('*').forEach(el => {
    const style = getComputedStyle(el);
    
    const spacingProps = [
      'marginTop', 'marginRight', 'marginBottom', 'marginLeft',
      'paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft',
      'gap', 'rowGap', 'columnGap'
    ];
    
    spacingProps.forEach(prop => {
      const value = style[prop];
      const px = parseFloat(value);
      if (!isNaN(px) && px > 0 && px < 500) {
        spacing.set(px, (spacing.get(px) || 0) + 1);
      }
    });
  });
  
  return [...spacing.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([value, count]) => ({ value: `${value}px`, count }));
};
```

### Detect Spacing Base Unit

```javascript
const detectBaseUnit = (spacingValues) => {
  const values = spacingValues.map(s => parseFloat(s.value));
  
  // Check if values are divisible by 4 or 8
  const divisibleBy4 = values.filter(v => v % 4 === 0).length;
  const divisibleBy8 = values.filter(v => v % 8 === 0).length;
  
  const percentDivisibleBy4 = divisibleBy4 / values.length;
  const percentDivisibleBy8 = divisibleBy8 / values.length;
  
  if (percentDivisibleBy8 > 0.7) return { baseUnit: 8, scale: [8, 16, 24, 32, 40, 48, 64] };
  if (percentDivisibleBy4 > 0.7) return { baseUnit: 4, scale: [4, 8, 12, 16, 20, 24, 32, 40, 48] };
  
  return { baseUnit: 'custom', mostCommon: values.slice(0, 10) };
};
```

---

## Layout Extraction

### Detect Grid Systems

```javascript
const detectGridSystems = () => {
  const grids = [];
  
  document.querySelectorAll('*').forEach(el => {
    const style = getComputedStyle(el);
    
    if (style.display === 'grid' || style.display === 'inline-grid') {
      grids.push({
        element: el.tagName + (el.className ? '.' + el.className.split(' ')[0] : ''),
        columns: style.gridTemplateColumns,
        rows: style.gridTemplateRows,
        gap: style.gap,
        areas: style.gridTemplateAreas
      });
    }
  });
  
  return grids;
};
```

### Detect Flex Layouts

```javascript
const detectFlexLayouts = () => {
  const flexContainers = [];
  
  document.querySelectorAll('*').forEach(el => {
    const style = getComputedStyle(el);
    
    if (style.display === 'flex' || style.display === 'inline-flex') {
      flexContainers.push({
        element: el.tagName + (el.className ? '.' + el.className.split(' ')[0] : ''),
        direction: style.flexDirection,
        wrap: style.flexWrap,
        justify: style.justifyContent,
        align: style.alignItems,
        gap: style.gap
      });
    }
  });
  
  return flexContainers;
};
```

### Get Container Widths

```javascript
const getContainerWidths = () => {
  const widths = new Map();
  
  document.querySelectorAll('*').forEach(el => {
    const style = getComputedStyle(el);
    const maxWidth = style.maxWidth;
    
    if (maxWidth !== 'none' && maxWidth !== '100%') {
      const px = parseFloat(maxWidth);
      if (!isNaN(px) && px > 500 && px < 2000) {
        widths.set(px, (widths.get(px) || 0) + 1);
      }
    }
  });
  
  return [...widths.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([width, count]) => ({ width: `${width}px`, count }));
};
```

---

## Border & Shadow Extraction

### Get Border Radii

```javascript
const getBorderRadii = () => {
  const radii = new Map();
  
  document.querySelectorAll('*').forEach(el => {
    const style = getComputedStyle(el);
    const radius = style.borderRadius;
    
    if (radius && radius !== '0px') {
      radii.set(radius, (radii.get(radius) || 0) + 1);
    }
  });
  
  return [...radii.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([radius, count]) => ({ radius, count }));
};
```

### Get Box Shadows

```javascript
const getBoxShadows = () => {
  const shadows = new Map();
  
  document.querySelectorAll('*').forEach(el => {
    const shadow = getComputedStyle(el).boxShadow;
    
    if (shadow && shadow !== 'none') {
      shadows.set(shadow, (shadows.get(shadow) || 0) + 1);
    }
  });
  
  return [...shadows.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([shadow, count]) => ({ shadow, count }));
};
```

---

## Motion Extraction

### Get Transitions

```javascript
const getTransitions = () => {
  const transitions = new Map();
  
  document.querySelectorAll('*').forEach(el => {
    const transition = getComputedStyle(el).transition;
    
    if (transition && transition !== 'all 0s ease 0s' && transition !== 'none') {
      transitions.set(transition, (transitions.get(transition) || 0) + 1);
    }
  });
  
  return [...transitions.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([transition, count]) => ({ transition, count }));
};
```

### Get Animations

```javascript
const getAnimations = () => {
  const animations = new Map();
  
  document.querySelectorAll('*').forEach(el => {
    const animation = getComputedStyle(el).animation;
    
    if (animation && animation !== 'none') {
      animations.set(animation, (animations.get(animation) || 0) + 1);
    }
  });
  
  return [...animations.entries()]
    .map(([animation, count]) => ({ animation, count }));
};
```

---

## Complete Extraction Function

```javascript
const extractDesignSystem = () => {
  console.log('🎨 Extracting design system...\n');
  
  const designSystem = {
    colors: {
      customProperties: getAllCustomProperties(),
      computed: getAllColors().slice(0, 30)
    },
    typography: {
      families: getFontFamilies(),
      sizes: getFontSizes(),
      weights: getFontWeights(),
      lineHeights: getLineHeights()
    },
    spacing: {
      values: getSpacingValues().slice(0, 20),
      baseUnit: detectBaseUnit(getSpacingValues())
    },
    layout: {
      grids: detectGridSystems(),
      containers: getContainerWidths()
    },
    borders: {
      radii: getBorderRadii(),
      shadows: getBoxShadows()
    },
    motion: {
      transitions: getTransitions(),
      animations: getAnimations()
    }
  };
  
  console.log('✅ Design system extracted!');
  console.log(JSON.stringify(designSystem, null, 2));
  
  return designSystem;
};

// Run extraction
extractDesignSystem();
```

---

## Exporting to Design Tokens

```javascript
const toDesignTokens = (extracted) => {
  // Convert extracted data to standard token format
  return {
    colors: {
      // Map top colors to semantic names
      primary: extracted.colors.computed[0]?.color || '#3b82f6',
      // ... additional mapping
    },
    typography: {
      fontFamily: {
        sans: extracted.typography.families[0]?.font || 'system-ui',
      },
      fontSize: {
        // Map sizes to scale
      }
    },
    spacing: extracted.spacing.baseUnit.scale || [4, 8, 12, 16, 24, 32, 48],
    borderRadius: extracted.borders.radii.slice(0, 5).map(r => r.radius),
    shadow: extracted.borders.shadows.slice(0, 3).map(s => s.shadow)
  };
};
```
