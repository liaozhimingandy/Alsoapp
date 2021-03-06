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
        matchContains: true,
        cache: false,
        // object to local or url to remote search
        // source: colors,
        // 请求后台数据
        source: 'sug',
        // custom template
        //template: '{{ label }} <span>({{ hex }})</span>',
        // 不能替换lable,否则报错;'{{ label }}<span>{{ count }}</span>',内容需要空格隔开
        // customValue: "label",
        template: '{{ label }}',
        // show hint
        hint: true,

        // abort source if empty field
        empty: false,

        // max results
        limit: 8,

        callback: function (value, index, selected) {
            // console.info("value=" + value);
            if (selected) {
                // $('.icon').css('background-color', selected.hex);
                console.info("您选择了:"+selected.label+"(" + selected.count + ")");

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

    const wd = $('input[id="kw"]').val().trim();
    if (wd === '' || wd.length === 0) {
        // 重新定位到本页面
        window.open("/", "_self");
        return;
    }
    var tsn = $(".also-tag").attr("name");
    if (tsn === '' || tsn === undefined) {
        tsn = "also";
    }
    // alert(tsn);
    // 对url参数进行编码处理
    // window.open("s?tn=" + tsn + "&wd=" + escape(wd), "_self");
    window.open("s?tn=" + tsn + "&wd=" + encodeURIComponent(wd), "_self");

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
        to_search();
    }
}
