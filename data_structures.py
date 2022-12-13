# Author: Donato Quartuccia
# Last Modified: 2022-12-12


class DirectoryStack:
    """A directory stack with an popped-directory accumulator and history"""
    def __init__(self, max_tracked_directory_size: int = None):
        self._directories = []
        self._max_size = max_tracked_directory_size if max_tracked_directory_size else float('inf')
        self._accumulator = 0

    def __len__(self):
        return len(self._directories)

    @property
    def accumulator(self) -> int:
        """Total size of all directories popped"""
        return self._accumulator

    def update_size(self, size: int):
        """Updates the size of the *last* directory that was pushed onto the stack"""
        self._directories[-1][1] += size

    def push(self, directory: str, size: int) -> None:
        """Push a directory onto the stack"""
        self._directories.append([directory, size])

    def pop(self) -> tuple[str, int]:
        """Pop a directory from the stack and return the path to the directory and its size"""
        path = '/'.join(directory for directory, _ in self._directories)
        directory, size = self._directories.pop()
        if self._directories:
            self.update_size(size)
        self._accumulator += size if size <= self._max_size else 0
        return path, size
