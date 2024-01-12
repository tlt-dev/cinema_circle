function mark_movie_as_seen(movie_id) {

    $.ajax({
        url: '/cinema_circle/movies/' + movie_id + '/seen',
        type: 'POST',
        dataType: 'JSON',
        headers: {'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()}
    }).done(function (response) {
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
                '            <h5>' + value.statistic + '</h5>' +
                '            <p>' + value.title + '</p>' +
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
                '            <h5>' + value.statistic + '</h5>' +
                '            <p>' + value.title + '</p>' +
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
                '            <h5>' + value.statistic + '</h5>' +
                '            <p>' + value.title + '</p>' +
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
                '            <h5>' + value.statistic + '</h5>' +
                '            <p>' + value.title + '</p>' +
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
                '            <h5>' + value.statistic + '</h5>' +
                '            <p>' + value.title + '</p>' +
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
                '            <h5>' + value.statistic + '</h5>' +
                '            <p>' + value.title + '</p>' +
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
                '            <h5>' + value.statistic + '</h5>' +
                '            <p>' + value.title + '</p>' +
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
                '            <h5>' + value.statistic + '</h5>' +
                '            <p>' + value.title + '</p>' +
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
                '            <h5>' + value.statistic + '</h5>' +
                '            <p>' + value.title + '</p>' +
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
                '            <h5>' + value.statistic + '</h5>' +
                '            <p>' + value.title + '</p>' +
                '        </div>' +
                '     </div>' +
                '</div>'
            )
        })
    })

}

function get_movies_list(page = 1) {

    $.ajax({
        url: '/cinema_circle/admin/movie_list/' + page,
        type: 'GET',
        dataType: 'JSON'
    }).done(function (response) {
        next_page = page + 1
        $("#link_next_page").attr('onclick', 'get_movies_list(' + next_page + ')')

        $.each(response.movies, function (index, value) {
            $("#table_movies").append(
                '<tr id="row_' + value._id.$oid + '">' +
                '<td>' + value._id.$oid + '</td>' +
                '<td id="row_' + value._id.$oid + '_title">' + value.title + '</td>' +
                '<td id="row_' + value._id.$oid + '_release_date">' + new Date(value.release_date.$date).toLocaleDateString('it-IT') + '</td>' +
                '<td id="row_' + value._id.$oid + '_runtime">' + value.runtime + '</td>' +
                '<td><button class="btn btn-outline-primary" onclick="showModalMovie(\'' + value._id.$oid + '\')">Edit</button></td>' +
                '<td><button class="btn btn-outline-danger" onclick="deleteMovie(\'' + value._id.$oid + '\')">Delete</button></td>' +
                '</tr>'
            )
        })

    })

}

function deleteMovie(movie_id) {

    $.ajax({
        url: '/cinema_circle/admin/movie/' + movie_id + '/delete',
        type: 'POST',
        dataType: 'JSON',
        headers: {'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()},
    }).done(function (response) {
        $('#row_' + response.movie_id).remove()
    })

}

function showModalMovie(id = null) {

    var modal_movie = new bootstrap.Modal(document.getElementById('modal_movie'))

    var genres = ['Drama', 'Crime', 'History', 'War', 'Comedy', 'Romance', 'Animation', 'Family', 'Fantasy', 'Thriller', 'Action', 'Adventure', 'Western', 'Horror', 'Music', 'Science Fiction', 'Mystery', 'TV Movie', 'Documentary']

    $.each(genres, function (index, genre) {
        $("#genre").append(
            '<option value="' + genre + '">' + genre + '</option>'
        )
    })

    $.ajax({
        url: '/cinema_circle/admin/movie/' + id,
        type: 'GET',
        dataType: 'JSON'
    }).done(function (response) {

        $('input[name="movie_id"]').val(response.id)
        $('input[name="title"]').val(response.title)

        date = new Date(response.release_date.$date)
        var day = ("0" + date.getDate()).slice(-2);
        var month = ("0" + (date.getMonth() + 1)).slice(-2);
        release_date = date.getFullYear() + "-" + month + "-" + day
        if (release_date != "Invalid Date") {
            $('input[name="release_date"]').val(release_date)
        } else {
            $('input[name="release_date"]').val('-')
        }

        $('input[name="runtime"]').val(response.runtime)
        $('textarea[name="overview"]').val(response.overview)
        $('#genre').val(response.genre[0])

    })

    modal_movie.show()

}

window.addEventListener('DOMContentLoaded', function () {
    $('#form_movie').on('submit', function (e) {
        e.preventDefault();
        return false
    })
});


function saveModalMovie() {

    id = $("input[name='movie_id']").val()

    // TODO : if fields pas remplis, on renvoit vers le formulaire
    title = $("input[name='title").val()
    release_date = $("input[name='release_date").val()
    runtime = $("input[name='runtime").val()
    overview = $("textarea[name='overview']").val()

    if (title == '' || release_date == '' || runtime == '' || overview == '') {
        return false
    }

    if (id == "") {
        $.ajax({
            url: '/cinema_circle/admin/add/movie',
            type: 'POST',
            dataType: 'JSON',
            headers: {'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()},
            data: {
                "title": $("input[name='title").val(),
                "release_date": $("input[name='release_date']").val(),
                "genre": $("#genre").val(),
                "runtime": $("input[name='runtime']").val(),
                "overview": $("textarea[name='overview']").val()
            }
        }).done(function (response) {
            $("#table_movies").prepend(
                '<tr id="row_' + response.movie_id + '">' +
                '<td >' + response.movie_id + '</td>' +
                '<td id="row_' + response.movie_id + '_title">' + title + '</td>' +
                '<td id="row_' + response.movie_id + '_release_date">' + release_date + '</td>' +
                '<td id="row_' + response.movie_id + '_runtime">' + runtime + '</td>' +
                '<td><button class="btn btn-outline-primary" onclick="showModalMovie(\'' + response.movie_id + '\')">Edit</button></td>' +
                '<td><button class="btn btn-outline-danger" onclick="deleteMovie(\'' + response.movie_id + '\')">Delete</button></td>' +
                '</tr>'
            )
        })
    } else {
        $.ajax({
            url: '/cinema_circle/admin/movie/' + id + '/edit',
            type: 'POST',
            dataType: 'JSON',
            headers: {'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()},
            data: {
                "title": $("input[name='title").val(),
                "release_date": $("input[name='release_date']").val(),
                "genre": $("#genre").val(),
                "runtime": $("input[name='runtime']").val(),
                "overview": $("textarea[name='overview']").val()
            }
        }).done(function (response) {
            $("#row_" + response.movie_id + "_title").text(title)
            $("#row_" + response.movie_id + "_release_date").text(release_date)
            $("#row_" + response.movie_id + "_runtime").text(runtime)
        })
    }

    resetModalMovie()
    $('#modal_movie').modal('hide');

}

function resetModalMovie() {

    $('input[name="movie_id"]').val('')
    $('input[name="title"]').val('')
    $('input[name="release_date"]').val('')
    $('input[name="genre"]').val('')
    $('input[name="runtime"]').val('')
    $('textarea[name="overview"]').val('')

}


function get_users_list(page = 1) {

    $.ajax({
        url: '/cinema_circle/admin/user_list/' + page,
        type: 'GET',
        dataType: 'JSON'
    }).done(function (response) {
        next_page = page + 1
        $("#link_next_user_page").attr('onclick', 'get_users_list(' + next_page + ')')

        $.each(response.users, function (index, value) {
            $("#table_users").append(
                '<tr id="row_' + value._id.$oid + '">' +
                '<td>' + value._id.$oid + '</td>' +
                '<td id="row_' + value._id.$oid + '_first_name">' + value.first_name + '</td>' +
                '<td id="row_' + value._id.$oid + '_last_name">' + value.last_name + '</td>' +
                '<td id="row_' + value._id.$oid + '_email">' + value.email + '</td>' +
                '<td><button class="btn btn-outline-primary" onclick="showModalUser(\'' + value._id.$oid + '\')">Edit</button></td>' +
                '<td><button class="btn btn-outline-danger" onclick="deleteUser(\'' + value._id.$oid + '\')">Delete</button></td>' +
                '</tr>'
            )
        })

    })

}

function deleteUser(user_id) {

    $.ajax({
        url: '/cinema_circle/admin/user/' + user_id + '/delete',
        type: 'POST',
        dataType: 'JSON',
        headers: {'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()},
    }).done(function (response) {
        $('#row_' + response.user_id).remove()
    })

}

function showModalUser(id = null) {

    var modal_user = new bootstrap.Modal(document.getElementById('modal_user'))

    $.ajax({
        url: '/cinema_circle/admin/user/' + id,
        type: 'GET',
        dataType: 'JSON'
    }).done(function (response) {
        console.log(response.admin)
        $('input[name="user_id"]').val(response.id)
        $('input[name="first_name"]').val(response.first_name)
        $('input[name="last_name"]').val(response.last_name)
        $('input[name="email"]').val(response.email)
        $('input[name="password"]').val(response.password)
        if(response.admin == true) {
            $("#admin").val("true")
        } else {
            $("#admin").val("false")
        }

    })

    modal_user.show()

}

window.addEventListener('DOMContentLoaded', function () {
    $('#form_user').on('submit', function (e) {
        e.preventDefault();
        return false
    })
});


function saveModalUser() {

    id = $("input[name='user_id']").val()

    first_name = $("input[name='first_name").val()
    last_name = $("input[name='last_name").val()
    email = $("input[name='email").val()
    password = $("input[name='password").val()

    if (first_name == '' || last_name == '' || password == '' || email == '') {
        return false
    }

    if (id == "") {
        $.ajax({
            url: '/cinema_circle/admin/add/user',
            type: 'POST',
            dataType: 'JSON',
            headers: {'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()},
            data: {
                "first_name": $("input[name='first_name").val(),
                "last_name": $("input[name='last_name']").val(),
                "email": $("input[name='email']").val(),
                "password": $("input[name='password']").val(),
                "admin": $('#admin').val()
            }
        }).done(function (response) {
            console.log(response.user_id)
            $("#table_users").prepend(
                '<tr id="row_' + response.user_id + '">' +
                '<td>' + response.user_id + '</td>' +
                '<td id="row_' + response.user_id + '_first_name">' + first_name + '</td>' +
                '<td id="row_' + response.user_id + '_last_name">' + last_name + '</td>' +
                '<td id="row_' + response.user_id + '_email">' + email + '</td>' +
                '<td><button class="btn btn-outline-primary" onclick="showModalUser(\'' + response.user_id + '\')">Edit</button></td>' +
                '<td><button class="btn btn-outline-danger" onclick="deleteUser(\'' + response.user_id + '\')">Delete</button></td>' +
                '</tr>'
            )
        })
    } else {
        $.ajax({
            url: '/cinema_circle/admin/user/' + id + '/edit',
            type: 'POST',
            dataType: 'JSON',
            headers: {'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()},
            data: {
                "first_name": $("input[name='first_name").val(),
                "last_name": $("input[name='last_name']").val(),
                "email": $("input[name='email']").val(),
                "password": $("input[name='password']").val(),
                "admin": $('#admin').val()
            }
        }).done(function (response) {
            $("#row_" + response.user_id + "_first_name").text(first_name)
            $("#row_" + response.user_id + "_last_name").text(last_name)
            $("#row_" + response.user_id + "_email").text(email)
        })
    }

    resetModalUser()
    $('#modal_user').modal('hide');

}

function resetModalUser() {

    $('input[name="user_id"]').val('')
    $('input[name="first_name"]').val('')
    $('input[name="last_name"]').val('')
    $('input[name="email"]').val('')

}



