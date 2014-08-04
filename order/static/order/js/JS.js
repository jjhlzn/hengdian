// 检测所有
function CheckAll(form) {
    for (var i = 0; i < form.elements.length; i++) {
        var e = form.elements[i];
        if (e.name != 'chkall') e.checked = form.chkall.checked;
    }
}

// 选择所有
function selectCheck(commandname) {
    var inputs = document.all.tags("input");
    var selectedLen = 0;
    for (var i = 0; i < inputs.length; i++) {
        if (inputs[i].type == "checkbox") {
            if (inputs[i].checked) {
                if (inputs[i].id != "CheckAll") {
                    selectedLen++;
                }
            }
        }
    }
    if (selectedLen == 0) {
        alert("请先选择您要" + commandname + "的数据！");
        return false;
    }
    else {
        return confirm("您确定要" + commandname + "所选择的这 " + selectedLen + " 条数据吗？");
    }
}

//去除左空格
function LTrim(str) {
    var whitespace = new String(" \t\n\r");
    var s = new String(str);

    if (whitespace.indexOf(s.charAt(0)) != -1) {
        var j = 0, i = s.length;
        while (j < i && whitespace.indexOf(s.charAt(j)) != -1) {
            j++;
        }
        s = s.substring(j, i);
    }

    return s;
}

//去除右空格：
function RTrim(str) {
    var whitespace = new String(" \t\n\r");
    var s = new String(str);

    if (whitespace.indexOf(s.charAt(s.length - 1)) != -1) {
        var i = s.length - 1;

        while (i >= 0 && whitespace.indexOf(s.charAt(i)) != -1) {
            i--;
        }

        s = s.substring(0, i + 1);
    }

    return s;
}

//去除左右空格
function Trim(str) {
    return RTrim(LTrim(str));
}