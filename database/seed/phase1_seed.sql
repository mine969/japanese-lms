INSERT INTO courses (code, title, description)
VALUES ('JLPT', 'JLPT N5 to N1', 'LMS course shell for JLPT progression.')
ON CONFLICT (code) DO NOTHING;
