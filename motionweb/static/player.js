var myPlaylist;

var playlistFuture = $.ajax('/playlist');

function save(key, object) {
	localStorage.setItem(key, JSON.stringify(object));
}

function load(key) {
	return JSON.parse(localStorage.getItem(key));
}

function remove(key) {
	return localStorage.removeItem(key);
}

function loadPlaylist() {
	playlistFuture.done(function(playlist) {

		myPlaylist.setPlaylist(playlist);

		var currentVideo = load('currentVideo');
		if (currentVideo) {
			var candidate = myPlaylist.playlist.find(function(item) {
				return currentVideo.filename == item.filename;
			});
			if (candidate) {
				var index = myPlaylist.playlist.indexOf(candidate)
				if (currentVideo.ended && myPlaylist.playlist.length - index > 1) {
					myPlaylist.select(index + 1);
				} else {
					myPlaylist.select(index);
				}
			} else {
				remove('currentVideo');
			}
		}

		// Sroll to Current
		$('li.jp-playlist-current').each(function() { this.scrollIntoView() });

		$('#videoContainer').bind($.jPlayer.event.play, function(e) {
			var currentVideo = myPlaylist.playlist[myPlaylist.current];
			if (currentVideo) {
				save('currentVideo', currentVideo);
			}

			$('li.jp-playlist-current').each(function() { this.scrollIntoView() });
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

	var source = new EventSource('/subscribe');

	source.onmessage = function (event) {
		var video = JSON.parse(event.data)
		myPlaylist.add(video);
	};
});
