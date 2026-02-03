"""
Example: Running StackOne Benchmarks
====================================

This example demonstrates how to run a pre-built benchmark (HRIS)
to evaluate an agent's performance on StackOne tasks.
"""

from superoptix.benchmarks.stackone import HRISBenchmark

def run_benchmark_demo():
    print("📊 Starting StackOne HRIS Benchmark...")
    
    benchmark = HRISBenchmark()
    dataset = benchmark.get_dataset()
    
    print(f"Loaded benchmark '{benchmark.name}' with {len(dataset)} test cases.\n")

    total_score = 0.0
    
    for case in dataset:
        print(f"📝 Test Case: '{case['input']}'")
        
        # In a real scenario, you would run your agent here:
        # tool_call = agent.run(case['input'])
        
        # Simulating a correct agent response for the first case
        if "12345" in case['input']:
            simulated_tool_call = {
                "name": "hris_get_employee",
                "args": {"id": "12345"}
            }
        else:
            # Simulating a mistake for other cases
            simulated_tool_call = {
                "name": "wrong_tool",
                "args": {}
            }
            
        score = benchmark.evaluate_tool_call(
            tool_name=simulated_tool_call["name"],
            tool_args=simulated_tool_call["args"],
            expected=case
        )
        
        total_score += score
        status = "✅ PASS" if score == 1.0 else "❌ FAIL"
        print(f"   Agent Action: {simulated_tool_call['name']}({simulated_tool_call['args']})")
        print(f"   Result: {status} (Score: {score})\n")

    avg_score = total_score / len(dataset)
    print(f"🏁 Benchmark Complete. Average Score: {avg_score:.2f}")

if __name__ == "__main__":
    run_benchmark_demo()
