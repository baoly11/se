document.addEventListener('DOMContentLoaded',()=>{
    getDataHourly();

    function getDataHourly(){
        setInterval(() => {
            updateInforamtion();
        }, 1000*10);
    }
    function updateInforamtion(){
        const request = new XMLHttpRequest();
        request.open('POST','/updateHomepage');
        request.onload = function(){
            const data = JSON.parse(request.responseText);
            if(data.success){
                temp_info = data.info[0].temperature;
                humid_info = data.info[0].humidity;
                light_info = data.info[1].light_intensity;
                document.querySelector('#temperature').innerHTML = temp_info;
                document.querySelector('#humidity').innerHTML  = humid_info;
                document.querySelector('#light').innerHTML  = light_info;
            }
            else{
                alert('There was an error');
            }
        }
        const data = new FormData();
        request.send(data);
    }
});
