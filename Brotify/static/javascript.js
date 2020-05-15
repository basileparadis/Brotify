$(document).ready(() => {

    $('#un-ami').parent().mouseover(() => {
        $('#un-ami').parent().attr('class', 'button is-rounded is-inverted is-danger');
        $('#un-ami').attr('class', 'fas fa-user-times');
    });

    $('#un-ami').parent().mouseout(() => {
        $('#un-ami').parent().attr('class', 'button is-rounded is-inverted is-primary');
        $('#un-ami').attr('class', 'fas fa-user-check');
    });

});