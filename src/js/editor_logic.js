// --- Global Helper Functions ---
// Moved to global scope to be accessible by onclick attributes
function formatDoc(command, value = null) {
    const contentDiv = document.querySelector('.lesson-content-editable');
    if (contentDiv && contentDiv.isContentEditable) {
        document.execCommand(command, false, value);
        contentDiv.focus();
    }
}
function changeBlockFormat(selectElement) {
    const value = selectElement.value;
    if (value) {
        formatDoc('formatBlock', value);
    }
    selectElement.selectedIndex = 0; // Reset dropdown to default
}
function insertStyledBox(className) {
    const selection = window.getSelection();
    if (!selection.rangeCount) return;
    const range = selection.getRangeAt(0);
    const selectedText = selection.toString();
    
    const box = document.createElement('div');
    box.className = className;
    
    const p = document.createElement('p');
    if (selectedText) {
        p.textContent = selectedText;
        range.deleteContents();
    } else {
        p.innerHTML = 'Votre texte ici...';
    }
    box.appendChild(p);
    range.insertNode(box);
}
// --- Main Logic ---
var print_handler_obj;
var edit_handler_obj;
var originalContent = ''; // To store content for cancellation
new QWebChannel(qt.webChannelTransport, function(channel) {
    // Assign channel objects
    var height_reporter = channel.objects.height_reporter_obj;
    print_handler_obj = channel.objects.print_handler_obj;
    edit_handler_obj = channel.objects.edit_handler_obj;
    const wrapper = document.getElementById('content-wrapper');
    if (wrapper) {
        const resizeObserver = new ResizeObserver(entries => {
            // Use scrollHeight for a more reliable total height calculation, including margins and overflow.
            // Add a small buffer to prevent scrollbars from appearing due to sub-pixel rendering.
            height_reporter.setHeight(wrapper.scrollHeight + 20);
        });
        resizeObserver.observe(wrapper);
    }
    // --- Event Listeners Setup ---
    const editButton = document.querySelector('.edit-button-html');
    const cancelButton = document.querySelector('.cancel-button-html');
    const contentDiv = document.querySelector('.lesson-content-editable');
    const savedNotification = document.querySelector('.saved-notification');
    const editToolbar = document.querySelector('.edit-toolbar');
    const deleteButton = document.querySelector('.delete-button-html');
    if (editButton && cancelButton && contentDiv && editToolbar && deleteButton) {
        // EDIT/SAVE button
        editButton.addEventListener('click', function() {
            const isEditing = contentDiv.isContentEditable;
            if (isEditing) {
                // --- SAVE ---
                contentDiv.contentEditable = false;
                editToolbar.style.display = 'none';
                cancelButton.style.display = 'none';
                editButton.textContent = '✏️ Éditer';
                editButton.classList.remove('save-button-html');
                editButton.classList.add('edit-button-html');
                const updatedContent = contentDiv.innerHTML;
                edit_handler_obj.saveContent(updatedContent);
                // Show saved notification
                savedNotification.style.opacity = '1';
                savedNotification.style.transform = 'translateY(0)';
                setTimeout(() => {
                    savedNotification.style.opacity = '0';
                    savedNotification.style.transform = 'translateY(-10px)';
                }, 2000);
            } else {
                // --- START EDIT ---
                originalContent = contentDiv.innerHTML;
                contentDiv.contentEditable = true;
                editToolbar.style.display = 'flex';
                cancelButton.style.display = 'inline-block';
                contentDiv.focus();
                editButton.textContent = '💾 Enregistrer';
                editButton.classList.remove('edit-button-html');
                editButton.classList.add('save-button-html');
            }
        });
        // CANCEL button
        cancelButton.addEventListener('click', function() {
            contentDiv.innerHTML = originalContent;
            contentDiv.contentEditable = false;
            editToolbar.style.display = 'none';
            cancelButton.style.display = 'none';
            editButton.textContent = '✏️ Éditer';
            editButton.classList.remove('save-button-html');
            editButton.classList.add('edit-button-html');
        });
        // DELETE button
        deleteButton.addEventListener('click', function() {
            confirmDialog.style.display = 'flex';
        });
        // --- Custom Confirmation Dialog Logic ---
        const confirmDialog = document.querySelector('.confirm-dialog-overlay');
        const confirmBtn = document.querySelector('.dialog-confirm-btn');
        const cancelDialogBtn = document.querySelector('.dialog-cancel-btn');
        // CONFIRM button in dialog
        confirmBtn.addEventListener('click', function() {
            if (edit_handler_obj) {
                edit_handler_obj.deleteLesson();
            }
            confirmDialog.style.display = 'none';
        });
        // CANCEL button in dialog or clicking the overlay
        [cancelDialogBtn, confirmDialog].forEach(el => {
            el.addEventListener('click', function(e) {
                if (e.target === el) { // Ensure we're not clicking on a child element for the overlay
                    confirmDialog.style.display = 'none';
                }
            });
        });
        // --- Custom Tooltip Logic ---
        const tooltip = document.getElementById('custom-tooltip');
        if (tooltip) {
            document.querySelectorAll('[data-title]').forEach(elem => {
                elem.addEventListener('mousemove', e => {
                    tooltip.style.left = e.pageX + 15 + 'px';
                    tooltip.style.top = e.pageY + 15 + 'px';
                });
                elem.addEventListener('mouseenter', e => {
                    tooltip.innerHTML = elem.getAttribute('data-title');
                    tooltip.style.display = 'block';
                });
                elem.addEventListener('mouseleave', e => {
                    tooltip.style.display = 'none';
                });
            });
        }
    }
});