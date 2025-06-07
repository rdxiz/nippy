function loginPage() {
    location.href=PROPS.redirectSignIn;
}

const messageError = document.querySelector('.messages .error');
if (messageError){
    messageError.addEventListener('animationend', () => {
        messageError.style.display = 'none';
    });
}

const itemsSync = document.querySelectorAll('[data-sync]');
itemsSync.forEach(item => {
    item.addEventListener('click', () => {
        item.blur();
        const hasSwitch = item.toggleAttribute('data-switch');
        const docLink = document.getElementById(item.dataset.link);
        if (hasSwitch) {
            docLink.setAttribute('data-switch', '');
        } else {
            docLink.removeAttribute('data-switch');
        }
    });
});

const followContainers = document.querySelectorAll('.follow-container, .branded-profile');
followContainers.forEach(item => {
    const button = item.querySelector('button');
    const followCount = item.querySelector('.follow-count');
    if (PROPS.redirectSignIn) {
        item.addEventListener('click', loginPage);
    } else {
        item.addEventListener('click', () => {
            const hasSwitch = button.toggleAttribute('data-switch');
            if (followCount){
                if (hasSwitch) {
                    followCount.innerText = parseInt(followCount.innerText) + 1;
                } else {
                    followCount.innerText = parseInt(followCount.innerText) - 1;
                }
            }
        
            const formData = new FormData();
            formData.append('profile_id', item.dataset.profileId);
            formData.append('follow', hasSwitch);
            button.disabled = true;

            fetch('/follow', {
                'method': 'POST',
                'body': formData
            })
                .then(response => {
                    button.disabled = false;
                    if (!response.ok) {
                        throw new Error(response.status);
                    }
                    return response.text();
                })
                .then(text => {
                    if (followCount) {
                    followCount.innerText = text;

                    }
                })
                .catch(error => {
                    
                    console.log(error);
                }); 
        });
        
    }
});

const watchVoters = document.querySelectorAll('.watch-vote');


watchVoters.forEach(item => {
    const likeButton = item.querySelector('[data-like]');
    const dislikeButton = item.querySelector('[data-dislike]');
    const ratings = document.querySelector('.rating');
    const positiveRatings = ratings.querySelector('.positive-ratings');
    const negativeRatings = ratings.querySelector('.negative-ratings');
    
    function intComma(text) {
        if (text.indexOf(",") > -1) {
            return ",";
        } else {
            return ".";
        }
    }
    function replaceIntComma(text, comma) {
        return text.toString().replace(/\B(?=(\d{3})+(?!\d))/g, comma);
    }

    function actionRatings(formData) {
        likeButton.disabled = true;
        dislikeButton.disabled = true;

        fetch('/video/ratings', {
            'method': 'POST',
            'body': formData
        })
            .then(response => {
                likeButton.disabled = false;
                dislikeButton.disabled = false;
                if (!response.ok) {
                    throw new Error(response.status);
                }
                return response.json();
            })
            .then(data => {
                if (positiveRatings) {
                    positiveRatings.innerText = data[0];
                }
                if (negativeRatings) {
                    negativeRatings.innerText = data[1];
                }
            })
            .catch(error => {
                console.log(error);
            }); 
    }
    
    function addPositiveRating(rating){
        if (positiveRatings) {
            const comma = intComma(positiveRatings.innerText);
            const parsedRating = positiveRatings.innerText.replace(comma, "");
            positiveRatings.innerText = replaceIntComma(parseInt(parsedRating) + rating, comma);
        }
    }

    function addNegativeRating(rating){
        if (negativeRatings) {
            const comma = intComma(negativeRatings.innerText);
            const parsedRating = negativeRatings.innerText.replace(comma, "");
            negativeRatings.innerText = replaceIntComma(parseInt(parsedRating) + rating, comma);
        }
    }

    function removeRatings() {
        if (likeButton.hasAttribute('data-checked')) {
            likeButton.removeAttribute('data-checked');
            addPositiveRating(-1);
        }
        if (dislikeButton.hasAttribute('data-checked')) {
            dislikeButton.removeAttribute('data-checked');
            addNegativeRating(-1);
        }
        const formData = new FormData();
        formData.append('video_id', document.getElementById('nippy-vp-data').dataset.id);
        formData.append('rating', 0);
        actionRatings(formData);
        
        return;
    }

    
    if (PROPS.redirectSignIn) {
        likeButton.addEventListener('click', loginPage);
        dislikeButton.addEventListener('click', loginPage);
    } else {
        likeButton.addEventListener('click', () => {
            if (likeButton.hasAttribute('data-checked')){
                removeRatings();
                return;
            }
            
            likeButton.setAttribute('data-checked', '');
            if (dislikeButton.hasAttribute('data-checked')){
                dislikeButton.removeAttribute('data-checked');
                addNegativeRating(-1);
            }
            addPositiveRating(1);

            const formData = new FormData();
            formData.append('video_id', document.getElementById('nippy-vp-data').dataset.id);
            formData.append('rating', 1);
            actionRatings(formData);
        });

        dislikeButton.addEventListener('click', () => {
            
            if (dislikeButton.hasAttribute('data-checked')){
                removeRatings();
                return;
            }
            
            dislikeButton.setAttribute('data-checked', '');
            if (likeButton.hasAttribute('data-checked')){
                likeButton.removeAttribute('data-checked');
                addPositiveRating(-1);

            }
            addNegativeRating(1);

            const formData = new FormData();
            formData.append('video_id', document.getElementById('nippy-vp-data').dataset.id);
            formData.append('rating', -1);
            actionRatings(formData);
        });
    }
    
});
const userProfileMenu = document.getElementById('my-profile-menu');

function profileMenu(){
    const profileMenuToggle = document.getElementById('nav-my-profile').toggleAttribute('data-hidden');
    let dropdown = document.getElementById('my-profile-dropdown')
    dropdown.className = profileMenuToggle ? dropdown.className.replace(' r-180', '') : `${dropdown.className} r-180`
}

if (userProfileMenu) {
    userProfileMenu.addEventListener('click', profileMenu);
}

function s(e) {
    // Function for slide
    e.preventDefault();
    const target = e.target;
    const dataset = target.dataset;
    const container = document.getElementById(dataset.videoList);
    const items = container.getElementsByClassName('video-container');
    if (dataset.direction === 'right') {
        for (let item of items) {
            const itemRect = item.getBoundingClientRect();
            const containerRect = container.getBoundingClientRect();
    
            if (itemRect.left > containerRect.right || itemRect.right > containerRect.right) {
                item.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'start' });
                break;
            }
        }
    }
    if (dataset.direction === 'left') {
        for (let item of items) {
            const itemRect = item.getBoundingClientRect();
            const containerRect = container.getBoundingClientRect();
            if (itemRect.right > containerRect.left) {
                item.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'end' });
                break; 
            }
        }
    }
    
}





function __(e) {
    e.preventDefault();
    const target = e.target;
    const dataset = target.dataset;
    const formBody = new FormData(target)
    const docSuccess = document.getElementById(dataset.replaceOnSuccess);
    docSuccess.setAttribute('data-loading', '');
    target.setAttribute('data-loading', '');
    fetch(dataset.ajax, {
        'method': 'POST',
        'body': formBody
    })
        .then(response => {
            return Promise.all([response.status, response.text()]);
        })
        .then(([status, text]) => {
            if (status > 399 && dataset.replaceOnError) {
                document.getElementById(dataset.replaceOnError).innerHTML = text;
            target.removeAttribute('data-loading');
            docSuccess.removeAttribute('data-loading');
                
                return;
            }
            docSuccess.innerHTML = text;
            const inputs = target.querySelectorAll('input:not([type="hidden"]), textarea, select');
            inputs.forEach(input => {
                input.value = ''
            });
            const errorLists = target.querySelectorAll('.errorlist');
            errorLists.forEach(errorList => {
                errorList.remove();
            });
            docSuccess.removeAttribute('data-loading');
            target.removeAttribute('data-loading');
            
        })
}

// var $i = {}
// let profileMenuToggle;

// function setInnerHTML(elm, html) {
//     elm.innerHTML = html;
    
//     Array.from(elm.querySelectorAll("script"))
//       .forEach( oldScriptEl => {
//         const newScriptEl = document.createElement("script");
        
//         Array.from(oldScriptEl.attributes).forEach( attr => {
//           newScriptEl.setAttribute(attr.name, attr.value) 
//         });
        
//         const scriptText = document.createTextNode(oldScriptEl.innerHTML);
//         newScriptEl.appendChild(scriptText);
        
//         oldScriptEl.parentNode.replaceChild(newScriptEl, oldScriptEl);
//     });
//   }

// function on(endpoint, func) {
//     $i[endpoint] = func;
// }

// function load() {
//     profileMenuToggle = false;
//     try {
//         $i[location.pathname]();
//     } catch (e) {}
// }

// on('/login', function() {
//     console.log('login :D');
// });

// on('/signup', function () {
//     console.log('signup :D');
// });

// on('/', function() {
//     console.log('index :D');
// });

// on('/test', function() {
//     console.log('test :D');
// });

// function goto(url, options, push=true) {
//     console.log("[i] Fetching ", url);
//     document.getElementById('progress').style.display="block";
//     fetch(url, options)
//         .then(response => {
//             !response.ok && (location.href = url);
//             return Promise.all([response.url, response.text()]);
//         })
//         .then(([url, text]) => {
//             var pathname = new URL(url).pathname;
//             var parser = new DOMParser();
//             var doc = parser.parseFromString(text, "text/html");
//             document.title = doc.title;
//             push ? window.history.pushState({"html":doc.body.innerHTML,"pageTitle":doc.title},"", pathname) : window.history.replaceState({"html":doc.body.innerHTML,"pageTitle":doc.title},"", pathname);
//             setInnerHTML(document.body, doc.body.innerHTML);
//             load();
//         })
//         .catch(error => {
//             console.log(error);
//             location.href = url;
//         });
    
    
// }
// function _(e, target){
//     e.preventDefault();
//     window.history.replaceState({"html":document.body.innerHTML,"pageTitle":document.title},"", location.pathname)
//     if (e.target instanceof HTMLFormElement) {
//         const formData = new FormData(e.target);
//         goto (location.pathname, {
//             'method': 'POST', 
//             'body': formData
//         });
//         return;
//     }
//     var pathname = new URL(target ? target.href : e.target.href);
//     goto(pathname);
// }

// addEventListener("popstate", function (e) {
//     console.log("[i] Event \"popstate\" emitted");
//     if (e.state.html) {
//         setInnerHTML(document.body, e.state.html)
//         // document.body.innerHTML = e.state.html;
//         load();
//     } else {
//         goto(location.pathname, null, false);
//     }
// });
// load();

