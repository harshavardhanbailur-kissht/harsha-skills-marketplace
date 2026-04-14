# Ruby, PHP, and C# Refactoring Patterns

Combined reference for Ruby, PHP 8+, and C#/.NET. Each language has fewer
unique patterns than JS/TS or Python, so they're consolidated here.

## Table of Contents

1. [Ruby Patterns](#ruby)
2. [PHP 8+ Patterns](#php)
3. [C# / .NET Patterns](#csharp)

---

## Ruby

### 1. Frozen String Literals
**Risk: Very Low**
```ruby
# Add to top of every file:
# frozen_string_literal: true
```
- Prevents unintended string mutation; improves memory
- Safety: May break code that mutates string literals (use .dup)

### 2. Keyword Arguments
**Risk: Low**
```ruby
# Before
def create_user(name, email, role)

# After
def create_user(name:, email:, role: 'user')
```
- Safety: Update ALL call sites to use keyword syntax

### 3. Pattern Matching (Ruby 3+)
**Risk: Low**
```ruby
# Before
case response
when Hash then process_hash(response)
when Array then process_array(response)
end

# After
case response
in { status: 200, body: String => body }
  process_success(body)
in { status: 404 }
  handle_not_found
end
```

### 4. Hash Shorthand (Ruby 3.1+)
**Risk: Very Low**
```ruby
# Before: { name: name, email: email }
# After:  { name:, email: }
```

### 5. Endless Methods (Ruby 3+)
**Risk: Very Low**
```ruby
# Before: def double(x); x * 2; end
# After:  def double(x) = x * 2
```
- When: Single-expression methods only

### Tools
| Tool | Command |
|------|---------|
| RuboCop | `rubocop --auto-correct` |
| Reek | `reek .` (code smells) |
| Flog | `flog .` (complexity) |

---

## PHP

### 1. Constructor Promotion (PHP 8.0+)
**Risk: Low**
```php
// Before
class User {
    private string $name;
    private string $email;
    public function __construct(string $name, string $email) {
        $this->name = $name;
        $this->email = $email;
    }
}

// After
class User {
    public function __construct(
        private string $name,
        private string $email,
    ) {}
}
```

### 2. Match Expressions (PHP 8.0+)
**Risk: Low**
```php
// Before
switch ($status) {
    case 'active': $label = 'Active'; break;
    case 'inactive': $label = 'Inactive'; break;
    default: $label = 'Unknown';
}

// After
$label = match($status) {
    'active' => 'Active',
    'inactive' => 'Inactive',
    default => 'Unknown',
};
```
- Safety: `match` uses strict comparison (===) unlike switch (==)

### 3. Typed Properties (PHP 7.4+)
**Risk: Medium**
```php
// Before: public $name;
// After:  public string $name;
```
- Safety: Will throw TypeError on wrong type; verify all assignments

### 4. Enums (PHP 8.1+)
**Risk: Low**
```php
// Before: const STATUS_ACTIVE = 'active';
// After:
enum Status: string {
    case Active = 'active';
    case Inactive = 'inactive';
}
```

### 5. Named Arguments (PHP 8.0+)
**Risk: Low**
```php
// Before: array_slice($arr, 0, 5, true);
// After:  array_slice($arr, offset: 0, length: 5, preserve_keys: true);
```

### Tools
| Tool | Command |
|------|---------|
| PHP CS Fixer | `php-cs-fixer fix .` |
| PHPStan | `phpstan analyse src` |
| Rector | `rector process src` (automated refactoring) |
| Psalm | `psalm --show-info=true` |

---

## C# / .NET

### 1. Records (C# 9+)
**Risk: Medium**
```csharp
// Before
public class Point {
    public int X { get; init; }
    public int Y { get; init; }
    // Equals, GetHashCode, ToString...
}

// After
public record Point(int X, int Y);
```
- Records have value-based equality by default
- Safety: Check code that compares by reference (==)

### 2. Pattern Matching (C# 8+)
**Risk: Low**
```csharp
// Before
if (shape is Circle) { var c = (Circle)shape; return c.Radius * c.Radius * Math.PI; }

// After
return shape switch {
    Circle c => c.Radius * c.Radius * Math.PI,
    Rectangle r => r.Width * r.Height,
    _ => 0
};
```

### 3. Nullable Reference Types (C# 8+)
**Risk: High** (breaking change)
```csharp
// Enable in .csproj: <Nullable>enable</Nullable>
// Then: string? nullable, string nonNullable
```
- Safety: VERY HIGH RISK — generates warnings everywhere
- Strategy: Enable per-file with `#nullable enable`, fix incrementally

### 4. Async Streams (C# 8+)
**Risk: Medium**
```csharp
// Before: async Task<List<Item>> GetAllAsync()
// After:  async IAsyncEnumerable<Item> GetAllAsync()
```
- When: Processing large datasets incrementally
- Safety: Callers must use `await foreach`

### 5. Global Using Directives (C# 10+)
**Risk: Very Low**
```csharp
// In GlobalUsings.cs:
global using System;
global using System.Collections.Generic;
global using System.Linq;
```
- Reduces repetitive imports across all files

### Tools
| Tool | Command |
|------|---------|
| dotnet format | `dotnet format` |
| Roslynator | VS extension / CLI |
| SonarAnalyzer | NuGet package |
| JetBrains Rider | Built-in refactoring |
