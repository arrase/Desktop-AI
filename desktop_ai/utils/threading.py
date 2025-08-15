"""Threading utilities for async operations in Qt."""

import asyncio
from typing import Callable, Any
from PyQt6.QtCore import QThread, QObject, pyqtSignal


class AsyncWorker(QObject):
    """Generic worker for executing async functions in a separate thread."""
    
    result_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, async_func: Callable, *args, **kwargs):
        super().__init__()
        self.async_func = async_func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        """Execute the async function and emit the result."""
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                self.async_func(*self.args, **self.kwargs)
            )
            self.result_ready.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            loop.close()


class ThreadManager:
    """Helper class to manage QThread lifecycle."""
    
    def __init__(self):
        self._thread = None
        self._worker = None
    
    def is_active(self) -> bool:
        """Check if a thread is currently running."""
        if self._thread is None:
            return False
        try:
            return self._thread.isRunning()
        except RuntimeError:
            self._thread = None
            return False
    
    def start_async_task(self, async_func: Callable, *args, **kwargs) -> AsyncWorker:
        """Start an async task in a separate thread."""
        if self.is_active():
            raise RuntimeError("A task is already running")
        
        self._thread = QThread()
        self._worker = AsyncWorker(async_func, *args, **kwargs)
        self._worker.moveToThread(self._thread)
        
        # Connect signals
        self._thread.started.connect(self._worker.run)
        self._worker.result_ready.connect(self._thread.quit)
        self._worker.error_occurred.connect(self._thread.quit)
        self._worker.result_ready.connect(self._worker.deleteLater)
        self._worker.error_occurred.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._cleanup)
        self._thread.finished.connect(self._thread.deleteLater)
        
        self._thread.start()
        return self._worker
    
    def _cleanup(self):
        """Clean up thread references."""
        self._thread = None
        self._worker = None
