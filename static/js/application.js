
$(document).ready(function(){
    
    var socket = io.connect('//' + document.domain + ':' + location.port + '/data', {secure: true});
    var title;

    socket.on('newsong', function(body){
        //Lyrics[0][0]
        //URL[0][1]
        //Title[1]


        title = body.lyricsBody[1];

        if(body.lyricsBody[0] == null){

            
            $('#lyrics').html("<h3> Couldn't find lyrics for this song: </h3><br>");
            $('#err').html(title)

            $('#url').html("");

        }else{
            $('#url').attr("href", body.lyricsBody[0][1]).html(title);
            $('#lyrics').html('<p>' + body.lyricsBody[0][0] + '</p>');
            $('#err').html("")
        }
    });
    
});