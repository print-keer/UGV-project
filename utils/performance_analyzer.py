"""
Performance Analyzer
Analyzes and compares pathfinding algorithm performance
"""

import numpy as np
import json
from datetime import datetime

class PerformanceAnalyzer:
    def __init__(self):
        self.results = {}
        
    def record_result(self, algorithm, environment, execution_time, metrics):
        """Record algorithm performance result"""
        if algorithm not in self.results:
            self.results[algorithm] = {}
        
        if environment not in self.results[algorithm]:
            self.results[algorithm][environment] = []
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'execution_time': execution_time,
            'metrics': metrics
        }
        
        self.results[algorithm][environment].append(result)
    
    def get_algorithm_stats(self, algorithm, environment):
        """Get statistical summary for algorithm in environment"""
        if algorithm not in self.results or environment not in self.results[algorithm]:
            return None
        
        runs = self.results[algorithm][environment]
        
        if not runs:
            return None
        
        # Extract metrics
        execution_times = [run['execution_time'] for run in runs]
        path_lengths = [run['metrics'].get('path_length', float('inf')) for run in runs]
        success_rates = [run['metrics'].get('success_rate', 0) for run in runs]
        
        stats = {
            'num_runs': len(runs),
            'avg_execution_time': np.mean(execution_times),
            'std_execution_time': np.std(execution_times),
            'avg_path_length': np.mean([pl for pl in path_lengths if pl != float('inf')]),
            'success_rate': np.mean(success_rates),
            'min_execution_time': np.min(execution_times),
            'max_execution_time': np.max(execution_times)
        }
        
        return stats
    
    def compare_algorithms(self, environment):
        """Compare all algorithms for a specific environment"""
        comparison = {}
        
        for algorithm in self.results:
            stats = self.get_algorithm_stats(algorithm, environment)
            if stats:
                comparison[algorithm] = stats
        
        return comparison
    
    def generate_comprehensive_report(self, results):
        """Generate comprehensive performance report"""
        report = {}
        
        # Process each environment
        for env_name, env_results in results.items():
            report[env_name] = {}
            
            for alg_name, result in env_results.items():
                if result['success']:
                    report[env_name][alg_name] = {
                        'execution_time': result['execution_time'],
                        'path_length': result['metrics'].get('path_length', float('inf')),
                        'success_rate': result['metrics'].get('success_rate', 0),
                        'nodes_explored': result['metrics'].get('nodes_explored', 0),
                        'smoothness': result['metrics'].get('smoothness', float('inf')),
                        'success': True
                    }
                else:
                    report[env_name][alg_name] = {
                        'execution_time': float('inf'),
                        'path_length': float('inf'),
                        'success_rate': 0,
                        'nodes_explored': result['metrics'].get('nodes_explored', 0),
                        'smoothness': float('inf'),
                        'success': False
                    }
        
        # Generate summary statistics
        summary = self.generate_summary_stats(report)
        report['summary'] = summary
        
        return report
    
    def generate_summary_stats(self, report):
        """Generate overall summary statistics"""
        summary = {
            'total_environments': len([k for k in report.keys() if k != 'summary']),
            'algorithms_tested': set(),
            'fastest_algorithm': None,
            'shortest_path_algorithm': None,
            'most_reliable_algorithm': None,
            'environment_difficulty_ranking': []
        }
        
        # Collect all algorithms
        for env_results in report.values():
            if isinstance(env_results, dict):
                summary['algorithms_tested'].update(env_results.keys())
        
        summary['algorithms_tested'] = list(summary['algorithms_tested'])
        
        # Find best performers
        avg_times = {}
        avg_path_lengths = {}
        success_rates = {}
        
        for alg in summary['algorithms_tested']:
            times = []
            lengths = []
            successes = []
            
            for env_name, env_results in report.items():
                if env_name != 'summary' and alg in env_results:
                    result = env_results[alg]
                    if result['success']:
                        times.append(result['execution_time'])
                        lengths.append(result['path_length'])
                        successes.append(result['success_rate'])
                    else:
                        successes.append(0)
            
            if times:
                avg_times[alg] = np.mean(times)
            if lengths:
                avg_path_lengths[alg] = np.mean(lengths)
            if successes:
                success_rates[alg] = np.mean(successes)
        
        # Determine best algorithms
        if avg_times:
            summary['fastest_algorithm'] = min(avg_times, key=avg_times.get)
        
        if avg_path_lengths:
            summary['shortest_path_algorithm'] = min(avg_path_lengths, key=avg_path_lengths.get)
        
        if success_rates:
            summary['most_reliable_algorithm'] = max(success_rates, key=success_rates.get)
        
        # Rank environment difficulty
        env_difficulties = {}
        for env_name, env_results in report.items():
            if env_name != 'summary':
                success_count = sum(1 for result in env_results.values() if result['success'])
                total_algorithms = len(env_results)
                difficulty_score = 1 - (success_count / total_algorithms) if total_algorithms > 0 else 1
                env_difficulties[env_name] = difficulty_score
        
        summary['environment_difficulty_ranking'] = sorted(
            env_difficulties.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return summary
    
    def export_results(self, filename):
        """Export results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
    
    def import_results(self, filename):
        """Import results from JSON file"""
        with open(filename, 'r') as f:
            self.results = json.load(f)
