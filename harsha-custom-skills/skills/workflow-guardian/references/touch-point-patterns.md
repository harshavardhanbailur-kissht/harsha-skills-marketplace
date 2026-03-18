# Touch Point Patterns for Common Change Types

This reference guide identifies all files and components that must be updated for common change scenarios in React/TypeScript web apps. Use this checklist to prevent incomplete implementations.

---

## 1. Adding a New Field to a Form

When adding a field (e.g., "phone" to user form), update in this order:

- [ ] **Type Definition** (`types/` or `interfaces/`)
  - Add field to TypeScript interface/type
  - Update validation schema if using zod/yup
  - Add JSDoc comments for field purpose

- [ ] **Form Component** (`components/forms/`)
  - Add input element with correct HTML type
  - Add form state/hook for new field
  - Add validation rules and error messages
  - Wire up onChange handlers
  - Update form submission to include field

- [ ] **API/Service Layer** (`services/api.ts` or `api/`)
  - Include field in POST/PUT request payload
  - Update service function signatures
  - Update response type definitions
  - Add field to request transformation if needed

- [ ] **Backend Schema** (if applicable)
  - Database migration script
  - Prisma schema / ORM model
  - API route handler validation
  - Default value handling

- [ ] **List/Table Views** (`components/tables/`, `pages/list/`)
  - Add table column definition
  - Add column header and sorting
  - Add data accessor/getter
  - Update table width calculations

- [ ] **Detail Views** (`pages/detail/`, `components/detailCards/`)
  - Add field display section
  - Add label and formatting
  - Add edit mode support if applicable
  - Update layout grid

- [ ] **Export/Report Features** (`services/export.ts`, `utils/report.ts`)
  - Add field to CSV export mapping
  - Add field to PDF report template
  - Update export column headers
  - Add field to data transformation logic

---

## 2. Adding a New Page/Route

When creating a new page (e.g., "Analytics Dashboard"), update in this order:

- [ ] **Router Configuration** (`router/`, `app.routes.ts`, `Router.tsx`)
  - Add route definition with path and component
  - Set route name/id for navigation
  - Add route-level error boundary if needed
  - Define route parameters if applicable

- [ ] **Navigation Component** (`components/Navigation.tsx`, `components/Sidebar.tsx`)
  - Add menu item/link to navigation
  - Set active state condition matching route
  - Add icon if applicable
  - Add tooltip/description

- [ ] **Role Guards** (`middleware/`, `hooks/useRouteGuard.ts`)
  - Add permission check to route definition
  - Add role-based visibility to navigation link
  - Create route guard component if complex logic
  - Update role permissions configuration

- [ ] **Page Component** (`pages/NewPage.tsx`)
  - Create page following existing pattern
  - Import layout wrapper
  - Add page title/heading
  - Include error boundaries
  - Add loading states

- [ ] **Breadcrumb Updates** (`components/Breadcrumb.tsx`)
  - Add breadcrumb definition for new route
  - Define parent breadcrumb if nested
  - Add breadcrumb label mapping
  - Test breadcrumb navigation

---

## 3. Adding a New User Role

When introducing a new role (e.g., "Auditor"), update in this order:

- [ ] **Role Type Definition** (`types/auth.ts`, `constants/roles.ts`)
  - Add role to role enum
  - Define role string literal union type
  - Add role display name/label
  - Add role icon or color if applicable

- [ ] **Login/Auth System** (`pages/login/`, `auth/`)
  - Add role to login form if user selects role
  - Update role assignment in authentication
  - Update token payload to include role
  - Add role to user profile/session storage
  - Update localStorage/sessionStorage logic

- [ ] **Route Guards** (`middleware/auth.ts`, `hooks/useAuth.ts`)
  - Add role check to protected routes
  - Update role-based route configuration
  - Add role validation in route guards
  - Handle unauthorized role access

- [ ] **Conditional Renders** (throughout app)
  - Find all `useAuth()` calls and role checks
  - Add role-specific UI sections
  - Update visible features based on new role
  - Add role-based button visibility
  - Update navigation based on role

- [ ] **API Permissions** (`backend/middleware/`, `backend/auth/`)
  - Add authorization check to API endpoints
  - Verify role in token before allowing action
  - Add role-specific response filtering
  - Log authorization checks for audit

---

## 4. Adding a New Status/State to a Workflow

When adding workflow status (e.g., "On Hold"), update in this order:

- [ ] **Status Type/Enum** (`types/workflow.ts`, `constants/statuses.ts`)
  - Add status to enum
  - Define status string literal union type
  - Add status label/display text
  - Add status color code
  - Define valid status transitions (state machine)

- [ ] **Status Display Components** (`components/badges/`, `components/status/`)
  - Add badge component styling for new status
  - Add status color mapping
  - Update status dropdown/selector
  - Add status to filter options
  - Update status column renderers

- [ ] **Transition Logic** (`hooks/useWorkflow.ts`, `services/workflow.ts`)
  - Define who can transition to new status
  - Define what statuses can transition to this
  - Add validation before status change
  - Add conditional UI for transition buttons
  - Update transition rules in backend

- [ ] **Dashboard/Analytics** (`pages/dashboard/`, `services/analytics.ts`)
  - Add new status to status count cards
  - Include status in workflow progress charts
  - Update status distribution calculations
  - Add new status to statistics display
  - Update data aggregation queries

- [ ] **Notification Triggers** (`services/notifications.ts`, `backend/notifications/`)
  - Add notification template for status change
  - Define who gets notified of new status
  - Set notification message text
  - Add notification trigger condition
  - Update email/push notification logic

---

## 5. Modifying the Auth System

When changing authentication (e.g., adding OAuth), update in this order:

- [ ] **Auth Context/Provider** (`context/AuthContext.tsx`, `providers/`)
  - Update auth state shape if adding fields
  - Add new auth methods/functions
  - Update login/logout logic
  - Add token refresh mechanism
  - Handle auth errors and redirects

- [ ] **Login Page** (`pages/login/`, `components/Login.tsx`)
  - Add new login method UI (buttons, forms)
  - Update form validation
  - Handle new auth flow response
  - Add loading states for new method
  - Update error message handling

- [ ] **All Route Guards** (`middleware/`, `components/ProtectedRoute.tsx`)
  - Update guard to check new auth state
  - Add fallback for missing auth data
  - Update unauthorized redirect behavior
  - Test auth redirect flows

- [ ] **Token Storage/Refresh** (`utils/storage.ts`, `services/api.ts`)
  - Update token storage mechanism
  - Implement token refresh logic
  - Update token expiry handling
  - Add refresh token storage if applicable
  - Handle token rotation

- [ ] **API Client** (`services/api.ts`, `client/axios.ts`)
  - Add auth headers to all requests
  - Update request interceptors
  - Add token to headers before each call
  - Handle 401 responses with token refresh
  - Update error handling for auth failures

- [ ] **Logout Flow** (`pages/logout/`, `hooks/useAuth.ts`)
  - Clear auth context on logout
  - Remove stored tokens
  - Redirect to login page
  - Clear session data
  - Notify backend of logout if needed

---

## 6. Adding File Upload to an Existing Form

When adding file upload capability (e.g., "document" field), update in this order:

- [ ] **Form State** (`pages/formPage/`, `hooks/useForm.ts`)
  - Add file input element
  - Handle file selection onChange
  - Store file in form state
  - Add file validation (size, type)
  - Display selected file name

- [ ] **Storage Service Integration** (`services/storage.ts`, `services/upload.ts`)
  - Create upload function
  - Add upload to S3/cloud storage service
  - Handle upload progress
  - Return uploaded file URL
  - Handle upload errors

- [ ] **Type Definitions** (`types/`)
  - Add file reference field to data type
  - Create FileUpload interface (name, url, size)
  - Add file validation types
  - Define accepted file types constant

- [ ] **Display Components** (`components/fileUpload/`, `components/filePreview/`)
  - Create file preview component
  - Add download link component
  - Add file delete/remove button
  - Add file size display
  - Handle preview for different file types

- [ ] **Validation** (`utils/validation.ts`, `validators/`)
  - Add file size validation rule
  - Add file type validation
  - Add maximum files validation
  - Update form validation schema
  - Add custom error messages

- [ ] **Error Handling** (`services/upload.ts`, `hooks/useUpload.ts`)
  - Handle network errors during upload
  - Handle storage quota exceeded
  - Add retry logic for failed uploads
  - Display user-friendly error messages
  - Log upload errors

---

## 7. Changing the Database/Backend

When modifying backend schema (e.g., adding new database table), update in this order:

- [ ] **Service Layer Functions** (`services/`, `api.ts`)
  - Update all service functions using affected tables
  - Add/modify fetch queries
  - Add/modify create/update payloads
  - Update response transformations
  - Add new service functions if needed

- [ ] **Type Definitions** (`types/`, `interfaces/`)
  - Update interfaces matching new schema
  - Update API response types
  - Update data transformation types
  - Add new types if new table added
  - Update type exports

- [ ] **Migration Scripts** (`migrations/`, `database/migrations/`)
  - Create migration file with timestamp
  - Write SQL for schema changes
  - Include rollback migration
  - Test migration up and down
  - Document breaking changes

- [ ] **Environment Variables** (`.env`, `.env.example`)
  - Add new environment variables if needed
  - Document required variables
  - Add to CI/CD configuration
  - Update deployment checklist

- [ ] **Backend Models** (`models/`, `schema.prisma`)
  - Update ORM model definitions
  - Add relationships if needed
  - Add indexes for performance
  - Update validation constraints
  - Add database constraints

- [ ] **API Endpoints** (`routes/`, `controllers/`)
  - Update endpoint signatures
  - Update request/response validation
  - Add new endpoints if needed
  - Update endpoint documentation
  - Test all modified endpoints

- [ ] **Frontend API Calls** (`services/api.ts`)
  - Update all API client functions
  - Update request payloads
  - Update response handling
  - Update error handling
  - Update TypeScript types

---

## Verification Checklist Template

Use this template after making changes:

```
[ ] All TypeScript types updated and compiling
[ ] All related components rendering without errors
[ ] Form validation working correctly
[ ] API calls sending correct data format
[ ] API responses match type definitions
[ ] All role/permission checks updated
[ ] Conditional renders working for all roles
[ ] Navigation links correct and accessible
[ ] Database migrations tested
[ ] No console errors in browser DevTools
[ ] No API 400/401/403 errors
[ ] Feature works end-to-end
[ ] Tests updated for new functionality
[ ] Documentation updated
```

---

## Common Miss Patterns

Avoid these common mistakes:

1. **Type Update Without UI** - Updated type but forgot to update form component
2. **Incomplete Navigation** - Added route but forgot to add to sidebar/navbar
3. **Permission Gaps** - Added feature but forgot role guards on route or API
4. **Missing Transitions** - Added status to enum but no state machine validation
5. **Partial Export** - New field added to form but missing from CSV/PDF exports
6. **API Mismatch** - Frontend type differs from backend response schema
7. **Storage Issues** - Forgot to clear storage on logout or role change
8. **No Error Handling** - Added new API call without error state handling
9. **Inconsistent Styling** - New status badge color doesn't match palette
10. **Missing Tests** - Added feature without updating relevant test files

---

## File Location Conventions

Standard directory structure assumed in this guide:

```
src/
  components/      # Reusable React components
  pages/           # Page/route components
  services/        # API and business logic
  types/           # TypeScript interfaces
  constants/       # Enums and constants
  hooks/           # Custom React hooks
  context/         # React Context providers
  middleware/      # Auth and route guards
  utils/           # Helper functions
  router/          # Route configuration
  styles/          # Global styles
database/
  migrations/      # Migration scripts
backend/
  routes/          # API endpoints
  middleware/      # Backend middleware
  controllers/     # Request handlers
```

---

## Related Documents

- `workflow-guardian/guides/code-change-workflow.md` - Step-by-step change process
- `workflow-guardian/references/component-patterns.md` - React component best practices
- `workflow-guardian/references/testing-patterns.md` - Testing checklist for changes
