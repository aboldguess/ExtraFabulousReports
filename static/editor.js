// JavaScript helpers for the document editor page.

/**
 * Insert the provided text at the current cursor position of the content
 * textarea, preserving focus so users can continue typing seamlessly.
 */
function insertAtCursor(text) {
    const textarea = document.querySelector('textarea[name="content"]');
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    // Replace the selected range with the new text and move the cursor
    textarea.setRangeText(text, start, end, 'end');
    textarea.focus();
}

/**
 * Fetch lorem ipsum text from the server and insert it into the document.
 */
async function insertLorem() {
    const response = await fetch('/lorem');
    const text = await response.text();
    insertAtCursor('\n' + text + '\n');
}

// Attach click handlers once the DOM is fully loaded
window.addEventListener('DOMContentLoaded', () => {
    document.getElementById('btn-heading').addEventListener('click', () => {
        insertAtCursor('\n\\section{Heading}\n');
    });
    document.getElementById('btn-subheading').addEventListener('click', () => {
        insertAtCursor('\n\\subsection{Subheading}\n');
    });
    document.getElementById('btn-figure').addEventListener('click', () => {
        insertAtCursor('\n{{figure:path/to/image.png|Caption|label}}\n');
    });
    document.getElementById('btn-reference').addEventListener('click', () => {
        insertAtCursor('{{ref:label}}');
    });
    document.getElementById('btn-lorem').addEventListener('click', insertLorem);
});
