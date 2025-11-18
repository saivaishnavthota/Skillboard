-- SQL script to update ratingenum enum type
-- Run this in your PostgreSQL database to add the new enum values

-- Add 'Developing' if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum 
        WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'ratingenum')
        AND enumlabel = 'Developing'
    ) THEN
        ALTER TYPE ratingenum ADD VALUE 'Developing';
    END IF;
END $$;

-- Add 'Expert' if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_enum 
        WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'ratingenum')
        AND enumlabel = 'Expert'
    ) THEN
        ALTER TYPE ratingenum ADD VALUE 'Expert';
    END IF;
END $$;

-- Verify the enum values
SELECT enumlabel 
FROM pg_enum 
WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'ratingenum')
ORDER BY enumsortorder;

