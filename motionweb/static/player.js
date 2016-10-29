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

function loadPlaylist(myPlaylist, videos) {
	myPlaylist.setPlaylist(videos);

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
}

var source = new EventSource('/subscribe');

var subscribePromise = new Promise(function(resolve, reject) {
	source.addEventListener('video:list', function(e) {
		var videos = JSON.parse(e.data)
		resolve(videos)
	});
});

var playerPromise = new Promise(function(resolve, reject) {
	window.addEventListener('load', function() {
		var myPlaylist = new jPlayerPlaylist({ jPlayer: "#jquery_jplayer_N", cssSelectorAncestor: "#videoContainer" }, [], {
			playlistOptions: {
				displayTime: 0
			},
			supplied: "m4v",
			useStateClassSkin: true,
			autoBlur: false,
			smoothPlayBar: false,
			keyEnabled: false,
			size: {	width: 800, height: 448, cssClass: "jp-video-480p" },
			ready: function() { resolve(myPlaylist) }
		});
	});
});

Promise.all([subscribePromise, playerPromise]).then(function(results) {
	var playlist = results[0];
	var player = results[1];

	loadPlaylist(player, playlist);

	source.addEventListener('video:new', function(e) {
		var video = JSON.parse(e.data)
		myPlaylist.add(video);
	});
});

window.addEventListener("unload", function(e) {
	source.close();
});
