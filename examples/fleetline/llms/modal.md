# Modal

Category: Overlays · page `components/modal.html` · CSS `css/components/modal.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `modal` — Modal Dialog | core | ready · stable | state:closed state:open size:sm size:md size:lg variant:fullscreen-mobile variant:scrolling-body |
| `alert-dialog` — Alert / Confirm Dialog | core | ready · stable | variant:confirm-destructive |

## Usage

Use a modal when the dispatcher must finish or cancel a short task before going on: reassign a mechanic, edit a service interval, confirm a deletion. The rest of the page becomes inert until it closes.
- Modal dialog — a focused task with a form or a decision. Keep it to one screen of content; long flows belong on a page.
- Alert dialog — a confirmation that interrupts: destructive or irreversible actions only ("Delete work order WO-1042?").
- Don't use a modal for information the user doesn't have to act on (use an alert or toast), for filters (use a drawer or popover), or open a modal from a modal.
Content: the title states the task or the consequence as a question ("Reassign work order WO-1042", "Delete work order WO-1042?"). Buttons are verb + object ("Delete work order", "Reassign mechanic"); the dismiss action is "Cancel", never "No" or "OK". Put the primary action at the inline end with Cancel beside it.

## Anatomy

- Backdrop — ::backdrop with --color-bg-overlay
- Container — <dialog class="modal"> on the overlay surface, --overlay-radius and --overlay-shadow
- Header — .modal__header : title .modal__title (an h2 ) and close button .modal__close ; alert dialogs show a tone icon .modal__icon instead of the close button
- Body — .modal__body , the only part that scrolls
- Footer — .modal__footer : Cancel, then the primary action at the inline end

## Examples

### modal · state:closed

```html
<div class="ds-demo__row">
              <button type="button" class="btn btn--secondary" commandfor="dlg-reassign" command="show-modal">Reassign mechanic</button>
            </div>
            <p>Closed: only the trigger is in the page. The dialog is <code>display: none</code> until opened.</p>
```

### modal · state:open size:md

```html
<dialog open class="modal is-preview" aria-labelledby="pv-reassign-title" aria-describedby="pv-reassign-desc">
              <div class="modal__header">
                <h2 class="modal__title" id="pv-reassign-title">Reassign work order WO-1042</h2>
                <button type="button" class="btn btn--ghost btn--sm modal__close" aria-label="Close">
                  <svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg>
                </button>
              </div>
              <div class="modal__body">
                <p id="pv-reassign-desc">Brake inspection on van KX-24 is assigned to Dana Ortiz, who is off shift until Thursday. Pick a mechanic at Northside Depot.</p>
              </div>
              <div class="modal__footer">
                <button type="button" class="btn btn--ghost">Cancel</button>
                <button type="button" class="btn btn--primary">Reassign mechanic</button>
              </div>
            </dialog>
```

### modal · size:sm

```html
<dialog open class="modal modal--sm is-preview" aria-labelledby="pv-sm-title">
              <div class="modal__header">
                <h2 class="modal__title" id="pv-sm-title">Rename depot</h2>
                <button type="button" class="btn btn--ghost btn--sm modal__close" aria-label="Close">
                  <svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg>
                </button>
              </div>
              <div class="modal__body"><p>Northside Depot will be renamed on every work order and report.</p></div>
              <div class="modal__footer">
                <button type="button" class="btn btn--ghost">Cancel</button>
                <button type="button" class="btn btn--primary">Rename depot</button>
              </div>
            </dialog>
            <div class="ds-demo__row"><button type="button" class="btn btn--secondary" commandfor="dlg-sm" command="show-modal">Open small</button></div>
```

### modal · size:lg

```html
<dialog open class="modal modal--lg is-preview" aria-labelledby="pv-lg-title">
              <div class="modal__header">
                <h2 class="modal__title" id="pv-lg-title">Service plan for KX-24</h2>
                <button type="button" class="btn btn--ghost btn--sm modal__close" aria-label="Close">
                  <svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg>
                </button>
              </div>
              <div class="modal__body">
                <p>Oil change every 10,000 km, brake inspection every 20,000 km, tire rotation every 12,000 km. Next due: brake inspection at 84,000 km (1,200 km overdue).</p>
              </div>
              <div class="modal__footer">
                <button type="button" class="btn btn--ghost">Cancel</button>
                <button type="button" class="btn btn--primary">Save service plan</button>
              </div>
            </dialog>
            <div class="ds-demo__row"><button type="button" class="btn btn--secondary" commandfor="dlg-lg" command="show-modal">Open large</button></div>
```

### modal · variant:scrolling-body

```html
<dialog open class="modal modal--scroll is-preview" aria-labelledby="pv-scroll-title" style="max-block-size: 22rem;">
              <div class="modal__header">
                <h2 class="modal__title" id="pv-scroll-title">Service history — KX-24</h2>
                <button type="button" class="btn btn--ghost btn--sm modal__close" aria-label="Close">
                  <svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg>
                </button>
              </div>
              <div class="modal__body" tabindex="0" aria-label="Service history entries">
                <p>14 Sep 2026 — Oil and filter change, 82,800 km. Mechanic: Dana Ortiz.</p>
                <p>2 Aug 2026 — Front brake pads replaced, 79,400 km. Mechanic: Lee Park.</p>
                <p>19 Jun 2026 — Tire rotation and alignment, 75,100 km. Mechanic: Dana Ortiz.</p>
                <p>3 May 2026 — Annual roadworthiness inspection passed, 71,600 km.</p>
                <p>22 Mar 2026 — Coolant hose replaced after leak report, 67,900 km.</p>
                <p>8 Feb 2026 — Oil and filter change, 64,300 km. Mechanic: Lee Park.</p>
              </div>
              <div class="modal__footer">
                <button type="button" class="btn btn--primary">Export service log</button>
              </div>
            </dialog>
            <div class="ds-demo__row"><button type="button" class="btn btn--secondary" commandfor="dlg-scroll" command="show-modal">Open service history</button></div>
```

### modal · variant:fullscreen-mobile

```html
<div style="max-inline-size: 20rem; block-size: 26rem; border: 1px solid var(--color-border-default); border-radius: var(--radius-lg); overflow: hidden;">
              <dialog open class="modal modal--fullscreen-mobile is-preview is-mobile" aria-labelledby="pv-mobile-title">
                <div class="modal__header">
                  <h2 class="modal__title" id="pv-mobile-title">Log inspection</h2>
                  <button type="button" class="btn btn--ghost btn--sm modal__close" aria-label="Close">
                    <svg class="btn__icon" aria-hidden="true" focusable="false"><use href="#icon-x"></use></svg>
                  </button>
                </div>
                <div class="modal__body"><p>Below 40rem the dialog fills the screen and stacks its actions full width, so mechanics on a tablet in portrait get 44px targets.</p></div>
                <div class="modal__footer">
                  <button type="button" class="btn btn--ghost">Cancel</button>
                  <button type="button" class="btn btn--primary">Save inspection</button>
                </div>
              </dialog>
            </div>
            <div class="ds-demo__row"><button type="button" class="btn btn--secondary" commandfor="dlg-mobile" command="show-modal">Open (resize below 40rem)</button></div>
```

### alert-dialog · variant:confirm-destructive

```html
<dialog open class="modal modal--alert modal--danger is-preview" role="alertdialog" aria-labelledby="pv-del-title" aria-describedby="pv-del-desc">
              <div class="modal__header">
                <span class="modal__icon" aria-hidden="true"><svg focusable="false"><use href="#icon-trash"></use></svg></span>
                <h2 class="modal__title" id="pv-del-title">Delete work order WO-1042?</h2>
              </div>
              <div class="modal__body">
                <p id="pv-del-desc">The brake inspection for KX-24, its 3 logged tasks and 12 photos will be deleted. This can't be undone.</p>
              </div>
              <div class="modal__footer">
                <button type="button" class="btn btn--ghost">Cancel</button>
                <button type="button" class="btn btn--destructive">Delete work order</button>
              </div>
            </dialog>
            <div class="ds-demo__row"><button type="button" class="btn btn--destructive" commandfor="dlg-delete" command="show-modal">Delete work order</button></div>
```

## API

Hook | Values | Purpose
<dialog class="modal"> | block | Modal surface; open with command="show-modal"
.modal--sm | --lg | modifier | Width 30rem / 48rem (md 40rem default), always within the viewport
.modal--scroll | modifier | Adds separators above and below a long scrolling body
.modal--fullscreen-mobile | modifier | Fills the screen below 40rem, stacks footer actions
.modal--alert + .modal--danger | --warning | modifier | Alert dialog layout and icon tone; pair with role="alertdialog"
.modal__header | __title | __close | __icon | __body | __footer | parts | See anatomy
commandfor="id" command="show-modal | close" | invoker attributes | Open and close without JavaScript
closedby="any" | attribute | Light dismiss (backdrop click) for non-destructive, non-form dialogs only; enhancement
autofocus | attribute | Initial focus target; on alert dialogs put it on Cancel
.is-preview | .is-mobile | docs-only class | Render an open dialog in the page flow / force the mobile layout

## Do and don't

Cancel Delete work order Do name the action and the object, and focus Cancel first in destructive confirmations. No OK Don't ask "Are you sure?" with Yes/No or OK: people click through without reading.

## Accessibility

Keyboard interaction
Key | Behavior
Tab / Shift + Tab | Moves between focusable elements inside the dialog; the page behind is inert
Esc | Closes the dialog (on an alert dialog it equals Cancel)
Enter / Space | Activates the focused button
- Role: native <dialog> opened with showModal() (via the invoker) is a modal dialog — top layer, inert background, Esc handling. Alert dialogs add role="alertdialog" (APG Alert Dialog).
- Name and description: aria-labelledby → the title; aria-describedby → the main paragraph, read on open.
- Focus: moves to the first focusable element or the autofocus one (Cancel in alert dialogs, the least destructive action). On close the browser returns focus to the invoker.
- No light dismiss on alert dialogs or dialogs with forms: an accidental click must not lose input.
- The scrolling body is focusable ( tabindex="0" + aria-label ) so keyboard users can scroll it.
- Fallback: browsers without invoker commands need the shared invoker polyfill that maps command to showModal() / close() .
- Forced colors: the dialog keeps a CanvasText border.

## Tokens

Custom property | Purpose
--color-elevation-surface-overlay | Dialog surface
--overlay-radius , --overlay-shadow | Corner radius and elevation
--color-bg-overlay | Backdrop scrim
--size-container-sm | -md | Widths (sm = 0.75 × container-sm)
--color-feedback-{danger|warning|info}-{bg|icon} | Alert dialog icon tone
--typography-h4-* | Title
--motion-duration-base | -fast , --motion-easing-enter | -exit | Enter and exit
--size-touch-target | Full-width footer buttons on mobile
