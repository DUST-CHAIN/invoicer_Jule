from flask import Flask, request, jsonify
import os
import openai
import base64

app = Flask(__name__)

# --- OpenAI API Key Handling ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_API_KEY_HERE")
OPENAI_API_KEY_CONFIGURED = False

if OPENAI_API_KEY != "YOUR_API_KEY_HERE" and OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
    OPENAI_API_KEY_CONFIGURED = True
    print("OpenAI API key is configured.")
else:
    print("Warning: OPENAI_API_KEY is not set or is a placeholder. OpenAI calls will be simulated with mock data.")

# --- Invoice Prompt ---
# ADVISORY: For more robust parsing of the AI's output, consider modifying this prompt
# to instruct the AI to use clear, unique delimiters between each requested section.
# For example:
# "---PRODUCTS_TSV_START---
# [Products TSV content]
# ---PRODUCTS_TSV_END---
# ---JSON_OUTPUT_START---
# [JSON content]
# ---JSON_OUTPUT_END---"
# Alternatively, you could simplify by asking the AI to return a single JSON object
# containing all the required data fields (Products TSV as a string, Alcohol TSV as a string, etc.).
# The parse_openai_response function would then need to be updated accordingly.
INVOICE_PROMPT = """
clear your memory before you start. 
You are an invoice parser/formatter. Extract structured data from the supplier invoice provided and output a TSV table of all the products in a given format which is this: TOTAL BUYING PRICE	CALC TOTAL	BUYING PRICE	PRODUCT CODE	CATEGORY	BRAND	PRODUCT NAME	QUANTITY	OUM	INVOICE DATE	DELIVERY DATE	PAYMENT DUE	SUPPLIER	SOURCE	NOTES	Alcohol contents	Wine Year	Wine Region & Country	ML

General rules:

* Parse all fields from the scan into your internal json object to contain all the data you found, then use this data to proceed.
* Every row must include all columns; use "" for missing. infer what you can, when inferring wrap in [ ].
* always Keep specified column order
* Output only the TSV tables (no explanations, no asking if user want anything else - just the output as TSV).
* Translate non-English to English (not names).
* do not add use emojis
* all details from invoice must be accuratly as in the invoice.
* anything inferred wrap in [].

here are explanation of the column headers:
for food products
	* TOTAL BUYING PRICE: total for this row (buying price x quantity, as in the invoice)
	* CALC TOTAL: do not fill this column, it will be filled later by the user
	* BUYING PRICE: buying price of a unit (as in the invoice).
	* PRODUCT CODE:  exact code.
	* CATEGORY: in case of food products: CHEESE, MEAT, CANNED, CONDIMENT, SPICE, etc. infer if not provided, leave empty if don't know.
	* CATEGORY: in case of alcohol/drink/wine products:  WINE (WHITE, RED, ROSE, SPARKLING, etc), Alcohol (WHISKEY, Rum, Champagne, etc)
	* BRAND: brand or manufacturer of the product. infer if not provided
	* PRODUCT NAME: product name as found in the invoice
	* QUANTITY: product quantity as found in the invoice
	* OUM: in case of food products: unit of measure as found in the invoice(kg, gr, lit. BT for bottle, can for canned, etc as found in the invoice)
	* OUM: in case of alcohol/drink/wine: unit of measure (kg, gr, lit. BT for bottle, etc) as found in the invoice
	* INVOICE DATE: INVOICE DATE
	* DELIVERY DATE: DELIVERY DATE
	* PAYMENT DUE: PAYMENT DUE
	* SUPPLIER: SUPPLIER name
	* SOURCE: invoice number
	* NOTES: any notes found that relate to this item
these are in case of alcohol/drink/wine:
	* Alcohol contents: alcohol %. infer if not provided, leave empty if don't know
	* Wine Year: for Wine: infer year if not provided, leave empty if you don't know
	* Wine Region & Country: infer wine region & country where it is made if not provided. leave empty if you don't know
	* ML: for wine: bottle volume (1 liter, 750ml etc.
"""

# The existing ADVISORY comment above the prompt is still relevant if the AI's single TSV output is inconsistent.
# However, since the prompt now asks for ONLY the TSV, the main risk is the AI including extra chatter
# before or after the TSV, which parse_openai_response will need to handle by stripping.
# ADVISORY: This parsing function relies on the AI outputting sections in the order
# specified in the prompt and using headers similar to those defined below.
# This can be brittle if the AI's output format varies.
# Testing with actual OpenAI responses for your specific invoice types is crucial.
# If parsing is unreliable, modify the INVOICE_PROMPT to include unique delimiters
# or request a single JSON output, and update this parsing logic accordingly.
def parse_openai_response(raw_text):
    # The new prompt asks the AI to "Output only the TSV tables (no explanations...)"
    # So, the raw_text should ideally be just the TSV.
    # We'll strip any leading/trailing whitespace just in case.
    cleaned_tsv_output = raw_text.strip()
    
    # The frontend will now expect a JSON with a single key for the TSV data.
    return {"invoice_tsv": cleaned_tsv_output}


def call_openai_api(image_bytes, filename):
    if not OPENAI_API_KEY_CONFIGURED:
        print("OpenAI API key not configured. Returning simulated AI data.") # Message updated for consistency
        # This part should use the new single TSV format
        simulated_raw_response_for_no_key = (
            "TOTAL BUYING PRICE\tCALC TOTAL\tBUYING PRICE\tPRODUCT CODE\tCATEGORY\tBRAND\tPRODUCT NAME\tQUANTITY\tOUM\tINVOICE DATE\tDELIVERY DATE\tPAYMENT DUE\tSUPPLIER\tSOURCE\tNOTES\tAlcohol contents\tWine Year\tWine Region & Country\tML\n"
            "SIM_NK_10.50\t\tSIM_NK_9.25\tSIM_NK_P1\tSIM_NK_CAT1\tSIM_NK_BRAND1\tSIM_NK_Prod1\tSIM_NK_1\tSIM_NK_gr\tSIM_NK_20231101\tSIM_NK_20231102\tSIM_NK_20231130\tSIM_NK_Supp1\tSIM_NK_INV000\tSIM_NK_Note1\t\t\t\t\n"
            "SIM_NK_100.00\t\tSIM_NK_90.00\tSIM_NK_A1\tSIM_NK_WINE\tSIM_NK_BRAND_A1\tSIM_NK_AlcName1\tSIM_NK_1\tSIM_NK_BT\tSIM_NK_20231101\tSIM_NK_20231102\tSIM_NK_20231130\tSIM_NK_Supp1\tSIM_NK_INV000\tSIM_NK_NoteAlc1\tSIM_NK_12.5\tSIM_NK_2022\tSIM_NK_Region\tSIM_NK_700ml"
        )
        # Also add the note_from_backend directly here, as parse_openai_response no longer handles it.
        parsed_data = parse_openai_response(simulated_raw_response_for_no_key)
        parsed_data["note_from_backend"] = "OpenAI API key not configured. Displaying simulated TSV data."
        return parsed_data

    try:
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        image_mime_type = "image/jpeg" 
        if filename.lower().endswith(".png"):
            image_mime_type = "image/png"
        elif filename.lower().endswith(".gif"):
            image_mime_type = "image/gif"
        elif filename.lower().endswith(".webp"):
            image_mime_type = "image/webp"

        print(f"Attempting live OpenAI API call for image: {filename} (MIME: {image_mime_type})")
        
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": INVOICE_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{image_mime_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=4000 
        )
        raw_response_content = response.choices[0].message.content
        print("Successfully received response from OpenAI API.")
        return parse_openai_response(raw_response_content)

    except openai.error.AuthenticationError as e:
        print(f"OpenAI Authentication Error: {e}")
        return {"error": f"OpenAI Authentication Error: Your API key may be invalid or revoked. Details: {e}"}
    except openai.error.RateLimitError as e:
        print(f"OpenAI Rate Limit Error: {e}")
        return {"error": f"OpenAI Rate Limit Error: You have exceeded your usage quota. Details: {e}"}
    except openai.error.APIConnectionError as e:
        print(f"OpenAI API Connection Error: {e}")
        return {"error": f"OpenAI API Connection Error: Could not connect to OpenAI. Details: {e}"}
    except openai.error.InvalidRequestError as e:
        print(f"OpenAI Invalid Request Error: {e}")
        return {"error": f"OpenAI Invalid Request Error: {e}"}
    except openai.error.OpenAIError as e:
        print(f"OpenAI API Error: {e}")
        return {"error": f"OpenAI API Error: {e}"}
    except Exception as e:
        print(f"An unexpected error occurred during OpenAI API call: {e}")
        return {"error": f"An unexpected error occurred: {e}"}


@app.route('/api/process-invoice', methods=['POST'])
def process_invoice():
    if 'invoiceImage' not in request.files:
        return jsonify({"error": "No invoice image provided"}), 400

    file = request.files['invoiceImage']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        image_bytes = file.read()
        
        api_response = call_openai_api(image_bytes, file.filename)

        if "error" in api_response:
            error_message = api_response["error"]
            status_code = 500 
            if "Authentication Error" in error_message:
                status_code = 401
            elif "Rate Limit Error" in error_message:
                status_code = 429
            elif "Invalid Request Error" in error_message:
                status_code = 400
            return jsonify(api_response), status_code
        
        return jsonify(api_response)

    return jsonify({"error": "File processing failed at an unexpected point"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
