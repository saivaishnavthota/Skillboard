-- Add is_custom column to employee_skills table
-- This column tracks whether a skill was added by the user outside of their category template

-- Check if column exists, if not add it
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'employee_skills' 
        AND column_name = 'is_custom'
    ) THEN
        ALTER TABLE employee_skills 
        ADD COLUMN is_custom BOOLEAN NOT NULL DEFAULT FALSE;
        
        RAISE NOTICE 'Column is_custom added to employee_skills table';
    ELSE
        RAISE NOTICE 'Column is_custom already exists in employee_skills table';
    END IF;
END $$;
