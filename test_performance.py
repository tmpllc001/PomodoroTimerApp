#!/usr/bin/env python3
"""
パフォーマンステスト
"""
import sys
import time
from pathlib import Path

# プロジェクトのルートディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.performance_monitor import PerformanceMonitor, ResponseTimeTracker
from src.controllers.timer_controller import TimerController


def test_performance_monitor():
    """Test performance monitor."""
    print("=== Performance Monitor Test ===")
    
    monitor = PerformanceMonitor(sample_interval=0.1)
    
    # Start monitoring
    monitor.start_monitoring()
    print("Performance monitoring started")
    
    # Simulate some work
    timer_controller = TimerController()
    timer_controller.set_sound_enabled(False)
    
    # Record some UI updates
    for i in range(10):
        monitor.record_ui_update()
        time.sleep(0.01)
    
    # Record some response times
    for i in range(5):
        with ResponseTimeTracker(monitor):
            # Simulate some work
            timer_info = timer_controller.get_timer_info()
            time.sleep(0.001)
    
    # Let monitor collect some data
    time.sleep(1.0)
    
    # Get current metrics
    current = monitor.get_current_metrics()
    if current:
        print(f"Current CPU: {current.cpu_percent:.1f}%")
        print(f"Current Memory: {current.memory_usage:.1f} MB")
        print(f"Response Time: {current.response_time:.1f} ms")
        print(f"UI Updates/sec: {current.ui_updates_per_second:.1f}")
        print(f"Active Threads: {current.active_threads}")
    
    # Get averages
    avg_metrics = monitor.get_average_metrics(1)
    if avg_metrics:
        print(f"Average CPU (1 min): {avg_metrics.get('cpu_percent', 0):.1f}%")
        print(f"Average Memory (1 min): {avg_metrics.get('memory_usage', 0):.1f} MB")
    
    # Test export
    export_success = monitor.export_metrics("test_metrics.json", hours=1)
    print(f"Export successful: {export_success}")
    
    # Check performance summary
    summary = monitor.get_performance_summary()
    print(f"Performance degraded: {summary['is_degraded']}")
    print(f"Total samples: {summary['total_samples']}")
    
    # Cleanup
    monitor.stop_monitoring()
    timer_controller.cleanup()
    
    print("✅ Performance Monitor Test completed")


def test_memory_usage():
    """Test memory usage over time."""
    print("\n=== Memory Usage Test ===")
    
    monitor = PerformanceMonitor(sample_interval=0.1)
    monitor.start_monitoring()
    
    # Create multiple timer controllers to test memory usage
    controllers = []
    
    for i in range(5):
        controller = TimerController()
        controller.set_sound_enabled(False)
        controllers.append(controller)
        print(f"Created controller {i+1}")
        time.sleep(0.2)
    
    # Let monitor collect data
    time.sleep(1.0)
    
    # Get memory trend
    memory_trend = monitor.get_memory_usage_trend(1)
    if len(memory_trend) > 1:
        initial_memory = memory_trend[0]
        final_memory = memory_trend[-1]
        memory_increase = final_memory - initial_memory
        print(f"Memory usage increase: {memory_increase:.1f} MB")
        
        if memory_increase > 50:  # 50MB increase might indicate a memory leak
            print("⚠️  Potential memory issue detected")
        else:
            print("✅ Memory usage within acceptable range")
    
    # Cleanup controllers
    for controller in controllers:
        controller.cleanup()
    
    # Let monitor collect cleanup data
    time.sleep(0.5)
    
    # Check if memory was freed
    final_trend = monitor.get_memory_usage_trend(1)
    if final_trend:
        cleanup_memory = final_trend[-1]
        if len(memory_trend) > 0:
            memory_freed = memory_trend[-1] - cleanup_memory
            print(f"Memory freed after cleanup: {memory_freed:.1f} MB")
    
    monitor.stop_monitoring()
    print("✅ Memory Usage Test completed")


def test_cpu_performance():
    """Test CPU performance under load."""
    print("\n=== CPU Performance Test ===")
    
    monitor = PerformanceMonitor(sample_interval=0.1)
    monitor.start_monitoring()
    
    # Create load with timer operations
    controller = TimerController()
    controller.set_sound_enabled(False)
    
    print("Starting CPU load test...")
    start_time = time.time()
    
    # Perform many operations
    for i in range(1000):
        controller.start_timer()
        time.sleep(0.001)
        controller.pause_timer()
        time.sleep(0.001)
        controller.stop_timer()
        
        if i % 100 == 0:
            print(f"Completed {i} operations")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"Total time for 1000 operations: {total_time:.2f} seconds")
    print(f"Operations per second: {1000/total_time:.1f}")
    
    # Get CPU trend
    cpu_trend = monitor.get_cpu_usage_trend(1)
    if cpu_trend:
        avg_cpu = sum(cpu_trend) / len(cpu_trend)
        max_cpu = max(cpu_trend)
        print(f"Average CPU during test: {avg_cpu:.1f}%")
        print(f"Peak CPU during test: {max_cpu:.1f}%")
        
        if max_cpu > 80:
            print("⚠️  High CPU usage detected")
        else:
            print("✅ CPU usage within acceptable range")
    
    controller.cleanup()
    monitor.stop_monitoring()
    print("✅ CPU Performance Test completed")


def main():
    """Run all performance tests."""
    print("Performance Tests Starting...")
    
    try:
        test_performance_monitor()
        test_memory_usage()
        test_cpu_performance()
        
        print("\n🎉 All Performance Tests Completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Performance Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)