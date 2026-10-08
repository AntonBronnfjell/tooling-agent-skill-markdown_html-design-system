# Theme Toggle

Category: Actions · page `components/theme-toggle.html` · CSS `css/components/theme-toggle.css` · JS `js/theme-toggle.js` (export `init(root)`)

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `theme-toggle` — Theme Toggle | core | ready · stable | state:system state:light state:dark state:focus-visible |

## Usage

Let people choose how Fleetline looks. Dispatchers on night shift prefer dark; mechanics outdoors usually need light. System is the default and follows the device setting.
- Cycling button in the app header: one click per step, the name always states the current theme ("Theme: dark").
- Radio group on the settings page: all options visible, nothing hidden behind clicks.
- Labels are nouns: "System", "Light", "Dark". Don't describe the effect ("Easy on the eyes").
- High contrast follows the OS ( prefers-contrast: more ); don't add it as a fourth option unless research asks for it.

## Anatomy

- Button — .btn.btn--ghost.theme-toggle[data-theme-cycle]
- Icons — three svg.theme-toggle__icon[data-for] ; only the current one shows
- Label — .theme-toggle__label[data-theme-label] , updated by js/theme.js
- Radio group — fieldset.theme-choice + legend + three label.theme-choice__option wrapping a radio

## Examples

### theme-toggle · variant:cycle

```html
<div class="ds-demo__row"><button type="button" class="btn btn--ghost theme-toggle" data-theme-cycle data-themes="system light dark"><svg class="theme-toggle__icon" data-for="system" aria-hidden="true" focusable="false"><use href="#icon-monitor"></use></svg><svg class="theme-toggle__icon" data-for="light" aria-hidden="true" focusable="false"><use href="#icon-sun"></use></svg><svg class="theme-toggle__icon" data-for="dark" aria-hidden="true" focusable="false"><use href="#icon-moon"></use></svg><span class="theme-toggle__label" data-theme-label>Theme: system</span></button></div>
            <p>Live: cycles System → Light → Dark; the name says the current theme.</p>
```

### theme-toggle · variant:radio-group

```html
<fieldset class="theme-choice" data-theme-choice><legend class="theme-choice__legend">Appearance</legend><label class="theme-choice__option"><input type="radio" name="theme-live" value="system" checked><svg class="theme-choice__icon" aria-hidden="true" focusable="false"><use href="#icon-monitor"></use></svg>System</label><label class="theme-choice__option"><input type="radio" name="theme-live" value="light"><svg class="theme-choice__icon" aria-hidden="true" focusable="false"><use href="#icon-sun"></use></svg>Light</label><label class="theme-choice__option"><input type="radio" name="theme-live" value="dark"><svg class="theme-choice__icon" aria-hidden="true" focusable="false"><use href="#icon-moon"></use></svg>Dark</label></fieldset>
            <p>Live: settings form. System follows the operating system.</p>
```

### theme-toggle · state:system

```html
<div class="ds-demo__row"><button type="button" class="btn btn--ghost theme-toggle" data-preview="system"><svg class="theme-toggle__icon" data-for="system" aria-hidden="true" focusable="false"><use href="#icon-monitor"></use></svg><svg class="theme-toggle__icon" data-for="light" aria-hidden="true" focusable="false"><use href="#icon-sun"></use></svg><svg class="theme-toggle__icon" data-for="dark" aria-hidden="true" focusable="false"><use href="#icon-moon"></use></svg><span class="theme-toggle__label" data-theme-label>Theme: system</span></button></div><div inert><fieldset class="theme-choice"><legend class="theme-choice__legend">Appearance</legend><label class="theme-choice__option"><input type="radio" name="theme-s" value="system" checked><svg class="theme-choice__icon" aria-hidden="true" focusable="false"><use href="#icon-monitor"></use></svg>System</label><label class="theme-choice__option"><input type="radio" name="theme-s" value="light"><svg class="theme-choice__icon" aria-hidden="true" focusable="false"><use href="#icon-sun"></use></svg>Light</label><label class="theme-choice__option"><input type="radio" name="theme-s" value="dark"><svg class="theme-choice__icon" aria-hidden="true" focusable="false"><use href="#icon-moon"></use></svg>Dark</label></fieldset></div>
```

### theme-toggle · state:light

```html
<div class="ds-demo__row"><button type="button" class="btn btn--ghost theme-toggle" data-preview="light"><svg class="theme-toggle__icon" data-for="system" aria-hidden="true" focusable="false"><use href="#icon-monitor"></use></svg><svg class="theme-toggle__icon" data-for="light" aria-hidden="true" focusable="false"><use href="#icon-sun"></use></svg><svg class="theme-toggle__icon" data-for="dark" aria-hidden="true" focusable="false"><use href="#icon-moon"></use></svg><span class="theme-toggle__label" data-theme-label>Theme: light</span></button></div><div inert><fieldset class="theme-choice"><legend class="theme-choice__legend">Appearance</legend><label class="theme-choice__option"><input type="radio" name="theme-l" value="system"><svg class="theme-choice__icon" aria-hidden="true" focusable="false"><use href="#icon-monitor"></use></svg>System</label><label class="theme-choice__option"><input type="radio" name="theme-l" value="light" checked><svg class="theme-choice__icon" aria-hidden="true" focusable="false"><use href="#icon-sun"></use></svg>Light</label><label class="theme-choice__option"><input type="radio" name="theme-l" value="dark"><svg class="theme-choice__icon" aria-hidden="true" focusable="false"><use href="#icon-moon"></use></svg>Dark</label></fieldset></div>
```

### theme-toggle · state:dark

```html
<div class="ds-demo__row"><button type="button" class="btn btn--ghost theme-toggle" data-preview="dark"><svg class="theme-toggle__icon" data-for="system" aria-hidden="true" focusable="false"><use href="#icon-monitor"></use></svg><svg class="theme-toggle__icon" data-for="light" aria-hidden="true" focusable="false"><use href="#icon-sun"></use></svg><svg class="theme-toggle__icon" data-for="dark" aria-hidden="true" focusable="false"><use href="#icon-moon"></use></svg><span class="theme-toggle__label" data-theme-label>Theme: dark</span></button></div><div inert><fieldset class="theme-choice"><legend class="theme-choice__legend">Appearance</legend><label class="theme-choice__option"><input type="radio" name="theme-d" value="system"><svg class="theme-choice__icon" aria-hidden="true" focusable="false"><use href="#icon-monitor"></use></svg>System</label><label class="theme-choice__option"><input type="radio" name="theme-d" value="light"><svg class="theme-choice__icon" aria-hidden="true" focusable="false"><use href="#icon-sun"></use></svg>Light</label><label class="theme-choice__option"><input type="radio" name="theme-d" value="dark" checked><svg class="theme-choice__icon" aria-hidden="true" focusable="false"><use href="#icon-moon"></use></svg>Dark</label></fieldset></div>
```

### theme-toggle · state:focus-visible

```html
<div class="ds-demo__row"><button type="button" class="btn btn--ghost theme-toggle is-focus-visible" data-preview="system"><svg class="theme-toggle__icon" data-for="system" aria-hidden="true" focusable="false"><use href="#icon-monitor"></use></svg><svg class="theme-toggle__icon" data-for="light" aria-hidden="true" focusable="false"><use href="#icon-sun"></use></svg><svg class="theme-toggle__icon" data-for="dark" aria-hidden="true" focusable="false"><use href="#icon-moon"></use></svg><span class="theme-toggle__label" data-theme-label>Theme: system</span></button></div><div inert><fieldset class="theme-choice"><legend class="theme-choice__legend">Appearance</legend><label class="theme-choice__option"><input type="radio" name="theme-f" value="system"><svg class="theme-choice__icon" aria-hidden="true" focusable="false"><use href="#icon-monitor"></use></svg>System</label><label class="theme-choice__option"><input type="radio" name="theme-f" value="light" checked><svg class="theme-choice__icon" aria-hidden="true" focusable="false"><use href="#icon-sun"></use></svg>Light</label><label class="theme-choice__option is-focus-visible"><input type="radio" name="theme-f" value="dark"><svg class="theme-choice__icon" aria-hidden="true" focusable="false"><use href="#icon-moon"></use></svg>Dark</label></fieldset></div>
```

## API

Hook | Values | Purpose
.theme-toggle | block class on a .btn | Cycling theme button
data-theme-cycle , data-themes | attribute | Enhanced by js/theme.js ; themes in cycle order
.theme-toggle__icon[data-for] | part | System / light / dark icon
[data-theme-label] | attribute | Text updated to "Theme: …"
.theme-choice[data-theme-choice] | block + attribute | Radio group, wired by js/theme-toggle.js
.theme-choice__option | part | Label wrapping a radio
data-preview | docs-only attribute | Freeze the icon of a theme
setTheme() , getTheme() , onThemeChange() | JS (theme.js) | Runtime API

## Do and don't

Theme: dark Do say the current theme in the name.
<button aria-label="Dark mode" aria-pressed="false"> on a three-way cycle
Don't use aria-pressed on a button that cycles through three themes — pressed/unpressed can't describe it.

## Accessibility

Keyboard interaction
Key | Behavior
Enter / Space (button) | Switches to the next theme; the name updates ("Theme: light")
Tab (radio group) | Moves into the group, to the checked option
↑ ↓ ← → | Select the previous / next theme (native radios)
- The choice persists in localStorage (try/catch for private mode) and syncs across tabs through the storage event.
- The no-flash snippet in <head> applies the saved theme before first paint.
- Checked option: selected fill, border and semibold label — not color alone. Forced colors use Highlight .

## Tokens

Custom property | Purpose
--color-action-secondary-* | Option rest / hover
--color-selected-bg | -fg | -border | Checked option
--size-control-md , --button-radius | Option size and shape
--icon-size-sm , --icon-stroke | Icons
--focus-ring-* | Focus ring
