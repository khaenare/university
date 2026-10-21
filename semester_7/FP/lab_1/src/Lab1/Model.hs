-- | Domain types of the "Individual work of the department with students"
-- system and their instances of the project type classes.
module Lab1.Model
  ( Student (..)
  , Teacher (..)
  , Topic (..)
  , ScheduleEntry (..)
  , Assignment (..)
  , SubmissionStatus (..)
  , Submission (..)
  , Material (..)
  , Question (..)
  , Answer (..)
  ) where

import Control.Exception (throw)
import qualified Data.ByteString.Char8 as B8
import Data.Text (Text)
import qualified Data.Text as T
import Data.Time (Day, TimeOfDay, timeOfDayToTime)
import Database.MySQL.Base.Types (Field (..))
import Database.MySQL.Simple (query)
import Database.MySQL.Simple.Param (Param (..))
import Database.MySQL.Simple.QueryResults (QueryResults (..))
import Database.MySQL.Simple.Result (Result (..), ResultError (..))

import Lab1.Console (Input (..), addMinutes, askField, askOptional, orDash, shorten, showMaybe, showT, today)
import Lab1.Entity (Entity (..), Tabular (..))
import Lab1.Form (Form (..), askRef)

-- Helpers ------------------------------------------------------------------

emailRule :: Maybe Text -> [Text]
emailRule email =
  ["Email must contain '@'." | Just e <- [email], not ("@" `T.isInfixOf` e)]

-- Students -----------------------------------------------------------------

data Student = Student
  { studentId :: Int
  , studentName :: Text
  , studentGroup :: Text
  , studentEmail :: Maybe Text
  , studentPhone :: Maybe Text
  }
  deriving (Show, Eq)

-- The 'case' forces the converted tuple, so a conversion error is raised
-- inside 'query' and not later when a field is used.
instance QueryResults Student where
  convertResults fs vs = case convertResults fs vs of
    (a, b, c, d, e) -> Student a b c d e

instance Entity Student where
  tableName = "students"
  entityName = "student"
  columns = ["full_name", "group_name", "email", "phone"]
  searchColumns = ["full_name", "group_name", "email", "phone"]
  orderColumn = "full_name"
  entityId = studentId
  toParams s =
    [render (studentName s), render (studentGroup s), render (studentEmail s), render (studentPhone s)]
  summary s = studentName s <> " (" <> studentGroup s <> ")"

instance Tabular Student where
  headers = ["ID", "Full name", "Group", "Email", "Phone"]
  cells s =
    [showT (studentId s), studentName s, studentGroup s, orDash (studentEmail s), orDash (studentPhone s)]

instance Form Student where
  form _ old =
    Student (maybe 0 studentId old)
      <$> askField "Full name" (studentName <$> old)
      <*> askField "Group" (studentGroup <$> old)
      <*> askOptional "Email" (studentEmail <$> old)
      <*> askOptional "Phone" (studentPhone <$> old)
  validate s = emailRule (studentEmail s)

-- Teachers -----------------------------------------------------------------

data Teacher = Teacher
  { teacherId :: Int
  , teacherName :: Text
  , teacherPosition :: Text
  , teacherEmail :: Maybe Text
  , teacherPhone :: Maybe Text
  }
  deriving (Show, Eq)

instance QueryResults Teacher where
  convertResults fs vs = case convertResults fs vs of
    (a, b, c, d, e) -> Teacher a b c d e

instance Entity Teacher where
  tableName = "teachers"
  entityName = "teacher"
  columns = ["full_name", "position", "email", "phone"]
  orderColumn = "full_name"
  entityId = teacherId
  toParams t =
    [render (teacherName t), render (teacherPosition t), render (teacherEmail t), render (teacherPhone t)]
  summary t = teacherName t <> ", " <> teacherPosition t

instance Tabular Teacher where
  headers = ["ID", "Full name", "Position", "Email", "Phone"]
  cells t =
    [showT (teacherId t), teacherName t, teacherPosition t, orDash (teacherEmail t), orDash (teacherPhone t)]

instance Form Teacher where
  form _ old =
    Teacher (maybe 0 teacherId old)
      <$> askField "Full name" (teacherName <$> old)
      <*> askField "Position" (teacherPosition <$> old)
      <*> askOptional "Email" (teacherEmail <$> old)
      <*> askOptional "Phone" (teacherPhone <$> old)
  validate t = emailRule (teacherEmail t)

-- Topics -------------------------------------------------------------------

data Topic = Topic
  { topicId :: Int
  , topicTeacher :: Int
  , topicTitle :: Text
  , topicDescription :: Maybe Text
  }
  deriving (Show, Eq)

instance QueryResults Topic where
  convertResults fs vs = case convertResults fs vs of
    (a, b, c, d) -> Topic a b c d

instance Entity Topic where
  tableName = "topics"
  entityName = "topic"
  columns = ["teacher_id", "title", "description"]
  searchColumns = ["title", "description"]
  orderColumn = "title"
  entityId = topicId
  toParams t = [render (topicTeacher t), render (topicTitle t), render (topicDescription t)]
  summary = topicTitle

instance Tabular Topic where
  headers = ["ID", "Teacher ID", "Title", "Description"]
  cells t = [showT (topicId t), showT (topicTeacher t), topicTitle t, orDash (topicDescription t)]

instance Form Topic where
  form conn old =
    Topic (maybe 0 topicId old)
      <$> askRef @Teacher conn "Teacher" (topicTeacher <$> old)
      <*> askField "Title" (topicTitle <$> old)
      <*> askOptional "Description" (topicDescription <$> old)

-- Schedule -----------------------------------------------------------------

-- | An individual meeting of a student with the topic supervisor.
data ScheduleEntry = ScheduleEntry
  { scheduleId :: Int
  , scheduleTopic :: Int
  , scheduleStudent :: Int
  , scheduleDate :: Day
  , scheduleTime :: TimeOfDay
  , -- | Length of the meeting in minutes.
    scheduleDuration :: Int
  , scheduleRoom :: Text
  }
  deriving (Show, Eq)

-- | Default meeting length, the same as the column default in the schema.
defaultDuration :: Int
defaultDuration = 45

-- | Seconds from midnight to the end of the meeting.
endSeconds :: ScheduleEntry -> Integer
endSeconds s = floor (timeOfDayToTime (scheduleTime s)) + 60 * toInteger (scheduleDuration s)

-- | "10:00-10:45"
timeRange :: ScheduleEntry -> Text
timeRange s =
  showInput (scheduleTime s) <> "-" <> showInput (addMinutes (scheduleDuration s) (scheduleTime s))

instance QueryResults ScheduleEntry where
  convertResults fs vs = case convertResults fs vs of
    (a, b, c, d, e, f, g) -> ScheduleEntry a b c d e f g

instance Entity ScheduleEntry where
  tableName = "schedule"
  entityName = "schedule entry"
  columns = ["topic_id", "student_id", "meeting_date", "start_time", "duration_min", "room"]
  searchColumns = ["meeting_date", "room"]
  orderColumn = "meeting_date, start_time"
  entityId = scheduleId
  toParams s =
    [ render (scheduleTopic s)
    , render (scheduleStudent s)
    , render (scheduleDate s)
    , render (scheduleTime s)
    , render (scheduleDuration s)
    , render (scheduleRoom s)
    ]
  summary s = showInput (scheduleDate s) <> " " <> timeRange s <> ", room " <> scheduleRoom s

instance Tabular ScheduleEntry where
  headers = ["ID", "Topic ID", "Student ID", "Date", "Time", "Room"]
  cells s =
    [ showT (scheduleId s)
    , showT (scheduleTopic s)
    , showT (scheduleStudent s)
    , showInput (scheduleDate s)
    , timeRange s
    , scheduleRoom s
    ]

instance Form ScheduleEntry where
  form conn old =
    ScheduleEntry (maybe 0 scheduleId old)
      <$> askRef @Topic conn "Topic" (scheduleTopic <$> old)
      <*> askRef @Student conn "Student" (scheduleStudent <$> old)
      <*> askField "Date" (scheduleDate <$> old)
      <*> askField "Start time" (scheduleTime <$> old)
      <*> askField "Duration, minutes" (Just (maybe defaultDuration scheduleDuration old))
      <*> askField "Room" (scheduleRoom <$> old)
  validate s =
    ["Duration must be between 5 and 240 minutes." | d < 5 || d > 240]
      ++ ["The meeting must end before midnight." | endSeconds s > 24 * 3600]
    where
      d = scheduleDuration s

  -- A student, a room and a supervisor can each have only one meeting at a
  -- time, so look for meetings on the same day whose time ranges overlap.
  validateWith conn s = do
    rows <-
      query
        conn
        "SELECT sc.id, sc.start_time, sc.duration_min, sc.room, st.full_name, \
        \  CASE WHEN sc.student_id = ? THEN 'student' \
        \       WHEN sc.room = ? THEN 'room' \
        \       ELSE 'supervisor' END \
        \FROM schedule sc \
        \JOIN topics t ON t.id = sc.topic_id \
        \JOIN students st ON st.id = sc.student_id \
        \WHERE sc.id <> ? AND sc.meeting_date = ? \
        \  AND sc.start_time < ADDTIME(CAST(? AS TIME), SEC_TO_TIME(? * 60)) \
        \  AND ADDTIME(sc.start_time, SEC_TO_TIME(sc.duration_min * 60)) > CAST(? AS TIME) \
        \  AND (sc.student_id = ? OR sc.room = ? \
        \       OR t.teacher_id = (SELECT teacher_id FROM topics WHERE id = ?)) \
        \ORDER BY sc.start_time"
        [ render (scheduleStudent s)
        , render (scheduleRoom s)
        , render (scheduleId s)
        , render (scheduleDate s)
        , render (scheduleTime s)
        , render (scheduleDuration s)
        , render (scheduleTime s)
        , render (scheduleStudent s)
        , render (scheduleRoom s)
        , render (scheduleTopic s)
        ]
    pure
      [ "Overlaps meeting " <> showT key <> " (" <> timeRange other <> ", room " <> room
          <> ", student " <> student <> "): the same " <> reason <> " is busy."
      | (key, start, duration, room, student, reason) <- rows :: [(Int, TimeOfDay, Int, Text, Text, Text)]
      , let other = s {scheduleTime = start, scheduleDuration = duration}
      ]

-- Assignments --------------------------------------------------------------

data Assignment = Assignment
  { assignmentId :: Int
  , assignmentTopic :: Int
  , assignmentTitle :: Text
  , assignmentDescription :: Maybe Text
  , assignmentDeadline :: Day
  }
  deriving (Show, Eq)

instance QueryResults Assignment where
  convertResults fs vs = case convertResults fs vs of
    (a, b, c, d, e) -> Assignment a b c d e

instance Entity Assignment where
  tableName = "assignments"
  entityName = "assignment"
  columns = ["topic_id", "title", "description", "deadline"]
  searchColumns = ["title", "description"]
  orderColumn = "deadline"
  entityId = assignmentId
  toParams a =
    [ render (assignmentTopic a)
    , render (assignmentTitle a)
    , render (assignmentDescription a)
    , render (assignmentDeadline a)
    ]
  summary a = assignmentTitle a <> " (until " <> showInput (assignmentDeadline a) <> ")"

instance Tabular Assignment where
  headers = ["ID", "Topic ID", "Title", "Description", "Deadline"]
  cells a =
    [ showT (assignmentId a)
    , showT (assignmentTopic a)
    , assignmentTitle a
    , orDash (assignmentDescription a)
    , showInput (assignmentDeadline a)
    ]

instance Form Assignment where
  form conn old =
    Assignment (maybe 0 assignmentId old)
      <$> askRef @Topic conn "Topic" (assignmentTopic <$> old)
      <*> askField "Title" (assignmentTitle <$> old)
      <*> askOptional "Description" (assignmentDescription <$> old)
      <*> askField "Deadline" (assignmentDeadline <$> old)

-- Submissions --------------------------------------------------------------

-- | Progress of a student on an assignment.
data SubmissionStatus = Assigned | Submitted | Reviewed
  deriving (Show, Eq, Ord, Enum, Bounded)

statusText :: SubmissionStatus -> Text
statusText Assigned = "assigned"
statusText Submitted = "submitted"
statusText Reviewed = "reviewed"

statusFromText :: Text -> Maybe SubmissionStatus
statusFromText t = lookup (T.toLower t) [(statusText s, s) | s <- [minBound .. maxBound]]

-- | The status is stored in a VARCHAR column as its text name.
instance Param SubmissionStatus where
  render = render . statusText

instance Result SubmissionStatus where
  convert field value =
    case statusFromText (convert field value) of
      Just status -> status
      Nothing ->
        throw
          ConversionFailed
            { errSQLType = show (fieldType field)
            , errHaskellType = "SubmissionStatus"
            , errFieldName = B8.unpack (fieldName field)
            , errMessage = "unknown submission status"
            }

instance Input SubmissionStatus where
  parseInput = statusFromText
  showInput = statusText
  inputHint = T.intercalate "/" (map statusText [minBound .. maxBound])

data Submission = Submission
  { submissionId :: Int
  , submissionAssignment :: Int
  , submissionStudent :: Int
  , submissionStatus :: SubmissionStatus
  , submissionDate :: Maybe Day
  , submissionGrade :: Maybe Int
  }
  deriving (Show, Eq)

instance QueryResults Submission where
  convertResults fs vs = case convertResults fs vs of
    (a, b, c, d, e, f) -> Submission a b c d e f

instance Entity Submission where
  tableName = "submissions"
  entityName = "submission"
  columns = ["assignment_id", "student_id", "status", "submitted_on", "grade"]
  searchColumns = ["status", "submitted_on"]
  entityId = submissionId
  toParams s =
    [ render (submissionAssignment s)
    , render (submissionStudent s)
    , render (submissionStatus s)
    , render (submissionDate s)
    , render (submissionGrade s)
    ]
  summary s =
    "assignment " <> showT (submissionAssignment s) <> ", student " <> showT (submissionStudent s)
      <> ": " <> statusText (submissionStatus s)

instance Tabular Submission where
  headers = ["ID", "Assignment ID", "Student ID", "Status", "Submitted on", "Grade"]
  cells s =
    [ showT (submissionId s)
    , showT (submissionAssignment s)
    , showT (submissionStudent s)
    , statusText (submissionStatus s)
    , showMaybe (submissionDate s)
    , showMaybe (submissionGrade s)
    ]

instance Form Submission where
  form conn old =
    Submission (maybe 0 submissionId old)
      <$> askRef @Assignment conn "Assignment" (submissionAssignment <$> old)
      <*> askRef @Student conn "Student" (submissionStudent <$> old)
      <*> askField "Status" (Just (maybe Assigned submissionStatus old))
      <*> askOptional "Submitted on" (submissionDate <$> old)
      <*> askOptional "Grade (0-100)" (submissionGrade <$> old)
  validate s =
    ["Grade must be between 0 and 100." | Just g <- [submissionGrade s], g < 0 || g > 100]
      ++ case submissionStatus s of
        Assigned ->
          ["An assigned task cannot have a submission date." | Just _ <- [submissionDate s]]
            ++ ["An assigned task cannot have a grade." | Just _ <- [submissionGrade s]]
        Submitted ->
          ["A submitted task needs a submission date." | Nothing <- [submissionDate s]]
            ++ ["Only a reviewed task can have a grade." | Just _ <- [submissionGrade s]]
        Reviewed ->
          ["A reviewed task needs a submission date." | Nothing <- [submissionDate s]]
            ++ ["A reviewed task needs a grade." | Nothing <- [submissionGrade s]]

-- Materials ----------------------------------------------------------------

-- | Supporting information material for a topic.
data Material = Material
  { materialId :: Int
  , materialTopic :: Int
  , materialTitle :: Text
  , materialKind :: Text
  , materialLink :: Maybe Text
  }
  deriving (Show, Eq)

instance QueryResults Material where
  convertResults fs vs = case convertResults fs vs of
    (a, b, c, d, e) -> Material a b c d e

instance Entity Material where
  tableName = "materials"
  entityName = "material"
  columns = ["topic_id", "title", "kind", "link"]
  searchColumns = ["title", "kind", "link"]
  orderColumn = "title"
  entityId = materialId
  toParams m =
    [render (materialTopic m), render (materialTitle m), render (materialKind m), render (materialLink m)]
  summary m = materialTitle m <> " [" <> materialKind m <> "]"

instance Tabular Material where
  headers = ["ID", "Topic ID", "Title", "Kind", "Link"]
  cells m =
    [showT (materialId m), showT (materialTopic m), materialTitle m, materialKind m, orDash (materialLink m)]

instance Form Material where
  form conn old =
    Material (maybe 0 materialId old)
      <$> askRef @Topic conn "Topic" (materialTopic <$> old)
      <*> askField "Title" (materialTitle <$> old)
      <*> askField "Kind (book, article, lecture notes, ...)" (materialKind <$> old)
      <*> askOptional "Link" (materialLink <$> old)

-- Questions ----------------------------------------------------------------

data Question = Question
  { questionId :: Int
  , questionStudent :: Int
  , questionTopic :: Int
  , questionBody :: Text
  , questionDate :: Day
  }
  deriving (Show, Eq)

instance QueryResults Question where
  convertResults fs vs = case convertResults fs vs of
    (a, b, c, d, e) -> Question a b c d e

instance Entity Question where
  tableName = "questions"
  entityName = "question"
  columns = ["student_id", "topic_id", "body", "asked_on"]
  searchColumns = ["body"]
  orderColumn = "asked_on"
  entityId = questionId
  toParams q =
    [render (questionStudent q), render (questionTopic q), render (questionBody q), render (questionDate q)]
  summary q = shorten 60 (questionBody q)

instance Tabular Question where
  headers = ["ID", "Student ID", "Topic ID", "Question", "Asked on"]
  cells q =
    [ showT (questionId q)
    , showT (questionStudent q)
    , showT (questionTopic q)
    , questionBody q
    , showInput (questionDate q)
    ]

instance Form Question where
  form conn old = do
    now <- today
    Question (maybe 0 questionId old)
      <$> askRef @Student conn "Student" (questionStudent <$> old)
      <*> askRef @Topic conn "Topic" (questionTopic <$> old)
      <*> askField "Question" (questionBody <$> old)
      <*> askField "Asked on" (Just (maybe now questionDate old))

-- Answers ------------------------------------------------------------------

data Answer = Answer
  { answerId :: Int
  , answerQuestion :: Int
  , answerTeacher :: Int
  , answerBody :: Text
  , answerDate :: Day
  }
  deriving (Show, Eq)

instance QueryResults Answer where
  convertResults fs vs = case convertResults fs vs of
    (a, b, c, d, e) -> Answer a b c d e

instance Entity Answer where
  tableName = "answers"
  entityName = "answer"
  columns = ["question_id", "teacher_id", "body", "answered_on"]
  searchColumns = ["body"]
  orderColumn = "answered_on"
  entityId = answerId
  toParams a =
    [render (answerQuestion a), render (answerTeacher a), render (answerBody a), render (answerDate a)]
  summary a = shorten 60 (answerBody a)

instance Tabular Answer where
  headers = ["ID", "Question ID", "Teacher ID", "Answer", "Answered on"]
  cells a =
    [ showT (answerId a)
    , showT (answerQuestion a)
    , showT (answerTeacher a)
    , answerBody a
    , showInput (answerDate a)
    ]

instance Form Answer where
  form conn old = do
    now <- today
    Answer (maybe 0 answerId old)
      <$> askRef @Question conn "Question" (answerQuestion <$> old)
      <*> askRef @Teacher conn "Teacher" (answerTeacher <$> old)
      <*> askField "Answer" (answerBody <$> old)
      <*> askField "Answered on" (Just (maybe now answerDate old))
