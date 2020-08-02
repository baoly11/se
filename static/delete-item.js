document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('#form').onsubmit = () => {
        const request = new XMLHttpRequest();
        const item_id = document.querySelector('#item_id').value;
        request.open('POST','/deleting-item');
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
        data.append('id', item_id);
        request.send(data);
        return false;
    };
});