from flask import Flask, request, jsonify
import os
import google.generativeai as genai

app = Flask(__name__)

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "system": "Autopilot System v1.0 (Google Gemini)"
    })

@app.route("/autopilot/execute", methods=["POST"])
def execute_task():
    """Execute a single autopilot task"""
    try:
        data = request.json
        prompt = data.get("prompt")
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        response = model.generate_content(prompt)
        
        return jsonify({
            "status": "completed",
            "result": response.text
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
            prompt = step.get("prompt")
            context = step.get("context", "")
            
            # Add context from previous steps
            if context:
                prompt = f"Previous context: {context}\n\nNew task: {prompt}"
            
            response = model.generate_content(prompt)
            results.append(response.text)
            
            # Use result as context for next step
            if len(results) > 0:
                step["context"] = results[-1]
        
        return jsonify({
            "status": "workflow_completed",
            "steps_executed": len(results),
            "results": results
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
