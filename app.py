from flask import Flask, render_template, request, redirect, url_for, jsonify, abort, flash, session
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import json
#flash above is used for retrieving messages

app = Flask(__name__)
app.static_folder = 'static'


app.config['SECRET_KEY'] = 'your-secret-key'
# Configure JWT settings
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt = JWTManager(app)


with open('./static/authenticatedUsers.json', 'r') as file:
    users = json.load(file)

with open('./static/data.json', 'r') as file:
    users = json.load(file)

def save_users():
    with open('./static/data.json', 'w') as f:
        json.dump(users, f, indent=2)

# crud get all profiles
@app.route('/get_all_profiles', methods=['GET'])
def get_all_profiles():
    return jsonify({'users': users})

def get_next_user_id():
    if users:
        return max(user['id'] for user in users) + 1
    return 1

@app.route('/')
def main():
    registration_message = session.pop('registration_message', None)
    print(f"DEBUG: registration_message in main: {registration_message}")

    return render_template('main.html', registration_message=registration_message)

#crud get username by id 
@app.route('/get_username_by_id/<int:user_id>', methods=['GET'])
def get_profiles_by_id(user_id):
    user = next((user for user in users if user['id'] == user_id), None)
    if user:
        return jsonify({'id': user['id'], 'username': user['username']})
    else:
        return jsonify({'error': 'User not found'}), 404


@app.route('/edit/<int:user_id>', methods=['GET'])
def edit_profile(user_id):
    user = next((user for user in users if user['id'] == user_id), None)
    if user:
        return render_template('edit.html', user_id=user_id, user=user)
    else:
        return "User not found", 404


@app.route('/update_profile/<int:user_id>', methods=['POST'])
def update_profile(user_id):
    new_username = request.form.get('username')
    new_email = request.form.get('email')
    new_photo = request.form.get('photo')

    for user in users:
        if user['id'] == user_id:
            user['username'] = new_username
            user['email'] = new_email
            user['photo'] = new_photo

            save_users()

            response = {
                'message': 'Profile updated successfully',
                'user': user
            }

            if 'Postman' in request.user_agent.string:
                return jsonify(response)
            else:
                return redirect(url_for('index'))

    abort(404, "User not found")


#crud deleting user
@app.route('/delete_user/<int:user_id>', methods=['GET'])
def delete_profile(user_id):
    for user in users:
        if user['id'] == user_id:
            username = user['username']
            users.remove(user)
            for i, user in enumerate(users, start=1):
                user['id'] = i
            save_users()
            response = {
                'message': f"User {user_id} ({username}) is deleted."
            }

            if 'Postman' in request.user_agent.string:
                return jsonify(response)
            else:
                return redirect(url_for('index'))

    print(f"DEBUG: Users after the loop: {users}")
    abort(404, f"User {user_id} doesn't exist.")


@app.route('/create_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_email = request.form.get('email')
        new_photo = request.form.get('photo')

        new_user = {
            'id': get_next_user_id(),
            'username': new_username,
            'email': new_email,
            'photo': new_photo
        }

        users.append(new_user)
        save_users()

        response = {
            'message': 'User created successfully!',
            'user': new_user
        }

        if 'Postman' in request.user_agent.string:
            return jsonify(response)
        else:
            return redirect(url_for('index'))
    else:
        return render_template('add_user.html')


@app.route('/profile_page/<int:user_id>', methods=["GET"])
def profile_page(user_id):
    user = next((user for user in users if user['id'] == user_id), None)
    if user:
        return render_template('profile_page.html', user=user)
    else:
        return "User not found", 404


@app.route('/search', methods=['POST'])
def search():
    search_term = request.form.get('search_term', '')
    with open ('./static/data.json', 'r') as file:
        search_users = json.load(file)
        results = [user['username'] for user in search_users if search_term.lower() in user['username'].lower()]
    return jsonify(results) 


#registration process
@app.route('/registration', methods = ['GET', 'POST'])
def registration():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        result = register_user(email, password)
        # # Check the result and handle accordingly
        # flash(result['message'])
        # return render_template('main.html', registration_message=result['message'])
        if isinstance(result, tuple) and len(result) == 2:
            # Unpack the tuple
            status_code, message = result

            flash(message)

            # Check the status code and redirect accordingly
            if status_code == 200:
                return redirect(url_for('main'))
            else:
                return render_template('registration.html')  # Render the registration page again


    return render_template('registration.html')
    

def register_user(email, password):
    with open('static/authenticatedUsers.json', 'r') as f:
        users_data = json.load(f)

        # checking email is already registered
        if any(user.get('email') == email for user in users_data):
            return 400, "Email already registered"

        # else adding a new user
        new_user = {"email": email, "password": password, "access": "user", "tokens": []}
        users_data.append(new_user)

        # updating the json with the new user
        with open('static/authenticatedUsers.json', 'w') as f:
            json.dump(users_data, f, indent=2)

        return 200, "Registration successful"



def login_user(email, password):
    with open('static/authenticatedUsers.json', 'r') as file:
        users_data = json.load(file)

        # Find the user with the matching email
        user = next((user for user in users_data if user['email'] == email), None)

        if user is None:
            return {"message": "Invalid user"}, 404

        if password != user['password']:
            return {"message": "Invalid user"}, 404

        access_token = create_access_token(identity=email)
        user['tokens'].append(access_token)

        # Update the user in the list
        with open('static/authenticatedUsers.json', 'w') as file:
            json.dump(users_data, file, indent=2)

        return {"access_token": access_token, "access_level": user.get('access_level')}



# Authentication route
@app.route('/authentication', methods=['GET', 'POST'])
def authentication():
    email = request.form.get('email')
    password = request.form.get('password')

    result = login_user(email, password)

    if "access_token" in result:
        # after successful authentication redirecting to a main page
        return redirect(url_for('index'))

    # Authentication failed
    flash(result[0] if result else 'Authentication failed')
    return render_template('authentication.html')

@app.route('/index')
def index():
    return render_template('index.html', users = users)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
