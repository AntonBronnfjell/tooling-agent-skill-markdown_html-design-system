// @HEAD
// Core components, tokens only. Needs compose-foundation (+ material3 only for the loading spinner).
package @PKG

import androidx.compose.animation.core.animateDpAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.interaction.collectIsFocusedAsState
import androidx.compose.foundation.interaction.collectIsPressedAsState
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.defaultMinSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.matchParentSize
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.selection.toggleable
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicText
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ColorFilter
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.layout
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.error
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

enum class DsButtonVariant { Primary, Secondary, Ghost, Danger }
enum class DsControlSize { Sm, Md, Lg }
enum class DsTone { Neutral, Info, Success, Warning, Danger }

/** Snapshot tests provide false so layout matches the web box; apps keep the 48 dp Android touch target. */
val LocalDsTouchTarget = staticCompositionLocalOf { true }

@Composable
fun Modifier.dsTouchTarget(): Modifier {
    if (!LocalDsTouchTarget.current) return this
    return layout { measurable, constraints ->
        val min = DsDimension.androidTouchTarget.dp.roundToPx()
        val p = measurable.measure(constraints)
        val w = maxOf(p.width, min)
        val h = maxOf(p.height, min)
        layout(w, h) { p.place((w - p.width) / 2, (h - p.height) / 2) }
    }
}

internal data class DsToneColors(val bg: Color, val fg: Color, val border: Color, val icon: Color)

@Composable
internal fun dsTone(tone: DsTone): DsToneColors = when (tone) {
    DsTone.Neutral -> DsToneColors(@C(bg.muted|badge), @C(text.default|badge), @C(border.default), @C(text.muted))
    DsTone.Info -> DsToneColors(@C(feedback.info.bg|alert), @C(feedback.info.fg), @C(feedback.info.border|alert), @C(feedback.info.icon))
    DsTone.Success -> DsToneColors(@C(feedback.success.bg), @C(feedback.success.fg), @C(feedback.success.border), @C(feedback.success.icon))
    DsTone.Warning -> DsToneColors(@C(feedback.warning.bg), @C(feedback.warning.fg), @C(feedback.warning.border), @C(feedback.warning.icon))
    DsTone.Danger -> DsToneColors(@C(feedback.danger.bg), @C(feedback.danger.fg), @C(feedback.danger.border), @C(feedback.danger.icon))
}

/** Button — web: components/button.html. Pressed replaces hover. */
@Composable
fun DsButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    variant: DsButtonVariant = DsButtonVariant.Primary,
    size: DsControlSize = DsControlSize.Md,
    enabled: Boolean = true,
    loading: Boolean = false,
) {
    val interaction = remember { MutableInteractionSource() }
    val pressed by interaction.collectIsPressedAsState()
    val bg = when (variant) {
        DsButtonVariant.Primary -> if (pressed) @C(action.primary.bg-active) else @C(action.primary.bg)
        DsButtonVariant.Secondary -> if (pressed) @C(action.secondary.bg-active) else @C(action.secondary.bg)
        DsButtonVariant.Ghost -> if (pressed) @C(action.ghost.bg-active) else @C(action.ghost.bg)
        DsButtonVariant.Danger -> if (pressed) @C(action.danger.bg-active) else @C(action.danger.bg)
    }
    val fg = when (variant) {
        DsButtonVariant.Primary -> @C(action.primary.fg)
        DsButtonVariant.Secondary -> @C(action.secondary.fg)
        DsButtonVariant.Ghost -> @C(action.ghost.fg)
        DsButtonVariant.Danger -> @C(action.danger.fg)
    }
    val border = if (variant == DsButtonVariant.Secondary) @C(action.secondary.border) else Color.Transparent
    val height = when (size) {
        DsControlSize.Sm -> @D(button.heightSm)
        DsControlSize.Md -> @D(button.height)
        DsControlSize.Lg -> @D(button.heightLg)
    }
    val shape = RoundedCornerShape(@D(button.radius).dp)
    Row(
        modifier = modifier
            .dsTouchTarget()
            .clickable(interactionSource = interaction, indication = null, enabled = enabled && !loading, role = Role.Button, onClick = onClick)
            .defaultMinSize(minWidth = height.dp, minHeight = height.dp)
            .alpha(if (enabled) 1f else DsOpacity.disabled)
            .clip(shape)
            .background(bg, shape)
            .border(@D(button.borderWidth).dp, border, shape)
            .padding(horizontal = @D(button.paddingX).dp),
        horizontalArrangement = Arrangement.spacedBy(@D(button.gap).dp, Alignment.CenterHorizontally),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        if (loading) CircularProgressIndicator(color = fg, strokeWidth = DsDimension.iconStroke.dp, modifier = Modifier.size(DsDimension.iconSizeSm.dp))
        BasicText(text, maxLines = 1, style = @T(body).copy(color = fg, fontSize = @D(button.fontSize).sp, fontWeight = @W(button.fontWeight), lineHeight = (@D(button.fontSize) * 1.2f).sp))
    }
}

/** Text field — label above, hint or error below; the error is text, not color alone. */
@Composable
fun DsTextField(
    value: String,
    onValueChange: (String) -> Unit,
    label: String,
    modifier: Modifier = Modifier,
    hint: String? = null,
    errorText: String? = null,
    enabled: Boolean = true,
) {
    val interaction = remember { MutableInteractionSource() }
    val focused by interaction.collectIsFocusedAsState()
    val shape = RoundedCornerShape(@D(text-field.radius).dp)
    val borderColor = when {
        errorText != null -> @C(border.invalid)
        focused -> @C(border.focus)
        else -> @C(input.border|text-field)
    }
    val borderWidth = if (focused || errorText != null) (@D(text-field.borderWidth) * 2).dp else @D(text-field.borderWidth).dp
    val fieldBg = @C(input.bg|text-field)
    Column(modifier.alpha(if (enabled) 1f else DsOpacity.disabled), verticalArrangement = Arrangement.spacedBy(@D(text-field.gap).dp)) {
        BasicText(label, style = @T(small).copy(color = @C(text.default)))
        BasicTextField(
            value = value,
            onValueChange = onValueChange,
            enabled = enabled,
            singleLine = true,
            interactionSource = interaction,
            textStyle = @T(body).copy(color = @C(text.default), fontSize = @D(text-field.fontSize).sp),
            cursorBrush = SolidColor(@C(text.default)),
            modifier = Modifier.fillMaxWidth().semantics {
                contentDescription = label
                if (errorText != null) error(errorText)
            },
            decorationBox = { inner ->
                Box(
                    Modifier
                        .defaultMinSize(minHeight = @D(text-field.height).dp)
                        .background(fieldBg, shape)
                        .border(borderWidth, borderColor, shape)
                        .padding(horizontal = @D(text-field.paddingX).dp),
                    contentAlignment = Alignment.CenterStart,
                ) { inner() }
            },
        )
        when {
            errorText != null -> BasicText(errorText, style = @T(small).copy(color = @C(feedback.danger.fg)))
            hint != null -> BasicText(hint, style = @T(small).copy(color = @C(text.muted)))
        }
    }
}

@Composable
fun DsCheckbox(checked: Boolean, onCheckedChange: (Boolean) -> Unit, label: String, modifier: Modifier = Modifier, enabled: Boolean = true) {
    val shape = RoundedCornerShape(@D(checkbox.radius).dp)
    val mark = @C(action.primary.fg)
    Row(
        modifier
            .dsTouchTarget()
            .toggleable(value = checked, enabled = enabled, role = Role.Checkbox, onValueChange = onCheckedChange)
            .defaultMinSize(minHeight = @D(checkbox.rowHeight).dp)
            .alpha(if (enabled) 1f else DsOpacity.disabled),
        horizontalArrangement = Arrangement.spacedBy(@D(checkbox.gap).dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            Modifier
                .size(@D(checkbox.size).dp)
                .background(if (checked) @C(action.primary.bg) else @C(input.bg), shape)
                .border(@D(checkbox.borderWidth).dp, if (checked) @C(action.primary.bg) else @C(input.border|checkbox), shape),
        ) {
            if (checked) {
                Canvas(Modifier.matchParentSize().padding((@D(checkbox.size) * 0.22f).dp)) {
                    val p = Path().apply {
                        moveTo(0f, size.height / 2)
                        lineTo(size.width * 0.38f, size.height * 0.88f)
                        lineTo(size.width, size.height * 0.12f)
                    }
                    drawPath(p, mark, style = Stroke(width = DsDimension.iconStroke.dp.toPx(), cap = StrokeCap.Round, join = StrokeJoin.Round))
                }
            }
        }
        BasicText(label, style = @T(body).copy(color = @C(text.default)))
    }
}

/** Switch — web geometry. */
@Composable
fun DsSwitch(checked: Boolean, onCheckedChange: (Boolean) -> Unit, label: String, modifier: Modifier = Modifier, enabled: Boolean = true) {
    val travel by animateDpAsState(if (checked) (@D(switch.width) - @D(switch.height)).dp else 0.dp, tween(DsMotion.durationFast.toInt()), label = "knob")
    Row(
        modifier
            .dsTouchTarget()
            .toggleable(value = checked, enabled = enabled, role = Role.Switch, onValueChange = onCheckedChange)
            .defaultMinSize(minHeight = @D(switch.rowHeight).dp)
            .alpha(if (enabled) 1f else DsOpacity.disabled),
        horizontalArrangement = Arrangement.spacedBy(@D(switch.gap).dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Box(
            Modifier
                .size(width = @D(switch.width).dp, height = @D(switch.height).dp)
                .background(if (checked) @C(action.primary.bg) else @C(input.border), CircleShape)
                .padding(@D(switch.inset).dp),
        ) {
            Box(Modifier.offset(x = travel).size((@D(switch.height) - 2 * @D(switch.inset)).dp).background(@C(bg.surface), CircleShape))
        }
        BasicText(label, style = @T(body).copy(color = @C(text.default)))
    }
}

@Composable
fun DsCard(modifier: Modifier = Modifier, content: @Composable ColumnScope.() -> Unit) {
    val shape = RoundedCornerShape(@D(card.radius).dp)
    Column(
        modifier
            .fillMaxWidth()
            .shadow(@E(card.shadow|elevation.raised|shadow.sm).dp, shape, clip = false)
            .background(@C(surface.raised|card), shape)
            .border(@D(card.borderWidth).dp, @C(border.default), shape)
            .padding(@D(card.padding).dp),
        verticalArrangement = Arrangement.spacedBy(@D(card.gap).dp),
        content = content,
    )
}

@Composable
fun DsBadge(text: String, modifier: Modifier = Modifier, tone: DsTone = DsTone.Neutral) {
    val c = dsTone(tone)
    Box(
        modifier
            .defaultMinSize(minHeight = @D(badge.height).dp)
            .background(c.bg, RoundedCornerShape(@D(badge.radius).dp))
            .padding(horizontal = @D(badge.paddingX).dp),
        contentAlignment = Alignment.Center,
    ) {
        BasicText(text, maxLines = 1, style = @T(body).copy(color = c.fg, fontSize = @D(badge.fontSize).sp, fontWeight = @W(badge.fontWeight), lineHeight = (@D(badge.fontSize) * 1.2f).sp))
    }
}

/** Alert — role is conveyed by text and icon, never color alone. */
@Composable
fun DsAlert(title: String, modifier: Modifier = Modifier, message: String? = null, tone: DsTone = DsTone.Info, icon: ImageVector? = null) {
    val c = dsTone(tone)
    val shape = RoundedCornerShape(@D(alert.radius).dp)
    Row(
        modifier
            .fillMaxWidth()
            .background(c.bg, shape)
            .border(@D(alert.borderWidth).dp, c.border, shape)
            .padding(@D(alert.padding).dp)
            .semantics(mergeDescendants = true) {},
        horizontalArrangement = Arrangement.spacedBy(@D(alert.gap).dp),
    ) {
        if (icon != null) Image(icon, contentDescription = null, colorFilter = ColorFilter.tint(c.icon), modifier = Modifier.size(@D(alert.iconSize).dp))
        Column(verticalArrangement = Arrangement.spacedBy(DsDimension.space1.dp)) {
            BasicText(title, style = @T(body).copy(color = c.fg, fontWeight = @W(button.fontWeight)))
            if (message != null) BasicText(message, style = @T(small).copy(color = c.fg))
        }
    }
}

@Composable
fun DsAvatar(name: String, modifier: Modifier = Modifier, size: Float = @D(avatar.size)) {
    val initials = if (name.length <= 3) name.uppercase() else name.split(" ").take(2).mapNotNull { it.firstOrNull()?.toString() }.joinToString("").uppercase()
    Box(
        modifier
            .size(size.dp)
            .clip(RoundedCornerShape(minOf(@D(avatar.radius), size / 2).dp))
            .background(@C(bg.muted|avatar))
            .semantics { contentDescription = name },
        contentAlignment = Alignment.Center,
    ) {
        BasicText(initials, style = @T(body).copy(color = @C(text.default), fontSize = (@D(avatar.fontSize) * size / @D(avatar.size)).sp, fontWeight = @W(button.fontWeight)))
    }
}

@Composable
fun DsTag(text: String, modifier: Modifier = Modifier, onRemove: (() -> Unit)? = null) {
    val shape = RoundedCornerShape(@D(tag.radius).dp)
    val fg = @C(text.default)
    Row(
        modifier
            .defaultMinSize(minHeight = @D(tag.height).dp)
            .background(@C(bg.muted), shape)
            .border(@D(tag.borderWidth).dp, @C(border.default|tag), shape)
            .padding(horizontal = @D(tag.paddingX).dp),
        horizontalArrangement = Arrangement.spacedBy(@D(tag.gap).dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        BasicText(text, maxLines = 1, style = @T(body).copy(color = fg, fontSize = @D(tag.fontSize).sp))
        if (onRemove != null) {
            Canvas(
                Modifier
                    .dsTouchTarget()
                    .clickable(role = Role.Button, onClick = onRemove)
                    .semantics { contentDescription = "Remove $text" }
                    .size(DsDimension.iconSizeSm.dp)
                    .padding(DsDimension.space1.dp),
            ) {
                val w = DsDimension.iconStroke.dp.toPx()
                drawLine(fg, androidx.compose.ui.geometry.Offset(0f, 0f), androidx.compose.ui.geometry.Offset(size.width, size.height), w, StrokeCap.Round)
                drawLine(fg, androidx.compose.ui.geometry.Offset(size.width, 0f), androidx.compose.ui.geometry.Offset(0f, size.height), w, StrokeCap.Round)
            }
        }
    }
}

@Composable
fun DsDivider(modifier: Modifier = Modifier) {
    Box(modifier.fillMaxWidth().height(@D(divider.thickness).dp).background(@C(border.default|divider)))
}
