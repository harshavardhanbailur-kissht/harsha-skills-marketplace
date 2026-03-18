# Mobile Animations Reference Guide

## Table of Contents

- [1. Animation Principles for Mobile UI](#1-animation-principles-for-mobile-ui)
- [2. iOS Animations - SwiftUI](#2-ios-animations---swiftui)
- [3. Android Animations - Compose](#3-android-animations---compose)
- [4. React Native - Reanimated 3](#4-react-native---reanimated-3)
- [5. Flutter Animations](#5-flutter-animations)
- [6. Gesture-Driven Animations](#6-gesture-driven-animations)
- [7. Spring Physics](#7-spring-physics)
- [8. Skeleton/Shimmer Loading Animations](#8-skeletenshimmer-loading-animations)
- [9. Page Transitions & Shared Element Transitions](#9-page-transitions--shared-element-transitions)
- [10. Micro-Interactions](#10-micro-interactions)
- [11. Lottie & Rive Integration](#11-lottie--rive-integration)
- [12. Performance Optimization](#12-performance-optimization)
- [13. Accessibility - prefers-reduced-motion](#13-accessibility---prefers-reduced-motion)

## 1. Animation Principles for Mobile UI

Mobile animations serve specific purposes: guide attention, provide feedback, communicate state changes, and create delightful experiences within performance constraints.

### Core Principles

**Timing**: Keep animations brief (200-500ms for micro-interactions, 300-800ms for transitions)
**Easing**: Use ease-out for exits, ease-in-out for continuous motion, bounce for playful interactions
**Meaningful Motion**: Every animation should communicate or facilitate user intent
**Performance**: Aim for consistent 60fps on low-end devices
**Accessibility**: Respect motion preferences, provide non-animated alternatives

### Easing Functions

```
Linear: constant speed (progress, duration)
Ease-in: slow start, fast end (exiting animations)
Ease-out: fast start, slow end (entering animations)
Ease-in-out: slow start and end (focused motion)
Custom curves: match brand personality
Spring: physics-based natural motion
Bounce: playful, attention-grabbing
```

---

## 2. iOS Animations - SwiftUI

### Basic withAnimation

```swift
@State private var isExpanded = false

Button("Toggle") {
    withAnimation(.easeInOut(duration: 0.3)) {
        isExpanded.toggle()
    }
}
```

### matchedGeometryEffect (Shared Element Transitions)

```swift
@State private var isExpanded = false
@Namespace private var sharedNamespace

ZStack(alignment: .topLeading) {
    if isExpanded {
        // Expanded view
        RoundedRectangle(cornerRadius: 20)
            .fill(Color.blue)
            .matchedGeometryEffect(id: "card", in: sharedNamespace)
            .frame(height: 600)
    } else {
        // Collapsed view
        RoundedRectangle(cornerRadius: 12)
            .fill(Color.blue)
            .matchedGeometryEffect(id: "card", in: sharedNamespace)
            .frame(height: 100)
    }
}
.onTapGesture {
    withAnimation(.easeInOut(duration: 0.4)) {
        isExpanded.toggle()
    }
}
```

### PhaseAnimator (Phase-Based Animation)

```swift
struct PulseAnimation: View {
    var body: some View {
        Circle()
            .fill(Color.blue)
            .frame(width: 60, height: 60)
            .phaseAnimator(
                [0, 1, 0],
                trigger: true,
                animation: .easeInOut(duration: 2)
            ) { content, phase in
                content
                    .scaleEffect(1 + phase * 0.3)
                    .opacity(1 - phase * 0.5)
            }
    }
}
```

### KeyframeAnimator (Complex Multi-Step Animations)

```swift
struct BounceAnimation: View {
    var body: some View {
        Circle()
            .fill(Color.red)
            .frame(width: 50, height: 50)
            .keyframeAnimator(
                initialValue: AnimationValue(),
                trigger: true,
                content: { content, value in
                    content
                        .offset(y: value.verticalPosition)
                        .scaleEffect(value.scale)
                },
                keyframes: { _ in
                    KeyframeTrack(\.verticalPosition) {
                        LinearKeyframe(0, duration: 0.0)
                        CubicKeyframe(-100, duration: 0.4)
                        CubicKeyframe(0, duration: 0.4)
                    }
                    KeyframeTrack(\.scale) {
                        LinearKeyframe(1.0, duration: 0.0)
                        LinearKeyframe(0.8, duration: 0.2)
                        LinearKeyframe(1.0, duration: 0.2)
                    }
                }
            )
    }
}

struct AnimationValue {
    var verticalPosition: CGFloat = 0
    var scale: CGFloat = 1.0
}
```

### Spring Animation

```swift
withAnimation(.spring(response: 0.6, dampingFraction: 0.7, blendDuration: 0.1)) {
    isAnimating = true
}

// Parameters:
// response: oscillation period (smaller = faster)
// dampingFraction: 0 = oscillates forever, 1 = no oscillation, <1 = bouncy
// blendDuration: transition smoothness
```

---

## 3. Android Animations - Compose

### Basic AnimatedVisibility

```kotlin
var isVisible by remember { mutableStateOf(false) }

Column {
    Button(onClick = { isVisible = !isVisible }) {
        Text("Toggle")
    }

    AnimatedVisibility(
        visible = isVisible,
        enter = fadeIn(animationSpec = tween(300)) + expandVertically(),
        exit = fadeOut(animationSpec = tween(300)) + shrinkVertically()
    ) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(200.dp)
                .background(Color.Blue)
        )
    }
}
```

### animate*AsState

```kotlin
val backgroundColor by animateColorAsState(
    targetValue = if (isPressed) Color.Blue else Color.Gray,
    animationSpec = tween(durationMillis = 300)
)

Box(
    modifier = Modifier
        .size(100.dp)
        .background(backgroundColor)
)
```

### AnimatedContent (State-Based Transitions)

```kotlin
var count by remember { mutableStateOf(0) }

Column {
    Button(onClick = { count++ }) {
        Text("Increment")
    }

    AnimatedContent(
        targetState = count,
        transitionSpec = {
            (slideInVertically { height -> height } + fadeIn())
                .togetherWith(slideOutVertically { height -> -height } + fadeOut())
                .using(SizeTransform(clip = false))
        }
    ) { targetCount ->
        Text(
            text = "$targetCount",
            modifier = Modifier.padding(16.dp)
        )
    }
}
```

### Shared Element Transitions

```kotlin
@OptIn(ExperimentalSharedTransitionApi::class)
@Composable
fun SharedElementExample(
    sharedTransitionScope: SharedTransitionScope,
    animatedVisibilityScope: AnimatedVisibilityScope
) {
    with(sharedTransitionScope) {
        Image(
            painter = painterResource(R.drawable.image),
            contentDescription = null,
            modifier = Modifier
                .size(100.dp)
                .sharedElement(
                    rememberSharedContentState(key = "image"),
                    animatedVisibilityScope
                )
        )
    }
}
```

### Spring Physics

```kotlin
val offset by animateFloatAsState(
    targetValue = if (isDragged) 100f else 0f,
    animationSpec = spring(
        dampingRatio = Spring.DampingRatioMediumBouncy,
        stiffness = Spring.StiffnessMedium
    )
)
```

---

## 4. React Native - Reanimated 3

### useSharedValue & useAnimatedStyle

```javascript
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
  withSpring,
} from 'react-native-reanimated';

function AnimatedButton() {
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => {
    return {
      transform: [{ scale: scale.value }],
    };
  });

  return (
    <Animated.View style={[styles.box, animatedStyle]}>
      <TouchableOpacity
        onPress={() => {
          scale.value = withSpring(1.2, {
            damping: 0.8,
            mass: 1,
            stiffness: 100,
          });
        }}
      >
        <Text>Press Me</Text>
      </TouchableOpacity>
    </Animated.View>
  );
}
```

### withSpring (Advanced Spring Physics)

```javascript
scale.value = withSpring(
  1.2,
  {
    damping: 0.8,      // 0-1: higher = less bounce
    mass: 1,           // higher = slower oscillation
    overshootClamping: false,
    restSpeedThreshold: 2,
    restDisplacementThreshold: 2,
    stiffness: 100,    // higher = faster spring
  },
  () => {
    runOnJS(onAnimationComplete)();
  }
);
```

### Gesture Handler Integration

```javascript
import { GestureHandlerRootView, PanGestureHandler } from 'react-native-gesture-handler';

function DragAnimation() {
  const translateX = useSharedValue(0);
  const translateY = useSharedValue(0);

  const gestureHandler = useAnimatedGestureHandler({
    onStart: (event, ctx) => {
      ctx.startX = translateX.value;
      ctx.startY = translateY.value;
    },
    onActive: (event, ctx) => {
      translateX.value = ctx.startX + event.translationX;
      translateY.value = ctx.startY + event.translationY;
    },
    onEnd: () => {
      translateX.value = withSpring(0);
      translateY.value = withSpring(0);
    },
  });

  const animatedStyle = useAnimatedStyle(() => {
    return {
      transform: [
        { translateX: translateX.value },
        { translateY: translateY.value },
      ],
    };
  });

  return (
    <GestureHandlerRootView>
      <PanGestureHandler onGestureEvent={gestureHandler}>
        <Animated.View style={[styles.box, animatedStyle]} />
      </PanGestureHandler>
    </GestureHandlerRootView>
  );
}
```

### Lottie Integration

```javascript
import LottieView from 'lottie-react-native';

function LottieAnimation() {
  const animationProgress = useSharedValue(0);

  return (
    <LottieView
      source={require('./animations/heart.json')}
      progress={animationProgress}
      style={{ width: 200, height: 200 }}
      loop={false}
    />
  );
}
```

---

## 5. Flutter Animations

### Implicit Animations (AnimatedContainer)

```dart
class ImplicitAnimationExample extends StatefulWidget {
  @override
  State<ImplicitAnimationExample> createState() => _ImplicitAnimationExampleState();
}

class _ImplicitAnimationExampleState extends State<ImplicitAnimationExample> {
  bool isExpanded = false;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => setState(() => isExpanded = !isExpanded),
      child: AnimatedContainer(
        duration: Duration(milliseconds: 300),
        curve: Curves.easeInOut,
        width: isExpanded ? 200 : 100,
        height: isExpanded ? 400 : 100,
        decoration: BoxDecoration(
          color: isExpanded ? Colors.blue : Colors.gray,
          borderRadius: BorderRadius.circular(isExpanded ? 20 : 8),
        ),
      ),
    );
  }
}
```

### Explicit Animations (AnimationController)

```dart
class ExplicitAnimationExample extends StatefulWidget {
  @override
  State<ExplicitAnimationExample> createState() => _ExplicitAnimationExampleState();
}

class _ExplicitAnimationExampleState extends State<ExplicitAnimationExample>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _rotateAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: Duration(milliseconds: 800),
      vsync: this,
    );

    _scaleAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.elasticOut),
    );

    _rotateAnimation = Tween<double>(begin: 0.0, end: 2 * pi).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );

    _controller.forward();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Transform.scale(
          scale: _scaleAnimation.value,
          child: Transform.rotate(
            angle: _rotateAnimation.value,
            child: Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                color: Colors.blue,
                borderRadius: BorderRadius.circular(50),
              ),
            ),
          ),
        );
      },
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}
```

### Hero Animation (Shared Element)

```dart
class HeroAnimationExample extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        GestureDetector(
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => DetailPage()),
            );
          },
          child: Hero(
            tag: 'imageHero',
            child: Container(
              width: 100,
              height: 100,
              color: Colors.blue,
            ),
          ),
        ),
      ],
    );
  }
}

class DetailPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Hero(
          tag: 'imageHero',
          child: Container(
            width: 300,
            height: 400,
            color: Colors.blue,
          ),
        ),
      ),
    );
  }
}
```

### Staggered Animations

```dart
class StaggeredAnimationExample extends StatefulWidget {
  @override
  State<StaggeredAnimationExample> createState() =>
      _StaggeredAnimationExampleState();
}

class _StaggeredAnimationExampleState extends State<StaggeredAnimationExample>
    with TickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: Duration(milliseconds: 1500),
      vsync: this,
    )..repeat();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: List.generate(3, (index) {
        final delayedAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
          CurvedAnimation(
            parent: _controller,
            curve: Interval(
              index * 0.2,
              (index + 1) * 0.2 + 0.3,
              curve: Curves.easeInOut,
            ),
          ),
        );

        return AnimatedBuilder(
          animation: delayedAnimation,
          builder: (context, child) {
            return Opacity(
              opacity: delayedAnimation.value,
              child: Transform.translate(
                offset: Offset(0, -20 * delayedAnimation.value),
                child: Container(
                  width: 100,
                  height: 50,
                  margin: EdgeInsets.all(8),
                  color: Colors.blue,
                ),
              ),
            );
          },
        );
      }),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}
```

---

## 6. Gesture-Driven Animations

### Drag Gesture (Multi-Platform)

**SwiftUI**:
```swift
@State private var dragOffset = CGSize.zero

var body: some View {
    Circle()
        .fill(Color.blue)
        .frame(width: 80, height: 80)
        .offset(dragOffset)
        .gesture(
            DragGesture()
                .onChanged { value in
                    dragOffset = value.translation
                }
                .onEnded { _ in
                    withAnimation(.spring()) {
                        dragOffset = .zero
                    }
                }
        )
}
```

**Flutter**:
```dart
class DragAnimationExample extends StatefulWidget {
  @override
  State<DragAnimationExample> createState() => _DragAnimationExampleState();
}

class _DragAnimationExampleState extends State<DragAnimationExample> {
  Offset position = Offset.zero;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onPanUpdate: (details) {
        setState(() {
          position += details.delta;
        });
      },
      onPanEnd: (details) {
        // Snap back animation
        // Use AnimationController for smooth return
      },
      child: Transform.translate(
        offset: position,
        child: Container(
          width: 80,
          height: 80,
          decoration: BoxDecoration(
            color: Colors.blue,
            shape: BoxShape.circle,
          ),
        ),
      ),
    );
  }
}
```

### Swipe Gesture

```swift
// SwiftUI
var body: some View {
    ZStack {
        if currentIndex < items.count {
            CardView(item: items[currentIndex])
                .gesture(
                    DragGesture()
                        .onEnded { value in
                            if value.translation.width < -50 {
                                // Swiped left
                                withAnimation(.easeInOut(duration: 0.3)) {
                                    currentIndex += 1
                                }
                            } else if value.translation.width > 50 {
                                // Swiped right
                                withAnimation(.easeInOut(duration: 0.3)) {
                                    currentIndex -= 1
                                }
                            }
                        }
                )
        }
    }
}
```

### Pinch Gesture

```swift
@State private var scale: CGFloat = 1.0

var body: some View {
    Image(systemName: "photo")
        .scaleEffect(scale)
        .gesture(
            MagnificationGesture()
                .onChanged { value in
                    scale = value
                }
                .onEnded { value in
                    withAnimation(.spring()) {
                        scale = 1.0
                    }
                }
        )
}
```

---

## 7. Spring Physics

Spring animations use physics-based parameters for natural motion:

```
damping (0-1):
  0 = oscillates forever
  <1 = bouncy with decreasing oscillation
  1 = critically damped (no overshoot)
  >1 = overdamped (sluggish)

stiffness (>0):
  higher = faster response, more oscillation
  lower = slower, less bouncy

mass (>0):
  higher = slower to accelerate
  lower = quicker response

Recommended combinations:
  Bouncy: dampingFraction: 0.5-0.6, stiffness: 100+
  Natural: dampingFraction: 0.8-0.9, stiffness: 100-150
  Smooth: dampingFraction: 1.0+, stiffness: 80-100
```

**Formula**: `frequency = sqrt(stiffness / mass) / (2 * π)`

---

## 8. Skeleton/Shimmer Loading Animations

### SwiftUI Skeleton

```swift
struct SkeletonLoadingView: View {
    @State private var isShimmering = false

    var body: some View {
        VStack(spacing: 16) {
            SkeletonView()
                .frame(height: 100)
            SkeletonView()
                .frame(height: 60)
            SkeletonView()
                .frame(height: 60)
        }
        .onAppear {
            withAnimation(.easeInOut(duration: 1.5).repeatForever(autoreverses: true)) {
                isShimmering = true
            }
        }
    }
}

struct SkeletonView: View {
    @State private var isShimmering = false

    var body: some View {
        RoundedRectangle(cornerRadius: 8)
            .fill(Color.gray.opacity(0.3))
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .fill(
                        LinearGradient(
                            gradient: Gradient(stops: [
                                .init(color: .clear, location: 0),
                                .init(color: .white.opacity(0.3), location: 0.5),
                                .init(color: .clear, location: 1),
                            ]),
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .offset(x: isShimmering ? 400 : -400)
            )
            .onAppear {
                withAnimation(.easeInOut(duration: 1.5).repeatForever(autoreverses: false)) {
                    isShimmering = true
                }
            }
    }
}
```

### Compose Shimmer

```kotlin
@Composable
fun ShimmerLoading() {
    val shimmerColors = listOf(
        Color.LightGray.copy(alpha = 0.6f),
        Color.LightGray.copy(alpha = 0.2f),
        Color.LightGray.copy(alpha = 0.6f),
    )

    val transition = rememberInfiniteTransition(label = "shimmer")
    val shimmerX by transition.animateFloat(
        initialValue = -1000f,
        targetValue = 1000f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 1500),
            repeatMode = RepeatMode.Restart
        ),
        label = "shimmerX"
    )

    val brush = Brush.linearGradient(
        colors = shimmerColors,
        start = Offset(shimmerX, 0f),
        end = Offset(shimmerX + 500f, 0f)
    )

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(100.dp)
            .background(brush)
    )
}
```

---

## 9. Page Transitions & Shared Element Transitions

### iOS Navigation Transition

```swift
struct NavigationTransitionExample: View {
    @State private var showDetail = false

    var body: some View {
        NavigationStack {
            VStack {
                Button("Show Detail") {
                    withAnimation(.easeInOut(duration: 0.4)) {
                        showDetail = true
                    }
                }
            }
            .navigationDestination(isPresented: $showDetail) {
                DetailView()
                    .transition(.asymmetric(
                        insertion: .move(edge: .trailing).combined(with: .opacity),
                        removal: .move(edge: .trailing).combined(with: .opacity)
                    ))
            }
        }
    }
}
```

### Android Compose Transitions

```kotlin
@Composable
fun TransitionExample(navController: NavController) {
    NavHost(navController, startDestination = "list") {
        composable("list") {
            ListScreen(
                onNavigate = { navController.navigate("detail") }
            )
        }
        composable(
            "detail",
            enterTransition = {
                slideIntoContainer(
                    AnimatedContentTransitionScope.SlideDirection.Start,
                    animationSpec = tween(300)
                )
            },
            exitTransition = {
                slideOutOfContainer(
                    AnimatedContentTransitionScope.SlideDirection.End,
                    animationSpec = tween(300)
                )
            }
        ) {
            DetailScreen()
        }
    }
}
```

---

## 10. Micro-Interactions

### Button Feedback (Press Animation)

**SwiftUI**:
```swift
struct PressableButton: View {
    @State private var isPressed = false

    var body: some View {
        Button(action: {}) {
            Text("Press Me")
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(8)
        }
        .scaleEffect(isPressed ? 0.95 : 1.0)
        .brightness(isPressed ? -0.1 : 0)
        .gesture(
            DragGesture(minimumDistance: 0)
                .onChanged { _ in
                    withAnimation(.easeInOut(duration: 0.1)) {
                        isPressed = true
                    }
                }
                .onEnded { _ in
                    withAnimation(.easeInOut(duration: 0.1)) {
                        isPressed = false
                    }
                }
        )
    }
}
```

### Toggle Animation

```kotlin
@Composable
fun AnimatedToggle(
    checked: Boolean,
    onCheckedChange: (Boolean) -> Unit
) {
    val backgroundColor by animateColorAsState(
        targetValue = if (checked) Color.Green else Color.Gray,
        animationSpec = tween(300)
    )

    val offset by animateFloatAsState(
        targetValue = if (checked) 28f else 4f,
        animationSpec = tween(300)
    )

    Surface(
        modifier = Modifier
            .width(60.dp)
            .height(30.dp)
            .clip(RoundedCornerShape(15.dp))
            .background(backgroundColor)
            .clickable { onCheckedChange(!checked) },
        color = backgroundColor
    ) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(2.dp),
            contentAlignment = Alignment.CenterStart
        ) {
            Surface(
                modifier = Modifier
                    .offset(x = offset.dp)
                    .size(24.dp)
                    .clip(RoundedCornerShape(12.dp)),
                color = Color.White
            ) {}
        }
    }
}
```

### Pull-to-Refresh

```swift
struct PullToRefreshExample: View {
    @State private var isRefreshing = false

    var body: some View {
        List(items) { item in
            Text(item.title)
        }
        .refreshable {
            isRefreshing = true
            try await Task.sleep(nanoseconds: 1_000_000_000)
            // Fetch new data
            isRefreshing = false
        }
    }
}
```

---

## 11. Lottie & Rive Integration

### React Native Lottie

```javascript
import LottieView from 'lottie-react-native';

function LottieExample() {
  const animationProgress = useSharedValue(0);

  return (
    <LottieView
      source={require('./animations/loading.json')}
      autoPlay
      loop
      style={{ width: 200, height: 200 }}
    />
  );
}
```

### Flutter Lottie

```dart
import 'package:lottie/lottie.dart';

class LottieAnimationExample extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Lottie.asset(
      'assets/animations/loading.json',
      width: 200,
      height: 200,
      fit: BoxFit.contain,
    );
  }
}
```

### SwiftUI with Lottie

```swift
import Lottie

struct LottieView: UIViewRepresentable {
    let name: String

    func makeUIView(context: UIViewRepresentableContext<LottieView>) -> UIView {
        let view = UIView()
        let animationView = LottieAnimationView(name: name)
        animationView.loopMode = .loop
        animationView.play()
        view.addSubview(animationView)
        animationView.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            animationView.widthAnchor.constraint(equalTo: view.widthAnchor),
            animationView.heightAnchor.constraint(equalTo: view.heightAnchor),
        ])
        return view
    }

    func updateUIView(_ uiView: UIView, context: UIViewRepresentableContext<LottieView>) {}
}
```

---

## 12. Performance Optimization

### 60fps Target

- Keep animations under 500ms when possible
- Use GPU-accelerated properties: transform, opacity
- Avoid animating: layout, size, position (use transform instead)
- Profile with DevTools, Instruments, or Android Profiler

### Reduced Motion (Accessibility)

**SwiftUI**:
```swift
@Environment(\.accessibilityReduceMotion) var reduceMotion

withAnimation(reduceMotion ? nil : .easeInOut(duration: 0.3)) {
    isExpanded.toggle()
}
```

**Compose**:
```kotlin
@Composable
fun AccessibleAnimation() {
    val motionDuration = if (isSystemAnimationEnabled()) 300 else 0

    val offset by animateFloatAsState(
        targetValue = 100f,
        animationSpec = tween(motionDuration)
    )
}

fun isSystemAnimationEnabled(): Boolean {
    return Settings.Global.getFloat(
        contentResolver,
        Settings.Global.ANIMATOR_DURATION_SCALE,
        1f
    ) != 0f
}
```

**React Native**:
```javascript
import { AccessibilityInfo } from 'react-native';

const duration = reduceMotionEnabled ? 0 : 300;
```

### Rendering Optimization

- Use `shouldRasterize` sparingly in SwiftUI
- Implement `key` prop correctly in React Native animations
- Use `repaint` boundaries in Flutter for complex animated trees
- Profile GPU memory usage

---

## 13. Accessibility - prefers-reduced-motion

Web/React compliance:

```css
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

Cross-platform strategy:

1. **Detect preference** at app startup
2. **Disable non-essential animations** (decorative motion)
3. **Preserve essential feedback** (button press, state change)
4. **Test with accessibility tools** on each platform

---

## Best Practices Summary

✓ Keep timing 200-800ms
✓ Use easing that matches intent
✓ Respect accessibility preferences
✓ Animate GPU-accelerated properties
✓ Test performance on low-end devices
✓ Provide non-animated fallbacks
✓ Use springs for natural feel
✓ Limit simultaneous animations
✓ Document animation parameters
✓ Profile before shipping
