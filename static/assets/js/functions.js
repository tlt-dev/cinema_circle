

function mark_movie_as_seen(movie_id) {

    $.ajax({
      url: '/cinema_circle/movies/' + movie_id + '/seen',
      type: 'POST',
      dataType: 'JSON',
      headers: {'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()}
    }).done(function(response){
        console.log('ici')
        $("button[name='btn_movie_watched']").removeClass('d-none');
        $("button[name='btn_mark_movie_watched']").addClass('d-none');
    })

}

function like_movie(movie_id, value) {

    $.ajax({
      url: '/cinema_circle/movies/' + movie_id + '/like/' + value,
      type: 'POST',
      dataType: 'JSON',
      headers: {'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()}
    }).done(function(response){
        if(response.value == 1){
            $("button[name='btn_dislike']").first().removeClass('d-none');
            $("button[name='btn_disliked']").addClass('d-none');
            $("button[name='btn_liked']").first().removeClass('d-none');
            $("button[name='btn_like']").addClass('d-none');
        } else {
            $("button[name='btn_dislike']").addClass('d-none');
            $("button[name='btn_disliked']").first().removeClass('d-none');
            $("button[name='btn_liked']").addClass('d-none');
            $("button[name='btn_like']").first().removeClass('d-none');
        }

    })

}


