 -- 1. Wish List Table
CREATE TABLE WishList (
    wishlist_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    artwork_id INT,
    date_added DATETIME,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (artwork_id) REFERENCES Artwork(artwork_id)
);

-- 2. Artist Table
CREATE TABLE Artist (
    artist_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    biography TEXT,
    birth_date DATE,
    country VARCHAR(100),
    email VARCHAR(255),
    profile_picture VARCHAR(255)
);

-- 3. Artwork Table
CREATE TABLE Artwork (
    artwork_id INT AUTO_INCREMENT PRIMARY KEY,
    artist_id INT,
    category_id INT,
    title VARCHAR(255),
    description TEXT,
    creation_date DATE,
    price DECIMAL(10, 2),
    image_url VARCHAR(255),
    status ENUM('available', 'sold', 'auctioned'),
    FOREIGN KEY (artist_id) REFERENCES Artist(artist_id),
    FOREIGN KEY (category_id) REFERENCES Category(category_id)
);

-- 4. Purchase Table
CREATE TABLE Purchase (
    purchase_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    artwork_id INT,
    purchase_date DATETIME,
    amount DECIMAL(10, 2),
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (artwork_id) REFERENCES Artwork(artwork_id)
);

-- 5. Bids Table
CREATE TABLE Bids (
    bid_id INT AUTO_INCREMENT PRIMARY KEY,
    auction_id INT,
    customer_id INT,
    bid_amount DECIMAL(10, 2),
    bid_date DATETIME,
    status ENUM('active', 'won', 'outbid'),
    FOREIGN KEY (auction_id) REFERENCES Auction(auction_id),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

-- 6. Review Table
CREATE TABLE Review (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    artwork_id INT,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    review_date DATETIME,
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id),
    FOREIGN KEY (artwork_id) REFERENCES Artwork(artwork_id)
);

-- 7. Auction Table
CREATE TABLE Auction (
    auction_id INT AUTO_INCREMENT PRIMARY KEY,
    artwork_id INT,
    start_date DATETIME,
    end_date DATETIME,
    starting_bid DECIMAL(10, 2),
    current_highest_bid DECIMAL(10, 2),
    status ENUM('active', 'completed'),
    auction_name VARCHAR(255),
    FOREIGN KEY (artwork_id) REFERENCES Artwork(artwork_id)
);

-- 8. Curator Table
CREATE TABLE Curator (
    curator_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    assigned_category INT,
    bio TEXT,
    FOREIGN KEY (assigned_category) REFERENCES Category(category_id)
);

-- 9. Notification Table
CREATE TABLE Notification (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    message TEXT,
    date DATETIME,
    status ENUM('read', 'unread'),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
);

-- 10. Customer Table
CREATE TABLE Customer (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    email VARCHAR(255),
    date_joined DATETIME,
    profile_picture VARCHAR(255),
    contact_number VARCHAR(20)
);

-- 11. Admin Table
CREATE TABLE Admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    email VARCHAR(255),
    role ENUM('superadmin', 'moderator')
);

-- 12. Category Table
CREATE TABLE Category (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    description TEXT
);
select * from auction
ALTER TABLE admin CHANGE username name VARCHAR(255) NOT NULL;
ALTER TABLE artist
ADD COLUMN password VARCHAR(255) NOT NULL;
CREATE TABLE auction_artwork (
    auction_artwork_id INT AUTO_INCREMENT PRIMARY KEY,   -- Unique ID for each entry in the junction table
    auction_id INT,                                      -- Foreign key to the auction table
    artwork_id INT,                                      -- Foreign key to the artwork table
    FOREIGN KEY (auction_id) REFERENCES Auction(auction_id) ON DELETE CASCADE,
    FOREIGN KEY (artwork_id) REFERENCES artwork(artwork_id) ON DELETE CASCADE
);
select * from artwork;
INSERT INTO wishlist (customer_id, artwork_id, date_added) VALUES
(1, 16, NOW()),
(2, 16, NOW()),
(3, 16, NOW()),
(4, 17, NOW()),
(5, 20, NOW());
INSERT INTO customer (name, password, email, date_joined, profile_picture, contact_number, role) VALUES
('Alice Johnson', 'password123', 'alice@example.com', NOW(), 'alice.jpg', '1234567890', 'customer'),
('Bob Smith', 'password456', 'bob@example.com', NOW(), 'bob.jpg', '0987654321', 'customer'),
('Charlie Brown', 'password789', 'charlie@example.com', NOW(), 'charlie.jpg', '1122334455', 'customer'),
('David Clark', 'password101', 'david@example.com', NOW(), 'david.jpg', '2233445566', 'customer'),
('Eva Williams', 'password202', 'eva@example.com', NOW(), 'eva.jpg', '3344556677', 'customer');

INSERT INTO category (name, description) VALUES
('Painting', 'Artworks created using paint on various surfaces'),
('Sculpture', 'Three-dimensional art pieces created by shaping materials'),
('Photography', 'Art of capturing still images using cameras'),
('Printmaking', 'Art of creating prints on paper or other materials'),
('Mixed Media', 'Art that combines different artistic materials');

INSERT INTO artist (name, biography, birth_date, country, email, profile_picture,password) VALUES
('Leonardo da Vinci', 'Renaissance artist and inventor', '1452-04-15', 'Italy', 'leonardo@example.com', 'leonardo.jpg','1222'),
('Pablo Picasso', 'Spanish painter and sculptor', '1881-10-25', 'Spain', 'picasso@example.com', 'picasso.jpg','1445dd'),
('Vincent van Gogh', 'Dutch painter, known for his post-impressionist works', '1853-03-30', 'Netherlands', 'vincent@example.com', 'vincent.jpg','abc'),
('Claude Monet', 'French painter, founder of Impressionism', '1840-11-14', 'France', 'claude@example.com', 'claude.jpg','sdf'),
('Frida Kahlo', 'Mexican painter known for her self-portraits', '1907-07-06', 'Mexico', 'frida@example.com', 'frida.jpg','wee');
INSERT INTO artwork (artist_id, category_id, title, description, creation_date, price, image_url, status) VALUES
(1, 1, 'Mona Lisa', 'A portrait painting by Leonardo da Vinci', '1503-01-01', 1000000.00, 'mona_lisa.jpg', 'available'),
(2, 1, 'Guernica', 'A mural painting by Pablo Picasso', '1937-04-01', 500000.00, 'guernica.jpg', 'available'),
(3, 1, 'Starry Night', 'A famous oil painting by Vincent van Gogh', '1889-06-01', 700000.00, 'starry_night.jpg', 'available'),
(4, 1, 'Water Lilies', 'A series of paintings by Claude Monet', '1914-10-26', 800000.00, 'water_lilies.jpg', 'available'),
(5, 1, 'The Two Fridas', 'A double self-portrait by Frida Kahlo', '1939-01-01', 600000.00, 'two_fridas.jpg', 'available');
select * from artwork;

DELETE FROM Artwork WHERE artwork_id IS NOT NULL;

 DELETE FROM Artwork;
SET SQL_SAFE_UPDATES = 0;


INSERT INTO artwork (artist_id, category_id, title, description, creation_date, price, image_url, status)
VALUES
(1, 1, 'street art 3', 'Description for street art 3', '2024-12-06', 100.00, '/static/images/street art 3.jpeg', 'available'),
(1, 2, 'street art 4', 'Description for street art 4', '2024-12-06', 120.00, '/static/images/street art 4.jpeg', 'available'),
(1, 2, 'street art 5', 'Description for street art 5', '2024-12-06', 130.00, '/static/images/street art 5.jpeg', 'available'),
(1, 3, 'time lapse 1', 'Description for time lapse 1', '2024-12-06', 150.00, '/static/images/time lapse 1.mp4', 'available'),
(1, 3, 'time lapse 2', 'Description for time lapse 2', '2024-12-06', 160.00, '/static/images/time lapse 2.mp4', 'available'),
(1, 4, 'view to live for', 'Description for view to live for', '2024-12-06', 110.00, '/static/images/view to live for.jpeg', 'available'),
(1, 5, 'landscape 5', 'Description for landscape 5', '2024-12-06', 180.00, '/static/images/landscape 5.jpeg', 'available'),
(1, 6, 'motion graphic 4', 'Description for motion graphic 4', '2024-12-06', 200.00, '/static/images/motion graphic 4.mp4', 'available'),
(1, 6, 'motion graphic 5', 'Description for motion graphic 5', '2024-12-06', 210.00, '/static/images/motion graphic 5.mp4', 'available'),
(1, 7, 'one night at the lake', 'Description for one night at the lake', '2024-12-06', 140.00, '/static/images/one night at the lake.jpeg', 'available'),
(1, 8, 'qjqzxjq-2', 'Description for qjqzxjq-2', '2024-12-06', 90.00, '/static/images/qjqzxjq-2.jpeg', 'available'),
(1, 9, 'street art 2', 'Description for street art 2', '2024-12-06', 100.00, '/static/images/street art 2.jpeg', 'available'),
(1, 10, 'apple inside box', 'Description for apple inside box', '2024-12-06', 150.00, '/static/images/apple inside box.jpeg', 'available'),
(1, 1, 'calligraphy 2', 'Description for calligraphy 2', '2024-12-06', 160.00, '/static/images/calligraphy 2.jpeg', 'available'),
(1, 2, 'Checkers-in-Russian-100x100-cm-oil-canvas-', 'Description for Checkers-in-Russian', '2024-12-06', 180.00, '/static/images/Checkers-in-Russian-100x100-cm-oil-canvas-.jpeg', 'available'),
(1, 3, 'eye of the', 'Description for eye of the', '2024-12-06', 170.00, '/static/images/eye of the.jpeg', 'available'),
(1, 4, 'jar of buttons', 'Description for jar of buttons', '2024-12-06', 160.00, '/static/images/jar of buttons.jpeg', 'available'),
(1, 5, 'street art 1', 'Description for street art 1', '2024-12-06', 110.00, '/static/images/street art 1.jpeg', 'available'),
(1, 6, 'landscape 1', 'Description for landscape 1', '2024-12-06', 180.00, '/static/images/landscape 1.jpeg', 'available'),
(1, 7, 'landscape 3', 'Description for landscape 3', '2024-12-06', 190.00, '/static/images/landscape 3.jpeg', 'available'),
(1, 8, 'motion graphic 2', 'Description for motion graphic 2', '2024-12-06', 200.00, '/static/images/motion graphic 2.mp4', 'available'),
(1, 9, 'motion graphic 6', 'Description for motion graphic 6', '2024-12-06', 210.00, '/static/images/motion graphic 6.mp4', 'available'),
(1, 10, 'morning train', 'Description for morning train', '2024-12-06', 150.00, '/static/images/morning train.jpeg', 'available'),
(1, 1, 'other world', 'Description for other world', '2024-12-06', 160.00, '/static/images/other world.jpeg', 'available'),
(1, 2, 'ships', 'Description for ships', '2024-12-06', 170.00, '/static/images/ships.jpeg', 'available'),
(1, 3, 'plants from elsewhere', 'Description for plants from elsewhere', '2024-12-06', 180.00, '/static/images/plants from elsewhere.jpeg', 'available'),
(1, 4, 'silent eyes', 'Description for silent eyes', '2024-12-06', 150.00, '/static/images/silent eyes.jpeg', 'available'),
(1, 5, '2020', 'Description for 2020', '2024-12-06', 200.00, '/static/images/2020.jpeg', 'available'),
(1, 6, 'born from sky', 'Description for born from sky', '2024-12-06', 190.00, '/static/images/born from sky.jpeg', 'available'),
(1, 7, 'a home', 'Description for a home', '2024-12-06', 150.00, '/static/images/a home.jpeg', 'available'),
(1, 8, 'butterfly on sunflower', 'Description for butterfly on sunflower', '2024-12-06', 160.00, '/static/images/butterfly on sunflower.jpeg', 'available'),
(1, 9, 'calligraphy 3', 'Description for calligraphy 3', '2024-12-06', 130.00, '/static/images/calligraphy 3.jpeg', 'available'),
(1, 10, 'calligraphy 4', 'Description for calligraphy 4', '2024-12-06', 140.00, '/static/images/calligraphy 4.jpeg', 'available'),
(1, 1, 'Drapery-IV', 'Description for Drapery-IV', '2024-12-06', 220.00, '/static/images/Drapery-IV.jpeg', 'available'),
(1, 2, 'future city', 'Description for future city', '2024-12-06', 200.00, '/static/images/future city.jpeg', 'available');

INSERT INTO category (name, description)
VALUES
('Street Art', 'Urban art, often created in public spaces, that includes graffiti, murals, and other forms of creative expression.'),
('Photography', 'Art created through capturing images with a camera, including both traditional and digital photography.'),
('Time Lapse', 'A type of photography where the time between each shot is greatly increased, creating a video that shows changes over a longer period.'),
('Landscape', 'Art that focuses on the depiction of natural scenery such as mountains, valleys, trees, rivers, and forests.'),
('Motion Graphics', 'Graphic design elements that are animated to create visual storytelling and interactive media.'),
('Abstract', 'Art that does not attempt to represent reality but instead uses shapes, colors, and forms to create a new visual experience.'),
('Calligraphy', 'The art of beautiful handwriting, often used to create decorative letters and intricate designs.'),
('Mixed Media', 'Artworks created by combining different media or materials, often blending traditional and contemporary techniques.'),
('Surrealism', 'A 20th-century avant-garde movement that sought to express the unconscious mind, dreams, and irrational images.'),
('Pop Art', 'An art movement that draws on popular culture and everyday objects, often using bright colors and bold imagery.'),
('Illustration', 'Visual artwork used to clarify, decorate, or add to text, often used in books, magazines, and other media.'),
('Conceptual', 'Art that emphasizes the idea or concept over the traditional aesthetic or material qualities of the artwork.');

delete from artwork where id=16
UPDATE artwork
SET image_url = REPLACE(image_url, '.jpeg', '.jpg')
WHERE image_url LIKE '%.jpeg';
DELETE FROM artwork
WHERE id = 18;
insert into wishlist valu( )
select * from customer

select * from bids
select * from auction