import google.generativeai as genai
import ast
import json
import re
from PIL import Image
from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)


def analyze_image(img: Image, dict_of_vars: dict):
    # Use the updated Gemini 2.0 model name
    model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

    dict_of_vars_str = json.dumps(dict_of_vars, ensure_ascii=False)

    prompt = (
        f"You have been given an image with some mathematical expressions, equations, or graphical problems, and you need to solve them. "
        f"Note: Use the PEMDAS rule for solving mathematical expressions. PEMDAS stands for the Priority Order: Parentheses, Exponents, Multiplication and Division (from left to right), Addition and Subtraction (from left to right). "
        f"For example: "
        f"Q. 2 + 3 * 4 "
        f"(3 * 4) => 12, 2 + 12 = 14. "
        f"Q. 2 + 3 + 5 * 4 - 8 / 2 "
        f"5 * 4 => 20, 8 / 2 => 4, 2 + 3 => 5, 5 + 20 => 25, 25 - 4 => 21. "
        f"YOU CAN HAVE FIVE TYPES OF EQUATIONS/EXPRESSIONS IN THIS IMAGE, AND ONLY ONE CASE SHALL APPLY EVERY TIME: "
        f"Following are the cases: "
        f"1. Simple mathematical expressions like 2 + 2, 3 * 4, 5 / 6, 7 - 8, etc.: In this case, solve and return the answer in the format of a LIST OF ONE DICT [{{'expr': given expression, 'result': calculated answer}}]. "
        f"2. Set of Equations like x^2 + 2x + 1 = 0, 3y + 4x = 0, 5x^2 + 6y + 7 = 12, etc.: In this case, solve for the given variable, and the format should be a COMMA SEPARATED LIST OF DICTS, with dict 1 as {{'expr': 'x', 'result': 2, 'assign': True}} and dict 2 as {{'expr': 'y', 'result': 5, 'assign': True}}. Include as many dicts as there are variables. "
        f"3. Assigning values to variables like x = 4, y = 5, z = 6, etc.: In this case, assign values to variables and return another key in the dict called {{'assign': True}}, keeping the variable as 'expr' and the value as 'result'. RETURN AS A LIST OF DICTS. "
        f"4. Analyzing Graphical Math problems, such as cars colliding, trigonometric drawings, Pythagorean theorem visuals, etc. PAY CLOSE ATTENTION TO DIFFERENT COLORS. Return in LIST OF ONE DICT format. "
        f"5. Detecting Abstract Concepts like love, war, discovery, or quotes represented as drawings. Use the same format: {{'expr': explanation, 'result': abstract concept}}. "
        f"Analyze the equation or expression in this image and return the answer according to the rules. "
        f"Use escape characters properly like \\f → \\\\f, \\n → \\\\n. "
        f"If a variable in the expression is in this dictionary, use its value: {dict_of_vars_str}. "
        f"IMPORTANT: Return ONLY a valid Python list of dictionaries without any markdown formatting, code blocks, or backticks. "
        f"Use single quotes for strings. Example format: [{'expr': '2+2', 'result': 4}]"
    )

    try:
        response = model.generate_content([prompt, img])
        print("Raw Gemini response:", response.text)
        
        # Clean the response text to remove markdown formatting
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if '```' in response_text:
            # Find content between code blocks
            json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
            else:
                # Alternative: find content between backticks
                parts = response_text.split('```')
                if len(parts) >= 3:
                    # Take the middle part (should be the data)
                    response_text = parts[1]
                    # Remove 'json' if it's at the start
                    if response_text.strip().startswith('json'):
                        response_text = response_text.strip()[4:].strip()
        
        # Further clean the response - remove any remaining non-JSON content
        response_text = response_text.strip()
        
        # Find the array in the text
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            response_text = response_text[start_idx:end_idx + 1]
        
        print(f"Cleaned response text: '{response_text}'")
        
        # Try ast.literal_eval first (handles Python-like syntax with single quotes)
        try:
            answers = ast.literal_eval(response_text)
            print("Parsed answers with ast.literal_eval:", answers)
        except (ValueError, SyntaxError) as e:
            print(f"ast.literal_eval failed: {e}")
            # Try json.loads as fallback (for proper JSON with double quotes)
            try:
                answers = json.loads(response_text)
                print("Parsed answers with json.loads:", answers)
            except json.JSONDecodeError as e:
                print(f"json.loads also failed: {e}")
                # Try to fix single quotes to double quotes and parse again
                try:
                    # Simple quote replacement (be careful with quotes inside strings)
                    fixed_text = response_text.replace("'", '"')
                    answers = json.loads(fixed_text)
                    print("Parsed answers after quote fixing:", answers)
                except json.JSONDecodeError:
                    print("All parsing methods failed")
                    answers = []
        
    except Exception as e:
        print(f"Error in parsing response from Gemini API: {e}")
        answers = []

    # Ensure all answers have the 'assign' key
    for answer in answers:
        answer['assign'] = answer.get('assign', False)

    return answers