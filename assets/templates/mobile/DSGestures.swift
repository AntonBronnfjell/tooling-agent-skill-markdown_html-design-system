// @HEAD
// Mobile scope: gesture components on the platform built-ins, styled with tokens. Web spec: references/components/mobile.md.
// Every gesture also has a non-drag path: long press / VoiceOver actions for rows, buttons for sheets, pages and zoom.
// No wrapper needed: pull-to-refresh = `.refreshable { await reload() }` (+ a Refresh toolbar button);
// collapsing-app-bar = NavigationStack + `.navigationTitle(...)` + `.navigationBarTitleDisplayMode(.large)`.
import SwiftUI

/// One action of a swipe row or an action sheet.
public struct DSAction: Identifiable {
    public let id = UUID()
    public let label: String
    public let isDestructive: Bool
    public let perform: () -> Void

    public init(_ label: String, isDestructive: Bool = false, perform: @escaping () -> Void) {
        self.label = label
        self.isDestructive = isDestructive
        self.perform = perform
    }
}

private func dsActionButton(_ a: DSAction) -> some View {
    Button(a.label, role: a.isDestructive ? .destructive : nil, action: a.perform)
        .tint(a.isDestructive ? @C(action.danger.bg) : @C(action.primary.bg))
}

public extension View {
    /// swipe-actions — web: components/swipe-actions.html. Use on rows of a List. The same actions open on long press
    /// (context menu) and are VoiceOver actions, so the swipe is never the only way.
    func dsSwipeActions(leading: [DSAction] = [], trailing: [DSAction], allowsFullSwipe: Bool = false) -> some View {
        self
            .swipeActions(edge: .trailing, allowsFullSwipe: allowsFullSwipe) { ForEach(trailing) { dsActionButton($0) } }
            .swipeActions(edge: .leading, allowsFullSwipe: false) { ForEach(leading) { dsActionButton($0) } }
            .contextMenu { ForEach(leading + trailing) { a in Button(a.label, role: a.isDestructive ? .destructive : nil, action: a.perform) } }
            .accessibilityActions { ForEach(leading + trailing) { a in Button(a.label, action: a.perform) } }
    }

    /// action-sheet — web: components/action-sheet.html. Cancel is added; the destructive action is never the default.
    func dsActionSheet(_ title: String, isPresented: Binding<Bool>, actions: [DSAction]) -> some View {
        confirmationDialog(title, isPresented: isPresented, titleVisibility: .visible) {
            ForEach(actions) { a in Button(a.label, role: a.isDestructive ? .destructive : nil, action: a.perform) }
            Button("Cancel", role: .cancel) {}
        }
    }

    /// detent-sheet — web: components/detent-sheet.html. Peek (size.sheet.peek), half and full, with the system drag
    /// indicator. modal = false keeps the content behind usable up to half height. Put a Close button in the content.
    func dsDetentSheet<Content: View>(isPresented: Binding<Bool>, modal: Bool = true, @ViewBuilder content: @escaping () -> Content) -> some View {
        sheet(isPresented: isPresented) {
            content()
                .presentationDetents([.height(DSDimension.sizeSheetPeek), .medium, .large])
                .presentationDragIndicator(.visible)
                .modifier(DSSheetChrome(modal: modal))
        }
    }
}

private struct DSSheetChrome: ViewModifier {
    let modal: Bool

    func body(content: Content) -> some View {
        if #available(iOS 16.4, *) {
            content
                .presentationBackground(@C(surface.raised|card))
                .presentationCornerRadius(@D(card.radius))
                .presentationBackgroundInteraction(modal ? .automatic : .enabled(upThrough: .medium))
        } else {
            content
        }
    }
}

/// swipe-pager — web: components/swipe-pager.html. Swipe between pages; the dots are buttons ("Page 2 of 4").
public struct DSPager<Page: View>: View {
    @Binding private var selection: Int
    private let count: Int
    private let page: (Int) -> Page
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    public init(selection: Binding<Int>, count: Int, @ViewBuilder page: @escaping (Int) -> Page) {
        self._selection = selection
        self.count = count
        self.page = page
    }

    public var body: some View {
        VStack(spacing: DSDimension.space1) {
            TabView(selection: $selection) {
                ForEach(0..<count, id: \.self) { i in page(i).tag(i) }
            }
            .tabViewStyle(.page(indexDisplayMode: .never))
            HStack(spacing: DSDimension.space1) {
                ForEach(0..<count, id: \.self) { i in
                    Button {
                        withAnimation(reduceMotion ? nil : .default) { selection = i }
                    } label: {
                        Circle()
                            .fill(i == selection ? @C(action.primary.bg) : @C(border.default))
                            .frame(width: DSDimension.space1 * 2, height: DSDimension.space1 * 2)
                            .frame(minWidth: DSDimension.sizeTouchTarget, minHeight: DSDimension.sizeTouchTarget)
                            .contentShape(Rectangle())
                    }
                    .buttonStyle(.plain)
                    .accessibilityLabel("Page \(i + 1) of \(count)")
                    .accessibilityAddTraits(i == selection ? .isSelected : [])
                }
            }
        }
    }
}

/// zoomable-image — web: components/zoomable-image.html. Pinch or double tap to zoom (1x–4x), drag to pan when zoomed,
/// and Zoom out / Reset / Zoom in buttons as the non-gesture path.
public struct DSZoomableImage: View {
    private let image: Image
    private let label: String
    @State private var scale: CGFloat = 1
    @State private var settledScale: CGFloat = 1
    @State private var offset: CGSize = .zero
    @State private var settledOffset: CGSize = .zero
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    public init(_ image: Image, label: String) {
        self.image = image
        self.label = label
    }

    private func zoom(_ to: CGFloat) {
        withAnimation(reduceMotion ? nil : .default) {
            scale = min(4, max(1, to))
            settledScale = scale
            if scale == 1 { offset = .zero; settledOffset = .zero }
        }
    }

    public var body: some View {
        VStack(spacing: DSDimension.space1) {
            image
                .resizable()
                .scaledToFit()
                .accessibilityLabel(label)
                .accessibilityValue("\(Int(scale * 100))%")
                .scaleEffect(scale)
                .offset(offset)
                // ponytail: pan isn't clamped to the image edges; Reset brings it back. Clamp with GeometryReader if users get lost.
                .gesture(MagnificationGesture()
                    .onChanged { scale = min(4, max(1, settledScale * $0)) }
                    .onEnded { _ in zoom(scale) })
                .simultaneousGesture(DragGesture()
                    .onChanged { v in
                        guard scale > 1 else { return }
                        offset = CGSize(width: settledOffset.width + v.translation.width, height: settledOffset.height + v.translation.height)
                    }
                    .onEnded { _ in settledOffset = offset })
                .onTapGesture(count: 2) { zoom(scale > 1 ? 1 : 2) }
                .clipped()
            HStack(spacing: DSDimension.space1) {
                Button("Zoom out") { zoom(scale - 1) }.disabled(scale <= 1)
                Button("Reset zoom") { zoom(1) }.disabled(scale == 1)
                Button("Zoom in") { zoom(scale + 1) }.disabled(scale >= 4)
            }
            .buttonStyle(DSButtonStyle(.secondary, size: .sm))
        }
    }
}
