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

// --- Summernote Integration ---
var isEditMode = false;
var originalContent = '';
var summernoteInitialized = false;

// Fonction pour insérer une image dans Summernote (évite les callbacks QWebChannel)
function insertImageIntoSummernote(imageUrl) {
    if (window.$ && $.fn && $.fn.summernote) {
        $('#summernote').summernote('insertImage', imageUrl);
        print('insertImageIntoSummernote appelée avec rel_path : ' + imageUrl);
    }
}

// Fonction pour gérer les erreurs d'upload d'image
function handleImageUploadError(errorMessage) {
    console.error("Erreur de téléchargement d'image:", errorMessage);
}

function switchToEditMode() {
    console.log('=== switchToEditMode called ===');
    console.log('isEditMode before:', isEditMode);
    
    if (isEditMode) {
        console.log('Already in edit mode, doing nothing');
        return;
    }
    
    isEditMode = true;
    console.log('isEditMode after:', isEditMode);
    
    // Sauvegarder le contenu original
    const readMode = document.getElementById('read-mode');
    if (readMode) {
        originalContent = readMode.innerHTML;
        console.log('Original content saved for cancellation');
    }
    
    // Changer le bouton Éditer en Sauvegarder
    const editButton = document.querySelector('.edit-button-html');
    if (editButton) {
        editButton.textContent = '💾 Sauvegarder';
        editButton.classList.remove('edit-button-html');
        editButton.classList.add('save-button-html');
        console.log('Button changed to Sauvegarder');
    }

    // Afficher les boutons Annuler et Supprimer
    const cancelButton = document.querySelector('.cancel-button-html');
    const deleteButton = document.querySelector('.delete-button-html');
    if (cancelButton) cancelButton.style.display = 'inline-block';
    if (deleteButton) deleteButton.style.display = 'inline-block';
    
    // Initialiser Summernote seulement si pas encore fait
    if (!summernoteInitialized) {
        console.log('Initializing Summernote for the first time');
        // Afficher Summernote mais garder le contenu visible pendant l'initialisation
        document.getElementById('edit-mode').style.display = 'block';
        
        waitForSummernote(function() {
            $('#summernote').summernote({
                lang: 'fr-FR',
                height: 300,
                className: 'note-frame-dark',
                toolbar: [
                    ['style', ['style']],
                    ['font', ['bold', 'italic', 'underline', 'clear', 'strikethrough', 'superscript', 'subscript']],
                    ['fontsize', ['fontsize']],
                    ['color', ['color']],
                    ['para', ['ul', 'ol', 'paragraph']],
                    ['height', ['height']],
                    ['insert', ['picture', 'table', 'hr']],
                    ['view', ['codeview']]
                ],
                dialogsInBody: true,
                disableDragAndDrop: false,
                popover: {
                    image: [
                        ['resize', ['resizeFull', 'resizeHalf', 'resizeQuarter', 'resizeNone']],
                        ['remove', ['removeMedia']]
                    ]
                },
                callbacks: {
                    onImageUpload: function(files) {
                        var editor = $('#summernote');
                        // var lastRange = editor.summernote('createRange'); // Supprimer cette ligne

                        for (const file of files) {
                            const filename = file.name;
                            // Le chemin doit être relatif à la base de la page (src/), donc 'html/...'
                            var rel_path_check = 'html/data/images/' + filename;
                            var img = new Image();
                            img.onload = function() {
                                // L'image existe déjà, on l'insère directement
                                editor.summernote('insertImage', rel_path_check);
                            };
                            img.onerror = function() {
                                // L'image n'existe pas, on tente l'upload via Python
                                console.log("js/upload: L'image n'existe pas localement. Début de l'upload pour :", filename);
                                const reader = new FileReader();
                                reader.onload = function(e) {
                                    const base64data = e.target.result;
                                    if (window.edit_handler_obj && window.edit_handler_obj.imageUploadCallback) {
                                        try {
                                            // Appel asynchrone, la valeur de retour est une promesse
                                            console.log("js/upload: Appel de la fonction Python imageUploadCallback...");
                                            window.edit_handler_obj.imageUploadCallback(filename, base64data).then(rel_path_upload => {
                                                console.log("js/upload: Promesse Python résolue. Chemin reçu :", rel_path_upload);
                                                if (rel_path_upload) {
                                                    // Insérer l'image uniquement si le chemin est valide
                                                    console.log("js/upload: Insertion de l'image dans Summernote avec src :", rel_path_upload);
                                                    editor.summernote('insertImage', rel_path_upload);
                                                } else {
                                                    console.error('Image upload failed: Empty path returned from Python.');
                                                }
                                            }).catch(error => {
                                                console.error("js/upload: Erreur dans la promesse de imageUploadCallback :", error);
                                            });
                                        
                                        } catch (error) {
                                            console.error("Error calling imageUploadCallback directly:", error);
                                        }
                                    } else {
                                        console.error('Aucun callback imageUploadCallback disponible, image non insérée.');
                                    }
                                };
                                reader.readAsDataURL(file);
                            };
                            // Déclenche la vérification d'existence
                            img.src = rel_path_check; // Tente de charger l'image pour vérifier son existence
                        }
                    }
                }
            });
            
            // Charger le contenu dans Summernote
            $('#summernote').summernote('code', originalContent);
            
            // Maintenant que Summernote est prêt, cacher le contenu en lecture
            document.getElementById('read-mode').style.display = 'none';
            
            // Forcer les couleurs de la palette après un délai
            setTimeout(function() {
                // forceSummernoteColors(); // Removed as per edit hint
                console.log('Colors forced for Summernote palette');
            }, 500);
            
            summernoteInitialized = true;
            console.log('Summernote initialized successfully');
        });
    } else {
        console.log('Summernote already initialized, switching display');
        // Summernote déjà initialisé, juste basculer l'affichage
        document.getElementById('edit-mode').style.display = 'block';
        document.getElementById('read-mode').style.display = 'none';
        $('#summernote').summernote('code', originalContent);
    }
}

function switchToReadMode() {
    console.log('=== switchToReadMode called ===');
    console.log('isEditMode before:', isEditMode);
    
    if (!isEditMode) {
        console.log('Not in edit mode, doing nothing');
        return;
    }
    
    isEditMode = false;
    console.log('isEditMode after:', isEditMode);
    
    // Changer le bouton Sauvegarder en Éditer
    const saveButton = document.querySelector('.save-button-html');
    if (saveButton) {
        saveButton.textContent = '✏️ Éditer';
        saveButton.classList.remove('save-button-html');
        saveButton.classList.add('edit-button-html');
        console.log('Button changed to Éditer');
    }

    // Cacher les boutons Annuler et Supprimer
    const cancelButton = document.querySelector('.cancel-button-html');
    const deleteButton = document.querySelector('.delete-button-html');
    if (cancelButton) cancelButton.style.display = 'none';
    if (deleteButton) deleteButton.style.display = 'none';
    
    document.getElementById('read-mode').style.display = 'block';
    document.getElementById('edit-mode').style.display = 'none';
    
    // Mettre à jour le contenu affiché
    if (summernoteInitialized) {
        var newContent = $('#summernote').summernote('code');
        document.getElementById('read-mode').innerHTML = newContent;
        originalContent = newContent;
    }
}

function saveContent() {
    console.log('=== saveContent called ===');
    console.log('isEditMode:', isEditMode, 'summernoteInitialized:', summernoteInitialized);
    
    if (!isEditMode || !summernoteInitialized) {
        console.log('Cannot save: not in edit mode or Summernote not initialized');
        return;
    }
    
    var newContent = $('#summernote').summernote('code');
    console.log('Content to save:', newContent.substring(0, 100) + '...');
    
    if (window.edit_handler_obj && window.edit_handler_obj.saveContent) {
        try {
            window.edit_handler_obj.saveContent(newContent);
            console.log('Content saved via Python handler');
        } catch (error) {
            console.error('Error calling saveContent:', error);
        }
    } else {
        console.error('edit_handler_obj or saveContent not available');
    }
    
    // Retourner en mode lecture après sauvegarde
    switchToReadMode();
}

function waitForSummernote(callback) {
    if (window.$ && $.fn && $.fn.summernote) {
        callback();
    } else {
        setTimeout(function() { waitForSummernote(callback); }, 100);
    }
}

// --- Main Logic ---
var print_handler_obj;
var edit_handler_obj;

// Initialiser QWebChannel pour la hauteur automatique avec gestion d'erreur
function initializeQWebChannel() {
    try {
        if (typeof qt !== 'undefined' && qt.webChannelTransport) {
            new QWebChannel(qt.webChannelTransport, function(channel) {
                console.log('QWebChannel initialized successfully');
                
                // Assign channel objects
                var height_reporter = channel.objects.height_reporter_obj;
                print_handler_obj = channel.objects.print_handler_obj;
                edit_handler_obj = channel.objects.edit_handler_obj;
                
                console.log('Channel objects assigned:', {
                    height_reporter: !!height_reporter,
                    print_handler: !!print_handler_obj,
                    edit_handler: !!edit_handler_obj
                });
                
                // Setup height observer
                const wrapper = document.getElementById('content-wrapper');
                if (wrapper && height_reporter) {
                    const resizeObserver = new ResizeObserver(entries => {
                        // Use scrollHeight for a more reliable total height calculation, including margins and overflow.
                        // Add a small buffer to prevent scrollbars from appearing due to sub-pixel rendering.
                        height_reporter.setHeight(wrapper.scrollHeight + 20);
                    });
                    resizeObserver.observe(wrapper);
                    console.log('Height observer setup complete');
                }
            });
        } else {
            console.log('qt.webChannelTransport not available, skipping QWebChannel initialization');
        }
    } catch (error) {
        console.error('Error initializing QWebChannel:', error);
    }
}

// Attendre que le DOM soit chargé avant d'initialiser
$(document).ready(function() {
    console.log('=== DOM Ready ===');
    
    // Initialiser QWebChannel
    initializeQWebChannel();
    
    // FORCER l'état initial
    isEditMode = false;
    summernoteInitialized = false;
    console.log('Initial state set - isEditMode:', isEditMode, 'summernoteInitialized:', summernoteInitialized);
    
    // Store original content
    const readMode = document.getElementById('read-mode');
    if (readMode) {
        originalContent = readMode.innerHTML;
        console.log('Original content stored:', originalContent.substring(0, 100) + '...');
    }
    
    // --- Event Listeners Setup ---
    const editButton = document.querySelector('.edit-button-html');
    const cancelButton = document.querySelector('.cancel-button-html');
    const savedNotification = document.querySelector('.saved-notification');
    const deleteButton = document.querySelector('.delete-button-html');

    // Cacher les boutons Annuler et Supprimer au démarrage
    if (cancelButton) cancelButton.style.display = 'none';
    if (deleteButton) deleteButton.style.display = 'none';
    
    // Observer pour détecter l'ouverture des palettes de couleurs
    // Removed as per edit hint
    
    // Observer les changements dans le document
    // Removed as per edit hint
    
    console.log('Buttons found:', {
        editButton: !!editButton,
        cancelButton: !!cancelButton,
        deleteButton: !!deleteButton
    });
    
    if (editButton && cancelButton && deleteButton) {
        // EDIT/SAVE button - LOGIQUE CORRIGÉE
        editButton.addEventListener('click', function(e) {
            console.log('=== Edit button clicked ===');
            console.log('isEditMode:', isEditMode, 'button text:', this.textContent, 'button class:', this.className);
            e.preventDefault();
            e.stopPropagation();
            
            if (isEditMode) {
                console.log('Currently in edit mode, saving...');
                // SAVE
                saveContent();
                // Show saved notification
                if (savedNotification) {
                    savedNotification.style.opacity = '1';
                    savedNotification.style.transform = 'translateY(0)';
                    setTimeout(() => {
                        savedNotification.style.opacity = '0';
                        savedNotification.style.transform = 'translateY(-10px)';
                    }, 2000);
                }
            } else {
                console.log('Currently in read mode, switching to edit...');
                // START EDIT - PAS DE SAUVEGARDE AUTOMATIQUE
                switchToEditMode();
            }
        });
        
        // CANCEL button
        cancelButton.addEventListener('click', function(e) {
            console.log('=== Cancel button clicked ===');
            e.preventDefault();
            e.stopPropagation();
            
            if (isEditMode) {
                // Restaurer le contenu original
                if (summernoteInitialized) {
                    $('#summernote').summernote('code', originalContent);
                }
                switchToReadMode();
                console.log('Edit mode cancelled, original content restored');
            }
        });
        
        // DELETE button
        deleteButton.addEventListener('click', function(e) {
            console.log('=== Delete button clicked ===');
            e.preventDefault();
            e.stopPropagation();
            const confirmDialog = document.querySelector('.confirm-dialog-overlay');
            if (confirmDialog) {
                confirmDialog.style.display = 'flex';
            }
        });
        
        // --- Custom Confirmation Dialog Logic ---
        const confirmDialog = document.querySelector('.confirm-dialog-overlay');
        const confirmBtn = document.querySelector('.dialog-confirm-btn');
        const cancelDialogBtn = document.querySelector('.dialog-cancel-btn');
        
        // CONFIRM button in dialog
        if (confirmBtn) {
            confirmBtn.addEventListener('click', function() {
                if (window.edit_handler_obj && window.edit_handler_obj.deleteLesson) {
                    try {
                        window.edit_handler_obj.deleteLesson();
                    } catch (error) {
                        console.error('Error calling deleteLesson:', error);
                    }
                }
                if (confirmDialog) {
                    confirmDialog.style.display = 'none';
                }
            });
        }
        
        // CANCEL button in dialog or clicking the overlay
        if (confirmDialog && cancelDialogBtn) {
            [cancelDialogBtn, confirmDialog].forEach(el => {
                el.addEventListener('click', function(e) {
                    if (e.target === el) { // Ensure we're not clicking on a child element for the overlay
                        confirmDialog.style.display = 'none';
                    }
                });
            });
        }
        
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

// Ajout du bouton floatCenter custom dans Summernote
if ($.summernote) {
    $.summernote.plugins['floatCenter'] = function (context) {
        var ui = $.summernote.ui;
        context.memo('button.floatCenter', function () {
            return ui.button({
                className: 'note-btn',
                contents: '<i class="note-icon-align-center"/>',
                tooltip: 'Centrer',
                click: function () {
                    var img = context.invoke('restoreTarget');
                    if (img && $(img).is('img')) {
                        $(img).css({
                            display: 'block',
                            float: '',
                            marginLeft: 'auto',
                            marginRight: 'auto'
                        });
                    } else {
                        console.warn('Aucune image sélectionnée pour centrage.');
                    }
                }
            }).render();
        });
    };
}

// --- Summernote: Forçage dynamique des titres et boutons en blanc dans les popins ---
function forceSummernoteDialogColors() {
    // Titre popin image
    $(".note-image-dialog .modal-title, .note-image-dialog .note-modal-title, .note-image-dialog label, .note-image-dialog span, .note-image-dialog .note-form-label").css("color", "#fff");
    // Titres palette couleur
    $(".note-color .note-color-title, .note-color .note-color-row .note-color-title, .note-color .note-color-row label, .note-color .note-color-row span").css("color", "#fff");
    // Boutons palette couleur
    $(".note-color-row .note-color-reset, .note-color-row .note-color-select, .note-color-row .note-color-transparent").css({
        background: "#222",
        color: "#fff",
        border: "1px solid #444"
    });
}

// Hook sur l'ouverture des modales Summernote
$(document).on('shown.bs.modal', function(e) {
    forceSummernoteDialogColors();
});
// Hook sur l'ouverture de la palette couleur
$(document).on('click', '.note-color-btn', function() {
    setTimeout(forceSummernoteDialogColors, 50);
});