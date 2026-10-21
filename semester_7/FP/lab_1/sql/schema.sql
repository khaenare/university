-- Schema for the information system
-- "Individual work of the department with students" (lab 1, variant 6).
--
-- Usage: mysql -uroot < sql/schema.sql
-- WARNING: drops and recreates the whole database.
--
-- Delete policy: a teacher cannot be deleted while topics or answers refer
-- to them (ON DELETE RESTRICT), so grades and answers are never lost by
-- accident. Other dependent rows (e.g. the assignments of a topic) are
-- deleted together with their parent (ON DELETE CASCADE); the application
-- shows how many before asking for confirmation.

DROP DATABASE IF EXISTS dept_individual_work;
CREATE DATABASE dept_individual_work
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE dept_individual_work;

-- Students who take part in individual work.
CREATE TABLE students (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  full_name   VARCHAR(120) NOT NULL,
  group_name  VARCHAR(20)  NOT NULL,
  email       VARCHAR(120) NULL UNIQUE,
  phone       VARCHAR(30)  NULL
) ENGINE = InnoDB;

-- Department teachers who supervise topics.
CREATE TABLE teachers (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  full_name   VARCHAR(120) NOT NULL,
  position    VARCHAR(80)  NOT NULL,
  email       VARCHAR(120) NULL UNIQUE,
  phone       VARCHAR(30)  NULL
) ENGINE = InnoDB;

-- Topics of individual work; every topic has a supervising teacher.
CREATE TABLE topics (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  teacher_id  INT          NOT NULL,
  title       VARCHAR(200) NOT NULL,
  description TEXT         NULL,
  CONSTRAINT fk_topics_teacher FOREIGN KEY (teacher_id)
    REFERENCES teachers (id) ON DELETE RESTRICT
) ENGINE = InnoDB;

-- Work schedule: individual meetings of a student on a topic.
-- Overlapping meetings of the same student, room or supervisor are
-- rejected by the application, because MySQL cannot express it as a key.
CREATE TABLE schedule (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  topic_id     INT         NOT NULL,
  student_id   INT         NOT NULL,
  meeting_date DATE        NOT NULL,
  start_time   TIME        NOT NULL,
  duration_min INT         NOT NULL DEFAULT 45,
  room         VARCHAR(30) NOT NULL,
  CONSTRAINT fk_schedule_topic FOREIGN KEY (topic_id)
    REFERENCES topics (id) ON DELETE CASCADE,
  CONSTRAINT fk_schedule_student FOREIGN KEY (student_id)
    REFERENCES students (id) ON DELETE CASCADE,
  -- A student cannot have two meetings starting at the same moment.
  CONSTRAINT uq_schedule_slot UNIQUE (student_id, meeting_date, start_time),
  CONSTRAINT chk_schedule_duration
    CHECK (duration_min BETWEEN 5 AND 240
           AND TIME_TO_SEC(start_time) + duration_min * 60 <= 24 * 3600)
) ENGINE = InnoDB;

-- Tasks issued within a topic.
CREATE TABLE assignments (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  topic_id    INT          NOT NULL,
  title       VARCHAR(200) NOT NULL,
  description TEXT         NULL,
  deadline    DATE         NOT NULL,
  CONSTRAINT fk_assignments_topic FOREIGN KEY (topic_id)
    REFERENCES topics (id) ON DELETE CASCADE
) ENGINE = InnoDB;

-- Completion of tasks by students.
CREATE TABLE submissions (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  assignment_id INT         NOT NULL,
  student_id    INT         NOT NULL,
  status        VARCHAR(20) NOT NULL DEFAULT 'assigned',
  submitted_on  DATE        NULL,
  grade         INT         NULL,
  CONSTRAINT fk_submissions_assignment FOREIGN KEY (assignment_id)
    REFERENCES assignments (id) ON DELETE CASCADE,
  CONSTRAINT fk_submissions_student FOREIGN KEY (student_id)
    REFERENCES students (id) ON DELETE CASCADE,
  CONSTRAINT uq_submission UNIQUE (assignment_id, student_id),
  CONSTRAINT chk_submission_status
    CHECK (status IN ('assigned', 'submitted', 'reviewed')),
  CONSTRAINT chk_submission_grade
    CHECK (grade IS NULL OR grade BETWEEN 0 AND 100),
  -- assigned: no date and no grade; submitted: date only;
  -- reviewed: both date and grade.
  CONSTRAINT chk_submission_progress
    CHECK ((status = 'assigned'  AND submitted_on IS NULL     AND grade IS NULL)
        OR (status = 'submitted' AND submitted_on IS NOT NULL AND grade IS NULL)
        OR (status = 'reviewed'  AND submitted_on IS NOT NULL AND grade IS NOT NULL))
) ENGINE = InnoDB;

-- Supporting information materials for topics.
CREATE TABLE materials (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  topic_id    INT          NOT NULL,
  title       VARCHAR(200) NOT NULL,
  kind        VARCHAR(40)  NOT NULL,
  link        VARCHAR(300) NULL,
  CONSTRAINT fk_materials_topic FOREIGN KEY (topic_id)
    REFERENCES topics (id) ON DELETE CASCADE
) ENGINE = InnoDB;

-- Questions asked by students on a topic.
CREATE TABLE questions (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  student_id  INT  NOT NULL,
  topic_id    INT  NOT NULL,
  body        TEXT NOT NULL,
  asked_on    DATE NOT NULL,
  CONSTRAINT fk_questions_student FOREIGN KEY (student_id)
    REFERENCES students (id) ON DELETE CASCADE,
  CONSTRAINT fk_questions_topic FOREIGN KEY (topic_id)
    REFERENCES topics (id) ON DELETE CASCADE
) ENGINE = InnoDB;

-- Teachers' answers to students' questions.
CREATE TABLE answers (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  question_id INT  NOT NULL,
  teacher_id  INT  NOT NULL,
  body        TEXT NOT NULL,
  answered_on DATE NOT NULL,
  CONSTRAINT fk_answers_question FOREIGN KEY (question_id)
    REFERENCES questions (id) ON DELETE CASCADE,
  CONSTRAINT fk_answers_teacher FOREIGN KEY (teacher_id)
    REFERENCES teachers (id) ON DELETE RESTRICT
) ENGINE = InnoDB;
