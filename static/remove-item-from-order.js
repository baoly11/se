document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('#form').onsubmit = () => {
        const request = new XMLHttpRequest();
        const item_id = document.querySelector('#itemId').value;
        request.open('POST','/removing-item');
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
        data.append('itemId', item_id);
        request.send(data);
        return false;
    };
});