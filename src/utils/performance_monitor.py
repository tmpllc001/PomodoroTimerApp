"""
Performance Monitor for Pomodoro Timer Application
Monitors memory usage, CPU usage, and response times.
"""

import time
import psutil
import threading
import logging
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    timestamp: datetime
    cpu_percent: float
    memory_usage: float  # MB
    memory_percent: float
    response_time: float  # milliseconds
    ui_updates_per_second: float
    active_threads: int
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_percent': self.cpu_percent,
            'memory_usage': self.memory_usage,
            'memory_percent': self.memory_percent,
            'response_time': self.response_time,
            'ui_updates_per_second': self.ui_updates_per_second,
            'active_threads': self.active_threads
        }


class PerformanceMonitor:
    """Monitors application performance metrics."""
    
    def __init__(self, sample_interval: float = 1.0):
        self.sample_interval = sample_interval
        self.is_monitoring = False
        self.metrics_history: List[PerformanceMetrics] = []
        self.max_history_size = 3600  # 1 hour of data at 1 second intervals
        
        self.process = psutil.Process()
        self.logger = logging.getLogger(__name__)
        
        # Performance thresholds
        self.cpu_threshold = 80.0  # percentage
        self.memory_threshold = 200.0  # MB
        self.response_time_threshold = 100.0  # milliseconds
        
        # Callbacks for performance alerts
        self.on_high_cpu: Optional[Callable[[float], None]] = None
        self.on_high_memory: Optional[Callable[[float], None]] = None
        self.on_slow_response: Optional[Callable[[float], None]] = None
        
        # UI update tracking
        self.ui_update_count = 0
        self.last_ui_update_time = time.time()
        
        # Response time tracking
        self.response_times: List[float] = []
        self.response_time_window = 100  # Keep last 100 measurements
        
        self.monitor_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
    def start_monitoring(self):
        """Start performance monitoring."""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.stop_event.clear()
            
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            
            self.logger.info("Performance monitoring started")
            
    def stop_monitoring(self):
        """Stop performance monitoring."""
        if self.is_monitoring:
            self.is_monitoring = False
            self.stop_event.set()
            
            if self.monitor_thread:
                self.monitor_thread.join(timeout=2.0)
                
            self.logger.info("Performance monitoring stopped")
            
    def _monitor_loop(self):
        """Main monitoring loop."""
        while not self.stop_event.is_set():
            try:
                metrics = self._collect_metrics()
                self._store_metrics(metrics)
                self._check_thresholds(metrics)
                
                time.sleep(self.sample_interval)
                
            except Exception as e:
                self.logger.error(f"Error in performance monitoring: {e}")
                time.sleep(self.sample_interval)
                
    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics."""
        # CPU and memory usage
        cpu_percent = self.process.cpu_percent()
        memory_info = self.process.memory_info()
        memory_usage = memory_info.rss / (1024 * 1024)  # Convert to MB
        memory_percent = self.process.memory_percent()
        
        # Response time (average of recent measurements)
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0.0
        
        # UI update rate
        current_time = time.time()
        time_diff = current_time - self.last_ui_update_time
        ui_updates_per_second = self.ui_update_count / time_diff if time_diff > 0 else 0
        
        # Reset UI update tracking
        self.ui_update_count = 0
        self.last_ui_update_time = current_time
        
        # Active threads
        active_threads = threading.active_count()
        
        return PerformanceMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_usage=memory_usage,
            memory_percent=memory_percent,
            response_time=avg_response_time,
            ui_updates_per_second=ui_updates_per_second,
            active_threads=active_threads
        )
        
    def _store_metrics(self, metrics: PerformanceMetrics):
        """Store metrics in history."""
        self.metrics_history.append(metrics)
        
        # Keep only recent history
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history.pop(0)
            
    def _check_thresholds(self, metrics: PerformanceMetrics):
        """Check performance thresholds and trigger alerts."""
        # Check CPU usage
        if metrics.cpu_percent > self.cpu_threshold:
            self.logger.warning(f"High CPU usage: {metrics.cpu_percent:.1f}%")
            if self.on_high_cpu:
                self.on_high_cpu(metrics.cpu_percent)
                
        # Check memory usage
        if metrics.memory_usage > self.memory_threshold:
            self.logger.warning(f"High memory usage: {metrics.memory_usage:.1f} MB")
            if self.on_high_memory:
                self.on_high_memory(metrics.memory_usage)
                
        # Check response time
        if metrics.response_time > self.response_time_threshold:
            self.logger.warning(f"Slow response time: {metrics.response_time:.1f} ms")
            if self.on_slow_response:
                self.on_slow_response(metrics.response_time)
                
    def record_ui_update(self):
        """Record a UI update event."""
        self.ui_update_count += 1
        
    def record_response_time(self, response_time: float):
        """Record a response time measurement."""
        self.response_times.append(response_time)
        
        # Keep only recent measurements
        if len(self.response_times) > self.response_time_window:
            self.response_times.pop(0)
            
    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get the most recent performance metrics."""
        return self.metrics_history[-1] if self.metrics_history else None
        
    def get_average_metrics(self, minutes: int = 5) -> Dict[str, float]:
        """Get average metrics over the specified time period."""
        if not self.metrics_history:
            return {}
            
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {}
            
        return {
            'cpu_percent': sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics),
            'memory_usage': sum(m.memory_usage for m in recent_metrics) / len(recent_metrics),
            'memory_percent': sum(m.memory_percent for m in recent_metrics) / len(recent_metrics),
            'response_time': sum(m.response_time for m in recent_metrics) / len(recent_metrics),
            'ui_updates_per_second': sum(m.ui_updates_per_second for m in recent_metrics) / len(recent_metrics),
            'active_threads': sum(m.active_threads for m in recent_metrics) / len(recent_metrics)
        }
        
    def get_peak_metrics(self, minutes: int = 30) -> Dict[str, float]:
        """Get peak metrics over the specified time period."""
        if not self.metrics_history:
            return {}
            
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return {}
            
        return {
            'peak_cpu_percent': max(m.cpu_percent for m in recent_metrics),
            'peak_memory_usage': max(m.memory_usage for m in recent_metrics),
            'peak_memory_percent': max(m.memory_percent for m in recent_metrics),
            'peak_response_time': max(m.response_time for m in recent_metrics),
            'peak_ui_updates_per_second': max(m.ui_updates_per_second for m in recent_metrics),
            'peak_active_threads': max(m.active_threads for m in recent_metrics)
        }
        
    def export_metrics(self, file_path: str, hours: int = 1) -> bool:
        """Export metrics to JSON file."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            export_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
            
            data = {
                'export_time': datetime.now().isoformat(),
                'time_range_hours': hours,
                'total_samples': len(export_metrics),
                'metrics': [m.to_dict() for m in export_metrics]
            }
            
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            self.logger.info(f"Performance metrics exported to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting metrics: {e}")
            return False
            
    def get_memory_usage_trend(self, minutes: int = 10) -> List[float]:
        """Get memory usage trend over time."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
        return [m.memory_usage for m in recent_metrics]
        
    def get_cpu_usage_trend(self, minutes: int = 10) -> List[float]:
        """Get CPU usage trend over time."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
        return [m.cpu_percent for m in recent_metrics]
        
    def get_response_time_trend(self, minutes: int = 10) -> List[float]:
        """Get response time trend over time."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
        return [m.response_time for m in recent_metrics]
        
    def is_performance_degraded(self) -> bool:
        """Check if performance is currently degraded."""
        current = self.get_current_metrics()
        if not current:
            return False
            
        return (current.cpu_percent > self.cpu_threshold or
                current.memory_usage > self.memory_threshold or
                current.response_time > self.response_time_threshold)
                
    def get_performance_summary(self) -> Dict[str, any]:
        """Get a comprehensive performance summary."""
        current = self.get_current_metrics()
        average_5min = self.get_average_metrics(5)
        peak_30min = self.get_peak_metrics(30)
        
        return {
            'current': current.to_dict() if current else None,
            'average_5min': average_5min,
            'peak_30min': peak_30min,
            'is_degraded': self.is_performance_degraded(),
            'total_samples': len(self.metrics_history),
            'monitoring_duration': (datetime.now() - self.metrics_history[0].timestamp).total_seconds() / 60 if self.metrics_history else 0
        }
        
    def cleanup(self):
        """Clean up resources."""
        self.stop_monitoring()
        self.metrics_history.clear()
        self.response_times.clear()
        
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()


class ResponseTimeTracker:
    """Utility class to track response times."""
    
    def __init__(self, performance_monitor: PerformanceMonitor):
        self.monitor = performance_monitor
        self.start_time = None
        
    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End timing and record response time."""
        if self.start_time:
            response_time = (time.time() - self.start_time) * 1000  # Convert to milliseconds
            self.monitor.record_response_time(response_time)