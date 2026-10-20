\c inji_certify postgres
CREATE TABLE certify.course_completion (
  subject_id varchar(36) PRIMARY KEY,
  learner_name text NOT NULL,
  course_id text NOT NULL,
  course_name text NOT NULL,
  completed_on date NOT NULL
);
-- Explicitly synthetic development records, fetched by the real PostgreSQL plugin.
INSERT INTO certify.course_completion VALUES
('11111111-1111-4111-8111-111111111111', 'Development Learner',
 'COURSE-DEV-001', 'Introduction to Digital Credentials', '2026-01-15');
