// @HEAD
// Mobile scope: gesture components on React Native core (no extra dependencies), styled with tokens.
// Web spec: references/components/mobile.md. Every gesture also has a non-drag path: long press + accessibility actions
// for rows, buttons for sheets, pages and zoom. collapsing-app-bar: an Animated header driven by onScroll (no wrapper).
import React, { useEffect, useMemo, useRef, useState } from 'react';
import type { ReactNode } from 'react';
import {
  AccessibilityInfo, Animated, FlatList, Modal, PanResponder, Pressable, RefreshControl, ScrollView, StyleSheet, Text, View,
  useWindowDimensions,
} from 'react-native';
import { DsButton, useDsColors } from './DsComponents';
import { dimension, typography } from './theme';
import type { DsColors } from './theme';

/** One action of a swipe row or an action sheet. */
export type DsAction = { label: string; onPress: () => void; destructive?: boolean };

function useReduceMotion() {
  const [reduce, setReduce] = useState(false);
  useEffect(() => {
    AccessibilityInfo.isReduceMotionEnabled().then(setReduce);
    const sub = AccessibilityInfo.addEventListener('reduceMotionChanged', setReduce);
    return () => sub.remove();
  }, []);
  return reduce;
}

function settle(value: Animated.Value, toValue: number, reduce: boolean) {
  if (reduce) value.setValue(toValue);
  else Animated.spring(value, { toValue, useNativeDriver: true, bounciness: 0 }).start();
}

/**
 * swipe-actions — web: components/swipe-actions.html. Swipe to reveal trailing (end) or leading (start) actions, each
 * size.swipe-action wide. Long press opens every action in DsActionSheet; they are accessibility actions too.
 */
export function DsSwipeRow({ trailing, leading, onPress, children }: {
  trailing: DsAction[];
  leading?: DsAction;
  onPress?: () => void;
  children: ReactNode;
}) {
  const colors = useDsColors();
  const reduce = useReduceMotion();
  const [menu, setMenu] = useState(false);
  const x = useRef(new Animated.Value(0)).current;
  const w = dimension.sizeSwipeAction;
  const all = leading ? [leading, ...trailing] : trailing;
  const pan = useMemo(() => PanResponder.create({
    onMoveShouldSetPanResponder: (_, g) => Math.abs(g.dx) > 10 && Math.abs(g.dx) > Math.abs(g.dy),
    onPanResponderMove: (_, g) => x.setValue(Math.max(-w * trailing.length, Math.min(leading ? w : 0, g.dx))),
    onPanResponderRelease: (_, g) => settle(x, g.dx < -w / 2 ? -w * trailing.length : g.dx > w / 2 && leading ? w : 0, reduce),
    onPanResponderTerminate: () => settle(x, 0, reduce),
  }), [x, w, trailing.length, leading, reduce]);
  const button = (a: DsAction) => (
    <Pressable
      key={a.label}
      accessibilityRole="button"
      onPress={() => { settle(x, 0, reduce); a.onPress(); }}
      style={{ width: w, justifyContent: 'center', alignItems: 'center', backgroundColor: a.destructive ? @C(action.danger.bg) : @C(action.primary.bg) }}
    >
      <Text style={[typography.body, { color: a.destructive ? @C(action.danger.fg) : @C(action.primary.fg) }]}>{a.label}</Text>
    </Pressable>
  );
  return (
    <View
      accessibilityActions={all.map((a) => ({ name: a.label, label: a.label }))}
      onAccessibilityAction={(e) => all.find((a) => a.label === e.nativeEvent.actionName)?.onPress()}
    >
      <View style={[StyleSheet.absoluteFill, { flexDirection: 'row', justifyContent: 'space-between' }]}>
        {leading ? button(leading) : <View />}
        <View style={{ flexDirection: 'row' }}>{trailing.map(button)}</View>
      </View>
      <Animated.View {...pan.panHandlers} style={{ transform: [{ translateX: x }], backgroundColor: @C(surface.raised|card) }}>
        <Pressable onPress={() => { settle(x, 0, reduce); onPress?.(); }} onLongPress={() => setMenu(true)}>{children}</Pressable>
      </Animated.View>
      <DsActionSheet visible={menu} actions={all} onClose={() => setMenu(false)} />
    </View>
  );
}

/** pull-to-refresh — web: components/pull-to-refresh.html. Pass as `refreshControl`; also offer a Refresh button. */
export function dsRefreshControl(colors: DsColors, refreshing: boolean, onRefresh: () => void) {
  return (
    <RefreshControl
      refreshing={refreshing}
      onRefresh={onRefresh}
      tintColor={@C(action.primary.bg)}
      colors={[@C(action.primary.bg)]}
      progressBackgroundColor={@C(surface.raised|card)}
    />
  );
}

function SheetFrame({ visible, onClose, children }: { visible: boolean; onClose: () => void; children: ReactNode }) {
  const colors = useDsColors();
  const reduce = useReduceMotion();
  return (
    <Modal visible={visible} transparent animationType={reduce ? 'none' : 'slide'} onRequestClose={onClose}>
      <Pressable accessibilityRole="button" accessibilityLabel="Close" style={{ flex: 1 }} onPress={onClose} />
      <View style={{ backgroundColor: @C(surface.raised|card), borderTopLeftRadius: @D(card.radius), borderTopRightRadius: @D(card.radius) }}>
        {children}
      </View>
    </Modal>
  );
}

/** action-sheet — web: components/action-sheet.html. Cancel is added; nothing destructive is pre-selected. */
export function DsActionSheet({ visible, title, actions, onClose }: {
  visible: boolean;
  title?: string;
  actions: DsAction[];
  onClose: () => void;
}) {
  const colors = useDsColors();
  return (
    <SheetFrame visible={visible} onClose={onClose}>
      <View style={{ paddingVertical: dimension.space1 * 2 }}>
        {title ? <Text style={[typography.small, { color: @C(text.muted), paddingHorizontal: dimension.space1 * 4 }]}>{title}</Text> : null}
        {[...actions, { label: 'Cancel', onPress: () => {} }].map((a: DsAction) => (
          <Pressable
            key={a.label}
            accessibilityRole="button"
            onPress={() => { onClose(); a.onPress(); }}
            style={{ minHeight: dimension.androidTouchTarget, justifyContent: 'center', paddingHorizontal: dimension.space1 * 4 }}
          >
            <Text style={[typography.body, { color: a.destructive ? @C(feedback.danger.fg) : @C(text.default) }]}>{a.label}</Text>
          </Pressable>
        ))}
      </View>
    </SheetFrame>
  );
}

/**
 * detent-sheet — web: components/detent-sheet.html. Snaps to peek (size.sheet.peek), half and full; dragging the handle
 * below peek closes it. The handle is also a button that cycles the heights. Put a Close button in the content.
 */
export function DsDetentSheet({ visible, onClose, children }: { visible: boolean; onClose: () => void; children: ReactNode }) {
  const colors = useDsColors();
  const reduce = useReduceMotion();
  const { height } = useWindowDimensions();
  const snaps = useMemo(() => [dimension.sizeSheetPeek, height * 0.5, height * 0.9], [height]);
  const [index, setIndex] = useState(1);
  const y = useRef(new Animated.Value(height - snaps[1])).current;
  const go = (i: number) => {
    setIndex(i);
    settle(y, height - snaps[i], reduce);
  };
  const pan = useMemo(() => PanResponder.create({
    onMoveShouldSetPanResponder: (_, g) => Math.abs(g.dy) > 6,
    onPanResponderMove: (_, g) => y.setValue(Math.max(height - snaps[2], height - snaps[index] + g.dy)),
    onPanResponderRelease: (_, g) => {
      const visible = snaps[index] - g.dy;
      if (visible < snaps[0] / 2) { onClose(); return; }
      let best = 0;
      snaps.forEach((s, i) => { if (Math.abs(s - visible) < Math.abs(snaps[best] - visible)) best = i; });
      go(best);
    },
  }), [height, snaps, index, reduce]);
  const names = ['peek', 'half height', 'full height'];
  return (
    <Modal visible={visible} transparent animationType="none" onRequestClose={onClose}>
      <Animated.View
        style={{ position: 'absolute', left: 0, right: 0, top: 0, height, transform: [{ translateY: y }],
          backgroundColor: @C(surface.raised|card), borderTopLeftRadius: @D(card.radius), borderTopRightRadius: @D(card.radius) }}
      >
        <Pressable
          {...pan.panHandlers}
          accessibilityRole="button"
          accessibilityLabel={`Resize sheet, ${names[index]}`}
          onPress={() => go((index + 1) % snaps.length)}
          style={{ height: dimension.androidTouchTarget, alignItems: 'center', justifyContent: 'center' }}
        >
          <View style={{ width: dimension.space1 * 9, height: dimension.space1, borderRadius: dimension.space1, backgroundColor: @C(border.default) }} />
        </Pressable>
        <View style={{ height: snaps[index] - dimension.androidTouchTarget }}>{children}</View>
      </Animated.View>
    </Modal>
  );
}

/** swipe-pager — web: components/swipe-pager.html. Swipe between pages; the dots are buttons ("Page 2 of 4"). */
export function DsPager({ count, renderPage }: { count: number; renderPage: (i: number) => ReactNode }) {
  const colors = useDsColors();
  const { width } = useWindowDimensions();
  const list = useRef<FlatList<number>>(null);
  const [page, setPage] = useState(0);
  return (
    <View style={{ flex: 1 }}>
      <FlatList
        ref={list}
        data={Array.from({ length: count }, (_, i) => i)}
        keyExtractor={(i) => String(i)}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        onMomentumScrollEnd={(e) => setPage(Math.round(e.nativeEvent.contentOffset.x / width))}
        renderItem={({ item }) => <View style={{ width }}>{renderPage(item)}</View>}
      />
      <View style={{ flexDirection: 'row', justifyContent: 'center' }}>
        {Array.from({ length: count }, (_, i) => (
          <Pressable
            key={i}
            accessibilityRole="button"
            accessibilityLabel={`Page ${i + 1} of ${count}`}
            accessibilityState={{ selected: i === page }}
            onPress={() => { setPage(i); list.current?.scrollToIndex({ index: i }); }}
            style={{ width: dimension.androidTouchTarget, height: dimension.androidTouchTarget, alignItems: 'center', justifyContent: 'center' }}
          >
            <View style={{ width: dimension.space1 * 2, height: dimension.space1 * 2, borderRadius: dimension.space1,
              backgroundColor: i === page ? @C(action.primary.bg) : @C(border.default) }} />
          </Pressable>
        ))}
      </View>
    </View>
  );
}

/**
 * zoomable-image — web: components/zoomable-image.html. iOS: pinch to zoom (ScrollView); everywhere: Zoom out / Reset /
 * Zoom in buttons (1x–4x).
 * ponytail: no pinch on Android and no double tap; add react-native-gesture-handler when the app needs them.
 */
export function DsZoomableImage({ label, children }: { label: string; children: ReactNode }) {
  const [scale, setScale] = useState(1);
  const zoom = (to: number) => setScale(Math.min(4, Math.max(1, to)));
  return (
    <View style={{ gap: dimension.space1 }}>
      <ScrollView
        maximumZoomScale={4}
        minimumZoomScale={1}
        accessibilityLabel={label}
        accessibilityValue={{ text: `${Math.round(scale * 100)}%` }}
      >
        <View style={{ transform: [{ scale }] }}>{children}</View>
      </ScrollView>
      <View style={{ flexDirection: 'row', gap: dimension.space1 }}>
        <DsButton label="Zoom out" variant="secondary" size="sm" disabled={scale <= 1} onPress={() => zoom(scale - 1)} />
        <DsButton label="Reset zoom" variant="secondary" size="sm" disabled={scale <= 1} onPress={() => zoom(1)} />
        <DsButton label="Zoom in" variant="secondary" size="sm" disabled={scale >= 4} onPress={() => zoom(scale + 1)} />
      </View>
    </View>
  );
}
