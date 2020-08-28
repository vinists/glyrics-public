
$(document).ready(function(){
    
    var socket = io.connect('//' + document.domain + ':' + location.port + '/data', {secure: true});

    var targetObj = {};
    var targetProxy = new Proxy(targetObj, {
    set: function (target, key, value) {
        $(document).ready(function(){
            $(window).scrollTop(0);
        });
        target[key] = value;
        return true;
    }
    });
    targetProxy.title = "";

    socket.on('newsong', function(body){
        //Lyrics[0][0]
        //URL[0][1]
        //Title[1]

        if (body.lyricsBody[1] != targetProxy.title){
            targetProxy.title = body.lyricsBody[1];
        }


        if(body.lyricsBody[0] == null){
            
            $('#lyrics').html("<h3> Couldn't find lyrics for this song: </h3><br>");
            $('#err').html(targetProxy.title)
            $('#url').html("");

        }else{
            $('#url').attr("href", body.lyricsBody[0][1]).html(targetProxy.title);
            $('#lyrics').html('<p>' + body.lyricsBody[0][0] + '</p>');
            $('#err').html("")
        }
    });
    


});