
function addDir() {
    let ans = prompt("Podaj nazwę folderu")
    if (ans == null) {
        return;
    }
    let csrftoken = getCookie('csrftoken');
    let data = {
        'add_directory_name': ans,
        'parent_directory': currentDirId
    }
    $.ajax({
        url: '/add_directory/',
        type: 'POST',
        data: data,
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: function(response) {
            document.getElementById('dir-list').innerHTML = response.dir_list;
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(data)
            alert("Wystąpił niezidentyfikowany błąd, odśwież stronę i spróbuj ponownie");
        }
    });
}


function updateInputValue(inputId, selectId) {
    document.getElementById(inputId).value = document.getElementById(selectId).value;
}

function updateOptimizationValue() {
    let optimizationValue = '';
    for (let i = 1; i <= 3; i++) {
        if (document.getElementById('opt' + i).checked) {
            optimizationValue += 'opt' + i + ',';
        }
    }
    document.getElementById('optimization-input').value = optimizationValue.slice(0, -1);
}

function initializeFormValues() {
    updateInputValue('standard-input', 'standard-select');
    updateInputValue('processor-input', 'processor-select');
    updateInputValue('dependent-input', 'processor-dependent-select');
    updateOptimizationValue();
    updateProcessorDependentOptions();
}

function updateProcessorDependentOptions() {
    const processorSelect = document.getElementById('processor-select');
    const dependentSelect = document.getElementById('processor-dependent-select');
    const processorValue = processorSelect.value;

    // Clear existing options
    dependentSelect.innerHTML = '';

    // Add processor-specific options
    let processorOptions = [];

     if (processorValue === 'mmcs51') {
            processorOptions = [
                { value: 'small', text: 'Small Model Program' },
                { value: 'medium', text: 'Medium Model Program' },
                { value: 'large', text: 'Large Model Program' },
                { value: 'huge', text: 'Huge Model Program' }
            ];
        } else if (processorValue === 'z80') {
            processorOptions = [
                { value: 'model-small', text: 'Small Model Program' },
                { value: 'model-medium', text: 'Medium Model Program' },
                { value: 'model-compact', text: 'Compact Model Program' },
                { value: 'model-large', text: 'Large Model Program' }
            ];
        } else if (processorValue === 'mstm8') {
            processorOptions = [
                { value: 'iram-size 128', text: 'Internal RAM Size' },
                { value: 'xram-size 128', text: 'External RAM Size' },
                { value: 'code-size 128', text: 'Code Size' }
            ];
        }


    for (const option of processorOptions) {
        const newOption = document.createElement('option');
        newOption.value = option.value;
        newOption.textContent = option.text;
        dependentSelect.appendChild(newOption);
    }

    // Update dependent input value
    updateInputValue('dependent-input', 'processor-dependent-select');
}

document.getElementById('standard-select').addEventListener('change', function() {
    updateInputValue('standard-input', 'standard-select');
});

document.getElementById('processor-select').addEventListener('change', function() {
    updateInputValue('processor-input', 'processor-select');
    updateProcessorDependentOptions();
});

document.getElementById('processor-dependent-select').addEventListener('change', function() {
    updateInputValue('dependent-input', 'processor-dependent-select');
});

for (let i = 1; i <= 3; i++) {
    document.getElementById('opt' + i).addEventListener('change', updateOptimizationValue);
}

// Initialize default form values
initializeFormValues();

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


function deleteItem() {
    let csrftoken = getCookie('csrftoken');
    let data = {
        'file_id': currentFileId,
        'dir_id': currentDirId
    }
    $.ajax({
        url: '/delete_item/',
        type: 'POST',
        data: data,
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: function(response) {
            if(currentFileId != null) {
                document.getElementById('file' + currentFileId).remove();
                currentFileId = null;
            }
            else {
                document.getElementById('dir' + currentDirId).remove();
                currentDirId = null;
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(data)
            alert("Wystąpił niezidentyfikowany błąd, odśwież stronę i spróbuj ponownie");
        }
    });
}

function hideAll() {
    let elements = document.getElementsByClassName('section-content');
    for (let i = 0; i < elements.length; i++) {
        elements[i].style.display = 'none';
    }
}

function showAll() {
    let elements = document.getElementsByClassName('section-content');
    for (let i = 0; i < elements.length; i++) {
        elements[i].style.display = 'block';
    }
}

function setSectionsASM(){
    let section_contents = document.getElementsByClassName('section-content');
    let sections = document.getElementsByClassName('section');
    for (let i = 0; i < sections.length; i++) {
        sections[i].addEventListener('click', function() {
                section_contents[i].style.display = section_contents[i].style.display === 'none' ? 'block' : 'none';
            }
        );
    }
}


function showFile(id) {
    if(id == null) {
        refresh(null, null, null, null)
        return
    }
    let csrftoken = getCookie('csrftoken');
    let data = {
        'file_id': id
    }
    $.ajax({
        url: '/' + id,
        type: 'POST',
        data: data,
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: function(response) {
            refresh(response.code_in_c, response.right_panel_code, id, response.dir_id)
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(data)
            alert("Wystąpił niezidentyfikowany błąd, odśwież stronę i spróbuj ponownie");
        }
    });
}

function showDir(id) {
    refreshFilesAndDirs(null, id)
}

function refresh(code_in_c, asm_code, file_id, dir_id) {
    a.getTextArea().style.width = "100vw";
    a.getTextArea().style.height = "100%";
    if(code_in_c == null && asm_code == null) {
        a.setValue("Wybierz plik z listy po lewej stronie");
        document.getElementById('asm_sections').innerHTML = "Wybierz plik z listy po lewej stronie";
        refreshFilesAndDirs(null, null)
        return
    }
     a.setValue(code_in_c);

    document.getElementById('asm_sections').innerHTML = null;

    console.log(asm_code)
    console.log(asm_code[1])

    if(asm_code[0] === "ERROR") {
        for(let i = 0; i < asm_code[1].length; i = i + 1) {
            let inner = "<div class=\"section\">"
            inner += "<h3 class=\"section-title\" onmouseenter= \"highlight(" + asm_code[2][i] + ")\" onmouseleave=\"stopHighlight(" + asm_code[2][i] + ")\">" + asm_code[1][i] + "</h3>"

            document.getElementById('asm_sections').innerHTML += inner
            setSectionsASM()
        }
    }
    else{
         for(let i = 0; i < asm_code.length; i = i + 2) {
            let inner = "<div class=\"section\">"
            inner += "<h3 class=\"section-title\">" + asm_code[i][0] + "</h3>"
            inner += "<div class=\"section-content\" style=\"display: none;\">"
            for (let j = 1; j < asm_code[i].length; j++) {
                if(asm_code[i][j].startsWith(';\t./app_main/c_files/')) {
                    // split by : ant convert second part to int
                    let line_id = parseInt(asm_code[i][j].split(':')[1]);
                    inner += "<div onmouseenter= \" highlight(" + line_id + ")\" onmouseleave =\"stopHighlight(" + line_id + ")\" >" + asm_code[i][j] + "</div>"
                }
                else{
                    inner += "<div>" + asm_code[i][j] + "</div>"
                }
            }
            inner = inner + "</div>"

            document.getElementById('asm_sections').innerHTML += inner
            setSectionsASM()
        }
    }


    refreshFilesAndDirs(file_id, dir_id)
}

function refreshFilesAndDirs(file_id, dir_id) {
    // Refresh file highlight
    if (currentFileId != null) {
        document.getElementById('file' + currentFileId).classList.remove("chosen");
    }

    currentFileId = file_id;
    if(file_id != null){
        document.getElementById('file' + currentFileId).classList.add("chosen");
    }

    // Refresh dir highlight
    if (currentDirId != null) {
        document.getElementById('dir' + currentDirId).classList.remove("chosen");
    }
    document.getElementById('root_dir').classList.remove("chosen");

    currentDirId = dir_id;
    if(dir_id != null){
        document.getElementById('dir' + currentDirId).classList.add("chosen");
    }
    else {
        document.getElementById('root_dir').classList.add("chosen");
    }

    document.getElementById("dir-id").value = dir_id;
}
function addFile() {
    let form = document.getElementById('file_upload');
    let formData = new FormData(form);
    let csrftoken = getCookie('csrftoken');

    $.ajax({
        url: '/add_file/',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: function(response) {
            if(response.status !== 'ok') {
                alert(response.error);
                return
            }
            document.getElementById('dir-list').innerHTML = response.dir_list;
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(jqXHR);
            alert("Wystąpił niezidentyfikowany błąd, odśwież stronę i spróbuj ponownie");
        }
    });
}

function highlight(id) {
    // Get the <pre> element with the id "code_box"
    const codeBox = document.getElementById("code_box");

    // Split the code into an array of lines
    const lines = codeBox.innerHTML.split("\n");

    // Remove existing "highlighted" or "unhighlighted" classes
    lines[id - 1] = lines[id - 1].replace(/<span class="(highlighted|unhighlighted)">|<\/span>/g, '');

    // Add the "highlighted" class to the line with the specified id
    lines[id - 1] = `<span class="highlighted">${lines[id - 1]}</span>`;

    // Join the lines back together and update the <pre> element's innerHTML
    codeBox.innerHTML = lines.join("\n");
  }

  function stopHighlight(id) {
    // Get the <pre> element with the id "code_box"
    const codeBox = document.getElementById("code_box");

    // Split the code into an array of lines
    const lines = codeBox.innerHTML.split("\n");

    // Remove the "highlighted" class and add the "unhighlighted" class
    lines[id - 1] = lines[id - 1].replace(/<span class="highlighted">|<\/span>/g, '');

    // Add the "unhighlighted" class to the line with the specified id
    lines[id - 1] = `<span class="unhighlighted">${lines[id - 1]}</span>`;

    // Join the lines back together and update the <pre> element's innerHTML
    codeBox.innerHTML = lines.join("\n");
  }

  function recompile() {
    let form = document.getElementById('recompile_form');
    document.getElementById('recompile_file_id').value = currentFileId;
    document.getElementById('recompile_dir_id').value = currentDirId;
    let formData = new FormData(form);
    let csrftoken = getCookie('csrftoken');

    $.ajax({
        url: '/recompile/',
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        },
        success: function(response) {
            if(response.status !== 'ok') {
                alert(response.error);
                return
            }
            console.log(response)
            refresh(response.code_in_c, response.right_panel_code, response.file_id, response.dir_id)
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.log(jqXHR);
            alert("Wystąpił niezidentyfikowany błąd, odśwież stronę i spróbuj ponownie");
        }
    });
  }