from flask import Flask, request, jsonify
import os
import google.generativeai as genai

app = Flask(__name__)

# Initialize Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# --- CONFIGURATION START ---
# We use "gemini-1.5-flash" as the replacement for "gemini-pro".
# This solves the 404 Model Not Found error.
CURRENT_MODEL = "gemini-1.5-flash"
# --- CONFIGURATION END ---

@app.route("/", methods=["GET"])
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "online",
        "system": "Autopilot AI",
        "version": "1.1",
        "model": CURRENT_MODEL
    })

@app.route("/autopilot/execute", methods=["POST"])
def execute():
    """Single task execution"""
    try:
        prompt = request.json.get("prompt")
        if not prompt:
            return jsonify({"error": "Missing prompt"}), 400
        
        # Use the updated model variable
        model = genai.GenerativeModel(CURRENT_MODEL)
        response = model.generate_content(prompt)
        
        return jsonify({
            "success": True,
            "result": response.text
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/autopilot/workflow", methods=["POST"])
def workflow():
    """Multi-step workflow execution"""
    try:
        steps = request.json.get("steps", [])
        if not steps:
            return jsonify({"error": "No steps provided"}), 400
        
        # Use the updated model variable
        model = genai.GenerativeModel(CURRENT_MODEL)
        results = []
        context = ""
        
        for step in steps:
            prompt = step.get("prompt", "")
            if context:
                prompt = f"Context: {context}\n\nTask: {prompt}"
            
            response = model.generate_content(prompt)
            result = response.text
            results.append(result)
            context = result[:500]  # Use first 500 chars as context
        
        return jsonify({
            "success": True,
            "steps_completed": len(results),
            "results": results
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
