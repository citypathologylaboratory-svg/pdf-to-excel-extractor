const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const convertBtn = document.getElementById('convertBtn');
const statusArea = document.getElementById('statusArea');
const statusText = document.getElementById('statusText');
const browseLink = document.querySelector('.browse-link');

let selectedFile = null;

// File selection
fileInput.addEventListener('change', (e) => {
    selectedFile = e.target.files[0];
    if (selectedFile) {
        uploadArea.style.borderColor = '#764ba2';
        uploadArea.style.background = '#f0f1ff';
        uploadArea.querySelector('h2').textContent = selectedFile.name;
        uploadArea.querySelector('p').innerHTML = `<strong>${(selectedFile.size / 1024 / 1024).toFixed(2)} MB</strong> selected`;
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
    if (!selectedFile) {
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

// Convert button
convertBtn.addEventListener('click', async () => {
    if (!selectedFile) return;

    const format = document.querySelector('input[name="format"]:checked').value;
    
    // Show status
    document.querySelector('.upload-section').style.display = 'none';
    statusArea.classList.remove('hidden');
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('format', format);

    try {
        statusText.textContent = 'Processing your PDF...';
        
        const response = await fetch('/api/convert', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Conversion failed');
        }

        statusText.textContent = 'Downloading your file...';
        
        // Download the file
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = selectedFile.name.replace('.pdf', '_extracted.xlsx');
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        // Reset UI
        setTimeout(() => {
            statusArea.classList.add('hidden');
            document.querySelector('.upload-section').style.display = 'flex';
            selectedFile = null;
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
