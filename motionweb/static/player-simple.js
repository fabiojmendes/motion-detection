var playlist;
var currentVideo;

function save(key, object) {
	localStorage.setItem(key, JSON.stringify(object));
}

function load(key) {
	return JSON.parse(localStorage.getItem(key));
}

function setCurrent(video) {
	currentVideo = video;
	$('#videoarea').prop('src', video.m4v);
	$('#videoarea').prop('autoplay', true);
}

function loadPlaylist() {
	$.ajax('/playlist').done(function(pl) {
		playlist = pl

		playlist.forEach(function(video) {
			var item = $('<button type="button" class="list-group-item">');
			item.data('video', video);
			item.text(video.title);
			$('#playlist').append(item)
		});

		var currentVideo = load('currentVideo');
		if (currentVideo) {
			var candidate = playlist[currentVideo.index];
			if (candidate && candidate.filename == currentVideo.filename) {
				if (currentVideo.ended && playlist.length - currentVideo.index > 1) {
					setCurrent(playlist[currentVideo.index + 1])
				} else {
					setCurrent(playlist[currentVideo.index])
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
	loadPlaylist()

	$('#playlist').on('click', 'button', function() {
		var video = $(this).data('video');
		$('#playlist button.active').removeClass('active');
		$(this).addClass('active')
		setCurrent(video);
		return false;
	});
});
