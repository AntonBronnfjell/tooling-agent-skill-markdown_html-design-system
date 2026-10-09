// @HEAD
// Core components, tokens only. Needs react-native-svg (also used by DsIcon). Works with Expo.
import React, { createContext, useContext, useState } from 'react';
import type { ReactNode } from 'react';
import { ActivityIndicator, Platform, Pressable, Text, TextInput, View, useColorScheme } from 'react-native';
import Svg, { Path } from 'react-native-svg';
import { dimension, elevation, opacity, themes, typography } from './theme';
import type { DsColors } from './theme';

export const DsThemeContext = createContext<string | null>(null);

/** theme undefined = follow the system light/dark setting. */
export function DsThemeProvider({ theme, children }: { theme?: string; children: ReactNode }) {
  return <DsThemeContext.Provider value={theme ?? null}>{children}</DsThemeContext.Provider>;
}

export function useDsColors(): DsColors {
  const scheme = useColorScheme();
  const name = useContext(DsThemeContext) ?? (scheme === 'dark' ? '@DARK' : '@LIGHT');
  return themes[name] ?? themes['@LIGHT'];
}

const minTouch = Platform.OS === 'ios' ? dimension.sizeTouchTarget : dimension.androidTouchTarget;

/** Grows the touch area to 44 pt / 48 dp without changing layout (matches the web box). */
export function hitSlop(size: number) {
  const v = Math.max(0, (minTouch - size) / 2);
  return { top: v, bottom: v, left: v, right: v };
}

export type DsTone = 'neutral' | 'info' | 'success' | 'warning' | 'danger';

function tone(colors: DsColors, t: DsTone) {
  return {
    neutral: { bg: @C(bg.muted|badge), fg: @C(text.default|badge), border: @C(border.default), icon: @C(text.muted) },
    info: { bg: @C(feedback.info.bg|alert), fg: @C(feedback.info.fg), border: @C(feedback.info.border|alert), icon: @C(feedback.info.icon) },
    success: { bg: @C(feedback.success.bg), fg: @C(feedback.success.fg), border: @C(feedback.success.border), icon: @C(feedback.success.icon) },
    warning: { bg: @C(feedback.warning.bg), fg: @C(feedback.warning.fg), border: @C(feedback.warning.border), icon: @C(feedback.warning.icon) },
    danger: { bg: @C(feedback.danger.bg), fg: @C(feedback.danger.fg), border: @C(feedback.danger.border), icon: @C(feedback.danger.icon) },
  }[t];
}

export type DsButtonProps = {
  label: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
};

/** Button — web: components/button.html. Pressed replaces hover. */
export function DsButton({ label, onPress, variant = 'primary', size = 'md', disabled = false, loading = false }: DsButtonProps) {
  const colors = useDsColors();
  const v = {
    primary: [@C(action.primary.bg|button), @C(action.primary.bg-active), @C(action.primary.fg|button), 'transparent'],
    secondary: [@C(action.secondary.bg), @C(action.secondary.bg-active), @C(action.secondary.fg), @C(action.secondary.border)],
    ghost: [@C(action.ghost.bg), @C(action.ghost.bg-active), @C(action.ghost.fg), 'transparent'],
    danger: [@C(action.danger.bg), @C(action.danger.bg-active), @C(action.danger.fg), 'transparent'],
  }[variant];
  const height = size === 'sm' ? @D(button.heightSm) : size === 'lg' ? @D(button.heightLg) : @D(button.height);
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ disabled: disabled || loading, busy: loading }}
      disabled={disabled || loading}
      onPress={onPress}
      hitSlop={hitSlop(height)}
      style={({ pressed }) => ({
        flexDirection: 'row',
        alignItems: 'center',
        justifyContent: 'center',
        alignSelf: 'flex-start',
        minHeight: height,
        minWidth: height,
        paddingHorizontal: @D(button.paddingX),
        gap: @D(button.gap),
        borderRadius: @D(button.radius),
        borderWidth: @D(button.borderWidth),
        borderColor: v[3],
        backgroundColor: pressed ? v[1] : v[0],
        opacity: disabled ? opacity.disabled : 1,
      })}
    >
      {loading ? <ActivityIndicator size="small" color={v[2]} /> : null}
      <Text numberOfLines={1} style={[typography.body, { color: v[2], fontSize: @D(button.fontSize), fontWeight: @W(button.fontWeight), lineHeight: undefined }]}>
        {label}
      </Text>
    </Pressable>
  );
}

/** Text field — label above, hint or error below; the error is text, not color alone. */
export function DsTextField({ label, value, onChangeText, hint, error, editable = true }: {
  label: string;
  value: string;
  onChangeText: (text: string) => void;
  hint?: string;
  error?: string;
  editable?: boolean;
}) {
  const colors = useDsColors();
  const [focused, setFocused] = useState(false);
  const borderColor = error ? @C(border.invalid) : focused ? @C(border.focus) : @C(input.border|text-field);
  return (
    <View style={{ gap: @D(text-field.gap), opacity: editable ? 1 : opacity.disabled }}>
      <Text style={[typography.small, { color: @C(text.default) }]}>{label}</Text>
      <TextInput
        accessibilityLabel={label}
        accessibilityHint={error ?? hint}
        value={value}
        onChangeText={onChangeText}
        editable={editable}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        style={[typography.body, {
          minHeight: @D(text-field.height),
          paddingHorizontal: @D(text-field.paddingX),
          fontSize: @D(text-field.fontSize),
          lineHeight: undefined,
          color: @C(text.default),
          backgroundColor: @C(input.bg|text-field),
          borderColor,
          borderWidth: focused || error ? @D(text-field.borderWidth) * 2 : @D(text-field.borderWidth),
          borderRadius: @D(text-field.radius),
        }]}
      />
      {error ? (
        <Text style={[typography.small, { color: @C(feedback.danger.fg) }]}>{error}</Text>
      ) : hint ? (
        <Text style={[typography.small, { color: @C(text.muted) }]}>{hint}</Text>
      ) : null}
    </View>
  );
}

function Mark({ color, size, cross = false }: { color: string; size: number; cross?: boolean }) {
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      <Path d={cross ? 'M6 6l12 12M18 6L6 18' : 'M4 12.5l5 5L20 6.5'} stroke={color} strokeWidth={dimension.iconStroke * 24 / size} strokeLinecap="round" strokeLinejoin="round" />
    </Svg>
  );
}

export function DsCheckbox({ value, onValueChange, label, disabled = false }: { value: boolean; onValueChange: (v: boolean) => void; label: string; disabled?: boolean }) {
  const colors = useDsColors();
  const s = @D(checkbox.size);
  return (
    <Pressable
      accessibilityRole="checkbox"
      accessibilityState={{ checked: value, disabled }}
      accessibilityLabel={label}
      disabled={disabled}
      onPress={() => onValueChange(!value)}
      style={{ flexDirection: 'row', alignItems: 'center', gap: @D(checkbox.gap), minHeight: @D(checkbox.rowHeight), opacity: disabled ? opacity.disabled : 1 }}
    >
      <View style={{ width: s, height: s, alignItems: 'center', justifyContent: 'center', borderRadius: @D(checkbox.radius), borderWidth: @D(checkbox.borderWidth), borderColor: value ? @C(action.primary.bg) : @C(input.border|checkbox), backgroundColor: value ? @C(action.primary.bg) : @C(input.bg) }}>
        {value ? <Mark color={@C(action.primary.fg)} size={s * 0.8} /> : null}
      </View>
      <Text style={[typography.body, { color: @C(text.default), flexShrink: 1 }]}>{label}</Text>
    </Pressable>
  );
}

/** Switch — web geometry, not the platform control. */
export function DsSwitch({ value, onValueChange, label, disabled = false }: { value: boolean; onValueChange: (v: boolean) => void; label: string; disabled?: boolean }) {
  const colors = useDsColors();
  const inset = @D(switch.inset);
  const knob = @D(switch.height) - 2 * inset;
  return (
    <Pressable
      accessibilityRole="switch"
      accessibilityState={{ checked: value, disabled }}
      accessibilityLabel={label}
      disabled={disabled}
      onPress={() => onValueChange(!value)}
      style={{ flexDirection: 'row', alignItems: 'center', gap: @D(switch.gap), minHeight: @D(switch.rowHeight), opacity: disabled ? opacity.disabled : 1 }}
    >
      <View style={{ width: @D(switch.width), height: @D(switch.height), borderRadius: @D(switch.radius), padding: inset, backgroundColor: value ? @C(action.primary.bg) : @C(input.border), alignItems: value ? 'flex-end' : 'flex-start' }}>
        <View style={{ width: knob, height: knob, borderRadius: knob, backgroundColor: @C(bg.surface) }} />
      </View>
      <Text style={[typography.body, { color: @C(text.default), flexShrink: 1 }]}>{label}</Text>
    </Pressable>
  );
}

export function DsCard({ children }: { children: ReactNode }) {
  const colors = useDsColors();
  return (
    <View style={[@E(card.shadow|elevation.raised|shadow.sm), { padding: @D(card.padding), gap: @D(card.gap), borderRadius: @D(card.radius), borderWidth: @D(card.borderWidth), borderColor: @C(border.default), backgroundColor: @C(surface.raised|card) }]}>
      {children}
    </View>
  );
}

export function DsBadge({ text, tone: t = 'neutral' }: { text: string; tone?: DsTone }) {
  const c = tone(useDsColors(), t);
  return (
    <View style={{ alignSelf: 'flex-start', justifyContent: 'center', minHeight: @D(badge.height), paddingHorizontal: @D(badge.paddingX), borderRadius: @D(badge.radius), backgroundColor: c.bg }}>
      <Text numberOfLines={1} style={[typography.body, { color: c.fg, fontSize: @D(badge.fontSize), fontWeight: @W(badge.fontWeight), lineHeight: undefined }]}>{text}</Text>
    </View>
  );
}

/** Alert — role is conveyed by text and icon, never color alone. */
export function DsAlert({ title, message, tone: t = 'info', icon }: { title: string; message?: string; tone?: DsTone; icon?: ReactNode }) {
  const c = tone(useDsColors(), t);
  return (
    <View accessible style={{ flexDirection: 'row', alignItems: 'flex-start', gap: @D(alert.gap), padding: @D(alert.padding), borderRadius: @D(alert.radius), borderWidth: @D(alert.borderWidth), borderColor: c.border, backgroundColor: c.bg }}>
      {icon ?? null}
      <View style={{ flex: 1, gap: dimension.space1 }}>
        <Text style={[typography.body, { color: c.fg, fontWeight: @W(button.fontWeight) }]}>{title}</Text>
        {message ? <Text style={[typography.small, { color: c.fg }]}>{message}</Text> : null}
      </View>
    </View>
  );
}

export function DsAvatar({ name, size = @D(avatar.size) }: { name: string; size?: number }) {
  const colors = useDsColors();
  const initials = name.length <= 3 ? name.toUpperCase() : name.split(' ').filter(Boolean).slice(0, 2).map((p) => p[0]).join('').toUpperCase();
  return (
    <View accessible accessibilityLabel={name} style={{ width: size, height: size, alignItems: 'center', justifyContent: 'center', borderRadius: Math.min(@D(avatar.radius), size / 2), backgroundColor: @C(bg.muted|avatar) }}>
      <Text style={[typography.body, { color: @C(text.default), fontSize: (@D(avatar.fontSize) * size) / @D(avatar.size), fontWeight: @W(button.fontWeight), lineHeight: undefined }]}>{initials}</Text>
    </View>
  );
}

export function DsTag({ text, onRemove }: { text: string; onRemove?: () => void }) {
  const colors = useDsColors();
  return (
    <View style={{ flexDirection: 'row', alignItems: 'center', alignSelf: 'flex-start', gap: @D(tag.gap), minHeight: @D(tag.height), paddingHorizontal: @D(tag.paddingX), borderRadius: @D(tag.radius), borderWidth: @D(tag.borderWidth), borderColor: @C(border.default|tag), backgroundColor: @C(bg.muted) }}>
      <Text numberOfLines={1} style={[typography.body, { color: @C(text.default), fontSize: @D(tag.fontSize), lineHeight: undefined }]}>{text}</Text>
      {onRemove ? (
        <Pressable accessibilityRole="button" accessibilityLabel={`Remove ${text}`} onPress={onRemove} hitSlop={hitSlop(dimension.iconSizeSm)}>
          <Mark color={@C(text.default)} size={dimension.iconSizeSm} cross />
        </Pressable>
      ) : null}
    </View>
  );
}

export function DsDivider() {
  const colors = useDsColors();
  return <View accessibilityElementsHidden importantForAccessibility="no" style={{ height: @D(divider.thickness), backgroundColor: @C(border.default|divider) }} />;
}
