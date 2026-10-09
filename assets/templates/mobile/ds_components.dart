// @HEAD
// Core components, tokens only (flutter/widgets + CircularProgressIndicator). Build the rest from dist/mobile/spec.json.
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart' show CircularProgressIndicator, Colors;
import 'package:flutter/widgets.dart';

import 'ds_theme.dart';

enum DsButtonVariant { primary, secondary, ghost, danger }

enum DsControlSize { sm, md, lg }

enum DsTone { neutral, info, success, warning, danger }

/// Golden tests set expandTapTargets = false so layout matches the web box.
class DsConfig {
  DsConfig._();
  static bool expandTapTargets = true;
  static double get minTapTarget => defaultTargetPlatform == TargetPlatform.iOS ? DsDimension.sizeTouchTarget : DsDimension.androidTouchTarget;
}

Widget _tapTarget(Widget child) => DsConfig.expandTapTargets
    ? ConstrainedBox(
        constraints: BoxConstraints(minHeight: DsConfig.minTapTarget, minWidth: DsConfig.minTapTarget),
        child: Center(widthFactor: 1, heightFactor: 1, child: child),
      )
    : child;

List<Widget> _spaced(List<Widget> children, double gap) => [
      for (var i = 0; i < children.length; i++) ...[if (i > 0) SizedBox(width: gap, height: gap), children[i]],
    ];

({Color bg, Color fg, Color border, Color icon}) _tone(DsColors c, DsTone tone) => switch (tone) {
      DsTone.neutral => (bg: @C(bg.muted|badge), fg: @C(text.default|badge), border: @C(border.default), icon: @C(text.muted)),
      DsTone.info => (bg: @C(feedback.info.bg|alert), fg: @C(feedback.info.fg), border: @C(feedback.info.border|alert), icon: @C(feedback.info.icon)),
      DsTone.success => (bg: @C(feedback.success.bg), fg: @C(feedback.success.fg), border: @C(feedback.success.border), icon: @C(feedback.success.icon)),
      DsTone.warning => (bg: @C(feedback.warning.bg), fg: @C(feedback.warning.fg), border: @C(feedback.warning.border), icon: @C(feedback.warning.icon)),
      DsTone.danger => (bg: @C(feedback.danger.bg), fg: @C(feedback.danger.fg), border: @C(feedback.danger.border), icon: @C(feedback.danger.icon)),
    };

/// Button — web: components/button.html. Pressed replaces hover.
class DsButton extends StatefulWidget {
  const DsButton(this.label, {super.key, required this.onPressed, this.variant = DsButtonVariant.primary, this.size = DsControlSize.md, this.loading = false});

  final String label;
  final VoidCallback? onPressed;
  final DsButtonVariant variant;
  final DsControlSize size;
  final bool loading;

  @override
  State<DsButton> createState() => _DsButtonState();
}

class _DsButtonState extends State<DsButton> {
  bool _pressed = false;

  void _press(bool v) => setState(() => _pressed = v);

  @override
  Widget build(BuildContext context) {
    final c = DsTheme.of(context);
    final enabled = widget.onPressed != null && !widget.loading;
    final p = _pressed;
    final (Color bg, Color fg, Color border) = switch (widget.variant) {
      DsButtonVariant.primary => (p ? @C(action.primary.bg-active) : @C(action.primary.bg), @C(action.primary.fg|button), Colors.transparent),
      DsButtonVariant.secondary => (p ? @C(action.secondary.bg-active) : @C(action.secondary.bg), @C(action.secondary.fg), @C(action.secondary.border)),
      DsButtonVariant.ghost => (p ? @C(action.ghost.bg-active) : @C(action.ghost.bg), @C(action.ghost.fg), Colors.transparent),
      DsButtonVariant.danger => (p ? @C(action.danger.bg-active) : @C(action.danger.bg), @C(action.danger.fg), Colors.transparent),
    };
    final double h = switch (widget.size) {
      DsControlSize.sm => @D(button.heightSm),
      DsControlSize.md => @D(button.height),
      DsControlSize.lg => @D(button.heightLg),
    };
    final box = Container(
      constraints: BoxConstraints(minHeight: h, minWidth: h),
      padding: EdgeInsets.symmetric(horizontal: @D(button.paddingX)),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(@D(button.radius)), border: Border.all(color: border, width: @D(button.borderWidth))),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        mainAxisAlignment: MainAxisAlignment.center,
        children: _spaced([
          if (widget.loading)
            SizedBox.square(dimension: DsDimension.iconSizeSm, child: CircularProgressIndicator(strokeWidth: DsDimension.iconStroke, color: fg)),
          Text(widget.label, maxLines: 1, style: @T(body).copyWith(color: fg, fontSize: @D(button.fontSize), fontWeight: @W(button.fontWeight), height: 1.2)),
        ], @D(button.gap)),
      ),
    );
    return Semantics(
      button: true,
      enabled: enabled,
      child: Opacity(
        opacity: widget.onPressed == null ? DsOpacity.disabled : 1,
        child: GestureDetector(
          behavior: HitTestBehavior.opaque,
          onTapDown: enabled ? (_) => _press(true) : null,
          onTapUp: enabled ? (_) => _press(false) : null,
          onTapCancel: enabled ? () => _press(false) : null,
          onTap: enabled ? widget.onPressed : null,
          child: _tapTarget(box),
        ),
      ),
    );
  }
}

/// Text field — label above, hint or error below; the error is text, not color alone.
class DsTextField extends StatefulWidget {
  const DsTextField({super.key, required this.label, this.controller, this.hint, this.error, this.enabled = true, this.onChanged});

  final String label;
  final TextEditingController? controller;
  final String? hint;
  final String? error;
  final bool enabled;
  final ValueChanged<String>? onChanged;

  @override
  State<DsTextField> createState() => _DsTextFieldState();
}

class _DsTextFieldState extends State<DsTextField> {
  final _focus = FocusNode();
  late final TextEditingController _controller = widget.controller ?? TextEditingController();

  @override
  void initState() {
    super.initState();
    _focus.addListener(() => setState(() {}));
  }

  @override
  void dispose() {
    _focus.dispose();
    if (widget.controller == null) _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final c = DsTheme.of(context);
    final focused = _focus.hasFocus;
    final error = widget.error;
    final borderColor = error != null ? @C(border.invalid) : focused ? @C(border.focus) : @C(input.border|text-field);
    final double bw = focused || error != null ? @D(text-field.borderWidth) * 2 : @D(text-field.borderWidth);
    final hint = error ?? widget.hint;
    return Opacity(
      opacity: widget.enabled ? 1 : DsOpacity.disabled,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: _spaced([
          Text(widget.label, style: @T(small).copyWith(color: @C(text.default))),
          Semantics(
            label: widget.label,
            hint: hint,
            textField: true,
            child: Container(
              constraints: BoxConstraints(minHeight: @D(text-field.height)),
              padding: EdgeInsets.symmetric(horizontal: @D(text-field.paddingX)),
              alignment: Alignment.centerLeft,
              decoration: BoxDecoration(
                color: @C(input.bg|text-field),
                borderRadius: BorderRadius.circular(@D(text-field.radius)),
                border: Border.all(color: borderColor, width: bw),
              ),
              child: EditableText(
                controller: _controller,
                focusNode: _focus,
                readOnly: !widget.enabled,
                style: @T(body).copyWith(color: @C(text.default), fontSize: @D(text-field.fontSize)),
                cursorColor: @C(text.default),
                backgroundCursorColor: @C(text.muted),
                onChanged: widget.onChanged,
              ),
            ),
          ),
          if (hint != null) Text(hint, style: @T(small).copyWith(color: error != null ? @C(feedback.danger.fg) : @C(text.muted))),
        ], @D(text-field.gap)),
      ),
    );
  }
}

class _MarkPainter extends CustomPainter {
  _MarkPainter(this.color, {this.cross = false});

  final Color color;
  final bool cross;

  @override
  void paint(Canvas canvas, Size size) {
    final path = Path();
    if (cross) {
      path
        ..moveTo(0, 0)
        ..lineTo(size.width, size.height)
        ..moveTo(size.width, 0)
        ..lineTo(0, size.height);
    } else {
      path
        ..moveTo(0, size.height / 2)
        ..lineTo(size.width * 0.38, size.height * 0.88)
        ..lineTo(size.width, size.height * 0.12);
    }
    canvas.drawPath(
      path,
      Paint()
        ..color = color
        ..style = PaintingStyle.stroke
        ..strokeWidth = DsDimension.iconStroke
        ..strokeCap = StrokeCap.round
        ..strokeJoin = StrokeJoin.round,
    );
  }

  @override
  bool shouldRepaint(_MarkPainter oldDelegate) => oldDelegate.color != color || oldDelegate.cross != cross;
}

class DsCheckbox extends StatelessWidget {
  const DsCheckbox({super.key, required this.value, required this.onChanged, required this.label});

  final bool value;
  final ValueChanged<bool>? onChanged;
  final String label;

  @override
  Widget build(BuildContext context) {
    final c = DsTheme.of(context);
    final enabled = onChanged != null;
    final double s = @D(checkbox.size);
    return Semantics(
      checked: value,
      enabled: enabled,
      label: label,
      excludeSemantics: true,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: enabled ? () => onChanged!(!value) : null,
        child: Opacity(
          opacity: enabled ? 1 : DsOpacity.disabled,
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: @D(checkbox.rowHeight)),
            child: Row(mainAxisSize: MainAxisSize.min, children: _spaced([
              Container(
                width: s,
                height: s,
                decoration: BoxDecoration(
                  color: value ? @C(action.primary.bg) : @C(input.bg),
                  borderRadius: BorderRadius.circular(@D(checkbox.radius)),
                  border: Border.all(color: value ? @C(action.primary.bg) : @C(input.border|checkbox), width: @D(checkbox.borderWidth)),
                ),
                child: value ? Padding(padding: EdgeInsets.all(s * 0.22), child: CustomPaint(painter: _MarkPainter(@C(action.primary.fg)))) : null,
              ),
              Flexible(child: Text(label, style: @T(body).copyWith(color: @C(text.default)))),
            ], @D(checkbox.gap))),
          ),
        ),
      ),
    );
  }
}

/// Switch — web geometry, not the Material/Cupertino control.
class DsSwitch extends StatelessWidget {
  const DsSwitch({super.key, required this.value, required this.onChanged, required this.label});

  final bool value;
  final ValueChanged<bool>? onChanged;
  final String label;

  @override
  Widget build(BuildContext context) {
    final c = DsTheme.of(context);
    final enabled = onChanged != null;
    final double inset = @D(switch.inset);
    final double knob = @D(switch.height) - 2 * inset;
    final reduce = MediaQuery.maybeDisableAnimationsOf(context) ?? false;
    return Semantics(
      toggled: value,
      enabled: enabled,
      label: label,
      excludeSemantics: true,
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTap: enabled ? () => onChanged!(!value) : null,
        child: Opacity(
          opacity: enabled ? 1 : DsOpacity.disabled,
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: @D(switch.rowHeight)),
            child: Row(mainAxisSize: MainAxisSize.min, children: _spaced([
              Container(
                width: @D(switch.width),
                height: @D(switch.height),
                padding: EdgeInsets.all(inset),
                decoration: BoxDecoration(color: value ? @C(action.primary.bg) : @C(input.border), borderRadius: BorderRadius.circular(@D(switch.radius))),
                child: AnimatedAlign(
                  alignment: value ? Alignment.centerRight : Alignment.centerLeft,
                  duration: reduce ? Duration.zero : DsMotion.durationFast,
                  curve: DsMotion.easingStandard,
                  child: Container(width: knob, height: knob, decoration: BoxDecoration(color: @C(bg.surface), shape: BoxShape.circle)),
                ),
              ),
              Flexible(child: Text(label, style: @T(body).copyWith(color: @C(text.default)))),
            ], @D(switch.gap))),
          ),
        ),
      ),
    );
  }
}

class DsCard extends StatelessWidget {
  const DsCard({super.key, required this.children});

  final List<Widget> children;

  @override
  Widget build(BuildContext context) {
    final c = DsTheme.of(context);
    return Container(
      width: double.infinity,
      padding: EdgeInsets.all(@D(card.padding)),
      decoration: BoxDecoration(
        color: @C(surface.raised|card),
        borderRadius: BorderRadius.circular(@D(card.radius)),
        border: Border.all(color: @C(border.default), width: @D(card.borderWidth)),
        boxShadow: @E(card.shadow|elevation.raised|shadow.sm),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, mainAxisSize: MainAxisSize.min, children: _spaced(children, @D(card.gap))),
    );
  }
}

class DsBadge extends StatelessWidget {
  const DsBadge(this.text, {super.key, this.tone = DsTone.neutral});

  final String text;
  final DsTone tone;

  @override
  Widget build(BuildContext context) {
    final t = _tone(DsTheme.of(context), tone);
    return Container(
      constraints: BoxConstraints(minHeight: @D(badge.height)),
      padding: EdgeInsets.symmetric(horizontal: @D(badge.paddingX)),
      alignment: Alignment.center,
      decoration: BoxDecoration(color: t.bg, borderRadius: BorderRadius.circular(@D(badge.radius))),
      child: Text(text, maxLines: 1, style: @T(body).copyWith(color: t.fg, fontSize: @D(badge.fontSize), fontWeight: @W(badge.fontWeight), height: 1.2)),
    );
  }
}

/// Alert — role is conveyed by text and icon, never color alone.
class DsAlert extends StatelessWidget {
  const DsAlert(this.title, {super.key, this.message, this.tone = DsTone.info, this.icon});

  final String title;
  final String? message;
  final DsTone tone;
  final Widget? icon;

  @override
  Widget build(BuildContext context) {
    final t = _tone(DsTheme.of(context), tone);
    return Semantics(
      container: true,
      child: Container(
        width: double.infinity,
        padding: EdgeInsets.all(@D(alert.padding)),
        decoration: BoxDecoration(color: t.bg, borderRadius: BorderRadius.circular(@D(alert.radius)), border: Border.all(color: t.border, width: @D(alert.borderWidth))),
        child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: _spaced([
          if (icon != null) IconTheme(data: IconThemeData(color: t.icon, size: @D(alert.iconSize)), child: ExcludeSemantics(child: icon!)),
          Expanded(
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: _spaced([
              Text(title, style: @T(body).copyWith(color: t.fg, fontWeight: @W(button.fontWeight))),
              if (message != null) Text(message!, style: @T(small).copyWith(color: t.fg)),
            ], DsDimension.space1)),
          ),
        ], @D(alert.gap))),
      ),
    );
  }
}

class DsAvatar extends StatelessWidget {
  const DsAvatar(this.name, {super.key, this.size = @D(avatar.size)});

  final String name;
  final double size;

  String get _initials => name.length <= 3
      ? name.toUpperCase()
      : name.split(' ').where((p) => p.isNotEmpty).take(2).map((p) => p[0]).join().toUpperCase();

  @override
  Widget build(BuildContext context) {
    final c = DsTheme.of(context);
    return Semantics(
      label: name,
      excludeSemantics: true,
      child: Container(
        width: size,
        height: size,
        alignment: Alignment.center,
        decoration: BoxDecoration(color: @C(bg.muted|avatar), borderRadius: BorderRadius.circular(@D(avatar.radius) < size / 2 ? @D(avatar.radius) : size / 2)),
        child: Text(_initials, style: @T(body).copyWith(color: @C(text.default), fontSize: @D(avatar.fontSize) * size / @D(avatar.size), fontWeight: @W(button.fontWeight))),
      ),
    );
  }
}

class DsTag extends StatelessWidget {
  const DsTag(this.text, {super.key, this.onRemove});

  final String text;
  final VoidCallback? onRemove;

  @override
  Widget build(BuildContext context) {
    final c = DsTheme.of(context);
    return Container(
      constraints: BoxConstraints(minHeight: @D(tag.height)),
      padding: EdgeInsets.symmetric(horizontal: @D(tag.paddingX)),
      decoration: BoxDecoration(
        color: @C(bg.muted),
        borderRadius: BorderRadius.circular(@D(tag.radius)),
        border: Border.all(color: @C(border.default|tag), width: @D(tag.borderWidth)),
      ),
      child: Row(mainAxisSize: MainAxisSize.min, children: _spaced([
        Text(text, maxLines: 1, style: @T(body).copyWith(color: @C(text.default), fontSize: @D(tag.fontSize))),
        if (onRemove != null)
          Semantics(
            button: true,
            label: 'Remove $text',
            child: GestureDetector(
              behavior: HitTestBehavior.opaque,
              onTap: onRemove,
              child: _tapTarget(SizedBox.square(
                dimension: DsDimension.iconSizeSm,
                child: Padding(padding: EdgeInsets.all(DsDimension.space1), child: CustomPaint(painter: _MarkPainter(@C(text.default), cross: true))),
              )),
            ),
          ),
      ], @D(tag.gap))),
    );
  }
}

class DsDivider extends StatelessWidget {
  const DsDivider({super.key});

  @override
  Widget build(BuildContext context) {
    final c = DsTheme.of(context);
    return ExcludeSemantics(child: Container(height: @D(divider.thickness), color: @C(border.default|divider)));
  }
}
