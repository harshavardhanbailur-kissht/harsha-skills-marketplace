# Function Documentation Template

**Function**: `{{FUNCTION_NAME}}` | **Module**: {{MODULE}} | **Last Updated**: {{DATE}}

---

## Summary

{{One-sentence description of what this function does}}

---

## Behavioral Contract

**What It Promises**:
- {{Promise 1}}: {{Specific, testable behavior}}
- {{Promise 2}}: {{Specific, testable behavior}}
- {{Promise 3}}: {{Specific, testable behavior}}

**What It Requires**:
- {{Precondition 1}}: {{What must be true before calling}}
- {{Precondition 2}}: {{What must be true before calling}}

**What It Guarantees**:
- {{Postcondition 1}}: {{What will be true after successful execution}}
- {{Postcondition 2}}: {{What will be true after successful execution}}

---

## Signature

```{{LANGUAGE}}
{{FULL_FUNCTION_SIGNATURE}}
```

**Type**: {{Function | Async Function | Generator | Class Constructor}}

**Category**: {{Public API | Internal | Deprecated | Experimental}}

---

## Parameters

### `{{PARAM_NAME}}`

| Aspect | Value |
|--------|-------|
| **Type** | `{{TYPE}}` |
| **Required** | Yes / No |
| **Default** | {{DEFAULT_VALUE}} |
| **Valid Range** | {{MIN}}–{{MAX}} or {{ENUM_VALUES}} |
| **Validation** | {{Validation rule}} |

**Description**: {{Detailed description of what this parameter is used for}}

**Example Values**:
- `{{example1}}` — {{Explanation}}
- `{{example2}}` — {{Explanation}}

---

### `{{PARAM_NAME}}`

| Aspect | Value |
|--------|-------|
| **Type** | `{{TYPE}}` |
| **Required** | Yes / No |
| **Default** | {{DEFAULT_VALUE}} |

**Description**: {{Detailed description}}

---

## Return Value

| Aspect | Value |
|--------|-------|
| **Type** | `{{TYPE}}` |
| **Description** | {{What is returned}} |
| **Null/Undefined** | {{When can it be null?}} |

**Return Examples**:
```javascript
// Success case
{{example_return_value}}

// Edge case
{{example_return_value}}
```

---

## Exceptions/Errors

### `{{ERROR_TYPE}}`

| Property | Value |
|----------|-------|
| **Thrown When** | {{Specific condition that triggers error}} |
| **Error Code** | `{{ERROR_CODE}}` |
| **Message** | `"{{ERROR_MESSAGE}}"` |
| **Data Property** | {{Additional error details}} |

**How to Handle**:
```javascript
try {
  {{FUNCTION_NAME}}({{args}});
} catch (error) {
  if (error.code === '{{ERROR_CODE}}') {
    // Handle this specific error
    console.error('{{Error description}}:', error.details);
  } else {
    throw error;  // Re-throw unknown errors
  }
}
```

---

### `{{ERROR_TYPE}}`

| Property | Value |
|----------|-------|
| **Thrown When** | {{Condition}} |
| **Error Code** | `{{ERROR_CODE}}` |

**How to Handle**: {{Guidance}}

---

## Behavior

### Normal Execution

**Step-by-step flow**:
1. Validate input parameters ({{Validations}})
2. {{Step 2}}: {{Description}}
3. {{Step 3}}: {{Description}}
4. Return {{Return description}}

**Time Complexity**: `O({{COMPLEXITY}})`

**Space Complexity**: `O({{COMPLEXITY}})`

### Side Effects

**This function may**:
- {{Side effect 1}} — {{Description}}
- {{Side effect 2}} — {{Description}}

**This function does NOT**:
- ✗ Modify global state
- ✗ Make network calls
- ✗ Write to filesystem

---

## Usage Examples

### Example 1: Basic Usage

```javascript
const result = {{FUNCTION_NAME}}({{simple_args}});
console.log(result);
// Output: {{expected_output}}
```

---

### Example 2: With Error Handling

```javascript
try {
  const result = {{FUNCTION_NAME}}({{args}});
  console.log('Success:', result);
} catch (error) {
  console.error('Failed:', error.message);
}
```

---

### Example 3: Async Pattern (if applicable)

```javascript
async function processData() {
  try {
    const result = await {{FUNCTION_NAME}}({{args}});
    return result;
  } catch (error) {
    logger.error('Operation failed:', error);
    throw error;
  }
}

processData().catch(error => {
  // Handle error at call site
});
```

---

### Example 4: Advanced Usage

```javascript
// Using with options
const result = {{FUNCTION_NAME}}({{required_arg}}, {
  option1: {{value}},
  option2: {{value}},
  timeout: 5000
});

// Chaining with other operations
const processed = {{FUNCTION_NAME}}(data)
  .then(result => transform(result))
  .then(final => save(final))
  .catch(error => logger.error(error));
```

---

## Edge Cases & Special Behaviors

| Case | Behavior | Handling |
|------|----------|----------|
| {{Empty input}} | {{What happens}} | {{How to handle}} |
| {{Null input}} | {{What happens}} | {{How to handle}} |
| {{Large input}} | {{What happens}} | {{How to handle}} |
| {{Concurrent calls}} | {{What happens}} | {{How to handle}} |

---

## Performance Characteristics

### Benchmarks

```
Input Size: 1000 items
  Time: {{TIME}}ms (P50), {{TIME}}ms (P99)
  Memory: {{MEMORY}}MB
  Allocation Count: {{COUNT}}

Input Size: 100,000 items
  Time: {{TIME}}ms (P50), {{TIME}}ms (P99)
  Memory: {{MEMORY}}MB
  Allocation Count: {{COUNT}}
```

### Optimization Tips

- {{Tip 1}}: {{Explanation and impact}}
- {{Tip 2}}: {{Explanation and impact}}

---

## Dependencies

| Dependency | Why | Impact if Unavailable |
|---|---|---|
| `{{module}}` | {{Purpose}} | {{What breaks}} |
| `{{module}}` | {{Purpose}} | {{What breaks}} |

---

## Related Functions

| Function | Relationship | When to Use |
|---|---|---|
| `{{function}}` | {{Precursor / Alternative / Follow-up}} | {{When}} |
| `{{function}}` | {{Precursor / Alternative / Follow-up}} | {{When}} |

---

## Testing

### Unit Tests

Location: `tests/{{path}}.test.js`

```javascript
describe('{{FUNCTION_NAME}}', () => {
  describe('normal case', () => {
    it('should {{expected behavior}}', () => {
      const input = {{value}};
      const expected = {{value}};

      const result = {{FUNCTION_NAME}}(input);

      expect(result).toEqual(expected);
    });
  });

  describe('edge cases', () => {
    it('should handle empty input', () => {
      const result = {{FUNCTION_NAME}}([]);
      expect(result).toEqual({{expected}});
    });

    it('should throw error when {{condition}}', () => {
      expect(() => {{FUNCTION_NAME}}({{invalid_input}}))
        .toThrow('{{error_message}}');
    });
  });

  describe('performance', () => {
    it('should complete within {{TIME}}ms for {{INPUT_SIZE}} items', () => {
      const largeInput = generateInput({{INPUT_SIZE}});
      const start = performance.now();

      {{FUNCTION_NAME}}(largeInput);

      const elapsed = performance.now() - start;
      expect(elapsed).toBeLessThan({{TIME}});
    });
  });
});
```

### Test Coverage

- **Lines**: {{COVERAGE}}%
- **Branches**: {{COVERAGE}}%
- **Functions**: {{COVERAGE}}%

---

## Known Issues

| Issue | Impact | Workaround | Fix Timeline |
|---|---|---|---|
| {{Issue}} | {{Impact}} | {{Workaround}} | {{Timeline}} |

---

## Deprecation Status

**Status**: {{ACTIVE | DEPRECATED | EXPERIMENTAL}}

{{If deprecated:}}

**Deprecated Since**: Version {{VERSION}}

**Replacement**: Use `{{replacement_function}}` instead

**Migration Path**:
```javascript
// Old code (deprecated)
const result = {{OLD_FUNCTION}}({{args}});

// New code (preferred)
const result = {{NEW_FUNCTION}}({{new_args}});
```

**Sunset Date**: {{DATE}} ({{VERSIONS}}} versions)

---

## Changelog

| Version | Change | Author |
|---------|--------|--------|
| 2.1 | {{Change description}} | {{Author}} |
| 2.0 | {{Breaking change}} | {{Author}} |
| 1.0 | Initial implementation | {{Author}} |

---

## Signature History

### Current (v2.x)
```javascript
{{CURRENT_SIGNATURE}}
```

### Previous (v1.x)
```javascript
{{PREVIOUS_SIGNATURE}}
```

---

## Source Code Location

- **File**: `src/{{path}}/{{file}}.{{ext}}`
- **Line Range**: {{START}}–{{END}}
- **Module**: `{{module_name}}`

---

## See Also

- [Module Documentation](./module-doc-{{MODULE}}.md)
- [Architecture Guide](./architecture.md)
- [Related Function: {{function}}](./function-doc-{{function}}.md)
- [Use Case: {{use_case}}](./{{use_case}}.md)

---

**Confidence**: {{HIGH | MEDIUM | LOW}} ⚠️

{{If LOW confidence:}}
⚠️ **Note**: This documentation has low confidence. Recommend verifying behavior by:
1. Running the test suite
2. Checking recent commits/PRs
3. Reaching out to {{MODULE}} team

---

**Updated**: {{DATE}} | **By**: {{AUTHOR}} | **Reviewed**: {{REVIEWER}} | **Status**: {{VERIFIED | NEEDS_REVIEW}}
