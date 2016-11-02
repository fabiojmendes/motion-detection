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

	let currentVideo = load('currentVideo');
	if (currentVideo) {
		let candidate = player.playlist.find(function(item) {
			return currentVideo.filename == item.filename;
		});
		if (candidate) {
			let index = player.playlist.indexOf(candidate)
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
		let currentVideo = player.playlist[player.current];
		if (currentVideo) {
			save('currentVideo', currentVideo);
		}

		$('li.jp-playlist-current').each(function() { this.scrollIntoView() });
	});

	$('#videoContainer').bind($.jPlayer.event.ended, function(e) {
		let currentVideo = load('currentVideo');
		if (currentVideo) {
			currentVideo.ended = true;
			save('currentVideo', currentVideo);
		}
	});
}

let playerPromise = new Promise(function(resolve, reject) {
	window.addEventListener('load', function() {
		let player = new jPlayerPlaylist({ jPlayer: "#jplayer", cssSelectorAncestor: "#videoContainer" }, [], {
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

Promise.all([playlistPromise, playerPromise]).then(function(results) {
	let playlist = results[0];
	let player = results[1];

	loadPlaylist(player, playlist);

	source.addEventListener('video:new', function(e) {
		let videos = JSON.parse(e.data);
		for (let video of videos) {
			player.add(video);
		}
		if (videos.length > 0) {
			let jPlayer = $('#jplayer').data().jPlayer;
			let currentVideo = load('currentVideo');
			if (jPlayer.status.paused && currentVideo && currentVideo.ended) {
				player.select(player.current + 1);
				save('currentVideo', player.playlist[player.current]);
			}
			$('li.jp-playlist-current').each(function() { this.scrollIntoView() });
		}
	});
});

window.addEventListener("unload", function(e) {
	source.close();
});
