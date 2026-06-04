CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    display_name VARCHAR(120),
    role VARCHAR(40) NOT NULL DEFAULT 'learner',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    code VARCHAR(40) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS levels (
    id SERIAL PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(id),
    code VARCHAR(20) NOT NULL,
    title VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS modules (
    id SERIAL PRIMARY KEY,
    level_id INTEGER NOT NULL REFERENCES levels(id),
    code VARCHAR(40) NOT NULL,
    title VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS lessons (
    id SERIAL PRIMARY KEY,
    module_id INTEGER NOT NULL REFERENCES modules(id),
    code VARCHAR(40) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    status VARCHAR(60) NOT NULL DEFAULT 'placeholder',
    source_path VARCHAR(500),
    processed_path VARCHAR(500),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS quizzes (
    id SERIAL PRIMARY KEY,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id),
    title VARCHAR(255) NOT NULL,
    status VARCHAR(60) NOT NULL DEFAULT 'draft'
);

CREATE TABLE IF NOT EXISTS questions (
    id SERIAL PRIMARY KEY,
    quiz_id INTEGER NOT NULL REFERENCES quizzes(id),
    question_type VARCHAR(60) NOT NULL,
    prompt TEXT NOT NULL,
    choices JSONB,
    answer_key JSONB NOT NULL,
    order_index INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS flashcards (
    id SERIAL PRIMARY KEY,
    lesson_id INTEGER NOT NULL REFERENCES lessons(id),
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    card_type VARCHAR(60) NOT NULL DEFAULT 'vocabulary',
    order_index INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS assignments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    lesson_id INTEGER NOT NULL REFERENCES lessons(id),
    status VARCHAR(60) NOT NULL DEFAULT 'assigned',
    due_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    lesson_id INTEGER REFERENCES lessons(id),
    quiz_id INTEGER REFERENCES quizzes(id),
    status VARCHAR(60) NOT NULL DEFAULT 'not_started',
    score DOUBLE PRECISION,
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

