
document.addEventListener('DOMContentLoaded', function() {
    // 初始化预览容器
    const previewContainer = document.getElementById('preview-container');
    const imageUploadInput = document.getElementById('imageUpload');
    
    if (!previewContainer || !imageUploadInput) return;

    const previewRow = document.createElement('div');
    previewRow.className = 'd-flex flex-wrap gap-2 mb-3 upload-preview';
    previewContainer.appendChild(previewRow);

    // 处理文件上传预览
    imageUploadInput.addEventListener('change', function(e) {
        const files = e.target.files;
        if (!files || files.length === 0) return;

        // 清空现有预览
        while (previewRow.firstChild) {
            previewRow.removeChild(previewRow.firstChild);
        }

        for (let i = 0; i < files.length; i++) {
            const reader = new FileReader();
            reader.onload = function(event) {
                const preview = document.createElement('img');
                preview.src = event.target.result;
                preview.className = 'img-thumbnail';
                preview.style.maxHeight = '150px';
                previewRow.appendChild(preview);
            };
            reader.readAsDataURL(files[i]);
        }
    });
});
