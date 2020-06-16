document.addEventListener('DOMContentLoaded',()=>{
    getDataHourly();
      
    function getDataHourly(){       
        setInterval(() => {
            updateInforamtion();
        }, 1000*30);
    }
    function updateInforamtion(){        
        const request = new XMLHttpRequest();
        request.open('POST','/updateHomepage');
        request.onload = function(){
            const data = JSON.parse(request.responseText);         
            if(data.success){                                 
                temp_info = data.info1.temperature;
                humid_info = data.info1.humidity;
                light_info = data.info2.light_intensity;            
                t = data.device.temperature;
                h = data.device.humidity;
                l = data.device.light;
                console.log(t,h,l);
                document.querySelector('#temperature').innerHTML = temp_info;
                document.querySelector('#humidity').innerHTML = humid_info;
                document.querySelector('#light').innerHTML = light_info;        
                if(temp_info > t || humid_info > h || light_info > l){
                    alert("Storage condition is overlimit!!!");
                }
            }
            else{
                alert('There was an error');
            }
        }
        const data = new FormData();
        request.send(data);        
    }
});