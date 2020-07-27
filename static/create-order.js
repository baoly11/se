document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('#form').onsubmit = () => {
        const request = new XMLHttpRequest();
        const name = document.querySelector('#name').value;
        request.open('POST','/creating-order');
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
        data.append('name', name);
        request.send(data);
        return false;
    };
});