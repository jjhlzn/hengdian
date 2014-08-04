
function SetDate(indate, exitdate) {
    var d1 = document.getElementById(indate);
    var d2 = document.getElementById('<%= this.tb_ExitDate.ClientID %>');

    var dt1 = ToDate(d1.value, 0);
    alert(dt1);
    var dt2 = ToDate(null, 90);
    //alert(CompareDate(ToDate(d1.value,0),dt1)+','+dt1.toLocaleString());

    if (CompareDate(ToDate(d1.value, 0), dt1) != -1)
        d2.value = FormatDate(dt1);

    if (dt2 < AddDays(dt1, 29))
        WdatePicker({ minDate: '#F{$dp.$D(\'indate\',{d:0});}', maxDate: '%y-%M-#{%d+90}' });
    else
        WdatePicker({ minDate: '#F{$dp.$D(\'<%= this.tb_InDate.ClientID %>\',{d:0});}', maxDate: '#F{$dp.$D(\'<%= this.tb_InDate.ClientID %>\',{d:30});}' });

}

function ToDate(str, addDays) {
    var date = (str ? new Date(str.replace("-", "/")) : new Date());
    if (addDays)
        date = AddDays(date, addDays);
    return date;
}

function AddDays(date, day) {
    date.setTime(date.getTime() + day * 24 * 3600 * 1000);
    return date;
}

function FormatDate(date) {
    var s = date.getFullYear().toString();
    var m = 1 + date.getMonth();
    s += "-" + (m > 9 ? m.toString() : "0" + m.toString());
    var d = date.getDate();
    s += "-" + (d > 9 ? d.toString() : "0" + d.toString());
    return s;
}

function CompareDate(d1, d2) {
    if (Date.parse(d1) - Date.parse(d2) == 0) {
        return 0; //相等
    }
    if (Date.parse(d1) - Date.parse(d2) < 0) {
        return 1; //结束日期 大于 开始日期
    }
    if (Date.parse(d1) - Date.parse(d2) > 0) {
        return -1; //结束日期 小于 开始日期
    }
}

function GetDateDiffDay(d1, d2) {
    var s1 = ToDate(d1, 0);
    var s2 = ToDate(d2, 0);

    var time = s2.getTime() - s1.getTime();
    return parseInt(time / (1000 * 60 * 60 * 24));
}