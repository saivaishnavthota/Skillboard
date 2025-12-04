-- Create learning platform tables

-- Courses table
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description VARCHAR,
    skill_id INTEGER REFERENCES skills(id),
    external_url VARCHAR,
    is_mandatory BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_by INTEGER REFERENCES users(id)
);

-- Course assignments table
CREATE TABLE IF NOT EXISTS course_assignments (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(id),
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    assigned_by INTEGER REFERENCES users(id),
    assigned_at TIMESTAMP NOT NULL DEFAULT NOW(),
    due_date TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'Not Started',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    certificate_url VARCHAR,
    notes VARCHAR,
    CONSTRAINT uq_employee_course_assignment UNIQUE (employee_id, course_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_courses_skill_id ON courses(skill_id);
CREATE INDEX IF NOT EXISTS idx_course_assignments_course_id ON course_assignments(course_id);
CREATE INDEX IF NOT EXISTS idx_course_assignments_employee_id ON course_assignments(employee_id);
CREATE INDEX IF NOT EXISTS idx_course_assignments_status ON course_assignments(status);
