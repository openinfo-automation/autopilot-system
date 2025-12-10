# main.py - Event-driven approach
from flask import Flask, request, jsonify
import os
from openai import OpenAI
from anthropic import Anthropic
import json

app = Flask(__name__)

openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
anthropic_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Store task queue in memory (resets on spin-down)
task_queue = []

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "system": "Autopilot System v1.0",
        "tasks_queued": len(task_queue)
    })

@app.route("/autopilot/execute", methods=["POST"])
def execute_task():
    """Execute a single autopilot task"""
    try:
        data = request.json
        task_type = data.get("task_type")  # e.g., "analyze", "generate", "research"
        prompt = data.get("prompt")
        
        # Route to appropriate AI based on task
        if task_type == "creative":
            result = run_claude_task(prompt)
        elif task_type == "analytical":
            result = run_openai_task(prompt)
        else:
            # Use both and compare
            result = run_dual_task(prompt)
        
        return jsonify({
            "status": "completed",
            "task_type": task_type,
            "result": result
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/autopilot/workflow", methods=["POST"])
def run_workflow():
    """Execute a multi-step autopilot workflow"""
    try:
        data = request.json
        workflow_steps = data.get("steps", [])
        results = []
        
        for step in workflow_steps:
            # Execute each step sequentially
            step_result = execute_workflow_step(step)
            results.append(step_result)
            
            # Use previous results as context for next step
            if len(results) > 1:
                step["context"] = results[-2]
        
        return jsonify({
            "status": "workflow_completed",
            "steps_executed": len(results),
            "results": results
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_claude_task(prompt):
    """Execute task using Claude"""
    response = anthropic_client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

def run_openai_task(prompt):
    """Execute task using OpenAI"""
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000
    )
    return response.choices[0].message.content

def run_dual_task(prompt):
    """Get responses from both AIs"""
    return {
        "claude": run_claude_task(prompt),
        "openai": run_openai_task(prompt)
    }

def execute_workflow_step(step):
    """Execute a single workflow step"""
    task_type = step.get("type")
    prompt = step.get("prompt")
    context = step.get("context", "")
    
    # Add context from previous steps
    if context:
        prompt = f"Previous context: {context}\n\nNew task: {prompt}"
    
    if task_type == "claude":
        return run_claude_task(prompt)
    elif task_type == "openai":
        return run_openai_task(prompt)
    else:
        return run_dual_task(prompt)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
