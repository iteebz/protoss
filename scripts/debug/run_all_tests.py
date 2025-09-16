#!/usr/bin/env python3
"""
PROTOSS DEBUG TEST SUITE

Runs all debug tests in sequence, reports results, identifies bugs.
AUTONOMOUS CYCLE: test → identify → report → repeat.
"""

import asyncio
import subprocess
import sys
import os
from pathlib import Path

# Add protoss src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..', 'src'))


async def run_test_script(script_name: str) -> dict:
    """Run a single debug test script and capture results."""
    script_path = Path(__file__).parent / script_name
    
    print(f"\n{'='*60}")
    print(f"🚀 RUNNING: {script_name}")
    print(f"{'='*60}")
    
    try:
        # Run the test script
        process = await asyncio.create_subprocess_exec(
            sys.executable, str(script_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        result = {
            'script': script_name,
            'return_code': process.returncode,
            'stdout': stdout.decode('utf-8', errors='replace'),
            'stderr': stderr.decode('utf-8', errors='replace'),
            'success': process.returncode == 0,
            'duration': 'unknown'  # Could add timing if needed
        }
        
        # Print real-time output
        if result['stdout']:
            print(result['stdout'])
        
        if result['stderr']:
            print("STDERR:", result['stderr'])
            
        if result['success']:
            print(f"✅ {script_name} PASSED")
        else:
            print(f"❌ {script_name} FAILED (exit code: {process.returncode})")
            
        return result
        
    except Exception as e:
        print(f"❌ Failed to run {script_name}: {e}")
        return {
            'script': script_name,
            'return_code': -1,
            'stdout': '',
            'stderr': str(e),
            'success': False,
            'duration': 'unknown'
        }


def analyze_test_results(results: list) -> dict:
    """Analyze test results and identify common failure patterns."""
    analysis = {
        'total_tests': len(results),
        'passed': sum(1 for r in results if r['success']),
        'failed': sum(1 for r in results if not r['success']),
        'failure_patterns': [],
        'bug_suspects': [],
        'recommendations': []
    }
    
    # Analyze failure patterns
    for result in results:
        if not result['success']:
            output = result['stdout'] + result['stderr']
            
            # Common failure pattern detection
            if 'ConnectionRefusedError' in output:
                analysis['failure_patterns'].append('Connection failures - Pylon grid issues')
                analysis['bug_suspects'].append('WebSocket infrastructure')
                
            if 'AttributeError' in output:
                analysis['failure_patterns'].append('Missing methods/attributes')
                analysis['bug_suspects'].append('Unit interface mismatches')
                
            if 'TimeoutError' in output or 'timeout' in output.lower():
                analysis['failure_patterns'].append('Timeouts - Slow LLM responses')
                analysis['bug_suspects'].append('Agent response handling')
                
            if 'ModuleNotFoundError' in output or 'ImportError' in output:
                analysis['failure_patterns'].append('Import errors')
                analysis['bug_suspects'].append('Python path or dependency issues')
                
            if 'async' in output and 'generator' in output:
                analysis['failure_patterns'].append('Async generator issues')
                analysis['bug_suspects'].append('Cogency integration problems')
    
    # Generate recommendations
    if analysis['failed'] == 0:
        analysis['recommendations'].append('🎉 All tests passed! Coordination architecture is stable.')
    else:
        analysis['recommendations'].append(f'🔧 {analysis["failed"]} tests failed - debug required')
        
        if 'WebSocket infrastructure' in analysis['bug_suspects']:
            analysis['recommendations'].append('🔍 Check Pylon WebSocket server startup and port conflicts')
            
        if 'Unit interface mismatches' in analysis['bug_suspects']:
            analysis['recommendations'].append('🔍 Verify Gateway.spawn() and unit method signatures')
            
        if 'Agent response handling' in analysis['bug_suspects']:
            analysis['recommendations'].append('🔍 Check async generator cleanup and timeout handling')
            
        if 'Cogency integration problems' in analysis['bug_suspects']:
            analysis['recommendations'].append('🔍 Verify Cogency Agent API compatibility')
    
    return analysis


async def main():
    """Run complete debug test suite."""
    print("🏰⚔️ PROTOSS DEBUG TEST SUITE - AUTONOMOUS BUG HUNTING")
    print("=" * 70)
    
    # Define test execution order (infrastructure → units → integration)
    test_scripts = [
        'test_khala_network.py',           # Infrastructure first
        'test_carrier_conclave.py',        # Core coordination
        'test_squad_coordination.py',      # Multi-agent dynamics
        'test_archon_synthesis.py',        # Knowledge systems
        'test_full_symphony.py'            # End-to-end integration
    ]
    
    results = []
    
    print(f"🚀 Running {len(test_scripts)} debug tests in sequence...")
    
    # Run each test
    for script in test_scripts:
        result = await run_test_script(script)
        results.append(result)
        
        # Small delay between tests to avoid port conflicts
        await asyncio.sleep(2)
    
    # Analyze results
    print(f"\n{'='*70}")
    print("📊 TEST SUITE ANALYSIS")
    print(f"{'='*70}")
    
    analysis = analyze_test_results(results)
    
    print(f"📋 SUMMARY:")
    print(f"   Total Tests: {analysis['total_tests']}")
    print(f"   ✅ Passed: {analysis['passed']}")
    print(f"   ❌ Failed: {analysis['failed']}")
    print(f"   Success Rate: {analysis['passed']/analysis['total_tests']*100:.1f}%")
    
    if analysis['failure_patterns']:
        print(f"\n🔍 FAILURE PATTERNS DETECTED:")
        for pattern in set(analysis['failure_patterns']):
            print(f"   - {pattern}")
    
    if analysis['bug_suspects']:
        print(f"\n🐛 BUG SUSPECTS:")
        for suspect in set(analysis['bug_suspects']):
            print(f"   - {suspect}")
    
    print(f"\n💡 RECOMMENDATIONS:")
    for rec in analysis['recommendations']:
        print(f"   {rec}")
    
    # Detailed failure analysis
    failed_tests = [r for r in results if not r['success']]
    if failed_tests:
        print(f"\n❌ FAILED TEST DETAILS:")
        for fail in failed_tests:
            print(f"\n   📋 {fail['script']}:")
            print(f"      Exit Code: {fail['return_code']}")
            if fail['stderr']:
                error_preview = fail['stderr'][:200].replace('\n', ' ')
                print(f"      Error: {error_preview}...")
    
    print(f"\n🏰 DEBUG SUITE COMPLETE")
    
    if analysis['failed'] == 0:
        print("🎉 CATHEDRAL COORDINATION ARCHITECTURE IS STABLE")
        return 0
    else:
        print(f"🔧 {analysis['failed']} BUGS DETECTED - AUTONOMOUS FIXING CYCLE REQUIRED")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)