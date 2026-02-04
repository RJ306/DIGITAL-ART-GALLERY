from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, abort
import mysql.connector
 
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
 
from werkzeug.security import generate_password_hash, check_password_hash
 
from datetime import datetime





#app.config['SECRET_KEY'] = 'art'


# Database connection settings
db_config = {
    'user': 'root',
    'password': 'abc123',
    'host': 'localhost',
    
    'database': 'digital_gallery'
}
 
app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.route('/') 
def home_():
    try:
        # Establish a connection to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Query to fetch the 6 most recently added artworks
        query = "SELECT title, image_url, description FROM artwork ORDER BY creation_date DESC LIMIT 6"
        cursor.execute(query)
        artworks = cursor.fetchall()

        # Render the HTML page with the artworks
        return render_template('html_front.html', artworks=artworks)
    
    except Exception as e:
        return f"An error occurred: {e}"

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            
            
# Function to get artworks
def get_artworks():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        query = "SELECT artwork_id,title, image_url, description FROM artwork ORDER BY creation_date DESC"
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# View all artworks route
@app.route('/artwork')
def all_artworks():
    artworks = get_artworks()
    return render_template('artwork.html', artworks=artworks)

            



# Route to display artwork details
@app.route('/artwork_detail/<int:artwork_id>')
def artwork_detail(artwork_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Query to fetch detailed information about the artwork
        query = """
            SELECT a.artwork_id, a.title, a.description, a.creation_date, a.price, a.image_url, a.status,
                   ar.name AS artist_name, ar.biography AS artist_bio, ar.profile_picture AS artist_picture,
                   au.status AS auction_status, au.start_date, au.end_date, au.current_highest_bid
            FROM artwork a
            LEFT JOIN artist ar ON a.artist_id = ar.artist_id
            LEFT JOIN auction au ON a.artwork_id = au.artwork_id
            WHERE a.artwork_id = %s
        """
        cursor.execute(query, (artwork_id,))
        artwork = cursor.fetchone()

        if not artwork:
            return "Artwork not found", 404

        # Check if the user is logged in
        user_logged_in = 'user_id' in session

        return render_template('artwork_detail.html', artwork=artwork, user_logged_in=user_logged_in)

    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def add_to_wishlist(customer_id, artwork_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Start transaction
        cursor.execute("START TRANSACTION")

        query = """
            INSERT INTO wishlist (customer_id, artwork_id, date_added)
            VALUES (%s, %s, NOW())
        """
        cursor.execute(query, (customer_id, artwork_id))

        # Commit the transaction
        conn.commit()

    except Exception as e:
        conn.rollback()  # Rollback in case of error
        return f"An error occurred: {e}"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Route to handle adding to wishlist
@app.route('/add_to_wishlist', methods=['POST'])
def handle_add_to_wishlist():
    if current_user.is_authenticated and current_user.role == 'customer':
        artwork_id = request.form['artwork_id']
        customer_id = current_user.customer_id  # Assuming current_user has customer_id
        add_to_wishlist(customer_id, artwork_id)
        return redirect(url_for('all_artworks'))  # Redirect back to the artworks page
    else:
        return redirect(url_for('login')) 
 
 
 
 
 # Function to fetch wishlist data for the current customer
def get_wishlist(customer_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT a.artwork_id, a.title, a.image_url, a.description 
            FROM wishlist w
            JOIN artwork a ON w.artwork_id = a.artwork_id
            WHERE w.customer_id = %s
            ORDER BY w.date_added DESC
        """
        cursor.execute(query, (customer_id,))
        return cursor.fetchall()
    except Exception as e:
        return f"An error occurred: {e}"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Route to display the wishlist
@app.route('/wishlist')
@login_required  # Ensures the user is logged in
def view_wishlist():
    # Check if the logged-in user is a customer
     
    
    customer_id = current_user.id  # Assuming 'id' is the field in your User model
    artworks = get_wishlist(customer_id)  # Fetch wishlist artworks for the customer
    return render_template('wishlist.html', artworks=artworks)
 
 
 
 
 #purchase
@app.route('/process_payment', methods=['POST'])
def process_payment():
    if 'customer_id' not in session:
        return redirect('/login')

    # Get form data
    card_number = request.form['card_number']
    expiry_date = request.form['expiry_date']
    cvv = request.form['cvv']
    artwork_id = request.form['artwork_id']
    customer_id = session['customer_id']

    # Simulate payment processing (you would replace this with real payment API logic)
    payment_success = simulate_payment(card_number, expiry_date, cvv)

    if payment_success:
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Start transaction
            cursor.execute("START TRANSACTION")

            # Insert into Purchase Table
            cursor.execute('''
                INSERT INTO purchase (customer_id, artwork_id, purchase_date, amount, payment_method, transaction_id)
                VALUES (%s, %s, NOW(), %s, %s, %s)
            ''', (customer_id, artwork_id, 100, 'credit/debit', 'transaction_id_here'))

            # Update Artwork Table to 'sold'
            cursor.execute('''
                UPDATE artwork
                SET status = 'sold'
                WHERE artwork_id = %s
            ''', (artwork_id,))
            

            # Commit the transaction if all goes well
            conn.commit()

            # Prompt for review
            return render_template('review_page.html', artwork_id=artwork_id)

        except Exception as e:
            conn.rollback()  # Rollback in case of error
            return f"An error occurred: {e}"

        finally:
            cursor.close()
            conn.close()

    else:
        return "Payment failed. Please try again."


# Function to simulate payment processing
def simulate_payment(card_number, expiry_date, cvv):
    # Simulate a payment processing logic (you would integrate a payment gateway here)
    return True  # Assuming payment is successful for demo

# Route to submit review
@app.route('/submit_review', methods=['POST'])
def submit_review():
    if 'customer_id' not in session:
        return redirect('/login')

    artwork_id = request.form['artwork_id']
    rating = request.form['rating']
    review_text = request.form['review_text']
    customer_id = session['customer_id']

    # Insert review into the Review table
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO review (customer_id, artwork_id, rating, review_text, review_date)
        VALUES (%s, %s, %s, %s, NOW())
    ''', (customer_id, artwork_id, rating, review_text))
    conn.commit()
    return 
    cursor.close()
    conn.close()

    

 
from flask_login import UserMixin
# Define the user models for each type (admin, curator, customer, artist)
USER_MODELS = {
    'customer': 'Customer',
    'curator': 'Curator',
    'admin': 'Admin',
    'artist': 'Artist'
}


# Assuming you have a table 'users' for all user types in your database

class User(UserMixin):
    def __init__(self, id, name, user_type):
        self.id = id
        self.name = name
        self.user_type = user_type

@login_manager.user_loader
def load_user(user_id):
    user_tables = {
        'customer': {'id_col': 'customer_id', 'table': 'customer'},
        'curator': {'id_col': 'curator_id', 'table': 'curator'},
        'admin': {'id_col': 'admin_id', 'table': 'admin'},
        'artist': {'id_col': 'artist_id', 'table': 'artist'}
    }

    for user_type, config in user_tables.items():
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        query = f"SELECT * FROM {config['table']} WHERE {config['id_col']} = %s"
        cursor.execute(query, (user_id,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            return User(id=user_data[config['id_col']], name=user_data['name'], user_type=user_type)
    
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        user_type = request.form.get('user_type')

        if not all([name, password, user_type]):
            flash("All fields are required!")
            return redirect(url_for('login'))

        user_tables = {
            'customer': {'id_col': 'customer_id', 'table': 'customer'},
            'curator': {'id_col': 'curator_id', 'table': 'curator'},
            'admin': {'id_col': 'admin_id', 'table': 'admin'},
            'artist': {'id_col': 'artist_id', 'table': 'artist'}
        }

        if user_type in user_tables:
            table_config = user_tables[user_type]
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)
            
            query = f"SELECT * FROM {table_config['table']} WHERE name = %s"
            cursor.execute(query, (name,))
            user = cursor.fetchone()
            conn.close()

            if user and check_password_hash(user['password'], password):
                user_obj = User(id=user[table_config['id_col']], name=user['name'], user_type=user_type)
                login_user(user_obj)
                return redirect(url_for('dashboard', user_type=user_type))
            else:
                flash("Invalid credentials.")
        else:
            flash("Invalid user type.")

    return render_template('login.html')
# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     # if 'user_id' in session:
#     #     return redirect(url_for('home_'))

#     if request.method == 'POST':
#         user_type = request.form.get('user_type')
#         name = request.form.get('name')  # Replaced "username" with "name"
#         email = request.form.get('email')
#         password = generate_password_hash(request.form.get('password'))

#         # Check if name exists in any table
#         for table in USER_MODELS.values():
#             connection = mysql.connector.connect(**db_config)
#             cursor = connection.cursor()
#             cursor.execute(f'SELECT * FROM {table} WHERE name = %s', (name,))
#             existing_user = cursor.fetchone()
#             connection.close()

#             if existing_user:
#                 flash('Name already exists. Please choose another one.')
#                 return render_template('signup.html')

#         # Insert new user into the appropriate table
#         if user_type not in USER_MODELS:
#             flash('Invalid user type.')
#             return render_template('signup.html')

#         table = USER_MODELS[user_type]
#         connection = mysql.connector.connect(**db_config)
#         cursor = connection.cursor()
#         cursor.execute(f'INSERT INTO {table} (name, email, password) VALUES (%s, %s, %s)', (name, email, password))
#         connection.commit()
#         connection.close()

#         # After signup, log the user in manually
#         connection = mysql.connector.connect(**db_config)
#         cursor = connection.cursor()
#         cursor.execute(f'SELECT * FROM {table} WHERE name = %s', (name,))
#         user_data = cursor.fetchone()
#         connection.close()

#         # Store user data in the session
#         session['user_id'] = user_data[0]  # Assuming user_data[0] is the user ID
#         session['name'] = user_data[1]  # Assuming user_data[1] is the name
#         session['user_type'] = user_type  # Store the user type (role)

#         return redirect(url_for('home_'))

#     return render_template('signup.html')
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        name = request.form.get('name')  # Using 'name' instead of 'username'
        email = request.form.get('email')
        password = generate_password_hash(request.form.get('password'))

        # Check if name exists in any table
        for table in USER_MODELS.values():
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(f'SELECT * FROM {table} WHERE name = %s', (name,))
            existing_user = cursor.fetchone()
            connection.close()

            if existing_user:
                flash('Name already exists. Please choose another one.')
                return render_template('signup.html')

        # Insert new user into the appropriate table
        if user_type not in USER_MODELS:
            flash('Invalid user type.')
            return render_template('signup.html')

        table = USER_MODELS[user_type]
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute(f'INSERT INTO {table} (name, email, password) VALUES (%s, %s, %s)', (name, email, password))
        connection.commit()
        connection.close()

        # After signup, log the user in manually
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute(f'SELECT * FROM {table} WHERE name = %s', (name,))
        user_data = cursor.fetchone()
        connection.close()

        # Use Flask-Login to log the user in
        user_obj = User(id=user_data[0], name=user_data[1], user_type=user_type)
        login_user(user_obj)

        return redirect(url_for('dashboard', user_type=user_type))
    return render_template('signup.html')


 
@app.route('/logout')
@login_required
def logout():
    # Store the user type (role) in session before logging out
    # session['role'] = current_user.user_type  # Store the current role in session

    logout_user()  # Logs out the current user
    flash("You have been logged out.")
    return redirect(url_for('login')) # Redirect to the login page

@app.route('/curator/dashboard')
@login_required
def curator_dashboard():
    # Here you can fetch curator's data from the database if needed
    if 'user_type' in session and session['user_type'] == 'curator':
        return render_template('curator_dashboard.html')
    return render_template('curator_dashboard.html')
# Route to show the Organize Auction form
@app.route('/organize_auction', methods=['GET'])
def organize_auction_form():
    return render_template('organize_auction.html')

# Route to handle organizing an auction
@app.route('/organize_auction', methods=['POST'])
def organize_auction():
    # Get form data
    auction_name = request.form['auction_name']
    auction_date = request.form['auction_date']
    time_slot = request.form['time_slot']

    # Split the time slot into start time and end time
    start_time, end_time = time_slot.split('-')
    # Combine the auction date with the times to create full datetime values
    start_datetime = datetime.strptime(f"{auction_date} {start_time}", "%Y-%m-%d %H:%M")
    end_datetime = datetime.strptime(f"{auction_date} {end_time}", "%Y-%m-%d %H:%M")

    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Check for overlapping auctions in the database
    query = """
        SELECT COUNT(*) 
        FROM Auction
        WHERE (%s BETWEEN start_date AND end_date OR %s BETWEEN start_date AND end_date)
    """
    cursor.execute(query, (start_datetime, end_datetime))
    conflict_count = cursor.fetchone()[0]

    if conflict_count > 0:
        # Flash error message if there is a conflict
        flash("Another auction is already scheduled at the same date and time!", "error")
    else:
        # Insert the auction data into the database
        query = """
            INSERT INTO Auction (auction_name, start_date, end_date)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (auction_name, start_datetime, end_datetime))
        conn.commit()
        # Flash success message
        flash("Auction organized successfully!", "success")

    # Close the database connection
    cursor.close()
    conn.close()

    return redirect('/organize_auction')

@app.route('/notify_artist', methods=['POST'])
def notify_artist():
    # Get form data
    artwork_id = request.form['artwork_id']

    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Fetch the artist's details and artwork submission status
    query = """
        SELECT a.artist_id, ar.artist_name
        FROM Artwork a
        JOIN Artist ar ON a.artist_id = ar.artist_id
        WHERE a.artwork_id = %s AND a.status = 'Submitted'
    """
    cursor.execute(query, (artwork_id,))
    result = cursor.fetchone()

    if result:
        artist_id, artist_name = result

        # Update the artwork's status to 'Selected for Auction'
        update_query = """
            UPDATE Artwork
            SET status = 'Selected for Auction'
            WHERE artwork_id = %s
        """
        cursor.execute(update_query, (artwork_id,))
        conn.commit()

        # Insert notification into the database
        notification_message = f"Your artwork (ID: {artwork_id}) has been selected for the auction!"
        insert_notification_query = """
            INSERT INTO Notifications (artist_id, message, is_read)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_notification_query, (artist_id, notification_message, 0))
        conn.commit()

        # Flash success message
        flash(f"Notification sent to Artist {artist_name} successfully!", "success")
    else:
        # Flash error message if no matching artwork found
        flash("Artwork not found or not in 'Submitted' status!", "error")

    # Close the database connection
    cursor.close()
    conn.close()

    return redirect('/notify_artist')

@app.route('/artist_notifications/<int:artist_id>', methods=['GET'])
def view_notifications(artist_id):
    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Fetch notifications for the artist
    query = """
        SELECT notification_id, message, is_read
        FROM Notifications
        WHERE artist_id = %s
        ORDER BY notification_id DESC
    """
    cursor.execute(query, (artist_id,))
    notifications = cursor.fetchall()

    # Close the database connection
    cursor.close()
    conn.close()

    # Render notifications on the artist's dashboard
    return render_template('artist_notifications.html', notifications=notifications)


@app.route('/approve_artwork', methods=['GET', 'POST'])
def approve_artwork():
    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch auctions for selection in the form
        cursor.execute("SELECT auction_id, auction_name, start_date FROM Auction")
        auctions = cursor.fetchall()

        # Fetch pending artworks
        cursor.execute("""
            SELECT a.artwork_id, a.title, a.description, ar.name
            FROM artwork a
            JOIN artist ar ON a.artist_id = ar.artist_id
            WHERE a.status = 'pending'
        """)
        pending_artworks = cursor.fetchall()

        # Fetch top 10 most wishlisted artworks
        cursor.execute("""
            SELECT a.artwork_id, a.title, COUNT(w.wishlist_id) AS wishlist_count
            FROM artwork a
            LEFT JOIN wishlist w ON a.artwork_id = w.artwork_id
            GROUP BY a.artwork_id, a.title
            ORDER BY wishlist_count DESC
            LIMIT 10
        """)
        top_wishlisted_artworks = cursor.fetchall()

        # Handle approving an artwork
        if request.method == 'POST':
            artwork_id = request.form.get('artwork_id')
            auction_id = request.form.get('auction_id')

            if artwork_id:
                # Update artwork status to 'auctioned'
                cursor.execute("UPDATE artwork SET status = 'auctioned' WHERE artwork_id = %s", (artwork_id,))

                # Link artwork to the selected auction
                cursor.execute("""
                    INSERT INTO auction (artwork_id, auction_id)
                    VALUES (%s, %s)
                """, (artwork_id, auction_id))

                # Commit changes
                conn.commit()

                flash('The selected artwork has been added to the auction!', 'success')
            else:
                flash('No artwork selected for auction.', 'danger')
            return redirect(url_for('approve_artwork'))  # Refresh the page

    except Exception as e:
        flash(f"An error occurred: {str(e)}", 'danger')
    finally:
        # Ensure the cursor and connection are closed
        cursor.close()
        conn.close()

    return render_template(
        'approve_artwork.html',
        auctions=auctions,
        pending_artworks=pending_artworks,
        top_wishlisted_artworks=top_wishlisted_artworks
    )



@app.route('/<user_type>/dashboard')
@login_required
def dashboard(user_type):
    if user_type == "curator":
        return render_template('curator_dashboard.html')
    elif user_type == "customer":
        return render_template('html_front.html')
    elif user_type == "admin":
        return render_template('admin_dashboard.html')
    elif user_type == "artist":
        return redirect(url_for('artist_dashboard', artist_id=current_user.id))
    
@app.route('/auction_page', methods=['GET'])
def auction_page():
    # Connect to the database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Fetch ongoing auctions
    ongoing_query = """
        SELECT auction_id, auction_name, start_date, end_date
        FROM Auction
        WHERE NOW() BETWEEN start_date AND end_date
        ORDER BY start_date ASC
    """
    cursor.execute(ongoing_query)
    ongoing_auctions = cursor.fetchall()

    # Fetch scheduled auctions
    scheduled_query = """
        SELECT auction_id, auction_name, start_date, end_date
        FROM Auction
        WHERE NOW() < start_date
        ORDER BY start_date ASC
    """
    cursor.execute(scheduled_query)
    scheduled_auctions = cursor.fetchall()

    # Fetch artworks that are 'auctioned' (no join with auction_artwork)
    artworks_by_auction = {}
    for auction in ongoing_auctions:
        auction_id = auction['auction_id']
        cursor.execute("""
            SELECT artwork_id, title, description
            FROM artwork
            WHERE status = 'auctioned'
        """)
        artworks_by_auction[auction_id] = cursor.fetchall()
        

       




    # Close the database connection
    cursor.close()
    conn.close()

    # Check if the logged-in user is a customer
    user_type = session.get('user_type')  # Assuming user type is stored in the session

    # Render the auction page
    return render_template(
        'auction_page.html',
        ongoing_auctions=ongoing_auctions,
        scheduled_auctions=scheduled_auctions,
        artworks_by_auction=artworks_by_auction,
        user_type=user_type  # Pass user type to the template
    )

 
@app.route('/submit_bid/<int:auction_id>', methods=['POST'])
def submit_bid(auction_id):
    try:
        # Fetch bid amount from the form
        bid_amount = float(request.form['bid_amount'])

        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Fetch the current highest bid and auction details
        cursor.execute("SELECT current_highest_bid FROM auction WHERE auction_id = %s", (auction_id,))
        auction = cursor.fetchone()

        # Check if the auction exists
        if not auction:
            flash("Auction not found.", "error")
            return redirect(url_for('auction_page'))

        current_highest_bid = auction['current_highest_bid']

        # Ensure the new bid is higher than the current highest bid
        if bid_amount <= current_highest_bid:
            flash("Bid amount must be higher than the current highest bid.", "error")
            return redirect(url_for('bids', auction_id=auction_id))

        # Insert the bid into the bids table
        cursor.execute(
            """
            INSERT INTO bids (auction_id, bid_amount, user_id, bid_time)
            VALUES (%s, %s, %s, NOW())
            """,
            (auction_id, bid_amount, session.get('user_id'))  # Assuming user_id is stored in session
        )

        # Update the current highest bid in the auction table
        cursor.execute(
            "UPDATE auction SET current_highest_bid = %s WHERE auction_id = %s",
            (bid_amount, auction_id)
        )

        conn.commit()

        flash("Your bid has been placed successfully!", "success")
        return redirect(url_for('bids', auction_id=auction_id))

    except Exception as e:
        flash(f"An error occurred: {e}", "error")
        return redirect(url_for('auction_page'))

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/bids/<int:auction_id>')
def bids(auction_id):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Fetch auction details
        cursor.execute("SELECT * FROM auction WHERE auction_id = %s", (auction_id,))
        auction = cursor.fetchone()

        # Fetch all bids for the auction
        cursor.execute(
            "SELECT * FROM bids WHERE auction_id = %s ORDER BY bid_time DESC",
            (auction_id,)
        )
        bids = cursor.fetchall()

        return render_template('bids.html', auction=auction, bids=bids, current_highest_bid=auction['current_highest_bid'])

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/artist_dashboard/<artist_id>')
def artist_dashboard(artist_id):
    
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    try:
        
        # Fetch artist details
        cursor.execute("SELECT name FROM Artist WHERE artist_id = %s", (artist_id,))
        artist = cursor.fetchone()
      
        # Fetch up to 3 featured artworks for the artist
        cursor.execute("""
            SELECT artwork_id, title, description, price, image_url 
            FROM Artwork 
            WHERE artist_id = %s 
            LIMIT 3
        """, (artist_id,))
        featured_artworks = cursor.fetchall()

    finally:
        # Close the database connection
        cursor.close()
        conn.close()

    return render_template(
        'artist_dashboard.html',
        artist_name=artist['name'],
        featured_artworks=featured_artworks
    )


@app.route('/featured_artworks')
def featured_artworks():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Fetch featured artworks from the database
    cursor.execute("""
        SELECT artwork_id, title, description, creation_date, price, image_url
        FROM artwork
        ORDER BY creation_date DESC
    """)
    featured_artworks = cursor.fetchall()

    # Close the database connection
    cursor.close()
    conn.close()

    return render_template('featured_artworks.html', artworks=featured_artworks)


@app.route('/notifications/<artist_id>')
def notifications(artist_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Fetch notifications for the artist
    cursor.execute("SELECT message FROM Notifications WHERE artist_id = %s", (artist_id,))
    notifications = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('notifications.html', notifications=notifications)

@app.route('/auctions/<artist_id>')
def auctions(artist_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Fetch artworks in auctions
    cursor.execute("""
        SELECT a.artwork_id, a.title, a.image_url, au.auction_end_date, au.highest_bid
        FROM Artwork a
        JOIN Auction au ON a.artwork_id = au.artwork_id
        WHERE a.artist_id = %s
    """, (artist_id,))
    auctions = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('auction_page.html', auctions=auctions)

if __name__ == '__main__':
    app.run(debug=True)


