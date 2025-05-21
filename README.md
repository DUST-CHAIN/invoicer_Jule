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
