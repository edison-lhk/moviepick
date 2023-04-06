const toasts = document.querySelectorAll('.toast');
const toast_btns = document.querySelectorAll('.toast-btn');

// Flash content disappear automatically after a few seconds
if (toasts.length > 0) {
    let toasts_count = 0;
    toasts.forEach(toast => {
        setTimeout(() => {
            toast.remove();
        }, 3000 + toasts_count * 500);
        toasts_count += 1;
    });
};

// Allows users to delete the flash content manually if they want
if (toast_btns.length > 0) {
    toast_btns.forEach(toast_btn => {
        toast_btn.addEventListener('click', () => {
            toast_btn.parentElement.remove();
        });
    });
};

const section_navs = document.querySelectorAll('nav.section');
const category_navs = document.querySelectorAll('nav.category');
const genre_navs = document.querySelectorAll('nav.genre');

// Allows user to naviagate between different sections
if (section_navs.length > 0) {
    section_navs.forEach(section_nav => {
        section_nav.addEventListener('click', () => {
            window.location.href = '/' + section_nav.classList[1];
        });
    });
};

// Allows users to browse movies of different categories
if (category_navs.length > 0) {
    category_navs.forEach(category_nav => {
        category_nav.addEventListener('click', () => {
            window.location.href = '/' + category_nav.classList[1];
        });
    });
};

// Allows users to browse movies of different genres
if (genre_navs.length > 0) {
    genre_navs.forEach(genre_nav => {
        genre_nav.addEventListener('click', () => {
            window.location.href = '/' + genre_nav.classList[1];
        });
    });
};

const menu = document.querySelector('.menu-container');
const open_menu_btn = document.querySelector('.mobile-menu-btn');

// Allows users to open menu in mobile version
if (open_menu_btn != null && menu != null) {
    open_menu_btn.addEventListener('click', () => {
        if (menu.className.includes('open')) {
            menu.className = 'menu-container';
        } else {
            menu.className = 'menu-container open';
        };
    });
};

const close_menu_btn = document.querySelector('.icon-container span');

// Allows users to close menu in mobile version
if (close_menu_btn != null && menu != null) {
    close_menu_btn.addEventListener('click', () => {
        menu.className = 'menu-container';
    });
};

const carousel_movies = document.querySelectorAll('.carousel-inner > .item');
const movie_cards = document.querySelectorAll('.movie-card-container > img');

// Allows users to browse movie details by clicking on carousel movies
if (carousel_movies.length > 0) {
    carousel_movies.forEach(carousel_movie => {
        carousel_movie.addEventListener('click', () => {
            window.location.href = `/movie/${carousel_movie.id}`;
        });
    });
};

// Allows users to browse movie details by clicking on movie cards
if (movie_cards.length > 0) {
    movie_cards.forEach(movie_card => {
        movie_card.addEventListener('click', () => {
            window.location.href = `/movie/${movie_card.id}`;
        });
    });
};

const previous_page_nav = document.querySelector('.page-item.previous');
const page_num = document.querySelector('.page-item.page-num .page-link');
const next_page_nav = document.querySelector('.page-item.next');

let path_list = window.location.pathname.split('/');

// Update movie page number when users navigate between different pages
if (page_num != null) {
    if (!isNaN(Number(path_list.slice(-1))) && path_list.slice(-1) != '') {
        page_num.innerText = Number(path_list.slice(-1));
    } else {
        path_list = window.location.href.split('/')[3];
        if (path_list.includes('?') && path_list.split('?')[1].split('&').length == 2) {
            page_num.innerText = Number(path_list.split('?')[1].split('&')[1].split('=')[1]);
        } else {
            page_num.innerText = 1;
        }
    }
};

// Allows users to go to the previous movie page
if (previous_page_nav != null) {
    previous_page_nav.addEventListener('click', () => {
        path_list = window.location.href.split('/');
        if (!isNaN(Number(path_list.slice(-1))) && path_list.slice(-1) != '') {
            if (path_list.length === 4) {
                window.location.pathname = `/${Number(path_list[3]) - 1}`;
            } else {
                window.location.pathname =`/${path_list[3]}/${Number(path_list[4]) - 1}`;
            };
        } else {
            if (path_list[3].includes('?')) {
                path_list = path_list[3].split('?');
                if (path_list[1].split('&').length == 2 && path_list[1].split('&')[1].split('=')[1] != '1') {
                    window.location.href = `${window.location.origin}/${path_list[0]}?${path_list[1].split('&')[0]}&page=${Number(path_list[1].split('&')[1].split('=')[1]) - 1}`;
                }
            }
        }
    });
}

// Allows users to go to the next movie page
if (next_page_nav != null) {
    next_page_nav.addEventListener('click', () => {
        path_list = window.location.href.split('/');
        if (path_list.length === 4) {
            if (path_list[3] == '') {
                window.location.pathname = '/2';
            } else if (!isNaN(Number(path_list[3])))  {
                window.location.pathname = `/${Number(path_list[3]) + 1}`;
            } else if (path_list[3].includes('?')) {
                path_list = path_list[3].split('?')
                if (path_list[1].split('&').length == 1) {
                    window.location.href = `${window.location.origin}/${path_list[0]}?${path_list[1]}&page=2`;
                } else {
                    window.location.href = `${window.location.origin}/${path_list[0]}?${path_list[1].split('&')[0]}&page=${Number(path_list[1].split('&')[1].split('=')[1]) + 1}`;
                }
            } else {
                window.location.pathname = `/${path_list[3]}/2`;
            }
        } else if (path_list.length === 5) {
            window.location.pathname =`/${path_list[3]}/${Number(path_list[4]) + 1}`;
        };
    });
};

const favourite_btn = document.querySelector('.movie-title > span');

// Allows users to add or delete movies to their favourite list
if (favourite_btn != null) {
    favourite_btn.addEventListener('click', async () => {
       if (favourite_btn.classList[1] == 'glyphicon-heart-empty') {
            favourite_btn.className = `glyphicon glyphicon-heart ${favourite_btn.classList[2]}`;
            await fetch(`${window.location.origin}/my-favourite`, { method: 'POST', body: JSON.stringify({ movie_id: favourite_btn.classList[2]}) });
            window.location.reload();
       } else {
            favourite_btn.className = `glyphicon glyphicon-heart-empty ${favourite_btn.classList[2]}`;
            await fetch(`${window.location.origin}/my-favourite`, { method: 'DELETE', body: JSON.stringify({ movie_id: favourite_btn.classList[2]}) });
            window.location.reload();
       };
    });
};

const add_review_form = document.querySelector('.add-review-form');

// Allows users to create reviews for any movies
if (add_review_form != null) {
    add_review_form.addEventListener('submit', async (e) => {
        e.preventDefault();
        let body = new FormData(add_review_form)
        body.append('movie_id', add_review_form.classList[1])
        await fetch(`${window.location.origin}/add-review`, { method: 'POST', body: body });
        window.location.reload();
    });
};

const favourite_cards = document.querySelectorAll('.favourite-card > img');

// Allows users to browse movie details when they clicked on their favourite movie card
if (favourite_cards.length > 0) {
    favourite_cards.forEach(favourite_card => {
        favourite_card.addEventListener('click', () => {
            window.location.href = `/movie/${favourite_card.id}`;
        });
    });
};

const small_favourite_btns = document.querySelectorAll('.favourite-card .info-container > span');

// Allows users to delete movies to their favourite list
if (small_favourite_btns.length > 0) {
    small_favourite_btns.forEach(small_favourite_btn => {
        small_favourite_btn.addEventListener('click', async () => {
            small_favourite_btn.className = `glyphicon glyphicon-heart-empty ${small_favourite_btn.classList[2]}`;
            await fetch(`${window.location.origin}/my-favourite`, { method: 'DELETE', body: JSON.stringify({ movie_id: small_favourite_btn.classList[2] }) });
            window.location.reload();
        });
    });
};

const history_cards = document.querySelectorAll('.history-card > img');

// Allows users to browse movie details after they clicked on their watch history card
if (history_cards.length > 0) {
    history_cards.forEach(history_card => {
        history_card.addEventListener('click', () => {
            window.location.href = `/movie/${history_card.id}`;
        });
    });
};

const delete_history_btns = document.querySelectorAll('.history-card .info-container > span');

// Allows users to clear a specific watch history
if (delete_history_btns.length > 0) {
    delete_history_btns.forEach(delete_history_btn => {
        delete_history_btn.addEventListener('click', async () => {
            await fetch(`${window.location.origin}/watch-history`, { method: 'DELETE', body: JSON.stringify({ movie_id: delete_history_btn.classList[2], datetime: `${delete_history_btn.classList[3]} ${delete_history_btn.classList[4]}` }) });
            window.location.reload();
        });
    });
};