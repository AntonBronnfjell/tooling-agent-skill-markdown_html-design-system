# Pagination

Category: Navigation · page `components/pagination.html` · CSS `css/components/pagination.css`

| Component | Tier | Status | Required demos |
|---|---|---|---|
| `pagination` — Pagination | core | ready · stable | state:first state:middle state:last variant:compact variant:page-size |

## Usage

Use pagination for long, stable lists people navigate by position: the work-order table, the vehicle register, audit logs. For feeds and activity streams use a "Show 20 more" button; for short lists show everything.
- Always show first and last page, the current page and its neighbours; collapse the rest into "…".
- Labels: "Previous" / "Next", "Page 3 of 12", "Rows per page", "Showing 21–40 of 312 work orders" — name the thing being counted.
- Keep the page in the URL ( ?page=8 ) so links and the back button work.

## Anatomy

- Landmark — nav.pagination[aria-label] naming the list
- Previous / Next — .pagination__link--step (plain text when unavailable)
- Page links — a.pagination__link with hidden "Page "
- Ellipsis — .pagination__ellipsis
- Current page — aria-current="page" : fill, border, bold
- Table footer (optional) — .pagination__bar with page size and range

## Examples

### pagination · state:first

```html
<nav class="pagination" aria-label="Pagination, work orders (first page example)"><ul class="pagination__list"><li><span class="pagination__link pagination__link--step" aria-disabled="true"><svg class="pagination__icon" aria-hidden="true" focusable="false"><use href="#icon-chevron-left"></use></svg>Previous</span></li><li><a class="pagination__link" href="#page-1" aria-current="page"><span class="sr-only">Page </span>1</a></li><li><a class="pagination__link" href="#page-2"><span class="sr-only">Page </span>2</a></li><li><a class="pagination__link" href="#page-3"><span class="sr-only">Page </span>3</a></li><li><span class="pagination__ellipsis">…</span></li><li><a class="pagination__link" href="#page-16"><span class="sr-only">Page </span>16</a></li><li><a class="pagination__link pagination__link--step" href="#page-2" rel="next">Next<svg class="pagination__icon" aria-hidden="true" focusable="false"><use href="#icon-chevron-right"></use></svg></a></li></ul></nav>
            <p>First page: "Previous" is plain text, not a link.</p>
```

### pagination · state:middle

```html
<nav class="pagination" aria-label="Pagination, work orders (middle page example)"><ul class="pagination__list"><li><a class="pagination__link pagination__link--step" href="#page-7" rel="prev"><svg class="pagination__icon" aria-hidden="true" focusable="false"><use href="#icon-chevron-left"></use></svg>Previous</a></li><li><a class="pagination__link" href="#page-1"><span class="sr-only">Page </span>1</a></li><li><span class="pagination__ellipsis">…</span></li><li><a class="pagination__link" href="#page-7"><span class="sr-only">Page </span>7</a></li><li><a class="pagination__link" href="#page-8" aria-current="page"><span class="sr-only">Page </span>8</a></li><li><a class="pagination__link" href="#page-9"><span class="sr-only">Page </span>9</a></li><li><span class="pagination__ellipsis">…</span></li><li><a class="pagination__link" href="#page-16"><span class="sr-only">Page </span>16</a></li><li><a class="pagination__link pagination__link--step" href="#page-9" rel="next">Next<svg class="pagination__icon" aria-hidden="true" focusable="false"><use href="#icon-chevron-right"></use></svg></a></li></ul></nav>
```

### pagination · state:last

```html
<nav class="pagination" aria-label="Pagination, work orders (last page example)"><ul class="pagination__list"><li><a class="pagination__link pagination__link--step" href="#page-15" rel="prev"><svg class="pagination__icon" aria-hidden="true" focusable="false"><use href="#icon-chevron-left"></use></svg>Previous</a></li><li><a class="pagination__link" href="#page-1"><span class="sr-only">Page </span>1</a></li><li><span class="pagination__ellipsis">…</span></li><li><a class="pagination__link" href="#page-14"><span class="sr-only">Page </span>14</a></li><li><a class="pagination__link" href="#page-15"><span class="sr-only">Page </span>15</a></li><li><a class="pagination__link" href="#page-16" aria-current="page"><span class="sr-only">Page </span>16</a></li><li><span class="pagination__link pagination__link--step" aria-disabled="true">Next<svg class="pagination__icon" aria-hidden="true" focusable="false"><use href="#icon-chevron-right"></use></svg></span></li></ul></nav>
```

### pagination · variant:compact

```html
<nav class="pagination pagination--compact" aria-label="Pagination, inspections"><ul class="pagination__list"><li><a class="pagination__link" href="#page-2" rel="prev" aria-label="Previous page"><svg class="pagination__icon" aria-hidden="true" focusable="false"><use href="#icon-chevron-left"></use></svg></a></li><li><span class="pagination__status">Page 3 of 12</span></li><li><a class="pagination__link" href="#page-4" rel="next" aria-label="Next page"><svg class="pagination__icon" aria-hidden="true" focusable="false"><use href="#icon-chevron-right"></use></svg></a></li></ul></nav>
            <p>Phones and narrow panels.</p>
```

### pagination · variant:page-size

```html
<div class="pagination__bar"><div class="pagination__size"><label for="pg-size">Rows per page</label><select class="pagination__select" id="pg-size" name="per_page"><option>10</option><option selected>20</option><option>50</option><option>100</option></select></div><p class="pagination__range" role="status">Showing 21–40 of 312 work orders</p><nav class="pagination" aria-label="Pagination, work orders table"><ul class="pagination__list"><li><a class="pagination__link pagination__link--step" href="#page-1" rel="prev"><svg class="pagination__icon" aria-hidden="true" focusable="false"><use href="#icon-chevron-left"></use></svg>Previous</a></li><li><a class="pagination__link" href="#page-1"><span class="sr-only">Page </span>1</a></li><li><a class="pagination__link" href="#page-2" aria-current="page"><span class="sr-only">Page </span>2</a></li><li><a class="pagination__link" href="#page-3"><span class="sr-only">Page </span>3</a></li><li><span class="pagination__ellipsis">…</span></li><li><a class="pagination__link" href="#page-16"><span class="sr-only">Page </span>16</a></li><li><a class="pagination__link pagination__link--step" href="#page-3" rel="next">Next<svg class="pagination__icon" aria-hidden="true" focusable="false"><use href="#icon-chevron-right"></use></svg></a></li></ul></nav></div>
            <p>Data tables: page size, range and pages in one footer row. The range is a polite live region.</p>
```

### pagination · state:hover state:focus-visible

```html
<nav class="pagination" aria-label="Pagination states example"><ul class="pagination__list"><li><a class="pagination__link is-hover" href="#page-4"><span class="sr-only">Page </span>4</a></li><li><a class="pagination__link is-focus-visible" href="#page-5"><span class="sr-only">Page </span>5</a></li></ul></nav>
```

## API

Hook | Values | Purpose
.pagination | block class | <nav>
.pagination--compact | modifier | Prev / "Page 3 of 12" / Next
.pagination__list | __link | __link--step | __ellipsis | __icon | __status | parts | Pager
.pagination__bar | __size | __select | __range | parts | Data-table footer
aria-current="page" | attribute | Current page
aria-disabled="true" on a span | attribute | Unavailable Previous / Next

## Do and don't

"Showing 21–40 of 312 work orders"
Do say what is counted and where the reader is.
<a href="#" class="pagination__link" aria-disabled="true">Previous</a>
Don't leave a dead link on the first page — render text instead.

## Accessibility

Keyboard interaction
Key | Behavior
Tab | Moves through the page links (unavailable Previous/Next are skipped)
Enter | Opens that page
- Each <nav> has a unique name ("Pagination, work orders") when several lists share a page.
- Page links read "Page 8, current page" thanks to the hidden prefix and aria-current .
- After a page change, move focus to the table caption or heading and update the range text ( role="status" ).
- Targets are 40px; icon-only compact links have aria-label . Arrow icons mirror in RTL.

## Tokens

Custom property | Purpose
--size-control-md | Link size
--color-selected-bg | -fg | -border | Current page
--color-action-ghost-bg-hover | Hover
--color-text-disabled | Unavailable step
--input-bg | -border | -radius | Page-size select
--color-text-muted | Ellipsis, range
