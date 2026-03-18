# Error Handling and Error Boundary Preservation Reference

## Table of Contents
1. [React Error Boundary Fundamentals](#react-error-boundary-fundamentals)
2. [Error Boundary Patterns & Placement](#error-boundary-patterns--placement)
3. [API Error Handling Chains](#api-error-handling-chains)
4. [Toast/Notification Systems](#toastnotification-systems)
5. [Form Error Handling](#form-error-handling)
6. [Loading State Preservation](#loading-state-preservation)
7. [Common Error Handling Breakages](#common-error-handling-breakages)
8. [Preservation Checklist](#preservation-checklist)

---

## React Error Boundary Fundamentals

### What Error Boundaries Can and Cannot Catch

**Error Boundaries CATCH:**
- Rendering errors in child components
- Lifecycle method errors (constructor, render, componentDidMount, etc.)
- Errors in constructors of child components
- Errors during component render phase

**Error Boundaries CANNOT CATCH:**
- Event handler errors (onClick, onChange, etc.)
- Asynchronous code (setTimeout, Promises, async/await)
- Server-side rendering (SSR) errors
- Errors in the error boundary itself
- Error boundary's own constructor or render

### Why This Matters for Workflow-Guardian

When you add new features that interact with event handlers or async operations, you CANNOT rely on error boundaries alone. You must implement complementary error handling:

```javascript
// DANGER: This error will NOT be caught by error boundary
function MyComponent() {
  const handleClick = () => {
    throw new Error('This will crash silently!');
  };

  return <button onClick={handleClick}>Click me</button>;
}

// SAFE: Error is caught and handled
function MyComponent() {
  const handleClick = () => {
    try {
      throw new Error('This is caught');
    } catch (error) {
      toast.error(error.message);
    }
  };

  return <button onClick={handleClick}>Click me</button>;
}
```

### Class-Based Error Boundary (The Only Way in React)

Error boundaries MUST be class components. Functional component equivalents don't exist yet (React 18+).

```javascript
// ✅ CORRECT: Class-based error boundary
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so next render shows fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log error to service (Sentry, LogRocket, etc.)
    console.error('Error caught:', error, errorInfo);
    // errorInfo contains componentStack showing where error originated
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-fallback">
          <h2>Something went wrong</h2>
          <details style={{ whiteSpace: 'pre-wrap' }}>
            {this.state.error?.toString()}
          </details>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// ❌ WRONG: Functional component error boundary
function ErrorBoundary({ children }) {
  // This will NOT catch errors from children
  return children;
}
```

### Using react-error-boundary for Modern Code

The `react-error-boundary` library provides a functional component approach:

```javascript
import { ErrorBoundary } from 'react-error-boundary';

function ErrorFallback({ error, resetErrorBoundary }) {
  return (
    <div role="alert">
      <p>Something went wrong:</p>
      <pre>{error.message}</pre>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
}

// Usage
<ErrorBoundary FallbackComponent={ErrorFallback}>
  <MyComponent />
</ErrorBoundary>
```

Benefits:
- Works with functional components
- Automatic reset functionality
- useErrorBoundary hook for manual error handling in event handlers
- Better TypeScript support

---

## Error Boundary Patterns & Placement

### Strategic Placement Strategy

**DO NOT** wrap your entire app in one generic error boundary. Instead, use **nested boundaries** at multiple levels:

```javascript
// ✅ CORRECT: Multi-level error boundaries

export function App() {
  return (
    <ErrorBoundary FallbackComponent={AppErrorFallback}>
      <Header />

      <ErrorBoundary FallbackComponent={SidebarErrorFallback}>
        <Sidebar />
      </ErrorBoundary>

      <main>
        <ErrorBoundary FallbackComponent={ContentErrorFallback}>
          <RouterOutlet />
        </ErrorBoundary>

        <ErrorBoundary FallbackComponent={ChatErrorFallback}>
          <ChatPanel />
        </ErrorBoundary>
      </main>
    </ErrorBoundary>
  );
}
```

**Why this structure matters:**
- If Sidebar crashes, only Sidebar shows error state
- If ChatPanel crashes, the entire page doesn't go down
- Users can still interact with working parts of the app
- Error messages are contextually relevant to each section

### Three-Level Error Boundary Architecture

#### Level 1: Application-Level Boundary
```javascript
// Catches unexpected catastrophic errors
class AppErrorBoundary extends React.Component {
  render() {
    if (this.state.hasError) {
      return (
        <div className="app-error-page">
          <h1>Application Error</h1>
          <p>We're experiencing technical difficulties.</p>
          <button onClick={() => window.location.reload()}>
            Reload Application
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
```

#### Level 2: Feature-Level Boundary
```javascript
// Catches errors in specific features (Dashboard, Reports, etc.)
function FeatureErrorBoundary({ featureName, children }) {
  return (
    <ErrorBoundary
      FallbackComponent={({ error, resetErrorBoundary }) => (
        <div className="feature-error">
          <h3>{featureName} unavailable</h3>
          <p>Try refreshing or returning to dashboard</p>
          <button onClick={resetErrorBoundary}>Retry {featureName}</button>
        </div>
      )}
    >
      {children}
    </ErrorBoundary>
  );
}
```

#### Level 3: Component-Level Boundary
```javascript
// Wraps individual risky components
<ErrorBoundary FallbackComponent={SingleComponentError}>
  <DataVisualizationChart />
</ErrorBoundary>
```

### Error Boundary Placement Checklist

When adding a new component, decide on boundary placement:

```
New component added?
├─ Does it render complex logic?
│  └─ Yes → Consider component-level boundary
├─ Is it an optional feature?
│  └─ Yes → Definitely add boundary
├─ Could its error affect sibling components?
│  └─ Yes → Add boundary above it
├─ Is it a page-like section?
│  └─ Yes → Add feature-level boundary
└─ Query: Would users want to retry this in isolation?
   └─ Yes → Add ErrorBoundary with retry button
```

### Propagation Through Nested Boundaries

Error boundaries walk UP the component tree to find a handler:

```javascript
// Component tree visualization
<App> {/* AppErrorBoundary - Level 1 */}
  <Sidebar> {/* SidebarErrorBoundary - Level 2 */}
    <NavItem>
      <UserProfile> {/* Throws error here */}
    </NavItem>
  </Sidebar>
</App>

// Error propagation path:
// 1. UserProfile throws error
// 2. NavItem doesn't catch → propagates up
// 3. Sidebar doesn't catch → propagates up
// 4. SidebarErrorBoundary catches → shows fallback UI
// 5. Never reaches AppErrorBoundary
```

---

## API Error Handling Chains

### Axios Interceptor Global Error Handler

The standard pattern for consistent API error handling:

```javascript
// api/axiosInstance.js
import axios from 'axios';
import { toast } from 'sonner'; // or react-toastify

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - Add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor - Global error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Extract error information in consistent format
    const errorData = {
      status: error.response?.status,
      message: error.response?.data?.message || error.message,
      type: error.response?.data?.type || 'API_ERROR',
      originalError: error,
    };

    // Handle specific status codes
    switch (error.response?.status) {
      case 401:
        // Unauthorized - user needs to login
        localStorage.removeItem('authToken');
        toast.error('Session expired. Please log in again.');
        window.location.href = '/login';
        break;

      case 403:
        // Forbidden - user doesn't have permission
        toast.error('You do not have permission to perform this action.');
        break;

      case 404:
        // Not found
        toast.error('The requested resource was not found.');
        break;

      case 422:
        // Validation error - specific field errors
        if (error.response?.data?.errors) {
          // Let component handle field-specific errors
          return Promise.reject(errorData);
        }
        toast.error('Please check your input and try again.');
        break;

      case 500:
        // Server error
        toast.error('Server error. Please try again later.');
        break;

      default:
        toast.error(errorData.message);
    }

    return Promise.reject(errorData);
  }
);

export default apiClient;
```

### Using Axios Instance in Components

```javascript
// SAFE: Follows existing error handling chain
function UserList() {
  const [users, setUsers] = useState([]);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchUsers = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await apiClient.get('/users');
        setUsers(response.data);
      } catch (err) {
        // Error already shown via toast in interceptor
        // Store for component-level handling if needed
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUsers();
  }, []);

  if (isLoading) return <UserListSkeleton />;
  if (error) return <div>Error: {error}</div>;

  return <UserListView users={users} />;
}
```

### Error Response Type Contract

Establish a consistent error shape across your API:

```typescript
// types/api.ts
export interface ApiErrorResponse {
  status: number;
  message: string;
  type: 'VALIDATION_ERROR' | 'AUTH_ERROR' | 'NOT_FOUND' | 'SERVER_ERROR' | 'API_ERROR';
  details?: {
    [fieldName: string]: string[];
  };
  requestId?: string;
}

export interface ApiSuccessResponse<T> {
  status: 'success';
  data: T;
}
```

### Supabase vs Firebase Error Handling Differences

#### Supabase Error Pattern
```javascript
// Supabase returns specific error types
async function fetchData() {
  try {
    const { data, error } = await supabase
      .from('table')
      .select('*');

    if (error) {
      // Error is returned, not thrown
      // Check error.code for specific handling
      if (error.code === 'PGRST116') {
        // Relation not found
        toast.error('Data not found');
      } else {
        toast.error(error.message);
      }
      return null;
    }
    return data;
  } catch (err) {
    // Catch for unexpected errors
    toast.error('Unexpected error occurred');
  }
}
```

#### Firebase Error Pattern
```javascript
// Firebase throws errors directly
async function fetchData() {
  try {
    const snapshot = await getDoc(doc(db, 'collection', 'docId'));
    return snapshot.data();
  } catch (error) {
    // Firebase specific error codes
    if (error.code === 'permission-denied') {
      toast.error('You do not have permission to access this data');
    } else if (error.code === 'not-found') {
      toast.error('Document does not exist');
    } else {
      toast.error('Error fetching data');
    }
  }
}
```

**Workflow-Guardian Rule**: When adding features, match the error handling pattern of your existing database. Don't mix Supabase { error } pattern with Firebase throw pattern.

### Error Propagation Chain

```javascript
// ✅ CORRECT: Error handling chain

// Layer 1: API Client (global interceptors)
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Handle globally
      redirectToLogin();
    }
    return Promise.reject(error);
  }
);

// Layer 2: Hook (local try-catch)
const useFetchUsers = () => {
  const [state, setState] = useState({ data: null, error: null });

  const fetch = async () => {
    try {
      const res = await apiClient.get('/users');
      setState({ data: res.data, error: null });
    } catch (err) {
      // Component-specific handling
      setState({ data: null, error: err });
    }
  };

  return { ...state, fetch };
};

// Layer 3: Component (UI feedback)
function Component() {
  const { data, error, fetch } = useFetchUsers();

  useEffect(() => {
    fetch();
  }, []);

  if (error) return <ErrorMessage error={error} onRetry={fetch} />;
  return <DataView data={data} />;
}
```

---

## Toast/Notification Systems

### Toast Pattern Adoption

Pick ONE toast library and use it consistently. Don't mix:

```javascript
// ❌ WRONG: Mixing different notification systems
toast.error('Error 1'); // sonner
notify('Error 2', { type: 'error' }); // custom
showErrorMessage('Error 3'); // another custom
```

### Standard Toast Usage by Operation Type

#### Success Operations
```javascript
// Sonner pattern (recommended for 2025)
import { toast } from 'sonner';

async function handleCreate() {
  try {
    const result = await apiClient.post('/items', data);
    toast.success('Item created successfully');
    return result;
  } catch (error) {
    // Error shown by interceptor, don't duplicate
    throw error;
  }
}

// React-Toastify pattern (if already in codebase)
import { toast } from 'react-toastify';

async function handleCreate() {
  try {
    const result = await apiClient.post('/items', data);
    toast.success('Item created successfully');
    return result;
  } catch (error) {
    // Interceptor already showed error
    throw error;
  }
}
```

#### Promise-Based Operations with Toast Feedback
```javascript
// Sonner toast.promise() - best for async operations
function DataSync() {
  const handleSync = () => {
    toast.promise(
      apiClient.post('/sync'),
      {
        loading: 'Syncing data...',
        success: 'Data synced successfully',
        error: 'Failed to sync data',
      }
    );
  };

  return <button onClick={handleSync}>Sync Now</button>;
}

// React-Toastify toast.promise()
function DataSync() {
  const handleSync = () => {
    toast.promise(
      apiClient.post('/sync'),
      {
        pending: 'Syncing data...',
        success: 'Data synced successfully',
        error: 'Failed to sync data',
      }
    );
  };

  return <button onClick={handleSync}>Sync Now</button>;
}
```

#### Error-Only Operations
```javascript
// DON'T show toast for errors automatically caught by interceptor
async function fetchData() {
  try {
    return await apiClient.get('/data');
  } catch (error) {
    // Interceptor already showed toast
    // Only add custom toast if additional context needed
    if (error.type === 'SPECIFIC_ERROR') {
      toast.error('Custom error message with context');
    }
  }
}
```

### Toast Stacking and Visibility Control

```javascript
// Sonner - Controls max visible toasts
import { Toaster } from 'sonner';

function App() {
  return (
    <>
      <Toaster
        position="top-right"
        visibleToasts={3} // Max 3 toasts visible
        richColors // Color by type
        expand={false} // Don't expand on hover
      />
      {/* app content */}
    </>
  );
}

// React-Toastify - Uses limit prop
import { ToastContainer } from 'react-toastify';

function App() {
  return (
    <>
      <ToastContainer
        position="top-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        limit={3}
      />
      {/* app content */}
    </>
  );
}
```

### Toast Message Format Standards

Define your organization's toast message standards:

```javascript
// Sonner example with consistent formatting
const toastMessages = {
  // Success: Verb (past tense) + object
  userCreated: 'User created successfully',
  dataSaved: 'Changes saved',
  syncComplete: 'Data synced',

  // Error: Brief explanation + actionable next step
  networkError: 'Network error. Check your connection.',
  authExpired: 'Session expired. Please log in again.',
  validationFailed: 'Please check your input and try again.',

  // Info: Neutral notification
  processing: 'Processing your request...',
  loading: 'Loading data...',
};

// Usage enforces consistency
function MyComponent() {
  const handleSave = async () => {
    try {
      await apiClient.post('/save', data);
      toast.success(toastMessages.dataSaved);
    } catch (error) {
      // Interceptor shows toastMessages.networkError or similar
    }
  };
}
```

---

## Form Error Handling

### Field-Level Validation Pattern (React Hook Form)

```javascript
import { useForm, Controller } from 'react-hook-form';

function RegistrationForm() {
  const { control, handleSubmit, formState: { errors } } = useForm({
    defaultValues: {
      email: '',
      password: '',
      confirmPassword: '',
    },
  });

  const onSubmit = async (data) => {
    try {
      await apiClient.post('/register', data);
      toast.success('Registration successful');
    } catch (error) {
      // Handle server-side validation errors
      if (error.status === 422 && error.details) {
        // Server returned field-specific errors
        // This is handled via react-hook-form setError
      }
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <Controller
        name="email"
        control={control}
        rules={{
          required: 'Email is required',
          pattern: {
            value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
            message: 'Invalid email address',
          },
        }}
        render={({ field }) => (
          <div>
            <input {...field} type="email" placeholder="Email" />
            {errors.email && (
              <span className="error">{errors.email.message}</span>
            )}
          </div>
        )}
      />

      <Controller
        name="password"
        control={control}
        rules={{
          required: 'Password is required',
          minLength: {
            value: 8,
            message: 'Password must be at least 8 characters',
          },
        }}
        render={({ field }) => (
          <div>
            <input {...field} type="password" placeholder="Password" />
            {errors.password && (
              <span className="error">{errors.password.message}</span>
            )}
          </div>
        )}
      />

      <button type="submit">Register</button>
    </form>
  );
}
```

### Server-Side Validation Error Handling

```javascript
// Backend returns validation errors in specific format
// { status: 422, details: { fieldName: ['error message'] } }

function SubmitForm() {
  const { handleSubmit, setError } = useForm();

  const onSubmit = async (data) => {
    try {
      await apiClient.post('/form', data);
    } catch (error) {
      if (error.status === 422 && error.details) {
        // Populate field-specific errors
        Object.entries(error.details).forEach(([field, messages]) => {
          setError(field, {
            type: 'server',
            message: messages[0], // Show first error message
          });
        });
      } else {
        // Show general error
        toast.error('Form submission failed');
      }
    }
  };

  return <form onSubmit={handleSubmit(onSubmit)}>...</form>;
}
```

### Error State Persistence During Re-renders

```javascript
// ❌ WRONG: Error state gets cleared on re-render
function FormField() {
  const [error, setError] = useState(null);

  const handleChange = (value) => {
    setError(null); // Clears error too eagerly
    // Component re-renders, user can't see error
  };
}

// ✅ CORRECT: Use form library's error state
function FormField() {
  const { control, formState: { errors } } = useForm();

  // errors persist until explicitly cleared by form reset
  return (
    <Controller
      name="field"
      control={control}
      render={({ field }) => (
        <>
          <input {...field} />
          {errors.field && <span>{errors.field.message}</span>}
        </>
      )}
    />
  );
}
```

### Matching Existing Form Error Display

Before adding a new form field, observe the pattern:

```javascript
// Existing pattern in your codebase
<div className="form-group">
  <label htmlFor="email">Email</label>
  <input
    id="email"
    type="email"
    className={`form-input ${errors.email ? 'is-invalid' : ''}`}
  />
  {errors.email && (
    <span className="form-error">{errors.email.message}</span>
  )}
</div>

// NEW FIELD: Must match exact structure
<div className="form-group">
  <label htmlFor="username">Username</label>
  <input
    id="username"
    type="text"
    className={`form-input ${errors.username ? 'is-invalid' : ''}`}
  />
  {errors.username && (
    <span className="form-error">{errors.username.message}</span>
  )}
</div>
```

---

## Loading State Preservation

### Skeleton/Spinner Pattern Consistency

```javascript
// Define loading UI patterns once
const LoadingPatterns = {
  // For text content
  textSkeleton: <Skeleton className="h-4 w-3/4" />,

  // For full component
  componentSkeleton: (
    <div className="space-y-4">
      <Skeleton className="h-12 w-full" />
      <Skeleton className="h-40 w-full" />
      <Skeleton className="h-10 w-1/4" />
    </div>
  ),

  // For lists
  listSkeleton: (
    <div className="space-y-2">
      {[1, 2, 3].map(i => (
        <Skeleton key={i} className="h-16 w-full" />
      ))}
    </div>
  ),
};

// Use consistently across components
function UserProfile() {
  const { data, isLoading } = useUser();

  if (isLoading) return LoadingPatterns.componentSkeleton;
  return <UserView user={data} />;
}

function UserList() {
  const { data, isLoading } = useUsers();

  if (isLoading) return LoadingPatterns.listSkeleton;
  return <ListView items={data} />;
}
```

### React Query/SWR Loading State Pattern

```javascript
import { useQuery } from '@tanstack/react-query';

function DataComponent() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['data'],
    queryFn: () => apiClient.get('/data').then(res => res.data),
  });

  // Three clear states
  if (isLoading) return <Skeleton />;
  if (error) return <ErrorMessage error={error} />;
  return <DataView data={data} />;
}
```

### Suspense Fallback Pattern

```javascript
import { Suspense } from 'react';

// Pair each async component with a fallback
<Suspense fallback={<ComponentSkeleton />}>
  <AsyncDataComponent />
</Suspense>

// ✅ CORRECT: Suspense with error boundary
<ErrorBoundary FallbackComponent={ErrorFallback}>
  <Suspense fallback={<Loading />}>
    <AsyncContent />
  </Suspense>
</ErrorBoundary>
```

### Loading State Management Hook

```javascript
// Custom hook for consistent loading patterns
function useLoadingState() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = async (asyncFn) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await asyncFn();
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  return { isLoading, error, execute };
}

// Usage - follows same pattern everywhere
function Component() {
  const { isLoading, error, execute } = useLoadingState();

  const handleAction = () => execute(async () => {
    await apiClient.post('/action');
  });

  if (isLoading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;
  return <Button onClick={handleAction}>Do Action</Button>;
}
```

---

## Common Error Handling Breakages

### Breakage 1: Adding Async Code Without Error Handling

```javascript
// ❌ DANGER: Async error will be swallowed
function MyComponent() {
  useEffect(() => {
    // This promise rejection is unhandled
    fetchData().then(setData);
  }, []);

  return <div>{data}</div>;
}

// ✅ SAFE: Proper async error handling
function MyComponent() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    let mounted = true;

    const loadData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const result = await fetchData();
        if (mounted) setData(result);
      } catch (err) {
        if (mounted) setError(err);
        // Error also shown via toast in interceptor
      } finally {
        if (mounted) setIsLoading(false);
      }
    };

    loadData();

    return () => {
      mounted = false;
    };
  }, []);

  if (isLoading) return <Skeleton />;
  if (error) return <ErrorMessage error={error} />;
  return <DataView data={data} />;
}
```

### Breakage 2: Empty Catch Blocks (Error Swallowing)

```javascript
// ❌ DANGER: Error disappears silently
try {
  await criticalOperation();
} catch (error) {
  // Silence is NOT golden
}

// ✅ SAFE: Every catch block has a plan
try {
  await criticalOperation();
} catch (error) {
  // Option 1: Log and continue
  console.error('Operation failed:', error);

  // Option 2: Show user feedback
  toast.error('Operation failed, trying again...');

  // Option 3: Rethrow for higher-level handling
  throw error;

  // Option 4: Recover with fallback
  setData(fallbackData);
}
```

### Breakage 3: Breaking Error Propagation Chain

```javascript
// ❌ WRONG: Error chain is broken
class UserService {
  async getUser(id) {
    const response = await fetch(`/api/users/${id}`);
    // Error: didn't check response.ok
    return response.json(); // Might be error response
  }
}

function useUser(id) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    UserService.getUser(id).then(setUser); // No error handling!
  }, [id]);

  return user;
}

// ✅ CORRECT: Unbroken error chain
class UserService {
  async getUser(id) {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch user: ${response.status}`);
    }
    return response.json();
  }
}

function useUser(id) {
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;

    UserService.getUser(id)
      .then(u => mounted && setUser(u))
      .catch(err => mounted && setError(err)); // Error caught

    return () => {
      mounted = false;
    };
  }, [id]);

  return { user, error };
}
```

### Breakage 4: Mixing Error Handling Styles

```javascript
// ❌ INCONSISTENT: Different patterns in same codebase
// Pattern 1: .catch() style
fetchUsers()
  .then(setUsers)
  .catch(err => console.error(err));

// Pattern 2: async/await style (different file)
async function loadData() {
  try {
    const data = await fetchData();
    setData(data);
  } catch (err) {
    console.error(err);
  }
}

// Pattern 3: Promise-based error (different file)
function Component() {
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData()
      .catch(err => setError(err));
  }, []);
}

// ✅ CONSISTENT: All follow async/await pattern
async function loadUsers() {
  try {
    const users = await fetchUsers();
    return users;
  } catch (error) {
    toast.error('Failed to load users');
    throw error;
  }
}

async function loadData() {
  try {
    const data = await fetchData();
    return data;
  } catch (error) {
    toast.error('Failed to load data');
    throw error;
  }
}

function useAsyncData(fetchFn) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;

    (async () => {
      try {
        const result = await fetchFn();
        if (mounted) setData(result);
      } catch (err) {
        if (mounted) setError(err);
      }
    })();

    return () => {
      mounted = false;
    };
  }, [fetchFn]);

  return { data, error };
}
```

### Breakage 5: Not Matching Error Message Format

```javascript
// ❌ INCONSISTENT: Different error messages
function Component1() {
  const handleError = () => {
    toast.error('Error: Could not save data');
  };
}

function Component2() {
  const handleError = () => {
    toast.error('There was a problem saving your work.');
  };
}

function Component3() {
  const handleError = () => {
    toast.error('SAVE FAILED!');
  };
}

// ✅ CONSISTENT: Standardized error messages
const ErrorMessages = {
  saveFailed: 'Failed to save changes. Please try again.',
  loadFailed: 'Failed to load data. Please refresh and try again.',
  networkError: 'Network error. Check your connection.',
  authRequired: 'Please log in to continue.',
  permissionDenied: 'You do not have permission to perform this action.',
};

function Component1() {
  const handleError = () => {
    toast.error(ErrorMessages.saveFailed);
  };
}

function Component2() {
  const handleError = () => {
    toast.error(ErrorMessages.saveFailed);
  };
}

function Component3() {
  const handleError = () => {
    toast.error(ErrorMessages.saveFailed);
  };
}
```

### Breakage 6: Event Handler Errors Not Caught

```javascript
// ❌ DANGER: Error in event handler won't be caught by error boundary
function FormSubmit() {
  const handleClick = () => {
    throw new Error('This disappears!');
  };

  return <button onClick={handleClick}>Submit</button>;
}

// ✅ SAFE: Wrap event handler logic in try-catch
function FormSubmit() {
  const { setError } = useFormContext();

  const handleClick = async () => {
    try {
      // Validation errors thrown here
      validateForm();
      await submitForm();
      toast.success('Form submitted');
    } catch (error) {
      setError(error); // Show to user
      toast.error(error.message);
    }
  };

  return <button onClick={handleClick}>Submit</button>;
}
```

---

## Preservation Checklist

Use this checklist before adding new features to ensure error handling preservation.

### Before Writing Code

- [ ] Identify existing error handling pattern in similar component
- [ ] Identify existing toast system (sonner, react-toastify, custom)
- [ ] Identify existing loading state pattern (skeleton, spinner, suspense)
- [ ] Identify existing API client setup (axios, fetch, Supabase, Firebase)
- [ ] Identify error boundary placement strategy in codebase
- [ ] Check for global error handlers or interceptors

### When Adding API Calls

- [ ] Use existing API client instance (don't create new one)
- [ ] Rely on interceptor for global error handling (401, 500, etc.)
- [ ] Add try-catch for component-specific error handling
- [ ] Use existing error message format from constants
- [ ] Don't duplicate error toast from interceptor
- [ ] Handle field-specific errors (422 validation errors)

### When Adding Components

- [ ] Wrap in error boundary if it handles async operations
- [ ] Match existing loading skeleton pattern
- [ ] Use existing toast system for notifications
- [ ] Don't add console.log/alert in production code
- [ ] Handle event handler errors with try-catch
- [ ] Never swallow errors in catch blocks

### When Adding Forms

- [ ] Use same form library as existing forms (React Hook Form, Formik, etc.)
- [ ] Match field error display CSS classes
- [ ] Match field error message positioning
- [ ] Use same validation pattern (inline, on blur, on submit)
- [ ] Handle server validation errors consistently
- [ ] Preserve error state during re-renders

### When Adding Async Operations

- [ ] Add try-catch wrapper
- [ ] Implement proper loading state
- [ ] Handle cleanup (useEffect return, mounted flag)
- [ ] Don't leave promise rejections unhandled
- [ ] Match existing async error handling style (async/await vs .catch())
- [ ] Show appropriate user feedback (loading → success/error)

### Error Boundary Checklist

- [ ] Is this component inside an error boundary?
- [ ] Would error here crash sibling components?
- [ ] Is this a feature that should fail in isolation?
- [ ] Does component handle async errors (needs try-catch)?
- [ ] Does error boundary have meaningful fallback UI?
- [ ] Does error boundary have retry mechanism?

### Testing Checklist

- [ ] Test happy path (success case)
- [ ] Test API error (simulate 500 error)
- [ ] Test network error (offline)
- [ ] Test validation error (400/422)
- [ ] Test permission error (403)
- [ ] Test not found error (404)
- [ ] Test async error handling (promise rejection)
- [ ] Test event handler error (throw in onClick)
- [ ] Test form error persistence (error survives re-render)
- [ ] Test error boundary fallback (component crash)

---

## Quick Reference: Error Handling by Situation

### Situation: New API Call Added
```javascript
// Step 1: Use existing API client
import apiClient from 'api/axiosInstance';

// Step 2: Wrap in try-catch
try {
  const response = await apiClient.get('/endpoint');
  // Handle success
} catch (error) {
  // Interceptor shows toast for 401, 500, etc.
  // Component-level handling for specific cases
  if (error.status === 422) {
    // Handle validation error
  }
}

// Step 3: Use existing error message format
toast.error(ErrorMessages.loadFailed);

// Step 4: Manage loading state using existing pattern
const { isLoading, error, execute } = useLoadingState();
```

### Situation: New Component Added
```javascript
// Step 1: Check if wrapping in error boundary
<ErrorBoundary FallbackComponent={ComponentError}>
  <MyNewComponent />
</ErrorBoundary>

// Step 2: Use existing skeleton pattern
if (isLoading) return LoadingPatterns.componentSkeleton;

// Step 3: Use existing toast system
import { toast } from 'sonner';
toast.error('Something went wrong');

// Step 4: Handle event handler errors
const handleClick = () => {
  try {
    // Event handler logic
  } catch (error) {
    toast.error(error.message);
  }
};
```

### Situation: New Form Field Added
```javascript
// Step 1: Observe existing form pattern
<div className="form-group">
  <label htmlFor="field">Field</label>
  <input
    id="field"
    className={`form-input ${errors.field ? 'is-invalid' : ''}`}
  />
  {errors.field && (
    <span className="form-error">{errors.field.message}</span>
  )}
</div>

// Step 2: Match validation rules style
rules={{
  required: 'Field is required',
  minLength: { value: 3, message: 'Min 3 characters' },
}}

// Step 3: Use existing error handling for server errors
if (error.status === 422) {
  setError(fieldName, { message: serverError });
}
```

### Situation: Async Operation Added
```javascript
// Step 1: Create proper async function
async function executeOperation() {
  let mounted = true;

  try {
    setIsLoading(true);
    const result = await apiClient.post('/operation');
    if (mounted) setData(result);
    toast.success('Operation successful');
  } catch (error) {
    if (mounted) setError(error);
    // Toast shown by interceptor for standard errors
  } finally {
    if (mounted) setIsLoading(false);
  }

  return () => {
    mounted = false;
  };
}

// Step 2: Use in useEffect
useEffect(() => {
  const cleanup = executeOperation();
  return cleanup;
}, []);
```

---

## References and Further Reading

- [React Error Boundaries Documentation](https://legacy.reactjs.org/docs/error-boundaries.html)
- [Refine: Error Boundaries in React](https://refine.dev/blog/react-error-boundaries/)
- [React Router Error Boundary Guide](https://reactrouter.com/how-to/error-boundary)
- [2026 React Error Boundaries Best Practices](https://oneuptime.com/blog/post/2026-01-15-react-error-boundaries/view)
- [Mastering Error Boundaries: Medium Guide](https://medium.com/@vnkelkar11/using-error-boundary-in-react-a29ded725eee)
- [Modern React Data Fetching Handbook](https://www.freecodecamp.org/news/the-modern-react-data-fetching-handbook-suspense-use-and-errorboundary-explained/)
- [Why Error Boundaries Can't Catch Async Errors](https://medium.com/@bloodturtle/why-react-boundaries-cant-catch-asynchronous-errors-28b9cab07658)
- [LogRocket: React Error Handling Best Practices](https://blog.logrocket.com/react-error-handling-react-error-boundary/)
- [Toast Libraries Comparison 2025](https://blog.logrocket.com/react-toast-libraries-compared-2025/)
- [Axios Interceptors Documentation](https://axios-http.com/docs/interceptors)
- [Building Robust Error Handling with Axios](https://dev.to/riyon_sebastian/building-a-robust-frontend-error-handling-system-with-axios-and-custom-hooks-27k)
- [React Form Validation Guide](https://formspree.io/blog/react-form-validation/)
- [React Hook Form Advanced Usage](https://www.react-hook-form.com/advanced-usage/)
- [Form Validation with TanStack Form](https://tanstack.com/form/latest/docs/framework/react/guides/validation)
- [Better Error Handling in React and Axios](https://seanurgel.dev/blog/better-error-handling-in-react-and-axios)

---

## Document Version History

- **Version 1.0** (February 26, 2025): Initial comprehensive reference covering error boundaries, API error handling, toast systems, form validation, loading states, and common breakage patterns with prevention strategies.

---

**Last Updated**: February 26, 2025
**Audience**: Workflow-Guardian Skill Developers
**Purpose**: Preserve error handling patterns when adding new features
