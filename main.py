from flask import Flask, request, jsonify
import os
import google.generativeai as genai
import json
import time

app = Flask(__name__)

# Initialize Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# CONFIGURATION: Ensure this matches what we found in your list
CURRENT_MODEL = "gemini-2.5-flash"

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "online",
        "system": "Autopilot Manager",
        "version": "2.0",
        "model": CURRENT_MODEL
    })

@app.route("/check-models", methods=["GET"])
def check_models():
    try:
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                name = m.name.replace("models/", "")
                available_models.append(name)
        return jsonify({"success": True, "available_models": available_models})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/autopilot/execute", methods=["POST"])
def execute():
    """Simple one-shot prompt (Legacy)"""
    try:
        prompt = request.json.get("prompt")
        model = genai.GenerativeModel(CURRENT_MODEL)
        response = model.generate_content(prompt)
        return jsonify({"success": True, "result": response.text})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/autopilot/autonomous", methods=["POST"])
def autonomous():
    """
    THE MANAGER: Receives a GOAL, plans it, executes steps.
    """
    try:
        goal = request.json.get("goal")
        if not goal:
            return jsonify({"error": "Missing goal"}), 400

        # PHASE 1: PLANNING
        planner_model = genai.GenerativeModel(CURRENT_MODEL)
        planning_prompt = f"""
        You are an AI Manager. GOAL: {goal}
        Create a plan with 2 to 4 steps. Return ONLY valid JSON.
        JSON Format:
        {{
            "plan": [
                {{"step_name": "Step 1 Title", "prompt": "Instruction for AI..."}},
                {{"step_name": "Step 2 Title", "prompt": "Instruction..."}}
            ]
        }}
        """
        plan_response = planner_model.generate_content(planning_prompt)
        clean_json = plan_response.text.replace("```json", "").replace("```", "").strip()
        
        try:
            plan_data = json.loads(clean_json)
        except:
            # Fallback if AI messes up JSON
            return jsonify({"success": False, "error": "AI Plan Failed", "raw": clean_json})
        
        steps = plan_data.get("plan", [])
        
        # PHASE 2: EXECUTION
        results = []
        context = f"ORIGINAL GOAL: {goal}\n"
        worker_model = genai.GenerativeModel(CURRENT_MODEL)

        for i, step in enumerate(steps):
            if i > 0: time.sleep(2) # Safety for Free Tier
            
            step_prompt = step.get("prompt")
            full_prompt = f"CONTEXT:\n{context}\n\nTASK: {step_prompt}"
            
            response = worker_model.generate_content(full_prompt)
            result_text = response.text
            
            results.append(f"=== {step.get('step_name').upper()} ===\n{result_text}\n")
            context += f"\n[Finished Step {i+1}]\n{result_text}\n"

        # PHASE 3: REPORT
        final_report = "\n".join(results)

        return jsonify({
            "success": True,
            "goal": goal,
            "report": final_report
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
