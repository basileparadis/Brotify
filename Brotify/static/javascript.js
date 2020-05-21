$(document).ready(() => {

    let $hamburger = $(".hamburger");
    $hamburger.on("click", () => {
        $( "#navigation" ).animate({
            width: "toggle",
            height: "toggle"
        }, {
            duration: 300,
        });
    });

    $('#un-ami').parent().mouseover(() => {
        $('#un-ami').parent().attr('class', 'button is-rounded is-inverted is-danger');
        $('#un-ami').attr('class', 'fas fa-user-times');
    });

    $('#un-ami').parent().mouseout(() => {
        $('#un-ami').parent().attr('class', 'button is-rounded is-inverted is-primary');
        $('#un-ami').attr('class', 'fas fa-user-check');
    });

});