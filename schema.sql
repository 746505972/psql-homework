-- smart_home_full_schema.sql for PostgreSQL

-- ====================================================================================
-- 1. Database Creation (if not already created, execute outside psql or connect to template database)
--    CREATE DATABASE project2025;
--    \c project2025;  -- If you are inside psql, you need to connect to the target database first
-- ====================================================================================

-- Drop existing tables (if they exist) to allow for clean re-execution of the script
DROP TABLE IF EXISTS energy_consumption CASCADE;
DROP TABLE IF EXISTS automation_rules CASCADE;
DROP TABLE IF EXISTS user_feedback CASCADE;
DROP TABLE IF EXISTS security_events CASCADE;
DROP TABLE IF EXISTS usage_logs CASCADE;
DROP TABLE IF EXISTS device_status_history CASCADE;
DROP TABLE IF EXISTS devices CASCADE;
DROP TABLE IF EXISTS rooms CASCADE;
DROP TABLE IF EXISTS user_home_assignments CASCADE;
DROP TABLE IF EXISTS homes CASCADE;
DROP TABLE IF EXISTS users CASCADE;


-- ====================================================================================
-- 2. Table Structure Definition (DDL - Data Definition Language)
-- ====================================================================================

-- Users Table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL, -- Stores hashed password
    email VARCHAR(100) UNIQUE,
    phone_number VARCHAR(20) UNIQUE,
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    is_admin BOOLEAN DEFAULT FALSE
);

-- Homes Table (A user can manage multiple homes, and a home can have multiple users)
CREATE TABLE homes (
    home_id SERIAL PRIMARY KEY,
    home_name VARCHAR(100) NOT NULL,
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(50),
    zip_code VARCHAR(10),
    area_sqm REAL, -- Total area of the home in square meters
    owner_user_id INTEGER, -- Marks the primary owner, optional
    FOREIGN KEY (owner_user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- User-Home Assignment Table (Many-to-many relationship)
CREATE TABLE user_home_assignments (
    user_id INTEGER NOT NULL,
    home_id INTEGER NOT NULL,
    role VARCHAR(50) DEFAULT 'member', -- E.g., 'owner', 'admin', 'member', 'guest'
    assigned_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, home_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (home_id) REFERENCES homes(home_id) ON DELETE CASCADE
);


-- Rooms Table
CREATE TABLE rooms (
    room_id SERIAL PRIMARY KEY,
    home_id INTEGER NOT NULL,
    room_name VARCHAR(100) NOT NULL,
    room_type VARCHAR(50), -- E.g., 'Living Room', 'Bedroom', 'Kitchen', 'Bathroom'
    area_sqm REAL, -- Area of the room
    description TEXT,
    UNIQUE (home_id, room_name), -- Room names must be unique within a home
    FOREIGN KEY (home_id) REFERENCES homes(home_id) ON DELETE CASCADE
);

-- Devices Table
CREATE TABLE devices (
    device_id SERIAL PRIMARY KEY,
    device_name VARCHAR(100) NOT NULL,
    device_type VARCHAR(50) NOT NULL, -- E.g., 'Smart Light', 'Smart AC', 'Smart Lock', 'Camera', 'Smart Speaker', 'Sensor'
    model_number VARCHAR(50),
    manufacturer VARCHAR(100),
    room_id INTEGER, -- Associated with a room, can be null (e.g., main router, outdoor camera)
    home_id INTEGER NOT NULL, -- Associated with a home
    current_status TEXT DEFAULT 'offline', -- E.g., 'online', 'offline', 'on', 'off', 'faulty'
    firmware_version VARCHAR(20),
    installation_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_communication TIMESTAMP WITH TIME ZONE, -- Last communication timestamp
    UNIQUE (home_id, device_name), -- Device names must be unique within a home
    FOREIGN KEY (room_id) REFERENCES rooms(room_id) ON DELETE SET NULL,
    FOREIGN KEY (home_id) REFERENCES homes(home_id) ON DELETE CASCADE
);

-- Device Status History Table (Records key status changes, e.g., on/off, not all sensor data)
CREATE TABLE device_status_history (
    history_id SERIAL PRIMARY KEY,
    device_id INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    old_status TEXT,
    new_status TEXT NOT NULL,
    user_id INTEGER, -- If manually operated by a user
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- Usage Logs Table
CREATE TABLE usage_logs (
    log_id SERIAL PRIMARY KEY,
    device_id INTEGER NOT NULL,
    user_id INTEGER, -- User who operated the device, can be null (e.g., automation triggered)
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER, -- Usage duration in seconds
    action TEXT, -- E.g., 'turn on', 'turn off', 'adjust brightness', 'set temperature', 'play music', 'view live feed'
    value_change TEXT, -- E.g., 'brightness from 50% to 80%', 'temp from 25°C to 22°C'
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    CHECK (end_time IS NULL OR end_time >= start_time)
);

-- Security Events Table
CREATE TABLE security_events (
    event_id SERIAL PRIMARY KEY,
    home_id INTEGER NOT NULL, -- Which home the event belongs to
    device_id INTEGER, -- Which device triggered the event, e.g., camera, lock
    event_type VARCHAR(100) NOT NULL, -- E.g., 'Intrusion Alert', 'Smoke Detected', 'Water Leak', 'Door/Window Anomaly', 'Unauthorized Unlock', 'Device Offline'
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    severity VARCHAR(20), -- E.g., 'High', 'Medium', 'Low', 'Critical'
    handled BOOLEAN DEFAULT FALSE, -- Whether the event has been handled
    handled_by_user_id INTEGER, -- User who handled the event
    handled_time TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (home_id) REFERENCES homes(home_id) ON DELETE CASCADE,
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE SET NULL,
    FOREIGN KEY (handled_by_user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- User Feedback Table
CREATE TABLE user_feedback (
    feedback_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    home_id INTEGER, -- Optional: Feedback related to a specific home
    device_id INTEGER, -- Optional: Feedback specific to a device
    feedback_type VARCHAR(50) DEFAULT 'suggestion', -- E.g., 'suggestion', 'bug report', 'praise', 'question'
    rating INTEGER, -- 1-5 stars, optional
    feedback_text TEXT NOT NULL,
    feedback_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending', -- E.g., 'pending', 'in progress', 'resolved', 'ignored'
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (home_id) REFERENCES homes(home_id) ON DELETE CASCADE,
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE SET NULL,
    CHECK (rating >= 1 AND rating <= 5 OR rating IS NULL)
);

-- Automation Rules Table
CREATE TABLE automation_rules (
    rule_id SERIAL PRIMARY KEY,
    home_id INTEGER NOT NULL,
    rule_name VARCHAR(100) NOT NULL,
    description TEXT,
    trigger_type VARCHAR(50) NOT NULL, -- E.g., 'time-based', 'device-state', 'sensor-data', 'user-action'
    trigger_condition TEXT, -- Trigger condition description (JSON or plain text)
    action_type VARCHAR(50) NOT NULL, -- E.g., 'device-control', 'send-notification'
    action_details TEXT, -- Action details (JSON or plain text)
    is_enabled BOOLEAN DEFAULT TRUE,
    created_by_user_id INTEGER,
    created_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (home_id) REFERENCES homes(home_id) ON DELETE CASCADE,
    FOREIGN KEY (created_by_user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

-- Energy Consumption Table (Assumes devices report energy data)
CREATE TABLE energy_consumption (
    consumption_id SERIAL PRIMARY KEY,
    device_id INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    consumption_kwh REAL NOT NULL, -- Unit: kilowatt-hour (kWh)
    reading_type VARCHAR(50) DEFAULT 'real-time', -- E.g., 'real-time', 'cumulative', 'periodic'
    FOREIGN KEY (device_id) REFERENCES devices(device_id) ON DELETE CASCADE
);


-- ====================================================================================
-- 3. Data Insertion (DML - Data Manipulation Language)
-- ====================================================================================

-- User Data
INSERT INTO users (username, password_hash, email, phone_number, is_admin) VALUES
('alice_smart', 'hashed_pw_alice_123', 'alice@smarthome.com', '13800000001', TRUE),
('bob_tech', 'hashed_pw_bob_456', 'bob@smarthome.com', '13900000002', FALSE),
('charlie_guest', 'hashed_pw_charlie_789', 'charlie@guest.com', '13700000003', FALSE);

-- Home Data
INSERT INTO homes (home_name, address, city, state, zip_code, area_sqm, owner_user_id) VALUES
('幸福之家', '北京市朝阳区幸福路1号', '北京', '北京', '100020', 120.5, 1),
('科技公寓', '上海市浦东新区创新街20号', '上海', '上海', '200120', 65.0, 2);

-- User-Home Assignment Data
INSERT INTO user_home_assignments (user_id, home_id, role) VALUES
(1, 1, 'owner'),
(2, 1, 'member'),
(1, 2, 'admin'),
(2, 2, 'owner'),
(3, 1, 'guest');

-- Room Data
INSERT INTO rooms (home_id, room_name, room_type, area_sqm, description) VALUES
(1, '客厅', '起居室', 35.0, '家庭聚会的中心区域'),
(1, '主卧', '卧室', 20.0, '带独立卫生间的主卧室'),
(1, '厨房', '功能区', 12.0, '烹饪美食的地方'),
(1, '儿童房', '卧室', 15.0, '孩子的专属空间'),
(2, '客厅', '起居室', 25.0, '小户型客厅'),
(2, '卧室', '卧室', 18.0, '单人卧室');

-- Device Data
INSERT INTO devices (device_name, device_type, model_number, manufacturer, room_id, home_id, current_status, firmware_version) VALUES
-- 幸福之家 (Home 1)
('客厅氛围灯', '智能灯', 'L100', 'Philips Hue', 1, 1, '开启', '1.2.0'),
('卧室中央空调', '智能空调', 'AC-Z1', '美的', 2, 1, '关闭', '3.5.1'),
('前门智能锁', '智能门锁', 'DL-A1', '小米', NULL, 1, '在线', '2.0.5'), -- Door lock not necessarily tied to a room
('厨房烟雾传感器', '传感器', 'S-SMOKE', 'Aqara', 3, 1, '在线', '1.0.1'),
('儿童房智能音箱', '智能音箱', 'Echo Dot', 'Amazon', 4, 1, '播放音乐', '4.1.0'),
('主卧窗帘', '智能窗帘', 'CL-01', 'Tuya', 2, 1, '关闭', '1.1.0'),
('客厅智能电视', '智能电视', 'TV-X1', 'Sony', 1, 1, '待机', 'V5.0'),

-- 科技公寓 (Home 2)
('公寓客厅灯', '智能灯', 'L200', 'Yeelight', 5, 2, '开启', '1.5.0'),
('公寓卧室空调', '智能空调', 'AC-X5', '格力', 6, 2, '关闭', '3.8.0'),
('公寓门磁传感器', '传感器', 'MS-01', 'Aqara', NULL, 2, '在线', '1.0.0');

-- Device Status History Data
INSERT INTO device_status_history (device_id, timestamp, old_status, new_status, user_id) VALUES
(1, '2025-05-20 08:00:00+08', '关闭', '开启', 1),
(1, '2025-05-20 10:00:00+08', '开启', '关闭', 1),
(2, '2025-05-20 12:30:00+08', '关闭', '开启', 2),
(2, '2025-05-20 13:00:00+08', '开启', '关闭', 2),
(1, '2025-05-21 19:00:00+08', '关闭', '开启', 1),
(6, '2025-05-21 20:00:00+08', '关闭', '开启', 1), -- Alice opens curtains
(5, '2025-05-22 07:00:00+08', '播放音乐', '待机', NULL), -- Automation turns off music
(8, '2025-05-23 21:00:00+08', '关闭', '开启', 2);

-- Usage Logs Data
-- Assuming duration_seconds is calculated during insertion or derived from frontend/backend
INSERT INTO usage_logs (device_id, user_id, start_time, end_time, duration_seconds, action, value_change) VALUES
(1, 1, '2025-05-20 08:00:00+08', '2025-05-20 10:00:00+08', 7200, '开启/关闭', NULL),
(2, 2, '2025-05-20 12:30:00+08', '2025-05-20 13:00:00+08', 1800, '设置温度', '26°C -> 24°C'),
(1, 1, '2025-05-21 19:00:00+08', '2025-05-21 22:00:00+08', 10800, '开启/关闭', NULL),
(5, 1, '2025-05-21 20:00:00+08', '2025-05-21 20:30:00+08', 1800, '播放音乐', '舒缓轻音乐'),
(6, 1, '2025-05-21 20:00:00+08', '2025-05-21 21:00:00+08', 3600, '开启/关闭', '开窗帘'), -- Used simultaneously with smart speaker
(7, 1, '2025-05-21 21:00:00+08', '2025-05-21 23:00:00+08', 7200, '观看', '播放电影'),
(8, 2, '2025-05-23 21:00:00+08', '2025-05-23 23:00:00+08', 7200, '开启/关闭', NULL);


-- Security Events Data
INSERT INTO security_events (home_id, device_id, event_type, description, severity, handled, handled_by_user_id, handled_time) VALUES
(1, 3, '非法开锁', '前门智能锁检测到非法开锁尝试', '高', TRUE, 1, '2025-05-20 02:15:00+08'),
(1, 4, '烟雾探测', '厨房烟雾传感器检测到烟雾', '紧急', FALSE, NULL, NULL),
(1, 3, '门窗异常', '前门长时间未关闭', '中', TRUE, 2, '2025-05-21 14:00:00+08'),
(2, 10, '设备离线', '公寓门磁传感器离线', '低', FALSE, NULL, NULL);

-- User Feedback Data
INSERT INTO user_feedback (user_id, home_id, device_id, feedback_type, rating, feedback_text, status) VALUES
(1, 1, 1, '表扬', 5, '客厅氛围灯的颜色和亮度调节非常棒！', '已解决'),
(2, 1, 2, '问题', 3, '卧室空调偶尔会有异响，希望改进。', '待处理'),
(1, 1, NULL, '建议', NULL, '希望增加多用户同时控制设备的权限管理功能。', '待处理'),
(3, 1, 5, '问题', 2, '儿童房智能音箱的语音识别有点迟钝。', '待处理');

-- Automation Rules Data
INSERT INTO automation_rules (home_id, rule_name, description, trigger_type, trigger_condition, action_type, action_details, created_by_user_id) VALUES
(1, '早安模式', '每天早上7点自动开启客厅灯和卧室窗帘', '时间', '{"time": "07:00:00", "days_of_week": [1,2,3,4,5]}', '设备控制', '{"device_id": [1, 6], "action": "开启"}', 1),
(1, '离家布防', '所有用户离家后自动关闭所有灯并开启安防', '用户操作', '{"users_status": "all_away"}', '设备控制', '{"device_type": "智能灯", "action": "关闭", "security_system": "布防"}', 1),
(2, '夜间节电', '晚上23点后，如果公寓客厅灯还开着，自动调低亮度', '时间', '{"time": "23:00:00", "check_status": {"device_id": 8, "status": "开启"}}', '设备控制', '{"device_id": 8, "action": "调节亮度", "value": "20%"}', 2);

-- Energy Consumption Data
INSERT INTO energy_consumption (device_id, timestamp, consumption_kwh, reading_type) VALUES
(1, '2025-05-20 09:00:00+08', 0.05, '实时'),
(1, '2025-05-20 10:00:00+08', 0.03, '实时'),
(2, '2025-05-20 12:45:00+08', 0.8, '实时'),
(8, '2025-05-23 22:00:00+08', 0.08, '实时'),
(7, '2025-05-21 22:00:00+08', 0.2, '实时'),
(2, '2025-05-21 00:00:00+08', 5.5, '累计'); -- Daily cumulative energy consumption