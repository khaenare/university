-- Sample data for the "Individual work of the department with students" system.
--
-- Usage: mysql -uroot dept_individual_work < sql/seed.sql
-- Run after sql/schema.sql.

SET NAMES utf8mb4;

INSERT INTO students (id, full_name, group_name, email, phone) VALUES
  (1, 'Іваненко Олена Петрівна',     'КН-31', 'ivanenko@student.edu.ua',  '+380501112233'),
  (2, 'Коваленко Максим Ігорович',   'КН-31', 'kovalenko@student.edu.ua', '+380672223344'),
  (3, 'Шевчук Андрій Васильович',    'КН-32', 'shevchuk@student.edu.ua',  NULL),
  (4, 'Бондар Юлія Сергіївна',       'КН-32', 'bondar@student.edu.ua',    '+380933334455'),
  (5, 'Мельник Дмитро Олександрович', 'ПМ-21', NULL,                      '+380994445566'),
  (6, 'Ткаченко Ірина Миколаївна',   'ПМ-21', 'tkachenko@student.edu.ua', NULL);

INSERT INTO teachers (id, full_name, position, email, phone) VALUES
  (1, 'Петренко Віктор Андрійович', 'доцент',           'petrenko@univ.edu.ua',  '+380441230001'),
  (2, 'Савченко Наталія Іванівна',  'професор',         'savchenko@univ.edu.ua', '+380441230002'),
  (3, 'Кравчук Олег Миколайович',   'старший викладач', 'kravchuk@univ.edu.ua',  NULL),
  (4, 'Литвиненко Марія Петрівна',  'асистент',         NULL,                    '+380441230004');

INSERT INTO topics (id, teacher_id, title, description) VALUES
  (1, 1, 'Класи типів у Haskell',            'Type classes, instances, функтори та монади.'),
  (2, 2, 'Паралельні обчислення',            'Потоки, MVar, STM та оцінка прискорення.'),
  (3, 3, 'Проєктування реляційних БД',       'Нормалізація, ключі, зовнішні ключі, індекси.'),
  (4, 1, 'Лямбда-числення',                  'Редукція, комбінатори, типізоване лямбда-числення.'),
  (5, 4, 'Обробка тексту функціональними засобами', 'Розбір тексту, алгебраїчні типи даних.');

INSERT INTO schedule (topic_id, student_id, meeting_date, start_time, duration_min, room) VALUES
  (1, 1, '2026-10-14', '10:00', 60, '305'),
  (1, 2, '2026-10-14', '11:30', 45, '305'),
  (2, 3, '2026-10-20', '13:00', 45, '412'),
  (3, 4, '2026-10-22', '09:00', 90, '210'),
  (1, 1, '2026-10-28', '10:00', 45, '305'),
  (4, 5, '2026-10-29', '14:30', 30, '307'),
  (5, 6, '2026-11-03', '12:00', 45, '118'),
  (2, 2, '2026-11-04', '13:00', 60, '412');

INSERT INTO assignments (id, topic_id, title, description, deadline) VALUES
  (1, 1, 'Власний клас типів Shape', 'Описати клас Shape та три його екземпляри.', '2026-10-10'),
  (2, 1, 'Екземпляр Functor для дерева', 'Реалізувати fmap для бінарного дерева.', '2026-10-30'),
  (3, 2, 'Паралельне сортування', 'Сортування злиттям з використанням forkIO.', '2026-10-15'),
  (4, 3, 'ER-діаграма предметної області', 'Побудувати ER-діаграму та нормалізувати до 3НФ.', '2026-11-05'),
  (5, 4, 'Комбінатори SKI', 'Виразити функцію через комбінатори S, K, I.', '2026-10-18'),
  (6, 5, 'Підрахунок частоти слів', 'Розбити текст на слова та порахувати частоти.', '2026-11-10');

INSERT INTO submissions (assignment_id, student_id, status, submitted_on, grade) VALUES
  (1, 1, 'reviewed',  '2026-10-08', 95),
  (1, 2, 'reviewed',  '2026-10-10', 78),
  (2, 1, 'submitted', '2026-10-19', NULL),
  (2, 2, 'assigned',  NULL,         NULL),
  (3, 3, 'reviewed',  '2026-10-14', 88),
  (3, 2, 'assigned',  NULL,         NULL),
  (4, 4, 'assigned',  NULL,         NULL),
  (5, 5, 'assigned',  NULL,         NULL),
  (5, 6, 'reviewed',  '2026-10-17', 70),
  (6, 6, 'submitted', '2026-10-20', NULL);

INSERT INTO materials (topic_id, title, kind, link) VALUES
  (1, 'Learn You a Haskell: Typeclasses', 'книга',     'https://learnyouahaskell.com/types-and-typeclasses'),
  (1, 'Лекція 3: класи типів',            'конспект',  NULL),
  (2, 'Parallel and Concurrent Programming in Haskell', 'книга', 'https://simonmar.github.io/pages/pcph.html'),
  (3, 'Нормальні форми: приклади',        'презентація', NULL),
  (4, 'Вступ до лямбда-числення',         'стаття',    NULL),
  (5, 'Data.Text documentation',          'документація', 'https://hackage.haskell.org/package/text');

INSERT INTO questions (id, student_id, topic_id, body, asked_on) VALUES
  (1, 1, 1, 'Чим відрізняється class від data?',                   '2026-10-05'),
  (2, 2, 1, 'Чи можна мати два екземпляри класу для одного типу?', '2026-10-09'),
  (3, 3, 2, 'Як виміряти прискорення на кількох ядрах?',           '2026-10-12'),
  (4, 4, 3, 'Коли варто денормалізувати таблиці?',                 '2026-10-18'),
  (5, 5, 4, 'Що таке нормальний порядок редукції?',                '2026-10-19');

INSERT INTO answers (question_id, teacher_id, body, answered_on) VALUES
  (1, 1, 'data оголошує новий тип, class описує набір операцій для типів.', '2026-10-06'),
  (2, 1, 'Ні, але можна обгорнути тип у newtype і дати йому інший екземпляр.', '2026-10-10'),
  (3, 2, 'Запустіть програму з +RTS -N1 та -N4 і порівняйте час виконання.',  '2026-10-13');
