// Color theme ('light' or 'dark')
let theme = 'light';

window.addEventListener('load', () => {
	// Enable dark mode if state is stored
	const prefersDark = (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);
	theme = window.localStorage.getItem('color_theme') || (prefersDark ? 'dark' : 'light');
	setTheme();

	// TODO: Add range limits to pickers
	flatpickr('.datepicker', {});
	toggleInfo();
});

/*
* Event handlers
*/
// Toggle color theme between light and dark
function toggleDarkMode() {
	theme = theme == 'dark' ? 'light' : 'dark';
	setTheme();
}

// Toggles the extra stat cards
function toggleExtraCards(e) {
	let moreStats = document.getElementById('moreStats');

	e.children[0].classList.toggle('fa-chevron-up');
	e.children[0].classList.toggle('fa-chevron-down');
	moreStats.classList.toggle('closed');
}

function toggleInfo(e) {
	const isHidden = window.localStorage.getItem('hiddenInfo');
	if (isHidden) return;

	document.querySelector('#message').classList.toggle('is-hidden');

	// If coming from a click then store we want to permanently hide this
	if (e) window.localStorage.setItem('hiddenInfo', true);
}

function showSettings(type) {
	document.querySelector('#settings').setAttribute('type', type);
	document.querySelector('#settings').classList.add('is-active');
}

function saveSettings() {
	let query = {};

	const type  = document.querySelector('#settings').getAttribute('type');
	const start = document.querySelector('#start-date').value;
	const end   = document.querySelector('#end-date').value;

	if (start) query.start = start;
	if (end) query.end = end;

	reloadChart(type, query);
	closeSettings();
}

function closeSettings() {
	document.querySelector('#settings').setAttribute('type', null);
	document.querySelector('#settings').classList.remove('is-active');
}

// Set the color theme
function setTheme() {
	const btn = document.querySelector('#themeToggle');

	// If on then disable and set icon to moon
	if (theme == 'light') {
		btn.classList = ['fas fa-moon fa-2x'];
		document.querySelector('#darkly').disabled = true;

	// If off then enable and set icon to sun
	} else {
		btn.classList = ['fas fa-sun fa-2x'];
		document.querySelector('#darkly').disabled = false;
	}

	// Save in localStorage
	window.localStorage.setItem('color_theme', theme);
}
