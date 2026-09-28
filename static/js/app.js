// Navbar search (sidebar)
const searchInput = document.getElementById('search-input');
const searchResults = document.getElementById('search-results');
let searchTimer;

if (searchInput) {
    searchInput.addEventListener('input', function () {
        clearTimeout(searchTimer);
        const q = this.value.trim();
        if (q.length < 1) { searchResults.classList.remove('active'); return; }
        searchTimer = setTimeout(() => {
            fetch('/api/search/?q=' + encodeURIComponent(q) + '&category=all')
                .then(r => r.json())
                .then(data => {
                    let html = '';

                    // Users (top 4)
                    if (data.users && data.users.length > 0) {
                        html += '<div style="padding:8px 16px;font-weight:600;font-size:13px;color:#8e8e8e;">Users</div>';
                        html += data.users.slice(0, 4).map(u =>
                            `<a href="/profile/${u.username}/" class="search-result-item">
                                ${u.pic
                                    ? `<img src="${u.pic}" alt="">`
                                    : `<div class="avatar-placeholder" style="width:44px;height:44px;font-size:16px;">${u.username[0].toUpperCase()}</div>`
                                }
                                <div class="result-info">
                                    <div class="result-username">${u.username}</div>
                                    <div class="result-name">${u.name}</div>
                                </div>
                            </a>`
                        ).join('');
                    }

                    // Posts (top 3)
                    if (data.posts && data.posts.length > 0) {
                        html += '<div style="padding:8px 16px;font-weight:600;font-size:13px;color:#8e8e8e;border-top:1px solid #efefef;">Posts</div>';
                        html += data.posts.slice(0, 3).map(p =>
                            `<a href="/posts/${p.id}/" class="search-result-item">
                                <img src="${p.image}" style="width:44px;height:44px;border-radius:6px;object-fit:cover;">
                                <div class="result-info">
                                    <div class="result-username">${p.username}</div>
                                    <div class="result-name">${p.caption ? p.caption.substring(0, 40) : 'No caption'}${p.location ? ' · ' + p.location : ''}</div>
                                </div>
                            </a>`
                        ).join('');
                    }

                    // Reels (top 3)
                    if (data.reels && data.reels.length > 0) {
                        html += '<div style="padding:8px 16px;font-weight:600;font-size:13px;color:#8e8e8e;border-top:1px solid #efefef;">Reels</div>';
                        html += data.reels.slice(0, 3).map(r =>
                            `<a href="/reels/" class="search-result-item">
                                <div style="width:44px;height:44px;border-radius:6px;background:#000;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="white" stroke="none"><polygon points="5 3 19 12 5 21"/></svg>
                                </div>
                                <div class="result-info">
                                    <div class="result-username">${r.username}</div>
                                    <div class="result-name">${r.caption ? r.caption.substring(0, 40) : 'No caption'}</div>
                                </div>
                            </a>`
                        ).join('');
                    }

                    // Locations (top 3)
                    if (data.locations && data.locations.length > 0) {
                        html += '<div style="padding:8px 16px;font-weight:600;font-size:13px;color:#8e8e8e;border-top:1px solid #efefef;">Locations</div>';
                        html += data.locations.slice(0, 3).map(l =>
                            `<a href="/location/${encodeURIComponent(l.name)}/" class="search-result-item">
                                <div style="width:44px;height:44px;border-radius:50%;background:#efefef;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#262626" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                                </div>
                                <div class="result-info">
                                    <div class="result-username">${l.name}</div>
                                    <div class="result-name">${l.total} post${l.total !== 1 ? 's' : ''}</div>
                                </div>
                            </a>`
                        ).join('');
                    }

                    // See all results link
                    if (html) {
                        html += `<a href="/search/?q=${encodeURIComponent(q)}" style="display:block;text-align:center;padding:12px;font-size:14px;font-weight:600;color:#0095f6;border-top:1px solid #efefef;">See all results</a>`;
                    } else {
                        html = '<div style="padding:20px;text-align:center;color:#8e8e8e;">No results found.</div>';
                    }

                    searchResults.innerHTML = html;
                    searchResults.classList.add('active');
                });
        }, 300);
    });

    searchInput.addEventListener('blur', function () {
        setTimeout(() => searchResults.classList.remove('active'), 200);
    });

    searchInput.addEventListener('focus', function () {
        if (this.value.trim().length > 0) searchResults.classList.add('active');
    });
}

// Notifications dropdown
const notifToggle = document.getElementById('notif-toggle');
const notifDropdown = document.getElementById('notif-dropdown');

if (notifToggle && notifDropdown) {
    notifToggle.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        const isOpen = notifDropdown.classList.toggle('active');
        if (isOpen) {
            fetch('/api/notifications/')
                .then(r => r.json())
                .then(data => {
                    const list = document.getElementById('notif-list');
                    if (data.notifications.length === 0) {
                        list.innerHTML = '<div style="padding:40px;text-align:center;color:#8e8e8e;">No notifications yet.</div>';
                    } else {
                        list.innerHTML = data.notifications.map(n =>
                            `<a href="${n.link || '#'}" class="notif-item ${!n.is_read ? 'unread' : ''}">
                                ${n.pic
                                    ? `<img src="${n.pic}" alt="">`
                                    : `<div class="avatar-placeholder" style="width:44px;height:44px;font-size:16px;flex-shrink:0;">${n.actor[0].toUpperCase()}</div>`
                                }
                                <span class="notif-text"><strong>${n.actor}</strong> ${n.text.replace(n.actor + ' ', '')}</span>
                                <span class="notif-time">${n.time}</span>
                            </a>`
                        ).join('');
                    }
                    const badge = notifToggle.querySelector('.badge');
                    if (badge) badge.remove();
                });
        }
    });

    document.addEventListener('click', function (e) {
        if (!notifToggle.contains(e.target)) {
            notifDropdown.classList.remove('active');
        }
    });

    notifDropdown.addEventListener('click', function (e) {
        e.stopPropagation();
    });
}
