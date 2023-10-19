const BASE_API_URL = "https://swipe.exc.cx/api";
// const BASE_API_URL = "http://127.0.0.1:8008";

let likeCurrentProfile = false;
let passCurrentProfile = false;
let rewind = false;
let rewinding = false;

document.addEventListener("keypress", function (event) {
    if (event.key === 'j') {
        likeCurrentProfile = true;
    } else if (event.key === 'k') {
        likeCurrentProfile = false;
    }
    switch (event.key) {
        case 'l':
        case 'd':
            likeCurrentProfile = true;
            break;
        case 'j':
        case 'a':
            passCurrentProfile = true;
            likeCurrentProfile = false;
            break;
        case 'k':
        case 's':
            likeCurrentProfile = false;
            rewind = true;
            rewinding = true;
            swipe('rewind');
            break;
        default: {
            rewind = false
            likeCurrentProfile = false;
        }

    }
});

function swipe(action) {
    let bnts = document.querySelectorAll('button.button');
    let swipeButtons = [];
    for (const bnt of bnts) {
        if (['REWIND', 'NOPE', 'SUPER LIKE', 'LIKE', 'BOOST'].includes(bnt.innerText)) {
            swipeButtons.push(bnt);
        }
    }
    if (swipeButtons.length !== 5) {
        // Not found buttons.
        return;
    }
    if (action === 'super-like') {
        console.log('⭐ Send Super Like!');
        let noSuperLike = swipeButtons[2].parentNode.parentNode.querySelectorAll("span[aria-label=\"0 remaining\"]");
        if (noSuperLike.length === 1) {
            // No super like, send like
            swipeButtons[3].click();
        } else {
            // Send super like
            swipeButtons[2].click();
        }
    } else if (action === 'like') {
        console.log('💗 Send Like!');
        swipeButtons[3].click();
    } else if (action === 'rewind') {
        console.log('Rewind');
        swipeButtons[0].click();
    } else { // pass
        console.log('❌ Send Pass');
        swipeButtons[1].click();
    }

    // If popup
    setTimeout(function () {
        const button_texts = ['NO THANKS', 'NO, THANKS', 'NOT NOW', 'MAYBE LATER',  'NOT INTERESTED'];
        let bntsPopup = document.querySelectorAll('button.button');
        for (const bntPop of bntsPopup) {
            // Close Popup -- No, Thanks
            if (button_texts.includes(bntPop.innerText.trim().toUpperCase())) {
                console.log('❌ Close Popup');
                bntPop.click();
            }
        }
        let bntsPopup2 = document.querySelectorAll('button[type="button"]');
        for (const bntPop2 of bntsPopup2) {
            // Close Popup -- No, Thanks
            if (button_texts.includes(bntPop2.innerText.trim().toUpperCase())) {
                console.log('❌ Close Popup2');
                bntPop2.click();
            }
        }
    }, 1500);
}

function nextPhoto() { // Browse next photo for active button.
    let activeBullets = document.querySelectorAll("button.bullet.bullet--active");
    for (let activeBullet of activeBullets) {
        let bullet = activeBullet.nextSibling;
        if (bullet !== null) {
            bullet.click();
        } else {
            bullet = activeBullet.parentNode.firstChild;
            if (bullet !== null) {
                bullet.click();
            }
        }
    }
}

async function checkProfile(profile) {
    let headers = new Headers();
    headers.append("Content-Type", "application/json");
    let payload = {
        "name": profile.name ?? '',
        "age": profile.age ?? null,
        "active": profile.active ?? false,
        "verified": profile.verified ?? false,
        "livesIn": profile.livesIn ?? '',
        "bio": profile.bio ?? '',
        "job": profile.job ?? '',
        "school": profile.school ?? '',
        "tags": Array.from(profile.tags) ?? [],
        "photos": profile.photos ?? [],
        "like": profile.like ?? false,
    }
    let raw = JSON.stringify(payload);
    let requestOptions = {
        method: 'POST', headers: headers, body: raw, redirect: 'follow'
    };

    try {
        const response = await fetch(BASE_API_URL + '/save', requestOptions)
        const data = await response.json();
        console.log('HOT!', data['profile']['hot'])
        return [data['profile']['hot'], data];
    } catch (e) {
        return [false, null];
    }
}


function findPhotos() {
    let photos = [];
    try {
        let images = document.querySelectorAll('div.StretchedBox[role="img"]');
        for (const imageNode of images) {
            let hide = imageNode.parentNode.parentNode.parentNode.parentNode.getAttribute('aria-hidden');
            if (hide === 'false') { // Displaying profile's image
                let imgUrl = imageNode.style.backgroundImage;
                imgUrl = imgUrl.substring(imgUrl.indexOf("\"") + 1, imgUrl.lastIndexOf("\""));
                photos.push(imgUrl);
            }
        }
        return photos;
    } catch (e) {
        return photos;
    }
}

function getValueBySelector(parent, selector) {
    let valueNode = parent.querySelector(selector)
    if (valueNode !== null) {
        return valueNode.innerText;
    }
    return null;
}

function findInfo(profile) {
    try {
        // let nameNode = document.querySelectorAll('span[itemprop="name"]')[1];
        let names = document.querySelectorAll('span[itemprop="name"]');
        for (const nameNode of names) {
            let parent = nameNode.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode.parentNode;
            let hide = parent.getAttribute('aria-hidden');
            if (hide === 'false') { // Active profile
                profile.name = nameNode.innerText;

                let age = getValueBySelector(parent, 'span[itemprop="age"]');
                if (age !== null) {
                    profile.age = age;
                }


                let spans = nameNode.parentNode.parentNode.parentNode.parentNode.parentNode.querySelectorAll('span')
                for (const span of spans) {
                    if (span.innerText.trim() === 'Recently Active') {
                        profile.active = true;
                        break;
                    }
                }

                let livingIn = getValueBySelector(parent, 'div[itemprop="homeLocation"]');
                if (livingIn != null) {
                    profile.livingIn = livingIn.replace("Lives in ", "");
                }

                let school = getValueBySelector(parent, 'div[itemprop="affiliation"]');
                if (school != null) {
                    profile.school = school.replace("Also went to ", "");
                }

                let job = getValueBySelector(parent, 'div[itemprop="jobTitle"]');
                if (job != null) {
                    profile.job = job;
                }

                let bio = getValueBySelector(parent, '.BreakWord');
                if (bio != null && bio !== '') {
                    profile.bio = bio;
                }

                let titleNode = nameNode.parentNode.parentNode
                let verified = titleNode.querySelector('svg')
                if (verified != null) {
                    profile.verified = true;
                }

                let bubbles = parent.querySelectorAll('div[tabindex="0"]')
                if (bubbles.length > 0) {
                    let bubble_boxs = bubbles[0].querySelectorAll('.Bd')
                    if (bubble_boxs.length === 0) {
                        return;
                    }
                    for (const bubble_box of bubble_boxs) {
                        if (bubble_box.innerText === '' || bubble_box.innerText === '0') {
                            continue
                        }

                        if (bubble_box.innerText.endsWith(' more')) {
                            continue
                        }

                        profile.tags.add(bubble_box.innerText);
                    }
                }
            }
        }
    } catch (e) {
        console.log(e);
    }
}

const sleep = async (secs) => new Promise(resolve => setTimeout(resolve, secs * 1000));


async function extractProfile() {
    let profile = {
      active: false,
      tags: new Set(),
    };
    findInfo(profile);

    const allPhotos = new Set();

    for (let i = 0; i < 10; i++) { // Browse photos
        if (rewind) {
            rewind = false;
            rewinding = true;
            console.log('Rewinding')
            return profile;
        }
        findInfo(profile);
        let photos = findPhotos();
        for (const photo of photos) {
            allPhotos.add(photo);
        }
        if (i > 3 && (i - allPhotos.size) >= 0) { // No more photos
            break;
        }
        await sleep(0.1 + Math.random() * 0.9);
        nextPhoto();
    }

    profile.photos = Array.from(allPhotos);

    console.log(profile);
    return profile;
}

async function swipeLoop() {
    let empty_count = 0;
    let lastProfile = {name: null, age: null}
    while (true) {
        if (Math.random() >= 0.999) {
            location.reload();
        } else {
            try {
                let profile = await extractProfile();
                if (profile.photos.length > 0) { // Must have photos to swipe
                    if (lastProfile.age === profile.name && lastProfile.age === profile.age) {
                        console.log('Must have photos to swipe');
                        location.reload();
                        likeCurrentProfile = false;
                        return;
                    }
                    let result = await checkProfile(profile);
                    if (rewinding) {
                        console.log('Rewinding after checkProfile')
                        rewinding = false;
                        continue;
                    }
                    if (likeCurrentProfile || result[0] && !passCurrentProfile) {
                        console.log('score', result[1]['score']);
                        location.reload();
                    } else {
                        swipe('pass');
                        profile.like = false;
                        likeCurrentProfile = false;
                        passCurrentProfile = false;
                    }
                    lastProfile = profile;
                } else {
                    if (empty_count++ > 10) {
                        console.log('empty_count reload');
                        location.reload();
                    }
                }
            } catch (e) {
                likeCurrentProfile = false;
                rewind = false;
                console.log(e);
            }
        }
        await sleep(0.1);
    }
}

swipeLoop().then();
