
function resetTextSize(){
    try {
        window.fontSize = parseInt(Cookies.get("font-size"), 10);
        if (isNaN(window.fontSize)) {
            window.fontSize = 100;
        }
    } catch (e) {
        window.fontSize = 100;
    }
    document.getElementById("chapter-content").style.fontSize = window.fontSize + '%';
}

function resizeText (bigger) {
    if (bigger === true) {
        step = 1;
    } else {
        step = -1;
    }
    window.fontSize = window.fontSize * Math.pow(1.2, step);
    document.getElementById("chapter-content").style.fontSize = window.fontSize + '%';
    Cookies.set('font-size', window.fontSize);
    console.log(Cookies.get('font-size'));
}

function getScrollPercentage(){
    const total_height = $(document).height();
    const current_position = $(window).scrollTop() + $(window).height();
    return Math.round(current_position / total_height * 100);
}

function scrollToPercentage(percentage){
    const total_height = $(document).height();
    const target_position = (total_height / 100 * percentage) - $(window).height();
    console.log('scrolled to ' + percentage + ' %')
    $(window).scrollTop(target_position);
}

function submitScrollPosition(callback=null) {
    const position = getScrollPercentage();
    const reading_progress = window.progress_id;
    const request = {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
        url: '/api/progress/' + reading_progress + '/',
        type: 'PATCH',
        data: JSON.stringify({'chapter_id': window.chapter_id, 'progress': position}),
        success: function(){
            $('#server-progress').text(window.current_position + ' %');
        },
        error: function (jqXhr, textStatus, errorThrown) {
            console.log('couldnt update progress');
            return errorThrown;
        }
    };
    $.ajax(request);
}
