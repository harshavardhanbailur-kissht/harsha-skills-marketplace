# Offline-First Architecture: Comprehensive Reference

## Table of Contents
- [1. Offline-First Principles and Local-First Software Concepts](#1-offline-first-principles-and-local-first-software-concepts)
- [2. Conflict Resolution Strategies](#2-conflict-resolution-strategies)
- [3. Sync Architectures](#3-sync-architectures)
- [4. Optimistic UI Updates with Rollback](#4-optimistic-ui-updates-with-rollback)
- [5. Queue-Based Sync with Pending Operations](#5-queue-based-sync-with-pending-operations)
- [6. Network State Detection](#6-network-state-detection)
- [7. Firebase Firestore Offline Persistence](#7-firebase-firestore-offline-persistence)
- [8. WatermelonDB for React Native](#8-watermelondb-for-react-native)
- [9. Background Sync Scheduling](#9-background-sync-scheduling)
- [10. Retry Strategies: Exponential Backoff with Jitter](#10-retry-strategies-exponential-backoff-with-jitter)
- [11. Data Integrity Validation (Checksums)](#11-data-integrity-validation-checksums)
- [12. Testing Offline Scenarios](#12-testing-offline-scenarios)

## 1. Offline-First Principles and Local-First Software Concepts

Offline-first architecture prioritizes local data persistence and availability over constant connectivity. Applications can function completely without network access, syncing data opportunistically when connectivity is available.

### Core Principles

**Local-First Software** emphasizes:
- Data sovereignty: Users own their data locally first
- No mandatory cloud dependency
- Reduced latency through local reads/writes
- Seamless offline/online transitions
- User control over synchronization

```typescript
// Offline-first application flow
interface OfflineFirstApp {
  // All operations work on local database first
  async createNote(content: string): Promise<Note> {
    const note = await localDb.notes.create({
      id: generateUUID(),
      content,
      createdAt: Date.now(),
      synced: false
    });

    // Queue for sync when connection available
    syncQueue.add({
      operation: 'create',
      entity: 'notes',
      data: note,
      timestamp: Date.now()
    });

    return note;
  }

  // Read from local storage immediately
  async getNotes(): Promise<Note[]> {
    return localDb.notes.all();
  }
}
```

### Benefits and Trade-offs

**Benefits:**
- Works completely offline
- Instant local feedback
- Reduced bandwidth usage
- Better user experience for mobile/unreliable networks

**Trade-offs:**
- Complex conflict resolution
- Data consistency challenges
- Storage constraints on devices
- Sync complexity

---

## 2. Conflict Resolution Strategies

### Last-Write-Wins (LWW)

Simple strategy where the most recent update wins. Works well for non-collaborative scenarios.

```typescript
interface ConflictableRecord {
  id: string;
  value: any;
  timestamp: number;
  version: number;
}

function resolveConflictLWW(
  local: ConflictableRecord,
  remote: ConflictableRecord
): ConflictableRecord {
  return local.timestamp > remote.timestamp ? local : remote;
}

// Example: User updates same field offline and online
const localUpdate = {
  id: 'user-1',
  value: 'Alice Updated',
  timestamp: 1709500800000,
  version: 2
};

const remoteUpdate = {
  id: 'user-1',
  value: 'Alice Changed',
  timestamp: 1709500700000,
  version: 2
};

const winner = resolveConflictLWW(localUpdate, remoteUpdate);
// Result: localUpdate (timestamp is newer)
```

### Merge Functions

Custom logic to intelligently merge conflicting changes.

```typescript
interface MergeableData {
  id: string;
  name: string;
  tags: string[];
  metadata: Record<string, any>;
}

function smartMerge(
  local: MergeableData,
  remote: MergeableData,
  base?: MergeableData
): MergeableData {
  const result = { ...local };

  // Merge arrays (tags) by combining unique values
  const localTags = new Set(local.tags);
  const remoteTags = new Set(remote.tags);
  result.tags = Array.from(
    new Set([...localTags, ...remoteTags])
  );

  // For scalar values, use remote if local unchanged from base
  if (base && local.name === base.name && remote.name !== base.name) {
    result.name = remote.name;
  } else if (local.name !== remote.name && local.name !== base?.name) {
    // Both changed - mark for user review
    result.metadata._conflict = {
      field: 'name',
      local: local.name,
      remote: remote.name
    };
  }

  return result;
}
```

### CRDTs (Conflict-free Replicated Data Types)

CRDTs mathematically guarantee convergence without central coordination. G-Counter example:

```typescript
// G-Counter: Grow-only counter (part of CRDT family)
class GCounter {
  private counts: Map<string, number> = new Map();
  private nodeId: string;

  constructor(nodeId: string) {
    this.nodeId = nodeId;
  }

  increment(amount: number = 1): void {
    const current = this.counts.get(this.nodeId) || 0;
    this.counts.set(this.nodeId, current + amount);
  }

  value(): number {
    let sum = 0;
    for (const count of this.counts.values()) {
      sum += count;
    }
    return sum;
  }

  merge(other: GCounter): void {
    for (const [nodeId, count] of other.counts) {
      const current = this.counts.get(nodeId) || 0;
      this.counts.set(nodeId, Math.max(current, count));
    }
  }

  getState(): Record<string, number> {
    return Object.fromEntries(this.counts);
  }

  setState(state: Record<string, number>): void {
    for (const [nodeId, count] of Object.entries(state)) {
      this.counts.set(nodeId, count);
    }
  }
}

// Example usage across replicas
const counter1 = new GCounter('device-1');
const counter2 = new GCounter('device-2');

counter1.increment(5); // device-1: 5
counter2.increment(3); // device-2: 3

counter1.merge(counter2); // device-1 sees total: 8
counter2.merge(counter1); // device-2 sees total: 8
```

---

## 3. Sync Architectures

### Client-Server Sync Flow

```typescript
interface SyncOperation {
  id: string;
  entity: string;
  operation: 'create' | 'update' | 'delete';
  data: any;
  timestamp: number;
  clientId: string;
}

interface SyncState {
  lastSyncTimestamp: number;
  pendingOperations: SyncOperation[];
  isSyncing: boolean;
}

class ClientServerSync {
  private syncState: SyncState = {
    lastSyncTimestamp: 0,
    pendingOperations: [],
    isSyncing: false
  };

  async sync(): Promise<void> {
    if (this.syncState.isSyncing) return;

    try {
      this.syncState.isSyncing = true;

      // Step 1: Upload pending local changes
      const uploaded = await this.uploadPendingOperations(
        this.syncState.pendingOperations
      );

      // Step 2: Download server changes since last sync
      const serverChanges = await this.downloadChanges(
        this.syncState.lastSyncTimestamp
      );

      // Step 3: Apply server changes locally
      await this.applyRemoteChanges(serverChanges);

      // Step 4: Update sync state
      this.syncState.lastSyncTimestamp = Date.now();
      this.syncState.pendingOperations = this.syncState.pendingOperations.filter(
        op => !uploaded.includes(op.id)
      );
    } finally {
      this.syncState.isSyncing = false;
    }
  }

  private async uploadPendingOperations(
    operations: SyncOperation[]
  ): Promise<string[]> {
    const response = await fetch('/api/sync/upload', {
      method: 'POST',
      body: JSON.stringify({ operations })
    });
    const data = await response.json();
    return data.uploadedIds;
  }

  private async downloadChanges(since: number): Promise<any[]> {
    const response = await fetch(`/api/sync/download?since=${since}`);
    return response.json();
  }

  private async applyRemoteChanges(changes: any[]): Promise<void> {
    for (const change of changes) {
      await this.applyChange(change);
    }
  }

  private async applyChange(change: any): Promise<void> {
    // Merge with local state if conflict
    const local = await this.getLocalEntity(change.id);
    if (local && local.version === change.version - 1) {
      // No conflict, fast-forward
      await this.updateLocalEntity(change.id, change);
    } else if (local) {
      // Conflict - resolve
      const resolved = this.resolveConflict(local, change);
      await this.updateLocalEntity(change.id, resolved);
    } else {
      // New remote entity
      await this.insertLocalEntity(change);
    }
  }

  private resolveConflict(local: any, remote: any): any {
    // Implement conflict resolution strategy
    return remote.timestamp > local.timestamp ? remote : local;
  }

  private async getLocalEntity(id: string): Promise<any> {
    // Fetch from local database
    return null;
  }

  private async updateLocalEntity(id: string, data: any): Promise<void> {
    // Update local database
  }

  private async insertLocalEntity(data: any): Promise<void> {
    // Insert to local database
  }
}
```

### Delta vs Full Sync

```typescript
// DELTA SYNC: Only sync changes since last sync
class DeltaSyncManager {
  private lastSyncClock: Map<string, number> = new Map();

  async getDelta(entityType: string, since: number): Promise<any[]> {
    // Efficient: only fetch modified records
    return fetch(
      `/api/delta/${entityType}?since=${since}&clientId=${this.getClientId()}`
    ).then(r => r.json());
  }

  async syncDelta(): Promise<void> {
    const lastClock = this.lastSyncClock.get('records') || 0;
    const delta = await this.getDelta('records', lastClock);

    for (const change of delta) {
      await this.applyDeltaChange(change);
    }

    this.lastSyncClock.set('records', Date.now());
  }

  private async applyDeltaChange(change: any): Promise<void> {
    // Apply individual change
  }
}

// FULL SYNC: Periodically sync entire dataset
class FullSyncManager {
  async syncFull(): Promise<void> {
    // Heavy operation, but ensures consistency
    const allRemoteRecords = await fetch('/api/records/all').then(
      r => r.json()
    );

    // Determine local record IDs
    const localRecords = await this.getLocalRecords();
    const localIds = new Set(localRecords.map(r => r.id));

    // Delete records not on server
    for (const local of localRecords) {
      if (!allRemoteRecords.some((r: any) => r.id === local.id)) {
        await this.deleteLocalRecord(local.id);
      }
    }

    // Upsert server records
    for (const remote of allRemoteRecords) {
      const local = localRecords.find(r => r.id === remote.id);
      if (!local) {
        await this.insertLocalRecord(remote);
      } else {
        await this.updateLocalRecord(remote);
      }
    }
  }

  private async getLocalRecords(): Promise<any[]> {
    return [];
  }

  private async deleteLocalRecord(id: string): Promise<void> {}
  private async insertLocalRecord(data: any): Promise<void> {}
  private async updateLocalRecord(data: any): Promise<void> {}
}
```

---

## 4. Optimistic UI Updates with Rollback

```typescript
class OptimisticUpdateManager {
  private optimisticCache: Map<string, any> = new Map();

  async updateNoteOptimistically(
    noteId: string,
    updates: Partial<Note>
  ): Promise<void> {
    // Cache original state
    const original = await this.getNote(noteId);
    this.optimisticCache.set(`note-${noteId}-original`, original);

    // Immediately update local state (optimistic)
    const updated = { ...original, ...updates };
    await this.updateLocalNote(noteId, updated);

    // Update UI immediately
    this.notifyUIStateChanged(noteId, updated);

    // Sync to server in background
    try {
      const result = await fetch(`/api/notes/${noteId}`, {
        method: 'PATCH',
        body: JSON.stringify(updates)
      }).then(r => r.json());

      // Server confirms - update version number
      await this.updateLocalNote(noteId, {
        ...updated,
        version: result.version,
        synced: true
      });

      this.optimisticCache.delete(`note-${noteId}-original`);
    } catch (error) {
      // Rollback on failure
      await this.updateLocalNote(noteId, original);
      this.notifyUIStateChanged(noteId, original);
      this.optimisticCache.delete(`note-${noteId}-original`);

      throw new Error('Failed to update note. Changes rolled back.');
    }
  }

  private async getNote(id: string): Promise<Note> {
    return {} as Note;
  }

  private async updateLocalNote(id: string, data: any): Promise<void> {}

  private notifyUIStateChanged(id: string, data: any): void {
    // Trigger UI update via state management
  }
}
```

---

## 5. Queue-Based Sync with Pending Operations

```typescript
interface QueuedOperation {
  id: string;
  entity: string;
  operation: 'create' | 'update' | 'delete';
  payload: any;
  timestamp: number;
  retryCount: number;
  maxRetries: number;
  nextRetryAt: number;
}

class OperationQueue {
  private queue: QueuedOperation[] = [];
  private processing = false;

  async enqueue(operation: Omit<QueuedOperation, 'id' | 'retryCount' | 'maxRetries' | 'nextRetryAt'>): Promise<void> {
    const queuedOp: QueuedOperation = {
      ...operation,
      id: this.generateId(),
      retryCount: 0,
      maxRetries: 3,
      nextRetryAt: Date.now()
    };

    this.queue.push(queuedOp);
    await this.persistQueue();

    // Process immediately if network available
    if (this.isNetworkAvailable()) {
      this.processQueue();
    }
  }

  async processQueue(): Promise<void> {
    if (this.processing) return;

    this.processing = true;

    try {
      while (this.queue.length > 0) {
        const operation = this.queue[0];

        // Skip if not ready for retry yet
        if (operation.nextRetryAt > Date.now()) {
          break;
        }

        try {
          await this.executeOperation(operation);
          this.queue.shift(); // Remove successful operation
          await this.persistQueue();
        } catch (error) {
          operation.retryCount++;

          if (operation.retryCount >= operation.maxRetries) {
            // Max retries exceeded
            this.handleMaxRetriesExceeded(operation);
            this.queue.shift();
          } else {
            // Schedule retry with backoff
            operation.nextRetryAt = this.calculateNextRetry(
              operation.retryCount
            );
          }

          await this.persistQueue();
          break; // Stop processing on error
        }
      }
    } finally {
      this.processing = false;
    }
  }

  private async executeOperation(op: QueuedOperation): Promise<void> {
    const { entity, operation, payload } = op;

    const endpoint = `/api/${entity}`;

    switch (operation) {
      case 'create':
        await fetch(endpoint, {
          method: 'POST',
          body: JSON.stringify(payload)
        });
        break;

      case 'update':
        await fetch(`${endpoint}/${payload.id}`, {
          method: 'PATCH',
          body: JSON.stringify(payload)
        });
        break;

      case 'delete':
        await fetch(`${endpoint}/${payload.id}`, {
          method: 'DELETE'
        });
        break;
    }
  }

  private calculateNextRetry(retryCount: number): number {
    const baseDelay = 1000; // 1 second
    return Date.now() + baseDelay * Math.pow(2, retryCount);
  }

  private handleMaxRetriesExceeded(operation: QueuedOperation): void {
    console.error(`Operation ${operation.id} failed after max retries`, operation);
    // Notify user of sync failure
  }

  private async persistQueue(): Promise<void> {
    // Save queue to local storage or database
  }

  private isNetworkAvailable(): boolean {
    return typeof navigator !== 'undefined' && navigator.onLine;
  }

  private generateId(): string {
    return `${Date.now()}-${Math.random()}`;
  }
}
```

---

## 6. Network State Detection

### iOS (NWPathMonitor)

```swift
import Network

class NetworkMonitor {
    private let queue = DispatchQueue(label: "NetworkMonitor")
    private let monitor = NWPathMonitor()

    var isConnected: Bool {
        return monitor.currentPath.status == .satisfied
    }

    var connectionType: String {
        let path = monitor.currentPath

        if path.usesInterfaceType(.wifi) {
            return "wifi"
        } else if path.usesInterfaceType(.cellular) {
            return "cellular"
        } else if path.usesInterfaceType(.wiredEthernet) {
            return "ethernet"
        } else if path.usesInterfaceType(.loopback) {
            return "loopback"
        }
        return "unknown"
    }

    func startMonitoring(onChange: @escaping (Bool) -> Void) {
        monitor.pathUpdateHandler = { path in
            DispatchQueue.main.async {
                onChange(path.status == .satisfied)
            }
        }
        monitor.start(queue: queue)
    }

    func stopMonitoring() {
        monitor.cancel()
    }
}
```

### Android (ConnectivityManager)

```kotlin
import android.content.Context
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities

class NetworkMonitor(context: Context) {
    private val connectivityManager =
        context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager

    val isConnected: Boolean
        get() = connectivityManager.activeNetwork != null

    val connectionType: String
        get() {
            val network = connectivityManager.activeNetwork ?: return "none"
            val capabilities =
                connectivityManager.getNetworkCapabilities(network) ?: return "unknown"

            return when {
                capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> "wifi"
                capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> "cellular"
                capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET) -> "ethernet"
                else -> "unknown"
            }
        }

    fun startMonitoring(onChange: (Boolean) -> Unit) {
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) {
                onChange(true)
            }

            override fun onLost(network: Network) {
                onChange(false)
            }
        }

        val request = android.net.NetworkRequest.Builder()
            .build()

        connectivityManager.registerNetworkCallback(request, callback)
    }
}
```

### React Native (NetInfo)

```typescript
import { useNetInfo } from '@react-native-community/netinfo';
import { useEffect, useState } from 'react';

export function useNetworkMonitor() {
  const netInfo = useNetInfo();
  const [syncEnabled, setSyncEnabled] = useState(true);

  useEffect(() => {
    const isConnected =
      netInfo.isConnected &&
      netInfo.isInternetReachable !== false;

    setSyncEnabled(isConnected);
  }, [netInfo.isConnected, netInfo.isInternetReachable]);

  return {
    isConnected: netInfo.isConnected ?? false,
    isInternetReachable: netInfo.isInternetReachable,
    type: netInfo.type,
    syncEnabled
  };
}

// Usage in component
function SyncStatus() {
  const { isConnected, type, syncEnabled } = useNetworkMonitor();

  return (
    <View>
      <Text>
        Connected: {isConnected ? 'Yes' : 'No'}
      </Text>
      <Text>Type: {type || 'unknown'}</Text>
      <Text>
        Sync: {syncEnabled ? 'Enabled' : 'Disabled'}
      </Text>
    </View>
  );
}
```

---

## 7. Firebase Firestore Offline Persistence

```typescript
import {
  initializeApp,
  FirebaseApp
} from 'firebase/app';
import {
  getFirestore,
  Firestore,
  enableIndexedDbPersistence,
  disablePersistence,
  collection,
  query,
  where,
  getDocs,
  addDoc,
  updateDoc,
  deleteDoc,
  onSnapshot,
  doc
} from 'firebase/firestore';

class FirestoreOfflineManager {
  private db: Firestore;
  private app: FirebaseApp;

  constructor(config: any) {
    this.app = initializeApp(config);
    this.db = getFirestore(this.app);
  }

  async enableOfflinePersistence(): Promise<void> {
    try {
      await enableIndexedDbPersistence(this.db);
      console.log('Firestore offline persistence enabled');
    } catch (error) {
      if ((error as any).code === 'failed-precondition') {
        console.log('Multiple tabs open, persistence disabled');
      } else if ((error as any).code === 'unimplemented') {
        console.log('Browser does not support persistence');
      }
    }
  }

  // Listen for documents with offline support
  listenToDocuments(
    collectionName: string,
    callback: (docs: any[]) => void
  ): () => void {
    const q = query(collection(this.db, collectionName));

    return onSnapshot(q, (snapshot) => {
      const docs = snapshot.docs.map((doc) => ({
        id: doc.id,
        ...doc.data()
      }));
      callback(docs);
    });
  }

  // Add document (works offline)
  async addDocument(
    collectionName: string,
    data: any
  ): Promise<string> {
    const ref = await addDoc(
      collection(this.db, collectionName),
      {
        ...data,
        createdAt: new Date(),
        synced: false
      }
    );
    return ref.id;
  }

  // Update document (works offline, syncs when online)
  async updateDocument(
    collectionName: string,
    docId: string,
    data: any
  ): Promise<void> {
    await updateDoc(
      doc(this.db, collectionName, docId),
      {
        ...data,
        updatedAt: new Date(),
        synced: false
      }
    );
  }

  // Delete document (works offline)
  async deleteDocument(
    collectionName: string,
    docId: string
  ): Promise<void> {
    await deleteDoc(doc(this.db, collectionName, docId));
  }

  // Query with offline support
  async queryDocuments(
    collectionName: string,
    field: string,
    operator: any,
    value: any
  ): Promise<any[]> {
    const q = query(
      collection(this.db, collectionName),
      where(field, operator, value)
    );

    const snapshot = await getDocs(q);
    return snapshot.docs.map((doc) => ({
      id: doc.id,
      ...doc.data()
    }));
  }

  async disableOfflinePersistence(): Promise<void> {
    await disablePersistence(this.db);
  }
}
```

---

## 8. WatermelonDB for React Native

```typescript
import {
  Database,
  Model,
  Q
} from '@nozbe/watermelondb';
import SQLiteAdapter from '@nozbe/watermelondb/adapters/sqlite';
import { tableSchema, appSchema } from '@nozbe/watermelondb';

// Define schema
const schema = appSchema({
  version: 1,
  tables: [
    tableSchema({
      name: 'notes',
      columns: [
        { name: 'title', type: 'string' },
        { name: 'content', type: 'string' },
        { name: 'synced', type: 'boolean', isIndexed: true },
        { name: 'version', type: 'number' },
        { name: 'created_at', type: 'number' },
        { name: 'updated_at', type: 'number' }
      ]
    }),
    tableSchema({
      name: 'tags',
      columns: [
        { name: 'name', type: 'string' },
        { name: 'note_id', type: 'string', isIndexed: true }
      ]
    })
  ]
});

// Define models
class Note extends Model {
  static table = 'notes';
  static associations = {
    tags: { type: 'has_many', foreignKey: 'note_id' }
  };

  title!: string;
  content!: string;
  synced!: boolean;
  version!: number;
  createdAt!: number;
  updatedAt!: number;
}

class Tag extends Model {
  static table = 'tags';
  name!: string;
  noteId!: string;
}

// Initialize database
const adapter = new SQLiteAdapter({
  schema,
  dbname: 'MyApp'
});

export const database = new Database({
  adapter,
  modelClasses: [Note, Tag]
});

// Usage: Query and create
class WatermelonDBManager {
  async createNote(title: string, content: string): Promise<void> {
    await database.write(async () => {
      await database.get<Note>('notes').create((note) => {
        note.title = title;
        note.content = content;
        note.synced = false;
        note.version = 1;
        note.createdAt = Date.now();
        note.updatedAt = Date.now();
      });
    });
  }

  async getUnsyncedNotes(): Promise<Note[]> {
    const notesCollection = database.get<Note>('notes');
    const unsyncedNotes = await notesCollection.query(
      Q.where('synced', false)
    ).fetch();
    return unsyncedNotes;
  }

  async updateNote(noteId: string, title: string, content: string): Promise<void> {
    await database.write(async () => {
      const note = await database.get<Note>('notes').find(noteId);
      await note.update((n) => {
        n.title = title;
        n.content = content;
        n.synced = false;
        n.updatedAt = Date.now();
      });
    });
  }

  async deleteNote(noteId: string): Promise<void> {
    await database.write(async () => {
      const note = await database.get<Note>('notes').find(noteId);
      await note.destroyPermanently();
    });
  }

  async markNoteAsSynced(noteId: string): Promise<void> {
    await database.write(async () => {
      const note = await database.get<Note>('notes').find(noteId);
      await note.update((n) => {
        n.synced = true;
      });
    });
  }

  async observeNotes(callback: (notes: Note[]) => void): Promise<void> {
    const notesCollection = database.get<Note>('notes');
    notesCollection.query().observe().subscribe((notes) => {
      callback(notes);
    });
  }
}
```

---

## 9. Background Sync Scheduling

### React Native with React-Native-Background-Fetch

```typescript
import BackgroundFetch from 'react-native-background-fetch';

class BackgroundSyncScheduler {
  async initializeBackgroundSync(): Promise<void> {
    // Configure background fetch
    const status = await BackgroundFetch.configure(
      {
        minimumFetchInterval: 15, // minutes
        stopOnTerminate: false,
        enableHeadless: true
      },
      async (taskId: string) => {
        console.log('[BackgroundFetch] Task:', taskId);

        try {
          await this.performSync();
          BackgroundFetch.finish(taskId);
        } catch (error) {
          console.error('Sync failed:', error);
          BackgroundFetch.finish(taskId);
        }
      },
      (taskId: string) => {
        console.log('[BackgroundFetch] TIMEOUT:', taskId);
        BackgroundFetch.finish(taskId);
      }
    );

    console.log('[BackgroundFetch] Status:', status);
  }

  private async performSync(): Promise<void> {
    // Implement sync logic
    console.log('Performing background sync...');

    // Get pending operations
    const pending = await this.getPendingOperations();

    // Sync each operation
    for (const operation of pending) {
      try {
        await this.syncOperation(operation);
      } catch (error) {
        console.error('Failed to sync operation:', operation.id);
      }
    }
  }

  private async getPendingOperations(): Promise<any[]> {
    return [];
  }

  private async syncOperation(operation: any): Promise<void> {
    // Send to server
  }

  stopBackgroundSync(): void {
    BackgroundFetch.stop();
  }
}
```

### Web with Service Workers

```typescript
// service-worker.ts
self.addEventListener('sync', (event: any) => {
  if (event.tag === 'sync-pending-operations') {
    event.waitUntil(
      (async () => {
        try {
          const queue = await openQueue();
          const pending = await queue.getAll();

          for (const item of pending) {
            try {
              await syncItem(item);
              await queue.delete(item.key);
            } catch (error) {
              console.error('Sync failed for:', item);
            }
          }
        } catch (error) {
          console.error('Background sync failed:', error);
        }
      })()
    );
  }
});

async function openQueue() {
  return new Promise((resolve) => {
    const request = indexedDB.open('sync-queue', 1);

    request.onupgradeneeded = (event: any) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('operations')) {
        db.createObjectStore('operations', { keyPath: 'id' });
      }
    };

    request.onsuccess = () => {
      const db = request.result;
      const tx = db.transaction('operations', 'readonly');
      resolve(tx.objectStore('operations'));
    };
  });
}

async function syncItem(item: any): Promise<void> {
  const response = await fetch('/api/sync', {
    method: 'POST',
    body: JSON.stringify(item)
  });

  if (!response.ok) {
    throw new Error(`Sync failed: ${response.statusText}`);
  }
}

// Register sync in app
export function registerBackgroundSync(): void {
  if ('serviceWorker' in navigator && 'SyncManager' in window) {
    navigator.serviceWorker.ready.then((registration) => {
      return (registration as any).sync.register('sync-pending-operations');
    });
  }
}
```

---

## 10. Retry Strategies: Exponential Backoff with Jitter

```typescript
interface RetryConfig {
  maxRetries: number;
  initialDelayMs: number;
  maxDelayMs: number;
  backoffMultiplier: number;
  jitterFactor: number; // 0-1
}

class ExponentialBackoffRetry {
  private config: RetryConfig;

  constructor(config: Partial<RetryConfig> = {}) {
    this.config = {
      maxRetries: 5,
      initialDelayMs: 1000,
      maxDelayMs: 60000,
      backoffMultiplier: 2,
      jitterFactor: 0.1,
      ...config
    };
  }

  async executeWithRetry<T>(
    operation: () => Promise<T>,
    operationName: string = 'operation'
  ): Promise<T> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= this.config.maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error as Error;

        if (attempt === this.config.maxRetries) {
          break; // Don't delay after final attempt
        }

        const delay = this.calculateDelay(attempt);
        console.log(
          `${operationName} failed (attempt ${attempt + 1}/${
            this.config.maxRetries + 1
          }). Retrying in ${delay}ms...`
        );

        await this.sleep(delay);
      }
    }

    throw new Error(
      `${operationName} failed after ${this.config.maxRetries + 1} attempts. ` +
        `Last error: ${lastError?.message}`
    );
  }

  private calculateDelay(attempt: number): number {
    // Base exponential backoff
    const exponentialDelay = this.config.initialDelayMs *
      Math.pow(this.config.backoffMultiplier, attempt);

    // Cap at max delay
    const cappedDelay = Math.min(
      exponentialDelay,
      this.config.maxDelayMs
    );

    // Add jitter: random percentage of delay
    const jitter = cappedDelay * this.config.jitterFactor * Math.random();

    return Math.floor(cappedDelay + jitter);
  }

  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

// Usage
const retry = new ExponentialBackoffRetry({
  maxRetries: 5,
  initialDelayMs: 1000,
  maxDelayMs: 30000,
  jitterFactor: 0.1
});

async function syncWithServer() {
  await retry.executeWithRetry(
    async () => {
      const response = await fetch('/api/sync', {
        method: 'POST',
        body: JSON.stringify({ data: 'sync-data' })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return response.json();
    },
    'Server sync'
  );
}
```

---

## 11. Data Integrity Validation (Checksums)

```typescript
import { createHash } from 'crypto';

class DataIntegrityValidator {
  // Generate checksum for data
  generateChecksum(data: any): string {
    const jsonString = JSON.stringify(data);
    return createHash('sha256').update(jsonString).digest('hex');
  }

  // Validate data against checksum
  validateChecksum(data: any, expectedChecksum: string): boolean {
    const calculatedChecksum = this.generateChecksum(data);
    return calculatedChecksum === expectedChecksum;
  }

  // Create checksummed entity
  createChecksummedEntity(data: any): any {
    return {
      ...data,
      _checksum: this.generateChecksum(data),
      _timestamp: Date.now()
    };
  }

  // Validate entire dataset
  validateDataset(records: any[]): { valid: boolean; invalidIds: string[] } {
    const invalidIds: string[] = [];

    for (const record of records) {
      const { _checksum, ...data } = record;

      if (!_checksum) {
        console.warn(`Record ${record.id} missing checksum`);
        invalidIds.push(record.id);
        continue;
      }

      if (!this.validateChecksum(data, _checksum)) {
        console.warn(`Record ${record.id} checksum mismatch`);
        invalidIds.push(record.id);
      }
    }

    return {
      valid: invalidIds.length === 0,
      invalidIds
    };
  }

  // Detect tampering
  detectTampering(
    original: any,
    currentChecksum: string,
    currentData: any
  ): boolean {
    const originalChecksum = this.generateChecksum(original);

    if (originalChecksum === currentChecksum) {
      return false; // Data unchanged
    }

    // Verify current data matches current checksum
    const calculatedChecksum = this.generateChecksum(currentData);
    return calculatedChecksum !== currentChecksum;
  }
}

// Usage in sync
class SafeSyncManager {
  private validator = new DataIntegrityValidator();

  async syncWithValidation(records: any[]): Promise<void> {
    // Checksum all records before sending
    const checksummedRecords = records.map((record) =>
      this.validator.createChecksummedEntity(record)
    );

    try {
      const response = await fetch('/api/sync', {
        method: 'POST',
        body: JSON.stringify(checksummedRecords)
      });

      const result = await response.json();

      // Validate server response
      const { valid, invalidIds } = this.validator.validateDataset(
        result.synced
      );

      if (!valid) {
        throw new Error(
          `Server returned invalid data for records: ${invalidIds.join(', ')}`
        );
      }
    } catch (error) {
      console.error('Sync with validation failed:', error);
      throw error;
    }
  }
}
```

---

## 12. Testing Offline Scenarios

```typescript
// Test utilities
class OfflineTestHelper {
  private originalFetch: typeof fetch;
  private isOffline = false;
  private failureRate = 0; // 0-1

  startOfflineMode(): void {
    this.isOffline = true;
    this.interceptFetch();
  }

  stopOfflineMode(): void {
    this.isOffline = false;
    this.restoreFetch();
  }

  setNetworkFailureRate(rate: number): void {
    this.failureRate = Math.max(0, Math.min(1, rate));
  }

  private interceptFetch(): void {
    this.originalFetch = global.fetch;

    global.fetch = async (...args: any[]) => {
      if (this.isOffline) {
        throw new Error('Network error: offline mode enabled');
      }

      if (Math.random() < this.failureRate) {
        throw new Error('Network error: simulated failure');
      }

      return this.originalFetch(...args);
    };
  }

  private restoreFetch(): void {
    global.fetch = this.originalFetch;
  }
}

// Test cases
describe('Offline-First Sync', () => {
  let helper: OfflineTestHelper;
  let syncManager: any; // Your sync manager

  beforeEach(() => {
    helper = new OfflineTestHelper();
    syncManager = new YourSyncManager();
  });

  afterEach(() => {
    helper.stopOfflineMode();
  });

  test('should queue operations when offline', async () => {
    helper.startOfflineMode();

    await expect(syncManager.updateNote('123', 'Content')).rejects.toThrow();

    const queue = await syncManager.getPendingOperations();
    expect(queue).toHaveLength(1);
    expect(queue[0].operation).toBe('update');
  });

  test('should sync when coming back online', async () => {
    helper.startOfflineMode();
    await syncManager.updateNote('123', 'New Content');

    helper.stopOfflineMode();
    await syncManager.sync();

    const queue = await syncManager.getPendingOperations();
    expect(queue).toHaveLength(0);
  });

  test('should handle conflicts during sync', async () => {
    const local = { id: '1', title: 'Local', version: 1 };
    const remote = { id: '1', title: 'Remote', version: 2 };

    const resolved = syncManager.resolveConflict(local, remote);
    expect(resolved.title).toBe('Remote');
  });

  test('should retry with exponential backoff', async () => {
    let attempts = 0;
    helper.setNetworkFailureRate(0.8);

    try {
      await syncManager.syncWithRetry();
    } catch (error) {
      // Expected to fail
    }

    expect(attempts).toBeGreaterThan(1);
  });

  test('should validate data integrity', async () => {
    const validator = new DataIntegrityValidator();
    const data = { id: '1', name: 'Test' };
    const entity = validator.createChecksummedEntity(data);

    expect(validator.validateChecksum(data, entity._checksum)).toBe(true);

    data.name = 'Modified';
    expect(validator.validateChecksum(data, entity._checksum)).toBe(false);
  });

  test('should recover from corrupted data', async () => {
    helper.startOfflineMode();
    await syncManager.updateNote('123', 'Data');

    const queue = await syncManager.getPendingOperations();
    queue[0].data = null; // Corrupt

    helper.stopOfflineMode();
    await expect(syncManager.sync()).rejects.toThrow();

    const remaining = await syncManager.getPendingOperations();
    expect(remaining).toHaveLength(1);
  });
});
```

---

## Key Takeaways

1. **Local-First Design**: Data lives locally first; sync is opportunistic
2. **Conflict Resolution**: Choose strategy based on use case (LWW, merge functions, CRDTs)
3. **Queuing**: Persist operations and retry with exponential backoff
4. **Network Awareness**: Monitor connectivity and adjust behavior
5. **Data Integrity**: Validate checksums to detect corruption/tampering
6. **User Experience**: Optimistic updates with rollback on failure
7. **Testing**: Simulate offline and failure scenarios comprehensively
8. **Framework Integration**: Use platform-specific libraries (Firebase, WatermelonDB, etc.)

## References

- [Local-First Software](https://www.inkandswitch.com/local-first/)
- [CRDTs for Non-Academics](https://www.figma.com/blog/how-figmas-multiplayer-technology-works/)
- [Firebase Offline Persistence](https://firebase.google.com/docs/firestore/manage-data/enable-offline-persistence)
- [WatermelonDB Documentation](https://watermelondb.nozbe.com/)
- [Network Information API](https://developer.mozilla.org/en-US/docs/Web/API/Network_Information_API)
