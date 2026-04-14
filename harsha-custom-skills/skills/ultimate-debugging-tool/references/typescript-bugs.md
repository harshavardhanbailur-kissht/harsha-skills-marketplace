# TypeScript Bug Patterns

**Versions Covered:** TypeScript 5.x through 6.0.2 (TS 7 in Go coming; validated April 2, 2026)

### TS-001: any Type Masking Real Bugs

**Symptom:** Type errors not caught until runtime; refactoring breaks code silently

**Root Cause:** Using `any` type bypasses type checking. Legitimate bugs go undetected

**Detection:**
```typescript
// BUGGY - any type hides bugs
function processData(data: any) {
  return data.toLowerCase(); // What if data is number?
}

const result = processData(42); // No error, crashes at runtime

// BUGGY - any in function signatures
function handleResponse(response: any) {
  const user = response.user; // Could be undefined
  console.log(user.name); // Runtime error
}
```

**Safe Fix:**
```typescript
// Define proper types
interface User {
  id: number;
  name: string;
  email: string;
}

function processData(data: string): string {
  return data.toLowerCase();
}

// Use type guard
function processData(data: string | number): string {
  if (typeof data === 'string') {
    return data.toLowerCase();
  }
  return String(data);
}

// Proper response typing
interface ApiResponse {
  user: User | null;
  error?: string;
}

function handleResponse(response: ApiResponse) {
  if (!response.user) {
    console.error(response.error);
    return;
  }

  console.log(response.user.name); // Type-safe
}

// Utility to catch any usage
type NoAny<T> = T extends any[]
  ? T extends (infer U)[]
    ? U extends any ? never : T
    : never
  : T extends {}
  ? { [K in keyof T]: NoAny<T[K]> }
  : T;

const data: NoAny<any> = {}; // Error: any not allowed
```

**UNSAFE Fix:**
```typescript
// DON'T: Use any to "fix" type errors
interface User {
  name: string;
}

function getUser(): User {
  return fetchUser() as any; // Hides type mismatch
}

// DON'T: Use any in generics
function processArray<T = any>(arr: T[]): T[] {
  return arr.sort((a: any, b: any) => a - b); // Doesn't work for all types
}
```

**Regression Test:**
```typescript
describe('TS-001: any Type', () => {
  it('should not allow any types', () => {
    // @ts-expect-error - any not allowed
    const data: NoAny<any> = {};
  });

  it('should type-check function arguments', () => {
    // @ts-expect-error - number not assignable to string
    processData(42);
  });
});
```

---

### TS-002: Missing Strict Null Checks

**Symptom:** "Cannot read property of undefined" errors in production

**Root Cause:** `strictNullChecks` not enabled. undefined and null treated as any type

**Detection:**
```typescript
// BUGGY - without strictNullChecks
function getName(user: { name: string }) {
  return user.name.toLowerCase(); // Crashes if user is null/undefined
}

const user = fetchUser(); // Could be null
const name = getName(user); // No error

// BUGGY - optional chaining not required
function getEmail(user: User) {
  return user.email; // Error if email is undefined
}
```

**Safe Fix:**
```typescript
// Enable in tsconfig.json
{
  "compilerOptions": {
    "strict": true, // Enables strictNullChecks + other strict flags
    "strictNullChecks": true
  }
}

// Use optional chaining and nullish coalescing
function getName(user: User | null | undefined): string {
  return user?.name.toLowerCase() ?? 'Unknown';
}

// Explicit null handling
function getEmail(user: User | null): string {
  if (!user) {
    throw new Error('User required');
  }

  return user.email ?? 'No email';
}

// Use type guards
function processUser(user: User | null) {
  if (user === null) {
    console.log('No user');
    return;
  }

  // user is User here, not User | null
  console.log(user.name);
}

// Use Optional type
type Optional<T> = T | null | undefined;

function getName(user: Optional<User>): string {
  return user?.name ?? 'Unknown';
}
```

**UNSAFE Fix:**
```typescript
// DON'T: Disable strictNullChecks
{
  "compilerOptions": {
    "strict": false,
    "strictNullChecks": false // Dangerous
  }
}

// DON'T: Use non-null assertion carelessly
function getName(user: User | null) {
  return user!.name; // Crashes if user is null
}
```

**Regression Test:**
```typescript
describe('TS-002: Strict Null Checks', () => {
  it('should require null checks', () => {
    const user: User | null = null;

    // @ts-expect-error - null not handled
    const name = user.name;

    // Correct
    const safeName = user?.name ?? 'Unknown';
    expect(safeName).toBe('Unknown');
  });
});
```

---

### TS-003: Incorrect Type Narrowing

**Symptom:** Type logic errors; wrong code path executed; type confusion

**Root Cause:** Type guards don't actually narrow types correctly. Or type system doesn't recognize narrowing

**Detection:**
```typescript
// BUGGY - type guard doesn't work
function processValue(value: string | number) {
  if (typeof value === 'string') {
    return value.toUpperCase();
  }

  // Still could be string here if guard is wrong
  return value.toFixed(2); // Error: string has no toFixed
}

// BUGGY - union type issue
type Animal = { type: 'dog'; bark: () => void } | { type: 'cat'; meow: () => void };

function makeSound(animal: Animal) {
  if (animal.type === 'dog') {
    animal.meow(); // Should be animal.bark()
  }
}
```

**Safe Fix:**
```typescript
// Strong type guards
function processValue(value: string | number): string {
  if (typeof value === 'string') {
    return value.toUpperCase();
  }

  // value is number here
  return value.toFixed(2);
}

// Custom type guard
function isString(value: unknown): value is string {
  return typeof value === 'string';
}

function processValue(value: unknown): string {
  if (isString(value)) {
    return value.toUpperCase();
  }

  return String(value);
}

// Union type with proper narrowing
type Animal = Dog | Cat;

interface Dog {
  type: 'dog';
  bark: () => void;
}

interface Cat {
  type: 'cat';
  meow: () => void;
}

function makeSound(animal: Animal) {
  switch (animal.type) {
    case 'dog':
      animal.bark(); // Type-safe
      break;
    case 'cat':
      animal.meow(); // Type-safe
      break;
  }
}

// Discriminated unions
type Result = { status: 'success'; data: User } | { status: 'error'; error: string };

function handleResult(result: Result) {
  if (result.status === 'success') {
    console.log(result.data.name); // data exists here
  } else {
    console.log(result.error); // error exists here
  }
}
```

**UNSAFE Fix:**
```typescript
// DON'T: Use type assertion instead of narrowing
function processValue(value: string | number): string {
  return (value as string).toUpperCase(); // Crashes if number
}

// DON'T: Rely on object shape without discriminator
type Animal = { bark?: () => void; meow?: () => void };

function makeSound(animal: Animal) {
  animal.bark?.(); // Might call meow instead
}
```

**Regression Test:**
```typescript
describe('TS-003: Type Narrowing', () => {
  it('should correctly narrow string type', () => {
    function processValue(value: string | number): string {
      if (typeof value === 'string') {
        return value.toUpperCase();
      }
      return value.toFixed(2);
    }

    expect(processValue('hello')).toBe('HELLO');
    expect(processValue(3.14159)).toBe('3.14');
  });

  it('should handle discriminated unions', () => {
    function handleResult(result: Result) {
      if (result.status === 'success') {
        expect(result.data).toBeDefined();
        expect(result.error).toBeUndefined();
      } else {
        expect(result.error).toBeDefined();
        expect(result.data).toBeUndefined();
      }
    }
  });
});
```

---
