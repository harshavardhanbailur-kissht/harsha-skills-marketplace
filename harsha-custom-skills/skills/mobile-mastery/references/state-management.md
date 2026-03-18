# Comprehensive State Management Reference

A complete guide to state management across all major mobile development platforms with production-ready code examples, patterns, and decision matrices.

---

## Table of Contents
1. [iOS](#ios)
2. [Android](#android)
3. [React Native](#react-native)
4. [Flutter](#flutter)
5. [Cross-Cutting Concerns](#cross-cutting-concerns)
6. [Decision Matrix](#decision-matrix)

---

## iOS

### SwiftUI Basics: @State and @Binding

`@State` is used for local state within a single view. `@Binding` enables passing mutable references to child views.

```swift
import SwiftUI

// Local state example
struct CounterView: View {
    @State private var count = 0

    var body: some View {
        VStack(spacing: 20) {
            Text("Count: \(count)")
                .font(.title)

            Button("Increment") {
                count += 1
            }

            // Pass binding to child view
            ChildView(value: $count)
        }
    }
}

// Child receives a binding
struct ChildView: View {
    @Binding var value: Int

    var body: some View {
        Button("Decrement in child") {
            value -= 1
        }
    }
}
```

### @Observable (iOS 17+)

Modern replacement for `@StateObject` and `@ObservedObject`. Simpler, more performant syntax.

```swift
import SwiftUI
import Observation

@Observable
final class UserViewModel {
    var username: String = ""
    var email: String = ""
    var isLoading = false
    var error: String?

    func loadUser(id: String) async {
        isLoading = true
        defer { isLoading = false }

        do {
            let user = try await fetchUser(id: id)
            self.username = user.name
            self.email = user.email
        } catch {
            self.error = error.localizedDescription
        }
    }

    private func fetchUser(id: String) async throws -> User {
        // API call
        fatalError("Implement API")
    }
}

struct UserProfileView: View {
    @State private var viewModel = UserViewModel()

    var body: some View {
        VStack {
            if viewModel.isLoading {
                ProgressView()
            } else if let error = viewModel.error {
                Text("Error: \(error)")
                    .foregroundColor(.red)
            } else {
                Form {
                    TextField("Username", text: $viewModel.username)
                    TextField("Email", text: $viewModel.email)
                }
            }
        }
        .task {
            await viewModel.loadUser(id: "123")
        }
    }
}
```

### @EnvironmentObject

For passing objects down the view hierarchy without prop drilling.

```swift
import SwiftUI

@Observable
final class AppState {
    var authToken: String?
    var currentUser: User?
    var isDarkMode = false

    func logout() {
        authToken = nil
        currentUser = nil
    }
}

// Root view injects environment
@main
struct MyApp: App {
    @State private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(appState)
        }
    }
}

// Child view accesses without passing through intermediate views
struct UserSettingsView: View {
    @Environment(AppState.self) var appState

    var body: some View {
        VStack {
            Text("User: \(appState.currentUser?.name ?? "Unknown")")

            Toggle("Dark Mode", isOn: $appState.isDarkMode)

            Button("Logout") {
                appState.logout()
            }
        }
    }
}
```

### The Composable Architecture (TCA)

Production-grade state management with testability, modularity, and powerful composition.

```swift
import ComposableArchitecture

// MARK: - Feature Domain
@Reducer
struct TodoFeature {
    @ObservableState
    struct State: Equatable {
        var todos: [TodoItem] = []
        var newTodoText = ""
        var isLoading = false
        var error: String?
        var editingId: UUID?
    }

    enum Action {
        case loadTodos
        case todosLoaded([TodoItem])
        case addTodo
        case updateNewTodoText(String)
        case deleteTodo(UUID)
        case editTodo(UUID)
        case saveTodo(String)
        case todoError(String)
        case clearError
    }

    var body: some ReducerOf<Self> {
        Reduce { state, action in
            switch action {
            case .loadTodos:
                state.isLoading = true
                return .run { send in
                    do {
                        let todos = try await fetchTodos()
                        await send(.todosLoaded(todos))
                    } catch {
                        await send(.todoError(error.localizedDescription))
                    }
                }

            case let .todosLoaded(todos):
                state.isLoading = false
                state.todos = todos
                return .none

            case .addTodo:
                guard !state.newTodoText.isEmpty else { return .none }

                let newItem = TodoItem(
                    id: UUID(),
                    text: state.newTodoText,
                    isCompleted: false
                )
                state.todos.append(newItem)
                state.newTodoText = ""
                return .none

            case let .updateNewTodoText(text):
                state.newTodoText = text
                return .none

            case let .deleteTodo(id):
                state.todos.removeAll { $0.id == id }
                return .none

            case let .editTodo(id):
                state.editingId = id
                return .none

            case let .saveTodo(text):
                if let index = state.todos.firstIndex(where: { $0.id == state.editingId }) {
                    state.todos[index].text = text
                    state.editingId = nil
                }
                return .none

            case let .todoError(message):
                state.error = message
                return .none

            case .clearError:
                state.error = nil
                return .none
            }
        }
    }

    private func fetchTodos() async throws -> [TodoItem] {
        // API implementation
        fatalError("Implement API")
    }
}

// MARK: - View
struct TodoView: View {
    @Bindable var store: StoreOf<TodoFeature>

    var body: some View {
        NavigationStack {
            VStack {
                HStack {
                    TextField("New todo...", text: $store.newTodoText)

                    Button("Add") {
                        store.send(.addTodo)
                    }
                    .disabled(store.newTodoText.isEmpty)
                }
                .padding()

                List {
                    ForEach(store.todos) { todo in
                        HStack {
                            Text(todo.text)
                            Spacer()
                            Button("Delete") {
                                store.send(.deleteTodo(todo.id))
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }

                if let error = store.error {
                    Text(error)
                        .foregroundColor(.red)
                        .padding()
                }
            }
            .navigationTitle("Todos")
            .task {
                store.send(.loadTodos)
            }
            .alert("Error", isPresented: .constant(store.error != nil)) {
                Button("OK") {
                    store.send(.clearError)
                }
            } message: {
                Text(store.error ?? "")
            }
        }
    }
}

// MARK: - Preview
#Preview {
    TodoView(
        store: Store(
            initialState: TodoFeature.State(
                todos: [TodoItem(id: UUID(), text: "Buy milk", isCompleted: false)]
            ),
            reducer: { TodoFeature() }
        )
    )
}

// MARK: - Domain Models
struct TodoItem: Identifiable, Equatable {
    let id: UUID
    var text: String
    var isCompleted: Bool
}
```

---

## Android

### ViewModel + StateFlow (Kotlin)

The standard pattern for Android state management with reactive updates.

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

// Domain model
data class Todo(
    val id: String,
    val text: String,
    val isCompleted: Boolean
)

// UI State
data class TodoListState(
    val todos: List<Todo> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
    val newTodoText: String = ""
)

// Events from UI
sealed interface TodoEvent {
    data class UpdateNewTodoText(val text: String) : TodoEvent
    object AddTodo : TodoEvent
    data class DeleteTodo(val id: String) : TodoEvent
    object LoadTodos : TodoEvent
    object ClearError : TodoEvent
}

// ViewModel
class TodoViewModel(private val todoRepository: TodoRepository) : ViewModel() {

    private val _uiState = MutableStateFlow(TodoListState())
    val uiState: StateFlow<TodoListState> = _uiState.asStateFlow()

    init {
        loadTodos()
    }

    fun onEvent(event: TodoEvent) {
        when (event) {
            is TodoEvent.UpdateNewTodoText -> {
                _uiState.value = _uiState.value.copy(newTodoText = event.text)
            }

            is TodoEvent.AddTodo -> {
                val currentState = _uiState.value
                if (currentState.newTodoText.isNotEmpty()) {
                    val newTodo = Todo(
                        id = System.currentTimeMillis().toString(),
                        text = currentState.newTodoText,
                        isCompleted = false
                    )
                    _uiState.value = currentState.copy(
                        todos = currentState.todos + newTodo,
                        newTodoText = ""
                    )
                }
            }

            is TodoEvent.DeleteTodo -> {
                _uiState.value = _uiState.value.copy(
                    todos = _uiState.value.todos.filterNot { it.id == event.id }
                )
            }

            TodoEvent.LoadTodos -> loadTodos()

            TodoEvent.ClearError -> {
                _uiState.value = _uiState.value.copy(error = null)
            }
        }
    }

    private fun loadTodos() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            try {
                val todos = todoRepository.getTodos()
                _uiState.value = _uiState.value.copy(
                    todos = todos,
                    isLoading = false
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    error = e.localizedMessage,
                    isLoading = false
                )
            }
        }
    }
}

// Repository
interface TodoRepository {
    suspend fun getTodos(): List<Todo>
}
```

### Jetpack Compose with remember

Local state in Compose with composable-level state preservation.

```kotlin
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel

@Composable
fun TodoListScreen(viewModel: TodoViewModel = viewModel()) {
    val uiState by viewModel.uiState.collectAsState()

    Column(modifier = Modifier.padding(16.dp)) {
        TodoInput(
            newTodoText = uiState.newTodoText,
            onTextChanged = {
                viewModel.onEvent(TodoEvent.UpdateNewTodoText(it))
            },
            onAddClick = {
                viewModel.onEvent(TodoEvent.AddTodo)
            }
        )

        when {
            uiState.isLoading -> {
                CircularProgressIndicator()
            }
            uiState.error != null -> {
                ErrorMessage(
                    error = uiState.error!!,
                    onDismiss = {
                        viewModel.onEvent(TodoEvent.ClearError)
                    }
                )
            }
            else -> {
                TodoList(
                    todos = uiState.todos,
                    onDeleteTodo = { id ->
                        viewModel.onEvent(TodoEvent.DeleteTodo(id))
                    }
                )
            }
        }
    }
}

@Composable
fun TodoInput(
    newTodoText: String,
    onTextChanged: (String) -> Unit,
    onAddClick: () -> Unit
) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(bottom = 16.dp)
    ) {
        OutlinedTextField(
            value = newTodoText,
            onValueChange = onTextChanged,
            label = { Text("New todo...") },
            modifier = Modifier
                .weight(1f)
                .padding(end = 8.dp)
        )

        Button(
            onClick = onAddClick,
            enabled = newTodoText.isNotEmpty()
        ) {
            Text("Add")
        }
    }
}

@Composable
fun TodoList(
    todos: List<Todo>,
    onDeleteTodo: (String) -> Unit
) {
    LazyColumn {
        items(todos, key = { it.id }) { todo ->
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(8.dp)
            ) {
                Text(
                    text = todo.text,
                    modifier = Modifier.weight(1f)
                )
                Button(onClick = { onDeleteTodo(todo.id) }) {
                    Text("Delete")
                }
            }
        }
    }
}

@Composable
fun ErrorMessage(error: String, onDismiss: () -> Unit) {
    Column(modifier = Modifier.padding(16.dp)) {
        Text(text = "Error: $error", color = androidx.compose.ui.graphics.Color.Red)
        Button(onClick = onDismiss) {
            Text("Dismiss")
        }
    }
}
```

### MVI with Orbit

Type-safe, predictable state management for complex features.

```kotlin
import org.orbitmvi.orbit.Container
import org.orbitmvi.orbit.ContainerHost
import org.orbitmvi.orbit.syntax.simple.intent
import org.orbitmvi.orbit.syntax.simple.reduce

// State
data class UserDetailState(
    val userId: String = "",
    val userName: String = "",
    val email: String = "",
    val isLoading: Boolean = false,
    val error: String? = null
)

// Side Effects
sealed class UserDetailSideEffect {
    data class ShowMessage(val message: String) : UserDetailSideEffect()
    object NavigateBack : UserDetailSideEffect()
}

// ViewModel using ContainerHost
class UserDetailViewModel(
    private val userRepository: UserRepository,
    userId: String
) : ContainerHost<UserDetailState, UserDetailSideEffect>,
    ViewModel() {

    override val container: Container<UserDetailState, UserDetailSideEffect> =
        container(UserDetailState(userId = userId)) {
            loadUser()
        }

    fun loadUser() = intent {
        reduce { state.copy(isLoading = true) }

        try {
            val user = userRepository.getUser(state.userId)
            reduce {
                state.copy(
                    userName = user.name,
                    email = user.email,
                    isLoading = false
                )
            }
        } catch (e: Exception) {
            reduce { state.copy(error = e.localizedMessage, isLoading = false) }
        }
    }

    fun updateEmail(newEmail: String) = intent {
        reduce { state.copy(email = newEmail) }

        try {
            userRepository.updateUser(state.userId, state.copy(email = newEmail))
            postSideEffect(UserDetailSideEffect.ShowMessage("Updated successfully"))
        } catch (e: Exception) {
            reduce { state.copy(error = e.localizedMessage) }
        }
    }

    fun deleteUser() = intent {
        try {
            userRepository.deleteUser(state.userId)
            postSideEffect(UserDetailSideEffect.NavigateBack)
        } catch (e: Exception) {
            reduce { state.copy(error = e.localizedDescription) }
        }
    }
}
```

---

## React Native

### Redux Toolkit

Predictable state container for complex app state.

```typescript
import { configureStore, createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';
import { TypedUseSelectorHook, useDispatch, useSelector } from 'react-redux';

// Types
interface Todo {
  id: string;
  text: string;
  completed: boolean;
}

interface TodoState {
  items: Todo[];
  loading: boolean;
  error: string | null;
  newTodoText: string;
}

// Async thunk
export const fetchTodos = createAsyncThunk('todos/fetchTodos', async () => {
  const response = await fetch('/api/todos');
  return (await response.json()) as Todo[];
});

// Slice
const todoSlice = createSlice({
  name: 'todos',
  initialState: {
    items: [],
    loading: false,
    error: null,
    newTodoText: '',
  } as TodoState,
  reducers: {
    setNewTodoText: (state, action: PayloadAction<string>) => {
      state.newTodoText = action.payload;
    },
    addTodo: (state) => {
      if (state.newTodoText.trim()) {
        state.items.push({
          id: Date.now().toString(),
          text: state.newTodoText,
          completed: false,
        });
        state.newTodoText = '';
      }
    },
    deleteTodo: (state, action: PayloadAction<string>) => {
      state.items = state.items.filter(todo => todo.id !== action.payload);
    },
    toggleTodo: (state, action: PayloadAction<string>) => {
      const todo = state.items.find(t => t.id === action.payload);
      if (todo) {
        todo.completed = !todo.completed;
      }
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchTodos.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTodos.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload;
      })
      .addCase(fetchTodos.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to fetch todos';
      });
  },
});

// Store
export const store = configureStore({
  reducer: {
    todos: todoSlice.reducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

export const { setNewTodoText, addTodo, deleteTodo, toggleTodo, clearError } = todoSlice.actions;

// Component
import React, { useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';

const TodoListScreen: React.FC = () => {
  const dispatch = useAppDispatch();
  const { items, loading, error, newTodoText } = useAppSelector(state => state.todos);

  useEffect(() => {
    dispatch(fetchTodos());
  }, [dispatch]);

  return (
    <View style={{ flex: 1, padding: 16 }}>
      <View style={{ marginBottom: 16 }}>
        <TextInput
          placeholder="Add new todo..."
          value={newTodoText}
          onChangeText={(text) => dispatch(setNewTodoText(text))}
          style={{
            borderWidth: 1,
            borderColor: '#ccc',
            padding: 8,
            marginBottom: 8,
            borderRadius: 4,
          }}
        />
        <TouchableOpacity
          disabled={!newTodoText.trim() || loading}
          onPress={() => dispatch(addTodo())}
          style={{
            backgroundColor: newTodoText.trim() ? '#007AFF' : '#ccc',
            padding: 12,
            borderRadius: 4,
            alignItems: 'center',
          }}
        >
          <Text style={{ color: '#fff', fontWeight: 'bold' }}>Add Todo</Text>
        </TouchableOpacity>
      </View>

      {loading && <ActivityIndicator size="large" color="#007AFF" />}
      {error && <Text style={{ color: 'red', marginBottom: 8 }}>Error: {error}</Text>}

      <FlatList
        data={items}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View
            style={{
              flexDirection: 'row',
              padding: 12,
              borderBottomWidth: 1,
              borderBottomColor: '#eee',
              alignItems: 'center',
            }}
          >
            <Text style={{ flex: 1, textDecorationLine: item.completed ? 'line-through' : 'none' }}>
              {item.text}
            </Text>
            <TouchableOpacity onPress={() => dispatch(toggleTodo(item.id))}>
              <Text>{item.completed ? '✓' : '○'}</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => dispatch(deleteTodo(item.id))}>
              <Text style={{ color: 'red', marginLeft: 8 }}>Delete</Text>
            </TouchableOpacity>
          </View>
        )}
      />
    </View>
  );
};

export default TodoListScreen;
```

### Zustand

Lightweight, minimal boilerplate state management.

```typescript
import create from 'zustand';
import { devtools, persist } from 'zustand/middleware';

interface Todo {
  id: string;
  text: string;
  completed: boolean;
}

interface TodoStore {
  todos: Todo[];
  newTodoText: string;
  isLoading: boolean;
  error: string | null;

  setNewTodoText: (text: string) => void;
  addTodo: () => void;
  deleteTodo: (id: string) => void;
  toggleTodo: (id: string) => void;
  fetchTodos: () => Promise<void>;
  clearError: () => void;
}

export const useTodoStore = create<TodoStore>()(
  devtools(
    persist(
      (set) => ({
        todos: [],
        newTodoText: '',
        isLoading: false,
        error: null,

        setNewTodoText: (text) => set({ newTodoText: text }),

        addTodo: () =>
          set((state) => {
            if (!state.newTodoText.trim()) return state;
            return {
              todos: [
                ...state.todos,
                {
                  id: Date.now().toString(),
                  text: state.newTodoText,
                  completed: false,
                },
              ],
              newTodoText: '',
            };
          }),

        deleteTodo: (id) =>
          set((state) => ({
            todos: state.todos.filter((todo) => todo.id !== id),
          })),

        toggleTodo: (id) =>
          set((state) => ({
            todos: state.todos.map((todo) =>
              todo.id === id ? { ...todo, completed: !todo.completed } : todo
            ),
          })),

        fetchTodos: async () => {
          set({ isLoading: true, error: null });
          try {
            const response = await fetch('/api/todos');
            const data = (await response.json()) as Todo[];
            set({ todos: data, isLoading: false });
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Unknown error',
              isLoading: false,
            });
          }
        },

        clearError: () => set({ error: null }),
      }),
      { name: 'todo-store' }
    )
  )
);

// Component usage
import React, { useEffect } from 'react';
import {
  View,
  Text,
  FlatList,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';

const TodoListScreen: React.FC = () => {
  const {
    todos,
    newTodoText,
    isLoading,
    error,
    setNewTodoText,
    addTodo,
    deleteTodo,
    toggleTodo,
    fetchTodos,
  } = useTodoStore();

  useEffect(() => {
    fetchTodos();
  }, [fetchTodos]);

  return (
    <View style={{ flex: 1, padding: 16 }}>
      <View style={{ marginBottom: 16 }}>
        <TextInput
          placeholder="Add new todo..."
          value={newTodoText}
          onChangeText={setNewTodoText}
          style={{
            borderWidth: 1,
            borderColor: '#ccc',
            padding: 8,
            marginBottom: 8,
            borderRadius: 4,
          }}
        />
        <TouchableOpacity
          disabled={!newTodoText.trim() || isLoading}
          onPress={addTodo}
          style={{
            backgroundColor: newTodoText.trim() ? '#007AFF' : '#ccc',
            padding: 12,
            borderRadius: 4,
            alignItems: 'center',
          }}
        >
          <Text style={{ color: '#fff', fontWeight: 'bold' }}>Add Todo</Text>
        </TouchableOpacity>
      </View>

      {isLoading && <ActivityIndicator size="large" color="#007AFF" />}
      {error && <Text style={{ color: 'red', marginBottom: 8 }}>Error: {error}</Text>}

      <FlatList
        data={todos}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View
            style={{
              flexDirection: 'row',
              padding: 12,
              borderBottomWidth: 1,
              borderBottomColor: '#eee',
              alignItems: 'center',
            }}
          >
            <Text style={{ flex: 1, textDecorationLine: item.completed ? 'line-through' : 'none' }}>
              {item.text}
            </Text>
            <TouchableOpacity onPress={() => toggleTodo(item.id)}>
              <Text>{item.completed ? '✓' : '○'}</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => deleteTodo(item.id)}>
              <Text style={{ color: 'red', marginLeft: 8 }}>Delete</Text>
            </TouchableOpacity>
          </View>
        )}
      />
    </View>
  );
};

export default TodoListScreen;
```

### React Query/TanStack Query

Powerful server state management with caching and synchronization.

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

interface Todo {
  id: string;
  text: string;
  completed: boolean;
}

// API calls
const todoAPI = {
  getTodos: async (): Promise<Todo[]> => {
    const response = await fetch('/api/todos');
    return response.json();
  },

  addTodo: async (text: string): Promise<Todo> => {
    const response = await fetch('/api/todos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    });
    return response.json();
  },

  updateTodo: async (id: string, updates: Partial<Todo>): Promise<Todo> => {
    const response = await fetch(`/api/todos/${id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates),
    });
    return response.json();
  },

  deleteTodo: async (id: string): Promise<void> => {
    await fetch(`/api/todos/${id}`, { method: 'DELETE' });
  },
};

// Component
import React, { useState } from 'react';
import {
  View,
  Text,
  FlatList,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';

const TodoListScreen: React.FC = () => {
  const [newTodoText, setNewTodoText] = useState('');
  const queryClient = useQueryClient();

  // Fetch todos
  const { data: todos = [], isLoading, error } = useQuery({
    queryKey: ['todos'],
    queryFn: todoAPI.getTodos,
  });

  // Add todo mutation
  const addTodoMutation = useMutation({
    mutationFn: (text: string) => todoAPI.addTodo(text),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
      setNewTodoText('');
    },
  });

  // Update todo mutation
  const updateTodoMutation = useMutation({
    mutationFn: ({ id, updates }: { id: string; updates: Partial<Todo> }) =>
      todoAPI.updateTodo(id, updates),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    },
  });

  // Delete todo mutation
  const deleteTodoMutation = useMutation({
    mutationFn: (id: string) => todoAPI.deleteTodo(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] });
    },
  });

  const handleAddTodo = () => {
    if (newTodoText.trim()) {
      addTodoMutation.mutate(newTodoText);
    }
  };

  return (
    <View style={{ flex: 1, padding: 16 }}>
      <View style={{ marginBottom: 16 }}>
        <TextInput
          placeholder="Add new todo..."
          value={newTodoText}
          onChangeText={setNewTodoText}
          style={{
            borderWidth: 1,
            borderColor: '#ccc',
            padding: 8,
            marginBottom: 8,
            borderRadius: 4,
          }}
        />
        <TouchableOpacity
          disabled={!newTodoText.trim() || addTodoMutation.isPending}
          onPress={handleAddTodo}
          style={{
            backgroundColor: newTodoText.trim() ? '#007AFF' : '#ccc',
            padding: 12,
            borderRadius: 4,
            alignItems: 'center',
          }}
        >
          <Text style={{ color: '#fff', fontWeight: 'bold' }}>
            {addTodoMutation.isPending ? 'Adding...' : 'Add Todo'}
          </Text>
        </TouchableOpacity>
      </View>

      {isLoading && <ActivityIndicator size="large" color="#007AFF" />}
      {error instanceof Error && <Text style={{ color: 'red', marginBottom: 8 }}>Error: {error.message}</Text>}

      <FlatList
        data={todos}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View
            style={{
              flexDirection: 'row',
              padding: 12,
              borderBottomWidth: 1,
              borderBottomColor: '#eee',
              alignItems: 'center',
            }}
          >
            <Text style={{ flex: 1, textDecorationLine: item.completed ? 'line-through' : 'none' }}>
              {item.text}
            </Text>
            <TouchableOpacity
              onPress={() =>
                updateTodoMutation.mutate({
                  id: item.id,
                  updates: { completed: !item.completed },
                })
              }
            >
              <Text>{item.completed ? '✓' : '○'}</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => deleteTodoMutation.mutate(item.id)}>
              <Text style={{ color: 'red', marginLeft: 8 }}>Delete</Text>
            </TouchableOpacity>
          </View>
        )}
      />
    </View>
  );
};

export default TodoListScreen;
```

---

## Flutter

### Provider Pattern

Simple, scalable state management with ChangeNotifier.

```dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

// Models
class Todo {
  final String id;
  final String text;
  final bool isCompleted;

  Todo({
    required this.id,
    required this.text,
    this.isCompleted = false,
  });

  Todo copyWith({
    String? id,
    String? text,
    bool? isCompleted,
  }) {
    return Todo(
      id: id ?? this.id,
      text: text ?? this.text,
      isCompleted: isCompleted ?? this.isCompleted,
    );
  }
}

// ViewModel
class TodoViewModel extends ChangeNotifier {
  final List<Todo> _todos = [];
  String _newTodoText = '';
  bool _isLoading = false;
  String? _error;

  List<Todo> get todos => _todos;
  String get newTodoText => _newTodoText;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadTodos() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final todos = await _fetchTodos();
      _todos.clear();
      _todos.addAll(todos);
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void updateNewTodoText(String text) {
    _newTodoText = text;
    notifyListeners();
  }

  void addTodo() {
    if (_newTodoText.trim().isEmpty) return;

    _todos.add(Todo(
      id: DateTime.now().toString(),
      text: _newTodoText,
    ));
    _newTodoText = '';
    notifyListeners();
  }

  void deleteTodo(String id) {
    _todos.removeWhere((todo) => todo.id == id);
    notifyListeners();
  }

  void toggleTodo(String id) {
    final index = _todos.indexWhere((todo) => todo.id == id);
    if (index != -1) {
      _todos[index] = _todos[index].copyWith(
        isCompleted: !_todos[index].isCompleted,
      );
      notifyListeners();
    }
  }

  void clearError() {
    _error = null;
    notifyListeners();
  }

  Future<List<Todo>> _fetchTodos() async {
    // Simulate API call
    await Future.delayed(Duration(seconds: 1));
    return [
      Todo(id: '1', text: 'Buy milk'),
      Todo(id: '2', text: 'Walk the dog'),
    ];
  }
}

// UI
class TodoListScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => TodoViewModel()..loadTodos(),
      child: Scaffold(
        appBar: AppBar(title: Text('Todos')),
        body: Consumer<TodoViewModel>(
          builder: (context, viewModel, _) {
            if (viewModel.isLoading) {
              return Center(child: CircularProgressIndicator());
            }

            if (viewModel.error != null) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text('Error: ${viewModel.error}'),
                    SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: () => viewModel.clearError(),
                      child: Text('Dismiss'),
                    ),
                  ],
                ),
              );
            }

            return Column(
              children: [
                Padding(
                  padding: EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Expanded(
                        child: TextField(
                          value: viewModel.newTodoText,
                          onChanged: (text) => viewModel.updateNewTodoText(text),
                          decoration: InputDecoration(
                            hintText: 'Add new todo...',
                            border: OutlineInputBorder(),
                          ),
                        ),
                      ),
                      SizedBox(width: 8),
                      ElevatedButton(
                        onPressed: viewModel.newTodoText.trim().isEmpty
                            ? null
                            : () => viewModel.addTodo(),
                        child: Text('Add'),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: ListView.builder(
                    itemCount: viewModel.todos.length,
                    itemBuilder: (context, index) {
                      final todo = viewModel.todos[index];
                      return ListTile(
                        title: Text(
                          todo.text,
                          style: TextStyle(
                            decoration: todo.isCompleted
                                ? TextDecoration.lineThrough
                                : null,
                          ),
                        ),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            IconButton(
                              icon: Icon(
                                todo.isCompleted
                                    ? Icons.check_circle
                                    : Icons.circle_outlined,
                              ),
                              onPressed: () => viewModel.toggleTodo(todo.id),
                            ),
                            IconButton(
                              icon: Icon(Icons.delete, color: Colors.red),
                              onPressed: () => viewModel.deleteTodo(todo.id),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                ),
              ],
            );
          },
        ),
      ),
    );
  }
}
```

### Riverpod

Modern, functional reactive state management.

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Models
class Todo {
  final String id;
  final String text;
  final bool isCompleted;

  Todo({
    required this.id,
    required this.text,
    this.isCompleted = false,
  });

  Todo copyWith({String? id, String? text, bool? isCompleted}) {
    return Todo(
      id: id ?? this.id,
      text: text ?? this.text,
      isCompleted: isCompleted ?? this.isCompleted,
    );
  }
}

// State Providers
final todosProvider = StateNotifierProvider<TodoNotifier, AsyncValue<List<Todo>>>(
  (ref) => TodoNotifier(),
);

final newTodoTextProvider = StateProvider<String>((ref) => '');

class TodoNotifier extends StateNotifier<AsyncValue<List<Todo>>> {
  TodoNotifier() : super(const AsyncValue.loading()) {
    _load();
  }

  Future<void> _load() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _fetchTodos());
  }

  Future<List<Todo>> _fetchTodos() async {
    await Future.delayed(Duration(seconds: 1));
    return [
      Todo(id: '1', text: 'Buy milk'),
      Todo(id: '2', text: 'Walk the dog'),
    ];
  }

  void addTodo(String text) {
    state.whenData((todos) {
      state = AsyncValue.data([
        ...todos,
        Todo(id: DateTime.now().toString(), text: text),
      ]);
    });
  }

  void deleteTodo(String id) {
    state.whenData((todos) {
      state = AsyncValue.data(todos.where((t) => t.id != id).toList());
    });
  }

  void toggleTodo(String id) {
    state.whenData((todos) {
      state = AsyncValue.data(
        todos
            .map((t) => t.id == id ? t.copyWith(isCompleted: !t.isCompleted) : t)
            .toList(),
      );
    });
  }
}

// UI
class TodoListScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final todosAsync = ref.watch(todosProvider);
    final newTodoText = ref.watch(newTodoTextProvider);

    return Scaffold(
      appBar: AppBar(title: Text('Todos')),
      body: todosAsync.when(
        loading: () => Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(child: Text('Error: $error')),
        data: (todos) {
          return Column(
            children: [
              Padding(
                padding: EdgeInsets.all(16),
                child: Row(
                  children: [
                    Expanded(
                      child: TextField(
                        onChanged: (text) {
                          ref.read(newTodoTextProvider.notifier).state = text;
                        },
                        decoration: InputDecoration(
                          hintText: 'Add new todo...',
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                    SizedBox(width: 8),
                    ElevatedButton(
                      onPressed: newTodoText.trim().isEmpty
                          ? null
                          : () {
                              ref.read(todosProvider.notifier).addTodo(newTodoText);
                              ref.read(newTodoTextProvider.notifier).state = '';
                            },
                      child: Text('Add'),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: ListView.builder(
                  itemCount: todos.length,
                  itemBuilder: (context, index) {
                    final todo = todos[index];
                    return ListTile(
                      title: Text(
                        todo.text,
                        style: TextStyle(
                          decoration: todo.isCompleted
                              ? TextDecoration.lineThrough
                              : null,
                        ),
                      ),
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          IconButton(
                            icon: Icon(
                              todo.isCompleted
                                  ? Icons.check_circle
                                  : Icons.circle_outlined,
                            ),
                            onPressed: () {
                              ref.read(todosProvider.notifier).toggleTodo(todo.id);
                            },
                          ),
                          IconButton(
                            icon: Icon(Icons.delete, color: Colors.red),
                            onPressed: () {
                              ref.read(todosProvider.notifier).deleteTodo(todo.id);
                            },
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
```

---

## Cross-Cutting Concerns

### Global vs Local State

**Local State**: UI-only state like form input, toggle visibility. Keep closest to where it's used.

```swift
// SwiftUI: Local state with @State
struct SearchView: View {
    @State private var searchText = ""
    @State private var isSearching = false

    var body: some View {
        SearchBar(text: $searchText, isSearching: $isSearching)
    }
}
```

**Global State**: Shared across features like auth, theme, user data. Use environment/DI.

```swift
// SwiftUI: Global state with @Observable + @Environment
@Observable
final class AppState {
    var authToken: String?
    var currentUser: User?
    var isDarkMode: Bool = false
}

@main
struct App: App {
    @State private var appState = AppState()
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(appState)
        }
    }
}
```

### Server State vs Client State

**Server State**: Remote data (todos, users, posts). Use caching + invalidation patterns.

**Client State**: Local UI state (filters, form state, theme). Keep simple and close.

```kotlin
// Android: Separate server state (from repository) and client state (from ViewModel)
@Observable
class TodoListViewModel(private val todoRepository: TodoRepository) {
    // Server state: managed via repository with caching
    val serverTodos: StateFlow<List<Todo>> = todoRepository.getTodosFlow()

    // Client state: UI preferences
    var sortBy: String by mutableStateOf("name")
    var filterCompleted: Boolean by mutableStateOf(false)

    val filteredTodos: StateFlow<List<Todo>> =
        serverTodos.map { todos ->
            todos.filter { !filterCompleted || it.completed }
                 .sortedBy { if (sortBy == "name") it.text else it.id }
        }.stateIn(viewModelScope, SharingStarted.Lazily, emptyList())
}
```

### State Persistence

Save state to disk/database to restore after app restart.

```swift
// iOS: Using Codable + UserDefaults
@Observable
final class AppState: Codable {
    var todos: [TodoItem] = []
    var lastSyncDate: Date?

    func save() {
        let encoder = JSONEncoder()
        if let encoded = try? encoder.encode(self),
           let jsonString = String(data: encoded, encoding: .utf8) {
            UserDefaults.standard.set(jsonString, forKey: "appState")
        }
    }

    static func load() -> AppState {
        let decoder = JSONDecoder()
        if let jsonString = UserDefaults.standard.string(forKey: "appState"),
           let data = jsonString.data(using: .utf8),
           let state = try? decoder.decode(AppState.self, from: data) {
            return state
        }
        return AppState()
    }
}
```

```dart
// Flutter: Using SharedPreferences
class PersistenceService {
  static const String _todosKey = 'todos';

  Future<void> saveTodos(List<Todo> todos) async {
    final prefs = await SharedPreferences.getInstance();
    final jsonList = todos.map((t) => jsonEncode(t.toJson())).toList();
    await prefs.setStringList(_todosKey, jsonList);
  }

  Future<List<Todo>> loadTodos() async {
    final prefs = await SharedPreferences.getInstance();
    final jsonList = prefs.getStringList(_todosKey) ?? [];
    return jsonList.map((json) => Todo.fromJson(jsonDecode(json))).toList();
  }
}

final persistenceProvider = Provider((ref) => PersistenceService());
```

### Derived/Computed State

Avoid storing computed values. Derive them on-the-fly.

```typescript
// React Native: Using selectors (Zustand example)
const useTodoStats = () => {
  const todos = useTodoStore((state) => state.todos);

  // Derived state - computed from base state
  return {
    total: todos.length,
    completed: todos.filter((t) => t.completed).length,
    pending: todos.filter((t) => !t.completed).length,
    completionPercent: todos.length === 0 ? 0 :
      Math.round((todos.filter((t) => t.completed).length / todos.length) * 100),
  };
};

// Usage in component
const TodoStats = () => {
  const { total, completed, completionPercent } = useTodoStats();
  return <Text>Progress: {completionPercent}% ({completed}/{total})</Text>;
};
```

### State Restoration After Process Death

Restore critical app state when the process is killed.

```kotlin
// Android: Using saved state module
class TodoViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val todoRepository: TodoRepository,
) : ViewModel() {

    companion object {
        private const val KEY_SCROLL_POSITION = "scroll_position"
        private const val KEY_SELECTED_FILTER = "selected_filter"
    }

    var scrollPosition: Int
        get() = savedStateHandle[KEY_SCROLL_POSITION] ?: 0
        set(value) = savedStateHandle.set(KEY_SCROLL_POSITION, value)

    var selectedFilter: String
        get() = savedStateHandle[KEY_SELECTED_FILTER] ?: "all"
        set(value) = savedStateHandle.set(KEY_SELECTED_FILTER, value)

    val todos = todoRepository.getTodos()
        .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())
}
```

### Debugging Tools

**Redux DevTools**: Time-travel debugging for Redux/Redux Toolkit apps.

```typescript
// Redux Toolkit includes devtools middleware by default
const store = configureStore({
  reducer: { todos: todoSlice.reducer },
  // devtools enabled by default in non-production
});
```

**Riverpod DevTools**: Monitor Riverpod providers in Flutter.

```dart
import 'package:riverpod_generator/riverpod_generator.dart';

// Automatically generates observability with 'riverpod' CLI tool
// Use: flutter pub run riverpod_generator_watcher
// Then open DevTools to inspect provider state
```

---

## Decision Matrix

| App Size | Complexity | iOS | Android | React Native | Flutter |
|----------|-----------|-----|---------|--------------|---------|
| **Tiny** (single screen, <5 features) | Minimal | @State | remember | useState | State |
| **Small** (5-15 screens, simple flow) | Simple | @State + @Environment | ViewModel + StateFlow | Zustand | Provider |
| **Medium** (15-50 screens, many features) | Moderate | @Observable + TCA lite | ViewModel + StateFlow + Orbit | Redux Toolkit + React Query | Riverpod |
| **Large** (50+ screens, complex state) | High | TCA (full) | MVI + Orbit | Redux Toolkit + React Query + Zustand | BLoC/Riverpod |
| **Enterprise** (multiple teams, shared state) | Very High | TCA (modular) | Modular MVI + Orbit | Redux + React Query + custom middleware | BLoC (package-based) + Riverpod |

### Recommendation Matrix by Concern

**Best for Client State:**
- iOS: @State, @Binding
- Android: remember (Compose)
- React Native: useState, Zustand
- Flutter: Provider, GetX

**Best for Server State:**
- iOS: Custom API wrapper + caching
- Android: Repository pattern + StateFlow
- React Native: React Query / TanStack Query
- Flutter: Riverpod (FutureProvider)

**Best for Testability:**
- iOS: TCA (strong), @Observable (moderate)
- Android: ViewModel + dependency injection
- React Native: Redux Toolkit (excellent)
- Flutter: Riverpod (excellent)

**Best for Performance at Scale:**
- iOS: TCA with proper granularity
- Android: Kotlin StateFlow with proper scoping
- React Native: Redux with selectors
- Flutter: Riverpod with .select()

**Best for Learning Curve:**
- iOS: @State → @Observable
- Android: ViewModel + StateFlow
- React Native: Zustand → Redux Toolkit
- Flutter: Provider → Riverpod

