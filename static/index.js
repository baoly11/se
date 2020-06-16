document.addEventListener('DOMContentLoaded',()=>{
    document.querySelector('#setting').onsubmit = function(){
        const temp = document.querySelector('#temperature').value;
        const light = document.querySelector('#light').value;
        const humidity = document.querySelector('#humidity').value;

        document.querySelector('#temperature').value = "";
        document.querySelector('#light').value = "";
        document.querySelector('#humidity').value = "";

        const request = new XMLHttpRequest();
        request.open('POST','/update');
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
        data.append('temp',temp);
        data.append('light',light);
        data.append('humidity',humidity);
        request.send(data);
        return false;
    }
    
});