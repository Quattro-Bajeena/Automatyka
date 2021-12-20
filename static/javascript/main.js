

function AddAltitudeInput(event){
    const altitudes = document.getElementById("altitudes");
    const list_el = document.createElement("li");

    const time_node = document.createElement('input');
    time_node.type = 'text';
    time_node.placeholder = 'time';
    time_node.classList.add("time");

    const altitude_node = document.createElement('input');
    altitude_node.type = 'text';
    altitude_node.placeholder = "altitude";
    altitude_node.classList.add("altitude");

    list_el.appendChild(time_node);
    list_el.appendChild(altitude_node);

    altitudes.appendChild(list_el);
}

function Simulate(event){
    const inputs = document.getElementById('water-tank').querySelectorAll('input');

    const normal_inputs = Array.from(inputs).filter(input => input.classList.contains('time') == false && input.classList.contains('altitude') == false);
    const altitude_inputs = Array.from(inputs).filter(input => input.classList.contains('time') || input.classList.contains('altitude'));
    //console.log(normal_inputs);
    //console.log(altitude_inputs);

    const data = {};
    for(let input of normal_inputs){
        //console.log(input);
        data[input.name] = input.value;
    }

    data["altitudes"] = [];
    for(let i = 0; i < altitude_inputs.length; i += 2){
        const time = altitude_inputs[i];
        const alt = altitude_inputs[i+1];
        //console.log(time.value, alt.value);

        if(time.value && alt.value){
            data["altitudes"].push([time.value, alt.value]);
        }
    }
    


    const url = '/drone';
    const xhr = new XMLHttpRequest();
    xhr.open("POST", url);

    xhr.setRequestHeader("Accept", "application/json");
    xhr.setRequestHeader("Content-Type", "application/json");  

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
        console.log(xhr.status);
        console.log(xhr.responseText);
        document.body.parentElement.innerHTML = xhr.responseText;
        Initialize();
        
        
    }};

    console.log(data);
    xhr.send(JSON.stringify(data));
}


function Initialize(){
    document.getElementById("add-altitude").addEventListener('click', AddAltitudeInput);
    document.getElementById("simulate").addEventListener('click', Simulate);
    
    document.querySelectorAll("input").forEach(inputElem => {
        if(inputElem.type == 'range'){
            inputElem.addEventListener('input', event => {
                event.target.nextElementSibling.value = event.target.value;
            });
            inputElem.nextElementSibling.value = inputElem.value;
        }
    });
}

Initialize();


