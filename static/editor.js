// JavaScript helpers for the document editor page.
// The script provides formatting utilities and figure insertion dialogs.

/**
 * Wrap the currently selected text within the content textarea with the
 * provided opening and closing strings.
 *
 * @param {string} before - Text to insert before the selection.
 * @param {string} after - Text to insert after the selection.
 */
function wrapSelection(before, after) {
    const textarea = document.querySelector('textarea[name="content"]');
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selected = textarea.value.substring(start, end);
    // Replace the selected range with the wrapped content and move cursor
    textarea.setRangeText(before + selected + after, start, end, 'end');
    textarea.focus();
}

/**
 * Fetch lorem ipsum text from the server and insert it at the cursor.
 */
async function insertLorem() {
    const response = await fetch('/lorem');
    const text = await response.text();
    wrapSelection('\n' + text + '\n', '');
}

/**
 * Retrieve a list of uploaded figures from the server.
 *
 * @returns {Promise<Array>} Array of figure metadata objects.
 */
async function fetchFigures() {
    const response = await fetch('/figures');
    const data = await response.json();
    console.log('Fetched figures:', data.figures);
    return data.figures;
}

/**
 * Display a simple modal listing available figures. When the user selects a
 * figure, the provided callback receives the figure metadata.
 *
 * @param {Function} onSelect - Callback executed with the chosen figure.
 */
async function showFigureDialog(onSelect) {
    const figures = await fetchFigures();
    // Build overlay container
    const overlay = document.createElement('div');
    overlay.id = 'figure-dialog';
    overlay.innerHTML = '<table class="table table-hover mb-0"></table>';
    const table = overlay.querySelector('table');

    figures.forEach(fig => {
        const row = document.createElement('tr');
        row.innerHTML = `<td><img src="${fig.url}" alt="${fig.filename}" width="100"></td>` +
                        `<td class="align-middle">${fig.filename}</td>`;
        row.addEventListener('click', () => {
            onSelect(fig);
            document.body.removeChild(overlay);
        });
        table.appendChild(row);
    });

    // Clicking outside the table closes the dialog
    overlay.addEventListener('click', e => {
        if (e.target === overlay) {
            document.body.removeChild(overlay);
        }
    });

    document.body.appendChild(overlay);
}

// Attach click handlers once the DOM is fully loaded
window.addEventListener('DOMContentLoaded', () => {
    // Heading, subheading and subsubheading wrap selected text in LaTeX commands
    document.getElementById('btn-heading').addEventListener('click', () => {
        wrapSelection('\n\\section{', '}\n');
    });
    document.getElementById('btn-subheading').addEventListener('click', () => {
        wrapSelection('\n\\subsection{', '}\n');
    });
    document.getElementById('btn-subsubheading').addEventListener('click', () => {
        wrapSelection('\n\\subsubsection{', '}\n');
    });

    // Insert figure at cursor position with user-selected image and caption
    document.getElementById('btn-insert-figure').addEventListener('click', () => {
        showFigureDialog(async fig => {
            const caption = prompt('Enter figure caption', '') || '';
            const markup = `\n{{figure:${fig.path}|${caption}|${fig.label}}}\n`;
            wrapSelection(markup, '');
        });
    });

    // Insert figure reference based on selected image
    document.getElementById('btn-insert-reference').addEventListener('click', () => {
        showFigureDialog(fig => {
            const ref = `{{ref:${fig.label}}}`;
            wrapSelection(ref, '');
        });
    });

    document.getElementById('btn-lorem').addEventListener('click', insertLorem);
});
