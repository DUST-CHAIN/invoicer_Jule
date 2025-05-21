document.addEventListener('DOMContentLoaded', () => {
    // --- Elements ---
    const imageUpload = document.getElementById('imageUpload');
    const imagePreview = document.getElementById('imagePreview');
    const processButton = document.getElementById('processButton');
    const productsTsvOutput = document.getElementById('productsTsvOutput');
    const alcoholTsvOutput = document.getElementById('alcoholTsvOutput');
    const jsonOutput = document.getElementById('jsonOutput');
    const vatGrandTotalOutput = document.getElementById('vatGrandTotalOutput');
    const richTextOutput = document.getElementById('richTextOutput');
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

    // --- Process Invoice (Mock Implementation) ---
    if (processButton) {
        processButton.addEventListener('click', () => {
            console.log("Processing Invoice (mock)...");

            if (productsTsvOutput) {
                productsTsvOutput.value = "TOTAL COST	BUY PRICE	PRODUCT CODE\n100.00	90.00	P123";
            }
            if (alcoholTsvOutput) {
                alcoholTsvOutput.value = "TOTAL COST	BUY PRICE	CODE\n200.00	180.00	A456";
            }
            if (jsonOutput) {
                jsonOutput.value = JSON.stringify({ product_count: 1, alcohol_count: 1, supplier: "Mock Supplier" }, null, 2);
            }
            if (vatGrandTotalOutput) {
                vatGrandTotalOutput.value = "VAT: 20.00\nGrand Total: 320.00";
            }
            if (richTextOutput) {
                richTextOutput.textContent = "Invoice Processed Successfully (Mock Data). Full rich text would appear here.";
            }
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
            } else { // For DIVs like richTextOutput
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

    // --- Conceptual: Handling pasted images ---
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
    //         // Store this blob or base64 string for later "processing"
    //         // For example, you might want to set the value of a hidden input field
    //         // or display a different preview specifically for pasted images.
    //         // If imageUpload is a file input, you can't directly set its value
    //         // for security reasons. You'd handle the pasted image data separately.
    //       };
    //       reader.readAsDataURL(blob);
    //     }
    //   }
    // });
});
