const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const convertBtn = document.getElementById('convertBtn');
const statusArea = document.getElementById('statusArea');
const statusText = document.getElementById('statusText');
const browseLink = document.querySelector('.browse-link');

let selectedFiles = [];

// File selection
fileInput.addEventListener('change', (e) => {
    selectedFiles = Array.from(e.target.files);
    if (selectedFiles.length > 0) {
        uploadArea.style.borderColor = '#764ba2';
        uploadArea.style.background = '#f0f1ff';
        uploadArea.querySelector('h2').textContent = `${selectedFiles.length} file(s) selected`;
        const totalSize = selectedFiles.reduce((sum, f) => sum + f.size, 0);
        uploadArea.querySelector('p').innerHTML = `<strong>${(totalSize / 1024 / 1024).toFixed(2)} MB</strong> total`;
        convertBtn.disabled = false;
    }
});

// Upload area click
uploadArea.addEventListener('click', () => {
    fileInput.click();
});

// Browse link
browseLink.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.click();
});

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.style.borderColor = '#764ba2';
    uploadArea.style.background = '#f0f1ff';
});

uploadArea.addEventListener('dragleave', () => {
    if (selectedFiles.length === 0) {
        uploadArea.style.borderColor = '#667eea';
        uploadArea.style.background = '#f8f9ff';
    }
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        const event = new Event('change', { bubbles: true });
        fileInput.dispatchEvent(event);
    }
});

// Convert button - Handle multiple files
convertBtn.addEventListener('click', async () => {
    if (selectedFiles.length === 0) return;

    const format = document.querySelector('input[name="format"]:checked').value;
    
    // Show status
    document.querySelector('.upload-section').style.display = 'none';
    statusArea.classList.remove('hidden');
    
    try {
        statusText.textContent = `Processing ${selectedFiles.length} file(s)...`;
        
        // Process each file
        for (let i = 0; i < selectedFiles.length; i++) {
            const file = selectedFiles[i];
            statusText.textContent = `Processing file ${i + 1} of ${selectedFiles.length}: ${file.name}...`;
            
            const formData = new FormData();
            formData.append('file', file);
            formData.append('format', format);

            const response = await fetch('/api/convert', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(`File ${file.name}: ${error.error || 'Conversion failed'}`);
            }

            // Download the file
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = file.name.replace('.pdf', '_extracted.xlsx');
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            // Small delay between downloads
            await new Promise(resolve => setTimeout(resolve, 500));
        }

        statusText.textContent = `Successfully converted ${selectedFiles.length} file(s)!`;
        
        // Reset UI
        setTimeout(() => {
            statusArea.classList.add('hidden');
            document.querySelector('.upload-section').style.display = 'flex';
            selectedFiles = [];
            fileInput.value = '';
            uploadArea.style.borderColor = '#667eea';
            uploadArea.style.background = '#f8f9ff';
            uploadArea.querySelector('h2').textContent = 'Drop your PDF here';
            uploadArea.querySelector('p').innerHTML = 'or <span class="browse-link">browse your files</span>';
            convertBtn.disabled = true;
            
            // Re-attach browse link listener
            document.querySelector('.browse-link').addEventListener('click', (e) => {
                e.stopPropagation();
                fileInput.click();
            });
        }, 2000);
    } catch (error) {
        statusText.textContent = `Error: ${error.message}`;
        console.error('Error:', error);
        
        setTimeout(() => {
            statusArea.classList.add('hidden');
            document.querySelector('.upload-section').style.display = 'flex';
        }, 3000);
    }
});
