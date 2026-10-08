# Form controls & inputs — specs

Files: `form-field` (label, form-field, fieldset), `text-field` (text-field, input-group), `textarea`, `password-input`, `search-input`, `number-input`, `checkbox`, `radio`, `switch`, `select`, `combobox`, `listbox`, `transfer-list`, `file-upload`, `slider`, `date-picker` (date-picker, calendar, date-range-picker), `time-picker`, `color-picker`, `otp-input`, `tag-input`, `rating`, `rich-text-editor`, `inline-edit`, `error-summary`.

Build `form-field` first — every control below is rendered inside it.

## form-field (label, wrapper, fieldset)
- Structure: `label[for]` → control → helper text (`id`, referenced by `aria-describedby`) → error message (`id`, added to `aria-describedby`, prefixed with an icon + "Error:" visually hidden). Character counter announced politely after typing pauses.
- Required: mark **optional** fields in long forms, or required with `*` + legend explaining it; set `required` attribute (not just `aria-required`).
- Horizontal variant (label beside control) only ≥ md breakpoint.
- `fieldset/legend` groups radios, checkboxes, date parts, address blocks.

## text-field & input-group
- Correct `type` + `inputmode` + `autocomplete` (email, tel, url, one-time-code, street-address…) — that's half of mobile usability.
- Visual: 1px `--input-border` (≥3:1), radius token, height = control size; focus = focus ring (not just border color change).
- States: placeholder is never a label; filled; disabled (muted, not focusable); read-only (focusable, no border emphasis, copyable); invalid via `aria-invalid="true"` + `:user-invalid` styling (only after interaction).
- Prefix/suffix (currency, units, icons) inside the border; addon buttons (e.g. "Apply") attached. Prefix text must be part of the label or `aria-describedby`.

## textarea
- Auto-grow via `field-sizing: content` (with min/max rows) where supported; resize vertical only. Counter shows remaining, turns invalid past limit but doesn't block typing.

## password-input
- Reveal toggle: `<button type="button" aria-pressed aria-controls>` "Show password", switches `type`. `autocomplete="current-password"|"new-password"`. Strength meter uses `<meter>` + text (never color only); requirements list updates live (polite).

## search-input
- Wrap in `<search>` (or `role="search"`); `type="search"`, clear button (`aria-label="Clear search"`) visible when filled, returns focus to input. Loading spinner inside; optional shortcut hint (`/` or ⌘K) as `kbd`.

## number-input
- `input type="number"` baseline or `type="text" inputmode="decimal"` + custom steppers (better for formatted values). Steppers are `tabindex="-1"` buttons (keyboard uses ↑/↓). min/max states disable the respective stepper. Locale formatting via `Intl.NumberFormat` on blur.

## checkbox & checkbox-group
- Native `input type=checkbox` restyled with `appearance:none` (keep it the real element, not a div). Checkmark via SVG/`clip-path`; indeterminate via `.indeterminate = true` (JS-only state) for "select all".
- Hit area includes the label. Group = fieldset + legend; group-level error message.

## radio & radio-group
- Native radios, `appearance:none`. Group arrow keys are native. Card variant: whole card is the label, selected card uses `selected.*` tokens + border.

## switch
- `<input type="checkbox" role="switch">` — immediate effect (no Save button); label states what's on ("Email notifications"), not "On/Off". If the effect is async, show spinner and revert on failure.

## select
- Native `<select>` styled (custom chevron via background SVG using currentColor mask). Progressive: `appearance: base-select` for customizable select in supporting browsers. `optgroup` demo. Use combobox when > ~15 options or search is needed.

## combobox (autocomplete)
- APG combobox with listbox popup: `input role="combobox" aria-expanded aria-controls aria-activedescendant aria-autocomplete="list"`; options `role="option" aria-selected`. ↓ opens, ↑/↓ move, Enter selects, Esc clears/closes. States: loading (status message), no results ("No matches for 'x'"), multi-select variant renders chips (see tag-input). Debounce async queries; announce result count politely.

## listbox (enterprise)
- `role="listbox"` (`aria-multiselectable` for multi), options with `aria-selected`; single Tab stop, arrows move, Space toggles in multi, Shift+arrow range.

## transfer-list (enterprise)
- Two listboxes + move buttons (→, ←, all). Every drag interaction has a button equivalent. Counts in headings; search filter per side.

## file-upload
- Real `<input type="file">` (visible button label "Choose files") + dropzone that's a `<label>` for it. Drag-over state; per-file rows with name, size, progress (`<progress>`), remove button, error (type/size) message. State changes announced. `accept` and size limits shown in helper text.

## slider
- `input type="range"` styled (track, filled portion via `--value` custom prop, thumb ≥ 24px). Show value (`<output>`); ticks via `<datalist>`. Range (two thumbs) = two inputs overlapped or APG multithumb with `aria-valuetext`.

## date-picker, calendar, date-range-picker
- Baseline: `input type="date"`. Custom: text input (with format hint, parse typed dates) + button opening a `dialog` containing an APG date-grid (`role="grid"`, arrows by day, PageUp/Down by month, Home/End week). Today marked (not only color), selected, disabled dates (`aria-disabled`), invalid typed value message.
- Range picker: two months side by side (stacked on mobile), presets list ("Last 7 days"), in-range styling, start/end labels. Locale-aware first day of week via `Intl`.

## time-picker
- `input type="time"` baseline; custom = segmented hour/minute spinbuttons or a listbox of slots (15/30 min). 12h/24h by locale, AM/PM segment. Timezone shown when relevant.

## color-picker (enterprise)
- `input type="color"` + swatch grid (radio group of swatches with names) + hex text input with validation; contrast hint optional.

## otp-input
- One `<input autocomplete="one-time-code" inputmode="numeric">` visually split into cells (via letter-spacing or overlaid boxes) is the most robust (paste + SMS autofill work). If using separate inputs: group with label, auto-advance, backspace moves back, paste fills all.

## tag-input (enterprise)
- Input + chip list; Enter/comma creates a tag, Backspace on empty input focuses/removes last chip; each chip has a remove button labeled "Remove <tag>"; suggestions via combobox. Max count + duplicate validation.

## rating (enterprise)
- Input: radio group of stars (each labeled "3 out of 5 stars"), half-star optional. Read-only display: `role="img" aria-label="Rated 4.5 out of 5"`.

## rich-text-editor (enterprise)
- Ship the **shell**: toolbar (per toolbar spec, toggle buttons with `aria-pressed`), `contenteditable` region with `role="textbox" aria-multiline="true"` + label, focus ring, disabled/read-only, character count, and `.prose` styling for content. Recommend an engine (Tiptap/ProseMirror, Lexical) in docs rather than hand-rolling editing behavior.

## inline-edit (enterprise)
- Read mode is a `<button>` showing the value ("Edit name: Acme"); Enter → input with Save/Cancel; Esc cancels and returns focus; saving and error states inline.

## error-summary
- On submit with errors: `role="alert"` (or focus the summary with `tabindex="-1"`) at the top of the form, heading "There is a problem", list of links to each invalid field (`href="#field-id"`). Prefix the page `<title>` with "Error: ". From GOV.UK — the single most impactful form pattern.

## composer (enterprise)
- `<form>` with a labelled auto-growing `<textarea>` (`field-sizing: content`, max height then scroll), attachment button (real `input[type=file]`) with removable previews, character counter (polite), send button (`type=submit`, disabled only while sending — show `aria-busy` + inline spinner). Enter inserts newline; Ctrl/Cmd+Enter sends (document it). Failed send keeps the text and shows an inline error with retry.
