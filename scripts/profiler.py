"""
Performance profiling and optimization utilities.
"""
import time
import psutil
import json
from typing import Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    """Analyze and profile API performance."""
    
    def __init__(self):
        """Initialize analyzer."""
        self.metrics: Dict[str, List[float]] = {}
        self.start_time = time.time()
    
    def record_latency(self, operation: str, latency: float):
        """Record operation latency."""
        if operation not in self.metrics:
            self.metrics[operation] = []
        self.metrics[operation].append(latency)
    
    def get_stats(self, operation: str) -> Dict[str, Any]:
        """Get statistics for an operation."""
        if operation not in self.metrics or not self.metrics[operation]:
            return {}
        
        times = self.metrics[operation]
        return {
            "operation": operation,
            "count": len(times),
            "min": min(times),
            "max": max(times),
            "avg": sum(times) / len(times),
            "p50": sorted(times)[len(times) // 2],
            "p95": sorted(times)[int(len(times) * 0.95)],
            "p99": sorted(times)[int(len(times) * 0.99)]
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all operations."""
        return {
            operation: self.get_stats(operation)
            for operation in self.metrics
        }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system resource usage."""
        process = psutil.Process()
        
        return {
            "cpu_percent": process.cpu_percent(interval=0.1),
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "memory_percent": process.memory_percent(),
            "num_threads": process.num_threads(),
            "uptime_seconds": time.time() - self.start_time
        }
    
    def get_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "system": self.get_system_stats(),
            "operations": self.get_all_stats()
        }
    
    def save_report(self, filepath: str):
        """Save performance report to file."""
        report = self.get_report()
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Performance report saved to {filepath}")

class BenchmarkRunner:
    """Run benchmarks on API endpoints."""
    
    @staticmethod
    async def benchmark_endpoint(client, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """
        Run benchmark on an endpoint.
        
        Args:
            client: HTTP client
            method: HTTP method
            url: Endpoint URL
            **kwargs: Additional parameters
            
        Returns:
            Benchmark results
        """
        times = []
        errors = 0
        
        for _ in range(10):
            start = time.time()
            try:
                if method == "GET":
                    await client.get(url)
                elif method == "POST":
                    await client.post(url, **kwargs)
                duration = time.time() - start
                times.append(duration)
            except Exception as e:
                errors += 1
                logger.error(f"Benchmark error: {e}")
        
        return {
            "endpoint": url,
            "method": method,
            "requests": len(times),
            "errors": errors,
            "min": min(times) if times else 0,
            "max": max(times) if times else 0,
            "avg": sum(times) / len(times) if times else 0,
            "throughput": len(times) / sum(times) if sum(times) > 0 else 0
        }

class MemoryProfiler:
    """Profile memory usage."""
    
    def __init__(self):
        """Initialize profiler."""
        self.snapshots: List[Dict[str, Any]] = []
    
    def take_snapshot(self, name: str = ""):
        """Take memory snapshot."""
        process = psutil.Process()
        
        self.snapshots.append({
            "name": name,
            "timestamp": time.time(),
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "memory_percent": process.memory_percent()
        })
    
    def get_diff(self, start_idx: int = 0, end_idx: int = -1) -> Dict[str, Any]:
        """Get memory difference between snapshots."""
        if len(self.snapshots) < 2:
            return {}
        
        start = self.snapshots[start_idx]
        end = self.snapshots[end_idx]
        
        return {
            "start": start["name"],
            "end": end["name"],
            "memory_delta_mb": end["memory_mb"] - start["memory_mb"],
            "memory_percent_delta": end["memory_percent"] - start["memory_percent"]
        }
