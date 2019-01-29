$(function () {
    $.each($("#treeMenu").find("a"), function(index, value) {
        if ($(value).attr("href") == window.location.pathname) {
            $(value).parent().addClass("active");
            if ($(value).parent().parent().attr("id") != "treeMenu") {
                $('#treeMenu').tree('expand', $(value).parent().parent().parent());
            }
            return
        }
    })
})
