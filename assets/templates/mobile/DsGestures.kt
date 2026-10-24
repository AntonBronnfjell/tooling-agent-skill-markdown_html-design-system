// @HEAD
// Mobile scope: gesture components on the platform built-ins, styled with tokens. Web spec: references/components/mobile.md.
// Every gesture also has a non-drag path: long press + TalkBack actions for rows, buttons for sheets, pages and zoom.
// No wrapper needed: collapsing-app-bar = LargeTopAppBar + TopAppBarDefaults.exitUntilCollapsedScrollBehavior().
package @PKG

import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.gestures.rememberTransformableState
import androidx.compose.foundation.gestures.transformable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.defaultMinSize
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicText
import androidx.compose.material3.BottomSheetDefaults
import androidx.compose.material3.BottomSheetScaffold
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.SwipeToDismissBox
import androidx.compose.material3.SwipeToDismissBoxValue
import androidx.compose.material3.pulltorefresh.PullToRefreshBox
import androidx.compose.material3.pulltorefresh.PullToRefreshDefaults
import androidx.compose.material3.pulltorefresh.rememberPullToRefreshState
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.material3.rememberSwipeToDismissBoxState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clipToBounds
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.semantics.CustomAccessibilityAction
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.customActions
import androidx.compose.ui.semantics.selected
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.semantics.stateDescription
import androidx.compose.ui.unit.dp
import kotlinx.coroutines.launch

/** One action of a swipe row or an action sheet. */
data class DsAction(val label: String, val destructive: Boolean = false, val onClick: () -> Unit)

/**
 * swipe-actions — web: components/swipe-actions.html. Swipe end→start runs the first trailing action, start→end the
 * leading one; the row snaps back. Long press opens every action in [DsActionSheet], and they're TalkBack actions too.
 */
@OptIn(ExperimentalMaterial3Api::class, ExperimentalFoundationApi::class)
@Composable
fun DsSwipeActionsRow(
    trailing: List<DsAction>,
    modifier: Modifier = Modifier,
    leading: DsAction? = null,
    onClick: () -> Unit = {},
    content: @Composable () -> Unit,
) {
    val state = rememberSwipeToDismissBoxState()
    var menuOpen by remember { mutableStateOf(false) }
    val all = listOfNotNull(leading) + trailing
    LaunchedEffect(state.currentValue) {
        when (state.currentValue) {
            SwipeToDismissBoxValue.EndToStart -> trailing.firstOrNull()?.onClick?.invoke()
            SwipeToDismissBoxValue.StartToEnd -> leading?.onClick?.invoke()
            SwipeToDismissBoxValue.Settled -> return@LaunchedEffect
        }
        state.reset()
    }
    SwipeToDismissBox(
        state = state,
        modifier = modifier.semantics { customActions = all.map { a -> CustomAccessibilityAction(a.label) { a.onClick(); true } } },
        enableDismissFromStartToEnd = leading != null,
        enableDismissFromEndToStart = trailing.isNotEmpty(),
        backgroundContent = {
            val toStart = state.dismissDirection == SwipeToDismissBoxValue.EndToStart
            DsSwipeBackground(if (toStart) trailing.firstOrNull() else leading, toStart)
        },
    ) {
        Box(Modifier.fillMaxWidth().background(@C(surface.raised|card)).combinedClickable(onClick = onClick, onLongClick = { menuOpen = true })) {
            content()
        }
    }
    if (menuOpen) DsActionSheet(title = null, actions = all, onDismiss = { menuOpen = false })
}

/** What a swipe reveals: the action's color and label filling the row (web: swipe-actions state:full-swipe). */
@Composable
fun DsSwipeBackground(action: DsAction?, toStart: Boolean, modifier: Modifier = Modifier) {
    Box(
        modifier
            .fillMaxSize()
            .background(if (action?.destructive == true) @C(action.danger.bg) else @C(action.primary.bg))
            .padding(horizontal = (DsDimension.space1 * 4).dp),
        contentAlignment = if (toStart) Alignment.CenterEnd else Alignment.CenterStart,
    ) {
        if (action != null) BasicText(action.label, style = @T(body).copy(color = if (action.destructive) @C(action.danger.fg) else @C(action.primary.fg)))
    }
}

/** pull-to-refresh — web: components/pull-to-refresh.html. Also offer a Refresh button in the top bar. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DsPullToRefresh(isRefreshing: Boolean, onRefresh: () -> Unit, modifier: Modifier = Modifier, content: @Composable () -> Unit) {
    val state = rememberPullToRefreshState()
    PullToRefreshBox(
        isRefreshing = isRefreshing,
        onRefresh = onRefresh,
        modifier = modifier,
        state = state,
        indicator = {
            PullToRefreshDefaults.Indicator(
                state = state,
                isRefreshing = isRefreshing,
                modifier = Modifier.align(Alignment.TopCenter),
                containerColor = @C(surface.raised|card),
                color = @C(action.primary.bg),
            )
        },
    ) { content() }
}

/** action-sheet — web: components/action-sheet.html. Cancel is added; nothing destructive is pre-selected. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DsActionSheet(title: String?, actions: List<DsAction>, onDismiss: () -> Unit) {
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        containerColor = @C(surface.raised|card),
        shape = RoundedCornerShape(topStart = @D(card.radius).dp, topEnd = @D(card.radius).dp),
        dragHandle = { BottomSheetDefaults.DragHandle(color = @C(border.default)) },
    ) { DsActionList(title, actions, onDismiss) }
}

/** The action sheet's content: optional title, the actions, then Cancel. Each row closes the sheet, then acts. */
@Composable
fun DsActionList(title: String?, actions: List<DsAction>, onDismiss: () -> Unit, modifier: Modifier = Modifier) {
    Column(modifier.fillMaxWidth().padding(bottom = (DsDimension.space1 * 4).dp)) {
        if (title != null) {
            BasicText(title, Modifier.padding(horizontal = (DsDimension.space1 * 4).dp), style = @T(small).copy(color = @C(text.muted)))
        }
        (actions + DsAction("Cancel") {}).forEach { a ->
            Box(
                Modifier
                    .fillMaxWidth()
                    .defaultMinSize(minHeight = DsDimension.androidTouchTarget.dp)
                    .clickable { onDismiss(); a.onClick() }
                    .padding(horizontal = (DsDimension.space1 * 4).dp),
                contentAlignment = Alignment.CenterStart,
            ) {
                BasicText(a.label, style = @T(body).copy(color = if (a.destructive) @C(feedback.danger.fg) else @C(text.default)))
            }
        }
    }
}

/**
 * detent-sheet — web: components/detent-sheet.html. modal = true: ModalBottomSheet (half and full, swipe down closes);
 * modal = false: BottomSheetScaffold peeking at size.sheet.peek over [content]. Put a Close button in [sheet].
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DsDetentSheet(
    modal: Boolean,
    onDismiss: () -> Unit,
    sheet: @Composable () -> Unit,
    content: @Composable (PaddingValues) -> Unit = {},
) {
    val shape = RoundedCornerShape(topStart = @D(card.radius).dp, topEnd = @D(card.radius).dp)
    val handle = @Composable { BottomSheetDefaults.DragHandle(color = @C(border.default)) }
    if (modal) {
        ModalBottomSheet(
            onDismissRequest = onDismiss,
            sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = false),
            shape = shape,
            containerColor = @C(surface.raised|card),
            dragHandle = handle,
        ) { sheet() }
    } else {
        BottomSheetScaffold(
            sheetContent = { sheet() },
            sheetPeekHeight = DsDimension.sizeSheetPeek.dp,
            sheetShape = shape,
            sheetContainerColor = @C(surface.raised|card),
            sheetDragHandle = handle,
            content = content,
        )
    }
}

/** swipe-pager — web: components/swipe-pager.html. Swipe between pages; the dots are buttons ("Page 2 of 4"). */
@Composable
fun DsPager(count: Int, modifier: Modifier = Modifier, page: @Composable (Int) -> Unit) {
    val state = rememberPagerState(pageCount = { count })
    val scope = rememberCoroutineScope()
    Column(modifier) {
        HorizontalPager(state = state, modifier = Modifier.weight(1f)) { page(it) }
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center) {
            repeat(count) { i ->
                Box(
                    Modifier
                        .defaultMinSize(DsDimension.androidTouchTarget.dp, DsDimension.androidTouchTarget.dp)
                        .clickable { scope.launch { state.animateScrollToPage(i) } }
                        .semantics { contentDescription = "Page ${i + 1} of $count"; selected = state.currentPage == i },
                    contentAlignment = Alignment.Center,
                ) {
                    Box(
                        Modifier
                            .size((DsDimension.space1 * 2).dp)
                            .background(if (state.currentPage == i) @C(action.primary.bg) else @C(border.default), CircleShape),
                    )
                }
            }
        }
    }
}

/**
 * zoomable-image — web: components/zoomable-image.html. Pinch or double tap to zoom (1x–4x), drag to pan when zoomed,
 * and Zoom out / Reset / Zoom in buttons as the non-gesture path. [image] draws the picture (Image, AsyncImage, ...).
 */
@Composable
fun DsZoomableImage(label: String, modifier: Modifier = Modifier, image: @Composable () -> Unit) {
    var scale by remember { mutableFloatStateOf(1f) }
    var offset by remember { mutableStateOf(Offset.Zero) }
    fun zoom(to: Float) {
        scale = to.coerceIn(1f, 4f)
        if (scale == 1f) offset = Offset.Zero
    }
    // ponytail: pan isn't clamped to the image edges; Reset brings it back. Clamp with the layout size if users get lost.
    val transform = rememberTransformableState { zoomChange, panChange, _ ->
        zoom(scale * zoomChange)
        if (scale > 1f) offset += panChange
    }
    Column(modifier, verticalArrangement = Arrangement.spacedBy(DsDimension.space1.dp)) {
        Box(
            Modifier
                .fillMaxWidth()
                .clipToBounds()
                .semantics { contentDescription = label; stateDescription = "${(scale * 100).toInt()}%" }
                .pointerInput(Unit) { detectTapGestures(onDoubleTap = { zoom(if (scale > 1f) 1f else 2f) }) }
                .transformable(transform)
                .graphicsLayer(scaleX = scale, scaleY = scale, translationX = offset.x, translationY = offset.y),
        ) { image() }
        Row(horizontalArrangement = Arrangement.spacedBy(DsDimension.space1.dp)) {
            DsButton("Zoom out", onClick = { zoom(scale - 1f) }, variant = DsButtonVariant.Secondary, size = DsControlSize.Sm, enabled = scale > 1f)
            DsButton("Reset zoom", onClick = { zoom(1f) }, variant = DsButtonVariant.Secondary, size = DsControlSize.Sm, enabled = scale > 1f)
            DsButton("Zoom in", onClick = { zoom(scale + 1f) }, variant = DsButtonVariant.Secondary, size = DsControlSize.Sm, enabled = scale < 4f)
        }
    }
}
