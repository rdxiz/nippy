let options = {};

let player = videojs('video-player', options, function onPlayerReady() {
    document.getElementById('nippy-vp-container').style.visibility = 'visible';
});
const videoData = document.getElementById('nippy-vp-data').dataset;
const targetDiv = document.getElementById('nippy-vp');
const contextMenu = document.getElementById('nippy-vp-context-menu');
if (parseInt(videoData.status) < 3) {
    player.createModal('Video is being processed, come back later!', { uncloseable: true });
    targetDiv.addEventListener('contextmenu', function (event) {
        event.preventDefault();
    });

} else if (parseInt(videoData.status) > 3) {
    player.createModal('Video is not available.', { uncloseable: true });
    targetDiv.addEventListener('contextmenu', function (event) {
        event.preventDefault();
    });
}
let playStartTime = null;
let checkDurationInterval = null;
let viewed = false;
let checkDurationTimeout = 2000;



document.addEventListener('click', function (event) {
    if (!contextMenu.contains(event.target) && !targetDiv.contains(event.target)) {
        contextMenu.setAttribute('data-hidden', '');
    }
});

document.getElementById('menu-item-1').addEventListener('click', function () {
    contextMenu.removeAttribute('data-hidden');
    player.createModal('by redux :D');



});


var Component = videojs.getComponent('Component');

class TitleBar extends Component {
    constructor(player, options) {
        super(player, options);

        if (options.text) {
            this.updateTextContent(options.text);
        }
    }

    createEl() {
        return videojs.createEl('div', {
            className: 'vjs-title-bar'
        });
    }

    updateTextContent(text) {
        if (typeof text !== 'string') {
            text = 'Title Unknown';
        }
        videojs.emptyEl(this.el());
        videojs.appendContent(this.el(), text);
    }
}

class EndScreen extends Component {
    constructor(player, options) {
        super(player, options);
        const formData = new FormData();
        formData.append('video_id', videoData.id);
        fetch("/video/related", {
            'method': 'POST',
            'body': formData
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(response.status);
                }
                return response.text();
            })
            .then(text => {
                videojs.dom.emptyEl(this.el());
                const container = document.createElement('div');
                container.className = 'end-screen-grid';
                container.innerHTML = text;

                videojs.dom.appendContent(this.el(), container);

            })
            .catch(error => {
                console.log(error);
            });
    }

    createEl() {
        return videojs.dom.createEl('div', {
            className: 'vjs-end-screen'
        });
    }

}

videojs.registerComponent('TitleBar', TitleBar);
videojs.registerComponent('EndScreen', EndScreen);

if (videoData.iframe === "true") {
    player.addChild('TitleBar', { text: videoData.title });

}
let endScreen = player.addChild('EndScreen');
endScreen.el().setAttribute('data-hidden', '');

player.on('playing', function () {
    contextMenu.setAttribute('data-hidden', '');
    endScreen.el().setAttribute('data-hidden', '');

    if (viewed) {
        return;
    }
    if (playStartTime === null) {
        playStartTime = new Date().getTime();
    }

    checkDurationInterval = setInterval(function () {
        if (player.paused()) {
            clearInterval(checkDurationInterval);
            playStartTime = null;
        } else {
            let currentTime = new Date().getTime();
            if (currentTime - playStartTime >= checkDurationTimeout) {
                clearInterval(checkDurationInterval);

                const formData = new FormData();
                formData.append('video_id', videoData.id);
                fetch("/video/views", {
                    'method': 'POST',
                    'body': formData
                })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(response.status);
                        }
                        return response.text();
                    })
                    .then(text => {

                        let watchViews = document.getElementById('watch-view-count');
                        
                        if (watchViews) {
                            watchViews.innerText = text;
                        }
                        viewed = true;
                    })
                    .catch(error => {
                        console.log(error);
                    });
            }
        }
    }, 100);
});

player.on('pause', function () {
    contextMenu.setAttribute('data-hidden', '');
    endScreen.el().setAttribute('data-hidden', '');
    clearInterval(checkDurationInterval);
    playStartTime = null;
});

player.on('ended', function () {
    contextMenu.setAttribute('data-hidden', '');
    endScreen.el().removeAttribute('data-hidden');
    clearInterval(checkDurationInterval);
    playStartTime = null;
});

player.on('seeking', function () {
    contextMenu.setAttribute('data-hidden', '');
    endScreen.el().setAttribute('data-hidden', '');
});