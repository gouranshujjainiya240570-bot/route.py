create database if not exists busmg;
use busmg;

-- Students Table
CREATE TABLE IF NOT EXISTS Students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

-- Drivers Table
CREATE TABLE IF NOT EXISTS Drivers (
    driver_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    experience_years INT
);

-- Buses Table
CREATE TABLE IF NOT EXISTS Buses (
    bus_id INT AUTO_INCREMENT PRIMARY KEY,
    bus_number VARCHAR(50) UNIQUE NOT NULL,
    capacity INT,
    driver_id INT,
    FOREIGN KEY (driver_id) REFERENCES Drivers(driver_id)
);

-- Routes Table
CREATE TABLE IF NOT EXISTS Routes (
    route_id INT AUTO_INCREMENT PRIMARY KEY,
    route_name VARCHAR(100) NOT NULL,
    start_point VARCHAR(100),
    end_point VARCHAR(100)
);

-- Stops Table
CREATE TABLE IF NOT EXISTS Stops (
    stop_id INT AUTO_INCREMENT PRIMARY KEY,
    stop_name VARCHAR(100) NOT NULL
);

-- Route_Stops Table (Many-to-Many between Routes and Stops)
CREATE TABLE IF NOT EXISTS Route_Stops (
    route_stop_id INT AUTO_INCREMENT PRIMARY KEY,
    route_id INT,
    stop_id INT,
    stop_order INT,
    FOREIGN KEY (route_id) REFERENCES Routes(route_id),
    FOREIGN KEY (stop_id) REFERENCES Stops(stop_id)
);

-- Schedules Table
CREATE TABLE IF NOT EXISTS Schedules (
    schedule_id INT AUTO_INCREMENT PRIMARY KEY,
    bus_id INT,
    route_id INT,
    arrival_time_1st_shift TIME,
    arrival_time_2nd_shift TIME,
    FOREIGN KEY (bus_id) REFERENCES Buses(bus_id),
    FOREIGN KEY (route_id) REFERENCES Routes(route_id)
);

-- Student_Routes Table (Mapping Students to Routes)
CREATE TABLE IF NOT EXISTS Student_Routes (
    student_route_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    route_id INT,
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (route_id) REFERENCES Routes(route_id)
);

-- Notices Table
CREATE TABLE IF NOT EXISTS Notices (
    notice_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expiry_date DATE,
    target_route_id INT,
    FOREIGN KEY (target_route_id) REFERENCES Routes(route_id)
);

-- ============================================================
-- SEED DATA FROM Bus-Route.pdf (July 2015 Schedule)
-- ============================================================

-- Drivers (from PDF - all 40 drivers)
INSERT INTO Drivers (name, phone_number, experience_years) VALUES
('Shri Santosh Choudhary', '9893000001', 5),
('Shri Ravi Rathore', '9893000002', 6),
('Shri Mohammad Firoz', '9893000003', 7),
('Shri Onkarlal Choudhary', '9893000004', 8),
('Shri Gautam Nagar', '9893000005', 4),
('Shri D. Makwana', '9893000006', 10),
('Jeevan S Thakur', '9893000007', 9),
('Shri Praveen Yadav', '9893000008', 6),
('Shri Kayyum Khan', '9893000009', 7),
('Shri Jeevan S Chavda', '9893000010', 5),
('Shri Ghanshyam Chouhan', '9893000011', 8),
('Shri Murarilal ji Mandloi', '9893000012', 6),
('Shri Gajju Limanpure', '9893000013', 7),
('Shri Rajendra Choudhary', '9893000014', 9),
('Shri Lakhan Thakur', '9893000015', 5),
('Shri Ishtikhar Hussain', '9893000016', 6),
('Shri Ranjeet Patel', '9893000017', 7),
('Shri Rajesh Patel', '9893000018', 8),
('Shri Champalal', '9893000019', 4),
('Shri Nilesh Patel', '9893000020', 6),
('Shri Vikram Patel', '9893000021', 7),
('Shri Prahlad Makwana', '9893000022', 5),
('Shri Akhilesh Patel', '9893000023', 8),
('Shri Jagdeesh Jatwa', '9893000024', 6),
('Shri Rajendra Rajpoot', '9893000025', 7),
('Shri Babulal Patel', '9893000026', 9),
('Shri Anil Choudhary', '9893000027', 5),
('Shri Anand Malviya', '9893000028', 6),
('Shri Lalji Malviya', '9893000029', 7),
('Shri Ramchander Baloniya', '9893000030', 8),
('Shri Chander Singh', '9893000031', 6),
('Shri Shankar Patel', '9893000032', 7),
('Shri Ganesh Patel', '9893000033', 5),
('Shri Dinesh Patel', '9893000034', 6),
('Shri Azamat Ali', '9893000035', 7),
('Shri Shriram Rawat', '9893000036', 8),
('Shri Madhav S. Dhakad', '9893000037', 6),
('Shri Omprakash Patel', '9893000038', 7),
('Shri Mukesh Patel', '9893000039', 5),
('Pappu Prajapat', '9575503760', 9);

-- ============================================================
-- ROUTES (5 routes with full details from PDF)
-- ============================================================
INSERT INTO Routes (route_name, start_point, end_point) VALUES
('Route 1 - Pragati Nagar', 'Pragati Nagar Ring Road', 'Acropolis College'),
('Route 3 - Kila Maidan', 'Kila Maidan', 'Acropolis College'),
('Route 5 - RTO', 'RTO', 'Acropolis College'),
('Route 7 - Gandhi Nagar', 'Gandhi Nagar', 'Acropolis College'),
('Route 10 - Bhamori Plaza', 'Bhamori Plaza', 'Acropolis College');

-- ============================================================
-- BUSES with correct driver assignments (from PDF)
-- ============================================================
-- Route 1 buses: Driver IDs 1(Santosh), 2(Ravi), 3(Mohammad Firoz)
INSERT INTO Buses (bus_number, capacity, driver_id) VALUES
('MP-09FA-5572', 52, 1),
('MP-09FA-4890', 52, 2),
('MP-09FA-4387', 52, 3);

-- Route 3 buses: Driver IDs 4(Onkarlal), 5(Gautam Nagar)
INSERT INTO Buses (bus_number, capacity, driver_id) VALUES
('MP-09FA-4892', 52, 4),
('MP-09FA-1691', 52, 5);

-- Route 5 buses: Driver IDs 6(D.Makwana), 7(Jeevan S Thakur), 8(Praveen Yadav)
INSERT INTO Buses (bus_number, capacity, driver_id) VALUES
('MP-09FA-3944', 52, 6),
('MP-09FA-1525', 52, 7),
('MP-09FA-1081', 52, 8);

-- Route 7 buses: Driver IDs 11(Ghanshyam Chouhan), 12(Murarilal), 13(Gajju Limanpure)
INSERT INTO Buses (bus_number, capacity, driver_id) VALUES
('MP-09FA-5571', 52, 11),
('MP-09FA-1521', 52, 12),
('MP-09FA-4889', 52, 13);

-- Route 10 buses: Driver IDs 20(Nilesh Patel), 21(Vikram Patel), 22(Prahlad Makwana)
INSERT INTO Buses (bus_number, capacity, driver_id) VALUES
('MP-09FA-5574', 52, 20),
('MP-09FA-4386', 52, 21),
('MP-09FA-4388', 52, 22);

-- ============================================================
-- STOPS - Insert all unique stops from the 5 routes
-- ============================================================
INSERT INTO Stops (stop_name) VALUES
('Pragati Nagar Ring Road'),
('CAT Chouraha'),
('Hawa Bungla (CAT Road)'),
('Gopur Chowki (Ring Road)'),
('Jarolia Market'),
('Sai Dwar'),
('Relax Garden'),
('Sudama Nagar Ring Road'),
('Footi Kothi Chouraha'),
('Suruchi Garden'),
('Reliance Fresh Footi Kothi Chouraha'),
('Chandan Nagar Thana'),
('Shankar Kirana Gumasta Nagar'),
('Gumasta Nagar Shiv Mandir'),
('Gumasta Nagar Chouraha'),
('Charumedicoz (Kothari Clinic)'),
('Ranjit Hanuman'),
('Dravid Nagar'),
('Usha Nagar'),
('Mhow Naka Shiv Mandir'),
('Mhow Naka Chouraha'),
('Old GDC Jairampur Colony Chouraha'),
('Collector Chauraha'),
('Palsikar Chauraha'),
('Juni Indore Bridge'),
('Sindhi Colony'),
('Ashok Nagar Bhauwarkua Main Road'),
('Bhauwarkua Chouraha'),
('Navlakha Chouraha'),
('Nemawar Road'),
('Teen Imli'),
('Musakhedi'),
('Acropolis College'),
('Kila Maidan'),
('Banganga Stop Old Naka'),
('Sangam Nagar'),
('Khada Ganpati'),
('Mahesh Gard Line Petrol Pump'),
('Marimata Chouraha'),
('Agniban Press Chouraha'),
('Rajkumar Bridge (Vallabh Nagar)'),
('Malwa Mill'),
('Ranisati Gate'),
('City Office Chouraha'),
('Janjirwala Chouraha'),
('Mahidpurwala Chouraha'),
('Palasia Thana'),
('Khajrana Chouraha'),
('Malvi Petrol Pump'),
('RTO'),
('Lokmanya Nagar'),
('Vinay Nagar'),
('Keshar Bag Railway Bridge'),
('Kodariya (Mhow)'),
('Dreamland Square'),
('Hotel Shyam Vilas Palace'),
('Hari Phatak Railway Crossing'),
('Rau Bypass'),
('Rau A.B. Road Bus Stand'),
('Silicon City'),
('IPS College'),
('Rajendra Nagar Thana'),
('Bijalpur Chouraha'),
('Gadbadi Pooliya'),
('Choithram Mandi Chouraha'),
('Rajiv Gandhi Chouraha'),
('Vishnupuri Chouraha'),
('Indrapuri'),
('Asharam Bapu Chouraha'),
('SDPS College'),
('Teen Imali Square'),
('Khandwa Naka Chouraha'),
('Mushakhedi Square'),
('Pipliya Hana Square'),
('Limbodi Gate Rani Bagh'),
('Tejaji Nagar'),
('Gandhi Nagar'),
('Aerodrum Thana'),
('Vidhya Dham'),
('Kalani Nagar'),
('Shikshak Nagar'),
('Ramchand Nagar Petrol Pump'),
('Bada Ganpati'),
('Rajmohalla Chouraha Petrol Pump'),
('Malganj Chouraha'),
('Narsingh Bazar Chouraha'),
('Bartanbazar Chouraha'),
('Gurudwara Jawaharmarg'),
('Saifi Hotel'),
('Patel Bridge'),
('Patel Pratima'),
('Shrimaya Hotel Madhumilan Chou.'),
('Dhakkanwala Kua'),
('Kanadia Bypass'),
('Bhamori Plaza'),
('Astha Talkies'),
('Patnipura Chouraha'),
('Bhandari Bridge Thana'),
('Subhash Nagar'),
('Pardeshipura'),
('Nanda Nagar Teen Puliya'),
('Nanda Nagar'),
('Patnipura'),
('Atal Dwar'),
('Christian Eminent School'),
('LIG Square'),
('Press Complex'),
('Malviya Nagar Chouraha'),
('Rasoma Chouraha'),
('Vijay Nagar RTO Office'),
('Hotel Redison Chouraha'),
('Bypass');

-- ============================================================
-- ROUTE_STOPS - Map stops to each route with order
-- ============================================================

-- Route 1: Pragati Nagar → Acropolis College (33 stops)
INSERT INTO Route_Stops (route_id, stop_id, stop_order)
SELECT 1, stop_id, pos.ord FROM Stops s JOIN (
  SELECT 'Pragati Nagar Ring Road' AS name, 1 AS ord UNION ALL
  SELECT 'CAT Chouraha', 2 UNION ALL
  SELECT 'Hawa Bungla (CAT Road)', 3 UNION ALL
  SELECT 'Gopur Chowki (Ring Road)', 4 UNION ALL
  SELECT 'Jarolia Market', 5 UNION ALL
  SELECT 'Sai Dwar', 6 UNION ALL
  SELECT 'Relax Garden', 7 UNION ALL
  SELECT 'Sudama Nagar Ring Road', 8 UNION ALL
  SELECT 'Footi Kothi Chouraha', 9 UNION ALL
  SELECT 'Suruchi Garden', 10 UNION ALL
  SELECT 'Reliance Fresh Footi Kothi Chouraha', 11 UNION ALL
  SELECT 'Chandan Nagar Thana', 12 UNION ALL
  SELECT 'Shankar Kirana Gumasta Nagar', 13 UNION ALL
  SELECT 'Gumasta Nagar Shiv Mandir', 14 UNION ALL
  SELECT 'Gumasta Nagar Chouraha', 15 UNION ALL
  SELECT 'Charumedicoz (Kothari Clinic)', 16 UNION ALL
  SELECT 'Ranjit Hanuman', 17 UNION ALL
  SELECT 'Dravid Nagar', 18 UNION ALL
  SELECT 'Usha Nagar', 19 UNION ALL
  SELECT 'Mhow Naka Shiv Mandir', 20 UNION ALL
  SELECT 'Mhow Naka Chouraha', 21 UNION ALL
  SELECT 'Old GDC Jairampur Colony Chouraha', 22 UNION ALL
  SELECT 'Collector Chauraha', 23 UNION ALL
  SELECT 'Palsikar Chauraha', 24 UNION ALL
  SELECT 'Juni Indore Bridge', 25 UNION ALL
  SELECT 'Sindhi Colony', 26 UNION ALL
  SELECT 'Ashok Nagar Bhauwarkua Main Road', 27 UNION ALL
  SELECT 'Bhauwarkua Chouraha', 28 UNION ALL
  SELECT 'Navlakha Chouraha', 29 UNION ALL
  SELECT 'Nemawar Road', 30 UNION ALL
  SELECT 'Teen Imli', 31 UNION ALL
  SELECT 'Musakhedi', 32 UNION ALL
  SELECT 'Acropolis College', 33
) pos ON s.stop_name = pos.name;

-- Route 3: Kila Maidan → Acropolis College (17 stops)
INSERT INTO Route_Stops (route_id, stop_id, stop_order)
SELECT 2, stop_id, pos.ord FROM Stops s JOIN (
  SELECT 'Kila Maidan' AS name, 1 AS ord UNION ALL
  SELECT 'Banganga Stop Old Naka', 2 UNION ALL
  SELECT 'Sangam Nagar', 3 UNION ALL
  SELECT 'Khada Ganpati', 4 UNION ALL
  SELECT 'Mahesh Gard Line Petrol Pump', 5 UNION ALL
  SELECT 'Marimata Chouraha', 6 UNION ALL
  SELECT 'Agniban Press Chouraha', 7 UNION ALL
  SELECT 'Rajkumar Bridge (Vallabh Nagar)', 8 UNION ALL
  SELECT 'Malwa Mill', 9 UNION ALL
  SELECT 'Ranisati Gate', 10 UNION ALL
  SELECT 'City Office Chouraha', 11 UNION ALL
  SELECT 'Janjirwala Chouraha', 12 UNION ALL
  SELECT 'Mahidpurwala Chouraha', 13 UNION ALL
  SELECT 'Palasia Thana', 14 UNION ALL
  SELECT 'Khajrana Chouraha', 15 UNION ALL
  SELECT 'Malvi Petrol Pump', 16 UNION ALL
  SELECT 'Acropolis College', 17
) pos ON s.stop_name = pos.name;

-- Route 5: RTO → Acropolis College (29 stops)
INSERT INTO Route_Stops (route_id, stop_id, stop_order)
SELECT 3, stop_id, pos.ord FROM Stops s JOIN (
  SELECT 'RTO' AS name, 1 AS ord UNION ALL
  SELECT 'Lokmanya Nagar', 2 UNION ALL
  SELECT 'Vinay Nagar', 3 UNION ALL
  SELECT 'Keshar Bag Railway Bridge', 4 UNION ALL
  SELECT 'Kodariya (Mhow)', 5 UNION ALL
  SELECT 'Dreamland Square', 6 UNION ALL
  SELECT 'Hotel Shyam Vilas Palace', 7 UNION ALL
  SELECT 'Hari Phatak Railway Crossing', 8 UNION ALL
  SELECT 'Rau Bypass', 9 UNION ALL
  SELECT 'Rau A.B. Road Bus Stand', 10 UNION ALL
  SELECT 'Silicon City', 11 UNION ALL
  SELECT 'IPS College', 12 UNION ALL
  SELECT 'Rajendra Nagar Thana', 13 UNION ALL
  SELECT 'Bijalpur Chouraha', 14 UNION ALL
  SELECT 'Gadbadi Pooliya', 15 UNION ALL
  SELECT 'Choithram Mandi Chouraha', 16 UNION ALL
  SELECT 'Rajiv Gandhi Chouraha', 17 UNION ALL
  SELECT 'Vishnupuri Chouraha', 18 UNION ALL
  SELECT 'Bhauwarkua Chouraha', 19 UNION ALL
  SELECT 'Indrapuri', 20 UNION ALL
  SELECT 'Asharam Bapu Chouraha', 21 UNION ALL
  SELECT 'SDPS College', 22 UNION ALL
  SELECT 'Teen Imali Square', 23 UNION ALL
  SELECT 'Khandwa Naka Chouraha', 24 UNION ALL
  SELECT 'Mushakhedi Square', 25 UNION ALL
  SELECT 'Pipliya Hana Square', 26 UNION ALL
  SELECT 'Limbodi Gate Rani Bagh', 27 UNION ALL
  SELECT 'Tejaji Nagar', 28 UNION ALL
  SELECT 'Acropolis College', 29
) pos ON s.stop_name = pos.name;

-- Route 7: Gandhi Nagar → Acropolis College (19 stops)
INSERT INTO Route_Stops (route_id, stop_id, stop_order)
SELECT 4, stop_id, pos.ord FROM Stops s JOIN (
  SELECT 'Gandhi Nagar' AS name, 1 AS ord UNION ALL
  SELECT 'Aerodrum Thana', 2 UNION ALL
  SELECT 'Vidhya Dham', 3 UNION ALL
  SELECT 'Kalani Nagar', 4 UNION ALL
  SELECT 'Shikshak Nagar', 5 UNION ALL
  SELECT 'Ramchand Nagar Petrol Pump', 6 UNION ALL
  SELECT 'Bada Ganpati', 7 UNION ALL
  SELECT 'Rajmohalla Chouraha Petrol Pump', 8 UNION ALL
  SELECT 'Malganj Chouraha', 9 UNION ALL
  SELECT 'Narsingh Bazar Chouraha', 10 UNION ALL
  SELECT 'Bartanbazar Chouraha', 11 UNION ALL
  SELECT 'Gurudwara Jawaharmarg', 12 UNION ALL
  SELECT 'Saifi Hotel', 13 UNION ALL
  SELECT 'Patel Bridge', 14 UNION ALL
  SELECT 'Patel Pratima', 15 UNION ALL
  SELECT 'Shrimaya Hotel Madhumilan Chou.', 16 UNION ALL
  SELECT 'Dhakkanwala Kua', 17 UNION ALL
  SELECT 'Kanadia Bypass', 18 UNION ALL
  SELECT 'Acropolis College', 19
) pos ON s.stop_name = pos.name;

-- Route 10: Bhamori Plaza → Acropolis College (19 stops)
INSERT INTO Route_Stops (route_id, stop_id, stop_order)
SELECT 5, stop_id, pos.ord FROM Stops s JOIN (
  SELECT 'Bhamori Plaza' AS name, 1 AS ord UNION ALL
  SELECT 'Astha Talkies', 2 UNION ALL
  SELECT 'Patnipura Chouraha', 3 UNION ALL
  SELECT 'Bhandari Bridge Thana', 4 UNION ALL
  SELECT 'Subhash Nagar', 5 UNION ALL
  SELECT 'Pardeshipura', 6 UNION ALL
  SELECT 'Nanda Nagar Teen Puliya', 7 UNION ALL
  SELECT 'Nanda Nagar', 8 UNION ALL
  SELECT 'Patnipura', 9 UNION ALL
  SELECT 'Atal Dwar', 10 UNION ALL
  SELECT 'Christian Eminent School', 11 UNION ALL
  SELECT 'LIG Square', 12 UNION ALL
  SELECT 'Press Complex', 13 UNION ALL
  SELECT 'Malviya Nagar Chouraha', 14 UNION ALL
  SELECT 'Rasoma Chouraha', 15 UNION ALL
  SELECT 'Vijay Nagar RTO Office', 16 UNION ALL
  SELECT 'Hotel Redison Chouraha', 17 UNION ALL
  SELECT 'Bypass', 18 UNION ALL
  SELECT 'Acropolis College', 19
) pos ON s.stop_name = pos.name;

-- ============================================================
-- SCHEDULES - Map buses to routes with shift timings (from PDF)
-- ============================================================
-- Route 1 (route_id=1): Buses 1,2,3
INSERT INTO Schedules (bus_id, route_id, arrival_time_1st_shift, arrival_time_2nd_shift) VALUES
(1, 1, '08:10:00', '10:15:00'),
(2, 1, '08:10:00', '10:15:00'),
(3, 1, '08:10:00', '10:15:00');

-- Route 3 (route_id=2): Buses 4,5
INSERT INTO Schedules (bus_id, route_id, arrival_time_1st_shift, arrival_time_2nd_shift) VALUES
(4, 2, '08:10:00', '10:15:00'),
(5, 2, '08:10:00', '10:15:00');

-- Route 5 (route_id=3): Buses 6,7,8
INSERT INTO Schedules (bus_id, route_id, arrival_time_1st_shift, arrival_time_2nd_shift) VALUES
(6, 3, '08:10:00', '10:15:00'),
(7, 3, '08:10:00', '10:15:00'),
(8, 3, '08:10:00', '10:15:00');

-- Route 7 (route_id=4): Buses 9,10,11
INSERT INTO Schedules (bus_id, route_id, arrival_time_1st_shift, arrival_time_2nd_shift) VALUES
(9, 4, '08:10:00', '10:15:00'),
(10, 4, '08:10:00', '10:15:00'),
(11, 4, '08:10:00', '10:15:00');

-- Route 10 (route_id=5): Buses 12,13,14
INSERT INTO Schedules (bus_id, route_id, arrival_time_1st_shift, arrival_time_2nd_shift) VALUES
(12, 5, '08:10:00', '10:15:00'),
(13, 5, '08:10:00', '10:15:00'),
(14, 5, '08:10:00', '10:15:00');

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================
SELECT '=== DRIVERS ===' AS info;
SELECT driver_id, name, phone_number FROM Drivers ORDER BY driver_id;

SELECT '=== BUSES ===' AS info;
SELECT b.bus_id, b.bus_number, b.capacity, d.name AS driver_name
FROM Buses b LEFT JOIN Drivers d ON b.driver_id = d.driver_id
ORDER BY b.bus_id;

SELECT '=== ROUTES ===' AS info;
SELECT route_id, route_name, start_point, end_point FROM Routes ORDER BY route_id;

SELECT '=== ROUTE STOPS COUNT ===' AS info;
SELECT r.route_name, COUNT(rs.stop_id) AS stop_count
FROM Routes r LEFT JOIN Route_Stops rs ON r.route_id = rs.route_id
GROUP BY r.route_id ORDER BY r.route_id;

SELECT '=== SCHEDULES ===' AS info;
SELECT s.schedule_id, b.bus_number, r.route_name, s.arrival_time_1st_shift, s.arrival_time_2nd_shift
FROM Schedules s
JOIN Buses b ON s.bus_id = b.bus_id
JOIN Routes r ON s.route_id = r.route_id
ORDER BY r.route_id, b.bus_number;