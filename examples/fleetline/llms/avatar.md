# Avatar

Category: Data Display · page `components/avatar.html` · CSS `css/components/avatar.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `avatar` — Avatar | core | ready · stable | variant:image variant:initials variant:fallback-icon size:sm size:md size:lg variant:with-status |

## Usage

Use an avatar to help people recognize a mechanic, driver or dispatcher at a glance — in assignment lists, work-order headers and comments. Don't use avatars for vehicles or depots; use an icon. An avatar never replaces the name: show the name next to it, or in its accessible name when space is tight.
- Image — profile photo, cropped to a circle.
- Initials — when there's no photo. Two letters, tone chosen by hashing the person's id so it is stable everywhere.
- Fallback icon — unknown or unassigned person ("Unassigned mechanic").
- Sizes — sm 32px (dense tables), md 40px (lists), lg 48px (headers, tablet).
Status text: "Available", "Busy · on WO-4191", "Off shift until 06:00" — always written, the dot only repeats it.

## Anatomy

- Container — .avatar , circle sized by --size-control-*
- Content — img.avatar__img , or .avatar__initials , or svg.avatar__icon
- Status dot (optional) — .avatar__status[data-status] , with its own shape per status
- Label (optional) — .avatar-label with name and detail text

## Examples

### avatar · variant:image

```html
<span class="avatar"><img class="avatar__img" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' fill='%23cbd5e1'/%3E%3Ccircle cx='32' cy='25' r='12' fill='%23475569'/%3E%3Cpath d='M10 64c2-14 11-21 22-21s20 7 22 21z' fill='%23475569'/%3E%3C/svg%3E" alt="Marta Quintero"></span>
```

### avatar · variant:initials

```html
<div class="ds-demo__row">
              <span class="avatar avatar--tone-teal" role="img" aria-label="Idris Okafor"><span class="avatar__initials" aria-hidden="true">IO</span></span>
              <span class="avatar avatar--tone-blue" role="img" aria-label="Lena Brandt"><span class="avatar__initials" aria-hidden="true">LB</span></span>
              <span class="avatar avatar--tone-neutral" role="img" aria-label="Sami Haddad"><span class="avatar__initials" aria-hidden="true">SH</span></span>
            </div>
```

### avatar · variant:fallback-icon

```html
<span class="avatar" role="img" aria-label="Unassigned mechanic"><svg class="avatar__icon" aria-hidden="true" focusable="false"><use href="#icon-user"></use></svg></span>
```

### avatar · size:sm size:md size:lg

```html
<div class="ds-demo__row">
              <span class="avatar avatar--sm avatar--tone-teal" role="img" aria-label="Idris Okafor"><span class="avatar__initials" aria-hidden="true">IO</span></span>
              <span class="avatar avatar--tone-teal" role="img" aria-label="Idris Okafor"><span class="avatar__initials" aria-hidden="true">IO</span></span>
              <span class="avatar avatar--lg avatar--tone-teal" role="img" aria-label="Idris Okafor"><span class="avatar__initials" aria-hidden="true">IO</span></span>
            </div>
```

### avatar · variant:with-status

```html
<div class="stack stack--gap-3">
              <span class="avatar-label">
                <span class="avatar"><img class="avatar__img" src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' fill='%23cbd5e1'/%3E%3Ccircle cx='32' cy='25' r='12' fill='%23475569'/%3E%3Cpath d='M10 64c2-14 11-21 22-21s20 7 22 21z' fill='%23475569'/%3E%3C/svg%3E" alt=""><span class="avatar__status" data-status="available"></span></span>
                <span class="avatar-label__text"><span class="avatar-label__name">Marta Quintero</span><span class="avatar-label__detail">Available · bay 2</span></span>
              </span>
              <span class="avatar-label">
                <span class="avatar avatar--tone-blue"><span class="avatar__initials" aria-hidden="true">LB</span><span class="avatar__status" data-status="busy"></span></span>
                <span class="avatar-label__text"><span class="avatar-label__name">Lena Brandt</span><span class="avatar-label__detail">Busy · on WO-4191</span></span>
              </span>
              <span class="avatar-label">
                <span class="avatar avatar--tone-neutral"><span class="avatar__initials" aria-hidden="true">SH</span><span class="avatar__status" data-status="off"></span></span>
                <span class="avatar-label__text"><span class="avatar-label__name">Sami Haddad</span><span class="avatar-label__detail">Off shift until 06:00</span></span>
              </span>
            </div>
```

## API

Hook | Values | Purpose
.avatar | block class | Circle container
.avatar--sm | --lg | modifier class | 32 / 40 (default) / 48px
.avatar--tone-neutral | --tone-teal | --tone-blue | modifier class | Initials colors; pick with id % 3
.avatar__img | __initials | __icon | part classes | Content in fallback order
.avatar__status + data-status="available|busy|away|off" | part + attribute | Status dot: filled / bar / ring / hollow
.avatar-label , __text | __name | __detail | companion block | Avatar with name and status text

## Do and don't

Avatar + "Marta Quintero · Available"
Do pair the avatar with the name and status in text.
Green dot only.
Don’t show availability with a colored dot alone.
alt="" when the name is printed right next to it
Do avoid announcing the name twice.
alt="avatar" or alt="profile picture"
Don’t describe the image type; name the person instead.

## Accessibility

Avatars are not interactive. If an avatar opens a profile, wrap it in a link whose name is the person's name.
- Photo: alt is the person's name, or alt="" when the name is visible beside it.
- Initials/icon alone: the container gets role="img" and aria-label with the full name; the letters are aria-hidden (otherwise "I O" is read).
- Status: the dot is decorative; status is in visible text (or .sr-only text in the name). Each status also has a distinct shape for color-blind users.
- Contrast: initials use contrast-checked pairs ( text.default / bg.subtle , selected.fg / selected.bg , feedback.info.fg / feedback.info.bg ).
- Forced colors: border and status dot render in CanvasText .

## Tokens

Custom property | Purpose
--size-control-sm | -md | -lg | Avatar sizes
--color-bg-subtle / --color-text-default | Neutral initials
--color-selected-bg | -fg | Teal initials
--color-feedback-info-bg | -fg | -border | Blue initials
--color-feedback-success-icon | -danger-icon | -warning-icon | Status dot fills
--color-bg-surface | Ring that separates the dot from the photo
--radius-full | Circle shape
