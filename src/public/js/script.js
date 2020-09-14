window.onload = () => toggleInfo();

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
	// TODO
	document.querySelector('#settings').classList.toggle('is-active');
	// reloadChart(type);
}

function closeSettings() {
	document.querySelector('#settings').classList.remove('is-active');
}
