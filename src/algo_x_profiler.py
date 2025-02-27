import time
import logging
import functools

logger = logging.getLogger("algo_x_profiler")

# Dictionary to store performance metrics
performance_metrics = {
    "select_min_column_c": {"calls": 0, "time": 0, "overhead": 0},
    "select_min_column_py": {"calls": 0, "time": 0},
    "cover_columns_c": {"calls": 0, "time": 0, "overhead": 0},
    "cover_columns_py": {"calls": 0, "time": 0},
}

def profile_function(func_name):
    """Decorator to profile function execution time"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if func_name not in performance_metrics:
                performance_metrics[func_name] = {"calls": 0, "time": 0}
            
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            performance_metrics[func_name]["calls"] += 1
            performance_metrics[func_name]["time"] += execution_time
            
            return result
        return wrapper
    return decorator

def print_performance_report():
    """Print a summary of performance metrics"""
    logger.info("============= PERFORMANCE REPORT =============")
    for func_name, metrics in performance_metrics.items():
        if metrics["calls"] > 0:
            avg_time = metrics["time"] / metrics["calls"] * 1000  # ms
            logger.info(f"{func_name}: {metrics['calls']} calls, {metrics['time']:.4f}s total, {avg_time:.4f}ms avg")
            
            # Compare C vs Python implementations
            if func_name.endswith("_c") and func_name.replace("_c", "_py") in performance_metrics:
                py_metrics = performance_metrics[func_name.replace("_c", "_py")]
                if py_metrics["calls"] > 0:
                    py_avg = py_metrics["time"] / py_metrics["calls"] * 1000  # ms
                    speedup = py_avg / avg_time if avg_time > 0 else 0
                    logger.info(f"  → {speedup:.2f}x faster than Python version")
                    
                    # Report overhead percentage
                    if "overhead" in metrics and metrics["overhead"] > 0:
                        overhead_pct = (metrics["overhead"] / metrics["time"]) * 100
                        logger.info(f"  → {overhead_pct:.2f}% of time spent in data conversion")
    
    logger.info("=============================================")

def reset_performance_metrics():
    """Reset all performance metrics"""
    for func_metrics in performance_metrics.values():
        func_metrics.update({"calls": 0, "time": 0})
        if "overhead" in func_metrics:
            func_metrics["overhead"] = 0
