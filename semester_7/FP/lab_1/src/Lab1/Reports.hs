-- | Reports that join several tables, and a search over the whole database.
module Lab1.Reports
  ( studentProgress
  , overdueAssignments
  , unansweredQuestions
  , topicOverview
  , topicDiscussion
  , scheduleForPeriod
  , teacherWorkload
  , studentRating
  , globalSearch
  ) where

import Control.Monad (forM_, when)
import Data.Function (on)
import Data.List (groupBy)
import Data.Maybe (catMaybes)
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.IO as TIO
import Data.Time (Day, TimeOfDay, addDays)
import Database.MySQL.Simple (Connection, Only (..), query, query_)
import Text.Printf (printf)

import Lab1.Console (Input (..), addMinutes, ask, askField, orDash, showMaybe, showT, today)
import Lab1.Entity (Entity (..), Tabular, findById, printRecord, printRows, printTable, searchEntity)
import Lab1.Form (askRef, pickRecord)
import Lab1.Model

heading :: Text -> IO ()
heading title = TIO.putStrLn ("\n--- " <> title <> " ---")

formatGrade :: Double -> Text
formatGrade = T.pack . printf "%.1f"

-- | All assignments of one student with status and grade.
studentProgress :: Connection -> IO ()
studentProgress conn = do
  key <- askRef @Student conn "Student" Nothing
  rows <-
    query
      conn
      "SELECT a.title, t.title, a.deadline, s.status, s.submitted_on, s.grade \
      \FROM submissions s \
      \JOIN assignments a ON a.id = s.assignment_id \
      \JOIN topics t ON t.id = a.topic_id \
      \WHERE s.student_id = ? \
      \ORDER BY a.deadline"
      (Only key)
  heading "Student progress"
  printRows
    ["Assignment", "Topic", "Deadline", "Status", "Submitted", "Grade"]
    [ [title, topic, showInput deadline, showInput status, showMaybe date, showMaybe grade]
    | (title, topic, deadline, status, date, grade) <-
        rows :: [(Text, Text, Day, SubmissionStatus, Maybe Day, Maybe Int)]
    ]
  let reviewed = length [() | (_, _, _, Reviewed, _, _) <- rows]
      grades = catMaybes [g | (_, _, _, _, _, g) <- rows]
  printf "Reviewed: %d of %d" reviewed (length rows)
  if null grades
    then TIO.putStrLn ", no grades yet."
    else printf ", average grade: %.1f\n" (fromIntegral (sum grades) / fromIntegral (length grades) :: Double)

-- | Tasks that are still not submitted after their deadline.
overdueAssignments :: Connection -> IO ()
overdueAssignments conn = do
  now <- today
  rows <-
    query
      conn
      "SELECT st.full_name, st.group_name, a.title, t.title, a.deadline, DATEDIFF(?, a.deadline) \
      \FROM submissions s \
      \JOIN students st ON st.id = s.student_id \
      \JOIN assignments a ON a.id = s.assignment_id \
      \JOIN topics t ON t.id = a.topic_id \
      \WHERE s.status = 'assigned' AND a.deadline < ? \
      \ORDER BY a.deadline, st.full_name"
      (now, now)
  heading ("Overdue assignments on " <> showInput now)
  printRows
    ["Student", "Group", "Assignment", "Topic", "Deadline", "Days late"]
    [ [student, group, title, topic, showInput deadline, showT late]
    | (student, group, title, topic, deadline, late) <- rows :: [(Text, Text, Text, Text, Day, Int)]
    ]

-- | Questions that have no answer yet, with the responsible teacher.
unansweredQuestions :: Connection -> IO ()
unansweredQuestions conn = do
  rows <-
    query_
      conn
      "SELECT q.id, q.asked_on, st.full_name, t.title, te.full_name, q.body \
      \FROM questions q \
      \JOIN students st ON st.id = q.student_id \
      \JOIN topics t ON t.id = q.topic_id \
      \JOIN teachers te ON te.id = t.teacher_id \
      \LEFT JOIN answers an ON an.question_id = q.id \
      \WHERE an.id IS NULL \
      \ORDER BY q.asked_on"
  heading "Unanswered questions"
  printRows
    ["ID", "Asked on", "Student", "Topic", "Supervisor", "Question"]
    [ [showT key, showInput asked, student, topic, teacher, body]
    | (key, asked, student, topic, teacher, body) <- rows :: [(Int, Day, Text, Text, Text, Text)]
    ]

-- | Full card of a topic: supervisor, materials and assignment progress.
topicOverview :: Connection -> IO ()
topicOverview conn = do
  topic <- pickRecord @Topic conn "Topic" Nothing
  let key = topicId topic
  heading ("Topic: " <> topicTitle topic)
  TIO.putStrLn (orDash (topicDescription topic))
  supervisor <- findById @Teacher conn (topicTeacher topic)
  forM_ supervisor $ \t -> TIO.putStrLn ("Supervisor: " <> summary t)

  heading "Materials"
  materials <-
    query conn "SELECT title, kind, link FROM materials WHERE topic_id = ? ORDER BY title" (Only key)
  printRows
    ["Title", "Kind", "Link"]
    [[title, kind, orDash link] | (title, kind, link) <- materials :: [(Text, Text, Maybe Text)]]

  heading "Assignments"
  assignments <-
    query
      conn
      "SELECT a.title, a.deadline, COUNT(s.id), \
      \COUNT(CASE WHEN s.status <> 'assigned' THEN 1 END), AVG(s.grade) \
      \FROM assignments a \
      \LEFT JOIN submissions s ON s.assignment_id = a.id \
      \WHERE a.topic_id = ? \
      \GROUP BY a.id, a.title, a.deadline \
      \ORDER BY a.deadline"
      (Only key)
  printRows
    ["Assignment", "Deadline", "Issued", "Done", "Avg grade"]
    [ [title, showInput deadline, showT issued, showT done, maybe "-" formatGrade avg]
    | (title, deadline, issued, done, avg) <- assignments :: [(Text, Day, Int, Int, Maybe Double)]
    ]

-- | Questions on a topic together with the teachers' answers.
topicDiscussion :: Connection -> IO ()
topicDiscussion conn = do
  key <- askRef @Topic conn "Topic" Nothing
  rows <-
    query
      conn
      "SELECT q.id, q.asked_on, st.full_name, q.body, an.answered_on, te.full_name, an.body \
      \FROM questions q \
      \JOIN students st ON st.id = q.student_id \
      \LEFT JOIN answers an ON an.question_id = q.id \
      \LEFT JOIN teachers te ON te.id = an.teacher_id \
      \WHERE q.topic_id = ? \
      \ORDER BY q.asked_on, q.id, an.answered_on"
      (Only key)
  heading "Questions and answers"
  let threads =
        groupBy ((==) `on` questionKey) (rows :: [(Int, Day, Text, Text, Maybe Day, Maybe Text, Maybe Text)])
      questionKey (k, _, _, _, _, _, _) = k
  if null threads
    then TIO.putStrLn "(no questions on this topic)"
    else forM_ threads $ \thread -> case thread of
      [] -> pure ()
      (_, asked, student, body, _, _, _) : _ -> do
        TIO.putStrLn ("\n[" <> showInput asked <> "] " <> student <> ":")
        TIO.putStrLn ("  Q: " <> body)
        let answers = [(d, t, a) | (_, _, _, _, Just d, Just t, Just a) <- thread]
        if null answers
          then TIO.putStrLn "  A: (no answer yet)"
          else forM_ answers $ \(day, teacher, answer) ->
            TIO.putStrLn ("  A [" <> showInput day <> "] " <> teacher <> ": " <> answer)

-- | Meetings within a date range (the next two weeks by default).
scheduleForPeriod :: Connection -> IO ()
scheduleForPeriod conn = do
  now <- today
  from <- askField "From" (Just now)
  let askEnd = do
        end <- askField "To" (Just (addDays 14 from))
        if end < from
          then TIO.putStrLn "  The end date must not be before the start date." >> askEnd
          else pure end
  to <- askEnd
  rows <-
    query
      conn
      "SELECT sc.meeting_date, sc.start_time, sc.duration_min, sc.room, t.title, te.full_name, \
      \st.full_name, st.group_name \
      \FROM schedule sc \
      \JOIN topics t ON t.id = sc.topic_id \
      \JOIN teachers te ON te.id = t.teacher_id \
      \JOIN students st ON st.id = sc.student_id \
      \WHERE sc.meeting_date BETWEEN ? AND ? \
      \ORDER BY sc.meeting_date, sc.start_time"
      (from, to)
  heading ("Schedule " <> showInput from <> " .. " <> showInput to)
  printRows
    ["Date", "Time", "Room", "Topic", "Teacher", "Student", "Group"]
    [ [showInput day, showInput time <> "-" <> showInput (addMinutes duration time), room, topic, teacher, student, group]
    | (day, time, duration, room, topic, teacher, student, group) <-
        rows :: [(Day, TimeOfDay, Int, Text, Text, Text, Text, Text)]
    ]

-- | Number of topics, meetings and answered/open questions per teacher.
teacherWorkload :: Connection -> IO ()
teacherWorkload conn = do
  rows <-
    query_
      conn
      "SELECT te.full_name, te.position, \
      \(SELECT COUNT(*) FROM topics t WHERE t.teacher_id = te.id), \
      \(SELECT COUNT(*) FROM schedule sc JOIN topics t ON t.id = sc.topic_id \
      \  WHERE t.teacher_id = te.id), \
      \(SELECT COUNT(*) FROM answers an WHERE an.teacher_id = te.id), \
      \(SELECT COUNT(*) FROM questions q JOIN topics t ON t.id = q.topic_id \
      \  WHERE t.teacher_id = te.id \
      \  AND NOT EXISTS (SELECT 1 FROM answers an WHERE an.question_id = q.id)) \
      \FROM teachers te \
      \ORDER BY te.full_name"
  heading "Teacher workload"
  printRows
    ["Teacher", "Position", "Topics", "Meetings", "Answers given", "Open questions"]
    [ [name, position, showT topics, showT meetings, showT answers, showT open]
    | (name, position, topics, meetings, answers, open) <- rows :: [(Text, Text, Int, Int, Int, Int)]
    ]

-- | Students ordered by their average grade.
studentRating :: Connection -> IO ()
studentRating conn = do
  rows <-
    query_
      conn
      "SELECT st.full_name, st.group_name, COUNT(s.id), COUNT(s.grade), AVG(s.grade) \
      \FROM students st \
      \LEFT JOIN submissions s ON s.student_id = st.id \
      \GROUP BY st.id, st.full_name, st.group_name \
      \ORDER BY AVG(s.grade) IS NULL, AVG(s.grade) DESC, st.full_name"
  heading "Student rating"
  printRows
    ["#", "Student", "Group", "Assignments", "Graded", "Avg grade"]
    [ [showT place, name, group, showT issued, showT graded, maybe "-" formatGrade avg]
    | (place, (name, group, issued, graded, avg)) <-
        zip [1 :: Int ..] (rows :: [(Text, Text, Int, Int, Maybe Double)])
    ]

-- | Search a text in every table that has textual data.
globalSearch :: Connection -> IO ()
globalSearch conn = do
  term <- ask "Search text: "
  if T.null term
    then TIO.putStrLn "Empty search text."
    else do
      counts <-
        sequence
          [ section @Student "Students" term
          , section @Teacher "Teachers" term
          , section @Topic "Topics" term
          , section @Assignment "Assignments" term
          , section @Material "Materials" term
          , section @Question "Questions" term
          , section @Answer "Answers" term
          ]
      when (sum counts == 0) $ TIO.putStrLn "Nothing found."
  where
    -- Print the matches from one table and return their number.
    section :: forall a. (Entity a, Tabular a) => Text -> Text -> IO Int
    section title term = do
      found <- searchEntity @a conn term
      case found of
        [] -> pure ()
        [one] -> heading title >> printRecord one
        _ -> heading title >> printTable found
      pure (length found)
