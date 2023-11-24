use travel;
#
create table tour(
	tourid INT AUTO_INCREMENT PRIMARY KEY, 
    tname CHAR(50), 
    tdesc CHAR(250), 
    cost INT, 
    imgsrc VARCHAR(100), 
    duration INT
);

INSERT INTO tour (tname, tdesc, cost, imgsrc, duration)
VALUES ('Explore the Serengeti', 'Embark on a once-in-a-lifetime adventure through the stunning landscapes of the Serengeti. Witness the Great Migration, spot the Big Five, and experience the rich culture of Tanzania.', 3499, 'static/tour1.jpg', '6');

INSERT INTO tour (tname, tdesc, cost, imgsrc, duration)
VALUES ('Enchanting Paris Getaway', 'Fall in love with the City of Light on this romantic Parisian escape. Explore iconic landmarks, savor gourmet cuisine, and cruise the Seine River.', 1999, 'static/tour2.jpg', '8');

INSERT INTO tour (tname, tdesc, cost, imgsrc, duration)
VALUES ('Caribbean Paradise Cruise', 'Set sail to the turquoise waters of the Caribbean. Enjoy endless sunshine, pristine beaches, and island-hopping adventures in this tropical paradise.', 2799, 'static/tour3.jpg', '3');

INSERT INTO tour (tname, tdesc, cost, imgsrc, duration)
VALUES ('Historic Europe Discovery', 'Travel back in time to explore the history and culture of Europe''s most iconic cities. Visit ancient castles, wander charming streets, and indulge in local cuisine.', 2899, 'static/tour4.jpg', '5');

INSERT INTO tour (tname, tdesc, cost, imgsrc, duration)
VALUES ('Adventure in Costa Rica', 'Unleash your adventurous spirit in Costa Rica''s lush rainforests and coastal paradises. Zip-line through the canopy, surf the Pacific waves, and encounter exotic wildlife.', 2199, 'static/tour5.jpg', '12');

INSERT INTO tour (tname, tdesc, cost, imgsrc, duration)
VALUES ('Magical Egypt Expedition', 'Journey along the banks of the Nile to uncover the mysteries of ancient Egypt. Explore the pyramids, cruise the Nile, and immerse yourself in pharaonic history.', 2599, 'static/tour6.jpg', '5');


create table contactus(
	messid INT AUTO_INCREMENT PRIMARY KEY, 
    mname CHAR(50), 
    memail CHAR(50), 
    maddress CHAR(50), 
    message CHAR(50)
);
create table user(
	userid INT AUTO_INCREMENT PRIMARY KEY, 
    username CHAR(50), 
    password CHAR(150), 
    email CHAR(50) UNIQUE, 
    phoneno INT, 
    role VARCHAR(50) DEFAULT 'user'    
);
INSERT INTO user (username, password, role) VALUES ('admin', 'admin', 'admin');
create table transportation(
	transportid INT AUTO_INCREMENT PRIMARY KEY, 
    trname CHAR(50), 
    trtype CHAR(50), 
    capacity INT, 
    trprice CHAR(50), 
    PRIMARY KEY(transportid)
);
create table booking (
    bookid INT AUTO_INCREMENT PRIMARY KEY,
    tourid INT,
    userid INT,
    transportid INT DEFAULT 1,
    total_cost INT,
    num_travelers INT,
    FOREIGN KEY (tourid) REFERENCES tour(tourid),
    FOREIGN KEY (userid) REFERENCES user(userid),
    FOREIGN KEY (transportid) REFERENCES transportation(transportid)
);


-- trigger that calculates and sets the total cost when a booking is inserted
DELIMITER //
CREATE TRIGGER calculate_total_cost
BEFORE INSERT ON booking
FOR EACH ROW
BEGIN
  DECLARE tour_price INT;
  DECLARE transport_cost INT;
  SELECT cost INTO tour_price FROM tour WHERE tourid = NEW.tourid;
  SELECT trprice INTO transport_cost FROM transportation WHERE transportid = NEW.transportid;
  SET NEW.total_cost = tour_price * NEW.num_travelers + transport_cost;
END;
//
DELIMITER ;


INSERT INTO transportation (trname, trtype, capacity, trprice) VALUES ('Compact Car', 'Car', 4, 50);
INSERT INTO transportation (trname, trtype, capacity, trprice) VALUES ('Luxury SUV', 'Car', 5, 120);
INSERT INTO transportation (trname, trtype, capacity, trprice) VALUES ('Minibus', 'Bus', 12, 200);
INSERT INTO transportation (trname, trtype, capacity, trprice) VALUES ('Double-Decker Bus', 'Bus', 50, 500);
INSERT INTO transportation (trname, trtype, capacity, trprice) VALUES ('Vintage Car', 'Car', 2, 80);

-- Procedure that gets the total revenue from all bookings
DELIMITER //
CREATE PROCEDURE generate_booking_stats()
BEGIN
SELECT COUNT(*) AS no_bookings,
SUM(total_cost) AS total_revenue
FROM booking;
END //
DELIMITER ;

SELECT userid, COUNT(*) AS number_of_tours
FROM booking
WHERE userid IN (SELECT DISTINCT userid FROM booking) and userid <> 0
GROUP BY userid;

SELECT username
FROM user
WHERE NOT EXISTS (SELECT * FROM booking WHERE user.userid = booking.userid);

SELECT user.userid, user.username, IFNULL(COUNT(booking.tourid), 0) AS number_booked
FROM user
LEFT JOIN booking ON user.userid = booking.userid
WHERE user.userid <> 1
GROUP BY user.userid, user.username;


SELECT b.bookid, t.tname, u.username, b.num_travelers, b.total_cost, tr.trname FROM booking b JOIN tour t ON b.tourid = t.tourid JOIN user u ON b.userid = u.userid JOIN transportation tr ON b.transportid = tr.transportid WHERE u.userid <> 0;

SELECT trname AS transport, number_of_tours AS tours_per_transport FROM (SELECT t.trname, COUNT(b.tourid) AS number_of_tours FROM transportation t LEFT JOIN booking b ON t.transportid = b.transportid GROUP BY t.trname) AS transport_stats GROUP BY transport;

SELECT b.bookid, t.tname, u.username, b.num_travelers, b.total_cost, tr.trname FROM booking b JOIN tour t ON b.tourid = t.tourid JOIN user u ON b.userid = u.userid JOIN transportation tr ON b.transportid = tr.transportid;


-- SET SQL_SAFE_UPDATES = 1;
