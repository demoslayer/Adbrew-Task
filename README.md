# NOTE: DO NOT FORK THIS REPOSITORY. CLONE AND SETUP A STANDALONE REPOSITORY.

# Adbrew Test!

Hello! This test is designed to specifically test your Python, React and web development skills. The task is unconventional and has a slightly contrived setup on purpose and requires you to learn basic concepts of Docker on the fly. 

## What We Built

This project implements a full-stack TODO application with:
- **React Frontend** (http://localhost:3000): Displays todos and provides a form to create new ones
- **Django REST API** (http://localhost:8000): Handles GET and POST requests for todos
- **MongoDB Database** (port 27017): Persists all todo data

### Implementation Summary

 **Backend (Django)**: 
- GET `/todos/` endpoint fetches all todos from MongoDB
- POST `/todos/` endpoint creates new todos in MongoDB
- Uses `pymongo` directly (no Django ORM/models)
- Production-ready error handling and logging

 **Frontend (React)**:
- Custom `useTodos` hook for API logic
- React Hooks implementation (`useState`, `useEffect`, `useCallback`)
- Fetches todos on mount from backend
- Form submission creates todos via POST request
- Automatically refreshes list after successful creation
- Loading states and error handling

---

# Structure

This repository includes code for a Docker setup with 3 containers:
* **App**: This is the React dev server and runs on http://localhost:3000. The code for this resides in `src/app` directory.
* **API**: This is the backend container that runs a Django instance on http://localhost:8000. The code resides in `src/rest` directory.
* **Mongo**: This is a DB instance running on port 27017. Django views connect to this instance of Mongo.

We highly recommend you go through the setup in `Dockerfile` and `docker-compose.yml`. If you are able to understand and explain the setup, that will be a huge differentiator.

---

# Problems Encountered & Solutions

## Problem 1: MongoDB Container Failing to Start 

### Issue
MongoDB container was continuously restarting with error:
```
/usr/bin/mongod: error while loading shared libraries: libcrypto.so.1.1: cannot open shared object file
```

### Root Cause
- MongoDB 4.4 requires `libssl1.1` (provides `libcrypto.so.1.1`)
- Docker base image (`python:3.8`) is based on Debian Bookworm
- Debian Buster (which had `libssl1.1`) reached End of Life (EOL)
- Package downloads from official repositories failed with 404 errors

### Solution 
1. **Extracted library files** from a working Debian Buster container
2. **Stored libraries** in `adb_test/libs/usr/lib/x86_64-linux-gnu/`:
   - `libcrypto.so.1.1`
   - `libssl.so.1.1`
3. **Mounted as volume** in `docker-compose.yml`
4. **Auto-copy on startup**: MongoDB container command copies libraries if they don't exist

**Files Modified**:
- `docker-compose.yml`: Added volume mount and startup command
- Created `libs/usr/lib/x86_64-linux-gnu/` directory with library files

---

## Problem 2: React App Not Starting 

### Issue
React app container failed with error:
```
Error [ERR_PACKAGE_PATH_NOT_EXPORTED]: Package subpath './lib/tokenize' is not defined by "exports"
```

### Root Cause
- Container was using Node.js v18.20.4 (from cached build)
- `react-scripts@4.0.1` requires Node.js 16.x
- Node.js 18 has stricter module resolution incompatible with older packages

### Solution 
- Rebuilt app container **without cache** to ensure Node.js 16 installation
- Verified Node.js version: `v16.20.2`

**Command**:
```powershell
docker-compose build --no-cache app
docker-compose up -d app
```

---

## Problem 3: React Hook Dependency Warning ⚠️

### Issue
React compilation warning:
```
React Hook useEffect has a missing dependency: 'fetchTodos'
```

### Root Cause
- `fetchTodos` function wasn't memoized with `useCallback`
- Missing from `useEffect` dependency array

### Solution 
- Wrapped `fetchTodos` in `useCallback` hook
- Added `fetchTodos` to `useEffect` dependency array

**File Modified**: `src/app/src/App.js`

---

# Setup

## Prerequisites
- Docker and Docker Compose installed
- Git installed

## Installation Steps

### 1. Clone Repository
```bash
git clone https://github.com/adbrew/test.git
cd test
```

### 2. Set Environment Variable

**Windows (PowerShell)**:
```powershell
cd adb_test
$env:ADBREW_CODEBASE_PATH="C:\Users\satwi\OneDrive\Desktop\Adbrew\adb_test\src"
```

**Linux/Mac**:
```bash
cd adb_test
export ADBREW_CODEBASE_PATH="$(pwd)/src"
```

### 3. Build Containers
 **This step takes 10-15 minutes** (downloads dependencies, builds images)

```bash
docker-compose build
```

**Note**: If you encounter MongoDB library issues, the libraries are already included in the `libs/` directory and will be automatically mounted.

### 4. Start Containers
```bash
docker-compose up -d
```

### 5. Verify Containers Are Running
```bash
docker ps
```

Expected output:
```
CONTAINER ID   IMAGE            COMMAND                  STATUS         PORTS                      NAMES
xxx            adb_test-api     "bash -c 'cd /src/re…"   Up X minutes   0.0.0.0:8000->8000/tcp     api
xxx            adb_test-app     "bash -c 'cd /src/ap…"   Up X minutes   0.0.0.0:3000->3000/tcp     app
xxx            adb_test-mongo   "bash -c 'if [ ! -f …"   Up X minutes   0.0.0.0:27017->27017/tcp   mongo
```

### 6. Verify Services
- **Frontend**: http://localhost:3000 (may take 2-3 minutes to compile)
- **Backend API**: http://localhost:8000/todos/ (should return `{"todos":[]}`)

### 7. Troubleshooting

If containers fail to start:

**Check logs**:
```bash
docker logs mongo --tail 50
docker logs app --tail 50
docker logs api --tail 50
```

**Rebuild if needed**:
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

**Restart specific container**:
```bash
docker-compose restart mongo
docker-compose restart app
docker-compose restart api
```

# Tips

1. **View container logs**: `docker logs -f --tail=100 {container_name}`
   - Replace `{container_name}` with `app`, `api`, or `mongo`

2. **Enter container shell**: `docker exec -it {container_name} bash`
   - Useful for debugging and inspecting files

3. **Stop all containers**: `docker-compose down`

4. **Restart container**: `docker restart {container_name}`

5. **Check Node.js version** (in app container): `docker exec app node --version`
   - Should show `v16.20.2`

6. **Check MongoDB status**: `docker exec mongo ps aux | grep mongod`
   - Should show mongod process running

---

# Task

When you run `localhost:3000`, you should see:

1. **A form** with a TODO description textbox and a submit button. On form submission, the app interacts with the Django backend (`POST http://localhost:8000/todos`) and creates a TODO in MongoDB.

2. **A list** showing TODOs from the backend (`GET http://localhost:8000/todos`). This replaces any hardcoded TODO list.

3. **Auto-refresh**: When the form is submitted, the TODO list automatically refreshes and fetches the latest list of TODOs from MongoDB.

---

# Implementation Details

## Backend Implementation (`src/rest/rest/views.py`)

### GET `/todos/` Endpoint
```python
def get(self, request):
    todos_cursor = todos_collection.find({})
    todos = []
    for todo in todos_cursor:
        todos.append({
            'id': str(todo['_id']),
            'description': todo.get('description', ''),
            'created_at': todo.get('created_at', datetime.utcnow()).isoformat()
        })
    return Response({'todos': todos}, status=status.HTTP_200_OK)
```

### POST `/todos/` Endpoint
```python
def post(self, request):
    description = request.data.get('description', '').strip()
    if not description:
        return Response({'error': 'Description is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    todo_doc = {
        'description': description,
        'created_at': datetime.utcnow()
    }
    result = todos_collection.insert_one(todo_doc)
    
    created_todo = {
        'id': str(result.inserted_id),
        'description': description,
        'created_at': todo_doc['created_at'].isoformat()
    }
    return Response({'todo': created_todo, 'message': 'Todo created successfully'}, status=status.HTTP_201_CREATED)
```

**Key Features**:
- Direct MongoDB access using `pymongo` (no Django ORM)
- Proper error handling and HTTP status codes
- Input validation
- Logging for debugging

## Frontend Implementation (`src/app/src/App.js`)

### Custom Hook: `useTodos`
```javascript
const useTodos = () => {
  const [todos, setTodos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchTodos = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/todos/`);
      const data = await response.json();
      setTodos(data.todos || []);
    } catch (err) {
      setError(err.message || 'Failed to fetch todos');
    } finally {
      setLoading(false);
    }
  }, []);

  const createTodo = async (description) => {
    const response = await fetch(`${API_BASE_URL}/todos/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description }),
    });
    await fetchTodos(); // Refresh list after creation
    return await response.json();
  };

  return { todos, loading, error, fetchTodos, createTodo };
};
```

### Main Component
```javascript
export function App() {
  const { todos, loading, error, fetchTodos, createTodo } = useTodos();
  const [todoInput, setTodoInput] = useState('');

  useEffect(() => {
    fetchTodos(); // Fetch on mount
  }, [fetchTodos]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await createTodo(todoInput.trim());
    setTodoInput(''); // Clear input
  };

  return (
    <div className="App">
      <div>
        <h1>List of TODOs</h1>
        {loading && <p>Loading todos...</p>}
        {error && <p style={{ color: 'red' }}>Error: {error}</p>}
        <ul>
          {todos.map((todo) => (
            <li key={todo.id}>{todo.description}</li>
          ))}
        </ul>
      </div>
      <div>
        <h1>Create a ToDo</h1>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={todoInput}
            onChange={(e) => setTodoInput(e.target.value)}
            placeholder="Enter todo description"
          />
          <button type="submit">Add ToDo!</button>
        </form>
      </div>
    </div>
  );
}
```

**Key Features**:
- ✅ React Hooks only (no class components)
- ✅ Custom hook for API logic (separation of concerns)
- ✅ Loading and error states
- ✅ Automatic list refresh after creation
- ✅ Input validation

# Instructions [IMPORTANT] 

1. **React Hooks Only**: All React code must use [React hooks](https://reactjs.org/docs/hooks-intro.html). No class components or lifecycle methods.

2. **MongoDB Direct Access**: Do not use Django's models, serializers, or SQLite DB. Persist and retrieve all data from the mongo instance. A `db` instance is already present in `views.py`.

3. **Docker Setup Required**: Do not bypass the Docker setup. Submissions without proper docker setup will be rejected.

4. **Learning on the Fly**: We expect you to learn and grasp basic React Hooks/Mongo/Docker concepts on the fly.

5. **No Forking**: Do not fork this repository or submit your solution as a PR. Send us a link to your repo privately.

6. **Code Walkthrough**: If you complete the test, we will have a live walkthrough of your code and ask questions to check your understanding.

7. **Production-Ready Code**: Code quality should be production-ready:
   - Error handling
   - Abstractions
   - Well-maintainable and modular code
   - Software design principles

   **Reading Resources**:
   * https://kinsta.com/blog/python-object-oriented-programming/
   * https://realpython.com/solid-principles-python/
   * https://www.toptal.com/python/python-design-patterns

---

# Docker Configuration Details

## docker-compose.yml

**Key Features**:
- Custom network (`adb_test_network`) for container communication
- Volume mounts for code persistence and MongoDB data
- MongoDB library files mounted from `libs/` directory
- Auto-installation of MongoDB libraries on startup

**Network**: All containers communicate via `adb_test_network` bridge network

**Volumes**:
- Code: `${ADBREW_CODEBASE_PATH}:/src` (shared across api and app)
- MongoDB data: `${ADBREW_CODEBASE_PATH}/db/:/data/db`
- MongoDB libraries: `${ADBREW_CODEBASE_PATH}/../libs:/tmp/libs:ro`

## Dockerfile

**Base Image**: `python:3.8`

**Key Installations**:
- Node.js 16.x (required for react-scripts 4.0.1)
- Yarn package manager
- MongoDB 4.4 (with dependency workarounds)
- Python dependencies from `requirements.txt`

**MongoDB Fix**: Libraries are installed at runtime via volume mount to work around Debian EOL issues.

---

# Current Status

 **All Issues Resolved**:
- MongoDB starts successfully with libssl1.1 libraries
- React app compiles and runs with Node.js 16
- No React Hook warnings
- All containers communicate properly
- Application is fully functional

 **All Requirements Met**:
- Form creates TODOs via POST request
- List displays TODOs from GET request
- List refreshes after form submission
- React Hooks implementation
- MongoDB persistence (no Django ORM)
- Docker setup working

---

# Additional Documentation

For more detailed information, see:
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
- `BUILD_FIX.md` - MongoDB build fix details
- `DOCKER_BUILD_EXPLANATION.md` - Docker build caching explanation
- `QUICK_START.md` - Quick reference for Docker commands

---

# Testing the Application

1. **Start all containers**: `docker-compose up -d`

2. **Wait for React to compile** (2-3 minutes):
   - Check logs: `docker logs app -f`
   - Look for: "Compiled successfully!"

3. **Open browser**: http://localhost:3000

4. **Test functionality**:
   - Enter a todo description
   - Click "Add ToDo!"
   - Verify it appears in the list
   - Check backend: http://localhost:8000/todos/

5. **Verify persistence**:
   - Restart containers: `docker-compose restart`
   - Todos should still be there (stored in MongoDB)

---

# Support

If you encounter issues:
1. Check container logs: `docker logs {container_name}`
2. Verify environment variable is set correctly
3. Ensure Docker has enough resources allocated
4. Try rebuilding without cache: `docker-compose build --no-cache`
5. Check that MongoDB libraries exist in `libs/usr/lib/x86_64-linux-gnu/` directory
