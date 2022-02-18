var staff_id = document.getElementById('staff_id').value;

function changeName() {
    document.getElementById('change_name').hidden = true;
    document.getElementById('save_name').hidden = false;
    document.getElementById('first_name').disabled = false;
    document.getElementById('last_name').disabled = false;
}

function saveName() {
    var first_name = document.getElementById('first_name').value;
    var last_name = document.getElementById('last_name').value;
    $(async () => {
        var serviceURL = "http://localhost:5000/updateName";
        const data = {
            first_name: first_name,
            last_name: last_name,
            id: staff_id
        };

        try {
            const response =
                await fetch(
                    serviceURL, {
                        method: 'POST',
                        body: JSON.stringify(data),
                        headers: {
                            Accept: 'application/json',
                            'Content-Type': 'application/json',
                        }
                    }
                );
            const result = await response.json();
            if (response.status === 500) {
                alert("There is an error saving changes.")
            } else {
                location.reload();
                alert("Successfully saved changes!")
            }
        } catch (error) {
            // Errors when calling the service; such as network error, 
            // service offline, etc
            console.log('There is a problem retrieving the data, please try again later.<br />' + error);
        } // error
    });
}

function changeEmail() {
    document.getElementById('change_email').hidden = true;
    document.getElementById('save_email').hidden = false;
    document.getElementById('email').disabled = false;
}

function checkEmail() {
    if (/^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/.test(document.getElementById('email').value)) {
        document.getElementById('save_email').disabled = false;
        document.getElementById('email_error_msg').innerHTML = '';
    } else {
        document.getElementById('email_error_msg').innerHTML = "You have entered an invalid email address!";
        document.getElementById('save_email').disabled = true;
    }
}

function saveEmail() {
    var email = document.getElementById('email').value;
    $(async () => {
        var serviceURL = "http://localhost:5000/updateEmail";
        const data = {
            email: email,
            id: staff_id
        };

        try {
            const response =
                await fetch(
                    serviceURL, {
                        method: 'POST',
                        body: JSON.stringify(data),
                        headers: {
                            Accept: 'application/json',
                            'Content-Type': 'application/json',
                        }
                    }
                );
            const result = await response.json();
            if (response.status === 500) {
                alert("There is an error saving changes.")
            } else {
                location.reload();
                alert("Successfully saved changes!")
            }
        } catch (error) {
            // Errors when calling the service; such as network error, 
            // service offline, etc
            console.log('There is a problem retrieving the data, please try again later.<br />' + error);
        } // error
    });
}

function changePassword() {
    document.getElementById('change_password').hidden = true;
    document.getElementById('save_password').hidden = false;
    document.getElementById('password').disabled = false;
    document.getElementById('change_password_form').hidden = false;
}

function savePassword() {
    var old_password = document.getElementById('password').value;
    var new_password = document.getElementById('password_new').value;
    $(async () => {
        var serviceURL = "http://localhost:5000/updatePassword";
        const data = {
            old_password: old_password,
            new_password: new_password,
            id: staff_id
        };
        console.log(data)
        try {
            const response =
                await fetch(
                    serviceURL, {
                        method: 'POST',
                        body: JSON.stringify(data),
                        headers: {
                            Accept: 'application/json',
                            'Content-Type': 'application/json',
                        }
                    }
                );
            const result = await response.json();
            if (response.status === 500) {
                alert("There is an error saving changes.")
            } else {
                location.reload();
                alert("Successfully saved changes!")
            }
        } catch (error) {
            // Errors when calling the service; such as network error, 
            // service offline, etc
            alert('Incorrect Password!')
        } // error
    });
}

function checkFile() {
    var reader = new FileReader();
    reader.readAsDataURL(document.getElementById('signature').files[0]);
    console.log(document.getElementById('signature').files[0].type)
    reader.onload = function (e) {
        var image = new Image();
        image.src = e.target.result;
        image.onload = function () {
            var height = this.height;
            var width = this.width;
            if (height > 300 || width > 400) {
                alert("Height and Width must not exceed 300px by 400px.");
            } else if (document.getElementById('signature').files[0].type != "image/png") {
                alert("We only accept PNG files!")
            } else if (document.getElementById('signature').files[0].size > 1000000) {
                alert("File size too big!");
            } else {
                document.getElementById('submit_signature').disabled = false;
            }
        };
    };
}

function submitSignature() {
    signature_name = document.getElementById('first_name').value + "_" + document.getElementById('last_name').value + "_Signature.png";
    $(async () => {
        var serviceURL = "http://localhost:5000/updateSignaturePath";
        const data = {
            signature_name: signature_name,
            id: staff_id
        };
        console.log(data)
        try {
            const response =
                await fetch(
                    serviceURL, {
                        method: 'POST',
                        body: JSON.stringify(data),
                        headers: {
                            Accept: 'application/json',
                            'Content-Type': 'application/json',
                        }
                    }
                );
            const result = await response.json();
            if (response.status === 500) {
                alert("There is an error saving changes.")
            } else {
                document.getElementById('signature_submit').submit();
                alert("Successfully saved changes!")
            }
        } catch (error) {
            // Errors when calling the service; such as network error, 
            // service offline, etc
            console.log('There is a problem retrieving the data, please try again later.<br />' + error);
        } // error
    });
}

function checkFirstName() {
    if (document.getElementById('first_name').value == '') {
        document.getElementById('first_name_error_msg').innerHTML = "First name cannot be blank!";
        document.getElementById('save_name').disabled = true;
    } else {
        document.getElementById('first_name_error_msg').innerHTML = ''
        document.getElementById('save_name').disabled = false;
    }
}

function checkLastName() {
    if (document.getElementById('last_name').value == '') {
        document.getElementById('last_name_error_msg').innerHTML = "Last name cannot be blank!";
        document.getElementById('save_name').disabled = true;
    } else {
        document.getElementById('last_name_error_msg').innerHTML = ''
        document.getElementById('save_name').disabled = false;
    }
}

function checkPassword() {
    if (document.getElementById('password').value == '') {
        document.getElementById('password_error_msg').innerHTML = "Password cannot be blank!";
        document.getElementById('save_password').disabled = true;
        document.getElementById('password_new').disabled = true;
        document.getElementById('password_new_2').disabled = true;
    } else {
        document.getElementById('password_error_msg').innerHTML = ''
        document.getElementById('save_password').disabled = false;
        document.getElementById('password_new').disabled = false;
        document.getElementById('password_new_2').disabled = false;
    }
}

function checkNewPassword() {
    if (document.getElementById('password_new').value == '') {
        document.getElementById('password_new_error_msg').innerHTML = "Password cannot be blank!";
        document.getElementById('save_password').disabled = true;
    } else {
        if (document.getElementById('password_new_2').value != document.getElementById('password_new').value) {
            document.getElementById('save_password').disabled = true;
            document.getElementById('password_new_error_msg').innerHTML = "Password cannot be different!";
            document.getElementById('password_new_2_error_msg').innerHTML = "Password cannot be different!";
        } else if (document.getElementById('password_new').value == document.getElementById('password').value) {
            document.getElementById('save_password').disabled = true;
            document.getElementById('password_new_error_msg').innerHTML = "Password cannot be the same as old password!";
            document.getElementById('password_new_2_error_msg').innerHTML = "Password cannot be the same as old password!";
        } else {
            document.getElementById('password_new_error_msg').innerHTML = ''
            document.getElementById('password_new_2_error_msg').innerHTML = ''
            document.getElementById('save_password').disabled = false;
        }
    }
}

function checkNewPassword2() {
    if (document.getElementById('password_new_2').value == '') {
        document.getElementById('password_new_2_error_msg').innerHTML = "Password cannot be blank!";
        document.getElementById('save_password').disabled = true;
    } else {
        if (document.getElementById('password_new_2').value != document.getElementById('password_new').value) {
            document.getElementById('save_password').disabled = true;
            document.getElementById('password_new_error_msg').innerHTML = "Password cannot be different!";
            document.getElementById('password_new_2_error_msg').innerHTML = "Password cannot be different!";
        } else if (document.getElementById('password_new_2').value == document.getElementById('password').value) {
            document.getElementById('save_password').disabled = true;
            document.getElementById('password_new_error_msg').innerHTML = "Password cannot be the same as old password!";
            document.getElementById('password_new_2_error_msg').innerHTML = "Password cannot be the same as old password!";
        } else {
            document.getElementById('password_new_error_msg').innerHTML = ''
            document.getElementById('password_new_2_error_msg').innerHTML = ''
            document.getElementById('save_password').disabled = false;
        }
    }
}