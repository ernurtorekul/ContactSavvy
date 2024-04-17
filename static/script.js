'use strict'

// starting from ajax ( async code ) all other functions works only with flask but this one is not the case

const usersContainer = $('#usersContainer');
const searchInput = $('#searchInput');

function updateUI(users) {
    const userList = document.getElementById('user-list');

    userList.innerHTML = '';    //clearing the existing content

    users.forEach(user => {
        const userContainer = document.createElement('div');
        userContainer.classList.add('user');

        const usernameElement = document.createElement('p');
        usernameElement.textContent = `Username: ${user.username}`;

        const emailElement = document.createElement('p');
        emailElement.textContent = `Email: ${user.email}`;

        const photoElement = document.createElement('img');

        // checking the link format of the photo
        if (user.photo.startsWith('data:image')) {
            photoElement.src = user.photo;  // setting base64-encoded image source 
        } else {
            photoElement.src = user.photo;  // setting regular image URL source
        }

        userContainer.appendChild(usernameElement);
        userContainer.appendChild(emailElement);
        userContainer.appendChild(photoElement);

        userList.appendChild(userContainer);
    });
}
// getting data
function fetchUserData(callback) {
    $.ajax({
        url: '/get_all_profiles',
        method: 'GET',
        dataType: 'json',
        success: function (data) {
            if (data && data.users && data.users.length) {
                callback(data.users);
            } else {
                console.warn('');
            }
        },
        error: function (error) {
            console.error('error loading json', error);
        }
    });
}
//handling the search
function handleSearch() {
    event.preventDefault();
    const searchTerm = searchInput.val().toLowerCase();

    fetchUserData(function (allUsers) {
        const filteredUsers = allUsers.filter(user => user.username.toLowerCase().includes(searchTerm));
        updateUI(filteredUsers);
        $('#user-list').removeClass('hidden')
    });

    $('#searchContainer').show();

}

$(document).on('click', function(event) {
    // Check if the clicked element is not the search input or its container
    if (!$(event.target).closest('.container-fluid.search').length && !$(event.target).is('#searchInput')) {
        // Hide the user-list container
        $('#user-list').addClass('hidden');
    }
});


searchInput.on('input', handleSearch);

// Add event listener to show search container when search input is focused
// searchInput.focus(function() {
//     $('#searchContainer').show();
// });



// using fetch data.json 
fetch('/static/data.json')
    .then(response => response.json())
    .then(users => {
        // calling updateUI after our data is ready
        updateUI(users);
    })
    .catch(error => {
        console.error('error fetching data json:', error);
});

