window.addEventListener('load', () => {
	// TODO: Add range limits to pickers
	flatpickr('.datepicker', {});
	toggleInfo();
});

/*
* Event handlers
*/
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
