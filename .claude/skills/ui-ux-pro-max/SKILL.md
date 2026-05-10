# UI UX Pro Max

## When to Apply

Use this skill for tasks involving **UI structure, visual design, interaction patterns, or user experience quality**. Skip it for backend logic, APIs, databases, or non-visual work.

## Priority-Based Rule Categories (1-10)

The framework prioritizes rules by impact:

1. **Accessibility** (CRITICAL) — Contrast 4.5:1, keyboard navigation, ARIA labels
2. **Touch & Interaction** (CRITICAL) — 44×44px minimum, 8px spacing, loading feedback
3. **Performance** (HIGH) — WebP/AVIF images, lazy loading, CLS < 0.1
4. **Style Selection** (HIGH) — Match product type, consistency, SVG icons
5. **Layout & Responsive** (HIGH) — Mobile-first, viewport meta, no horizontal scroll
6. **Typography & Color** (MEDIUM) — 16px base, 1.5 line-height, semantic tokens
7. **Animation** (MEDIUM) — 150-300ms duration, meaningful motion, reduced-motion support
8. **Forms & Feedback** (MEDIUM) — Visible labels, error placement, progressive disclosure
9. **Navigation Patterns** (HIGH) — Predictable back, ≤5 bottom nav items, deep linking
10. **Charts & Data** (LOW) — Match type to data, accessible colors, legends visible

## Key Implementation Steps

**Step 1:** Analyze user requirements (product type, audience, style keywords)

**Step 2:** Generate design system using CLI:
```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "<query>" --design-system -p "Project"
```

**Step 3:** Supplement with domain searches for specific needs (style, color, typography, UX)

**Step 4:** Apply stack-specific guidelines for the target framework

## Common Professional Standards

**Icons:** Use vector-based SVG only; never use emoji as structural icons. Maintain consistent stroke width and sizing within a visual hierarchy.

**Interaction:** Provide tap feedback within 80-150ms. Maintain 44×44pt minimum touch targets with expanded hit areas for smaller icons.

**Light/Dark Mode:** Test contrast independently in both themes. Maintain 4.5:1 for primary text, 3:1 for secondary text.

**Layout:** Respect safe areas for fixed elements. Use 4/8pt spacing rhythm. Adapt gutters by device size and orientation.

**Accessibility:** Ensure focus order matches visual hierarchy. Provide descriptive labels for all interactive elements. Support reduced motion and dynamic text scaling.

## Pre-Delivery Checklist

- No emoji icons; use consistent SVG sets
- Touch targets ≥44×44pt with clear pressed feedback
- Text contrast ≥4.5:1 (primary) in both light and dark modes
- Safe areas respected for headers and fixed bars
- 4/8dp spacing rhythm maintained throughout
- Screen reader focus order and labels tested
- Reduced motion and dynamic type supported
