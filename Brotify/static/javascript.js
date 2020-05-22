$(document).ready(() => {

    $('.tooltip').each(function() { // Grab all elements with a title attribute,and set "this"
        if(/None/g.test($(this).attr('data-*'))) {
            var text = 'Aperçu indisponible'
        }
        else {
            var text = "<video width='245' height='190' controls><source src='"+$(this).attr('data-*')+"' type='audio/mpeg'></video>"
        }
        $(this).qtip({
            style: {
                color: 'black'
            },
            content: {
                title: $(this).attr('title')+' par '+$(this).attr('alt'),
                text: text
            },
            position: {
                target: 'mouse', // Track the mouse as the positioning target
                adjust: {
                    mouse: false // Don't adjust continuously the mouse, just use initial position
                }
            },
            show: {
                solo: true
            },
            hide: false
        });
    });

    let $hamburger = $(".hamburger");
    $hamburger.on("click", () => {
        $hamburger.toggleClass("is-active");
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