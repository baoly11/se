document.addEventListener('DOMContentLoaded',()=>{
    document.querySelector('#import').onsubmit = function(){
       
        const item_id = document.querySelector("#item_id").value;
        const item_name = document.querySelector('#item_name').value;
        const item_quantity = document.querySelector('#item_quantity').value;
        const import_man = document.querySelector('#import_man').value;

        console.log(typeof(item_id),typeof(item_name),typeof(item_quantity),typeof(import_man));
        document.querySelector("#item_id").value="";
        document.querySelector('#item_name').value="";      
        document.querySelector('#item_quantity').value="";
        document.querySelector('#import_man').value="";

        const request = new XMLHttpRequest();
        request.open('POST','/import');
        request.onload = function(){
            const data = JSON.parse(request.responseText);
            if(data.success){
                const contents = `${data.response}`
                alert(contents);
            }
            else{
                alert('There was an error');
            }
        }

        const data = new FormData();
        data.append('item_id',item_id);
        data.append('item_name',item_name);
        data.append('item_quantity',item_quantity);
        data.append('import_man',import_man);

        request.send(data);
        return false;
    }

});