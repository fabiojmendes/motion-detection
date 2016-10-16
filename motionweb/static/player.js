var myPlaylist;

function save(key, object) {
	localStorage.setItem(key, JSON.stringify(object));
}

function load(key) {
	return JSON.parse(localStorage.getItem(key));
}

function loadPlaylist() {
	$.ajax('/playlist').done(function(playlist) {

		myPlaylist.setPlaylist(playlist);

		var currentVideo = load('currentVideo');
		if (currentVideo) {
			var candidate = playlist[currentVideo.index];
			if (candidate && candidate.filename == currentVideo.filename) {
				if (currentVideo.ended && myPlaylist.playlist.length - currentVideo.index > 1) {
					myPlaylist.select(currentVideo.index + 1);
				} else {
					myPlaylist.select(currentVideo.index);
				}
			} else {
				localStorage.removeItem('currentVideo');
			}
		}

		// Sroll to Current
		$('li.jp-playlist-current').each(function() { this.scrollIntoView() });

		$('#videoContainer').bind($.jPlayer.event.play, function(e) {
			var currentVideo = playlist[myPlaylist.current];
			save('currentVideo', currentVideo);
		});

		$('#videoContainer').bind($.jPlayer.event.ended, function(e) {
			var currentVideo = load('currentVideo');
			if (currentVideo) {
				currentVideo.ended = true;
				save('currentVideo', currentVideo);
			}
		});
	});
}

$(document).ready(function() {
	myPlaylist = new jPlayerPlaylist({ jPlayer: "#jquery_jplayer_N", cssSelectorAncestor: "#videoContainer" }, [], {
		playlistOptions: {
			displayTime: 0
		},
		supplied: "m4v",
		useStateClassSkin: true,
		autoBlur: false,
		smoothPlayBar: false,
		keyEnabled: false,
		size: {	width: 800, height: 448, cssClass: "jp-video-480p" },
		ready: loadPlaylist
	});
});
