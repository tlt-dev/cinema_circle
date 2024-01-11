function mark_movie_as_seen(movie_id) {

    $.ajax({
        url: '/cinema_circle/movies/' + movie_id + '/seen',
        type: 'POST',
        dataType: 'JSON',
        headers: {'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()}
    }).done(function (response) {
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
    }).done(function (response) {
        if (response.value == 1) {
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

function follow_user(id, value) {

    $.ajax({
        url: '/cinema_circle/user/' + id + '/follow/' + value,
        type: 'POST',
        dataType: 'JSON',
        headers: {'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()}
    }).done(function (response) {
        if (response.value == 1) {
            $("#btn_unfollow").removeClass('d-none');
            $("#btn_follow").addClass('d-none');
        } else {
            $("#btn_unfollow").addClass('d-none');
            $("#btn_follow").removeClass('d-none');
        }

    })

}

function get_users_activities_overview(filter) {

    $.ajax({
        url: '/cinema_circle/admin/users_activities_overview/' + filter,
        method: 'GET',
        dataType: 'JSON'
    }).done(function (response) {
        $("#row_uo_filter > div > button").removeClass('active')
        $("#buo_" + response.filter).addClass('active')

        $('#row_user_activity_overview').empty()

        $.each(response.overview, function (index, value) {
            $("#row_user_activity_overview").append(
                '<div class="col-3 bg-dark rounded text-center mx-auto">' +
                '    <div class="row">' +
                '        <div class="col pt-3">' +
                '            <h5>'+ value.statistic +'</h5>' +
                '            <p>'+ value.title +'</p>' +
                '        </div>' +
                '     </div>' +
                '</div>'
            )
        })
    })

}

function get_users_activities(filter) {

    $.ajax({
        url: '/cinema_circle/admin/users_activities/' + filter,
        method: 'GET',
        dataType: 'JSON'
    }).done(function (response) {

        $("#row_ua_filter > div > button").removeClass('active')
        $("#bua_" + response.filter).addClass('active')

        $('#row_users_activities').empty()

        $.each(response.activities, function (index, value) {
            $("#row_users_activities").append(
                '<div class="col-3 bg-dark rounded text-center p-0 me-2 ms-5 mt-2">' +
                '    <div class="row">' +
                '        <div class="col pt-3">' +
                '            <h5>'+ value.statistic +'</h5>' +
                '            <p>'+ value.title +'</p>' +
                '        </div>' +
                '     </div>' +
                '</div>'
            )
        })
    })

}

function get_users_networking_activities(filter) {

    $.ajax({
        url: '/cinema_circle/admin/users_networking_activities/' + filter,
        method: 'GET',
        dataType: 'JSON'
    }).done(function (response) {

        $("#row_na_filter > div > button").removeClass('active')
        $("#bna_" + response.filter).addClass('active')

        $('#row_networking_activities').empty()

        $.each(response.activities, function (index, value) {
            $("#row_networking_activities").append(
                '<div class="col-3 bg-dark rounded text-center mx-auto">' +
                '    <div class="row">' +
                '        <div class="col pt-3">' +
                '            <h5>'+ value.statistic +'</h5>' +
                '            <p>'+ value.title +'</p>' +
                '        </div>' +
                '     </div>' +
                '</div>'
            )
        })
    })

}


function get_movie_statistics() {

    $.ajax({
        url: '/cinema_circle/admin/movie_statistics',
        method: 'GET',
        dataType: 'JSON'
    }).done(function (response) {
        $('#row_movies_overview').empty()
        $('#row_movies_per_genre').empty()
        $('#row_popular_genres').empty()
        $('#row_detailled_statistics').empty()

        $.each(response.overview, function (index, value) {
            $("#row_movies_overview").append(
                '<div class="col-3 bg-dark rounded text-center mx-auto">' +
                '    <div class="row">' +
                '        <div class="col pt-3">' +
                '            <h5>'+ value.statistic +'</h5>' +
                '            <p>'+ value.title +'</p>' +
                '        </div>' +
                '     </div>' +
                '</div>'
            )
        })

        $.each(response.movies_per_genre, function (index, value) {
            $("#row_movies_per_genre").append(
                '<div class="col-3 bg-dark rounded text-center p-0 me-2 ms-5 mt-2">' +
                '    <div class="row">' +
                '        <div class="col pt-3">' +
                '            <h5>'+ value.statistic +'</h5>' +
                '            <p>'+ value.title +'</p>' +
                '        </div>' +
                '     </div>' +
                '</div>'
            )
        })

        $.each(response.popular, function (index, value) {
            $("#row_popular_genres").append(
                '<div class="col-3 bg-dark rounded text-center p-0 me-2 ms-5 mt-2">' +
                '    <div class="row">' +
                '        <div class="col pt-3">' +
                '            <h5>'+ value.statistic +'</h5>' +
                '            <p>'+ value.title +'</p>' +
                '        </div>' +
                '     </div>' +
                '</div>'
            )
        })

        $.each(response.detailled_statistics, function (index, value) {
            $("#row_detailled_statistics").append(
                '<div class="col-3 bg-dark rounded text-center mx-auto">' +
                '    <div class="row">' +
                '        <div class="col pt-3">' +
                '            <h5>'+ value.statistic +'</h5>' +
                '            <p>'+ value.title +'</p>' +
                '        </div>' +
                '     </div>' +
                '</div>'
            )
        })
    })

}

function get_popular_genres(filter) {

    $.ajax({
        url: '/cinema_circle/admin/popular_genres/' + filter,
        method: 'GET',
        dataType: 'JSON'
    }).done(function (response) {

        $("#row_pg_filter > div > button").removeClass('active')
        $("#bpg_" + response.filter).addClass('active')

        $('#row_popular_genres').empty()

        $.each(response.popular, function (index, value) {
            $("#row_popular_genres").append(
                '<div class="col-3 bg-dark rounded text-center p-0 me-2 ms-5 mt-2">' +
                '    <div class="row">' +
                '        <div class="col pt-3">' +
                '            <h5>'+ value.statistic +'</h5>' +
                '            <p>'+ value.title +'</p>' +
                '        </div>' +
                '     </div>' +
                '</div>'
            )
        })
    })

}

function get_popular_genres(filter) {

    $.ajax({
        url: '/cinema_circle/admin/popular_genres/' + filter,
        method: 'GET',
        dataType: 'JSON'
    }).done(function (response) {

        $("#row_pg_filter > div > button").removeClass('active')
        $("#bpg_" + response.filter).addClass('active')

        $('#row_popular_genres').empty()

        $.each(response.popular, function (index, value) {
            $("#row_popular_genres").append(
                '<div class="col-3 bg-dark rounded text-center p-0 me-2 ms-5 mt-2">' +
                '    <div class="row">' +
                '        <div class="col pt-3">' +
                '            <h5>'+ value.statistic +'</h5>' +
                '            <p>'+ value.title +'</p>' +
                '        </div>' +
                '     </div>' +
                '</div>'
            )
        })
    })

}

function get_detailled_statistics(filter) {

    $.ajax({
        url: '/cinema_circle/admin/detailled_statistics/' + filter,
        method: 'GET',
        dataType: 'JSON'
    }).done(function (response) {

        $("#row_ds_filter > div > button").removeClass('active')
        $("#bds_" + response.filter).addClass('active')

        $('#row_detailled_statistics').empty()

        $.each(response.detailled_statistics, function (index, value) {
            $("#row_detailled_statistics").append(
                '<div class="col-3 bg-dark rounded text-center mx-auto">' +
                '    <div class="row">' +
                '        <div class="col pt-3">' +
                '            <h5>'+ value.statistic +'</h5>' +
                '            <p>'+ value.title +'</p>' +
                '        </div>' +
                '     </div>' +
                '</div>'
            )
        })
    })

}




