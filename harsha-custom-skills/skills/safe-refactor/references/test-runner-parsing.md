# Test Runner Output Parsing Reference

How to run tests and parse output for every supported test runner.
The shell scripts handle most of this automatically, but this reference
documents the exact formats for troubleshooting and customization.

## Table of Contents

1. [Jest](#jest)
2. [Vitest](#vitest)
3. [Pytest](#pytest)
4. [Go Test](#go-test)
5. [Cargo Test](#cargo-test)
6. [Mocha](#mocha)
7. [RSpec](#rspec)
8. [PHPUnit](#phpunit)
9. [dotnet test](#dotnet-test)
10. [Maven / Gradle (JUnit)](#junit)

---

## Jest

**Run:** `npx jest --json --outputFile=results.json`
**Exit codes:** 0 = pass, 1 = fail

**JSON structure:**
```json
{
  "numTotalTests": 42,
  "numPassedTests": 40,
  "numFailedTests": 1,
  "numPendingTests": 1,
  "success": false,
  "testResults": [{
    "testFilePath": "/path/to/test.js",
    "assertionResults": [{
      "title": "should add numbers",
      "status": "passed",
      "duration": 5
    }]
  }]
}
```

**Regex fallback (verbose output):**
```
Tests:  1 failed, 1 skipped, 40 passed, 42 total
```

---

## Vitest

**Run:** `npx vitest run --reporter=json --outputFile=results.json`
**Exit codes:** 0 = pass, 1 = fail

JSON format is compatible with Jest. Same fields, same structure.

**Config alternative:**
```typescript
// vitest.config.ts
export default defineConfig({
  test: { reporters: ['json'], outputFile: './results.json' }
})
```

---

## Pytest

**Run (with plugin):** `python -m pytest --json-report --json-report-file=results.json`
**Run (basic):** `python -m pytest -v`
**Exit codes:** 0=pass, 1=fail, 2=interrupted, 3=internal error, 4=usage error, 5=no tests

**Plugin install:** `pip install pytest-json-report`

**JSON structure (pytest-json-report):**
```json
{
  "summary": { "passed": 10, "failed": 1, "error": 0, "total": 11 },
  "tests": [{
    "nodeid": "test_module.py::test_func",
    "outcome": "passed",
    "duration": 0.001
  }],
  "duration": 1.5
}
```

**Regex fallback (-v output):**
```
test_module.py::test_func PASSED
test_module.py::test_other FAILED
====== 1 failed, 10 passed in 1.50s ======
```
Pattern: `(\d+) passed`, `(\d+) failed`, `(\d+) skipped`

---

## Go Test

**Run:** `go test -json ./...`
**Exit codes:** 0 = pass, 1 = fail

**Output:** Line-delimited JSON (one object per line):
```json
{"Time":"2024-01-15T10:00:00Z","Action":"run","Package":"pkg","Test":"TestAdd"}
{"Time":"2024-01-15T10:00:00Z","Action":"output","Package":"pkg","Test":"TestAdd","Output":"--- PASS: TestAdd (0.00s)\n"}
{"Time":"2024-01-15T10:00:00Z","Action":"pass","Package":"pkg","Test":"TestAdd","Elapsed":0.001}
```

**Key Actions:** `run`, `pass`, `fail`, `skip`, `output`

**Parsing:** Count `"Action":"pass"` and `"Action":"fail"` lines.

**Regex fallback (-v output):**
```
--- PASS: TestAdd (0.00s)
--- FAIL: TestSub (0.01s)
ok      mypackage   0.005s
FAIL    otherpackage    0.010s
```

---

## Cargo Test

**Run:** `cargo test`
**Exit codes:** 0 = pass, 101 = fail

**Standard output:**
```
running 5 tests
test test_add ... ok
test test_sub ... ok
test test_mul ... FAILED
test test_div ... ok
test test_mod ... ignored

test result: FAILED. 3 passed; 1 failed; 1 ignored; 0 measured; 0 filtered out
```

**Regex patterns:**
- Per test: `test (\S+) \.\.\. (ok|FAILED|ignored)`
- Summary: `(\d+) passed; (\d+) failed; (\d+) ignored`

**JSON (nightly only):** `cargo +nightly test -- --format json -Z unstable-options`

---

## Mocha

**Run:** `npx mocha --reporter json`
**Exit codes:** 0 = pass, non-zero = fail

**JSON structure:**
```json
{
  "stats": {
    "suites": 5,
    "tests": 20,
    "passes": 18,
    "pending": 1,
    "failures": 1
  },
  "tests": [{ "title": "should work", "duration": 5 }],
  "failures": [{ "title": "should handle error", "err": { "message": "..." } }]
}
```

**Regex fallback (spec reporter):**
```
  20 passing (500ms)
  1 pending
  1 failing
```

---

## RSpec

**Run:** `bundle exec rspec --format json --out results.json`
**Exit codes:** 0 = pass, non-zero = fail

**JSON structure:**
```json
{
  "summary": {
    "example_count": 15,
    "failure_count": 1,
    "pending_count": 2,
    "duration": 3.5
  },
  "examples": [{
    "description": "adds numbers",
    "status": "passed",
    "run_time": 0.001
  }]
}
```

---

## PHPUnit

**Run:** `./vendor/bin/phpunit --testdox`
**Exit codes:** 0 = pass, non-zero = fail

**Standard output:**
```
OK (42 tests, 100 assertions)
```
or
```
Tests: 42, Assertions: 100, Failures: 2, Skipped: 1
```

**Regex patterns:**
- Success: `OK \((\d+) tests?`
- Detailed: `Tests: (\d+).*Failures: (\d+).*Skipped: (\d+)`

---

## dotnet test

**Run:** `dotnet test --logger "trx;LogFileName=results.trx"`
**Exit codes:** 0 = pass, non-zero = fail

**Console output:**
```
Passed!  - Failed: 0, Passed: 10, Skipped: 1, Total: 11
```

**Regex:** `Failed: (\d+), Passed: (\d+), Skipped: (\d+), Total: (\d+)`

**TRX format:** XML file at `TestResults/results.trx` with `<UnitTestResult>` elements.

---

## Maven / Gradle (JUnit)

**Run (Maven):** `mvn test`
**Run (Gradle):** `./gradlew test`
**Exit codes:** 0 = pass, non-zero = fail

**Console output:**
```
Tests run: 25, Failures: 1, Errors: 0, Skipped: 2
```

**JUnit XML (auto-generated):**
- Maven: `target/surefire-reports/TEST-*.xml`
- Gradle: `build/test-results/test/TEST-*.xml`

```xml
<testsuite tests="25" failures="1" errors="0" skipped="2">
  <testcase name="testAdd" classname="CalcTest" time="0.001"/>
  <testcase name="testSub" classname="CalcTest" time="0.002">
    <failure message="expected 3 but was 4"/>
  </testcase>
</testsuite>
```

**Regex:** `Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)`
