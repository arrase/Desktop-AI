"""Simplified threading utilities."""
import asyncio
from typing import Callable
from PyQt6.QtCore import QThread, QObject, pyqtSignal


class AsyncWorker(QObject):
    """Worker for async operations."""
    
    result_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, async_func: Callable, *args, **kwargs):
        super().__init__()
        self.async_func = async_func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        """Execute the async function."""
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
    """Simple thread manager."""
    
    def __init__(self):
        self._thread = None
        self._worker = None
    
    def is_active(self) -> bool:
        """Check if thread is running."""
        return self._thread is not None and self._thread.isRunning()
    
    def start_task(self, async_func: Callable, *args, **kwargs) -> AsyncWorker:
        """Start an async task."""
        if self.is_active():
            raise RuntimeError("Task already running")
        
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
        """Clean up references."""
        self._thread = None
        self._worker = None
