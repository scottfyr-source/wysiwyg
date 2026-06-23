// State Management
let selectedFiles = [];
let outputFolder = "";
let selectedFormat = "jpg";
let isConverting = false;

// DOM Elements
const inputWidth = document.getElementById("input-width");
const inputHeight = document.getElementById("input-height");
const selectScaleMode = document.getElementById("select-scale-mode");
const bgColorGroup = document.getElementById("bg-color-group");
const colorPickerBg = document.getElementById("color-picker-bg");
const colorHexBg = document.getElementById("color-hex-bg");
const sliderQuality = document.getElementById("slider-quality");
const qualityVal = document.getElementById("quality-val");
const qualityCard = document.getElementById("quality-card");
const inputOutputDir = document.getElementById("input-output-dir");
const badgeTotalFiles = document.getElementById("badge-total-files");

const progressContainer = document.getElementById("progress-container");
const progressStatusLabel = document.getElementById("progress-status-label");
const progressPercentLabel = document.getElementById("progress-percent-label");
const progressBarFill = document.getElementById("progress-bar-fill");

const imageDropzone = document.getElementById("image-dropzone");
const queuePanel = document.getElementById("queue-panel");
const queueTbody = document.getElementById("queue-tbody");
const terminalLogger = document.getElementById("terminal-logger");
const btnConvertTrigger = document.getElementById("btn-convert-trigger");

// Initialize listeners on load
window.addEventListener("DOMContentLoaded", () => {
    initFormatSelectors();
    initPresetButtons();
    initBgColorSync();
    initQualitySlider();
    initDropzoneEvents();
    
    // Default visibility states
    toggleBgColorVisibility();
    toggleQualityVisibility();
});

// 1. Format Selectors
function initFormatSelectors() {
    const formatButtons = document.querySelectorAll(".format-btn");
    formatButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            if (isConverting) return;
            formatButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            selectedFormat = btn.dataset.format;
            toggleQualityVisibility();
            toggleBgColorVisibility();
            addLogEntry(`Output format set to ${selectedFormat.toUpperCase()}`, "info");
        });
    });
}

// 2. Sizing Presets
function initPresetButtons() {
    const presetButtons = document.querySelectorAll(".preset-btn");
    presetButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            if (isConverting) return;
            presetButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            if (btn.id === "btn-custom-size") {
                addLogEntry("Custom size mode active. Input dimensions manually.", "info");
                return;
            }
            
            const w = btn.dataset.width;
            const h = btn.dataset.height;
            inputWidth.value = w;
            inputHeight.value = h;
            addLogEntry(`Dimensions preset set to ${w} × ${h}`, "info");
        });
    });

    // Reset preset buttons if user manually edits input fields
    [inputWidth, inputHeight].forEach(input => {
        input.addEventListener("input", () => {
            presetButtons.forEach(b => b.classList.remove("active"));
            document.getElementById("btn-custom-size").classList.add("active");
        });
    });
}

// 3. Background Color Sync (Color Picker & Hex Textfield)
function initBgColorSync() {
    colorPickerBg.addEventListener("input", (e) => {
        colorHexBg.value = e.target.value.toUpperCase();
    });
    colorHexBg.addEventListener("input", (e) => {
        let val = e.target.value;
        if (!val.startsWith("#")) val = "#" + val;
        if (val.length === 7 && /^#[0-9A-F]{6}$/i.test(val)) {
            colorPickerBg.value = val;
        }
    });

    // Also toggle color group if scaling mode is changed
    selectScaleMode.addEventListener("change", () => {
        toggleBgColorVisibility();
        addLogEntry(`Scale mode changed to: ${selectScaleMode.options[selectScaleMode.selectedIndex].text}`, "info");
    });
}

function toggleBgColorVisibility() {
    // Show bg color picker if scaling mode is 'fit' OR if target format is 'jpg/jpeg'
    const scaleMode = selectScaleMode.value;
    if (scaleMode === "fit" || selectedFormat === "jpg") {
        bgColorGroup.style.display = "flex";
    } else {
        bgColorGroup.style.display = "none";
    }
}

// 4. Quality Slider
function initQualitySlider() {
    sliderQuality.addEventListener("input", (e) => {
        qualityVal.textContent = e.target.value + "%";
    });
}

function toggleQualityVisibility() {
    // Quality is only applicable for JPG or WEBP formats (lossy compression)
    if (selectedFormat === "jpg" || selectedFormat === "webp") {
        qualityCard.style.display = "flex";
    } else {
        qualityCard.style.display = "none";
    }
}

// 5. Dropzone & File Browser Triggers
function initDropzoneEvents() {
    // Click on dropzone area triggers select file
    imageDropzone.addEventListener("click", (e) => {
        // Prevent click trigger if they clicked child buttons
        if (e.target.tagName !== "BUTTON" && !e.target.closest("button")) {
            chooseFiles();
        }
    });

    // HTML5 Drag and Drop handlers
    ["dragenter", "dragover"].forEach(eventName => {
        imageDropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            imageDropzone.classList.add("dragover");
        }, false);
    });

    ["dragleave", "drop"].forEach(eventName => {
        imageDropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            imageDropzone.classList.remove("dragover");
        }, false);
    });

    imageDropzone.addEventListener("drop", (e) => {
        // Direct drop of local files in pywebview is restricted or has variations.
        // We warn the user to use the file buttons if they drop without success.
        showNotification("Please use the 'Select Files' or 'Select Folder' buttons to add images.", "info");
    });
}

// 6. PyWebview Bridges (Calling Python Backend API)
function chooseFiles() {
    if (isConverting) return;
    if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.select_files_dialog("Select Image Files").then(response => {
            if (response.status === "success" && response.files.length > 0) {
                addFilesToQueue(response.files);
            }
        });
    } else {
        showNotification("Python backend not connected.", "error");
    }
}

function chooseFolder() {
    if (isConverting) return;
    if (window.pywebview && window.pywebview.api) {
        addLogEntry("Scanning folder for image files...", "info");
        window.pywebview.api.select_folder_dialog("Select Source Image Folder").then(response => {
            if (response.status === "success") {
                if (response.files.length > 0) {
                    addLogEntry(`Found ${response.files.length} images in folder: ${response.path}`, "success");
                    addFilesToQueue(response.files);
                } else {
                    addLogEntry("No valid image files found in folder.", "warn");
                    showNotification("No image files (.png, .jpg, .jpeg, .webp, .bmp, .gif, .tiff) found.", "error");
                }
            }
        });
    } else {
        showNotification("Python backend not connected.", "error");
    }
}

function chooseOutputDir() {
    if (isConverting) return;
    if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.select_output_folder_dialog("Select Output Folder").then(path => {
            if (path) {
                outputFolder = path;
                inputOutputDir.value = path;
                addLogEntry(`Output directory set to: ${path}`, "info");
                showNotification("Destination folder set.", "success");
            }
        });
    }
}

// 7. Queue Operations
function addFilesToQueue(files) {
    // Filter duplicates out (based on file path)
    const existingPaths = new Set(selectedFiles.map(f => f.path));
    let addedCount = 0;
    
    files.forEach(file => {
        if (!existingPaths.has(file.path)) {
            selectedFiles.push(file);
            addedCount++;
        }
    });

    if (addedCount > 0) {
        showNotification(`Added ${addedCount} images to queue.`, "success");
        renderQueueTable();
    } else {
        showNotification("Selected files are already in queue.", "info");
    }
}

function renderQueueTable() {
    const total = selectedFiles.length;
    badgeTotalFiles.textContent = `${total} Files Queue`;

    if (total > 0) {
        queuePanel.style.display = "block";
        queueTbody.innerHTML = "";
        
        selectedFiles.forEach((file, index) => {
            const tr = document.createElement("tr");
            tr.id = `queue-row-${index}`;
            tr.innerHTML = `
                <td style="white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 400px;" title="${file.path}">
                    ${file.name}
                </td>
                <td style="color: var(--color-text-muted); font-weight: 500;">
                    ${file.size}
                </td>
                <td style="text-align: right;">
                    <span class="status-badge ready" id="status-badge-${index}"><i class="fa-solid fa-clock"></i> Ready</span>
                </td>
            `;
            queueTbody.appendChild(tr);
        });
    } else {
        queuePanel.style.display = "none";
        queueTbody.innerHTML = "";
    }
}

function clearQueue() {
    if (isConverting) return;
    selectedFiles = [];
    renderQueueTable();
    addLogEntry("Queue cleared.", "info");
    showNotification("Queue cleared.", "info");
}

// 8. Conversion Execution
function runConversion() {
    if (isConverting) return;
    if (selectedFiles.length === 0) {
        showNotification("Please add images to the batch queue first.", "error");
        addLogEntry("Cannot start: queue is empty.", "error");
        return;
    }

    const width = parseInt(inputWidth.value);
    const height = parseInt(inputHeight.value);
    
    if (isNaN(width) || width <= 0 || isNaN(height) || height <= 0) {
        showNotification("Please input valid target dimensions.", "error");
        return;
    }

    // Set converting state
    isConverting = true;
    btnConvertTrigger.disabled = true;
    btnConvertTrigger.classList.add("disabled");
    btnConvertTrigger.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> CONVERTING...`;
    
    // Set all file statuses in UI to 'Ready' initially
    selectedFiles.forEach((_, idx) => {
        const badge = document.getElementById(`status-badge-${idx}`);
        if (badge) {
            badge.className = "status-badge ready";
            badge.innerHTML = `<i class="fa-solid fa-clock"></i> Ready`;
        }
    });

    // Reset progress UI
    progressContainer.style.display = "block";
    updateProgress(0, selectedFiles.length, "Initializing conversion...", "info");

    // Gather settings
    const filePaths = selectedFiles.map(f => f.path);
    const scaleMode = selectScaleMode.value;
    const quality = sliderQuality.value;
    const bgColor = colorHexBg.value;
    
    // If outputFolder is empty, default to the folder of the first image in the queue
    let finalOutputDir = outputFolder;
    if (!finalOutputDir && selectedFiles.length > 0) {
        // Get parent directory of the first file in queue
        const firstPath = selectedFiles[0].path;
        finalOutputDir = firstPath.substring(0, firstPath.lastIndexOf('\\'));
        addLogEntry(`Output directory not specified. Defaulting to first image parent: ${finalOutputDir}`, "warn");
    }

    // Send call to Python API
    if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.start_batch_conversion(
            filePaths,
            finalOutputDir,
            selectedFormat,
            width,
            height,
            scaleMode,
            quality,
            bgColor
        );
    } else {
        isConverting = false;
        btnConvertTrigger.disabled = false;
        btnConvertTrigger.innerHTML = `<i class="fa-solid fa-circle-play"></i> BATCH CONVERT`;
        showNotification("Backend not available.", "error");
    }
}

// 9. Callbacks called from Python Backend Thread
function addLogEntry(message, status = "info") {
    const entry = document.createElement("div");
    entry.className = `log-entry ${status}`;
    
    // Format timestamp
    const now = new Date();
    const timeStr = `[${now.toTimeString().split(' ')[0]}]`;
    entry.innerHTML = `<span style="color: var(--color-text-muted); font-size: 11px; margin-right: 8px;">${timeStr}</span>${message}`;
    
    terminalLogger.appendChild(entry);
    
    // Auto-scroll log to bottom
    terminalLogger.scrollTop = terminalLogger.scrollHeight;
}

function updateProgress(current, total, message, status = "info") {
    // Show progress bar
    progressContainer.style.display = "block";
    progressStatusLabel.textContent = message;

    const percent = total > 0 ? Math.round((current / total) * 100) : 0;
    progressPercentLabel.textContent = `${percent}%`;
    progressBarFill.style.width = `${percent}%`;

    // Highlight active row in file queue
    if (current < total) {
        // The current index is the active one processing
        const prevIdx = current - 1;
        if (prevIdx >= 0) {
            const prevBadge = document.getElementById(`status-badge-${prevIdx}`);
            if (prevBadge && !prevBadge.classList.contains("success") && !prevBadge.classList.contains("failed")) {
                prevBadge.className = "status-badge success";
                prevBadge.innerHTML = `<i class="fa-solid fa-circle-check"></i> Done`;
            }
        }

        const activeBadge = document.getElementById(`status-badge-${current}`);
        if (activeBadge) {
            activeBadge.className = "status-badge processing";
            activeBadge.innerHTML = `<i class="fa-solid fa-rotate fa-spin"></i> Active`;
            
            // Scroll table to active row
            const activeRow = document.getElementById(`queue-row-${current}`);
            if (activeRow) {
                activeRow.scrollIntoView({ behavior: "smooth", block: "nearest" });
            }
        }
    }
}

function onConversionComplete(successCount, failCount) {
    isConverting = false;
    btnConvertTrigger.disabled = false;
    btnConvertTrigger.classList.remove("disabled");
    btnConvertTrigger.innerHTML = `<i class="fa-solid fa-circle-play"></i> BATCH CONVERT`;

    // Set remaining queue badges to Done or Failed
    selectedFiles.forEach((_, idx) => {
        const badge = document.getElementById(`status-badge-${idx}`);
        if (badge && badge.classList.contains("processing")) {
            badge.className = "status-badge success";
            badge.innerHTML = `<i class="fa-solid fa-circle-check"></i> Done`;
        }
    });

    if (failCount === 0) {
        showNotification(`Batch finished! Converted ${successCount} images successfully.`, "success");
    } else {
        showNotification(`Batch completed with errors. ${successCount} Succeeded, ${failCount} Failed.`, "error");
    }
}

function clearConsoleLog() {
    terminalLogger.innerHTML = `<div class="log-entry info">Terminal cleared.</div>`;
}

// 10. Utility UI functions
function showNotification(message, type = "info") {
    const container = document.getElementById("notification-box");
    const toast = document.createElement("div");
    toast.className = `notification-toast ${type}`;
    
    let icon = "fa-circle-info";
    if (type === "success") icon = "fa-circle-check";
    if (type === "error") icon = "fa-circle-exclamation";
    
    toast.innerHTML = `<i class="fa-solid ${icon}"></i><span>${message}</span>`;
    container.appendChild(toast);

    // Auto-remove after 4 seconds
    setTimeout(() => {
        toast.style.animation = "slideIn 0.3s reverse forwards";
        setTimeout(() => {
            if (toast.parentNode) {
                container.removeChild(toast);
            }
        }, 300);
    }, 4000);
}

function exitApp() {
    if (window.pywebview && window.pywebview.api) {
        window.pywebview.api.exit_app();
    } else {
        window.close();
    }
}

// Restore persistent folders from backend when pywebview is ready
window.addEventListener('pywebviewready', () => {
    if (window.pywebview && window.pywebview.api && window.pywebview.api.get_saved_folders) {
        window.pywebview.api.get_saved_folders().then(config => {
            if (config && config.last_output_dir) {
                outputFolder = config.last_output_dir;
                inputOutputDir.value = config.last_output_dir;
                addLogEntry(`Restored last output folder: ${config.last_output_dir}`, "info");
            }
        }).catch(err => {
            console.error("Failed to restore saved folders:", err);
        });
    }
});
