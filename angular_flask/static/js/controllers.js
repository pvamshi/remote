'use strict';

/* Controllers */

function IndexController($scope,$http) {
	var fetch_files = function(pathdir){
		$http.get('/files/'+pathdir).
  		success(function(data, status, headers, config) {
	    	$scope.files = data
	    	$scope.path = pathdir;
	    // this callback will be called asynchronously
	    // when the response is available
		}).
		error(function(data, status, headers, config) {
		    // called asynchronously if an error occurs
		    // or server returns response with an error status.
		});
	}

	var play = function(pathfile){
		if($scope.playing){
			return;
		}
		$http.get('/player/play/'+pathfile)
			.success(function(data){
				$scope.playing = true;
			});
	};

	$scope.playing = false;
	$scope.path = "";
	fetch_files('+home+vamshi');
	$scope.deeper = function(file){
		if(file.dir){
			fetch_files($scope.path+'+'+file.name);
		}else{
			play($scope.path+'+'+file.name);
		}
	};
	
	$scope.player = {};
	$scope.player.pause = function(){
		$http.get('/player/pause')
			.success(function(data){

			});
	};

	$scope.player.fullscreen = function(){
		$http.get('/player/fullscreen')
			.success(function(data){

			});
	};

	$scope.player.stop = function(){
		$http.get('/player/stop')
			.success(function(data){
				$scope.playing = false;
			});
	};
	
	$scope.player.up = function(){
		$http.get('/player/volume/up')
			.success(function(data){
				
			});
	};
	
	$scope.player.down = function(){
		$http.get('/player/volume/down')
			.success(function(data){
				
			});
	};

	$scope.validate = function(file){
		if(file.name[0] ==='.'){
			return false;
		}
		if(!file.dir){
			var extension_list = file.name.split('.');
			var extension = extension_list[extension_list.length - 1];
			console.log(extension);

			return (['mp3','mp4','avi','mkv'].indexOf(extension) != -1)
		}
		return true;
	};	
}

function AboutController($scope) {
	
}

function PostListController($scope, Post) {
	var postsQuery = Post.get({}, function(posts) {
		$scope.posts = posts.objects;
	});
}

function PostDetailController($scope, $routeParams, Post) {
	var postQuery = Post.get({ postId: $routeParams.postId }, function(post) {
		$scope.post = post;
	});
}
