# Distributed Lock using Redis and Python

## Overview

This project implements a Redis-based distributed lock in Python using Redis as the centralized lock manager.

The implementation demonstrates how multiple independent processes coordinate access to a shared resource while preventing race conditions.

The lock implementation includes:

- Atomic lock acquisition using `SET NX PX`
- UUID-based lock ownership
- Automatic lock expiration (TTL)
- Atomic lock release using Lua scripting
- Redis deployment using Docker Compose

The implementation follows the locking approach recommended in the Redis documentation and is intended as an educational implementation of distributed synchronization.

---

## Problem Statement

In distributed systems, multiple application instances may attempt to modify the same shared resource simultaneously.

Common examples include:

- Inventory management
- Payment processing
- Order placement
- Cron jobs
- Report generation

Without synchronization, multiple workers can enter the critical section simultaneously.

Example:

```
Inventory

Stock = 1
```

Worker A

```
Stock = 1
```

Worker B

```
Stock = 1
```

Both workers process the order before either updates the database.

Result

```
Two successful orders

Only one item existed.
```

This is a classic race condition.

---

# Architecture

The following diagram illustrates the interaction between workers, Redis, and the protected resource.

<p align="center">
    <img src="images/arch-1.svg" width="850">
</p>

Redis acts as the centralized lock manager.

Only one worker can successfully acquire the lock at any point in time.

---

# Lock Lifecycle

The lock lifecycle from acquisition to release is shown below.

<p align="center">
    <img src="images/redislockflow-1.svg" width="900">
</p>

The worker:

1. Requests the lock
2. Executes the critical section
3. Releases the lock using an atomic Lua script

---

## Design Decisions

### Redis

Redis provides:

- Atomic commands
- Very low latency
- Automatic key expiration
- High throughput

Making it suitable for distributed coordination.

---

### Atomic Lock Acquisition

The lock is created using

```
SET lock_key owner_id NX PX timeout
```

| Parameter | Description |
|-----------|-------------|
| SET | Create key |
| NX | Only create if key does not exist |
| PX | Expiration time |
| owner_id | UUID identifying lock owner |

This operation is atomic.

---

### UUID Ownership

Each worker generates a unique UUID.

Example

```
inventory_lock

↓

4a8cde32-8d23-46f5-a31b...
```

The UUID identifies the owner of the lock.

Before releasing the lock, ownership is verified.

This prevents one worker from deleting another worker's lock.

---

### Automatic Expiration

Each lock has a configurable TTL.

If a worker crashes before releasing the lock, Redis automatically removes the key after expiration, preventing deadlocks.

---

### Atomic Unlock using Lua

Releasing a lock involves two logical operations:

1. Verify ownership
2. Delete the lock

Executing these as separate commands introduces a race condition.

Instead, Redis executes the following Lua script atomically.

```lua
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end
```

---

## Project Structure

```
distributed-lock-python/

├── archmermaids/
│   ├── arch.md
│   ├── redislockflow.md
│   ├── internalalgo.md
│   ├── luaunlock.md
│   ├── racecond(withoutlock).md
│   └── racecond(distributedlock).md
│
├── images/
│
├── config.py
├── redis_lock.py
├── unlock.lua
├── test_connection.py
├── test_lock.py
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Installation

Clone the repository.

```bash
git clone https://github.com/Manas-Dikshit/distributed-lock-python.git
```

Move into the project directory.

```bash
cd distributed-lock-python
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Start Redis.

```bash
docker compose up -d
```

Verify the container.

```bash
docker ps
```

---

## Running

Verify the Redis connection.

```bash
python test_connection.py
```

Run the distributed lock demonstration.

```bash
python test_lock.py
```

---

## Verifying Redis

Open Redis CLI.

```bash
docker exec -it distributed-lock-redis redis-cli
```

Useful commands

```
PING
```

```
KEYS *
```

```
GET inventory_lock
```

```
TTL inventory_lock
```

---

## Implementation

The lock implementation follows four steps.

### 1. Generate a UUID

Each worker generates a unique owner identifier.

```python
owner_id = str(uuid.uuid4())
```

---

### 2. Acquire Lock

Redis executes

```
SET inventory_lock owner_id NX PX timeout
```

Only one worker succeeds.

---

### 3. Execute Critical Section

The worker performs the protected operation.

---

### 4. Release Lock

The worker executes the Lua script.

Redis verifies ownership before deleting the key.

---

## Testing

Open two terminals.

Terminal 1

```bash
python test_lock.py
```

Terminal 2

```bash
python test_lock.py
```

Expected result

- First worker acquires the lock.
- Second worker is denied.
- Lock expires automatically after TTL.
- Lock ownership can be inspected using Redis CLI.

---

# Screenshots

### Docker Container

<p align="center">
    <img src="images/docker-container.png" width="900">
</p>

### Redis CLI

<p align="center">
    <img src="images/redis-cli.png" width="900">
</p>

---

## Current Limitations

This implementation currently does not include:

- Retry mechanism
- Exponential backoff
- Lock renewal (Heartbeat)
- Watchdog thread
- Redlock algorithm
- High availability
- Automated tests

---

## Future Improvements

Planned enhancements include:

- Lock heartbeat
- Retry with exponential backoff
- Context manager support
- Worker simulation
- Benchmarking
- Unit testing
- GitHub Actions
- Redlock implementation

---

## References

- Redis Documentation
- Redis Distributed Locks
- Redis Lua Scripting
- redis-py Documentation

---

## License

This project is licensed under the MIT License.