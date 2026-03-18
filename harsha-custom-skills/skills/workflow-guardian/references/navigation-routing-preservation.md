# Navigation and Routing Preservation Reference

## Overview

This reference provides defensive patterns for preserving routing configurations when adding features to React applications. The core principle is **OBSERVE and MATCH, don't fix**: when adding routes or navigation features, maintain the existing architectural patterns rather than reorganizing the routing structure.

Breaking routes makes entire pages inaccessible. This document covers the critical patterns that must be preserved across React Router v5, v6, and v7.

---

## Table of Contents

1. [React Router Version Differences](#react-router-version-differences)
2. [Route Definition Patterns](#route-definition-patterns)
3. [Protected Routes and Authentication](#protected-routes-and-authentication)
4. [Nested Routes and Layout Patterns](#nested-routes-and-layout-patterns)
5. [Route Parameters and Data](#route-parameters-and-data)
6. [Safe Route Addition Patterns](#safe-route-addition-patterns)
7. [Lazy Loading and Code Splitting](#lazy-loading-and-code-splitting)
8. [Navigation State Preservation](#navigation-state-preservation)
9. [Common Route Breakage Patterns](#common-route-breakage-patterns)
10. [Pre-Addition Checklist](#pre-addition-checklist)
11. [References and Resources](#references-and-resources)

---

## React Router Version Differences

### React Router v5 (Legacy)
- Uses `<Route>` with `component` or `render` props
- Route order matters (first match wins)
- `useHistory` hook for programmatic navigation
- Path matching uses path-to-regexp with advanced patterns
- No built-in nested routing with Outlet
- Protected routes require higher-order components

### React Router v6 (Current Standard)
- Uses `<Route>` with `element` prop (JSX)
- Route order doesn't matter (best match wins)
- `useNavigate` hook replaces `useHistory`
- Simplified path matching with `:id` params and `*` wildcards only
- `<Outlet>` component for nested route rendering
- Nested routes as parent-child relationships
- Non-breaking upgrade available

### React Router v7 (Latest)
- Non-breaking upgrade from v6
- Three operating modes: declarative, data, and framework
- Framework mode combines React Router with Remix features
- Enhanced TypeScript support
- Data loaders for pre-route-render data fetching
- All v6 hooks unchanged: `useNavigate`, `useParams`, `useLocation`, `useSearchParams`
- ScrollRestoration for automatic scroll position management

### Critical Migration Point: v5 to v6

**Danger Zones When Upgrading:**

1. **Component to Element Conversion**
   ```javascript
   // v5 - DON'T KEEP THIS
   <Route path="/dashboard" component={Dashboard} />

   // v6 - DO THIS
   <Route path="/dashboard" element={<Dashboard />} />
   ```

2. **History to Navigate**
   ```javascript
   // v5
   import { useHistory } from 'react-router-dom';
   const history = useHistory();
   history.push('/dashboard');

   // v6
   import { useNavigate } from 'react-router-dom';
   const navigate = useNavigate();
   navigate('/dashboard');
   ```

3. **Route Order No Longer Matters**
   - v5: Specific routes before general routes (critical)
   - v6: All routes evaluated; best match wins
   - v7: Same as v6

---

## Route Definition Patterns

### v5 Basic Routes
```javascript
// app/router/v5-routes.js
import { BrowserRouter, Route, Switch } from 'react-router-dom';
import Dashboard from '../pages/Dashboard';
import Products from '../pages/Products';
import ProductDetail from '../pages/ProductDetail';
import NotFound from '../pages/NotFound';

export function AppRoutes() {
  return (
    <BrowserRouter>
      <Switch>
        {/* More specific routes come first in v5 */}
        <Route exact path="/" component={Dashboard} />
        <Route exact path="/products" component={Products} />
        <Route path="/products/:id" component={ProductDetail} />

        {/* Catch-all at the end */}
        <Route component={NotFound} />
      </Switch>
    </BrowserRouter>
  );
}
```

### v6 Route Structure
```javascript
// app/router/v6-routes.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from '../pages/Dashboard';
import Products from '../pages/Products';
import ProductDetail from '../pages/ProductDetail';
import NotFound from '../pages/NotFound';

export function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Route order doesn't matter in v6 */}
        <Route path="/" element={<Dashboard />} />
        <Route path="/products" element={<Products />} />
        <Route path="/products/:id" element={<ProductDetail />} />

        {/* Catch-all wildcard at the end */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
```

### v7 Framework Mode Routes
```javascript
// app/router/v7-framework-routes.jsx
import { Route } from 'react-router-dom';
import { loader as dashboardLoader } from '../pages/Dashboard';
import { loader as productLoader } from '../pages/ProductDetail';
import Dashboard from '../pages/Dashboard';
import ProductDetail from '../pages/ProductDetail';

export const routes = [
  {
    path: '/',
    element: <Dashboard />,
    loader: dashboardLoader,
  },
  {
    path: '/products/:id',
    element: <ProductDetail />,
    loader: productLoader,
  },
];
```

### Key Observation Points When Adding Routes

When adding a new route, OBSERVE:
- Is the app using JSX routes (`<Routes>`) or configuration objects?
- What version of React Router? (Check imports: `useHistory` = v5, `useNavigate` = v6+)
- Where is the catch-all route? (Must stay at the end)
- Are there layout routes wrapping groups of routes?
- What naming convention is used for route files?

MATCH:
- Use the same `element={<Component />}` pattern (v6+) or `component={Component}` (v5)
- Add your route in the same location conceptually (before catch-all)
- Follow the same parameter naming conventions
- Use the same directory structure

---

## Protected Routes and Authentication

### v5 Higher-Order Component Pattern
```javascript
// app/routes/PrivateRoute.jsx - v5 PATTERN
import { Route, Redirect } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export function PrivateRoute({ component: Component, ...rest }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <Route
      {...rest}
      render={(props) =>
        isAuthenticated ? (
          <Component {...props} />
        ) : (
          <Redirect to="/login" />
        )
      }
    />
  );
}

// Usage in v5
<Switch>
  <Route path="/login" component={Login} />
  <PrivateRoute path="/dashboard" component={Dashboard} />
</Switch>
```

### v6+ Nested Protected Routes Pattern
```javascript
// app/routes/ProtectedRoute.jsx - v6/v7 PATTERN
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
}

// Usage in v6/v7
<Routes>
  <Route path="/login" element={<Login />} />

  {/* All child routes are protected */}
  <Route element={<ProtectedRoute />}>
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/settings" element={<Settings />} />
    <Route path="/profile" element={<Profile />} />
  </Route>
</Routes>
```

### Context-Based Auth Management
```javascript
// app/context/AuthContext.jsx
import { createContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Check authentication status on mount
    checkAuthStatus();
  }, []);

  async function checkAuthStatus() {
    try {
      const response = await fetch('/api/auth/status');
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  const value = {
    user,
    isLoading,
    error,
    isAuthenticated: !!user,
    login: async (email, password) => { /* ... */ },
    logout: async () => { /* ... */ },
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

### Role-Based Route Protection
```javascript
// app/routes/RoleProtectedRoute.jsx
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

export function RoleProtectedRoute({ requiredRoles = [] }) {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const hasRequiredRole = requiredRoles.some(role =>
    user.roles.includes(role)
  );

  if (!hasRequiredRole) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <Outlet />;
}

// Usage
<Route element={<RoleProtectedRoute requiredRoles={['admin']} />}>
  <Route path="/admin/users" element={<UserManagement />} />
  <Route path="/admin/settings" element={<AdminSettings />} />
</Route>
```

### Critical Auth Observations

When OBSERVING existing protected routes:
- Where is the auth state stored? (Context, Redux, Zustand?)
- What is the loading state handling pattern?
- Where is the authentication check happening?
- Are roles/permissions checked?
- Where do unauthenticated users redirect?

When MATCHING new protected routes:
- Use the same auth hook/context
- Maintain the same redirect destination
- Preserve the same loading state UI
- Keep the same permission checking logic

---

## Nested Routes and Layout Patterns

### v6/v7 Nested Layout Routes
```javascript
// app/pages/Layout.jsx
import { Outlet } from 'react-router-dom';
import { Header } from '../components/Header';
import { Sidebar } from '../components/Sidebar';

export function Layout() {
  return (
    <div className="app-container">
      <Header />
      <div className="main-content">
        <Sidebar />
        <div className="content-area">
          {/* Nested route components render here */}
          <Outlet />
        </div>
      </div>
    </div>
  );
}

// app/router/routes.jsx
<Routes>
  {/* Public routes without layout */}
  <Route path="/login" element={<Login />} />
  <Route path="/signup" element={<Signup />} />

  {/* All routes within this element share the Layout */}
  <Route element={<Layout />}>
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/projects" element={<Projects />} />
    <Route path="/projects/:id" element={<ProjectDetail />} />
    <Route path="/settings" element={<Settings />} />
  </Route>

  {/* 404 catch-all */}
  <Route path="*" element={<NotFound />} />
</Routes>
```

### Multi-Level Nested Routes with Layout Inheritance
```javascript
// app/router/routes.jsx
<Routes>
  <Route element={<Layout />}>
    {/* Dashboard section */}
    <Route path="/dashboard" element={<Dashboard />} />

    {/* Projects section with nested layout */}
    <Route path="/projects" element={<ProjectsLayout />}>
      <Route index element={<ProjectsList />} />
      <Route path=":id" element={<ProjectDetail />}>
        <Route path="overview" element={<ProjectOverview />} />
        <Route path="settings" element={<ProjectSettings />} />
        <Route path="team" element={<ProjectTeam />} />
      </Route>
    </Route>

    {/* Settings section */}
    <Route path="/settings" element={<SettingsLayout />}>
      <Route path="profile" element={<ProfileSettings />} />
      <Route path="account" element={<AccountSettings />} />
      <Route path="notifications" element={<NotificationSettings />} />
    </Route>
  </Route>

  <Route path="*" element={<NotFound />} />
</Routes>
```

### Layout-Only Routes (No URL Segment)
```javascript
// Some applications have layout routes that don't add to the URL
<Routes>
  <Route element={<AuthLayout />}>
    <Route path="/login" element={<Login />} />
    <Route path="/signup" element={<Signup />} />
    <Route path="/forgot-password" element={<ForgotPassword />} />
  </Route>

  <Route element={<MainLayout />}>
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/projects" element={<Projects />} />
  </Route>

  <Route path="*" element={<NotFound />} />
</Routes>
```

### Outlet with Index Routes
```javascript
// Using index routes to set default child content
<Routes>
  <Route path="/projects" element={<ProjectsLayout />}>
    {/* This renders when exactly at /projects */}
    <Route index element={<ProjectsList />} />

    {/* These render at /projects/:id */}
    <Route path=":id" element={<ProjectDetail />} />
  </Route>
</Routes>
```

### Critical Nested Route Observations

When OBSERVING existing nested routes:
- How many layout levels exist?
- Which routes share the same layout?
- Are there index routes?
- How does Outlet positioning affect layout?
- What data flows between parent and child routes?

When MATCHING new nested routes:
- Add routes at the correct nesting level
- Preserve the Outlet positioning
- Don't modify existing layout components
- Maintain the same data flow pattern
- Keep index routes if present in the section

---

## Route Parameters and Data

### useParams Hook (v6/v7)
```javascript
// app/pages/ProductDetail.jsx
import { useParams, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';

export function ProductDetail() {
  const { id } = useParams(); // id is always a string
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch product by ID
    fetch(`/api/products/${id}`)
      .then(res => res.json())
      .then(data => setProduct(data))
      .finally(() => setLoading(false));
  }, [id]); // Re-fetch if ID changes

  if (loading) return <LoadingSpinner />;
  if (!product) return <div>Product not found</div>;

  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <button onClick={() => navigate(-1)}>Back</button>
    </div>
  );
}

// Route definition
<Route path="/products/:id" element={<ProductDetail />} />
```

### Multiple Route Parameters
```javascript
// app/pages/TaskDetail.jsx
import { useParams } from 'react-router-dom';

export function TaskDetail() {
  const { projectId, taskId } = useParams();

  return (
    <div>
      <h1>Project {projectId}</h1>
      <h2>Task {taskId}</h2>
    </div>
  );
}

// Route definition
<Route path="/projects/:projectId/tasks/:taskId" element={<TaskDetail />} />
```

### Query Parameters (useSearchParams)
```javascript
// app/pages/Products.jsx
import { useSearchParams } from 'react-router-dom';

export function Products() {
  const [searchParams, setSearchParams] = useSearchParams();

  const category = searchParams.get('category');
  const page = searchParams.get('page') || '1';
  const sort = searchParams.get('sort') || 'name';

  function handleFilterChange(newCategory) {
    setSearchParams({
      category: newCategory,
      page: '1', // Reset pagination
      sort
    });
  }

  return (
    <div>
      <ProductFilter
        category={category}
        onCategoryChange={handleFilterChange}
      />
      {/* Display products for current category and page */}
    </div>
  );
}

// Usage: /products?category=electronics&page=2&sort=price
```

### v7 Data Loaders (Pre-Route-Load Data)
```javascript
// app/pages/ProjectDetail.jsx
import { useLoaderData, Await } from 'react-router-dom';
import { Suspense } from 'react';

// This runs before the component renders
export async function loader({ params }) {
  const projectId = params.id;
  const projectPromise = fetch(`/api/projects/${projectId}`)
    .then(r => r.json());

  return { projectPromise };
}

export function ProjectDetail() {
  const { projectPromise } = useLoaderData();

  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Await resolve={projectPromise}>
        {(project) => (
          <div>
            <h1>{project.name}</h1>
            {/* Content */}
          </div>
        )}
      </Await>
    </Suspense>
  );
}

// Route configuration
{
  path: '/projects/:id',
  element: <ProjectDetail />,
  loader: loader,
}
```

### Route Parameters Validation
```javascript
// app/pages/UserProfile.jsx
import { useParams, useNavigate } from 'react-router-dom';
import { useEffect } from 'react';

export function UserProfile() {
  const { userId } = useParams();
  const navigate = useNavigate();

  // Validate that userId is a valid number
  useEffect(() => {
    if (!userId || isNaN(parseInt(userId))) {
      navigate('/404', { replace: true });
    }
  }, [userId, navigate]);

  // Rest of component...
}
```

### Critical Parameter Observations

When OBSERVING existing parameter patterns:
- Are parameters validated?
- What type should parameters be (string, number)?
- Are there multiple levels of nesting?
- How are URL query strings used?
- Are loaders used (v7) or client-side fetching?

When MATCHING new parameters:
- Use the same naming conventions
- Add validation at the same level
- Preserve data fetching patterns
- Keep query string patterns consistent

---

## Safe Route Addition Patterns

### Pattern: Adding a Route to an Existing Group

**DANGEROUS:**
```javascript
// DON'T reorganize or restructure existing routes
// DON'T move routes around
// DON'T change route wrapper components
<Routes>
  <Route element={<Layout />}>
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/analytics" element={<Analytics />} />  {/* NEW */}
    <Route path="/projects" element={<Projects />} />
    <Route path="/settings" element={<Settings />} />
  </Route>
</Routes>
```

**SAFE:**
```javascript
// DO observe the existing structure
// DO add the route in the same nesting level
// DO follow the same naming patterns
// DO keep the route before any catch-all
<Routes>
  <Route element={<Layout />}>
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/projects" element={<Projects />} />
    <Route path="/analytics" element={<Analytics />} />  {/* ADDED - same level, same style */}
    <Route path="/settings" element={<Settings />} />
  </Route>
  <Route path="*" element={<NotFound />} />
</Routes>
```

### Pattern: Adding Nested Routes

**DANGEROUS:**
```javascript
// DON'T create new layout components unless necessary
// DON'T change the parent route structure
<Route path="/projects" element={<Projects />}>
  <Route index element={<ProjectsList />} />
  <Route path=":id" element={<ProjectDetail />} />
  {/* Wrapping in a new Layout breaks existing routes */}
  <Route element={<NewLayout />}>
    <Route path=":id/teams" element={<ProjectTeams />} />
  </Route>
</Route>
```

**SAFE:**
```javascript
// DO add nested routes in the same container
// DO use the same parent route
// DO add at the same nesting level
<Route path="/projects" element={<Projects />}>
  <Route index element={<ProjectsList />} />
  <Route path=":id" element={<ProjectDetail />} />
  <Route path=":id/teams" element={<ProjectTeams />} />  {/* ADDED - same pattern */}
</Route>
```

### Pattern: Adding Protected Routes

**DANGEROUS:**
```javascript
// DON'T modify the ProtectedRoute component
// DON'T add inline auth logic to new routes
// DON'T create a separate auth check
<Route element={<ProtectedRoute />}>
  <Route path="/dashboard" element={<Dashboard />} />
  <Route path="/profile" element={<Profile />} />
  {/* Inline auth check breaks the protection chain */}
  {user && <Route path="/admin" element={<Admin />} />}
</Route>
```

**SAFE:**
```javascript
// DO add routes inside the existing ProtectedRoute
// DO use the same auth mechanism
// DO preserve the route grouping
<Route element={<ProtectedRoute />}>
  <Route path="/dashboard" element={<Dashboard />} />
  <Route path="/profile" element={<Profile />} />
  <Route path="/admin" element={<Admin />} />  {/* ADDED - same protection */}
</Route>
```

### Pattern: Adding a New Route Section

**DANGEROUS:**
```javascript
// DON'T add BrowserRouter again
// DON'T create parallel routing structures
<Routes>
  <Route element={<Layout />}>
    <Route path="/dashboard" element={<Dashboard />} />
  </Route>
</Routes>

{/* WRONG - This breaks the router */}
<BrowserRouter>
  <Routes>
    <Route path="/new-feature" element={<NewFeature />} />
  </Routes>
</BrowserRouter>
```

**SAFE:**
```javascript
// DO add to the existing Routes container
// DO use the same router provider
<Routes>
  <Route element={<Layout />}>
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/new-feature" element={<NewFeature />} />
  </Route>
  <Route path="*" element={<NotFound />} />
</Routes>
```

### Pattern: Handling Catch-All Routes

**DANGEROUS:**
```javascript
// DON'T add routes after the wildcard
// DON'T put catch-all in the middle
<Routes>
  <Route path="/dashboard" element={<Dashboard />} />
  <Route path="*" element={<NotFound />} />
  {/* This route will never be reached */}
  <Route path="/settings" element={<Settings />} />
</Routes>
```

**SAFE:**
```javascript
// DO add all specific routes first
// DO put wildcard at the very end
<Routes>
  <Route path="/dashboard" element={<Dashboard />} />
  <Route path="/settings" element={<Settings />} />
  <Route path="/about" element={<About />} />
  {/* Catch-all goes last */}
  <Route path="*" element={<NotFound />} />
</Routes>
```

### Sidebar/Navigation Menu Updates

Routes are only useful if users can navigate to them. Always update navigation when adding routes.

**DANGEROUS:**
```javascript
// DON'T add a route without updating navigation
// This creates orphaned routes users can't reach
export function Sidebar() {
  return (
    <nav>
      <Link to="/dashboard">Dashboard</Link>
      <Link to="/projects">Projects</Link>
      {/* Users can't find the new /settings route */}
    </nav>
  );
}

// But the route exists
<Route path="/settings" element={<Settings />} />
```

**SAFE:**
```javascript
// DO update navigation when adding routes
export function Sidebar() {
  return (
    <nav>
      <Link to="/dashboard">Dashboard</Link>
      <Link to="/projects">Projects</Link>
      <Link to="/settings">Settings</Link>  {/* ADDED - discoverable */}
    </nav>
  );
}

// Route is also added
<Route path="/settings" element={<Settings />} />
```

### Pre-Addition Verification Checklist

Before adding any route:

1. **Route Structure**
   - [ ] Identify the exact location where the route should be added
   - [ ] Confirm the route doesn't already exist
   - [ ] Check if it's a top-level route or nested route
   - [ ] Verify the catch-all route position (must be last)

2. **Authentication**
   - [ ] Determine if the route requires authentication
   - [ ] Identify the correct protection wrapper
   - [ ] Check if role-based access is needed
   - [ ] Verify redirect destination for unauthorized users

3. **Layout Preservation**
   - [ ] Identify which layout the route belongs to
   - [ ] Confirm the layout component shouldn't be modified
   - [ ] Check for nested layout patterns
   - [ ] Verify Outlet positioning

4. **Parameters and Data**
   - [ ] Determine if route needs parameters
   - [ ] Check existing parameter naming patterns
   - [ ] Verify data fetching approach (loader vs client-side)
   - [ ] Confirm parameter validation requirements

5. **Navigation Integration**
   - [ ] Identify all navigation menus that need updating
   - [ ] Check for breadcrumb components
   - [ ] Verify Link component usage patterns
   - [ ] Update sidebar/nav if necessary

6. **Version-Specific Checks**
   - [ ] Confirm the React Router version being used
   - [ ] Use correct API: `element=` (v6+) vs `component=` (v5)
   - [ ] Use correct hook: `useNavigate` (v6+) vs `useHistory` (v5)
   - [ ] Check for loaders (v7 pattern)

---

## Lazy Loading and Code Splitting

### Basic React.lazy Pattern
```javascript
// app/pages/Analytics.jsx
export function Analytics() {
  return <div>Analytics content</div>;
}

// app/router/routes.jsx
import { lazy, Suspense } from 'react';

const Analytics = lazy(() => import('../pages/Analytics'));
const Reports = lazy(() => import('../pages/Reports'));

<Routes>
  <Route element={<Layout />}>
    <Route path="/dashboard" element={<Dashboard />} />
    <Route
      path="/analytics"
      element={
        <Suspense fallback={<LoadingSpinner />}>
          <Analytics />
        </Suspense>
      }
    />
    <Route
      path="/reports"
      element={
        <Suspense fallback={<LoadingSpinner />}>
          <Reports />
        </Suspense>
      }
    />
  </Route>
</Routes>
```

### Code Splitting with Error Boundaries
```javascript
// app/components/ErrorBoundary.jsx
import { Component } from 'react';

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error loading route:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-container">
          <h2>Failed to load this section</h2>
          <p>Please refresh the page or contact support</p>
        </div>
      );
    }

    return this.props.children;
  }
}

// app/router/routes.jsx
const Analytics = lazy(() => import('../pages/Analytics'));

<Routes>
  <Route
    path="/analytics"
    element={
      <ErrorBoundary>
        <Suspense fallback={<LoadingSpinner />}>
          <Analytics />
        </Suspense>
      </ErrorBoundary>
    }
  />
</Routes>
```

### Webpack Magic Comments for Code Splitting Hints
```javascript
// Providing hints to webpack about chunk naming
const Dashboard = lazy(() =>
  import(
    /* webpackChunkName: "dashboard" */
    '../pages/Dashboard'
  )
);

const Analytics = lazy(() =>
  import(
    /* webpackChunkName: "analytics" */
    /* webpackPrefetch: true */
    '../pages/Analytics'
  )
);

const Reports = lazy(() =>
  import(
    /* webpackChunkName: "reports" */
    /* webpackPreload: true */
    '../pages/Reports'
  )
);
```

### Critical Code Splitting Observations

When OBSERVING existing code splitting:
- Are routes lazy-loaded?
- What is the Suspense fallback UI?
- Are there Error Boundaries?
- What naming convention for chunks?
- Are webpackPrefetch hints used?

When MATCHING new lazy-loaded routes:
- Use the same lazy() + Suspense pattern
- Use the same fallback component
- Preserve Error Boundary wrapping
- Follow chunk naming conventions
- Don't modify import boundaries

### Dangerous Code Splitting Mistakes

**DANGEROUS:**
```javascript
// DON'T import lazy components at the top level
// This defeats the purpose of code splitting
import Analytics from '../pages/Analytics'; // <-- WRONG

const routes = (
  <Routes>
    <Route path="/analytics" element={<Analytics />} />
  </Routes>
);
```

**SAFE:**
```javascript
// DO use dynamic imports with lazy
const Analytics = lazy(() => import('../pages/Analytics'));

const routes = (
  <Routes>
    <Route
      path="/analytics"
      element={
        <Suspense fallback={<LoadingSpinner />}>
          <Analytics />
        </Suspense>
      }
    />
  </Routes>
);
```

---

## Navigation State Preservation

### useNavigate Hook (v6/v7)
```javascript
// app/pages/Dashboard.jsx
import { useNavigate } from 'react-router-dom';

export function Dashboard() {
  const navigate = useNavigate();

  function handleProjectClick(projectId) {
    // Basic navigation
    navigate(`/projects/${projectId}`);
  }

  function handleSaveAndReturn() {
    // Replace history instead of push
    navigate('/dashboard', { replace: true });
  }

  function handleGoBack() {
    // Go back in history
    navigate(-1);
  }

  return (
    <div>
      <button onClick={() => handleProjectClick(123)}>
        Open Project
      </button>
    </div>
  );
}
```

### Passing State Through Navigation
```javascript
// app/pages/ProjectsList.jsx
import { useNavigate } from 'react-router-dom';

export function ProjectsList() {
  const navigate = useNavigate();

  function handleProjectClick(project) {
    // Pass state to next route
    navigate(`/projects/${project.id}`, {
      state: {
        from: 'list',
        previousProject: null,
      },
    });
  }

  return (
    <div>
      {projects.map(project => (
        <button
          key={project.id}
          onClick={() => handleProjectClick(project)}
        >
          {project.name}
        </button>
      ))}
    </div>
  );
}

// app/pages/ProjectDetail.jsx
import { useLocation, useNavigate } from 'react-router-dom';

export function ProjectDetail() {
  const location = useLocation();
  const navigate = useNavigate();

  // Access state from navigation
  const from = location.state?.from; // 'list'

  function handleGoBack() {
    // Preserve navigation context
    if (from === 'list') {
      navigate('/projects');
    } else {
      navigate(-1);
    }
  }

  return (
    <div>
      <button onClick={handleGoBack}>
        Back {from === 'list' && 'to List'}
      </button>
    </div>
  );
}
```

### Breadcrumb Navigation Pattern
```javascript
// app/components/Breadcrumbs.jsx
import { useLocation } from 'react-router-dom';
import { Link } from 'react-router-dom';

export function Breadcrumbs() {
  const location = useLocation();
  const paths = location.pathname.split('/').filter(Boolean);

  const breadcrumbs = paths.map((path, index) => {
    const href = '/' + paths.slice(0, index + 1).join('/');
    const label = path.charAt(0).toUpperCase() + path.slice(1);

    return {
      href,
      label,
    };
  });

  return (
    <nav className="breadcrumbs">
      <Link to="/">Home</Link>
      {breadcrumbs.map((crumb, index) => (
        <span key={index}>
          <span className="separator">/</span>
          <Link to={crumb.href}>{crumb.label}</Link>
        </span>
      ))}
    </nav>
  );
}

// Uses useLocation() internally - must not break location.pathname
```

### Scroll Position Restoration (v6+)
```javascript
// app/components/ScrollRestoration.jsx
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

export function ScrollRestoration() {
  const { pathname } = useLocation();

  useEffect(() => {
    // Scroll to top on route change
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}

// app/App.jsx
<BrowserRouter>
  <ScrollRestoration />
  <Routes>
    {/* routes */}
  </Routes>
</BrowserRouter>
```

### Custom Scroll Restoration with Position Memory
```javascript
// app/hooks/useScrollRestoration.js
import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';

export function useScrollRestoration() {
  const location = useLocation();
  const scrollPositions = useRef({});

  useEffect(() => {
    // Save scroll position before navigation
    return () => {
      scrollPositions.current[location.pathname] =
        window.scrollY;
    };
  }, [location.pathname]);

  useEffect(() => {
    // Restore scroll position after navigation
    const savedPosition = scrollPositions.current[location.pathname];
    if (savedPosition !== undefined) {
      window.scrollTo(0, savedPosition);
    } else {
      window.scrollTo(0, 0);
    }
  }, [location]);
}

// Usage in component
export function Page() {
  useScrollRestoration();
  return <div>Page content</div>;
}
```

### Form State Preservation During Navigation
```javascript
// app/hooks/useFormState.js
import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';

export function useFormState(formKey) {
  const [formData, setFormData] = useState(() => {
    // Load from sessionStorage if available
    const saved = sessionStorage.getItem(formKey);
    return saved ? JSON.parse(saved) : {};
  });

  const location = useLocation();

  useEffect(() => {
    // Save form data to sessionStorage
    sessionStorage.setItem(formKey, JSON.stringify(formData));
  }, [formData, formKey]);

  function clearFormState() {
    sessionStorage.removeItem(formKey);
    setFormData({});
  }

  return { formData, setFormData, clearFormState };
}

// Usage
export function UserForm() {
  const { formData, setFormData } = useFormState('user-form');

  return (
    <form>
      <input
        value={formData.name || ''}
        onChange={(e) => setFormData({
          ...formData,
          name: e.target.value
        })}
      />
    </form>
  );
}
```

### Critical Navigation State Observations

When OBSERVING existing navigation patterns:
- How is navigation triggered? (Links vs useNavigate)
- Is state passed between routes?
- Are breadcrumbs displayed?
- How is scroll position handled?
- Is form state preserved during navigation?

When MATCHING new navigation:
- Use the same navigation method
- Preserve state passing patterns
- Update breadcrumbs if applicable
- Maintain scroll behavior
- Keep form state strategy consistent

---

## Common Route Breakage Patterns

### Breakage 1: Reordering Routes (v5 Only)

**WHAT BREAKS:**
In React Router v5, route order determines matching priority. Reordering routes breaks the first-match-wins logic.

```javascript
// v5 ORIGINAL - Works correctly
<Switch>
  <Route exact path="/" component={Home} />
  <Route path="/products/:id" component={ProductDetail} />
  <Route path="/products" component={Products} />
  <Route component={NotFound} />
</Switch>

// v5 BROKEN - Routes never match in this order
<Switch>
  <Route path="/products" component={Products} />
  {/* /products/123 now matches here instead of ProductDetail */}
  <Route path="/products/:id" component={ProductDetail} />
  <Route exact path="/" component={Home} />
  <Route component={NotFound} />
</Switch>
```

**HOW TO PREVENT:**
- v5: Never reorder routes in Switch
- v6+: Route order doesn't matter (safe to reorder if needed)
- Observe the original order; match it when adding routes

### Breakage 2: Modifying Route Wrapper Components

**WHAT BREAKS:**
Changing or removing layout components that wrap routes breaks the layout for all nested routes.

```javascript
// ORIGINAL - Works
<Routes>
  <Route element={<Layout />}>
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/projects" element={<Projects />} />
  </Route>
</Routes>

// BROKEN - Removing Layout breaks all nested routes
<Routes>
  <Route path="/dashboard" element={<Dashboard />} />
  <Route path="/projects" element={<Projects />} />
  {/* No Layout - header, sidebar, footer gone */}
</Routes>

// BROKEN - Changing Layout component
<Routes>
  <Route element={<NewLayout />}> {/* Different component */}
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/projects" element={<Projects />} />
  </Route>
</Routes>
```

**HOW TO PREVENT:**
- Never modify existing layout wrapper components
- Create new layout components for new route groups
- Preserve Outlet positioning in layouts
- Maintain consistent layout structure

### Breakage 3: Breaking the Auth Guard Chain

**WHAT BREAKS:**
Removing or modifying protection wrappers exposes protected routes.

```javascript
// ORIGINAL - Auth protected
<Routes>
  <Route element={<ProtectedRoute />}>
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/admin" element={<Admin />} />
  </Route>
</Routes>

// BROKEN - Routes are now unprotected
<Routes>
  <Route path="/dashboard" element={<Dashboard />} />
  <Route path="/admin" element={<Admin />} />
  {/* No ProtectedRoute wrapper - unauthenticated users can access */}
</Routes>

// BROKEN - Auth moved inside component (unreliable)
<Routes>
  <Route path="/admin" element={<AdminWithAuth />} />
</Routes>
```

**HOW TO PREVENT:**
- Never remove protection wrappers
- Always add new protected routes inside the wrapper
- Don't move auth logic to individual components
- Maintain the wrapping pattern for all protected sections

### Breakage 4: Catching Routes with Wildcard in Wrong Position

**WHAT BREAKS:**
Placing catch-all routes before specific routes makes specific routes unreachable.

```javascript
// ORIGINAL - Catch-all at the end
<Routes>
  <Route path="/dashboard" element={<Dashboard />} />
  <Route path="/products/:id" element={<ProductDetail />} />
  <Route path="*" element={<NotFound />} />
</Routes>

// BROKEN - Catch-all matches everything before it
<Routes>
  <Route path="*" element={<NotFound />} />
  <Route path="/dashboard" element={<Dashboard />} />
  <Route path="/products/:id" element={<ProductDetail />} />
  {/* These routes are never reached */}
</Routes>

// BROKEN - Wildcard in middle
<Routes>
  <Route path="/dashboard" element={<Dashboard />} />
  <Route path="*" element={<NotFound />} />
  <Route path="/products" element={<Products />} />
  {/* /products never matches */}
</Routes>
```

**HOW TO PREVENT:**
- Always place catch-all `path="*"` as the last route
- Add all specific routes before the wildcard
- Test that expected routes render, not 404
- Verify the order before committing changes

### Breakage 5: Import Order Affecting Tree-Shaking

**WHAT BREAKS:**
Circular imports or incorrect dynamic import patterns break code splitting.

```javascript
// BROKEN - Importing at top level defeats code splitting
import Analytics from '../pages/Analytics';
import Reports from '../pages/Reports';

const routes = [
  {
    path: '/analytics',
    element: <Analytics /> // Not lazy-loaded
  },
  {
    path: '/reports',
    element: <Reports /> // Not lazy-loaded
  }
];

// BROKEN - Circular import pattern
// routes.js imports components
// components import routes
// This breaks bundling

// BROKEN - Wrong dynamic import
const Analytics = () => import('../pages/Analytics');
// This returns a function, not a component
```

**HOW TO PREVENT:**
- Use `lazy(() => import(...))` for lazy routes
- Never import lazy-loadable routes at top level
- Avoid circular import patterns
- Use webpack magic comments correctly

### Breakage 6: Forgetting Navigation Updates

**WHAT BREAKS:**
Adding routes without updating navigation menus makes routes unreachable to users.

```javascript
// ORIGINAL - Route and Navigation in sync
<Sidebar>
  <Link to="/dashboard">Dashboard</Link>
  <Link to="/projects">Projects</Link>
</Sidebar>

// Routing layer
<Route path="/dashboard" element={<Dashboard />} />
<Route path="/projects" element={<Projects />} />

// BROKEN - Route added but not in navigation
<Sidebar>
  <Link to="/dashboard">Dashboard</Link>
  <Link to="/projects">Projects</Link>
  {/* /analytics route exists but isn't linked */}
</Sidebar>

// Routing layer
<Route path="/dashboard" element={<Dashboard />} />
<Route path="/projects" element={<Projects />} />
<Route path="/analytics" element={<Analytics />} /> {/* Hidden from users */}
```

**HOW TO PREVENT:**
- Update navigation whenever adding routes
- Update breadcrumbs if applicable
- Update sitemap or route lists
- Test that all routes are discoverable

### Breakage 7: Parameter Naming Inconsistencies

**WHAT BREAKS:**
Inconsistent parameter names between route definition and component usage.

```javascript
// BROKEN - Parameter name mismatch
<Route path="/products/:productId" element={<ProductDetail />} />

// In ProductDetail
const { id } = useParams(); // Wrong - looks for 'id', not 'productId'

// BROKEN - Parameter validation missing
<Route path="/users/:userId" element={<UserProfile />} />

// In UserProfile
const { userId } = useParams();
// If userId="abc", fetch fails but component doesn't handle it

// CORRECT
<Route path="/products/:id" element={<ProductDetail />} />

// In ProductDetail
const { id } = useParams(); // Matches
useEffect(() => {
  if (!id || isNaN(parseInt(id))) {
    navigate('/404');
    return;
  }
  fetchProduct(id);
}, [id]);
```

**HOW TO PREVENT:**
- Match parameter names between route and component
- Validate parameters in useParams
- Document expected parameter types
- Test with invalid parameters

---

## Additional Preservation Rules

### Version-Specific Import Preservation
```javascript
// v5 imports - preserve if v5 is the version
import { useHistory, Switch } from 'react-router-dom';

// v6+ imports - preserve if v6/v7 is the version
import { useNavigate, Routes } from 'react-router-dom';

// NEVER mix versions
// This breaks the app entirely
import { useHistory, Routes } from 'react-router-dom'; // WRONG
```

### Dynamic Route Configuration Pattern
```javascript
// If the app uses a route configuration object pattern
const routeConfig = [
  { path: '/', element: <Home /> },
  { path: '/products', element: <Products /> },
  { path: '/products/:id', element: <ProductDetail /> },
];

// OBSERVE and MATCH this pattern when adding routes
const routeConfig = [
  { path: '/', element: <Home /> },
  { path: '/products', element: <Products /> },
  { path: '/products/:id', element: <ProductDetail /> },
  { path: '/analytics', element: <Analytics /> }, // ADDED - same format
];
```

### Relative Routes Pattern
```javascript
// Some apps use relative routes in nested structures
<Route path="/projects" element={<ProjectsLayout />}>
  <Route index element={<ProjectsList />} />
  <Route path=":id" element={<ProjectDetail />} />
  {/* Relative to /projects */}
  <Route path=":id/team" element={<ProjectTeam />} />
</Route>

// PRESERVE this pattern - don't change to absolute paths
// DON'T do this:
<Route path="/projects/:id/team" element={<ProjectTeam />} />
```

---

## Pre-Addition Checklist

### Complete Route Addition Checklist

Before adding ANY route, go through this checklist:

#### Route Definition
- [ ] Find the exact Routes container where this route belongs
- [ ] Identify if it's a top-level or nested route
- [ ] Check the current nesting depth
- [ ] Locate the catch-all route (must stay at end)
- [ ] Verify the route doesn't already exist
- [ ] Note the React Router version (imports indicate this)

#### Authentication & Protection
- [ ] Determine if the route requires authentication
- [ ] Identify the protection wrapper used (ProtectedRoute, PrivateRoute, etc.)
- [ ] Check for role-based requirements
- [ ] Verify redirect destination for unauthorized users
- [ ] Add route inside the protection wrapper, not before/after

#### Layout Structure
- [ ] Identify which layout component wraps this section
- [ ] Confirm the Outlet position in the layout
- [ ] Check if layout needs modification (it shouldn't)
- [ ] Verify nested layout inheritance
- [ ] Identify the parent route if applicable

#### Parameters & Data
- [ ] Determine if route has dynamic parameters (:id)
- [ ] Check naming conventions used in app (userId vs user_id)
- [ ] Verify data fetching approach (loader vs useEffect)
- [ ] Identify validation requirements for parameters
- [ ] Check if query parameters are needed

#### Navigation Integration
- [ ] Update main navigation (Sidebar, Header, etc.)
- [ ] Update breadcrumb component if used
- [ ] Check for dynamic navigation builders
- [ ] Update any route-to-label mappings
- [ ] Verify the link text is user-friendly
- [ ] Test navigation link works correctly

#### Code Splitting
- [ ] Check if other routes are lazy-loaded
- [ ] If yes, add lazy loading for new route
- [ ] Verify Suspense fallback UI is consistent
- [ ] Confirm Error Boundary wrapping if used
- [ ] Check webpack chunk naming convention

#### Testing Plan
- [ ] Test the new route renders the correct component
- [ ] Test navigation link works
- [ ] Test back button from new route
- [ ] Test parameters load correct data (if applicable)
- [ ] Test protected routes show login if needed
- [ ] Test catch-all doesn't match the new route
- [ ] Test the new route doesn't break existing routes

#### Version-Specific Checks
- [ ] Use `element={<Component />}` (v6+) not `component={Component}` (v5)
- [ ] Use `useNavigate` (v6+) not `useHistory` (v5)
- [ ] Check if loaders are used (v7 pattern)
- [ ] Verify all imports from same version

---

## References and Resources

### Official Documentation
- [React Router Official Documentation](https://reactrouter.com/) - Latest v7 documentation
- [React Router v7 Release Notes](https://remix.run/blog/react-router-v7) - v7 announcement and features
- [React Router API Reference](https://api.reactrouter.com/v7/functions/react_router.useParams.html) - useParams and other hooks

### Authentication & Protection
- [Authentication with React Router v6: A complete guide - LogRocket](https://blog.logrocket.com/authentication-react-router-v6/)
- [Creating Protected Routes With React Router V6 - Medium](https://medium.com/@dennisivy/creating-protected-routes-with-react-router-v6-2c4bbaf7bc1c)
- [Building Reliable Protected Routes with React Router v7 - DEV Community](https://dev.to/ra1nbow1/building-reliable-protected-routes-with-react-router-v7-1ka0)
- [Protected Routes and Authentication with React Router - UI.dev](https://ui.dev/react-router-protected-routes-authentication)

### Nested Routes & Layout
- [Understanding Layout Components and React Router Outlet - DEV Community](https://dev.to/jps27cse/understanding-layout-components-and-react-router-outlet-in-react-3l2e)
- [The Guide to Nested Routes with React Router - UI.dev](https://ui.dev/react-router-nested-routes)
- [Mastering Layouts in React: In-Depth Guide to Using Outlet and Nested Routing - Medium](https://bk10895.medium.com/mastering-layouts-in-react-in-depth-guide-to-using-outlet-and-nested-routing-4eaaadafa71d)
- [React Router 7: Nested Routes - Robin Wieruch](https://www.robinwieruch.de/react-router-nested-routes/)

### Code Splitting & Performance
- [React Lazy Loading: Boosting Performance with Code Splitting - DEV Community](https://dev.to/shyam0118/react-lazy-loading-boosting-performance-with-code-splitting-45lg)
- [A Comprehensive Guide to React Lazy Loading - TatvaSoft Blog](https://www.tatvasoft.com/outsourcing/2025/11/react-lazy-loading.html)
- [React dynamic imports and route-centric code splitting - LogRocket](https://blog.logrocket.com/react-dynamic-imports-route-centric-code-splitting-guide/)
- [React lazy Hook - React Documentation](https://react.dev/reference/react/lazy)

### Navigation & State Preservation
- [Upgrade Your React Navigation: useNavigate for Efficient Routing - Medium](https://medium.com/@arshguleria1612/upgrade-your-react-navigation-replace-usehistory-with-usenavigate-for-efficient-routing-1708eb7ad672)
- [useNavigate Hook in React Router v6 - Perficient](https://blogs.perficient.com/2024/03/22/usenavigate-navigation-react-router-v6/)
- [Scroll Restoration in React Router - DEV Community](https://dev.to/tene/scroll-restoration-in-react-router-4gnc)
- [ScrollRestoration API Reference - React Router](https://reactrouter.com/6.30.3/components/scroll-restoration)
- [Preserving Form State in Refreshes and Navigation - gal.hagever.com](https://gal.hagever.com/posts/react-forms-and-history-state)

### Route Parameters
- [useParams Hook Guide - Refine](https://refine.dev/blog/react-router-useparams/)
- [Complete Guide to useParams - react.wiki](https://react.wiki/router/use-params-explained/)
- [The Complete Guide to URL parameters with React Router - UI.dev](https://ui.dev/react-router-url-parameters)
- [Navigating Common React Router useParams Pitfalls - DHI Wise](https://www.dhiwise.com/post/troubleshooting-react-router-useparams)

### Common Mistakes & Troubleshooting
- [React Router Common mistakes and how to avoid them - Medium](https://medium.com/@rowsana/react-router-common-mistakes-and-how-to-avoid-them-bc110a6dedfe)
- [Solving Common Routing Issues in React Router - MoldStud](https://moldstud.com/articles/p-solving-common-routing-issues-in-react-router)
- [Catch-All Routes for 404 Handling - OpenReplay Blog](https://blog.openreplay.com/catch-all-routes-404-react-router/)
- [Implementing a Catch All Route with React Router - Utah EDU DevCamp](https://utahedu.devcamp.com/dissecting-react-js/guide/implementing-catch-all-route-react-router)

### Version Upgrade Guides
- [React Router v7 Guide - LogRocket](https://blog.logrocket.com/react-router-v7-guide/)
- [Choosing the right React Router v7 mode - LogRocket](https://blog.logrocket.com/react-router-v7-modes/)
- [React Router: Upgrading from v5 - Official Docs](https://reactrouter.com/docs/en/v6/upgrading/v5)
- [React Router v7 for Non-Framework - Sentry Documentation](https://docs.sentry.io/platforms/javascript/guides/react/features/react-router/v7/)

---

## Final Notes for Skill Implementation

### When Adding Routes, ALWAYS:
1. Observe the current route structure before modifying
2. Match the existing patterns exactly
3. Verify the route is accessible from navigation
4. Test that existing routes still work
5. Check authentication/protection requirements
6. Preserve layout structure

### When Detecting Route Issues, LOOK FOR:
1. Routes added after catch-all wildcard
2. Layout components being modified
3. Auth wrappers being removed
4. Parameter name mismatches
5. Navigation not updated
6. Lazy loading imports changed
7. Route order changed (v5 only)

### Safe Modifications Are:
- Adding routes before catch-all
- Adding links to navigation
- Adding nested routes to existing groups
- Adding lazy loading to existing routes
- Adding validation to parameter handling

### Unsafe Modifications Are:
- Reordering existing routes (v5)
- Removing/changing layout components
- Removing protection wrappers
- Moving catch-all route
- Adding routes after wildcard
- Changing parameter names
- Removing navigation updates
