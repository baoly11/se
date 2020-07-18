document.addEventListener('DOMContentLoaded', () => {

    document.querySelector('#form').onsubmit = () => {
        const request = new XMLHttpRequest();
        const id = document.querySelector('#id').value;
        request.open('POST', '/get-order');

        request.onload = () => {
            const data = JSON.parse(request.responseText);

            if (data.success) {
                if (data.found) {
                    const r_id = data.id;
                    const name = data.name
                    const item = data.item;
                    const quantity = data.quantity;
                    const status = data.status;
                    const date = data.date;

                    document.querySelector('#r_id').innerHTML = `ID: ${r_id}`;
                    document.querySelector('#order_name').innerHTML = `Name: ${name}`;
                    document.querySelector("#item_list").innerHTML = ''
                    document.querySelector('#status').innerHTML = `Completed: ${status}`
                    var i
                    for (i = 0; i < item.length; i++) {
                        var l = `Item: ${item[i]} ------------------------ Quantity: ${quantity[i]}`
                        document.querySelector("#item_list").innerHTML += ('<li>' + l + '</li>')
                    }
                 }
                 else {
                    alert("Cannot find order!");
                 }
            }
            else {
                alert("There was an error!")
            }
        }
        const data = new FormData();
        data.append('id', id);

        request.send(data);
        return false;

    };


});