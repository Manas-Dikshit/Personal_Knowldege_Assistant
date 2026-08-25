# OS Lab

A collection of Java programs that demonstrate core operating-system system calls
(process management, process IDs, and directory operations) along with the underlying
OS concepts each one illustrates.

> **Note:** The folder structure of this repo is intentionally kept minimal and will
> grow over time as more programs are added. Each `.java` file is a standalone,
> self-contained program.

---

## Contents

| File | What it demonstrates |
|------|----------------------|
| `ChildTask.java` | A child process entry point; prints its own PID and an argument |
| `ProcessSyscalls.java` | `fork` + `exec` + `wait` (process creation and reuse) via `ProcessBuilder` |
| `DirectorySetup.java` | `opendir`, `readdir`, `closedir` (directory listing) |
| `MultipleDirectories.java` | `opendir`, `readdir`, `closedir` across multiple directories |
| `SyscallCommands.java` | Executes shell-level system programs (`ls`, `cp`, `grep`) and captures output |

Each file has its own `README-<name>.md` that explains the system calls it uses in detail.

---

## C programs

Go to the [`C-programusing/`](./C-programusing) folder to get the C equivalents of these
programs. They perform the exact same tasks but are written in C using raw system calls and
pointers (`char**`, `struct dirent*`, `DIR*`, process IDs). Everything platform-specific is
isolated in a single portable header (`osport.h`), so the programs compile and run on both
Windows and Linux/Unix with no include errors. The code is strictly local and safe: it only
touches the current folder, never spawns a shell (no `system()` / shell injection surface),
uses bounded string operations, and never opens network connections or elevates privileges.

---

## Prerequisites

- **JDK 9 or later** (programs use `ProcessHandle`, added in Java 9)
- **Git for Windows** (bash shell) — only required by `SyscallCommands.java`, which shells
  out to `ls`, `cp`, and `grep`. If you want that program to run, install Git Bash at the
  default location or update the Bash path in the source.

Verify Java is installed:

```bash
java -version
javac -version
```

---

## How to compile and run

Compile all programs (from the repo root):

```bash
javac *.java
```

This produces the corresponding `.class` files (which are git-ignored via the repo's
`.gitignore`).

### Run each program

```bash
# 1. Print the current process PID
java ChildTask
java ChildTask "any message"

# 2. Parent spawns a child; shows parent PID, child PID, and the child's exit code
java ProcessSyscalls

# 3. List the contents of the current directory
java DirectorySetup

# 4. List the contents of a specific directory
java DirectorySetup C:\Users\manas\Downloads\OSLab

# 5. List the contents of several directories at once
java MultipleDirectories newdir .
java MultipleDirectories newdir C:\Users\manas\Downloads\OSLab C:\Windows

# 6. Run shell utilities (ls, cp, grep) and print their output
java SyscallCommands
```

> **Windows note:** Directory paths like `C:\Users\...` can be passed as-is in most shells.
> If your shell interprets backslashes, use forward slashes instead: `C:/Users/manas/Downloads/OSLab`.

---

## The system calls demonstrated

| OS system call | Purpose | Demonstrated in |
|----------------|---------|-----------------|
| `fork` | Create a new child process | `ProcessSyscalls.java` |
| `exec` | Replace a process image with a new program | `ProcessSyscalls.java` |
| `wait` / `waitpid` | Parent waits for a child to finish | `ProcessSyscalls.java` |
| `getpid` | Get the current process ID | `ChildTask.java`, `ProcessSyscalls.java` |
| `exit` | Terminate a process and return a status | `ChildTask.java`, `ProcessSyscalls.java`, `SyscallCommands.java` |
| `opendir` | Open a directory for reading | `DirectorySetup.java`, `MultipleDirectories.java` |
| `readdir` | Read the next entry of an open directory | `DirectorySetup.java`, `MultipleDirectories.java` |
| `closedir` | Close an open directory | `DirectorySetup.java`, `MultipleDirectories.java` |

> Java exposes these OS concepts through its standard library rather than raw system calls:
> `ProcessBuilder` / `Process` stand in for `fork`/`exec`/`wait`, `ProcessHandle` for `getpid`,
> and `Files.newDirectoryStream` for `opendir`/`readdir`/`closedir`.

---

## Per-file system call readmes

- [`README-ChildTask.md`](./README-ChildTask.md)
- [`README-ProcessSyscalls.md`](./README-ProcessSyscalls.md)
- [`README-DirectorySetup.md`](./README-DirectorySetup.md)
- [`README-MultipleDirectories.md`](./README-MultipleDirectories.md)
- [`README-SyscallCommands.md`](./README-SyscallCommands.md)

---

## Cleanup

Remove the compiled `.class` files when you are done:

```bash
rm *.class
```

---

## License

Free to use for learning purposes.

---

Made by MRD with ❤️