angular.module('Album', [])

    .controller('AlbumCtrl', function ($scope, $http) {
        $scope.imagesurl = 'images.json';
        $scope.albumsurl = 'albums.json';
        $scope.images = [];
        $scope.allAlbums = [];
        $scope.loadedAlbums = [];
        $scope.albums = [];
        $scope.loadingStatus = false;

        function handleImagesLoaded(data, status) {

            for (var key in data) {
                var albumTimestamp = data[key]["album"];
                if (typeof $scope.images[albumTimestamp] == "undefined") {
                    $scope.images[albumTimestamp] = [];
                }
                var albumImages = $scope.images[albumTimestamp];
                albumImages[albumImages.length] = data[key];
            }
            $scope.loadingStatus = false;
        }

        function handleAlbumsLoaded(data, status) {
            $scope.allAlbums = data;
            $scope.loadMoreAlbums();
        }

        $scope.fetchImages = function (albumTimestamps) {
            $http({
                url: $scope.imagesurl,
                method: "GET",
                params: {"albums": albumTimestamps}
            }).success(handleImagesLoaded);
        }

        $scope.fetchAlbums = function () {
            $http({
                url: $scope.albumsurl,
                method: "GET"
            }).success(handleAlbumsLoaded);
        }

        $scope.loadMoreAlbums = function () {
            $scope.loadingStatus = true;
            //get unloaded albums
            var albums = $scope.allAlbums.splice(0, 20);
            $.each(albums, function () {
                $scope.loadedAlbums.push(this);
            });
            $scope.fetchImages(albums);
            $(window).scroll(scrollWatcher);
        };

        $scope.getAlbumTitle = function (albumTimestamp) {
            var date = new Date(albumTimestamp * 1000);
            return date.format("dd mmmm yyyy");
        }

        $scope.fetchAlbums();
    });


function scrollWatcher() {
    if ($(window).scrollTop() + $(window).height() > $(document).height() - 100) {
        $(window).unbind('scroll');
        $("#loadMoreAlbums").click();
    }
}

$(window).scroll(scrollWatcher);

var currentImg;
$(document).on("click", ".images img", function () {
    $("#myModalLabel").html($(this).parent().parent().prev().html());
    $('#imagemodal').modal('show');
    $('#imagepreview').on("load", function () {
        $('#imagemodal .modal-dialog').css("width", this.width + 30);
    });
    currentImg = this;
    $('#imagepreview').attr('src', '/images/medium/' + $(this).data('filename'));
    var element_to_scroll_to = document.getElementById($(this).data('filename'));
    element_to_scroll_to.scrollIntoView();
});

$(document).on('shown.bs.modal', '#imagemodal', function () {
});

$(document).keydown(function(e){
    if (e.keyCode == 37) {
        slide(false);
        return false;
    }if (e.keyCode == 39) {
        slide(true);
        return false;
    }
});

function slide(right) {
    if($('#imagemodal').attr("aria-hidden") == "false") {
        if(right) {
            var next = $(currentImg).parent().next();
            if(next.length == 0) {
                //next album
                next = $(currentImg).parent().parent().parent().next();
            }
            if(next.length != 0) {
                next.find("img").first().trigger("click");
            }
        } else {
            var prev = $(currentImg).parent().prev();
            if(prev.length == 0) {
                //prev album
                prev = $(currentImg).parent().parent().parent().prev();
            }
            if(prev.length != 0) {
                prev.find("img").last().trigger("click");
            }

        }

    }
}
