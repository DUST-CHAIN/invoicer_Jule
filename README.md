# Invoice Processing Web Application

This application provides a user interface to upload an invoice image, (conceptually) send it for AI processing, and display the extracted data in various formats.

## How to Use
1.  Open `index.html` in a web browser.
2.  Click "Choose File" to select an invoice image. A preview will be shown.
3.  Click "Process Invoice".
4.  The output areas below will be populated with (currently mock) data extracted from the invoice.
5.  Use the "Copy" buttons next to each field to copy the data to your clipboard.

## Files
*   `index.html`: The main HTML structure of the application.
*   `style.css`: Contains all the CSS styles for the application.
*   `script.js`: Contains the JavaScript logic for image preview, mock processing, and copy-to-clipboard functionality.

## Backend Interaction (Conceptual)

The current version uses mock data for demonstration purposes. A full implementation would require a backend service to handle the actual invoice processing using an AI model.

### 1. Request from Frontend to Backend

When the user clicks "Process Invoice" and an image is selected, the frontend would send a request to a backend API endpoint (e.g., `/api/process-invoice`).

*   **Endpoint:** `POST /api/process-invoice`
*   **Method:** `POST`
*   **Body Type:** `multipart/form-data`
    *   The request body would contain the invoice image file. For example, a field named `invoiceImage` of type `file`.

**Example JavaScript (Frontend - Conceptual):**
```javascript
// const imageFile = document.getElementById('imageUpload').files[0];
// const formData = new FormData();
// formData.append('invoiceImage', imageFile);
//
// fetch('/api/process-invoice', {
//   method: 'POST',
//   body: formData
// })
// .then(response => response.json())
// .then(data => {
//   // Populate text areas with data from the response
//   document.getElementById('productsTsvOutput').value = data.productsTsv;
//   document.getElementById('alcoholTsvOutput').value = data.alcoholTsv;
//   document.getElementById('jsonOutput').value = data.jsonOutput;
//   document.getElementById('vatGrandTotalOutput').value = data.vatGrandTotal;
//   document.getElementById('richTextOutput').textContent = data.richTextInfo;
// })
// .catch(error => console.error('Error:', error));
```

### 2. Backend Processing

The backend service would:
1.  Receive the image file.
2.  (Optional) Perform pre-processing on the image (e.g., resizing, enhancing quality).
3.  Send the image and the specified parsing prompt to an AI model (e.g., via an API call to a service like GPT).
    *   The prompt to be used is:
        ```
        You are an invoice parser/formatter. Extract structured data from a supplier invoice and output two TSV tables: Products and Alcohol/Wine.

        General rules:

        * Parse all fields.
        * Every row must include all columns; use "" for missing. If inferring with 100% accuracy, wrap in [ ].
        * Keep specified column order.
        * Output only the TSV tables (no explanations).
        * Translate non-English to English.

        Products TSV (headers):

        TOTAL COST  BUY PRICE  PRODUCT CODE  CATEGORY  BRAND  PRODUCT NAME  WEIGHT  UOM  INVOICE DATE  DELIVERY DATE  PAYMENT DUE  SUPPLIER  NOTE  SOURCE

        * BUY PRICE: unit price.
        * PRODUCT CODE: exact code.
        * CATEGORY: CHEESE, MEAT, CANNED, CONDIMENT, SPICE, etc.
        * BRAND: if present.
        * PRODUCT NAME: full name (excluding brand).
        * WEIGHT: per item.
        * UOM: unit (gr, Kg, Lt, PC, BT).
        * INVOICE DATE, DELIVERY DATE, PAYMENT DUE: as given.
        * SUPPLIER: name.
        * NOTE: comments (“keep frozen”), or "".
        * SOURCE: invoice number.

        Alcohol/Wine TSV (headers):

        TOTAL COST  BUY PRICE  CODE  TYPE  BRAND  NAME  YEAR  ML  ALC  QUANTITY  PAYABLE ON  NOTE  SOURCE

        * BUY PRICE: unit price.
        * CODE: exact code.
        * TYPE: e.g., RED WINE, ROSE.
        * BRAND: brand.
        * NAME: full product name.
        * YEAR: if wine.
        * ML: bottle volume.
        * ALC: alcohol %.
        * QUANTITY: number of bottles.
        * PAYABLE ON: due date.
        * NOTE: any notes.
        * SOURCE: invoice number.

        After TSVs, output JSON, then VAT, grand total, and full invoice info as rich text.

        Finally, request the invoice scan.
        ```
4.  Receive the structured data from the AI model.
5.  Parse and structure this data into a JSON response format.

### 3. Response from Backend to Frontend

The backend would send a JSON response to the frontend.

*   **Content-Type:** `application/json`
*   **Example JSON Response Body:**
    ```json
    {
      "productsTsv": "TOTAL COST	BUY PRICE	PRODUCT CODE	...
...",
      "alcoholTsv": "TOTAL COST	BUY PRICE	CODE	...
...",
      "jsonOutput": "{
  "key": "value",
  ...
}",
      "vatGrandTotal": "VAT: XX.XX
Grand Total: YY.YY",
      "richTextInfo": "Full extracted invoice information formatted as rich text (or Markdown)..."
    }
    ```

This conceptual outline provides a basis for developing the necessary backend services to make the application fully functional.

## Exploring Free AI/OCR Alternatives

The invoice processing requested involves not just Optical Character Recognition (OCR) to extract text, but also complex interpretation of that text and generation of multiple structured output formats (TSV, JSON, rich text) based on a detailed prompt. This level of understanding and generation is best suited for advanced AI models. However, let's explore some free or partially-free alternatives and their capabilities:

### 1. The Core Challenge

The primary task is to transform an image of an invoice into several specific, structured data formats. This requires:
*   Accurate text extraction from the image (OCR).
*   Understanding the relationships between different pieces of text (e.g., identifying line items, prices, supplier details).
*   Interpreting a complex prompt to categorize items (e.g., as "Products" vs. "Alcohol/Wine"), extract specific fields for each category, and handle missing information.
*   Formatting the extracted and interpreted data into TSV, JSON, and a rich text summary.

Simple OCR tools can handle the first step, but the subsequent steps typically require more advanced intelligence.

### 2. Tesseract OCR

*   **What it is:** Tesseract is a powerful, free, and open-source OCR engine.
*   **Usage:**
    *   **Backend:** It can be used in Python via the `pytesseract` wrapper.
    *   **Frontend:** `Tesseract.js` allows OCR directly in the browser.
*   **Capabilities & Limitations:**
    *   Tesseract excels at extracting raw text from images.
    *   However, it does **not** interpret the meaning of the text or understand the user's detailed prompt for structuring the output.
    *   Significant custom parsing logic (e.g., using regular expressions, keyword spotting, and complex algorithms) would be required to even attempt to transform Tesseract's raw text output into the desired TSV, JSON, and rich text formats. This would be a complex and error-prone development task for each different invoice layout.
    *   `Tesseract.js` could perform client-side OCR. The extracted raw text could then be sent to a backend. If a powerful AI (like OpenAI's models) is available on that backend, it could then process this text. Without such an AI on the backend, you'd face the same custom parsing challenges.

### 3. Cloud OCR Services (Google Cloud Vision AI, AWS Textract, Azure Form Recognizer)

*   **What they are:** Major cloud providers offer OCR services that often have free tiers for limited usage.
*   **Capabilities & Limitations:**
    *   These services are generally very good at text extraction.
    *   Some, like AWS Textract and Azure Form Recognizer, are specialized for documents and invoices. They can often provide a somewhat structured output (e.g., key-value pairs, tables) beyond just raw text.
    *   However, the structure they provide is their own predefined format. This output would still need to be mapped and transformed into the very specific multi-format output (Products TSV, Alcohol/Wine TSV with exact columns, custom JSON, specific VAT/Total formatting) required by the user's prompt.
    *   Achieving this final transformation would likely require another layer of processing, potentially involving a sophisticated AI call (if available) or very complex custom code to re-structure the cloud service's output.

### 4. Summarizing the Gap

While basic text can be extracted from invoices using free tools like Tesseract or free tiers of cloud OCR services, achieving the highly specific, structured, and multi-format output as detailed in the user's prompt (including distinct TSVs for products and alcohol, a custom JSON object, and specific formatting for totals) generally requires a sophisticated AI model like OpenAI's GPT. These advanced models can better understand the nuances of the prompt and generate the complex, structured output required.

### 5. Potential Limited Fallback (Conceptual)

If an OpenAI API key is not available or configured, a very basic fallback mechanism could be (conceptually) implemented in the backend:
1.  Use `pytesseract` to perform OCR on the uploaded invoice image.
2.  Return the raw, unstructured text extracted by Tesseract to the frontend.
3.  The frontend would then display this raw text, accompanied by a clear disclaimer stating: "The following is raw text extracted from the invoice. Full structured processing via AI is not available (e.g., API key missing). This text is unformatted and may contain OCR errors."

This approach would provide *some* utility by making the invoice text searchable/copyable, but it would not deliver the structured, multi-format output that is the primary goal of the application. This is only a conceptual addition to the README and not a current implementation feature.

## Deployment to GitHub Pages

This section explains how different parts of this project can (and cannot) be deployed, with a focus on GitHub Pages.

### 1. GitHub Pages is for Static Sites

*   GitHub Pages is designed to host static files (HTML, CSS, JavaScript) directly from a GitHub repository.
*   It **cannot** run server-side code like Python/Flask applications. This means our `backend/app.py` cannot run on GitHub Pages.

### 2. Deploying the Frontend

The frontend part of this project (the `index.html`, `style.css`, and `script.js` files located in the root directory) **can** be deployed to GitHub Pages.

#### Enabling GitHub Pages for Your Repository

Here are the steps to deploy the frontend to GitHub Pages:

1.  **Navigate to your GitHub repository on GitHub.com.**
2.  Click on the **Settings** tab (usually near the top of the repository page).
3.  In the left sidebar, scroll down and click on **Pages** (under the 'Code and automation' section).
4.  Under **Build and deployment**, for the **Source**, select **Deploy from a branch**.
5.  Under **Branch**:
    *   Select the branch you want to deploy from (e.g., `main`).
    *   For the folder, select `/root`.
    *   Click **Save**.
6.  **Wait for Deployment:** GitHub will start a deployment process. It might take a few minutes for your site to become live.
7.  **Accessing Your Site:** Once deployed, the URL of your live site (e.g., `https://<your-username>.github.io/<your-repository-name>/`) will be displayed at the top of the GitHub Pages settings page. You can click 'Visit site'.

**Important Reminder:** As mentioned earlier, these steps deploy only the frontend (HTML, CSS, JavaScript). The Python backend for processing invoices **will not run on GitHub Pages**. For the deployed site to be fully functional (i.e., to actually process invoices), you would need to:
1.  Host the Python backend on a separate server or platform (e.g., Heroku, AWS, Google Cloud, PythonAnywhere).
2.  Update the `API_ENDPOINT` constant in your `script.js` file (in the branch you deployed, e.g., `main`) to point to your live backend's public URL.
3.  Commit and push this change to `script.js`, which will trigger a new deployment on GitHub Pages with the updated API endpoint.

For further general instructions on setting up GitHub Pages, refer to the official documentation: [GitHub Pages Documentation](https://docs.github.com/en/pages).

### 3. Handling the Backend

*   As stated, the Python Flask backend (`backend/app.py`) **cannot** be deployed on GitHub Pages.
*   For the frontend deployed on GitHub Pages to work fully with the AI processing capabilities, the backend API (currently in `backend/app.py`) needs to be:
    1.  Running on a separate hosting service that supports Python/Flask applications (e.g., Heroku, AWS EC2/Lambda, Google Cloud Run/App Engine, PythonAnywhere, Vercel for serverless Python functions, etc.).
    2.  Accessible publicly via the internet.
*   The `API_ENDPOINT` constant in `script.js` (currently `http://127.0.0.1:5000/api/process-invoice`) would need to be **updated** to point to the public URL of your hosted backend API. For example:
    ```javascript
    // Example in script.js
    // const API_ENDPOINT = 'https://your-hosted-backend-api.com/api/process-invoice';
    ```

### 4. Alternative for Full Client-Side Functionality (Conceptual)

*   If the application were designed to be fully client-side, it could potentially run entirely on GitHub Pages. This would require:
    *   Using a client-side OCR solution (like `Tesseract.js`) to extract text from the image directly in the browser.
    *   The subsequent AI processing step (to interpret the user's prompt and structure the data) would also need to be:
        *   Performable by a client-side AI model/library (less likely for complex tasks), OR
        *   Handled by calling a public, CORS-enabled AI service that does not require a secret API key managed by *our own* backend (i.e., the API key could be a public one, or the service is free without keys for certain usage tiers).
*   However, given the current project structure (which includes a Python Flask backend and conceptual OpenAI API calls that would typically use a secret API key managed by that backend), this fully client-side approach is not the current design. This point is included for a comprehensive understanding of deployment options.

## Local End-to-End Testing

This section guides you through setting up and running the frontend and backend locally to test the complete application flow.

### 1. Prerequisites

*   Python 3.x installed.
*   `pip` (Python package installer) available.
*   A modern web browser (e.g., Chrome, Firefox, Edge).

### 2. Backend Setup and Execution

1.  **Navigate to the backend directory:**
    ```bash
    cd backend
    ```

2.  **Create and activate a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    # For Windows Command Prompt: venv\Scripts\activate
    # For Windows PowerShell: .\venv\Scripts\Activate.ps1
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **OpenAI API Key Configuration:**
    For actual OpenAI integration (currently simulated in the code if no key is provided), set the `OPENAI_API_KEY` environment variable **before** running the backend:
    ```bash
    export OPENAI_API_KEY="your_actual_openai_api_key_here" # Linux/macOS
    # set OPENAI_API_KEY="your_actual_openai_api_key_here" # Windows Command Prompt
    # $env:OPENAI_API_KEY="your_actual_openai_api_key_here" # Windows PowerShell
    ```
    Alternatively, you can temporarily modify the placeholder string in `backend/app.py` directly (where `OPENAI_API_KEY = os.getenv(...)` is defined), but using environment variables is strongly recommended for security and flexibility.

    If the `OPENAI_API_KEY` is not set, is empty, or remains as the placeholder "YOUR_API_KEY_HERE", the backend will use simulated AI data and inform the frontend via a note in the output.

5.  **Run the Flask server:**
    ```bash
    python app.py
    ```
    The backend will start, typically on `http://127.0.0.1:5000`. You should see output in your terminal indicating it's running.

### 3. Frontend Setup and Execution

1.  **Navigate to the project root directory** (if you were in the `backend` directory, go one level up):
    ```bash
    cd .. 
    ```

2.  **Open `index.html` in your web browser:**
    Simply find the `index.html` file in the project's root directory and open it with your browser (e.g., by double-clicking it or using "File > Open").

3.  **Cross-Origin Resource Sharing (CORS) Handling:**
    The frontend (`index.html` opened as a local file) will make requests to the backend server (`http://127.0.0.1:5000`). Browsers have security policies (CORS) that might block these requests by default.

    If you encounter issues (like the "Process Invoice" request failing silently, or seeing errors related to CORS in your browser's developer console), you'll need to enable CORS in the Flask backend for local development.

    **To enable CORS:**
    *   First, add `Flask-CORS` to the backend's requirements. Open `backend/requirements.txt` and add the line:
        ```
        Flask-CORS>=3.0
        ```
    *   Then, modify `backend/app.py`:
        ```python
        from flask import Flask, request, jsonify
        from flask_cors import CORS # <--- Add this import
        import os
        # ... other imports ...

        app = Flask(__name__)
        CORS(app) # <--- Add this line after app initialization

        # ... rest of your app.py code ...
        ```
    *   After saving these changes, go back to your `backend` directory terminal (ensure your virtual environment is active if you used one) and re-install the requirements:
        ```bash
        pip install -r requirements.txt
        ```
    *   Then, restart the Flask server (`python app.py`).

    **Security Note:** Enabling CORS for all origins using `CORS(app)` is acceptable for local development. For production environments, CORS should be configured more restrictively to only allow requests from trusted origins.

### 4. Testing Steps

1.  Ensure your backend Flask server is running (see Backend Setup).
2.  Open `index.html` in your web browser (see Frontend Setup).
3.  Click the "Choose File" button and select an image file (e.g., a JPEG or PNG of an invoice). You should see a preview of the image.
4.  Click the "Process Invoice" button.
    *   The button should change to "Processing..." temporarily.
    *   Observe the "Invoice Data (TSV)" text area below. It should become populated with the TSV data received from the backend.
5.  **Verification (Simulated Data - No API Key):**
    *   If you **did not** configure the `OPENAI_API_KEY` as described in "Backend Setup", the backend will use simulated data.
    *   The "Invoice Data (TSV)" text area on the frontend should display the simulated TSV data, prepended with a "Note: OpenAI API key not configured. Displaying simulated TSV data."
6.  Test the "Copy TSV" button next to the output area.

### 5. Testing with a Live OpenAI API Key

This is the crucial step to verify the actual AI-powered invoice processing.

*   **Prerequisite:** Ensure you have correctly set the `OPENAI_API_KEY` environment variable with a valid key for a model like `gpt-4-vision-preview`, and that your Flask server has been restarted since setting the variable. Refer to step 4 in "Backend Setup and Execution".
*   **Cost Warning:** Be aware that making calls to the OpenAI API will incur costs based on your usage. Monitor your OpenAI account for billing details.

**Expected Behavior with a Live API Key:**

1.  **Backend Console Logs:**
    *   When you process an invoice, the Flask server console should display messages indicating a live API call is being attempted (e.g., "Attempting live OpenAI API call for image: your_image.jpg...").
    *   If successful, it should log "Successfully received response from OpenAI API."
    *   If there are errors (e.g., authentication, rate limits, invalid image), specific error messages from the OpenAI API will be logged.

2.  **Frontend Display:**
    *   The data displayed in the "Invoice Data (TSV)" text area should be a single TSV string derived from the *actual content* of the invoice image you uploaded. It will **not** be the simulated data.
    *   The "Note: OpenAI API key not configured..." message should **not** appear.

**Troubleshooting and Verification for Live API Testing:**

1.  **Check API Key Setup:**
    *   Verify that the `OPENAI_API_KEY` environment variable is correctly set in the terminal session where you launched the Flask server.
    *   Ensure the Flask server was restarted *after* setting the environment variable.

2.  **Monitor Backend Logs Closely:**
    *   The Flask server console is your primary source for diagnosing issues. Look for:
        *   Confirmation that the API key is configured and being used (e.g., the "OpenAI API key is configured." message at startup).
        *   The "Attempting live OpenAI API call..." message.
        *   Any error messages prefixed with "OpenAI Authentication Error:", "OpenAI Rate Limit Error:", "OpenAI API Error:", etc. These errors come directly from the OpenAI service or library.
        *   The `backend/app.py` currently prints the raw response from OpenAI if the call is successful. You can inspect this to see exactly what the AI returned before parsing. (Be mindful this can be very large).

3.  **Examine Frontend Data Quality:**
    *   Does the TSV data in the "Invoice Data (TSV)" text area accurately reflect the content of your test invoice and the column structure defined in the `INVOICE_PROMPT`?
    *   Since the `parse_openai_response` function is now very simple (it just takes the AI's raw output and puts it into the `invoice_tsv` field after stripping whitespace), most "parsing" issues will relate to the AI's adherence to the `INVOICE_PROMPT` format.
    *   Check if the AI included any conversational text before or after the TSV data. The `strip()` method in `parse_openai_response` should handle leading/trailing whitespace, but not extraneous text mixed with the TSV.

4.  **Iterative Refinement (If AI Output is Incorrect or Inconsistent):**
    *   The reliability of the output heavily depends on the AI consistently formatting its response as a single, clean TSV according to the `INVOICE_PROMPT`.
    *   If you find that data is missing, incorrectly formatted, or the TSV structure is not as expected:
        *   **Review Backend Logs:** Look at the raw AI response. Is it a clean TSV? Does it follow the requested column order?
        *   **Adjust `INVOICE_PROMPT`:** You might need to further refine the prompt. For example, re-emphasize "Output only the TSV table and nothing else." Or, if the AI struggles with a single complex TSV, you might revert to asking for unique delimiters and more complex parsing, or request a JSON object (as suggested in the advisory comments in `backend/app.py`).
        *   **Consider Post-processing (if minor issues):** If the AI is *mostly* correct but adds small, predictable non-TSV elements, you could theoretically add more sophisticated stripping logic to `parse_openai_response` beyond just `strip()`. However, improving the prompt is usually a better first step.
        *   Refer to the detailed advisory comments near the `INVOICE_PROMPT` and `parse_openai_response` function in `backend/app.py` for more guidance. Testing with various invoices and iteratively refining the prompt and parser is often necessary.

By following these steps, you can thoroughly test the live OpenAI integration and refine the system for accuracy.
