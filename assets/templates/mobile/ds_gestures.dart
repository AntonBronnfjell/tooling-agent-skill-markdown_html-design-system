// @HEAD
// Mobile scope: gesture components on the platform built-ins, styled with tokens. Web spec: references/components/mobile.md.
// Every gesture also has a non-drag path: long press + semantics actions for rows, buttons for sheets, pages and zoom.
// No wrapper needed: collapsing-app-bar = CustomScrollView + SliverAppBar(pinned: true, expandedHeight: ...).
import 'package:flutter/material.dart' show RefreshIndicator, showModalBottomSheet;
import 'package:flutter/semantics.dart' show CustomSemanticsAction;
import 'package:flutter/widgets.dart';

import 'ds_components.dart';
import 'ds_theme.dart';

/// One action of a swipe row or an action sheet.
class DsAction {
  const DsAction(this.label, this.onPressed, {this.destructive = false});

  final String label;
  final VoidCallback onPressed;
  final bool destructive;
}

/// swipe-actions — web: components/swipe-actions.html. Swipe end→start runs the first trailing action, start→end the
/// leading one; the row snaps back (the app removes it and offers Undo if the action deletes). Long press opens every
/// action in an action sheet, and they are semantics actions too.
class DsSwipeActions extends StatelessWidget {
  const DsSwipeActions({super.key, required this.trailing, this.leading, required this.child});

  final List<DsAction> trailing;
  final DsAction? leading;
  final Widget child;

  Widget _background(BuildContext context, DsAction? a, AlignmentGeometry alignment) {
    final c = DsTheme.of(context);
    if (a == null) return const SizedBox.shrink();
    return Container(
      color: a.destructive ? @C(action.danger.bg) : @C(action.primary.bg),
      alignment: alignment,
      padding: EdgeInsets.symmetric(horizontal: DsDimension.space1 * 4),
      child: Text(a.label, style: @T(body).copyWith(color: a.destructive ? @C(action.danger.fg) : @C(action.primary.fg))),
    );
  }

  @override
  Widget build(BuildContext context) {
    final all = [if (leading != null) leading!, ...trailing];
    return Semantics(
      customSemanticsActions: {for (final a in all) CustomSemanticsAction(label: a.label): a.onPressed},
      child: Dismissible(
        key: ObjectKey(child),
        direction: leading == null
            ? DismissDirection.endToStart
            : trailing.isEmpty
                ? DismissDirection.startToEnd
                : DismissDirection.horizontal,
        background: _background(context, leading, AlignmentDirectional.centerStart),
        secondaryBackground: _background(context, trailing.isEmpty ? null : trailing.first, AlignmentDirectional.centerEnd),
        confirmDismiss: (direction) async {
          (direction == DismissDirection.startToEnd ? leading : trailing.first)?.onPressed();
          return false;
        },
        child: GestureDetector(onLongPress: () => showDsActionSheet(context, actions: all), child: child),
      ),
    );
  }
}

/// pull-to-refresh — web: components/pull-to-refresh.html. Also offer a Refresh button in the app bar.
class DsRefresh extends StatelessWidget {
  const DsRefresh({super.key, required this.onRefresh, required this.child});

  final Future<void> Function() onRefresh;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final c = DsTheme.of(context);
    return RefreshIndicator(onRefresh: onRefresh, color: @C(action.primary.bg), backgroundColor: @C(surface.raised|card), child: child);
  }
}

ShapeBorder _sheetShape() => RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(@D(card.radius))));

/// action-sheet — web: components/action-sheet.html. Cancel is added; nothing destructive is pre-selected.
Future<void> showDsActionSheet(BuildContext context, {String? title, required List<DsAction> actions}) {
  final c = DsTheme.of(context);
  return showModalBottomSheet<void>(
    context: context,
    backgroundColor: @C(surface.raised|card),
    showDragHandle: true,
    shape: _sheetShape(),
    builder: (sheet) => SafeArea(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (title != null)
            Padding(
              padding: EdgeInsets.symmetric(horizontal: DsDimension.space1 * 4),
              child: Text(title, style: @T(small).copyWith(color: @C(text.muted))),
            ),
          for (final a in [...actions, DsAction('Cancel', () {})])
            Semantics(
              button: true,
              child: GestureDetector(
                behavior: HitTestBehavior.opaque,
                onTap: () {
                  Navigator.of(sheet).pop();
                  a.onPressed();
                },
                child: ConstrainedBox(
                  constraints: BoxConstraints(minHeight: DsDimension.androidTouchTarget),
                  child: Padding(
                    padding: EdgeInsets.symmetric(horizontal: DsDimension.space1 * 4),
                    child: Align(
                      alignment: AlignmentDirectional.centerStart,
                      child: Text(a.label, style: @T(body).copyWith(color: a.destructive ? @C(feedback.danger.fg) : @C(text.default))),
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    ),
  );
}

/// detent-sheet (modal) — web: components/detent-sheet.html. Snaps to peek (size.sheet.peek), half and full; dragging
/// below peek closes it. Build the content with the given ScrollController and include a Close button.
Future<void> showDsDetentSheet(BuildContext context, {required ScrollableWidgetBuilder builder}) {
  final c = DsTheme.of(context);
  final peek = DsDimension.sizeSheetPeek / MediaQuery.sizeOf(context).height;
  return showModalBottomSheet<void>(
    context: context,
    isScrollControlled: true,
    showDragHandle: true,
    backgroundColor: @C(surface.raised|card),
    shape: _sheetShape(),
    builder: (_) => DraggableScrollableSheet(expand: false, snap: true, minChildSize: peek, initialChildSize: 0.5, snapSizes: const [0.5], builder: builder),
  );
}

/// detent-sheet (non-modal) — put it last in a Stack over the page. The handle is a button that cycles peek → half → full.
class DsDetentSheet extends StatefulWidget {
  const DsDetentSheet({super.key, required this.builder});

  final ScrollableWidgetBuilder builder;

  @override
  State<DsDetentSheet> createState() => _DsDetentSheetState();
}

class _DsDetentSheetState extends State<DsDetentSheet> {
  final _controller = DraggableScrollableController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _cycle(double peek) {
    final now = _controller.size;
    final next = now < 0.5 - 0.01 ? 0.5 : now < 1 - 0.01 ? 1.0 : peek;
    final reduce = MediaQuery.disableAnimationsOf(context);
    if (reduce) {
      _controller.jumpTo(next);
    } else {
      _controller.animateTo(next, duration: DsMotion.durationFast, curve: DsMotion.easingStandard);
    }
  }

  @override
  Widget build(BuildContext context) {
    final c = DsTheme.of(context);
    final peek = DsDimension.sizeSheetPeek / MediaQuery.sizeOf(context).height;
    return DraggableScrollableSheet(
      controller: _controller,
      snap: true,
      minChildSize: peek,
      initialChildSize: peek,
      snapSizes: const [0.5],
      builder: (context, scroll) => DecoratedBox(
        decoration: BoxDecoration(
          color: @C(surface.raised|card),
          borderRadius: BorderRadius.vertical(top: Radius.circular(@D(card.radius))),
          boxShadow: @E(card.shadow|elevation.raised|shadow.sm),
        ),
        child: Column(
          children: [
            Semantics(
              button: true,
              label: 'Resize sheet',
              child: GestureDetector(
                behavior: HitTestBehavior.opaque,
                onTap: () => _cycle(peek),
                child: SizedBox(
                  height: DsDimension.androidTouchTarget,
                  child: Center(
                    child: Container(
                      width: DsDimension.space1 * 9,
                      height: DsDimension.space1,
                      decoration: BoxDecoration(color: @C(border.default), borderRadius: BorderRadius.all(Radius.circular(DsDimension.space1))),
                    ),
                  ),
                ),
              ),
            ),
            Expanded(child: widget.builder(context, scroll)),
          ],
        ),
      ),
    );
  }
}

/// swipe-pager — web: components/swipe-pager.html. Swipe between pages; the dots are buttons ("Page 2 of 4").
class DsPager extends StatefulWidget {
  const DsPager({super.key, required this.count, required this.itemBuilder});

  final int count;
  final IndexedWidgetBuilder itemBuilder;

  @override
  State<DsPager> createState() => _DsPagerState();
}

class _DsPagerState extends State<DsPager> {
  final _controller = PageController();
  int _page = 0;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _go(int i) {
    if (MediaQuery.disableAnimationsOf(context)) {
      _controller.jumpToPage(i);
    } else {
      _controller.animateToPage(i, duration: DsMotion.durationFast, curve: DsMotion.easingStandard);
    }
  }

  @override
  Widget build(BuildContext context) {
    final c = DsTheme.of(context);
    return Column(
      children: [
        Expanded(
          child: PageView.builder(
            controller: _controller,
            itemCount: widget.count,
            onPageChanged: (i) => setState(() => _page = i),
            itemBuilder: widget.itemBuilder,
          ),
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            for (var i = 0; i < widget.count; i++)
              Semantics(
                button: true,
                selected: i == _page,
                label: 'Page ${i + 1} of ${widget.count}',
                child: GestureDetector(
                  behavior: HitTestBehavior.opaque,
                  onTap: () => _go(i),
                  child: SizedBox.square(
                    dimension: DsDimension.androidTouchTarget,
                    child: Center(
                      child: Container(
                        width: DsDimension.space1 * 2,
                        height: DsDimension.space1 * 2,
                        decoration: BoxDecoration(shape: BoxShape.circle, color: i == _page ? @C(action.primary.bg) : @C(border.default)),
                      ),
                    ),
                  ),
                ),
              ),
          ],
        ),
      ],
    );
  }
}

/// zoomable-image — web: components/zoomable-image.html. Pinch or double tap to zoom (1x–4x), drag to pan when zoomed,
/// and Zoom out / Reset / Zoom in buttons as the non-gesture path.
class DsZoomableImage extends StatefulWidget {
  const DsZoomableImage({super.key, required this.image, required this.label});

  final Widget image;
  final String label;

  @override
  State<DsZoomableImage> createState() => _DsZoomableImageState();
}

class _DsZoomableImageState extends State<DsZoomableImage> {
  final _transform = TransformationController();

  double get _scale => _transform.value.getMaxScaleOnAxis();

  void _zoom(double to) {
    final s = to.clamp(1.0, 4.0);
    setState(() => _transform.value = Matrix4.diagonal3Values(s, s, 1));
  }

  @override
  void dispose() {
    _transform.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        GestureDetector(
          onDoubleTap: () => _zoom(_scale > 1 ? 1 : 2),
          child: Semantics(
            image: true,
            label: widget.label,
            value: '${(_scale * 100).round()}%',
            child: InteractiveViewer(
              transformationController: _transform,
              minScale: 1,
              maxScale: 4,
              onInteractionEnd: (_) => setState(() {}),
              child: widget.image,
            ),
          ),
        ),
        SizedBox(height: DsDimension.space1),
        Wrap(
          spacing: DsDimension.space1,
          children: [
            DsButton('Zoom out', onPressed: _scale > 1 ? () => _zoom(_scale - 1) : null, variant: DsButtonVariant.secondary, size: DsControlSize.sm),
            DsButton('Reset zoom', onPressed: _scale > 1 ? () => _zoom(1) : null, variant: DsButtonVariant.secondary, size: DsControlSize.sm),
            DsButton('Zoom in', onPressed: _scale < 4 ? () => _zoom(_scale + 1) : null, variant: DsButtonVariant.secondary, size: DsControlSize.sm),
          ],
        ),
      ],
    );
  }
}
