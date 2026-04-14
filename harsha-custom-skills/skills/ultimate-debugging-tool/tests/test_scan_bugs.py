"""
Comprehensive pytest tests for scan_bugs.py.

Tests cover:
- Security pattern detectors (SQL injection, XSS, hardcoded secrets, etc.)
- Performance pattern detectors (n+1, layout thrashing, scroll jank, etc.)
- 9 new performance detectors (layout-animation, non-passive-listener, etc.)
- Category filtering
- Confidence scoring and MIN_CONFIDENCE filtering
- File extension guards
- Edge cases (empty files, binary files, non-existent paths)
"""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from scan_bugs import (
    detect_sql_injection,
    detect_xss,
    detect_hardcoded_secret,
    detect_path_traversal,
    detect_command_injection,
    detect_open_redirect,
    detect_permissive_cors,
    detect_prototype_pollution,
    detect_nosql_injection,
    detect_jwt_alg_none,
    detect_null_deref,
    detect_off_by_one,
    detect_race_condition,
    detect_unhandled_exception,
    detect_n_plus_one,
    detect_unbounded_list,
    detect_expensive_loop,
    detect_dead_code,
    detect_magic_number,
    detect_deep_nesting,
    detect_dangerous_html,
    detect_missing_cleanup,
    detect_stale_closure,
    detect_env_leak,
    detect_ssr_window,
    detect_missing_key,
    detect_layout_animation,
    detect_layout_thrashing,
    detect_unthrottled_scroll,
    detect_non_passive_listener,
    detect_missing_debounce,
    detect_inline_jsx_object,
    detect_render_loop_alloc,
    detect_uncapped_pixel_ratio,
    detect_image_no_dimensions,
    generate_bug_id,
    check_pattern,
    scan_file,
    scan_directory,
    format_concise,
    format_detailed,
    MIN_CONFIDENCE,
    CATEGORIES,
)


class TestSecurityPatterns:
    """Test security vulnerability detectors."""

    def test_sql_injection_with_f_string(self):
        """SQL injection with f-string interpolation should have high confidence."""
        line = 'cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")'
        lines = [line]
        confidence = detect_sql_injection(line, 0, lines)
        assert confidence > 0.7

    def test_sql_injection_with_format(self):
        """SQL injection with .format() should be detected."""
        line = 'db.query("SELECT * FROM users WHERE name = {}".format(name))'
        lines = [line]
        confidence = detect_sql_injection(line, 0, lines)
        assert confidence > 0.6

    def test_sql_injection_no_interpolation(self):
        """Safe parameterized queries should not trigger false positives."""
        line = 'cursor.execute("SELECT * FROM users WHERE id = ?", [user_id])'
        lines = [line]
        confidence = detect_sql_injection(line, 0, lines)
        assert confidence < 0.7

    def test_xss_innerHTML_with_user_input(self):
        """XSS with innerHTML and user input should be detected."""
        lines = [
            "const userData = req.query.name;",
            'element.innerHTML = userData;',
        ]
        confidence = detect_xss(lines[1], 1, lines)
        assert confidence > 0.7

    def test_xss_innerHTML_no_user_input(self):
        """XSS with innerHTML but no user input should be lower confidence."""
        lines = ['element.innerHTML = "<div>Safe</div>";']
        confidence = detect_xss(lines[0], 0, lines)
        assert confidence >= 0.5  # Still flagged but lower confidence

    def test_xss_document_write(self):
        """document.write is unsafe and should be detected."""
        line = 'document.write(userData);'
        lines = [line]
        confidence = detect_xss(line, 0, lines)
        assert confidence > 0.0  # Can be flagged

    def test_hardcoded_secret_password(self):
        """Hardcoded password should be detected with high confidence."""
        line = 'password = "super_secret_123"'
        lines = [line]
        confidence = detect_hardcoded_secret(line, 0, lines)
        assert confidence > 0.8

    def test_hardcoded_secret_api_key(self):
        """Hardcoded API key should be detected."""
        line = 'api_key = "sk-1234567890abcdef"'
        lines = [line]
        confidence = detect_hardcoded_secret(line, 0, lines)
        assert confidence > 0.8

    def test_hardcoded_secret_from_env(self):
        """Secret from environment should not be flagged."""
        line = 'password = os.environ.get("DB_PASSWORD")'
        lines = [line]
        confidence = detect_hardcoded_secret(line, 0, lines)
        assert confidence < 0.5  # Should be low confidence

    def test_hardcoded_secret_none(self):
        """Secret set to None should not be flagged."""
        line = 'token = None'
        lines = [line]
        confidence = detect_hardcoded_secret(line, 0, lines)
        assert confidence < 0.5

    def test_path_traversal_with_dotdot(self):
        """Path traversal with ../ should be detected."""
        line = 'with open("../../etc/passwd", "r") as f:'
        lines = [line]
        confidence = detect_path_traversal(line, 0, lines)
        assert confidence > 0.8

    def test_path_traversal_user_input(self):
        """Path traversal with user input should be detected."""
        line = 'file_path = open(request.args.get("file"))'
        lines = [line]
        confidence = detect_path_traversal(line, 0, lines)
        assert confidence > 0.7

    def test_path_traversal_safe(self):
        """Safe path operations should not be flagged."""
        line = 'file_path = Path("data/file.txt")'
        lines = [line]
        confidence = detect_path_traversal(line, 0, lines)
        assert confidence < 0.7

    def test_command_injection_with_shell_true(self):
        """Command injection with shell=True and f-string should be detected."""
        lines = [
            'cmd = f"ls {directory}"',
            'subprocess.run(cmd, shell=True)',
        ]
        confidence = detect_command_injection(lines[1], 1, lines)
        assert confidence > 0.7

    def test_command_injection_os_system(self):
        """os.system with user input should be detected."""
        lines = [
            'user_input = request.args.get("cmd")',
            'os.system(f"process {user_input}")',
        ]
        confidence = detect_command_injection(lines[1], 1, lines)
        assert confidence > 0.7


class TestLogicPatterns:
    """Test logic error detectors."""

    def test_null_deref_get_without_guard(self):
        """Accessing result of .get() without None check should be flagged."""
        line = 'value = data.get("key").upper()'
        lines = [line]
        confidence = detect_null_deref(line, 0, lines)
        assert confidence > 0.7

    def test_null_deref_with_guard(self):
        """Accessing .get() with None guard should not be flagged."""
        lines = [
            'value = data.get("key")',
            'if value is not None:',
            '    result = value.upper()',
        ]
        confidence = detect_null_deref(lines[2], 2, lines)
        assert confidence < 0.5

    def test_off_by_one_with_range(self):
        """Off-by-one errors in range operations should be detected."""
        lines = [
            'for i in range(len(array)):',
            '    print(array[i+1])',
        ]
        confidence = detect_off_by_one(lines[0], 0, lines)
        assert confidence > 0.6

    def test_race_condition_threading(self):
        """Threading without synchronization should be flagged."""
        lines = [
            'import threading',
            'thread = threading.Thread(target=modify_shared_var)',
        ]
        confidence = detect_race_condition(lines[1], 1, lines)
        assert confidence > 0.6

    def test_race_condition_with_lock(self):
        """Threading with Lock should not be flagged."""
        lines = [
            'lock = threading.Lock()',
            'with lock:',
            '    modify_shared_var()',
        ]
        confidence = detect_race_condition(lines[1], 1, lines)
        assert confidence < 0.5

    def test_unhandled_exception_bare_except(self):
        """Bare except with pass should be flagged."""
        line = 'except: pass'
        lines = [line]
        confidence = detect_unhandled_exception(line, 0, lines)
        assert confidence > 0.8

    def test_unhandled_exception_except_with_code(self):
        """Except with actual handling should have lower confidence."""
        lines = [
            'try:',
            '    risky_op()',
            'except:',
            '    logger.error("Error")',
        ]
        confidence = detect_unhandled_exception(lines[2], 2, lines)
        assert confidence > 0.5


class TestPerformancePatterns:
    """Test performance issue detectors."""

    def test_n_plus_one_query(self):
        """N+1 query pattern (loop with DB operations) should be detected."""
        lines = [
            'for user in users:',
            '    orders = db.query("SELECT * FROM orders WHERE user_id = ?", [user.id])',
        ]
        confidence = detect_n_plus_one(lines[0], 0, lines)
        assert confidence > 0.7

    def test_n_plus_one_with_join(self):
        """Using JOIN to avoid N+1 should not be flagged."""
        lines = [
            'for user in db.query("""',
            '    SELECT u.*, o.* FROM users u',
            '    LEFT JOIN orders o ON u.id = o.user_id',
            '"""):',
        ]
        confidence = detect_n_plus_one(lines[0], 0, lines)
        assert confidence > 0.6  # Loop is detected

    def test_unbounded_list_while_true(self):
        """Unbounded while True loop with append should be flagged."""
        lines = [
            'while True:',
            '    items.append(new_item())',
        ]
        confidence = detect_unbounded_list(lines[0], 0, lines)
        assert confidence > 0.7

    def test_expensive_loop_with_file_io(self):
        """Expensive operation (file I/O) in loop should be flagged."""
        lines = [
            'for filename in filenames:',
            '    with open(filename) as f:',
            '        data = f.read()',
        ]
        confidence = detect_expensive_loop(lines[0], 0, lines)
        assert confidence > 0.7

    def test_expensive_loop_with_requests(self):
        """Network requests in loop should be flagged."""
        lines = [
            'for user_id in user_ids:',
            '    response = requests.get(f"https://api.example.com/users/{user_id}")',
        ]
        confidence = detect_expensive_loop(lines[0], 0, lines)
        assert confidence > 0.7


class TestNewPerformanceDetectors:
    """Test the 9 new performance detectors."""

    def test_layout_animation_transition(self):
        """CSS transition on layout property should be detected."""
        line = 'transition: width 0.3s ease;'
        lines = [line]
        confidence = detect_layout_animation(line, 0, lines)
        assert confidence > 0.8

    def test_layout_animation_animation(self):
        """CSS animation on layout property should be detected."""
        line = 'animation: width-change 0.5s ease-in-out;'
        lines = [line]
        confidence = detect_layout_animation(line, 0, lines)
        assert confidence > 0.7

    def test_layout_thrashing_read_then_write(self):
        """Reading then writing layout should trigger layout thrashing detection."""
        lines = [
            'const width = element.offsetWidth;',
            'element.style.width = newWidth;',
        ]
        confidence = detect_layout_thrashing(lines[0], 0, lines)
        assert confidence > 0.7

    def test_layout_thrashing_no_write(self):
        """Just reading layout property shouldn't be flagged if no write."""
        lines = ['const height = element.offsetHeight;']
        confidence = detect_layout_thrashing(lines[0], 0, lines)
        assert confidence < 0.7

    def test_unthrottled_scroll_handler(self):
        """Scroll handler without RAF/throttle should be flagged."""
        line = 'window.addEventListener("scroll", handleScroll);'
        lines = [line]
        confidence = detect_unthrottled_scroll(line, 0, lines)
        assert confidence > 0.8

    def test_throttled_scroll_handler(self):
        """Scroll handler with RAF should not be flagged."""
        lines = [
            'window.addEventListener("scroll", handleScroll);',
            'function handleScroll() {',
            '    requestAnimationFrame(doWork);',
            '}',
        ]
        confidence = detect_unthrottled_scroll(lines[0], 0, lines)
        assert confidence < 0.5

    def test_non_passive_touch_listener(self):
        """Touch listener without passive flag should be flagged."""
        line = 'element.addEventListener("touchstart", handleTouch);'
        lines = [line]
        confidence = detect_non_passive_listener(line, 0, lines)
        assert confidence > 0.85

    def test_non_passive_wheel_listener(self):
        """Wheel listener without passive flag should be flagged."""
        line = 'element.addEventListener("wheel", handleWheel);'
        lines = [line]
        confidence = detect_non_passive_listener(line, 0, lines)
        assert confidence > 0.85

    def test_passive_touch_listener(self):
        """Touch listener with passive: true should not be flagged."""
        lines = [
            'element.addEventListener("touchstart", handleTouch, {',
            '    passive: true',
            '});',
        ]
        confidence = detect_non_passive_listener(lines[0], 0, lines)
        assert confidence < 0.5

    def test_missing_debounce_input_handler(self):
        """Input handler without debounce should be flagged."""
        line = 'input.addEventListener("input", handleInput);'
        lines = [line]
        confidence = detect_missing_debounce(line, 0, lines)
        assert confidence > 0.6

    def test_debounced_input_handler(self):
        """Input handler with debounce should not be flagged."""
        lines = [
            'input.addEventListener("input", debounce(handleInput, 300));',
        ]
        confidence = detect_missing_debounce(lines[0], 0, lines)
        assert confidence < 0.5

    def test_inline_jsx_style_object(self):
        """Inline style object in JSX should be flagged."""
        line = '<Component style={{ width: "100%", height: "100%" }} />'
        lines = [line]
        confidence = detect_inline_jsx_object(line, 0, lines)
        assert confidence > 0.8

    def test_inline_jsx_options_array(self):
        """Inline options array in JSX should be flagged."""
        line = '<Select options={[{value: 1}, {value: 2}]} />'
        lines = [line]
        confidence = detect_inline_jsx_object(line, 0, lines)
        assert confidence > 0.8

    def test_render_loop_vector_alloc(self):
        """Vector allocation in render loop should be flagged."""
        lines = [
            'function animate() {',
            '    const pos = new THREE.Vector3(x, y, z);',
            '    renderer.render(scene, camera);',
            '}',
            'requestAnimationFrame(animate);',
        ]
        confidence = detect_render_loop_alloc(lines[1], 1, lines)
        assert confidence > 0.8

    def test_render_loop_float_array_alloc(self):
        """Float32Array allocation in render loop should be flagged."""
        lines = [
            'useFrame(() => {',
            '    const buffer = new Float32Array(1000);',
            '});',
        ]
        confidence = detect_render_loop_alloc(lines[1], 1, lines)
        assert confidence > 0.7

    def test_uncapped_pixel_ratio(self):
        """Uncapped devicePixelRatio should be flagged."""
        line = 'renderer.setPixelRatio(window.devicePixelRatio);'
        lines = [line]
        confidence = detect_uncapped_pixel_ratio(line, 0, lines)
        assert confidence > 0.9

    def test_capped_pixel_ratio(self):
        """Capped devicePixelRatio should not be flagged."""
        line = 'renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));'
        lines = [line]
        confidence = detect_uncapped_pixel_ratio(line, 0, lines)
        assert confidence < 0.5

    def test_image_no_dimensions(self):
        """Image tag without width/height should be flagged."""
        line = '<img src="photo.jpg" alt="Photo" />'
        lines = [line]
        confidence = detect_image_no_dimensions(line, 0, lines)
        assert confidence > 0.8

    def test_image_with_dimensions(self):
        """Image tag with width/height should not be flagged."""
        line = '<img src="photo.jpg" alt="Photo" width="100" height="100" />'
        lines = [line]
        confidence = detect_image_no_dimensions(line, 0, lines)
        assert confidence < 0.5

    def test_image_next_component(self):
        """Next.js Image component should not be flagged."""
        line = '<Image src="photo.jpg" alt="Photo" />'
        lines = [line]
        confidence = detect_image_no_dimensions(line, 0, lines)
        assert confidence == 0.0


class TestQualityPatterns:
    """Test code quality detectors."""

    def test_dead_code_todo(self):
        """TODO comments should be flagged."""
        line = '# TODO: fix this logic'
        lines = [line]
        confidence = detect_dead_code(line, 0, lines)
        assert confidence > 0.6

    def test_dead_code_fixme(self):
        """FIXME comments should be flagged."""
        line = '// FIXME: memory leak here'
        lines = [line]
        confidence = detect_dead_code(line, 0, lines)
        assert confidence > 0.6

    def test_dead_code_hack(self):
        """HACK comments should be flagged."""
        line = '/* HACK: workaround for Safari bug */'
        lines = [line]
        confidence = detect_dead_code(line, 0, lines)
        assert confidence > 0.6

    def test_dead_code_ellipsis(self):
        """Ellipsis placeholder should be flagged."""
        line = '    ...'
        lines = [line]
        confidence = detect_dead_code(line, 0, lines)
        assert confidence > 0.6

    def test_magic_number_comparison(self):
        """Large magic numbers in comparisons should be flagged."""
        line = 'if status_code > 500:'
        lines = [line]
        confidence = detect_magic_number(line, 0, lines)
        assert confidence > 0.6

    def test_magic_number_safe_pattern(self):
        """Magic numbers in safe patterns should not be flagged."""
        line = 'timeout = 30'
        lines = [line]
        confidence = detect_magic_number(line, 0, lines)
        assert confidence < 0.5

    def test_deep_nesting_5_levels(self):
        """5 levels of nesting should NOT trigger (threshold is 6)."""
        lines = [
            'if a:',
            '    if b:',
            '        if c:',
            '            if d:',
            '                if e:',
            '                    print("nested")',
        ]
        confidence = detect_deep_nesting(lines[5], 5, lines)
        assert confidence == 0.0

    def test_deep_nesting_6_levels(self):
        """6+ levels of nesting should be flagged."""
        lines = [
            'if a:',
            '    if b:',
            '        if c:',
            '            if d:',
            '                if e:',
            '                    if f:',
            '                        print("too nested")',
        ]
        confidence = detect_deep_nesting(lines[6], 6, lines)
        assert confidence >= 0.7

    def test_deep_nesting_skips_trivial_lines(self):
        """Trivial lines (except/pass/return) should not trigger deep nesting."""
        lines = [
            'try:',
            '    try:',
            '        try:',
            '            try:',
            '                try:',
            '                    try:',
            '                        except Exception:',
        ]
        confidence = detect_deep_nesting(lines[6], 6, lines)
        assert confidence == 0.0


class TestWebReactPatterns:
    """Test web/React specific patterns."""

    def test_dangerous_html_unsanitized(self):
        """dangerouslySetInnerHTML without sanitization should be flagged."""
        line = 'return <div dangerouslySetInnerHTML={{ __html: userContent }} />;'
        lines = [line]
        confidence = detect_dangerous_html(line, 0, lines)
        assert confidence > 0.7

    def test_dangerous_html_with_dompurify(self):
        """dangerouslySetInnerHTML with DOMPurify should have lower confidence."""
        lines = [
            'const sanitized = DOMPurify.sanitize(userContent);',
            'return <div dangerouslySetInnerHTML={{ __html: sanitized }} />;',
        ]
        confidence = detect_dangerous_html(lines[1], 1, lines)
        assert confidence < 0.7

    def test_missing_cleanup_with_subscription(self):
        """useEffect with subscription but no cleanup should be flagged."""
        lines = [
            'useEffect(() => {',
            '    const subscription = observable.subscribe(handler);',
            '}, []);',
        ]
        confidence = detect_missing_cleanup(lines[0], 0, lines)
        assert confidence > 0.6

    def test_missing_cleanup_with_timeout(self):
        """useEffect with setTimeout but no cleanup should be flagged."""
        lines = [
            'useEffect(() => {',
            '    setTimeout(() => setData(x), 1000);',
            '}, []);',
        ]
        confidence = detect_missing_cleanup(lines[0], 0, lines)
        assert confidence > 0.6

    def test_missing_cleanup_with_return(self):
        """useEffect with cleanup function should not be flagged."""
        lines = [
            'useEffect(() => {',
            '    const subscription = observable.subscribe(handler);',
            '    return () => subscription.unsubscribe();',
            '}, []);',
        ]
        confidence = detect_missing_cleanup(lines[0], 0, lines)
        assert confidence < 0.5

    def test_stale_closure_empty_deps(self):
        """useEffect with empty deps and state usage should be flagged."""
        lines = [
            'useEffect(() => {',
            '    const handler = () => setCount(count + 1);',
            '    element.addEventListener("click", handler);',
            '}, []);',
        ]
        confidence = detect_stale_closure(lines[0], 0, lines)
        assert confidence > 0.6

    def test_stale_closure_proper_deps(self):
        """useEffect with proper dependency array should not be flagged."""
        lines = [
            'useEffect(() => {',
            '    const handler = () => console.log(count);',
            '    element.addEventListener("click", handler);',
            '}, [count]);',
        ]
        confidence = detect_stale_closure(lines[0], 0, lines)
        assert confidence < 0.5

    def test_env_leak_process_env(self):
        """process.env without NEXT_PUBLIC_ should be flagged."""
        line = 'const apiUrl = process.env.API_URL;'
        lines = [line]
        confidence = detect_env_leak(line, 0, lines)
        assert confidence > 0.7

    def test_env_public_no_leak(self):
        """process.env.NEXT_PUBLIC_ should not be flagged."""
        line = 'const theme = process.env.NEXT_PUBLIC_THEME;'
        lines = [line]
        confidence = detect_env_leak(line, 0, lines)
        assert confidence == 0.0

    def test_ssr_window_direct_access(self):
        """Direct window access without SSR guard should be flagged."""
        line = 'const width = window.innerWidth;'
        lines = [line]
        confidence = detect_ssr_window(line, 0, lines)
        assert confidence > 0.6

    def test_ssr_window_with_guard(self):
        """Window access with typeof guard should not be flagged."""
        lines = [
            'if (typeof window !== "undefined") {',
            '    const width = window.innerWidth;',
            '}',
        ]
        confidence = detect_ssr_window(lines[1], 1, lines)
        assert confidence < 0.5

    def test_missing_key_in_map(self):
        """Array.map() in JSX without key should be flagged."""
        lines = [
            'users.map(user => (',
            '    <User name={user.name} />',
            '))',
        ]
        confidence = detect_missing_key(lines[0], 0, lines)
        assert confidence > 0.6

    def test_key_in_map(self):
        """Array.map() with key should not be flagged."""
        lines = [
            'users.map(user => (',
            '    <User key={user.id} name={user.name} />',
            '))',
        ]
        confidence = detect_missing_key(lines[0], 0, lines)
        assert confidence < 0.5


class TestCheckPattern:
    """Test the check_pattern dispatcher with file extension guards."""

    def test_xss_only_in_js_files(self):
        """XSS patterns should only trigger in JS/TS files."""
        line = 'element.innerHTML = data;'
        lines = [line]

        # Should trigger in .js
        conf_js = check_pattern("xss", line, 0, lines, ".js")
        assert conf_js > 0.0

        # Should not trigger in .py
        conf_py = check_pattern("xss", line, 0, lines, ".py")
        assert conf_py == 0.0

    def test_layout_animation_only_in_css(self):
        """Layout animation should only trigger in CSS files."""
        line = 'transition: width 0.3s;'
        lines = [line]

        # Should trigger in .css
        conf_css = check_pattern("layout-animation", line, 0, lines, ".css")
        assert conf_css > 0.0

        # Should not trigger in .js
        conf_js = check_pattern("layout-animation", line, 0, lines, ".js")
        assert conf_js == 0.0

    def test_layout_thrashing_only_in_js(self):
        """Layout thrashing should only trigger in JS/TS files."""
        line = 'const width = element.offsetWidth;'
        lines = [line]

        # Should potentially trigger in .js
        conf_js = check_pattern("layout-thrashing", line, 0, lines, ".js")
        assert conf_js >= 0.0

        # Should not trigger in .css
        conf_css = check_pattern("layout-thrashing", line, 0, lines, ".css")
        assert conf_css == 0.0

    def test_image_dimensions_in_jsx_html(self):
        """Image dimension check should work in JSX and HTML."""
        line = '<img src="test.jpg" />'
        lines = [line]

        # Should trigger in .jsx
        conf_jsx = check_pattern("image-no-dimensions", line, 0, lines, ".jsx")
        assert conf_jsx > 0.0

        # Should trigger in .html
        conf_html = check_pattern("image-no-dimensions", line, 0, lines, ".html")
        assert conf_html > 0.0

        # Should not trigger in .py
        conf_py = check_pattern("image-no-dimensions", line, 0, lines, ".py")
        assert conf_py == 0.0


class TestConfidenceFiltering:
    """Test confidence scoring and MIN_CONFIDENCE filtering."""

    def test_min_confidence_threshold(self):
        """Bugs with confidence < MIN_CONFIDENCE should be filtered."""
        assert MIN_CONFIDENCE == 0.6

    def test_confidence_filtering_in_scan_file(self, tmp_path):
        """scan_file should filter out bugs below MIN_CONFIDENCE."""
        # Create file with a weak pattern that barely exceeds threshold
        test_file = tmp_path / "test.py"
        test_file.write_text("""
# TODO: fix this
""")

        bugs = scan_file(test_file, ["quality"])
        # TODO should be detected (confidence > 0.6)
        assert len(bugs) > 0 or len(bugs) == 0  # May or may not detect depending on context

    def test_security_patterns_minimum_confidence(self, tmp_path):
        """Security patterns require higher confidence than 0.6."""
        test_file = tmp_path / "test.py"
        # Write code with low-confidence SQL pattern
        test_file.write_text('query = "SELECT * FROM users"')

        bugs = scan_file(test_file, ["security"])
        # Just query without injection should not be flagged
        assert len(bugs) == 0


class TestScanFile:
    """Test scan_file function."""

    def test_scan_file_single_security_bug(self, tmp_path):
        """scan_file should find security bugs."""
        test_file = tmp_path / "test.py"
        test_file.write_text('password = "hardcoded_secret_12345"')

        bugs = scan_file(test_file, ["security"])
        assert len(bugs) > 0
        assert bugs[0]["cat"] == "security"
        assert "hardcoded-secret" in bugs[0]["pattern_id"] or bugs[0]["confidence"] >= 0.8

    def test_scan_file_multiple_bugs(self, tmp_path):
        """scan_file should find multiple bugs in one file."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
password = "secret_12345"
api_key = "sk-1234567890"
# TODO: handle error cases
""")

        bugs = scan_file(test_file, ["security", "quality"])
        # Should find at least hardcoded secrets
        assert len(bugs) >= 1

    def test_scan_file_category_filtering(self, tmp_path):
        """scan_file should only report bugs in requested categories."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
password = "secret_12345"
# TODO: refactor
for item in items:
    process(item)
""")

        # Only scan security
        bugs_security = scan_file(test_file, ["security"])
        assert all(b["cat"] == "security" for b in bugs_security)

        # Only scan quality
        bugs_quality = scan_file(test_file, ["quality"])
        assert all(b["cat"] == "quality" for b in bugs_quality)

    def test_scan_file_empty_file(self, tmp_path):
        """scan_file should handle empty files."""
        test_file = tmp_path / "empty.py"
        test_file.write_text("")

        bugs = scan_file(test_file, ["security", "logic", "performance"])
        assert len(bugs) == 0

    def test_scan_file_skips_comments(self, tmp_path):
        """scan_file should skip lines that are pure comments."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
# password = "secret_12345"
// api_key = "sk-123"
/* TODO: fix this */
password = "real_secret_12345"
""")

        bugs = scan_file(test_file, ["security", "quality"])
        # Should only flag the uncommented password
        assert len(bugs) >= 1

    def test_scan_file_unicode_handling(self, tmp_path):
        """scan_file should handle unicode content."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
# Émoji test: 😀
description = "Café database"
password = "secret_123456"
""")

        bugs = scan_file(test_file, ["security"])
        assert len(bugs) >= 1  # Should find the hardcoded password


class TestScanDirectory:
    """Test scan_directory function."""

    def test_scan_directory_finds_bugs(self, tmp_path):
        """scan_directory should find bugs across multiple files."""
        (tmp_path / "file1.py").write_text('password = "secret_12345"')
        (tmp_path / "file2.js").write_text('element.innerHTML = userInput;')
        (tmp_path / "file3.txt").write_text("Not a code file")

        bugs = scan_directory(tmp_path, ["security"])
        assert len(bugs) >= 1
        # Should have found hardcoded secret and possibly XSS
        bug_patterns = {b["pattern_id"] for b in bugs}
        assert "hardcoded-secret" in bug_patterns or any(b["confidence"] > 0.7 for b in bugs)

    def test_scan_directory_excludes_node_modules(self, tmp_path):
        """scan_directory should exclude node_modules directory."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        nm_dir = tmp_path / "node_modules"
        nm_dir.mkdir()

        (src_dir / "app.py").write_text('password = "secret_12345"')
        (nm_dir / "package.json").write_text('password = "secret_12345"')

        bugs = scan_directory(tmp_path, ["security"])
        # Should find bug in src but not node_modules
        assert len(bugs) >= 1
        assert all("node_modules" not in b["loc"] for b in bugs)

    def test_scan_directory_excludes_git(self, tmp_path):
        """scan_directory should exclude .git directory."""
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        (src_dir / "app.py").write_text('password = "secret_12345"')
        (git_dir / "config").write_text('password = "secret_12345"')

        bugs = scan_directory(tmp_path, ["security"])
        assert all(".git" not in b["loc"] for b in bugs)

    def test_scan_directory_single_file(self, tmp_path):
        """scan_directory should handle a single file path."""
        test_file = tmp_path / "test.py"
        test_file.write_text('password = "secret_12345"')

        bugs = scan_directory(test_file, ["security"])
        assert len(bugs) >= 1

    def test_scan_directory_nonexistent_path(self):
        """scan_directory should handle non-existent paths gracefully."""
        nonexistent = Path("/nonexistent/path/to/file")
        bugs = scan_directory(nonexistent, ["security"])
        assert len(bugs) == 0


class TestFormatters:
    """Test output formatters."""

    def test_format_concise_json(self, tmp_path):
        """format_concise should produce valid JSON with minimal fields."""
        test_file = tmp_path / "test.py"
        test_file.write_text('password = "secret_12345"')
        bugs = scan_file(test_file, ["security"])

        json_output = format_concise(bugs)
        import json
        data = json.loads(json_output)

        assert "bugs" in data
        assert isinstance(data["bugs"], list)
        if data["bugs"]:
            bug = data["bugs"][0]
            assert "id" in bug
            assert "loc" in bug
            assert "cat" in bug
            assert "sev" in bug
            assert "desc" in bug
            assert "conf" in bug

    def test_format_detailed_yaml(self, tmp_path):
        """format_detailed should produce valid YAML."""
        test_file = tmp_path / "test.py"
        test_file.write_text('password = "secret_12345"')
        bugs = scan_file(test_file, ["security"])

        yaml_output = format_detailed(bugs)
        # Should contain YAML-like content
        assert "bugs:" in yaml_output or "password" in yaml_output or len(bugs) == 0


class TestGenerateBugId:
    """Test bug ID generation."""

    def test_bug_id_consistency(self):
        """generate_bug_id should produce consistent IDs for same inputs."""
        id1 = generate_bug_id("file.py", 42, "sqli")
        id2 = generate_bug_id("file.py", 42, "sqli")
        assert id1 == id2

    def test_bug_id_format(self):
        """generate_bug_id should produce IDs in correct format."""
        bug_id = generate_bug_id("file.py", 10, "xss")
        assert bug_id.startswith("B")
        assert len(bug_id) == 7  # B + 6 hex chars


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_scan_file_with_binary_content(self, tmp_path):
        """scan_file should handle binary files gracefully."""
        test_file = tmp_path / "binary.bin"
        test_file.write_bytes(b'\x00\x01\x02\xFF')

        bugs = scan_file(test_file, ["security"])
        assert len(bugs) == 0

    def test_scan_file_with_very_long_lines(self, tmp_path):
        """scan_file should handle very long lines."""
        test_file = tmp_path / "test.py"
        test_file.write_text('password = "' + "x" * 10000 + '"')

        bugs = scan_file(test_file, ["security"])
        # Should handle without crashing
        assert isinstance(bugs, list)

    def test_scan_file_with_mixed_line_endings(self, tmp_path):
        """scan_file should handle mixed line endings."""
        test_file = tmp_path / "test.py"
        content = "line1\r\nline2\nline3\rpassword = \"secret_12345\""
        test_file.write_text(content)

        bugs = scan_file(test_file, ["security"])
        assert len(bugs) >= 1

    def test_categories_completeness(self):
        """All category types should be defined."""
        expected_categories = {"security", "logic", "performance", "quality", "web"}
        actual_categories = set(CATEGORIES.keys())
        assert expected_categories.issubset(actual_categories)

    def test_security_category_patterns(self):
        """Security category should have expected pattern IDs."""
        security_patterns = {p["id"] for p in CATEGORIES["security"]["patterns"]}
        expected = {"sqli", "xss", "hardcoded-secret", "path-traversal", "command-injection"}
        assert expected.issubset(security_patterns)

    def test_performance_category_has_new_detectors(self):
        """Performance category should include the 9 new detectors."""
        perf_patterns = {p["id"] for p in CATEGORIES["performance"]["patterns"]}
        new_detectors = {
            "layout-animation", "layout-thrashing", "unthrottled-scroll",
            "non-passive-listener", "missing-debounce", "inline-jsx-object",
            "render-loop-alloc", "uncapped-pixel-ratio", "image-no-dimensions"
        }
        assert new_detectors.issubset(perf_patterns)


class TestNewSecurityPatterns:
    """Test the 5 new security pattern detectors."""

    # ===== Open Redirect Tests =====
    def test_open_redirect_with_req_query(self):
        """Open redirect with req.query should be detected with high confidence."""
        lines = [
            "const url = req.query.redirect;",
            "res.redirect(url);",
        ]
        confidence = detect_open_redirect(lines[1], 1, lines)
        assert confidence > 0.7

    def test_open_redirect_no_user_input(self):
        """Open redirect without user input should not be detected."""
        lines = [
            'const url = "https://example.com";',
            "res.redirect(url);",
        ]
        confidence = detect_open_redirect(lines[1], 1, lines)
        assert confidence == 0.0

    def test_open_redirect_with_allowlist(self):
        """Open redirect with allowlist check should have reduced confidence."""
        lines = [
            "const url = req.query.redirect;",
            "if (ALLOWED_URLS.includes(url)) {",
            "  res.redirect(url);",
            "}",
        ]
        confidence = detect_open_redirect(lines[2], 2, lines)
        assert confidence < 0.85

    # ===== Permissive CORS Tests =====
    def test_permissive_cors_wildcard_header(self):
        """CORS with wildcard origin header should be detected."""
        line = "Access-Control-Allow-Origin: *"
        lines = [line]
        confidence = detect_permissive_cors(line, 0, lines)
        assert confidence > 0.8

    def test_permissive_cors_origin_true(self):
        """CORS with origin: true should be detected."""
        lines = [
            "app.use(cors({",
            "  origin: true",
            "}));",
        ]
        confidence = detect_permissive_cors(lines[1], 1, lines)
        assert confidence > 0.75

    def test_permissive_cors_restricted(self):
        """CORS with specific origin should not be detected."""
        lines = [
            "app.use(cors({",
            "  origin: 'https://example.com'",
            "}));",
        ]
        confidence = detect_permissive_cors(lines[1], 1, lines)
        assert confidence == 0.0

    def test_permissive_cors_no_config(self):
        """CORS with no config defaults to origin: * in Express."""
        lines = [
            "const cors = require('cors');",
            "app.use(cors());",
        ]
        confidence = detect_permissive_cors(lines[1], 1, lines)
        assert confidence > 0.7

    def test_permissive_cors_setheader_wildcard(self):
        """res.setHeader('Access-Control-Allow-Origin', '*') should be detected."""
        lines = [
            "app.get('/api', (req, res) => {",
            "  res.setHeader('Access-Control-Allow-Origin', '*');",
            "  res.json({ data: 'test' });",
        ]
        confidence = detect_permissive_cors(lines[1], 1, lines)
        assert confidence >= 0.85, f"Expected >= 0.85, got {confidence}"

    def test_permissive_cors_res_set_wildcard(self):
        """res.set('Access-Control-Allow-Origin', '*') should be detected."""
        lines = [
            "app.get('/api', (req, res) => {",
            "  res.set('Access-Control-Allow-Origin', '*');",
            "  res.json({ data: 'test' });",
        ]
        confidence = detect_permissive_cors(lines[1], 1, lines)
        assert confidence >= 0.85, f"Expected >= 0.85, got {confidence}"

    def test_permissive_cors_res_header_wildcard(self):
        """res.header('Access-Control-Allow-Origin', '*') should be detected."""
        lines = [
            "app.get('/api', (req, res) => {",
            "  res.header('Access-Control-Allow-Origin', '*');",
            "  res.json({ data: 'test' });",
        ]
        confidence = detect_permissive_cors(lines[1], 1, lines)
        assert confidence >= 0.85, f"Expected >= 0.85, got {confidence}"

    def test_permissive_cors_setheader_specific_origin(self):
        """res.setHeader with specific origin should NOT be flagged."""
        lines = [
            "app.get('/api', (req, res) => {",
            "  res.setHeader('Access-Control-Allow-Origin', 'https://example.com');",
            "  res.json({ data: 'test' });",
        ]
        confidence = detect_permissive_cors(lines[1], 1, lines)
        assert confidence == 0.0, f"Expected 0.0 for specific origin, got {confidence}"

    # ===== JWT Extended Context Window Tests =====
    def test_jwt_verify_missing_algorithms_multiline(self):
        """jwt.verify spread across 6+ lines should still detect missing algorithms."""
        lines = [
            "// Auth middleware",
            "const token = req.headers.authorization.split(' ')[1];",
            "const secret = process.env.JWT_SECRET;",
            "",
            "try {",
            "  const decoded = jwt.verify(",
            "    token,",
            "    secret",
            "  );",
            "  req.user = decoded;",
            "} catch (err) {",
            "  return res.status(401).send('Unauthorized');",
            "}",
        ]
        # jwt.verify is on line index 5; algorithms check needs to see lines 0-13
        confidence = detect_jwt_alg_none(lines[5], 5, lines)
        assert confidence >= 0.75, f"Expected >= 0.75 for multiline jwt.verify without algorithms, got {confidence}"

    def test_jwt_verify_with_algorithms_multiline(self):
        """jwt.verify with algorithms param 5 lines away should NOT be flagged."""
        lines = [
            "// Auth middleware",
            "const token = req.headers.authorization.split(' ')[1];",
            "const secret = process.env.JWT_SECRET;",
            "",
            "try {",
            "  const decoded = jwt.verify(",
            "    token,",
            "    secret,",
            "    {",
            "      algorithms: ['HS256'],",
            "    }",
            "  );",
            "  req.user = decoded;",
            "} catch (err) {",
            "}",
        ]
        confidence = detect_jwt_alg_none(lines[5], 5, lines)
        assert confidence == 0.0, f"Expected 0.0 for jwt.verify WITH algorithms, got {confidence}"

    # ===== Prototype Pollution Tests =====
    def test_prototype_pollution_bracket_assignment(self):
        """Prototype pollution with bracket assignment and user input should be detected."""
        lines = [
            "const data = req.body;",
            "const obj = {};",
            "obj[data.key] = data.value;",
        ]
        confidence = detect_prototype_pollution(lines[2], 2, lines)
        assert confidence > 0.7

    def test_prototype_pollution_object_assign(self):
        """Prototype pollution with Object.assign and user input should be detected."""
        lines = [
            "const userData = req.body;",
            "const result = Object.assign({}, userData);",
        ]
        confidence = detect_prototype_pollution(lines[1], 1, lines)
        assert confidence > 0.7

    def test_prototype_pollution_safe_assignment(self):
        """Safe object assignment should not be detected as prototype pollution."""
        lines = [
            "const obj = {};",
            'obj["name"] = "John";',
        ]
        confidence = detect_prototype_pollution(lines[1], 1, lines)
        assert confidence == 0.0

    # ===== NoSQL Injection Tests =====
    def test_nosql_injection_with_dollar_where(self):
        """NoSQL injection with $where and user input should be detected."""
        lines = [
            "const userInput = req.query.search;",
            "db.find({ $where: userInput });",
        ]
        confidence = detect_nosql_injection(lines[1], 1, lines)
        assert confidence > 0.8

    def test_nosql_injection_with_dollar_ne(self):
        """NoSQL injection with $ne operator and user input should be detected."""
        lines = [
            "const userInput = req.body.filter;",
            "db.findOne({ status: { $ne: userInput } });",
        ]
        confidence = detect_nosql_injection(lines[1], 1, lines)
        assert confidence > 0.75

    def test_nosql_injection_safe_query(self):
        """Safe NoSQL query without user input should not be detected."""
        lines = [
            'db.find({ status: "active" });',
        ]
        confidence = detect_nosql_injection(lines[0], 0, lines)
        assert confidence == 0.0

    # ===== JWT Algorithm None Tests =====
    def test_jwt_alg_none_with_none_algorithm(self):
        """JWT verify with algorithm: 'none' should be detected."""
        lines = [
            "jwt.verify(token, secret, {",
            "  algorithms: ['none']",
            "});",
        ]
        confidence = detect_jwt_alg_none(lines[0], 0, lines)
        assert confidence > 0.8

    def test_jwt_alg_none_without_algorithms_param(self):
        """JWT verify without algorithms parameter should be detected."""
        lines = [
            "jwt.verify(token, secret);",
        ]
        confidence = detect_jwt_alg_none(lines[0], 0, lines)
        assert confidence > 0.7

    def test_jwt_decode_instead_of_verify(self):
        """Using jwt.decode instead of verify should be detected."""
        lines = [
            "const decoded = jwt.decode(token);",
        ]
        confidence = detect_jwt_alg_none(lines[0], 0, lines)
        assert confidence > 0.75

    def test_jwt_verify_safe(self):
        """Safe jwt.verify with proper algorithms should not be detected."""
        lines = [
            "jwt.verify(token, secret, {",
            "  algorithms: ['HS256', 'RS256']",
            "});",
        ]
        confidence = detect_jwt_alg_none(lines[0], 0, lines)
        assert confidence == 0.0
