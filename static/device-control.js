document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('#form').onsubmit = () => {
        const request = new XMLHttpRequest();
        const air = document.querySelector('#air').value;
        const fan = document.querySelector('#fan').value;
        request.open('POST','/publish-to-device');
        request.onload = () => {
            const data = JSON.parse(request.responseText);
            if (data.success) {
                alert(data.msg)
            }
            else {
                alert("There was an error!")
            }
        }
        const data = new FormData();
        data.append('air', air);
        data.append('fan', fan);
        request.send(data);
        return false;
    };
});