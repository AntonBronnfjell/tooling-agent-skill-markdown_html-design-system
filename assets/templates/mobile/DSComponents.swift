// @HEAD
// Core components, tokens only. Build every other component from dist/mobile/spec.json the same way.
import SwiftUI

public enum DSButtonVariant { case primary, secondary, ghost, danger }
public enum DSControlSize { case sm, md, lg }
public enum DSTone { case neutral, info, success, warning, danger }

struct DSToneColors { let bg: Color; let fg: Color; let border: Color; let icon: Color }

func dsTone(_ tone: DSTone) -> DSToneColors {
    switch tone {
    case .neutral: return DSToneColors(bg: @C(bg.muted|badge), fg: @C(text.default|badge), border: @C(border.default), icon: @C(text.muted))
    case .info: return DSToneColors(bg: @C(feedback.info.bg|alert), fg: @C(feedback.info.fg), border: @C(feedback.info.border|alert), icon: @C(feedback.info.icon))
    case .success: return DSToneColors(bg: @C(feedback.success.bg), fg: @C(feedback.success.fg), border: @C(feedback.success.border), icon: @C(feedback.success.icon))
    case .warning: return DSToneColors(bg: @C(feedback.warning.bg), fg: @C(feedback.warning.fg), border: @C(feedback.warning.border), icon: @C(feedback.warning.icon))
    case .danger: return DSToneColors(bg: @C(feedback.danger.bg), fg: @C(feedback.danger.fg), border: @C(feedback.danger.border), icon: @C(feedback.danger.icon))
    }
}

/// Button — web: components/button.html. Pressed replaces hover; the hit area grows to 44 pt without changing the look.
public struct DSButtonStyle: ButtonStyle {
    public var variant: DSButtonVariant
    public var size: DSControlSize
    public var isLoading: Bool

    public init(_ variant: DSButtonVariant = .primary, size: DSControlSize = .md, isLoading: Bool = false) {
        self.variant = variant
        self.size = size
        self.isLoading = isLoading
    }

    public func makeBody(configuration: Configuration) -> some View {
        DSButtonBody(label: configuration.label, isPressed: configuration.isPressed, style: self)
    }
}

private struct DSButtonBody<Label: View>: View {
    let label: Label
    let isPressed: Bool
    let style: DSButtonStyle
    @Environment(\.isEnabled) private var isEnabled

    private var colors: (bg: Color, fg: Color, border: Color) {
        switch style.variant {
        case .primary: return (isPressed ? @C(action.primary.bg-active) : @C(action.primary.bg), @C(action.primary.fg|button), .clear)
        case .secondary: return (isPressed ? @C(action.secondary.bg-active) : @C(action.secondary.bg), @C(action.secondary.fg), @C(action.secondary.border))
        case .ghost: return (isPressed ? @C(action.ghost.bg-active) : @C(action.ghost.bg), @C(action.ghost.fg), .clear)
        case .danger: return (isPressed ? @C(action.danger.bg-active) : @C(action.danger.bg), @C(action.danger.fg), .clear)
        }
    }

    private var height: CGFloat {
        switch style.size {
        case .sm: return @D(button.heightSm)
        case .md: return @D(button.height)
        case .lg: return @D(button.heightLg)
        }
    }

    var body: some View {
        let c = colors
        HStack(spacing: @D(button.gap)) {
            if style.isLoading { ProgressView().tint(c.fg).controlSize(.small) }
            label
                .font(.custom(@T(body).family, size: @D(button.fontSize), relativeTo: .body).weight(@W(button.fontWeight)))
                .lineLimit(1)
        }
        .padding(.horizontal, @D(button.paddingX))
        .frame(minWidth: height, minHeight: height)
        .foregroundStyle(c.fg)
        .background(RoundedRectangle(cornerRadius: @D(button.radius)).fill(c.bg))
        .overlay(RoundedRectangle(cornerRadius: @D(button.radius)).strokeBorder(c.border, lineWidth: @D(button.borderWidth)))
        .opacity(isEnabled ? 1 : DSOpacity.disabled)
        .contentShape(Rectangle().inset(by: -max(0, (DSDimension.sizeTouchTarget - height) / 2)))
        .allowsHitTesting(!style.isLoading)
        .accessibilityAddTraits(.isButton)
    }
}

/// Text field — label above, hint or error below; error is text, not color alone.
public struct DSTextField: View {
    private let label: String
    @Binding private var text: String
    private let hint: String?
    private let error: String?
    @FocusState private var focused: Bool
    @Environment(\.isEnabled) private var isEnabled

    public init(_ label: String, text: Binding<String>, hint: String? = nil, error: String? = nil) {
        self.label = label
        self._text = text
        self.hint = hint
        self.error = error
    }

    private var borderColor: Color { error != nil ? @C(border.invalid) : focused ? @C(border.focus) : @C(input.border|text-field) }

    public var body: some View {
        VStack(alignment: .leading, spacing: @D(text-field.gap)) {
            Text(label).dsText(@T(small)).foregroundStyle(@C(text.default))
            TextField("", text: $text)
                .focused($focused)
                .font(.custom(@T(body).family, size: @D(text-field.fontSize), relativeTo: .body))
                .foregroundStyle(@C(text.default))
                .padding(.horizontal, @D(text-field.paddingX))
                .frame(minHeight: @D(text-field.height))
                .background(RoundedRectangle(cornerRadius: @D(text-field.radius)).fill(@C(input.bg|text-field)))
                .overlay(RoundedRectangle(cornerRadius: @D(text-field.radius))
                    .strokeBorder(borderColor, lineWidth: focused || error != nil ? @D(text-field.borderWidth) * 2 : @D(text-field.borderWidth)))
                .accessibilityLabel(label)
                .accessibilityHint(error ?? hint ?? "")
            if let error {
                Text(error).dsText(@T(small)).foregroundStyle(@C(feedback.danger.fg))
            } else if let hint {
                Text(hint).dsText(@T(small)).foregroundStyle(@C(text.muted))
            }
        }
        .opacity(isEnabled ? 1 : DSOpacity.disabled)
    }
}

struct DSCheckmark: Shape {
    func path(in r: CGRect) -> Path {
        var p = Path()
        p.move(to: CGPoint(x: r.minX, y: r.midY))
        p.addLine(to: CGPoint(x: r.minX + r.width * 0.38, y: r.maxY - r.height * 0.12))
        p.addLine(to: CGPoint(x: r.maxX, y: r.minY + r.height * 0.12))
        return p
    }
}

struct DSCross: Shape {
    func path(in r: CGRect) -> Path {
        var p = Path()
        p.move(to: CGPoint(x: r.minX, y: r.minY))
        p.addLine(to: CGPoint(x: r.maxX, y: r.maxY))
        p.move(to: CGPoint(x: r.maxX, y: r.minY))
        p.addLine(to: CGPoint(x: r.minX, y: r.maxY))
        return p
    }
}

/// Checkbox — use as Toggle(...).toggleStyle(DSCheckboxStyle()).
public struct DSCheckboxStyle: ToggleStyle {
    public init() {}

    public func makeBody(configuration: Configuration) -> some View {
        DSCheckboxBody(configuration: configuration)
    }
}

private struct DSCheckboxBody: View {
    let configuration: ToggleStyleConfiguration
    @Environment(\.isEnabled) private var isEnabled

    var body: some View {
        let on = configuration.isOn
        HStack(spacing: @D(checkbox.gap)) {
            ZStack {
                RoundedRectangle(cornerRadius: @D(checkbox.radius)).fill(on ? @C(action.primary.bg) : @C(input.bg))
                RoundedRectangle(cornerRadius: @D(checkbox.radius)).strokeBorder(on ? @C(action.primary.bg) : @C(input.border|checkbox), lineWidth: @D(checkbox.borderWidth))
                if on {
                    DSCheckmark()
                        .stroke(@C(action.primary.fg), style: StrokeStyle(lineWidth: DSDimension.iconStroke, lineCap: .round, lineJoin: .round))
                        .padding(@D(checkbox.size) * 0.22)
                }
            }
            .frame(width: @D(checkbox.size), height: @D(checkbox.size))
            configuration.label.dsText(@T(body)).foregroundStyle(@C(text.default))
        }
        .frame(minHeight: @D(checkbox.rowHeight))
        .contentShape(Rectangle())
        .onTapGesture { if isEnabled { configuration.isOn.toggle() } }
        .opacity(isEnabled ? 1 : DSOpacity.disabled)
        .accessibilityElement(children: .combine)
        .accessibilityAddTraits(.isButton)
        .accessibilityValue(on ? "Checked" : "Unchecked")
    }
}

/// Switch — web geometry, not the iOS 51×31 control. Prefer Toggle().tint(@C(action.primary.bg)) if the platform look is wanted.
public struct DSSwitchStyle: ToggleStyle {
    public init() {}

    public func makeBody(configuration: Configuration) -> some View {
        DSSwitchBody(configuration: configuration)
    }
}

private struct DSSwitchBody: View {
    let configuration: ToggleStyleConfiguration
    @Environment(\.isEnabled) private var isEnabled
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        let on = configuration.isOn
        HStack(spacing: @D(switch.gap)) {
            ZStack(alignment: on ? .trailing : .leading) {
                Capsule().fill(on ? @C(action.primary.bg) : @C(input.border))
                Circle().fill(@C(bg.surface)).padding(@D(switch.inset))
            }
            .frame(width: @D(switch.width), height: @D(switch.height)) // ds-lint: ignore (visual track; the row is the touch target)
            .animation(reduceMotion ? nil : DSMotion.easingStandard(DSMotion.durationFast), value: on)
            configuration.label.dsText(@T(body)).foregroundStyle(@C(text.default))
        }
        .frame(minHeight: @D(switch.rowHeight))
        .contentShape(Rectangle())
        .onTapGesture { if isEnabled { configuration.isOn.toggle() } }
        .opacity(isEnabled ? 1 : DSOpacity.disabled)
        .accessibilityElement(children: .combine)
        .accessibilityAddTraits(.isButton)
        .accessibilityValue(on ? "On" : "Off")
    }
}

public struct DSCard<Content: View>: View {
    private let content: Content

    public init(@ViewBuilder content: () -> Content) { self.content = content() }

    public var body: some View {
        VStack(alignment: .leading, spacing: @D(card.gap)) { content }
            .padding(@D(card.padding))
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(RoundedRectangle(cornerRadius: @D(card.radius)).fill(@C(surface.raised|card)))
            .overlay(RoundedRectangle(cornerRadius: @D(card.radius)).strokeBorder(@C(border.default), lineWidth: @D(card.borderWidth)))
            .dsShadow(@E(card.shadow|elevation.raised|shadow.sm))
    }
}

public struct DSBadge: View {
    private let text: String
    private let tone: DSTone

    public init(_ text: String, tone: DSTone = .neutral) {
        self.text = text
        self.tone = tone
    }

    public var body: some View {
        let c = dsTone(tone)
        Text(text)
            .font(.custom(@T(body).family, size: @D(badge.fontSize), relativeTo: .caption).weight(@W(badge.fontWeight)))
            .lineLimit(1)
            .padding(.horizontal, @D(badge.paddingX))
            .frame(minHeight: @D(badge.height))
            .foregroundStyle(c.fg)
            .background(RoundedRectangle(cornerRadius: @D(badge.radius)).fill(c.bg))
    }
}

/// Alert — role is conveyed by text and icon, never color alone.
public struct DSAlert: View {
    private let title: String
    private let message: String?
    private let tone: DSTone
    private let icon: Image?

    public init(_ title: String, message: String? = nil, tone: DSTone = .info, icon: Image? = nil) {
        self.title = title
        self.message = message
        self.tone = tone
        self.icon = icon
    }

    public var body: some View {
        let c = dsTone(tone)
        HStack(alignment: .top, spacing: @D(alert.gap)) {
            if let icon {
                icon.renderingMode(.template).resizable().scaledToFit()
                    .frame(width: @D(alert.iconSize), height: @D(alert.iconSize))
                    .foregroundStyle(c.icon)
                    .accessibilityHidden(true)
            }
            VStack(alignment: .leading, spacing: DSDimension.space1) {
                Text(title).fontWeight(.semibold).dsText(@T(body))
                if let message { Text(message).dsText(@T(small)) }
            }
        }
        .foregroundStyle(c.fg)
        .padding(@D(alert.padding))
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(RoundedRectangle(cornerRadius: @D(alert.radius)).fill(c.bg))
        .overlay(RoundedRectangle(cornerRadius: @D(alert.radius)).strokeBorder(c.border, lineWidth: @D(alert.borderWidth)))
        .accessibilityElement(children: .combine)
    }
}

public struct DSAvatar: View {
    private let name: String
    private let image: Image?
    private let size: CGFloat

    public init(_ name: String, image: Image? = nil, size: CGFloat = @D(avatar.size)) {
        self.name = name
        self.image = image
        self.size = size
    }

    private var initials: String {
        name.count <= 3 ? name.uppercased() : name.split(separator: " ").prefix(2).compactMap { $0.first }.map(String.init).joined().uppercased()
    }

    public var body: some View {
        ZStack {
            Rectangle().fill(@C(bg.muted|avatar))
            if let image {
                image.resizable().scaledToFill()
            } else {
                Text(initials)
                    .font(.custom(@T(body).family, size: @D(avatar.fontSize) * size / @D(avatar.size), relativeTo: .body).weight(.semibold))
                    .foregroundStyle(@C(text.default))
            }
        }
        .frame(width: size, height: size)
        .clipShape(RoundedRectangle(cornerRadius: min(@D(avatar.radius), size / 2)))
        .accessibilityElement()
        .accessibilityLabel(name)
    }
}

public struct DSTag: View {
    private let text: String
    private let onRemove: (() -> Void)?

    public init(_ text: String, onRemove: (() -> Void)? = nil) {
        self.text = text
        self.onRemove = onRemove
    }

    public var body: some View {
        HStack(spacing: @D(tag.gap)) {
            Text(text).font(.custom(@T(body).family, size: @D(tag.fontSize), relativeTo: .footnote)).lineLimit(1)
            if let onRemove {
                Button(action: onRemove) {
                    DSCross().stroke(style: StrokeStyle(lineWidth: DSDimension.iconStroke, lineCap: .round))
                        .padding(DSDimension.space1)
                        .frame(width: DSDimension.iconSizeSm, height: DSDimension.iconSizeSm)
                }
                .buttonStyle(.plain)
                .contentShape(Rectangle().inset(by: -(DSDimension.sizeTouchTarget - DSDimension.iconSizeSm) / 2))
                .accessibilityLabel("Remove \(text)")
            }
        }
        .padding(.horizontal, @D(tag.paddingX))
        .frame(minHeight: @D(tag.height))
        .foregroundStyle(@C(text.default))
        .background(RoundedRectangle(cornerRadius: @D(tag.radius)).fill(@C(bg.muted)))
        .overlay(RoundedRectangle(cornerRadius: @D(tag.radius)).strokeBorder(@C(border.default|tag), lineWidth: @D(tag.borderWidth)))
    }
}

public struct DSDivider: View {
    public init() {}

    public var body: some View {
        Rectangle().fill(@C(border.default|divider)).frame(height: @D(divider.thickness)).accessibilityHidden(true)
    }
}
