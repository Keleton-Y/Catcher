// 未被选中的字体颜色
let color = "#bbbbbb"

function addListener(){
    let flag = false
    let rows = document.querySelectorAll("#cache_filter tr")
    let checkboxes = document.querySelectorAll("#cache_filter input[type='checkbox']")

    for(let i = 0; i < checkboxes.length; i++){

        if (checkboxes[i].checked) {
            rows[i].style.color="inherit"
        } else {
            rows[i].style.color=color
        }

        // 防止闭包内的变量被修改
        let idx = i
        checkboxes[idx].addEventListener("change", () => {
            if (checkboxes[idx].checked) {
                rows[idx].style.color="inherit"
            } else {
                rows[idx].style.color=color
            }
            flag = true
        })

    }
    return flag
}

let id = setInterval(() => {
    let flag = addListener()
    if(flag){
        clearInterval(id)
    }
}, 200)

