var modal_add_review = document.getElementById('modal_add_review')
var modal_add_review_title_input = document.getElementById('modal_add_review_title')

modal_add_review.addEventListener('shown.bs.modal', function () {
  modal_add_review_title_input.focus()
})



