window.dccFunctions = window.dccFunctions || {}

window.dccFunctions.timeFormat = function(value) {

    // 使用Date对象来转换时间戳
    let date = new Date(value * 1000);  // 乘以1000将秒转换为毫秒

    // 使用Date对象的方法来获取小时和分钟部分
    let hours = date.getHours();
    let minutes = date.getMinutes();

    return hours.toString() + ":" + minutes.toString().padStart(2, '0')
}

