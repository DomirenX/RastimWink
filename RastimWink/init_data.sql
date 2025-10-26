INSERT INTO departments (name) VALUES 
('HR'),
('Разработка'),
('Аналитика'),
('Менеджмент');

INSERT INTO users (email, password_hash, full_name, role, department_id) VALUES 
('admin@wink.com', '$2b$12$LQv3c1yqBWVHxkd0L8k7Oe7M7M6M6M6M6M6M6M6M6M6M6M6M6M6M6', 'Администратор Системы', 'admin', 4);

INSERT INTO users (email, password_hash, full_name, role, department_id) VALUES 
('hr@wink.com', '$2b$12$LQv3c1yqBWVHxkd0L8k7Oe7M7M6M6M6M6M6M6M6M6M6M6M6M6M6', 'HR Сотрудник', 'hr', 1);

INSERT INTO users (email, password_hash, full_name, role, department_id) VALUES 
('manager@wink.com', '$2b$12$LQv3c1yqBWVHxkd0L8k7Oe7M7M6M6M6M6M6M6M6M6M6M6M6M6M6', 'Менеджер Проектов', 'manager', 4);

INSERT INTO users (email, password_hash, full_name, role, department_id) VALUES 
('employee1@wink.com', '$2b$12$LQv3c1yqBWVHxkd0L8k7Oe7M7M6M6M6M6M6M6M6M6M6M6M6M6', 'Сотрудник Разработки', 'employee', 2),
('employee2@wink.com', '$2b$12$LQv3c1yqBWVHxkd0L8k7Oe7M7M6M6M6M6M6M6M6M6M6M6M6M6', 'Аналитик Данных', 'employee', 3);