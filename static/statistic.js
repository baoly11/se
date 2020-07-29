document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('#form').onsubmit = () => {
        const request = new XMLHttpRequest();
        const day_s = document.querySelector('#day_s').value;
        const month_s = document.querySelector('#month_s').value;
        const year_s = document.querySelector('#year_s').value;
        const hour_s = document.querySelector('#hour_s').value;
        const minute_s = document.querySelector('#minute_s').value;

        const day_f = document.querySelector('#day_f').value;
        const month_f = document.querySelector('#month_f').value;
        const year_f = document.querySelector('#year_f').value;
        const hour_f = document.querySelector('#hour_f').value;
        const minute_f = document.querySelector('#minute_f').value;

        request.open('POST', '/get-info-for-report');
        request.onload = () => {
            const data = JSON.parse(request.responseText);
            if (data.success) {
                alert("ok");
            }
            else {
                alert("not ok");
            }
        }

        const data = new FormData();
        data.append('day_s', day_s);
        data.append('month_s', month_s);
        data.append('year_s', year_s);
        data.append('hour_s', hour_s);
        data.append('minute_s', minute_s);
        data.append('day_f', day_f);
        data.append('month_f', month_f);
        data.append('year_f', year_s);
        data.append('hour_f', hour_f);
        data.append('minute_f', minute_f);
        request.send(data);
        return false;
    };
});