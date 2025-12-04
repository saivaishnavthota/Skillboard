-- Create role_requirements table for band-based skill requirements
CREATE TABLE IF NOT EXISTS role_requirements (
    id SERIAL PRIMARY KEY,
    band VARCHAR NOT NULL,
    skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    required_rating VARCHAR(50) NOT NULL,
    is_required BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT uq_band_skill_requirement UNIQUE (band, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_role_requirements_band ON role_requirements(band);
CREATE INDEX IF NOT EXISTS idx_role_requirements_skill_id ON role_requirements(skill_id);

-- Example data: Add some sample role requirements
-- Uncomment and modify these as needed for your organization

-- INSERT INTO role_requirements (band, skill_id, required_rating, is_required)
-- SELECT 'A', id, 'Beginner', TRUE FROM skills WHERE name = 'Python' LIMIT 1;

-- INSERT INTO role_requirements (band, skill_id, required_rating, is_required)
-- SELECT 'B', id, 'Intermediate', TRUE FROM skills WHERE name = 'Python' LIMIT 1;

-- INSERT INTO role_requirements (band, skill_id, required_rating, is_required)
-- SELECT 'C', id, 'Advanced', TRUE FROM skills WHERE name = 'Python' LIMIT 1;
