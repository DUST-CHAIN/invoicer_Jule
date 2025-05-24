document.addEventListener('DOMContentLoaded', () => {
    // --- API Endpoint ---
    const API_ENDPOINT = 'http://127.0.0.1:5000/api/process-invoice';

    // --- Elements ---
    const imageUpload = document.getElementById('imageUpload');
    const imagePreview = document.getElementById('imagePreview');
    const processButton = document.getElementById('processButton');
    // const productsTsvOutput = document.getElementById('productsTsvOutput'); // Old
    // const alcoholTsvOutput = document.getElementById('alcoholTsvOutput'); // Old
    // const jsonOutput = document.getElementById('jsonOutput'); // Old
    // const vatGrandTotalOutput = document.getElementById('vatGrandTotalOutput'); // Old
    // const richTextOutput = document.getElementById('richTextOutput'); // Old
    const invoiceTsvOutput = document.getElementById('invoiceTsvOutput'); // New
    const copyButtons = document.querySelectorAll('.copy-btn');

    // --- Image Preview ---
    if (imageUpload && imagePreview) {
        imageUpload.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                imagePreview.src = URL.createObjectURL(file);
                imagePreview.style.display = 'block';
            } else {
                imagePreview.src = '#';
                imagePreview.style.display = 'none';
            }
        });
    }

    // --- Process Invoice (with Backend Integration) ---
    if (processButton) {
        processButton.addEventListener('click', () => {
            const file = imageUpload.files[0];

            if (!file) {
                alert("Please select an invoice image.");
                return;
            }

            const formData = new FormData();
            formData.append('invoiceImage', file);

            const originalButtonText = processButton.textContent;
            processButton.disabled = true;
            processButton.textContent = "Processing...";

            // Clear previous output
            if(invoiceTsvOutput) invoiceTsvOutput.value = ""; // Updated ID and only one field to clear

            fetch(API_ENDPOINT, {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    // Try to get error message from backend if available (JSON format)
                    return response.json().then(errData => {
                        // If backend sends a specific 'error' field, use it.
                        throw new Error(errData.error || `Server responded with ${response.status}`);
                    }).catch(() => { // If backend didn't send JSON error or response.json() fails
                        throw new Error(`Server responded with ${response.status}. Unable to parse error details.`);
                    });
                }
                return response.json();
            })
            .then(data => {
                let outputText = data.invoice_tsv || ""; // Expecting 'invoice_tsv' from backend
                if (data.note_from_backend) {
                    outputText = `Note: ${data.note_from_backend}\n\n${outputText}`;
                }
                if(invoiceTsvOutput) invoiceTsvOutput.value = outputText; // Updated ID
            })
            .catch(error => {
                console.error('Error processing invoice:', error);
                if(invoiceTsvOutput) invoiceTsvOutput.value = `Error: ${error.message}`; // Display error in the main textarea
            })
            .finally(() => {
                processButton.disabled = false;
                processButton.textContent = originalButtonText;
            });
        });
    }

    // --- Copy to Clipboard ---
    copyButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetId = button.dataset.target;
            const targetElement = document.getElementById(targetId);
            let textToCopy;

            if (!targetElement) return;

            if (targetElement.tagName === 'TEXTAREA') {
                textToCopy = targetElement.value;
            } else { 
                // No other element types are expected for copying now, but keeping structure.
                // Could be simplified if only TEXTAREA is ever targeted.
                textToCopy = targetElement.textContent; 
            }

            navigator.clipboard.writeText(textToCopy).then(() => {
                const originalText = button.textContent;
                button.textContent = 'Copied!';
                setTimeout(() => {
                    button.textContent = originalText;
                }, 2000); // Revert text after 2 seconds
            }).catch(err => {
                console.error('Failed to copy: ', err);
                // Optionally, provide error feedback to the user
            });
        });
    });

    // --- Conceptual: Handling pasted images (remains unchanged) ---
    // document.addEventListener('paste', function(event) {
    //   const items = (event.clipboardData || event.originalEvent.clipboardData).items;
    //   for (let item of items) {
    //     if (item.type.indexOf('image') !== -1) {
    //       const blob = item.getAsFile();
    //       const reader = new FileReader();
    //       reader.onload = function(e) {
    //         if (imagePreview) {
    //           imagePreview.src = e.target.result;
    //           imagePreview.style.display = 'block';
    //         }
    //       };
    //       reader.readAsDataURL(blob);
    //     }
    //   }
    // });
});
