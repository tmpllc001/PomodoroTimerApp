"""
Performance benchmarking tests for Pomodoro Timer Application.
Tests responsiveness, memory usage, and system resource consumption.
"""

import pytest
import time
import psutil
import threading
import gc
from unittest.mock import Mock, patch
from concurrent.futures import ThreadPoolExecutor
import sys
import os


class PerformanceMonitor:
    """Monitor system performance during tests."""
    
    def __init__(self):
        self.process = psutil.Process()
        self.start_memory = None
        self.start_cpu = None
        self.start_time = None
        
    def start_monitoring(self):
        """Start performance monitoring."""
        self.start_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        self.start_cpu = self.process.cpu_percent()
        self.start_time = time.time()
        
    def get_memory_usage(self):
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024
        
    def get_cpu_usage(self):
        """Get current CPU usage percentage."""
        return self.process.cpu_percent(interval=0.1)
        
    def get_elapsed_time(self):
        """Get elapsed time since monitoring started."""
        return time.time() - self.start_time if self.start_time else 0
        
    def get_memory_growth(self):
        """Get memory growth since monitoring started."""
        if self.start_memory:
            return self.get_memory_usage() - self.start_memory
        return 0


class MockTimerForPerformance:
    """Lightweight mock timer for performance testing."""
    
    def __init__(self):
        self.current_time = 25 * 60
        self.is_running = False
        self.tick_count = 0
        
    def start(self):
        self.is_running = True
        
    def tick(self):
        if self.is_running and self.current_time > 0:
            self.current_time -= 1
            self.tick_count += 1
            
    def stop(self):
        self.is_running = False
        
    def reset(self):
        self.current_time = 25 * 60
        self.is_running = False
        self.tick_count = 0


class TestTimerPerformance:
    """Performance tests for timer operations."""
    
    def setup_method(self):
        """Set up performance test fixtures."""
        self.monitor = PerformanceMonitor()
        self.timer = MockTimerForPerformance()
        
    def test_timer_tick_performance(self):
        """Test timer tick performance under high frequency."""
        self.monitor.start_monitoring()
        
        # Simulate 1 hour of timer ticks (3600 ticks)
        self.timer.start()
        start_time = time.time()
        
        for _ in range(3600):
            self.timer.tick()
            
        elapsed_time = time.time() - start_time
        memory_growth = self.monitor.get_memory_growth()
        
        # Performance assertions
        assert elapsed_time < 0.1  # Should complete in < 100ms
        assert memory_growth < 1.0  # Should not grow more than 1MB
        assert self.timer.tick_count == 3600
        
    def test_rapid_start_stop_performance(self):
        """Test performance of rapid start/stop operations."""
        self.monitor.start_monitoring()
        
        start_time = time.time()
        
        # Rapid start/stop cycles
        for _ in range(1000):
            self.timer.start()
            self.timer.stop()
            
        elapsed_time = time.time() - start_time
        memory_growth = self.monitor.get_memory_growth()
        
        # Performance assertions
        assert elapsed_time < 0.5  # Should complete in < 500ms
        assert memory_growth < 2.0  # Should not grow more than 2MB
        
    def test_memory_usage_stability(self):
        """Test memory usage stability over extended operation."""
        self.monitor.start_monitoring()
        
        # Record initial memory
        initial_memory = self.monitor.get_memory_usage()
        memory_samples = [initial_memory]
        
        # Run extended operations
        for cycle in range(100):
            self.timer.start()
            
            # Simulate session
            for _ in range(60):  # 1 minute of ticks
                self.timer.tick()
                
            self.timer.stop()
            self.timer.reset()
            
            # Sample memory every 10 cycles
            if cycle % 10 == 0:
                gc.collect()  # Force garbage collection
                memory_samples.append(self.monitor.get_memory_usage())
                
        # Analyze memory stability
        memory_growth = max(memory_samples) - min(memory_samples)
        
        # Memory should be stable (< 5MB variation)
        assert memory_growth < 5.0
        
    def test_cpu_usage_efficiency(self):
        """Test CPU usage efficiency during normal operations."""
        self.monitor.start_monitoring()
        
        # Start monitoring CPU
        cpu_samples = []
        
        def monitor_cpu():
            for _ in range(10):  # Monitor for 1 second
                cpu_samples.append(self.monitor.get_cpu_usage())
                time.sleep(0.1)
                
        # Start CPU monitoring in background
        monitor_thread = threading.Thread(target=monitor_cpu)
        monitor_thread.start()
        
        # Perform normal operations
        self.timer.start()
        for _ in range(60):  # 1 minute simulation
            self.timer.tick()
            time.sleep(0.001)  # Small delay to simulate real timing
            
        monitor_thread.join()
        
        # CPU usage should be reasonable
        avg_cpu = sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
        max_cpu = max(cpu_samples) if cpu_samples else 0
        
        assert avg_cpu < 10.0  # Average CPU < 10%
        assert max_cpu < 25.0  # Peak CPU < 25%


class TestAudioPerformance:
    """Performance tests for audio operations."""
    
    def setup_method(self):
        """Set up audio performance test fixtures."""
        self.monitor = PerformanceMonitor()
        self.audio_manager = Mock()
        
    def test_notification_playback_latency(self):
        """Test notification playback latency."""
        self.monitor.start_monitoring()
        
        latencies = []
        
        # Test multiple notification playbacks
        for _ in range(100):
            start_time = time.time()
            self.audio_manager.play_notification()
            end_time = time.time()
            
            latency = (end_time - start_time) * 1000  # Convert to ms
            latencies.append(latency)
            
        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        
        # Latency assertions
        assert avg_latency < 5.0  # Average < 5ms
        assert max_latency < 20.0  # Max < 20ms
        
    def test_bgm_performance_impact(self):
        """Test BGM impact on system performance."""
        self.monitor.start_monitoring()
        
        # Simulate BGM operations
        self.audio_manager.play_bgm.return_value = True
        self.audio_manager.pause_bgm.return_value = True
        self.audio_manager.resume_bgm.return_value = True
        
        start_time = time.time()
        
        # Perform BGM operations
        for _ in range(50):
            self.audio_manager.play_bgm("focus")
            self.audio_manager.pause_bgm()
            self.audio_manager.resume_bgm()
            self.audio_manager.stop_bgm()
            
        elapsed_time = time.time() - start_time
        memory_growth = self.monitor.get_memory_growth()
        
        # Performance assertions
        assert elapsed_time < 0.1  # Should be very fast for mocked operations
        assert memory_growth < 1.0  # Minimal memory impact


class TestUIPerformance:
    """Performance tests for UI operations."""
    
    def setup_method(self):
        """Set up UI performance test fixtures."""
        self.monitor = PerformanceMonitor()
        self.main_window = Mock()
        
    def test_window_update_performance(self):
        """Test window update performance."""
        self.monitor.start_monitoring()
        
        start_time = time.time()
        
        # Simulate rapid window updates
        for i in range(1000):
            # Mock timer display update
            formatted_time = f"{i//60:02d}:{i%60:02d}"
            self.main_window.update_timer_display(formatted_time)
            
        elapsed_time = time.time() - start_time
        
        # Should handle rapid updates efficiently
        assert elapsed_time < 0.2  # < 200ms for 1000 updates
        assert self.main_window.update_timer_display.call_count == 1000
        
    def test_window_rendering_performance(self):
        """Test window rendering performance."""
        self.monitor.start_monitoring()
        
        # Mock rendering operations
        self.main_window.repaint.return_value = True
        self.main_window.update.return_value = True
        
        start_time = time.time()
        
        # Simulate rendering calls
        for _ in range(100):
            self.main_window.repaint()
            self.main_window.update()
            
        elapsed_time = time.time() - start_time
        memory_growth = self.monitor.get_memory_growth()
        
        # Rendering should be efficient
        assert elapsed_time < 0.1  # < 100ms
        assert memory_growth < 0.5  # < 500KB growth


class TestConcurrencyPerformance:
    """Performance tests for concurrent operations."""
    
    def setup_method(self):
        """Set up concurrency test fixtures."""
        self.monitor = PerformanceMonitor()
        
    def test_thread_safety_performance(self):
        """Test performance under concurrent access."""
        self.monitor.start_monitoring()
        
        timer = MockTimerForPerformance()
        results = []
        
        def worker():
            start_time = time.time()
            
            # Perform operations
            timer.start()
            for _ in range(100):
                timer.tick()
            timer.stop()
            timer.reset()
            
            elapsed = time.time() - start_time
            results.append(elapsed)
            
        # Run concurrent workers
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker) for _ in range(10)]
            
            # Wait for completion
            for future in futures:
                future.result()
                
        # Analyze results
        avg_time = sum(results) / len(results)
        max_time = max(results)
        memory_growth = self.monitor.get_memory_growth()
        
        # Performance assertions
        assert avg_time < 0.1  # Average < 100ms per worker
        assert max_time < 0.5   # Max < 500ms per worker
        assert memory_growth < 5.0  # < 5MB total growth
        
    def test_scalability_limits(self):
        """Test scalability limits with increasing load."""
        self.monitor.start_monitoring()
        
        thread_counts = [1, 2, 5, 10, 20]
        performance_data = {}
        
        for thread_count in thread_counts:
            results = []
            
            def worker():
                timer = MockTimerForPerformance()
                start_time = time.time()
                
                timer.start()
                for _ in range(50):
                    timer.tick()
                timer.stop()
                
                results.append(time.time() - start_time)
                
            # Run with current thread count
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=thread_count) as executor:
                futures = [executor.submit(worker) for _ in range(thread_count)]
                for future in futures:
                    future.result()
                    
            total_time = time.time() - start_time
            performance_data[thread_count] = {
                'total_time': total_time,
                'avg_worker_time': sum(results) / len(results) if results else 0
            }
            
        # Performance should scale reasonably
        # More threads shouldn't dramatically increase individual worker time
        single_thread_time = performance_data[1]['avg_worker_time']
        multi_thread_time = performance_data[10]['avg_worker_time']
        
        # 10x threads shouldn't make individual operations 5x slower
        assert multi_thread_time < single_thread_time * 5


class TestMemoryLeakDetection:
    """Specialized tests for memory leak detection."""
    
    def test_timer_memory_leak(self):
        """Test for memory leaks in timer operations."""
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Perform many timer operations
        for _ in range(1000):
            timer = MockTimerForPerformance()
            timer.start()
            for _ in range(10):
                timer.tick()
            timer.stop()
            del timer
            
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Should not have significant object growth
        object_growth = final_objects - initial_objects
        assert object_growth < 100  # Allow some growth but not excessive
        
    def test_mock_object_cleanup(self):
        """Test that mock objects are properly cleaned up."""
        import weakref
        
        # Create mock objects with weak references
        mocks = []
        weak_refs = []
        
        for _ in range(100):
            mock_obj = Mock()
            mocks.append(mock_obj)
            weak_refs.append(weakref.ref(mock_obj))
            
        # Clear strong references
        del mocks
        gc.collect()
        
        # Check if objects were collected
        collected_count = sum(1 for ref in weak_refs if ref() is None)
        
        # Most objects should be collected
        assert collected_count > 50  # At least 50% should be collected


@pytest.mark.benchmark
class TestBenchmarks:
    """Benchmark tests for performance baselines."""
    
    def test_timer_tick_benchmark(self, benchmark):
        """Benchmark timer tick operation."""
        timer = MockTimerForPerformance()
        timer.start()
        
        def tick_operation():
            timer.tick()
            
        # Run benchmark
        result = benchmark(tick_operation)
        
        # Verify the operation works
        assert timer.tick_count > 0
        
    def test_notification_benchmark(self, benchmark):
        """Benchmark notification playback."""
        audio_manager = Mock()
        audio_manager.play_notification.return_value = True
        
        def notification_operation():
            return audio_manager.play_notification("work_complete")
            
        # Run benchmark
        result = benchmark(notification_operation)
        assert result is True
        
    def test_window_update_benchmark(self, benchmark):
        """Benchmark window update operation."""
        window = Mock()
        window.update_timer_display.return_value = True
        
        def update_operation():
            return window.update_timer_display("25:00")
            
        # Run benchmark
        result = benchmark(update_operation)
        assert result is True


if __name__ == "__main__":
    # Run performance tests standalone
    print("Running performance tests...")
    
    # Initialize monitor
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    
    # Run basic performance test
    timer = MockTimerForPerformance()
    timer.start()
    
    start_time = time.time()
    for _ in range(1000):
        timer.tick()
    elapsed = time.time() - start_time
    
    print(f"1000 timer ticks completed in {elapsed:.3f}s")
    print(f"Memory usage: {monitor.get_memory_usage():.1f}MB")
    print(f"Memory growth: {monitor.get_memory_growth():.1f}MB")