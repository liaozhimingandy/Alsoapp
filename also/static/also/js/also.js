const colors =
    [
        {
            "hex": "#EFDECD",
            "label": "Almond",
            "rgb": "(239, 222, 205)"
        },
        {
            "hex": "#CD9575",
            "label": "Antique Brass",
            "rgb": "(205, 149, 117)"
        }
    ];
$(function () {
    $('#kw').autocompleter({
        // marker for autocomplete matches
        highlightMatches: true,

        // object to local or url to remote search
        // source: colors,
        // 请求后台数据
        source: 'sug',
        // custom template
        //template: '{{ label }} <span>({{ hex }})</span>',
        template: '{{ label }}',
        // show hint
        hint: true,

        // abort source if empty field
        empty: false,

        // max results
        limit: 5,

        callback: function (value, index, selected) {
            // console.info("value=" + value);
            if (selected) {
                // $('.icon').css('background-color', selected.hex);
                console.info(selected.label);
            }
        }
    });
});

// 文档准备好事件
//  document.ready(function(){
//       //console.info($('#kw').outerWidth());
//       //$('autocompleter').outerWidth($('#kw').outerWidth())
//
//   });

//搜索按钮触发事件处理
function to_search(event) {

    var q = $('input[id="kw"]').val();
    if (q === '' || q.length === 0) {
        // 重新定位到本页面
        window.open("/", "_self");
    }
    var tsn = $(".also-tag").attr("name");
    if (tsn === '' || tsn === undefined) {
        tsn = "also";
    }
    window.open("s?tn=" + tsn + "&q=" + $('input[id="kw"]').val(), '_blank');

}

// 按键触发事件处理
function enter_search(event) {
    var e = event || window.event || arguments.callee.caller.arguments[0];
    if (e && e.keyCode === 27) { // 按 Esc
        //要做的事情
    }
    if (e && e.keyCode === 113) { // 按 F2
        //要做的事情
    }
    if (e && e.keyCode === 13) { // enter 键
        //alert("此处回车触发搜索事件");
        to_search()
    }
}
