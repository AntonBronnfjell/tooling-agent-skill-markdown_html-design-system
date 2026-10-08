# Toast

Category: Feedback · page `components/toast.html` · CSS `css/components/toast.css` · JS `js/toast.js` (export `init(root)`)

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `toast` — Toast | core | ready · stable | variant:info variant:success variant:warning variant:danger variant:with-action state:stacked |

## Usage

Use a toast to confirm something that happened in the background or off-screen ("Work order WO-1042 closed", "Odometer readings synced") without interrupting work. Toasts disappear on their own, so they must never be the only place important information lives.
- Errors that block the user or need a decision belong in an alert or an alert dialog , not a toast.
- Two lines at most: a title (what happened) and an optional message. One action at most ("Undo"); the same action must also be reachable elsewhere.
- No more than 3 on screen; the oldest leaves when a fourth arrives.

## Anatomy

- Region — .toast-region , top layer, bottom inline-end, labelled "Notifications", with one polite role="status"
- Toast — .toast.toast--{tone} , overlay surface with a tone bar
- Icon — .toast__icon , per tone, aria-hidden
- Title and message — .toast__title , .toast__message
- Action (optional) — .toast__action
- Close — .toast__close , "Dismiss notification"

## Examples

### toast · variant:info

```html
<div class="toast toast--info">
              <svg class="toast__icon" aria-hidden="true" focusable="false"><use href="#icon-info"></use></svg>
              <div class="toast__content"><p class="toast__title">Odometer readings synced</p><p class="toast__message">42 vehicles updated from telematics.</p></div>
              <button type="button" class="btn btn--ghost btn--sm toast__close" aria-label="Dismiss notification"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button>
            </div>
            <div class="ds-demo__row"><button type="button" class="btn btn--secondary btn--sm" data-toast data-toast-tone="info" data-toast-title="Odometer readings synced" data-toast-message="42 vehicles updated from telematics.">Show info toast</button></div>
```

### toast · variant:success

```html
<div class="toast toast--success">
              <svg class="toast__icon" aria-hidden="true" focusable="false"><use href="#icon-circle-check"></use></svg>
              <div class="toast__content"><p class="toast__title">Work order WO-1042 closed</p><p class="toast__message">Invoice sent to Northside Depot.</p></div>
              <button type="button" class="btn btn--ghost btn--sm toast__close" aria-label="Dismiss notification"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button>
            </div>
            <div class="ds-demo__row"><button type="button" class="btn btn--secondary btn--sm" data-toast data-toast-tone="success" data-toast-title="Work order WO-1042 closed" data-toast-message="Invoice sent to Northside Depot.">Show success toast</button></div>
```

### toast · variant:warning

```html
<div class="toast toast--warning">
              <svg class="toast__icon" aria-hidden="true" focusable="false"><use href="#icon-triangle-alert"></use></svg>
              <div class="toast__content"><p class="toast__title">KX-24 assigned while overdue</p><p class="toast__message">Brake inspection is 1,200 km overdue.</p></div>
              <button type="button" class="btn btn--ghost btn--sm toast__close" aria-label="Dismiss notification"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button>
            </div>
            <div class="ds-demo__row"><button type="button" class="btn btn--secondary btn--sm" data-toast data-toast-tone="warning" data-toast-title="KX-24 assigned while overdue" data-toast-message="Brake inspection is 1,200 km overdue.">Show warning toast</button></div>
```

### toast · variant:danger

```html
<div class="toast toast--danger">
              <svg class="toast__icon" aria-hidden="true" focusable="false"><use href="#icon-circle-x"></use></svg>
              <div class="toast__content"><p class="toast__title">Telematics sync failed</p><p class="toast__message">We'll retry in 5 minutes.</p></div>
              <button type="button" class="btn btn--ghost btn--sm toast__close" aria-label="Dismiss notification"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button>
            </div>
            <div class="ds-demo__row"><button type="button" class="btn btn--secondary btn--sm" data-toast data-toast-tone="danger" data-toast-title="Telematics sync failed" data-toast-message="We'll retry in 5 minutes.">Show danger toast</button></div>
```

### toast · variant:with-action

```html
<div class="toast toast--info">
              <svg class="toast__icon" aria-hidden="true" focusable="false"><use href="#icon-info"></use></svg>
              <div class="toast__content"><p class="toast__title">Work order WO-1042 deleted</p></div>
              <button type="button" class="btn btn--secondary btn--sm toast__action">Undo</button>
              <button type="button" class="btn btn--ghost btn--sm toast__close" aria-label="Dismiss notification"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button>
            </div>
            <div class="ds-demo__row"><button type="button" class="btn btn--secondary btn--sm" data-toast data-toast-tone="info" data-toast-title="Work order WO-1042 deleted" data-toast-action="Undo" data-toast-action-done="Work order WO-1042 restored">Show toast with undo</button></div>
```

### toast · state:stacked

```html
<ol class="toast-stack" aria-label="Stacked toasts preview">
              <li class="toast toast--success">
                <svg class="toast__icon" aria-hidden="true" focusable="false"><use href="#icon-circle-check"></use></svg>
                <div class="toast__content"><p class="toast__title">Mechanic Lee Park assigned</p></div>
                <button type="button" class="btn btn--ghost btn--sm toast__close" aria-label="Dismiss notification"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button>
              </li>
              <li class="toast toast--info">
                <svg class="toast__icon" aria-hidden="true" focusable="false"><use href="#icon-info"></use></svg>
                <div class="toast__content"><p class="toast__title">Odometer readings synced</p></div>
                <button type="button" class="btn btn--ghost btn--sm toast__close" aria-label="Dismiss notification"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button>
              </li>
              <li class="toast toast--success">
                <svg class="toast__icon" aria-hidden="true" focusable="false"><use href="#icon-circle-check"></use></svg>
                <div class="toast__content"><p class="toast__title">Work order WO-1042 closed</p></div>
                <button type="button" class="btn btn--ghost btn--sm toast__close" aria-label="Dismiss notification"><svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg></button>
              </li>
            </ol>
            <p>Newest at the bottom, nearest the screen edge; at most 3. Click the info, success and warning buttons quickly to see the real stack.</p>
```

## API

Hook | Values | Purpose
toast({ tone, title, message, action, duration }) | JS | Shows a toast; returns { dismiss } . Tone: info (default), success, warning, danger. action = { label, onAction }
init(root) | JS | Wires [data-toast] buttons ( data-toast-tone | -title | -message | -action ); safe to call twice
.toast--info | --success | --warning | --danger | modifier | Tone of the bar and icon
.toast__icon | __content | __title | __message | __action | __close | parts | See anatomy
[data-state="closing"] | attribute (set by JS) | Exit transition
Timing | 6s · 10s with action | Paused while the pointer or focus is in the region

## Do and don't

Work order WO-1042 closed
Do confirm a completed action with the object's name.
Payment card declined
Update billing details to keep dispatching.
Don't use a disappearing toast for a blocking problem. Use an alert that stays.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Toasts are at the end of the document; their action and close buttons are reachable. While focus is inside, timers pause
Enter / Space | Activates Undo or Dismiss; focus returns to where it was before entering the region
- Announcements go through one polite role="status" node (title + message), so screen readers aren't interrupted and don't read button names.
- WCAG 2.2.1 timing: at least 6s (10s with an action), paused on hover and focus, and every toast has a close button.
- The region is a labelled landmark ("Notifications") so it can be found with landmark navigation.
- Tone is shown by icon shape and words, not color alone. Reduced motion removes the slide; toasts appear and disappear instantly.

## Tokens

Custom property | Purpose
--color-elevation-surface-overlay , --elevation-overlay | Surface and shadow
--color-feedback-{tone}-icon | Tone bar and icon
--z-toast | Stacking when the top layer isn't available
--motion-duration-base | -fast , --motion-easing-enter | -exit | Slide in and out
--space-2 | -4 | Gap between toasts, distance from the screen edge
