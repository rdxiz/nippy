function y() {
    function log(level, msg) {
        const timestamp = new Date().toISOString();
        let color;
        
        switch(level) {
            case 'info':
                color = 'color: #0090ff';
                break;
            case 'error':
                color = 'color: #ff0000';
                break;
            case 'debug':
                color = 'color: #00ff00'; 
                break;
            default:
                color = 'color: #000000';
        }
        
        console.log(`${timestamp} - %c${level.toUpperCase()}:`, color, msg);
    }
    // Drag to upload
    let getElementById = document.getElementById.bind(document);
    const endpoints = {
        upload: '/video/upload',
        updateVideoData: '/video/update',
        newVideo: '/video/new',
        videoStatus: '/video/status'
    };
    let uploadApp = getElementById('upload-app');
    let currentTab = 0;
    let chunkSize = parseInt(uploadApp.dataset.chunkSize);
    let maxVideoSize = parseInt(uploadApp.dataset.maxVideoSize);
    let currentChunk = 0;
    let totalChunks = 0;
    let uploadPercentage = 0;
    let thumbSelected = null;
    let fileToUpload = null;
    let videoId = null;
    let isPaused = false;
    let falied = false;
    const dropArea = getElementById('drag-to-upload');
    const uploadFilePicker = getElementById('upload-file-picker');
    const uploadInfo = getElementById('upload-info');
    const uploadArrow = getElementById('upload-arrow');
    const fileInput = getElementById('file-input');
    const uploadTitle = getElementById('upload-title');
    const uploadTitleText = getElementById('upload-title').innerText;
    let videoStatusInterval;
    uploadArrow.addEventListener('click', function () {
        fileInput.click();
    });


    fileInput.addEventListener('change', function () {
        uploader(fileInput.files[0]);
    });

    dropArea.addEventListener('dragover', function (e) {
        e.preventDefault();
        uploadArrow.className = "hovered";
    });

    dropArea.addEventListener('drop', function (e) {
        e.preventDefault();
        uploadArrow.className = "";
        const files = e.dataTransfer.files;
        uploader(files[0]);
    });

    dropArea.addEventListener('dragleave', function () {
        uploadArrow.className = "";
    });

    // Video uploader
    const videoUploadPercentage = getElementById('video-upload-percentage');
    const uploadProgressBar = getElementById('upload-progress-bar');
    const uploadProgressBarInside = getElementById('upload-progress-bar-inside');
    const videoPanel = getElementById('video-panel');
    const changes = getElementById('changes');
    const uploadVisibility = getElementById('visibility');
    const visibility = getElementById('id_visibility');
    // Statuses
    const startingUpload = getElementById('starting-upload');
    const videoUploading = getElementById('video-uploading');
    const videoProcessing = getElementById('video-processing');
    const uploadComplete = getElementById('upload-complete');
    const uploadCancel = getElementById('upload-cancel');
    const uploadFalied = getElementById('upload-falied');
    const videoTooLong = getElementById('video-too-long');
    const videoRetrying = getElementById('video-retrying');
    const videoLive = getElementById('video-live');
    const videoLiveLink = getElementById('video-live-link');
    let notSaved = getElementById('not-saved');
    let allChangesSaved = getElementById('all-changes-saved');
    // Form
    let videoUploadForm;
    // Buttons
    let btnCancel, btnSaveChanges;
    let uploadTries = 0;
    // Tabs 
    let btnBasicInfo, btnAdvancedSettings, basicInfo, advancedSettings;
    // Text
    const textSaved = getElementById('text-saved').innerText;
    const textSaveChanges = getElementById('btn-save-changes').innerText;


    

    function changeTab(tab) {
        if (tab == currentTab) return;
        currentTab = tab;
        if (currentTab == 0) {
            basicInfo.className = "grid";
            btnBasicInfo.className = btnBasicInfo.className + " selected";
            advancedSettings.className = "";
            btnAdvancedSettings.className = btnAdvancedSettings.className.replace(" selected", "");
        } else {
            advancedSettings.className = "grid";
            btnAdvancedSettings.className = btnAdvancedSettings.className + " selected";
            basicInfo.className = "";
            btnBasicInfo.className = btnBasicInfo.className.replace(" selected", "");
        }
    }

    function switchSaveStatus(saved) {
        isSaved = saved;
        if (saved) {
            btnSaveChanges.innerText = textSaved;
            btnSaveChanges.disabled = true;
            btnSaveChanges.className = "btn secondary";
            notSaved.className = "";
            allChangesSaved.className = "visible";
        } else {
            btnSaveChanges.innerText = textSaveChanges;
            btnSaveChanges.disabled = false;
            btnSaveChanges.className = "btn primary";
            notSaved.className = "text-error visible";
            allChangesSaved.className = "none";
        }
    }

    function registerUploaderEvents() {
        // Form
        videoUploadForm = getElementById('video-upload-form');
        // Buttons
        btnCancel = getElementById('btn-cancel');
        btnSaveChanges = getElementById('btn-save-changes');
        // Tabs 
        btnBasicInfo = getElementById('btn-basic-info');
        btnAdvancedSettings = getElementById('btn-advanced-settings');
        basicInfo = getElementById('basic-info');
        advancedSettings = getElementById('advanced-settings');
        notSaved = getElementById('not-saved');
        allChangesSaved = getElementById('all-changes-saved');
        btnBasicInfo.addEventListener('click', function () { changeTab(0) });
        btnAdvancedSettings.addEventListener('click', function () { changeTab(1) });
        const inputs = videoUploadForm.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener(input.type === 'checkbox' ? 'change' : 'input', function () { switchSaveStatus(false); });
        });
    }

    function registerThumbEvents() {
        
        const listImgs = document.querySelectorAll('#video-thumbs-list > img');
        listImgs.forEach((img, index) => {
            img.addEventListener('click', function() {
                listImgs.forEach(img => {
                    img.removeAttribute('data-selected');
                });
                this.setAttribute('data-selected', 'true');
                getElementById('id_thumbnail').value = index;
                thumbSelected = img.src;
                switchSaveStatus(false);
            });
        });
    }

    registerUploaderEvents();

    registerThumbEvents();


    
    btnSaveChanges.addEventListener('click', function () {
        if (falied) return;
        const formData = new FormData(videoUploadForm);
        formData.append('current_tab', currentTab);
        formData.append('video_id', videoId);

        fetch(endpoints.updateVideoData, {
            'method': 'POST',
            'body': formData
        })
        
            .then(response => {
                
                return Promise.all([response.status, response.text()]);
            })
            .then(([status, text]) => {
                const innerVideoThumb = document.getElementById('video-thumbs').innerHTML;

                videoPanel.innerHTML = text;
                getElementById('video-thumbs').innerHTML = innerVideoThumb;
                
                registerThumbEvents();

                registerUploaderEvents();
                if (status == 200) {
                    getElementById('video-title-text').innerText = getElementById('id_title').value;
                    switchSaveStatus(true);
                    if (thumbSelected) {
                        getElementById('video-thumbs-empty').style.display = 'none';
                        setThumbnailPreview(thumbSelected);
                    }
                    // getElementById('video-thumbs-empty').style.display = thumbSet ? 'block' : 'none';

                }
            })
            .catch(error => {
                log('error', error);
            });
    });

    btnCancel.addEventListener('click', function () {
        isPaused = true;
        videoUploading.style.display = "none";
        startingUpload.style.display = "none";
        videoLive.style.display = "none";
        btnCancel.style.display = "none";
        uploadCancel.style.display = "block";
        window.onbeforeunload = null;
    });

    function uploader(file) {
        switchSaveStatus(false);
        log('info', "Type: " + file.type);
        startingUpload.style.display = "inline";
        uploadFilePicker.style.display = "none";
        uploadInfo.style.display = "block";
        getElementById('video-title-text').innerText = file.name
        getElementById('id_title').value = file.name
        uploadTitle.innerText = uploadTitleText
            .replace(/{cnt_vi}/g, '0')
            .replace(/{total_vi}/g, '1');
        visibility.value = uploadVisibility.value;
        window.onbeforeunload = function () {
            return "";
        }
        fileToUpload = file;
        const formData = new FormData();
        formData.append('title', fileToUpload.name);
        fetch(endpoints.newVideo, {
            'method': 'POST',
            'body': formData
        })
            .then(response => {
                if (!response.ok) {
                    uploadFail();
                    throw new Error(response.status);
                    
                }
                return response.text();
            })
            .then(text => {
                if (isPaused) return;
                videoId = text;
                videoPanel.className = "visible";
                changes.className = "visible";
                totalChunks = Math.ceil(file.size / chunkSize);
                currentChunk = 0;
                startingUpload.style.display = "none";
                videoUploading.style.display = "inline";
                videoLive.style.display = "inline";
                url = `${location.protocol}//${location.host}/watch?v=${videoId}`
                videoLiveLink.innerText = url;
                videoLiveLink.href = url;
                btnSaveChanges.click();
                log('info', `[\u{1F4E4}] Starting upload...`);


                uploadNextChunk();
            })
            .catch(error => {
                log('error', error);
            });
       

    }

    function uploadFail(type) {
        falied = true;
        uploadProgressBarInside.style.width = '0%';
        videoUploadPercentage.innerText = '0%';
        videoRetrying.style.display = "none";
        startingUpload.style.display = "none";
        uploadCancel.style.display = "none";
        uploadComplete.style.display = "none";
        videoUploading.style.display = "none";
        videoProcessing.style.display = "none";
        videoLive.style.display = "none";
        log('error', 'Upload falied!' + (type === 1 ? ' Video too long.' : ''));

        if (type === 1) {
            videoTooLong.style.display = "block";
            
        } else {
            uploadFalied.style.display = "block";
        }
        btnCancel.style.display = "none";
        window.onbeforeunload = null;
        
    }

    function setPercentage(percentage) {
        uploadPercentage = percentage;
        uploadProgressBarInside.style.width = uploadPercentage + '%';
        videoUploadPercentage.innerText = uploadPercentage + '%';
    }

    function setThumbnailPreview(thumbnailUrl) {
        getElementById('video-preview').innerHTML = '';
        getElementById('video-preview').style.backgroundImage = 'url("' + thumbnailUrl + '")';
                
    }
    function fetchVideoStatus (){
        const formData = new FormData();
        formData.append('video_id', videoId);
        fetch(endpoints.videoStatus, {
            'method': 'POST',
            'body': formData
        })
            .then(response => {
                if (!response.ok) {
                    clearInterval(videoStatusInterval);
                    uploadFail();
                    throw new Error(response.status);
                    
                }
                return response.json();
            })
            .then(json => {

                let progress = json.progress;
                log('info', `Processing - ${progress}%`);

                if (progress > 100) {
                    progress= 90;
                }
                setPercentage(75 + Math.round(progress/4));
                if (json.status === 3) {
                    videoProcessing.style.display = "none";
                    uploadComplete.style.display = "inline";
                    for (let i = 0; i < json.thumbnail.length; i++) {
                        document.getElementById('thumb-item-' + i).src = json.thumbnail[i];
                    }
                    thumbSet = true;
                    getElementById('video-thumbs-list').style.display = 'flex';
                    getElementById('video-thumbs-empty').style.display = 'none';
                    
                    setThumbnailPreview(json.thumbnail[0]);
                    thumbSelected = json.thumbnail[0];
                    clearInterval(videoStatusInterval);
                    setPercentage(100);
                    log('info', `Processing - 100%`);
                    log('info', `Finished processing! :D`);

                } else if (json.status === 4) {
                    clearInterval(videoStatusInterval);
                    uploadFail();
                } else if (json.status === 5) {
                    clearInterval(videoStatusInterval);
                    uploadFail(1);
                }
            })
            .catch(error => {
                log('error', error);
                clearInterval(videoStatusInterval);
                uploadFail();
            });
    }
    function uploadNextChunk() {
        if (isPaused) return;
        if (currentChunk >= totalChunks) {
            videoUploading.style.display = "none";
            videoProcessing.style.display = "inline";
            btnCancel.style.display = "none";
            window.onbeforeunload = null;
            uploadTitle.innerText = uploadTitleText
                .replace(/{cnt_vi}/g, '1')
                .replace(/{total_vi}/g, '1');
            log('info', `[\u{1F4E4}] Upload complete!`);
            
            videoStatusInterval = setInterval(fetchVideoStatus, 2000); 
            return;
        }
        
        const start = currentChunk * chunkSize;

        const end = Math.min(fileToUpload.size, start + chunkSize);
        const chunk = fileToUpload.slice(start, end);
        const formData = new FormData();
        formData.append('file', chunk);
        formData.append('chunk', currentChunk);
        formData.append('total_chunks', totalChunks);
        formData.append('video_id', videoId);

        const xhr = new XMLHttpRequest();
        xhr.open('POST', endpoints.upload, true);

        xhr.upload.addEventListener('progress', function (e) {
            if (e.lengthComputable) {
                const percentage = ((currentChunk + (e.loaded / e.total)) / totalChunks);
                const percentComplete = Math.round(percentage * 75);
                log('info', `[\u{1F4E4}] Uploading: ${Math.round(percentage * 100)}%`);
                
                setPercentage(percentComplete);
            }
        });

        xhr.addEventListener('load', function () {
            if (xhr.status < 400) {
                videoUploading.style.display = "block";
                videoRetrying.style.display = "none";
                uploadTries = 0;
                currentChunk++;
                uploadNextChunk();
            } else {
                if (xhr.status === 413){
                    uploadFail(1);
                } else {
                    if (uploadTries <= 5) {
                        videoUploading.style.display = "none";
                        videoRetrying.style.display = "inline";
                        uploadTries++;
                        uploadNextChunk();
                    } else {
                        uploadFail(0);
                    }
                }
            }
        });

        xhr.addEventListener('error', function () {
            log('error', `${xhr.status} status code`);

            uploadFail();
        });

        xhr.send(formData);
    }
}
y();