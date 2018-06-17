// This is the js for the default/index.html view.


var app = function() {

    var self = {};

    Vue.config.silent = false; // show all warnings

    // Extends an array
    self.extend = function(a, b) {
        for (var i = 0; i < b.length; i++) {
            a.push(b[i]);
        }
    };

    // Enumerates an array.
    var enumerate = function(v) { var k=0; return v.map(function(e) {e._idx = k++;});};

    self.open_uploader = function () {
        $("div#uploader_div").show();
        self.vue.is_uploading = true;
    };

    self.close_uploader = function () {
        $("div#uploader_div").hide();
        self.vue.is_uploading = false;
        $("input#file_input").val(""); // This clears the file choice once uploaded.

    };

    self.upload_file = function (event) {
        // Reads the file.
        var input = event.target;
        var file = input.files[0];
        if (file) {
            // First, gets an upload URL.
            console.log("Trying to get the upload url");
            $.getJSON('https://upload-dot-luca-teaching.appspot.com/start/uploader/get_upload_url',
                function (data) {
                    // We now have upload (and download) URLs.
                    var put_url = data['signed_url'];
                    var get_url = data['access_url'];
                    console.log("Received upload url: " + put_url);
                    // Uploads the file, using the low-level interface.
                    var req = new XMLHttpRequest();
                    req.addEventListener("load", self.upload_complete(get_url));
                    // TODO: if you like, add a listener for "error" to detect failure.
                    req.open("PUT", put_url, true);
                    req.send(file);
                });
        }
    };


    self.upload_complete = function(get_url) {
        // Hides the uploader div.
        self.close_uploader();
        console.log('The file was uploaded; it is now available at ' + get_url);
        // TODO: The file is uploaded.  Now you have to insert the get_url into the database, etc.
        setTimeout(function() {
            $.post(add_image_url,
            {
                image_url: get_url,
                current_page: self.vue.current_page
            },
            function(data) {
            $.web2py.enableElement($("#add_image_url"));
            self.vue.images.push(data.image_data);
            //self.get_images(self.vue.self_id);
            enumerate(self.vue.images);
            })
        }, 1000)
    };

    function get_image_url(current_id, current_page) {
        var pp = {
            current_id: current_id,
            current_page: current_page
        }
        return images_url + "?" + $.param(pp);
    }

    self.get_images = function(cuser, cpage){
        $.getJSON(get_image_url(cuser, cpage), function(data) {
            self.vue.images = data.images;
            self.vue.ratings = data.ratings;
            self.vue.self_id = data.user_id;
            self.vue.logged_in = data.logged_in;
            if (data.user_id == 0) {
                self.vue.self_page = false;
                if (self.vue.users.length > 0) {
                    self.vue.user_id = self.vue.users[0].id;
                }
            }
            else {
                self.vue.user_id = data.user_id;
            }
            if(self.vue.logged_in == false) {
                self.vue.ratings = [];
            }
            enumerate(self.vue.images);
            enumerate(self.vue.ratings);
        })
    };

    function get_profile_image_url(current_id) {
        var pp = {
            current_id: current_id
        }
        return profile_images_url + "?" + $.param(pp);
    }

    self.get_profile_images = function(cuser){
        $.getJSON(get_profile_image_url(cuser), function(data) {
            console.log(data)
            self.vue.images = data.images;
            self.vue.ratings = data.ratings;
            self.vue.self_id = data.user_id;
            self.vue.logged_in = data.logged_in;
            if (data.user_id == 0) {
                self.vue.self_page = false;
                if (self.vue.users.length > 0) {
                    self.vue.user_id = self.vue.users[0].id;
                }
            }
            else {
                self.vue.user_id = data.user_id;
            }
            enumerate(self.vue.images);
            enumerate(self.vue.ratings);
        })
    };

    self.select_user = function(id) {
        self.vue.user_id = id;
        self.vue.self_page = (id == self.vue.self_id);
        setTimeout(function() {
            self.get_images(self.vue.user_id);
        }, 100);
    };

    self.get_user = function() {
        $.getJSON(get_user_url, 
            function(data) {
                self.vue.users = data.users;
                if (data.user_id == 0) {
                    if (self.vue.users.length > 0) {
                        self.vue.user_id = self.vue.users[0].id;
                    }
                }
                else {
                    self.vue.user_id = data.user_id;
                }
                enumerate(self.vue.users);
                setTimeout(function() {
                    self.get_images(self.vue.user_id, self.vue.current_page);
                }, 100);
            })
    };

    self.delete_images = function(index) {
        $.post(del_image_url,
        {
            id: self.vue.images[index].id
        },
        function() {
            var rmid = self.vue.images[index].id;
            self.vue.images.splice(index, 1);
            enumerate(self.vue.images);
            for(var i = 0; i < self.vue.ratings.length; i++) {
                if (self.vue.ratings[i].image_id == rmid) {
                    self.vue.ratings.splice(i, 1);
                }
            }
            enumerate(self.vue.ratings);
        })
    };

    self.toggle_pfavorite = function(index) {
        self.vue.ratings[index].favorited = !self.vue.ratings[index].favorited;
        $.post(toggle_fav_url,
            {
                image_id: self.vue.ratings[index].image_id,
                user_id: self.vue.self_id
            })

    }

    self.toggle_favorite = function(index) {
        if (self.vue.logged_in == false) {
            return 0;
        }
        var exist = false;
        var img_id= 0;
        var current_id = self.vue.images[index].id;
        
        for(i = 0; i < self.vue.ratings.length; i++) {
            if(current_id == self.vue.ratings[i].image_id) {
                exist = true;
                img_id = self.vue.ratings[i].image_id;
                self.vue.ratings[i].favorited = !self.vue.ratings[i].favorited;
            }
        }
        if (exist){
            $.post(toggle_fav_url,
                {
                    image_id: img_id,
                    user_id: self.vue.self_id
                })
        }
        else {
            $.post(add_fav_url,
                {
                    user_id: self.vue.self_id,
                    image_id: self.vue.images[index].id,
                    image_url: self.vue.images[index].image_url
                },
                function(data) {
                    self.vue.ratings.push(data.favorite_data);
                    enumerate(self.vue.ratings);
                })
        }
    };

    self.check_favorite = function(index) {
        var current_id = self.vue.images[index].id;
        for(i = 0; i < self.vue.ratings.length; i++) {
            if(current_id == self.vue.ratings[i].image_id) {
                return self.vue.ratings[i].favorited;
            }
        }
        return false;
    }

    self.check_upvote = function(index) {
        var current_id = self.vue.images[index].id;
        for(i = 0; i < self.vue.ratings.length; i++) {
            if(current_id == self.vue.ratings[i].image_id) {
                return self.vue.ratings[i].upvote;
            }
        }
        return false;
    }

    self.check_downvote = function(index) {
        var current_id = self.vue.images[index].id;
        for(i = 0; i < self.vue.ratings.length; i++) {
            if(current_id == self.vue.ratings[i].image_id) {
                return self.vue.ratings[i].downvote;
            }
        }
        return false;
    }

    self.toggle_upvote = function(index) {
        if (self.vue.logged_in == false) {
            return 0;
        }
        var exist = false;
        var img_id= 0;
        var current_id = self.vue.images[index].id;
        for(i = 0; i < self.vue.ratings.length; i++) {
            if(current_id == self.vue.ratings[i].image_id) {
                exist = true;
                img_id = self.vue.ratings[i].image_id;
                self.vue.ratings[i].upvote = !self.vue.ratings[i].upvote;
            }
        }
        if (exist){
            if (self.vue.ratings[index].upvote == true && self.vue.ratings[index].downvote == true) {
                self.vue.ratings[index].downvote = false;
                self.vue.images[index].downvotes = self.vue.images[index].downvotes - 1;
            }
            $.post(toggle_up_url,
                {
                    image_id: img_id,
                    user_id: self.vue.self_id,
                    id: self.vue.images[index].id,
                    upvote: self.vue.ratings[index].upvote,
                })
            if(self.vue.ratings[index].upvote == false) {
                self.vue.images[index].upvotes = self.vue.images[index].upvotes - 1;
                }
            if (self.vue.ratings[index].upvote == true) {
                self.vue.images[index].upvotes = self.vue.images[index].upvotes + 1;
                }
        }
        else {
            $.post(add_up_url,
                {
                    user_id: self.vue.self_id,
                    image_id: self.vue.images[index].id,
                    image_url: self.vue.images[index].image_url
                },
                function(data) {
                    self.vue.ratings.push(data.upvote_data);
                    enumerate(self.vue.ratings);
                })
            self.vue.images[index].upvotes = self.vue.images[index].upvotes + 1;
        }
    };

    self.toggle_downvote = function(index) {
        if (self.vue.logged_in == false) {
            return 0;
        }
        var exist = false;
        var img_id= 0;
        var current_id = self.vue.images[index].id;
        for(i = 0; i < self.vue.ratings.length; i++) {
            if(current_id == self.vue.ratings[i].image_id) {
                exist = true;
                img_id = self.vue.ratings[i].image_id;
                self.vue.ratings[i].downvote = !self.vue.ratings[i].downvote;
            }
        }
        if (exist){
            if (self.vue.ratings[index].upvote == true && self.vue.ratings[index].downvote == true) {
                self.vue.ratings[index].upvote = false;
                self.vue.images[index].upvotes = self.vue.images[index].upvotes - 1;
            }
            $.post(toggle_down_url,
                {
                    image_id: img_id,
                    user_id: self.vue.self_id,
                    id: self.vue.images[index].id,
                    downvote: self.vue.ratings[index].downvote,
                })
            if(self.vue.ratings[index].downvote == false) {
                self.vue.images[index].downvotes = self.vue.images[index].downvotes - 1;
                }
            if (self.vue.ratings[index].downvote == true) {
                self.vue.images[index].downvotes = self.vue.images[index].downvotes + 1;
                }
        }
        else {
            $.post(add_down_url,
                {
                    user_id: self.vue.self_id,
                    image_id: self.vue.images[index].id,
                    image_url: self.vue.images[index].image_url
                },
                function(data) {
                    self.vue.ratings.push(data.downvote_data);
                    enumerate(self.vue.ratings);
                })
            self.vue.images[index].downvotes = self.vue.images[index].downvotes + 1;
        }
    };

    self.select_page = function(change) {
        self.vue.self_page = false;
        self.vue.current_page = change;
        self.get_images(self.vue.user_id, self.vue.current_page);
    }

    self.profile_page = function() {
        self.vue.self_page = !self.vue.self_page;
        if (self.vue.self_page) {
            self.get_profile_images(self.vue.user_id);
        }
        else {
            self.vue.self_page = false;
            self.get_images(self.vue.user_id, self.vue.current_page);
        }
    }

    self.toggle_commenting = function() {
        self.vue.commenting = !self.vue.commenting;
    }

    self.add_comment = function () {
        self.vue.commenting = false;
    }

    self.toggle_fullWidthImage = function () {
        self.vue.fullWidthImage = !self.vue.fullWidthImage
    }

    self.vue = new Vue({
        el: "#vue-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        data: {
            is_uploading: false,
            self_page: false, // Leave it to true, so initially you are looking at your own images.
            images: [],
            ratings: [],
            users: [],
            user_id: 0,
            self_id: 0,
            current_page: 'ALL',
            logged_in: false,
            fullWidthImage: false,
            comment_box: null,
            commenting: false,
        },
        methods: {
            open_uploader: self.open_uploader,
            close_uploader: self.close_uploader,
            upload_file: self.upload_file,
            select_user: self.select_user,
            delete_images: self.delete_images,
            toggle_favorite: self.toggle_favorite,
            check_favorite: self.check_favorite,
            check_upvote: self.check_upvote,
            check_downvote: self.check_downvote,
            toggle_upvote: self.toggle_upvote,
            toggle_downvote: self.toggle_downvote,
            select_page: self.select_page,
            profile_page: self.profile_page,
            toggle_pfavorite: self.toggle_pfavorite,
            toggle_commenting: self.toggle_commenting,
            add_comment: self.add_comment,
            toggle_fullWidthImage: self.toggle_fullWidthImage,
        }

    });
    
    self.get_user();
    $("#vue-div").show();

    return self;
};

var APP = null;

// This will make everything accessible from the js console;
// for instance, self.x above would be accessible as APP.x
jQuery(function(){APP = app();});

