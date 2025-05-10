-- Creating Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE
);

-- Creating Projects Table
CREATE TABLE IF NOT EXISTS projects (
    project_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Creating Tasks Table
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    task VARCHAR(255) NOT NULL,
    comments TEXT,
    time_spent INTERVAL DEFAULT '00:30:00',  -- Default to 30 minutes
    task_date DATE DEFAULT CURRENT_DATE,  -- Default to current date
    user_id INT REFERENCES users(user_id) ON DELETE CASCADE,  -- Foreign key to users
    project_id INT REFERENCES projects(project_id) ON DELETE CASCADE,  -- Foreign key to projects
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

