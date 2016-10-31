/*  */

function save(key, object) {
	localStorage.setItem(key, JSON.stringify(object));
}

function load(key) {
	return JSON.parse(localStorage.getItem(key));
}

function remove(key) {
	return localStorage.removeItem(key);
}

function loadPlaylist(player, playlist) {
	player.setPlaylist(playlist);

	var currentVideo = load('currentVideo');
	if (currentVideo) {
		var candidate = player.playlist.find(function(item) {
			return currentVideo.filename == item.filename;
		});
		if (candidate) {
			var index = player.playlist.indexOf(candidate)
			if (currentVideo.ended && player.playlist.length - index > 1) {
				player.select(index + 1);
			} else {
				player.select(index);
			}
		} else {
			remove('currentVideo');
		}
	}

	// Sroll to Current
	$('li.jp-playlist-current').each(function() { this.scrollIntoView() });

	$('#videoContainer').bind($.jPlayer.event.play, function(e) {
		var currentVideo = player.playlist[player.current];
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
}

var source = new EventSource('/playlist');

var subscribePromise = new Promise(function(resolve, reject) {
	source.addEventListener('video:list', function(e) {
		var videos = JSON.parse(e.data)
		resolve(videos);
	});
});

var playerPromise = new Promise(function(resolve, reject) {
	window.addEventListener('load', function() {
		var player = new jPlayerPlaylist({ jPlayer: "#jplayer", cssSelectorAncestor: "#videoContainer" }, [], {
			playlistOptions: {
				displayTime: 0
			},
			supplied: "m4v",
			useStateClassSkin: true,
			autoBlur: false,
			smoothPlayBar: false,
			keyEnabled: false,
			size: {	width: 800, height: 448, cssClass: "jp-video-480p" },
			ready: function() { resolve(player) }
		});
	});
});

Promise.all([subscribePromise, playerPromise]).then(function(results) {
	var playlist = results[0];
	var player = results[1];

	loadPlaylist(player, playlist);

	source.addEventListener('video:new', function(e) {
		var videos = JSON.parse(e.data);
		videos.forEach(function(video) { player.add(video) });
		if (videos.length > 0) {
			var jPlayer = $('#jplayer').data().jPlayer;
			var currentVideo = load('currentVideo');
			if (jPlayer.status.paused && currentVideo && currentVideo.ended) {
				player.select(player.current + 1);
			}
			$('li.jp-playlist-current').each(function() { this.scrollIntoView() });
		}
	});
});

window.addEventListener("unload", function(e) {
	source.close();
});
