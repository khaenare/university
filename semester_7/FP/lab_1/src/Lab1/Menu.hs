-- | Console menus of the application.
module Lab1.Menu
  ( mainMenu
  ) where

import Control.Exception (Handler (..), IOException, catches, throwIO)
import Control.Monad (forM_, unless)
import Data.Text (Text)
import qualified Data.Text as T
import qualified Data.Text.IO as TIO
import qualified Database.MySQL.Base as Base
import Database.MySQL.Simple (Connection, FormatError (..), QueryError (..))
import Database.MySQL.Simple.Result (ResultError)
import System.IO.Error (isEOFError)
import Text.Read (readMaybe)

import Lab1.Console (AppError (..), ask, askField, cancelKey, confirm, readLine, showT)
import Lab1.Entity
import Lab1.Form (Form, saveForm)
import Lab1.Model
import qualified Lab1.Reports as Reports

-- | Show numbered items until the user picks 0.
runMenu :: Text -> Text -> [(Text, IO ())] -> IO ()
runMenu title exitLabel items = loop
  where
    loop = do
      TIO.putStrLn ("\n=== " <> title <> " ===")
      forM_ (zip [1 :: Int ..] items) $ \(n, (label, _)) ->
        TIO.putStrLn (T.justifyRight 2 ' ' (showT n) <> ". " <> label)
      TIO.putStrLn (" 0. " <> exitLabel)
      choice <- readLine "> "
      case readMaybe (T.unpack choice) of
        Just 0 -> pure ()
        Just n | n >= 1 && n <= length items -> do
          safely (snd (items !! (n - 1)))
          loop
        _ -> TIO.putStrLn "Unknown option." >> loop

-- | Run an action and report database or user errors instead of crashing.
safely :: IO () -> IO ()
safely action =
  action
    `catches` [ Handler (\(e :: Base.MySQLError) -> failure ("Database error: " <> T.pack (Base.errMessage e)))
              , Handler (\(e :: FormatError) -> failure ("Query error: " <> T.pack (fmtMessage e)))
              , Handler (\(e :: QueryError) -> failure ("Query error: " <> T.pack (qeMessage e)))
              , Handler (\(e :: ResultError) -> failure ("Data conversion error: " <> showT e))
              , Handler appError
              , Handler ioFailure
              ]
  where
    failure message = TIO.putStrLn ("Error: " <> message)
    appError (UserError message) = failure message
    appError Cancelled = TIO.putStrLn "Cancelled."
    -- The end of input finishes the program (see Main); other I/O errors
    -- only abort the current action.
    ioFailure (e :: IOException)
      | isEOFError e = throwIO e
      | otherwise = failure ("Input/output error: " <> showT e)

mainMenu :: Connection -> IO ()
mainMenu conn = do
  TIO.putStrLn ("Type " <> cancelKey <> " at any prompt to cancel the current action.")
  runMenu
    "Individual work of the department with students"
    "Exit"
    [ ("Students", entityMenu @Student conn "Students")
    , ("Teachers", entityMenu @Teacher conn "Teachers")
    , ("Topics", entityMenu @Topic conn "Topics")
    , ("Work schedule", entityMenu @ScheduleEntry conn "Work schedule")
    , ("Assignments", entityMenu @Assignment conn "Assignments")
    , ("Assignment completion", entityMenu @Submission conn "Assignment completion")
    , ("Information materials", entityMenu @Material conn "Information materials")
    , ("Student questions", entityMenu @Question conn "Student questions")
    , ("Teacher answers", entityMenu @Answer conn "Teacher answers")
    , ("Reports and search", reportsMenu conn)
    ]

reportsMenu :: Connection -> IO ()
reportsMenu conn =
  runMenu
    "Reports and search"
    "Back"
    [ ("Search in the whole database", Reports.globalSearch conn)
    , ("Progress of a student", Reports.studentProgress conn)
    , ("Overdue assignments", Reports.overdueAssignments conn)
    , ("Unanswered questions", Reports.unansweredQuestions conn)
    , ("Topic overview", Reports.topicOverview conn)
    , ("Questions and answers on a topic", Reports.topicDiscussion conn)
    , ("Schedule for a period", Reports.scheduleForPeriod conn)
    , ("Teacher workload", Reports.teacherWorkload conn)
    , ("Student rating", Reports.studentRating conn)
    ]

-- | The same list/search/add/edit/delete menu for every entity type.
entityMenu :: forall a. (Entity a, Tabular a, Form a) => Connection -> Text -> IO ()
entityMenu conn title =
  runMenu
    title
    "Back"
    [ ("Show all", findAll @a conn >>= printTable)
    , ("Search", search)
    , ("Show by ID", withRecord (\_ -> pure ()))
    , ("Add", add)
    , ("Edit", withRecord edit)
    , ("Delete", withRecord remove)
    ]
  where
    search = do
      term <- ask "Search text: "
      searchEntity @a conn term >>= printTable

    -- Ask for an id, print the record and pass it on.
    withRecord :: (a -> IO ()) -> IO ()
    withRecord next = do
      key <- askField "ID" Nothing
      found <- findById @a conn key
      case found of
        Nothing -> TIO.putStrLn ("There is no " <> entityName @a <> " with ID " <> showT key <> ".")
        Just record -> printRecord record >> next record

    add = do
      key <- saveForm conn (Nothing :: Maybe a) (insertEntity conn)
      TIO.putStrLn ("Saved " <> entityName @a <> " with ID " <> showT key <> ".")

    edit old = do
      TIO.putStrLn "Press Enter to keep the current value."
      updated <- saveForm conn (Just old) (updateEntity conn)
      TIO.putStrLn (if updated then "Changes saved." else "The record no longer exists.")

    -- The foreign keys decide what happens to related records: references
    -- with ON DELETE RESTRICT block the deletion, CASCADE ones are deleted
    -- too, so the user sees both before confirming.
    remove record = do
      dependents <- dependentRecords @a conn (entityId record)
      let blocking = filter (not . dependentCascades) dependents
          cascading = filter dependentCascades dependents
          describe d = showT (dependentCount d) <> " record(s) in " <> T.pack (dependentTable d)
          list = T.intercalate ", " . map describe
      if not (null blocking)
        then
          TIO.putStrLn
            ( "This " <> entityName @a <> " cannot be deleted, it is used by " <> list blocking
                <> ". Delete or reassign those records first."
            )
        else do
          unless (null cascading) $
            TIO.putStrLn ("Also deleted: " <> list cascading <> ", and the records that depend on them.")
          sure <- confirm ("Delete this " <> entityName @a <> "?")
          if sure
            then do
              deleted <- deleteEntity @a conn (entityId record)
              TIO.putStrLn (if deleted then "Deleted." else "The record no longer exists.")
            else TIO.putStrLn "Cancelled."
